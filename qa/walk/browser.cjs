const {chromium}=require('playwright');
const fs=require('fs'),assert=require('assert');
(async()=>{
 const browser=await chromium.launch({headless:true});
 const page=await browser.newPage({viewport:{width:1360,height:1000},acceptDownloads:true});
 page.setDefaultTimeout(12000);
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 try {
  await page.goto(process.env.SCENE_URL);await page.waitForFunction(()=>typeof ready!=='undefined'&&ready);
  await page.screenshot({path:'qa/walk/initial-desktop.png'});
  await page.locator('#understood').click();
  async function world(){return page.evaluate(()=>JSON.parse(JSON.stringify(state)));}
  async function clickObject(id,button='left'){
   await page.waitForFunction(id=>hits.some(h=>h.id===id),id);
   const point=await page.evaluate(id=>{
    const h=hits.find(h=>h.id===id),r=canvas.getBoundingClientRect();
    let x=h.foot[0],y=h.foot[1]-(id==='key'?0:35*zoom);
    if(id!=='key'){
     const [l,t,w,hgt]=h.imageRect,mask=masks[h.asset];
     let best=null;
     for(let py=0;py<mask.height;py++)for(let px=0;px<mask.width;px++){
      if(mask.data[(py*mask.width+px)*4+3]<100)continue;
      const sx=l+(px+.5)/mask.width*w,sy=t+(py+.5)/mask.height*hgt,d=(sx-x)**2+(sy-y)**2;
      if(!best||d<best[0])best=[d,sx,sy];
     }
     if(!best)throw Error('No opaque object pixels');
     [,x,y]=best;
    }
    return [r.x+x,r.y+y];
   },id);
   await page.mouse.click(...point,{button});
  }
  async function ground(cell){
   const p=await page.evaluate(cell=>{const p=toScreen(...cell),r=canvas.getBoundingClientRect();if(hitAt(...p))throw Error('Chosen ground pixel hits object');return [p[0]+r.x,p[1]+r.y];},cell);
   await page.mouse.click(...p);
  }
  async function idle(){await page.waitForFunction(()=>!sending&&!queue.length&&!state.path.length,null,{timeout:20000});await page.waitForTimeout(350);}
  await clickObject('contact','right');await page.waitForFunction(()=>state.log.some(l=>l.text.includes('botas gastadas')));
  await ground([7,6]);await idle();assert.deepEqual((await world()).pos,[7,6]);assert((await world()).objects.some(o=>o.id==='key'));
  await clickObject('key','right');await page.waitForFunction(()=>state.log.some(l=>l.text.includes('cinta roja')));
  await clickObject('key');await idle();assert.equal((await world()).inventory.length,1);assert(!(await world()).objects.some(o=>o.id==='key'));
  await page.locator('#inventory-toggle').click();assert.match(await page.locator('#items').innerText(),/Llave de bronce/);await page.locator('#inventory-toggle').click();
  await ground([10,8]);await page.waitForFunction(()=>state.path.length>0);
  const downloadPromise=page.waitForEvent('download');await page.locator('#save').click();const download=await downloadPromise;await download.saveAs('qa/walk/saved-during-walk.json');
  const saved=JSON.parse(fs.readFileSync('qa/walk/saved-during-walk.json'));assert(saved.path.length>0);
  await idle();assert.deepEqual((await world()).pos,[10,8]);
  await page.locator('#file').setInputFiles('qa/walk/saved-during-walk.json');await idle();assert.deepEqual((await world()).pos,[10,8]);assert.equal((await world()).inventory.length,1);
  await clickObject('door');await idle();assert.equal((await world()).complete,true);assert.deepEqual((await world()).pos,[12,3]);
  await page.screenshot({path:'qa/walk/completed-desktop.png'});const completed=await world();
  // Swap regenerated coat atlas with identical authority state.
  await page.locator('#continue').click();const baseline=await world();
  await page.screenshot({path:'qa/walk/base-coat-in-scene.png'});
  await page.goto(process.env.SCENE_URL+'/?look=variant');await page.waitForFunction(()=>typeof ready!=='undefined'&&ready);
  await page.locator('#understood').click();await page.locator('#continue').click();await page.waitForTimeout(400);
  const variant=await world();assert.deepEqual(variant,baseline);
  await page.screenshot({path:'qa/walk/variant-coat-in-scene.png'});
  assert.notDeepEqual(fs.readFileSync('qa/walk/base-coat-in-scene.png'),fs.readFileSync('qa/walk/variant-coat-in-scene.png'));
  await page.locator('#reset').click();await idle();assert.equal((await world()).inventory.length,0);
  await page.setViewportSize({width:390,height:844});await page.waitForTimeout(400);await page.locator('#help-toggle').click();await page.screenshot({path:'qa/walk/initial-mobile.png'});
  const mobile=await page.evaluate(()=>({overflow:document.documentElement.scrollWidth>innerWidth,canvas:canvas.getBoundingClientRect().toJSON(),help:$('onboarding').getBoundingClientRect().toJSON()}));
  assert.equal(mobile.overflow,false);assert.equal(errors.length,0);
  const report={status:'PASS',browser:await browser.version(),real_mouse:true,checks:['inspection in visor','click route around obstacles','key ownership and inventory','save during walk and resume','door approach unlock and enter','regenerated coat in scene with identical authority state','reset','mobile layout no horizontal overflow'],completed,mobile,errors};
  fs.writeFileSync('qa/walk/browser-result.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
 }catch(e){
  await page.screenshot({path:'qa/walk/failure.png'}).catch(()=>{});
  fs.writeFileSync('qa/walk/browser-failure.json',JSON.stringify({error:e.stack,errors,state:await page.evaluate(()=>typeof state==='undefined'?null:state).catch(()=>null)},null,2)+'\n');throw e;
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
