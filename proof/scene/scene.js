'use strict';
const $ = id => document.getElementById(id);
let state, busy = false;
const canvas = $('scene'), ctx = canvas.getContext('2d');
const controls = {NORMAL:'Tenés el control',RESISTING:'Estás resistiendo a la Bestia',BEAST:'La Bestia tiene el control',LUCID_ACTION:'Una sola acción lúcida'};
const errors = {STALE_VIEW:'La partida cambió. Actualicé la vista; elegí nuevamente.',UNSUPPORTED_EXHAUSTION:'Esta prueba todavía no contempla agotar la sangre. Reiniciá para ensayar otra decisión.',SCENE_TIME_LIMIT:'Llegaste al final temporal de esta prueba.',USE_SHORT_STEPS:'Avanzá de a tres segundos mientras haya alimentación o frenesí.',INVALID_SAVE:'No se pudo reconocer la partida.',INCOMPATIBLE_SCENE_SAVE:'Ese archivo pertenece a otra versión de la prueba.'};
async function readView(){const response=await fetch('/api/view');if(!response.ok)throw Error('No pude conectar con la escena.');state=await response.json();render();}
async function act(action, extra={}){
  if(busy || !state)return;
  busy=true;setBusy();$('error').hidden=true;
  const request={revision:state.revision,request_id:crypto.randomUUID(),action,...extra};
  try{
    const response=await fetch('/api/action',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(request)});
    const result=await response.json();
    if(!response.ok){await readView();throw Error(errors[result.error] || 'La acción no está disponible o la partida no es compatible.');}
    state=result;render();
  }catch(error){$('error').textContent=error.message;$('error').hidden=false;}
  finally{busy=false;setBusy();}
}
function setBusy(){document.querySelectorAll('button,select').forEach(el=>el.disabled=busy || !state);}
function render(){
  $('mode').value=state.mode;$('place').textContent=state.location_label;
  $('clock').textContent=state.tick>=86400 ? `Noche 2 · ${state.tick-86400} s` : `Noche 1 · ${state.tick} s`;
  $('blood').textContent=`${state.blood} / 10`;$('blood-meter').value=state.blood;
  $('willpower').textContent=`${state.willpower} / 5`;$('will-meter').value=state.willpower;
  $('humanity').textContent=state.humanity;$('hunger').textContent=state.hungry?'Sentís hambre':'Sin hambre';
  $('control').textContent=state.availability==='asleep'?'Estás durmiendo':controls[state.governance];
  $('control').classList.toggle('beast',state.governance==='BEAST');
  const ids=new Set(state.actions.map(a=>a.id));
  let guide='Elegí una acción. El tiempo avanza cuando vos lo indicás.';
  if(ids.has('feed'))guide='Hay un adulto accesible. Alimentarte puede despertar a la Bestia; la cámara y el testigo están a la vista.';
  if(state.governance==='BEAST')guide='Cada avance permite actuar a la Bestia. Podés gastar voluntad en una acción lúcida. Soltar sin alejarte puede permitir que vuelva a alimentarse.';
  if(state.governance==='LUCID_ACTION')guide=`La acción termina en el segundo ${state.action_until}. Después vuelve la Bestia; retirarte no borra el daño.`;
  if(state.travelling)guide='Estás en camino. Avanzá tres segundos para llegar.';
  if(state.availability==='asleep')guide='Los otros actores siguen actuando mientras dormís. Continuá hasta la próxima noche.';
  if(state.location==='location:L_HAV' && state.governance==='NORMAL' && state.availability!=='asleep')guide='Estás en el refugio. Podés dormir, volver o encargar la retirada del video. Tu contacto sólo puede retirar el original.';
  if(state.tick>=86400 && state.location==='location:L_INC')guide='Volviste a la escena. Podés esperar un minuto para observar lo que ocurra en persona.';
  $('guide').textContent=guide;
  $('warning').hidden=state.governance!=='BEAST' && state.governance!=='LUCID_ACTION';
  $('warning').textContent=state.warnings.at(-1)||'Seguir alimentándote puede matar y provocar degeneración.';
  $('actions').replaceChildren();
  for(const action of state.actions){const button=document.createElement('button');button.textContent=action.label;button.dataset.action=action.id;button.addEventListener('click',()=>act(action.id));$('actions').append(button);}
  if(!state.actions.length){const p=document.createElement('p');p.className='quiet';p.textContent='No hay otra acción disponible durante este intervalo.';$('actions').append(p);}
  $('advance').hidden=state.availability==='asleep' || state.tick>=86460;
  $('minute').hidden=state.tick<86400 || state.tick>=86460 || state.governance!=='NORMAL' || state.travelling;
  $('wake').hidden=state.availability!=='asleep';
  const oldLength=$('log').children.length;$('log').replaceChildren();
  for(const row of state.log){const li=document.createElement('li'),time=document.createElement('time'),text=document.createElement('span');time.textContent=row.tick===null?'Recuerdo':`${row.tick>=86400?'N2 · ':''}${row.tick>=86400?row.tick-86400:row.tick} s`;text.textContent=row.text;li.append(time,text);$('log').append(li);}
  if(state.log.length!==oldLength)$('log').scrollTop=$('log').scrollHeight;
  $('demo').textContent=state.demonstration+' · Prueba local, sin motor de producción.';
  const victim=state.visible.find(a=>a.id==='actor:M0');
  $('scene-description').textContent=state.availability==='asleep'?'Dormís en el refugio.':state.travelling?'Te estás trasladando entre lugares.':victim?.condition==='medical_emergency'?'La víctima sigue viva, en una emergencia médica.':victim?.condition==='dead'?'La víctima murió; las consecuencias permanecen.':state.location==='location:L_INC'?'Estás en el callejón. Lo que ocurra puede dejar testigos y registros.':'Estás en el refugio; lo ocurrido en el callejón permanece.';
  draw();setBusy();
}
// Presentation geometry only. Tile positions never determine legal contact,
// movement, visibility, damage, time or outcomes in the simulation.
function iso(x,y,z=0){return [500+(x-y)*43,155+(x+y)*23-z];}
function poly(points,color,stroke){ctx.beginPath();points.forEach((p,i)=>i?ctx.lineTo(...p):ctx.moveTo(...p));ctx.closePath();ctx.fillStyle=color;ctx.fill();if(stroke){ctx.strokeStyle=stroke;ctx.lineWidth=1;ctx.stroke();}}
function tile(x,y,color){poly([iso(x,y),iso(x+1,y),iso(x+1,y+1),iso(x,y+1)],color,'#334248');}
function box(x,y,w,d,h,top,left,right){poly([iso(x,y),iso(x,y+d),iso(x,y+d,h),iso(x,y,h)],left);poly([iso(x,y+d),iso(x+w,y+d),iso(x+w,y+d,h),iso(x,y+d,h)],right);poly([iso(x,y,h),iso(x+w,y,h),iso(x+w,y+d,h),iso(x,y+d,h)],top);}
function label(text,x,y,color='#b3c1c2'){ctx.font='13px system-ui';ctx.textAlign='center';ctx.fillStyle='#0c151bea';const width=ctx.measureText(text).width+20;ctx.fillRect(x-width/2,y-15,width,24);ctx.fillStyle=color;ctx.fillText(text,x,y+2);}
function person(x,y,color,name,condition){const [sx,sy]=iso(x,y);ctx.fillStyle='#060c10aa';ctx.beginPath();ctx.ellipse(sx,sy+5,16,7,0,0,Math.PI*2);ctx.fill();
  if(condition==='dead'){ctx.fillStyle='#a59b8e';ctx.fillRect(sx-19,sy-6,35,9);ctx.beginPath();ctx.arc(sx-23,sy-4,6,0,Math.PI*2);ctx.fill();label(name+' · sin vida',sx,sy+32);return;}
  ctx.fillStyle=color;ctx.beginPath();ctx.moveTo(sx-10,sy);ctx.lineTo(sx-7,sy-28);ctx.quadraticCurveTo(sx,sy-35,sx+7,sy-28);ctx.lineTo(sx+10,sy);ctx.closePath();ctx.fill();ctx.fillStyle='#c9b6a3';ctx.beginPath();ctx.arc(sx,sy-39,7,0,Math.PI*2);ctx.fill();ctx.strokeStyle='#c9b6a3';ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(sx-7,sy-25);ctx.lineTo(sx-13,sy-11);ctx.moveTo(sx+7,sy-25);ctx.lineTo(sx+14,sy-13);ctx.stroke();label(name,sx,sy+32,color);if(condition==='medical_emergency'||condition==='weak')label(condition==='weak'?'Débil':'Emergencia médica',sx,sy+59,'#efa596');}
function draw(){
  ctx.clearRect(0,0,1000,620);const bg=ctx.createLinearGradient(0,0,0,620);bg.addColorStop(0,'#15252d');bg.addColorStop(1,'#101a20');ctx.fillStyle=bg;ctx.fillRect(0,0,1000,620);
  const refuge=state.location==='location:L_HAV';
  for(let sum=0;sum<16;sum++)for(let x=0;x<8;x++){const y=sum-x;if(y>=0&&y<8)tile(x,y,(x*7+y*11)%3===0?'#2d3d42':'#26363c');}
  box(0,0,7,0.45,104,'#4a5559','#273a43','#3c4b51');box(0,.45,.5,5.7,104,'#4a5559','#30434a','#24353d');
  if(refuge){box(1,1.5,1.7,2.7,17,'#777469','#504f47','#646359');box(1.15,1.7,1.35,.65,25,'#a19783','#655f53','#7d7365');box(5,1,1,1,38,'#5d655e','#33443f','#48544b');const [wx,wy]=iso(4,.48,50);ctx.fillStyle='#d4b379';ctx.fillRect(wx-26,wy-35,50,50);ctx.strokeStyle='#1d2c35';ctx.lineWidth=5;ctx.strokeRect(wx-26,wy-35,50,50);ctx.beginPath();ctx.moveTo(wx,wy-35);ctx.lineTo(wx,wy+15);ctx.stroke();label('Salida al callejón',...iso(7,5.8),'#dcbb80');}
  else{box(.9,1.8,1,1.4,40,'#59605a','#344341','#45514a');box(1.1,3.8,.8,.8,17,'#777364','#4c5149','#696b5d');const [cx,cy]=iso(5,.4,72);ctx.strokeStyle='#768e99';ctx.lineWidth=4;ctx.beginPath();ctx.moveTo(cx,cy-20);ctx.lineTo(cx,cy);ctx.lineTo(cx-16,cy+8);ctx.stroke();ctx.fillStyle='#93a7ae';ctx.fillRect(cx-25,cy+3,19,10);ctx.fillStyle='#dca284';ctx.fillRect(cx-27,cy+7,3,3);if(state.camera_visible)label('Cámara',cx,cy+38);const [lx,ly]=iso(.6,5.8,72);ctx.strokeStyle='#64787d';ctx.lineWidth=4;ctx.beginPath();ctx.moveTo(lx,ly+72);ctx.lineTo(lx,ly);ctx.lineTo(lx+20,ly-4);ctx.stroke();const glow=ctx.createRadialGradient(lx+20,ly,0,lx+20,ly,100);glow.addColorStop(0,'#dfba7540');glow.addColorStop(1,'#dfba7500');ctx.fillStyle=glow;ctx.fillRect(lx-80,ly-100,200,200);label('Paso al refugio',...iso(7,5.8),'#dcbb80');}
  const positions={'actor:V0':[4.3,5.2],'actor:M0':[4.35,4.25],'actor:W1':[6.2,2.8],'actor:G1':[5.7,4.2],'actor:I1':[6.7,3.2],'actor:W2':[5.4,2.8]};
  const figures=[...state.visible].sort((a,b)=>positions[a.id].reduce((a,b)=>a+b)-positions[b.id].reduce((a,b)=>a+b));
  for(const actor of figures){const pos=positions[actor.id];person(...pos,actor.id==='actor:V0'?(state.governance==='BEAST'?'#e38f80':'#dfbd80'):'#a4b5b6',actor.label,actor.condition);}
  if(state.travelling)person(7,5.9,'#dfbd80','En camino');
  if(state.availability==='asleep'){const [sx,sy]=iso(1.8,2.5,28);label('Dormís',sx,sy,'#dfbd80');ctx.fillStyle='#0b14256b';ctx.fillRect(0,0,1000,620);}
  if(state.governance==='BEAST'){ctx.strokeStyle='#ca716f';ctx.lineWidth=2;ctx.strokeRect(2,2,996,616);}
}
$('reset').addEventListener('click',()=>act('reset',{mode:$('mode').value}));
$('mode').addEventListener('change',()=>act('reset',{mode:$('mode').value}));
for(const id of ['advance','minute','wake'])$(id).addEventListener('click',()=>act(id));
$('save').addEventListener('click',async()=>{if(busy)return;try{const response=await fetch('/api/save');if(!response.ok)throw Error('No pude guardar la partida.');const url=URL.createObjectURL(await response.blob()),a=document.createElement('a');a.href=url;a.download='noche-guardada.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}catch(error){$('error').textContent=error.message;$('error').hidden=false;}});
$('load').addEventListener('click',()=>$('file').click());
$('file').addEventListener('change',async event=>{const file=event.target.files[0];if(file){if(file.size>2*1024*1024){$('error').textContent='La partida supera el tamaño de esta prueba.';$('error').hidden=false;}else await act('load',{snapshot:await file.text()});}event.target.value='';});
document.addEventListener('keydown',event=>{if(event.code==='Space'&&!['INPUT','SELECT','BUTTON'].includes(document.activeElement.tagName)&&!$('advance').hidden){event.preventDefault();act('advance');}});
readView().catch(error=>{$('error').textContent=error.message;$('error').hidden=false;setBusy();});
