import {readFile,writeFile,mkdtemp,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {execFileSync} from 'node:child_process';
const account = process.env.CLOUDFLARE_ACCOUNT_ID;
const token = process.env.CLOUDFLARE_API_TOKEN;
if (!account || !token) throw new Error('Set CLOUDFLARE_ACCOUNT_ID and the CLOUDFLARE_API_TOKEN repository secret.');
async function api(path, method='GET', body) {
  const response = await fetch(`https://api.cloudflare.com/client/v4/accounts/${account}/${path}`,{
    method,headers:{Authorization:`Bearer ${token}`,'Content-Type':'application/json'},
    ...(body ? {body:JSON.stringify(body)} : {})
  });
  const data = await response.json();
  if (!response.ok || !data.success) throw new Error(`Cloudflare ${method} ${path} failed (${response.status}). Check token permissions and account limits.`);
  return data.result;
}
const config = JSON.parse(await readFile('wrangler.jsonc','utf8'));
const databases = await api('d1/database?name=liquidjelly-enquiries');
let db = databases.find(item=>item.name==='liquidjelly-enquiries');
if (!db) db = await api('d1/database','POST',{name:'liquidjelly-enquiries',jurisdiction:'eu'});
if (db.jurisdiction !== 'eu') throw new Error('The existing database is not EU-restricted. Review before reusing it.');
config.d1_databases[0].database_id = db.uuid;
config.d1_databases[0].jurisdiction = 'eu';
const widgets = await api('challenges/widgets');
const existing = widgets.find(item=>item.name==='LiquidJelly enquiries');
const domains = config.vars.ALLOWED_HOSTS.split(',');
const widget = existing ? await api(`challenges/widgets/${existing.sitekey}`) : await api('challenges/widgets','POST',{name:'LiquidJelly enquiries',mode:'managed',domains});
if (!domains.every(domain=>widget.domains.includes(domain))) throw new Error('Turnstile hostname configuration needs review.');
if (!widget.secret) throw new Error('Turnstile secret was not returned.');
if (process.env.GITHUB_ACTIONS) console.log(`::add-mask::${widget.secret}`);
config.vars.TURNSTILE_SITE_KEY = widget.sitekey;
await writeFile('wrangler.deploy.json',JSON.stringify(config,null,2));
const temp = await mkdtemp(join(tmpdir(),'liquidjelly-deploy-'));
try {
  const secretPath = join(temp,'secrets.json');
  await writeFile(secretPath,JSON.stringify({TURNSTILE_SECRET_KEY:widget.secret}),{mode:0o600});
  execFileSync('npx',['wrangler','d1','migrations','apply','DB','--remote','--config','wrangler.deploy.json'],{stdio:'inherit'});
  execFileSync('npx',['wrangler','deploy','--config','wrangler.deploy.json','--secrets-file',secretPath],{stdio:'inherit'});
} finally {
  await rm(temp,{recursive:true,force:true});
  await rm('wrangler.deploy.json',{force:true});
}
