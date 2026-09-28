import {test, before, after} from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {Miniflare, convertV4MiniflareOptions} from 'miniflare';
import worker from '../src/worker.js';
let mf, db;
const origin='https://liquidjelly.example';
const valid={name:'Test enquiry',email:'test@example.com',company:'Example',interest:'Software development',message:'We would like to explore a workflow improvement.',website:'',token:'valid-test-token'};
const env=()=>({DB:db,TURNSTILE_SECRET_KEY:'test-secret',TURNSTILE_SITE_KEY:'test-site',ALLOWED_HOSTS:'liquidjelly.example'});
const request=(body=valid,headers={})=>new Request(`${origin}/api/enquiries`,{method:'POST',headers:{Origin:origin,'Content-Type':'application/json',...headers},body:JSON.stringify(body)});
before(async()=>{
 mf=new Miniflare(convertV4MiniflareOptions({modules:true,script:'export default {fetch(){return new Response("test")}}',compatibilityDate:'2026-09-28',d1Databases:['DB']}));
 db=await mf.getD1Database('DB');
 const sql=await readFile(new URL('../migrations/0001_enquiries.sql',import.meta.url),'utf8');
 for(const statement of sql.split(';').filter(x=>x.trim())) await db.prepare(statement).run();
});
after(async()=>{await mf.dispose();});
test('valid enquiry is persisted exactly; HTML and quotes remain inert data',async t=>{
 t.mock.method(globalThis,'fetch',async()=>Response.json({success:true,hostname:'liquidjelly.example',action:'enquiry'}));
 const body={...valid,message:"An idea with <script>alert('x')</script> and SQL ' characters."};
 const response=await worker.fetch(request(body),env());
 assert.equal(response.status,201);
 const {reference}=await response.json();
 const row=await db.prepare('SELECT * FROM enquiries WHERE id=?').bind(reference).first();
 assert.equal(row.message,body.message); assert.equal(row.email,body.email);
});
test('invalid input and honeypot never reach Turnstile',async t=>{
 const fetch=t.mock.method(globalThis,'fetch',async()=>{throw Error('must not call');});
 for(const change of [{email:'bad'}, {message:'short'}, {message:'x'.repeat(5001)}, {interest:'Unknown'}, {name:''}, {website:'spam.example'}, {name:99}]) assert.equal((await worker.fetch(request({...valid,...change}),env())).status,400);
 assert.equal(fetch.mock.callCount(),0);
});
test('cross-origin and oversized requests are rejected',async()=>{
 assert.equal((await worker.fetch(request(valid,{Origin:'https://other.example'}),env())).status,403);
 assert.equal((await worker.fetch(request({...valid,message:'x'.repeat(25000)}),env())).status,413);
});
test('Turnstile failure, wrong hostname and wrong action cannot save',async t=>{
 for(const result of [{success:false},{success:true,hostname:'attacker.example',action:'enquiry'},{success:true,hostname:'liquidjelly.example',action:'other'}]) {
  t.mock.method(globalThis,'fetch',async()=>Response.json(result));
  assert.equal((await worker.fetch(request(),env())).status,400);
  t.mock.restoreAll();
 }
 const row=await db.prepare('SELECT count(*) AS count FROM enquiries').first(); assert.equal(row.count,1);
});
test('missing configuration and database failures never report success',async t=>{
 assert.equal((await worker.fetch(request(),{...env(),TURNSTILE_SECRET_KEY:''})).status,503);
 t.mock.method(globalThis,'fetch',async()=>Response.json({success:true,hostname:'liquidjelly.example',action:'enquiry'}));
 t.mock.method(console,'error',()=>{});
 assert.equal((await worker.fetch(request(),{...env(),DB:{prepare(){throw Error('unavailable');}}})).status,503);
});
test('API has no public enquiry listing route',async()=>{
 assert.equal((await worker.fetch(new Request(`${origin}/api/enquiries`),env())).status,405);
 assert.equal((await worker.fetch(new Request(`${origin}/api/admin`),env())).status,404);
});
test('retention removes expired enquiries and preserves current records',async()=>{
 await db.prepare("INSERT INTO enquiries (id,created_at,name,email,interest,message) VALUES ('old','2020-01-01T00:00:00.000Z','Old','old@example.com','Something else','An older enquiry for retention testing')").run();
 await worker.scheduled({},env());
 assert.equal(await db.prepare("SELECT id FROM enquiries WHERE id='old'").first(),null);
 assert.equal((await db.prepare('SELECT count(*) AS count FROM enquiries').first()).count,1);
});
