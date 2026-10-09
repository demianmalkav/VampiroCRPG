'use strict';
const $=id=>document.getElementById(id),canvas=$('scene'),ctx=canvas.getContext('2d');
let state,art,images={},masks={},queue=[],sending=false,receivedAt=0,lastPulse=0,hover=null,hits=[],destination=null;
let camera=null,zoom=1,width=0,height=0,logLength=-1,successDismissed=false,ready=false,feedback=[];
const directions=[[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1]];
const iso=(x,y,z=0)=>[(y-x)*44,(x+y)*22-z*53.89];
function time(ms){const seconds=Math.floor(ms/1000);return String(Math.floor(seconds/60)).padStart(2,'0')+':'+String(seconds%60).padStart(2,'0');}
function error(text){$('toast').textContent=text;$('toast').hidden=false;setTimeout(()=>$('toast').hidden=true,4200);feedback.push({tick_ms:state?.tick_ms||0,text});feedback=feedback.slice(-5);logLength=-1;showLog();}
function showLog(){if(!state)return;const rows=[...state.log,...feedback];if(rows.length===logLength)return;logLength=rows.length;$('log').replaceChildren();for(const row of rows){const li=document.createElement('li'),t=document.createElement('time'),p=document.createElement('span');t.textContent=time(row.tick_ms);p.textContent=row.text;li.append(t,p);$('log').append(li);}$('log').scrollTop=$('log').scrollHeight;}
function apply(view){state=view;receivedAt=performance.now();if(!camera)camera=iso(...state.pos);$('connection').textContent='Partida local';$('clock').textContent=time(state.tick_ms);$('inventory-count').textContent=state.inventory.length;
 $('goal').textContent=state.complete?'Entraste al refugio.':state.inventory.length?'Llevá la llave hasta la puerta del refugio.':'Encontrá tu llave y entrá al refugio.';
 $('progress').textContent=state.complete?'Podés seguir explorando o reiniciar.':state.inventory.length?'Hacé clic en la puerta para acercarte, abrirla y entrar.':'La mujer puede orientarte. Mirá junto al contenedor.';
 $('movement').textContent=state.path.length?(state.pending?'Acercándote para interactuar…':'Caminando…'):'Clic en el suelo para caminar · clic derecho para mirar';
 $('success').hidden=!state.complete||successDismissed;
 $('items').replaceChildren();if(!state.inventory.length){$('items').textContent='Todavía no llevás ningún objeto.';}else{const img=document.createElement('img');img.src='/art/key.png';img.alt='Llave de bronce';const label=document.createElement('span');label.textContent='Llave de bronce';$('items').append(img,label);}showLog();}
async function refresh(){const response=await fetch('/api/view');if(!response.ok)throw Error('No pude conectar con la partida.');apply(await response.json());}
function enqueue(action,payload={},extra={}){if(!ready)return;if(action!=='advance'){$('onboarding').hidden=true;queue=queue.filter(c=>c.action!=='advance');}queue.push({action,payload,...extra});drain();}
async function drain(){if(sending||!queue.length||!state)return;sending=true;const command=queue.shift();const request={...command,revision:state.revision,request_id:crypto.randomUUID()};
 try{const response=await fetch('/api/command',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(request)});const result=await response.json();if(!response.ok){queue=[];await refresh();error(result.error==='STALE_VIEW'?'La partida cambió en otra ventana. Elegí nuevamente.':result.error);destination=null;}else apply(result);}
 catch(e){queue=[];$('connection').textContent='Sin conexión';error('Se interrumpió la conexión. Mantené abierta la consola de la partida.');}
 finally{sending=false;drain();}}
function resize(){const rect=canvas.getBoundingClientRect(),ratio=Math.min(devicePixelRatio||1,2);width=rect.width;height=rect.height;canvas.width=Math.round(width*ratio);canvas.height=Math.round(height*ratio);ctx.setTransform(ratio,0,0,ratio,0,0);zoom=Math.max(.65,Math.min(1.1,width/1150));}
function toScreen(x,y,z=0){const p=iso(x,y,z);return [width*.5+(p[0]-camera[0])*zoom,height*.56+(p[1]-camera[1])*zoom];}
function fromScreen(x,y){const u=(x-width*.5)/zoom+camera[0],v=(y-height*.56)/zoom+camera[1];return [Math.floor(v/44-u/88+.5),Math.floor(v/44+u/88+.5)];}
function poly(points,fill,stroke){ctx.beginPath();points.forEach((p,i)=>i?ctx.lineTo(...p):ctx.moveTo(...p));ctx.closePath();ctx.fillStyle=fill;ctx.fill();if(stroke){ctx.strokeStyle=stroke;ctx.lineWidth=.6;ctx.stroke();}}
function seeded(x,y,n=0){let v=(x*374761393+y*668265263+n*1274126177)|0;v=(v^(v>>>13))*1274126177;return ((v^(v>>>16))>>>0)/4294967295;}
function floor(){
 const gradient=ctx.createLinearGradient(0,0,0,height);gradient.addColorStop(0,'#18252d');gradient.addColorStop(1,'#10171b');ctx.fillStyle=gradient;ctx.fillRect(0,0,width,height);
 for(let y=1;y<state.map.height-1;y++)for(let x=1;x<state.map.width-1;x++){
  const interior=x>=11&&x<=14&&y<=3,shade=interior?39:Math.floor(34+seeded(x,y)*9),color=interior?'rgb('+shade+','+(shade-2)+','+(shade-4)+')':'rgb('+(shade-6)+','+(shade+2)+','+(shade+5)+')';
  poly([[-.5,-.5],[.5,-.5],[.5,.5],[-.5,.5]].map(([a,b])=>toScreen(x+a,y+b)),color,'#47525355');
  const p=toScreen(x,y);if(seeded(x,y,3)>.6){ctx.strokeStyle='#65707544';ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(p[0]-13*zoom,p[1]-3*zoom);ctx.lineTo(p[0]-2*zoom,p[1]+3*zoom);ctx.lineTo(p[0]+10*zoom,p[1]+2*zoom);ctx.stroke();}
  if(seeded(x,y,4)>.85&&!interior){ctx.fillStyle='#54727b33';ctx.beginPath();ctx.ellipse(p[0],p[1]+5*zoom,25*zoom,8*zoom,.1,0,Math.PI*2);ctx.fill();ctx.strokeStyle='#84999933';ctx.beginPath();ctx.ellipse(p[0]+3*zoom,p[1]+5*zoom,18*zoom,3*zoom,.1,0,Math.PI);ctx.stroke();}
  if(seeded(x,y,5)>.92)poly([[p[0]-8*zoom,p[1]],[p[0]+3*zoom,p[1]-4*zoom],[p[0]+8*zoom,p[1]],[p[0]-3*zoom,p[1]+5*zoom]],'#938d7655');
 }
 for(const light of [[3,9,125,'#c49b5740'],[11,4,100,'#7f9ca333']]){const p=toScreen(light[0],light[1]),g=ctx.createRadialGradient(p[0],p[1],0,p[0],p[1],light[2]*zoom);g.addColorStop(0,light[3]);g.addColorStop(1,'#c49b5700');ctx.fillStyle=g;ctx.fillRect(p[0]-light[2]*zoom,p[1]-light[2]*zoom,2*light[2]*zoom,2*light[2]*zoom);}
 if(destination){const p=toScreen(...destination);ctx.strokeStyle='#cbb88aa0';ctx.lineWidth=1.5;ctx.beginPath();ctx.ellipse(p[0],p[1],18*zoom,9*zoom,0,0,Math.PI*2);ctx.stroke();}
}
function sprite(asset,x,y,options={}){const meta=art.assets[asset],image=images[asset];if(!meta||!image)return;const p=toScreen(x,y),column=options.column||0,row=options.row||0,[sw,sh]=meta.size,dw=sw*meta.scale*zoom,dh=sh*meta.scale*zoom,left=p[0]-meta.anchor[0]*meta.scale*zoom,top=p[1]-meta.anchor[1]*meta.scale*zoom;
 ctx.globalAlpha=options.alpha??1;ctx.drawImage(image,column*sw,row*sh,sw,sh,left,top,dw,dh);ctx.globalAlpha=1;
 if(options.object){const target=options.object,padding=target.id==='key'?13*zoom:0;hits.push({id:target.id,name:target.name,asset,rect:[left-padding,top-padding,dw+2*padding,dh+2*padding],imageRect:[left,top,dw,dh],foot:p});if(hover?.id===target.id){ctx.strokeStyle='#e2c894';ctx.lineWidth=1;ctx.beginPath();ctx.ellipse(p[0],p[1]+2*zoom,target.id==='dumpster'?62*zoom:20*zoom,target.id==='dumpster'?26*zoom:10*zoom,0,0,Math.PI*2);ctx.stroke();}}
}
function draw(now){requestAnimationFrame(draw);if(!ready||!state||!art||!width||!camera)return;
 let pos=[...state.pos],fraction=state.progress_ms/state.step_ms,face=state.facing;
 if(state.path.length){fraction=Math.min(.99,(state.progress_ms+Math.min(now-receivedAt,200))/state.step_ms);const next=state.path[0];pos=[state.pos[0]+(next[0]-state.pos[0])*fraction,state.pos[1]+(next[1]-state.pos[1])*fraction];face=directions.findIndex(d=>d[0]===next[0]-state.pos[0]&&d[1]===next[1]-state.pos[1]);}
 const target=iso(...pos);camera[0]+=(target[0]-camera[0])*.07;camera[1]+=(target[1]-camera[1])*.07;
 floor();hits=[];const draws=[];
 for(const cell of state.map.walls){const tall=cell[0]!==9&&cell[0]!==2,alongY=[9,2,10,15].includes(cell[0]),asset=tall?(alongY?'wall_tall_y':'wall_tall_x'):'wall_low_y',depth=cell[0]+cell[1],alpha=depth>pos[0]+pos[1]&&Math.hypot(cell[0]-pos[0],cell[1]-pos[1])<3?.32:1;draws.push({depth,run:()=>sprite(asset,...cell,{alpha})});}
 for(const prop of [{asset:'lamp',pos:[3,9]},{asset:'window',pos:[11,4.15]},{asset:'crate',pos:[3,4]},{asset:'bottle',pos:[4,8]},{asset:'bottle',pos:[3.4,8.2]}])draws.push({depth:prop.pos[0]+prop.pos[1],run:()=>sprite(prop.asset,...prop.pos)});
 for(const object of state.objects){const asset=object.id==='door'&&state.door_open?'door_open':object.asset;draws.push({depth:object.pos[0]+object.pos[1]+.01,run:()=>{if(object.id==='key'){const p=toScreen(...object.pos);ctx.fillStyle='#d3b66b35';ctx.beginPath();ctx.ellipse(p[0],p[1],17*zoom,8*zoom,0,0,Math.PI*2);ctx.fill();}if(object.id==='contact'){const p=toScreen(...object.pos);ctx.fillStyle='#070c0e66';ctx.beginPath();ctx.ellipse(p[0],p[1]+3*zoom,12*zoom,5*zoom,0,0,Math.PI*2);ctx.fill();}sprite(asset,...object.pos,{object});}});
 }
 draws.push({depth:pos[0]+pos[1]+.02,run:()=>{const p=toScreen(...pos);ctx.fillStyle='#080d0f99';ctx.beginPath();ctx.ellipse(p[0],p[1]+4*zoom,13*zoom,6*zoom,0,0,Math.PI*2);ctx.fill();const col=state.path.length?1+Math.floor((((state.steps+fraction)/2)%1)*8):0;sprite('player',...pos,{row:Math.max(0,face),column:col});ctx.strokeStyle='#d5bb8866';ctx.beginPath();ctx.ellipse(p[0],p[1]+3*zoom,17*zoom,8*zoom,0,0,Math.PI*2);ctx.stroke();}});
 draws.sort((a,b)=>a.depth-b.depth);for(const item of draws)item.run();
 const label=toScreen(11.5,4,2.65);ctx.font=Math.max(10,Math.round(13*zoom))+'px Georgia';ctx.textAlign='center';ctx.fillStyle='#ceb68a';ctx.fillText('REFUGIO',...label);
 const p=toScreen(...state.map.entry);if(p[0]<50||p[0]>width-50||p[1]<100||p[1]>height-35){const dx=p[0]-width/2,dy=p[1]-height/2,t=Math.min((width/2-40)/Math.max(1,Math.abs(dx)),(height/2-110)/Math.max(1,Math.abs(dy)));ctx.fillStyle='#d4bc8f';ctx.font='11px system-ui';ctx.fillText('Refugio →',width/2+dx*t,height/2+dy*t);}
 if(state.path.length&&!document.hidden&&now-lastPulse>=140&&!sending&&!queue.length){const elapsed=Math.max(1,Math.min(250,Math.round(now-lastPulse)));lastPulse=now;enqueue('advance',{ms:elapsed});}else if(!state.path.length||document.hidden)lastPulse=now;
}
function hitAt(x,y){return [...hits].reverse().find(h=>{const [left,top,w,hgt]=h.rect;if(x<left||x>left+w||y<top||y>top+hgt)return false;if(h.id==='key')return true;const [l,t,dw,dh]=h.imageRect,mask=masks[h.asset],px=Math.floor((x-l)/dw*mask.width),py=Math.floor((y-t)/dh*mask.height);return px>=0&&py>=0&&px<mask.width&&py<mask.height&&mask.data[(py*mask.width+px)*4+3]>30;});}
canvas.addEventListener('pointermove',event=>{if(!ready||!camera)return;const rect=canvas.getBoundingClientRect(),x=event.clientX-rect.left,y=event.clientY-rect.top;hover=hitAt(x,y);canvas.style.cursor=hover?'pointer':'crosshair';$('tooltip').hidden=!hover;if(hover){$('tooltip').textContent=hover.name+' · clic: actuar · clic derecho: mirar';$('tooltip').style.left=Math.min(width-280,Math.max(8,x+15))+'px';$('tooltip').style.top=Math.max(10,y-34)+'px';}});
canvas.addEventListener('pointerleave',()=>{hover=null;$('tooltip').hidden=true;});
canvas.addEventListener('click',event=>{if(!ready||!camera)return;canvas.focus();const r=canvas.getBoundingClientRect(),x=event.clientX-r.left,y=event.clientY-r.top,hit=hitAt(x,y);if(hit){enqueue('use',{target:hit.id});destination=null;}else{const cell=fromScreen(x,y);destination=cell;enqueue('move',{cell});}});
canvas.addEventListener('contextmenu',event=>{event.preventDefault();if(!ready||!camera)return;const r=canvas.getBoundingClientRect(),hit=hitAt(event.clientX-r.left,event.clientY-r.top);if(hit)enqueue('inspect',{target:hit.id});else error('Señalá una persona u objeto visible para examinarlo.');});
$('understood').addEventListener('click',()=>$('onboarding').hidden=true);
$('help-toggle').addEventListener('click',()=>{$('inventory').hidden=true;$('onboarding').hidden=!$('onboarding').hidden;});
$('inventory-toggle').addEventListener('click',()=>{$('onboarding').hidden=true;$('inventory').hidden=!$('inventory').hidden;});
$('continue').addEventListener('click',()=>{successDismissed=true;$('success').hidden=true;});
$('reset').addEventListener('click',()=>{queue=[];successDismissed=false;feedback=[];logLength=-1;camera=null;destination=null;enqueue('reset');});
$('save').addEventListener('click',async()=>{try{const response=await fetch('/api/save');if(!response.ok)throw Error();const url=URL.createObjectURL(await response.blob()),a=document.createElement('a');a.href=url;a.download='pasaje-partida.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}catch{error('No se pudo guardar la partida.');}});
$('load').addEventListener('click',()=>$('file').click());
$('file').addEventListener('change',async event=>{const file=event.target.files[0];if(file){if(file.size>2*1024*1024)error('El archivo es demasiado grande para esta muestra.');else{queue=[];successDismissed=false;feedback=[];logLength=-1;camera=null;enqueue('load',{}, {snapshot:await file.text()});}}event.target.value='';});
document.addEventListener('keydown',event=>{if(!ready||['INPUT','SELECT'].includes(document.activeElement.tagName))return;if(event.key==='Escape'){event.preventDefault();$('onboarding').hidden=true;$('inventory').hidden=true;enqueue('move',{cell:state.pos});destination=null;}else if(event.key.toLowerCase()==='i')$('inventory-toggle').click();else{const keys={ArrowUp:[-1,-1],w:[-1,-1],ArrowDown:[1,1],s:[1,1],ArrowLeft:[1,-1],a:[1,-1],ArrowRight:[-1,1],d:[-1,1]},vector=keys[event.key]||keys[event.key.toLowerCase()];if(vector&&!event.repeat){event.preventDefault();enqueue('move',{cell:[state.pos[0]+vector[0],state.pos[1]+vector[1]]});}}});
window.addEventListener('resize',resize);document.addEventListener('visibilitychange',()=>lastPulse=performance.now());
(async()=>{try{
 art=await (await fetch('/art/index.json')).json();if(new URLSearchParams(location.search).get('look')==='variant'){const v=await (await fetch('/art/variant/index.json')).json();art.assets.player={...v.assets.player,file:'variant/'+v.assets.player.file};}
 await Promise.all(Object.entries(art.assets).map(([key,meta])=>new Promise((resolve,reject)=>{const image=new Image();image.onload=()=>{images[key]=image;if(key!=='player'){const c=document.createElement('canvas');c.width=meta.size[0];c.height=meta.size[1];const cx=c.getContext('2d');cx.drawImage(image,0,0);masks[key]=cx.getImageData(0,0,c.width,c.height);}resolve();};image.onerror=reject;image.src='/art/'+meta.file;})));
 await refresh();resize();ready=true;lastPulse=performance.now();requestAnimationFrame(draw);$('connection').textContent='Partida local';
 }catch{$('movement').textContent='No se pudo iniciar la escena. Verificá que descomprimiste toda la carpeta y mantené abierta la consola.';$('connection').textContent='Inicio incompleto';}})();
