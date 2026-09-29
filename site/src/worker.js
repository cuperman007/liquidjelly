const interests = new Set(['AI advice & discovery', 'Prototypes & feasibility', 'AI integration & automation', 'Software development', 'Something else']);
const json = (/** @type {unknown} */ body, status = 200) => Response.json(body, {status, headers: {'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff'}});

/** Read at most 24KB, including when Content-Length is missing or forged.
 * @param {Request} request
 */
async function readBody(request) {
  const reader = request.body?.getReader();
  if (!reader) throw new Error('empty');
  const chunks = []; let size = 0;
  for (;;) {
    const {done, value} = await reader.read();
    if (done) break;
    size += value.byteLength;
    if (size > 24000) { await reader.cancel(); throw new Error('oversize'); }
    chunks.push(value);
  }
  const bytes = new Uint8Array(size); let offset = 0;
  for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.length; }
  return JSON.parse(new TextDecoder().decode(bytes));
}

/** @param {unknown} body */
export function validate(body) {
  if (!body || typeof body !== 'object' || Array.isArray(body)) return null;
  const b = /** @type {Record<string, unknown>} */ (body);
  for (const key of ['name','email','company','interest','message','website','token']) if (typeof b[key] !== 'string') return null;
  const name = String(b.name).trim(), email = String(b.email).trim(), company = String(b.company).trim(), message = String(b.message).trim(), interest = String(b.interest);
  if (!name || name.length > 100 || email.length > 254 || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) || company.length > 150 || message.length < 20 || message.length > 5000 || !interests.has(interest) || String(b.token).length > 2048) return null;
  return {name,email,company,message,interest,website:String(b.website),token:String(b.token)};
}

export default {
  /** @param {Request} request @param {Env} env */
  async fetch(request, env) {
    const url = new URL(request.url);
    if (!url.pathname.startsWith('/api/')) return json({error:'Not found.'},404);
    if (url.pathname === '/api/form-config' && request.method === 'GET') {
      return json({siteKey:env.TURNSTILE_SITE_KEY || null});
    }
    if (url.pathname !== '/api/enquiries') return json({error:'Not found.'},404);
    if (request.method !== 'POST') return new Response(null,{status:405,headers:{Allow:'POST'}});
    if (request.headers.get('Origin') !== url.origin) return json({error:'Please submit this form from our website.'},403);
    if (!request.headers.get('Content-Type')?.startsWith('application/json')) return json({error:'Please send the form as JSON.'},415);
    let body;
    try { body = await readBody(request); } catch (error) { return json({error:'Please check the form and try again.'},error instanceof Error && error.message === 'oversize' ? 413 : 400); }
    const values = validate(body);
    if (!values) return json({error:'Please check your name, email, topic and message (20–5,000 characters).'},400);
    if (values.website) return json({error:'This submission could not be accepted.'},400);
    if (!env.TURNSTILE_SECRET_KEY || !env.TURNSTILE_SITE_KEY) return json({error:'The form is temporarily unavailable. Please email hello@liquidjelly.co.uk.'},503);
    try {
      const verify = await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
        method:'POST', headers:{'Content-Type':'application/json'},
        body:JSON.stringify({secret:env.TURNSTILE_SECRET_KEY,response:values.token}), signal:AbortSignal.timeout(8000)
      });
      const result = /** @type {{success?:boolean,hostname?:string,action?:string}} */ (await verify.json());
      if (!verify.ok || !result.success || result.action !== 'enquiry' || !env.ALLOWED_HOSTS.split(',').includes(result.hostname || '')) return json({error:'Please complete the spam check again.'},400);
      const id = crypto.randomUUID();
      await env.DB.prepare('INSERT INTO enquiries (id,name,email,company,interest,message) VALUES (?,?,?,?,?,?)')
        .bind(id,values.name,values.email,values.company,values.interest,values.message).run();
      return json({ok:true,reference:id},201);
    } catch {
      // Never log submitted details, tokens or provider responses.
      console.error(JSON.stringify({event:'enquiry_save_failed'}));
      return json({error:'We could not save your enquiry. Please try again or email hello@liquidjelly.co.uk.'},503);
    }
  }
};
