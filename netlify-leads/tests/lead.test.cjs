const test = require('node:test');
const assert = require('node:assert/strict');
const api=require('../netlify/functions/lead.js');
const origin='https://vadym9083.github.io';
const form={name:'Tester',network:'telegram',contact:'@target_vadym',lang:'ru',
page:'https://vadym9083.github.io/gpt/?lang=ru',utm_source:'meta'};
function req(method, body, o=origin){
 return {httpMethod:method,headers:{origin:o},body: body===undefined?undefined:JSON.stringify(body)};
}
test('health never calls upstream',async ()=>{
 const r=await api.handler(req('GET'));
 assert.equal(r.statusCode,200);
 assert.equal(JSON.parse(r.body).status,'ready');
});
test('preflight allowed with CORS',async ()=>{
 const r=await api.handler(req('OPTIONS'));
 assert.equal(r.statusCode,204);
 assert.equal(r.headers['Access-Control-Allow-Origin'],origin);
});
test('rejects untrusted origins',async ()=>{
 const r=await api.handler(req('POST',form,'https://spam.example'));
 assert.equal(r.statusCode,403);
});
test('rejects invalid contacts',async ()=>{
 const r=await api.handler(req('POST',{...form,contact:'й'}));
 assert.equal(r.statusCode,422);
});
test('forwards valid lead exactly once with site Origin and confirms success',async t=>{
 const f=global.fetch;let calls=0;
 global.fetch=async (url,opts)=>{
  calls++;
  assert.equal(url,'https://target-lb-leads.vadym9083.workers.dev/');
  assert.equal(opts.headers.Origin,origin);
  assert.equal(JSON.parse(opts.body).contact,'@target_vadym');
  return {ok:true,json:async()=>({success:true})};
 };
 t.after(()=>global.fetch=f);
 const r=await api.handler(req('POST',form));
 assert.equal(r.statusCode,200);assert.deepEqual(JSON.parse(r.body),{success:true});
 assert.equal(calls,1);
});
test('does not confirm when upstream rejects',async t=>{
 const f=global.fetch;
 global.fetch=async ()=>({ok:true,json:async()=>({success:false})});
 t.after(()=>global.fetch=f);
 const r=await api.handler(req('POST',form));
 assert.equal(r.statusCode,502);
 assert.equal(JSON.parse(r.body).success,false);
});
