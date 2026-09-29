import {readFile,writeFile} from 'node:fs/promises';
import {execFileSync} from 'node:child_process';
const account = process.env.CLOUDFLARE_ACCOUNT_ID;
const token = process.env.CLOUDFLARE_API_TOKEN;
if (!account || !token) throw new Error('Set CLOUDFLARE_ACCOUNT_ID and the CLOUDFLARE_API_TOKEN repository secret (Cloudflare Pages, D1 and Turnstile Edit).');
async function api(path, method='GET', body, allowMissing=false) {
  const response = await fetch(`https://api.cloudflare.com/client/v4/accounts/${account}/${path}`,{
    method,headers:{Authorization:`Bearer ${token}`,'Content-Type':'application/json'},
    ...(body ? {body:JSON.stringify(body)} : {})
  });
  if (allowMissing && response.status === 404) return null;
  const data = await response.json();
  if (!response.ok || !data.success) throw new Error(`Cloudflare ${method} ${path} failed (${response.status}). Check token permissions and account limits.`);
  return data.result;
}
const originalConfig = await readFile('wrangler.jsonc','utf8');
const config = JSON.parse(originalConfig);
const projectPath = `pages/projects/${config.name}`;
let project = await api(projectPath,'GET',undefined,true);
if (!project) project = await api('pages/projects','POST',{name:config.name,production_branch:'cf-pages'});
if (project.production_branch !== 'cf-pages') throw new Error('This Pages project uses a different production branch. Review its configuration before deploying.');
const databases = await api('d1/database?name=liquidjelly-enquiries');
let db = databases.find(item=>item.name==='liquidjelly-enquiries');
if (!db) db = await api('d1/database','POST',{name:'liquidjelly-enquiries',jurisdiction:'eu'});
if (db.jurisdiction !== 'eu') throw new Error('The existing database is not EU-restricted. Review before reusing it.');
config.d1_databases[0].database_id = db.uuid;
config.d1_databases[0].jurisdiction = 'eu';
// Use the actual Pages hostname returned by Cloudflare, not an assumed workers.dev address.
const domains = [...new Set([project.subdomain,'www.liquidjelly.co.uk','liquidjelly.co.uk'])];
if (!project.subdomain?.endsWith('.pages.dev')) throw new Error('Pages did not return a valid project hostname.');
config.vars.ALLOWED_HOSTS = domains.join(',');
const widgets = await api('challenges/widgets');
const existing = widgets.find(item=>item.name==='LiquidJelly enquiries');
let widget = existing ? await api(`challenges/widgets/${existing.sitekey}`) : await api('challenges/widgets','POST',{name:'LiquidJelly enquiries',mode:'managed',domains});
if (!domains.every(domain=>widget.domains.includes(domain))) {
  widget = await api(`challenges/widgets/${widget.sitekey}`,'PUT',{name:'LiquidJelly enquiries',mode:'managed',domains:[...new Set([...widget.domains,...domains])]});
}
if (!widget.secret) throw new Error('Turnstile secret was not returned.');
if (process.env.GITHUB_ACTIONS) console.log(`::add-mask::${widget.secret}`);
config.vars.TURNSTILE_SITE_KEY = widget.sitekey;
const production = project.deployment_configs?.production || {};
await api(projectPath,'PATCH',{
  deployment_configs:{production:{
    compatibility_date:config.compatibility_date,
    compatibility_flags:config.compatibility_flags,
    fail_open:false,
    d1_databases:{...production.d1_databases,DB:{id:db.uuid}},
    env_vars:{...production.env_vars,
      TURNSTILE_SITE_KEY:{type:'plain_text',value:widget.sitekey},
      ALLOWED_HOSTS:{type:'plain_text',value:config.vars.ALLOWED_HOSTS},
      TURNSTILE_SECRET_KEY:{type:'secret_text',value:widget.secret}
    }
  }}
});
try {
  // Pages reads wrangler.jsonc from the project directory; it has no --config flag.
  await writeFile('wrangler.jsonc',JSON.stringify(config,null,2));
  execFileSync('npx',['wrangler','d1','migrations','apply','DB','--remote'],{stdio:'inherit'});
  execFileSync('npx',['wrangler','pages','deploy','dist','--project-name',config.name,'--branch','cf-pages','--commit-dirty=true'],{stdio:'inherit'});
  await writeFile('.wrangler/pages-url.txt',`https://${project.subdomain}`);
} finally {
  await writeFile('wrangler.jsonc',originalConfig);
}
