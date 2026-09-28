const base = 'https://liquidjelly-website.mark-f44.workers.dev';
for (let attempt=0;attempt<6;attempt++) {
  try {
    const home=await fetch(base);
    if (!home.ok || !(await home.text()).includes('Talk through your idea')) throw new Error('Homepage check failed');
    const config=await fetch(`${base}/api/form-config`);
    if (!config.ok || !(await config.json()).siteKey) throw new Error('Form configuration check failed');
    const blocked=await fetch(`${base}/api/enquiries`,{method:'POST',headers:{'Content-Type':'application/json',Origin:base},body:JSON.stringify({name:'Deployment check',email:'test@example.com',company:'',interest:'Something else',message:'Automated rejection check; must not be saved.',website:'',token:'invalid'})});
    if (blocked.status!==400) throw new Error('Form rejection check failed');
    console.log(`Deployment verified: ${base}`); process.exit(0);
  } catch(error) { if(attempt===5) throw error; await new Promise(resolve=>setTimeout(resolve,5000)); }
}
