/* Executes the real frontend against the local authority with a small DOM
 * harness. Verifies events/data; does not claim browser CSS/layout coverage.
 * Node stdlib only. Server must be running on port 8765 (or SCENE_URL).
 */
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path'),crypto=require('node:crypto');
const base=process.env.SCENE_URL || 'http://127.0.0.1:8765';
class Element{
  constructor(tagName='DIV'){this.tagName=tagName;this.children=[];this.listeners={};this.dataset={};this.hidden=false;this.disabled=false;this.textContent='';this.classList={toggle:()=>{}};this.value='';this.files=[];}
  addEventListener(type,fn){this.listeners[type]=fn;}
  append(...els){this.children.push(...els);}
  replaceChildren(...els){this.children=[...els];}
  click(){if(!this.disabled)return this.listeners.click?.({target:this});}
}
const ids=['scene','error','mode','place','clock','blood','blood-meter','willpower','will-meter','humanity','hunger','control','guide','warning','actions','advance','minute','wake','log','demo','scene-description','reset','save','load','file'];
const elements=Object.fromEntries(ids.map(id=>[id,new Element()]));
for(const id of ['advance','minute','wake','reset','save','load'])elements[id].tagName='BUTTON';elements.mode.tagName='SELECT';elements.file.tagName='INPUT';
const drawing=[];const context={measureText:text=>({width:text.length*7}),createLinearGradient:()=>({addColorStop(){}}),createRadialGradient:()=>({addColorStop(){}})};
for(const name of ['beginPath','lineTo','moveTo','closePath','fill','stroke','clearRect','fillRect','strokeRect','fillText','ellipse','arc','quadraticCurveTo'])context[name]=(...args)=>drawing.push({name,args});
elements.scene.getContext=()=>context;
let downloadBlob;
const document={getElementById:id=>elements[id],createElement:tag=>new Element(tag.toUpperCase()),querySelectorAll:()=>[...Object.values(elements),...elements.actions.children].filter(el=>['BUTTON','SELECT'].includes(el.tagName)),addEventListener(){},activeElement:new Element('BODY')};
const sandbox={document,console,crypto,fetch:(url,options)=>fetch(base+url,options),setTimeout,URL:{createObjectURL:b=>{downloadBlob=b;return 'blob:test';},revokeObjectURL(){}},window:{},Blob};
const wait=async predicate=>{for(let i=0;i<500;i++){if(predicate())return;await new Promise(r=>setTimeout(r,10));}throw Error('UI timeout: '+elements.error.textContent);};
(async()=>{
  let view=await (await fetch(base+'/api/view')).json();
  await fetch(base+'/api/action',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({revision:view.revision,request_id:crypto.randomUUID(),action:'reset',mode:'control'})});
  vm.createContext(sandbox);vm.runInContext(fs.readFileSync(path.join(__dirname,'../../proof/scene/scene.js'),'utf8'),sandbox);
  const clickAction=async id=>{await wait(()=>!elements.advance.disabled);const button=elements.actions.children.find(el=>el.dataset.action===id);assert(button,'Missing '+id);await button.click();};
  await wait(()=>elements.blood.textContent==='2 / 10');
  elements.mode.value='pressure';await elements.mode.listeners.change();assert.match(elements.demo.textContent,/ensayo/);
  await clickAction('feed');assert.equal(elements.control.textContent,'La Bestia tiene el control');assert.equal(elements.warning.hidden,false);
  await elements.advance.click();assert.equal(elements.blood.textContent,'5 / 10');
  await clickAction('lucid_retreat');assert.equal(elements.willpower.textContent,'4 / 5');assert.equal(elements.control.textContent,'Una sola acción lúcida');
  await elements.save.click();assert(downloadBlob);const saved=await downloadBlob.text();
  await elements.advance.click();assert.equal(elements.place.textContent,'Refugio');
  elements.file.files=[{size:saved.length,text:async()=>saved}];await elements.file.listeners.change({target:elements.file});assert.equal(elements.control.textContent,'Una sola acción lúcida');assert.equal(elements.willpower.textContent,'4 / 5');
  for(let i=0;i<4;i++)await elements.advance.click();assert.equal(elements.control.textContent,'Tenés el control');assert.equal(elements.place.textContent,'Refugio');assert.equal(elements.blood.textContent,'5 / 10');assert(drawing.length>300);assert(elements.log.children.some(el=>el.children[1]?.textContent.includes('emergencia médica')));
  await elements.reset.click();await clickAction('feed');for(let i=0;i<6;i++)await elements.advance.click();assert.equal(elements.humanity.textContent,6);assert.match(elements['scene-description'].textContent,/murió/);
  assert(elements.error.hidden);console.log(JSON.stringify({status:'PASS',frontend:'actual scene.js',authority:base,checks:['mode change','live feeding','paid retreat','save download','file restore','lucid completion','death and humanity consequence','canvas draw calls'],limit:'DOM/canvas harness; not browser layout verification'}));
})().catch(error=>{console.error(error);process.exitCode=1;});
