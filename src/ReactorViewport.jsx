import React, {useEffect,useRef,useState} from 'react';
const palette=[[68,1,84],[59,82,139],[33,145,140],[94,201,98],[253,231,37]];
function speedColor(v){const t=Math.max(0,Math.min(1,Math.log(Math.max(v,.0001)/.0001)/Math.log(1.5/.0001)))*4,i=Math.min(3,Math.floor(t)),f=t-i;return `rgb(${palette[i].map((c,j)=>Math.round(c+(palette[i+1][j]-c)*f)).join(',')})`;}
export default function ReactorViewport({geometryUrl,flowUrl,label}){
 const ref=useRef(null),drag=useRef(null);
 const [mesh,setMesh]=useState(null),[flow,setFlow]=useState(null),[error,setError]=useState(''),[mode,setMode]=useState('flow');
 const [angle,setAngle]=useState([.55,.3]),[zoom,setZoom]=useState(1),[focus,setFocus]=useState('full');
 const [layers,setLayers]=useState({flow:true,walls:true,support:true,wafer:true,inlets:true,outlets:true});
 useEffect(()=>{const controller=new AbortController();setMesh(null);setFlow(null);setError('');
 Promise.all([geometryUrl,flowUrl].map(url=>fetch(url,{signal:controller.signal}).then(r=>{if(!r.ok)throw Error('Saved visualisation could not be loaded');return r.json()}))).then(([m,f])=>{setMesh(m);setFlow(f)}).catch(e=>{if(e.name!=='AbortError')setError(e.message)});return()=>controller.abort()},[geometryUrl,flowUrl]);
 useEffect(()=>{
  if(!mesh||mode!=='flow'||!ref.current)return;
  const canvas=ref.current;
  function draw(){
   const w=canvas.clientWidth,h=canvas.clientHeight,dpr=window.devicePixelRatio||1;canvas.width=w*dpr;canvas.height=h*dpr;
   const ctx=canvas.getContext('2d');ctx.scale(dpr,dpr);ctx.clearRect(0,0,w,h);
   const span=focus==='full'?.62:.24,center=focus==='full'?-.265:-.08;
   const scale=Math.min((h-40)/span,(w-30)/.2)*zoom,c=Math.cos(angle[0]),s=Math.sin(angle[0]),cp=Math.cos(angle[1]),sp=Math.sin(angle[1]);
   const project=([x,y,z])=>{const a=x*c-y*s,b=x*s+y*c,v=z-center;return[w/2+a*scale,h/2-(v*cp-b*sp)*scale,b*cp+v*sp]};
   const points=mesh.points.map(project), primitives=[];
   mesh.faces.forEach((f,i)=>{const r=mesh.regions[i],name=mesh.labels[String(r)]||'',layer=name.startsWith('inlet')?'inlets':name.startsWith('outlet')?'outlets':name==='support'?'support':name==='wafer'?'wafer':'walls';if(!layers[layer])return;
    const pts=f.map(j=>points[j]),depth=pts.reduce((n,p)=>n+p[2],0)/pts.length;
    primitives.push({pts,depth,fill:layer==='walls'?'rgba(104,173,191,.055)':layer==='wafer'?'#f4bd50':layer==='support'?'#677b88':layer==='inlets'?'#3ebea5':'#de906c'});
   });
   if(flow&&layers.flow)flow.lines.forEach((line,k)=>{
    // Display every fourth seed, across the inlet seed groups.
    if(k%4)return;
    const pts=line.map(project);
    for(let j=1;j<pts.length;j++)primitives.push({pts:[pts[j-1],pts[j]],depth:(pts[j-1][2]+pts[j][2])/2,color:speedColor((line[j-1][3]+line[j][3])/2)});
    for(const frac of [.2,.45,.7,.9]){const j=Math.floor((pts.length-7)*frac);if(j<0)continue;primitives.push({pts:[pts[j],pts[j+6]],depth:pts[j+6][2],arrow:true})}
   });
   primitives.sort((a,b)=>a.depth-b.depth);
   for(const p of primitives){
    ctx.beginPath();const [a,b]=p.pts;
    if(p.arrow){const dx=b[0]-a[0],dy=b[1]-a[1],len=Math.hypot(dx,dy);if(len<1)continue;const x=b[0],y=b[1],ux=dx/len,uy=dy/len;ctx.moveTo(x-ux*6-uy*3,y-uy*6+ux*3);ctx.lineTo(x,y);ctx.lineTo(x-ux*6+uy*3,y-uy*6-ux*3);ctx.strokeStyle='#d8f2ef';ctx.lineWidth=1.2;ctx.stroke();continue;}
    p.pts.forEach((v,i)=>i?ctx.lineTo(v[0],v[1]):ctx.moveTo(v[0],v[1]));
    if(p.fill){ctx.closePath();ctx.fillStyle=p.fill;ctx.fill()}else{ctx.strokeStyle=p.color;ctx.lineWidth=1.6;ctx.stroke()}
   }
   ctx.fillStyle='#b7cbd7';ctx.font='12px sans-serif';ctx.fillText(focus==='full'?'Full reactor · z points up':'Upper chamber and wafer · lower exhaust section outside view',14,h-16);
  }
  draw();const observer=new ResizeObserver(draw);observer.observe(canvas);return()=>observer.disconnect();
 },[mesh,flow,angle,zoom,layers,mode,focus]);
 return <div>
 <div className="reactor-controls"><button aria-pressed={mode==='flow'} onClick={()=>setMode('flow')}>3D nitrogen flow</button>{<button aria-pressed={mode==='movie'} onClick={()=>setMode('movie')}>Recorded tracer playback</button>}</div>
 {error&&<p role="alert">Visualisation unavailable: {error}</p>}
 {mode==='flow'?<>
 <p className="reactor-note">{flow?label+' · saved steady nitrogen velocity':'Loading saved nitrogen flow…'}</p>
 {mesh&&<div className="reactor-stage"><canvas ref={ref} aria-label="3D reactor with calculated nitrogen streamlines; drag to rotate" onPointerDown={e=>{drag.current=[e.clientX,e.clientY];e.currentTarget.setPointerCapture(e.pointerId)}} onPointerMove={e=>{if(drag.current){const dx=e.clientX-drag.current[0],dy=e.clientY-drag.current[1];setAngle(a=>[a[0]+dx*.01,Math.max(-1.4,Math.min(1.4,a[1]+dy*.01))]);drag.current=[e.clientX,e.clientY]}}} onPointerUp={()=>drag.current=null} onPointerCancel={()=>drag.current=null}/></div>}
 {flow&&<div className="reactor-speed-key"><span>Speed (m/s, logarithmic)</span><div className="reactor-speed-gradient"/><div className="reactor-speed-ticks"><span>0.0001</span><span>0.001</span><span>0.01</span><span>0.1</span><span>1.5</span></div></div>}
 <div className="reactor-controls"><button aria-pressed={focus==='full'} onClick={()=>{setFocus('full');setZoom(1)}}>Full reactor</button><button aria-pressed={focus==='upper'} onClick={()=>{setFocus('upper');setZoom(1)}}>Wafer close-up</button>{Object.keys(layers).filter(k=>!!flow||k!=='flow').map(k=><label key={k}><input type="checkbox" checked={layers[k]} onChange={e=>setLayers({...layers,[k]:e.target.checked})}/>{k}</label>)}</div>
 <div className="reactor-controls reactor-view-tools"><button onClick={()=>setAngle(a=>[a[0]-.3,a[1]])} aria-label="Rotate left">↶</button><button onClick={()=>setAngle(a=>[a[0]+.3,a[1]])} aria-label="Rotate right">↷</button><label>Zoom<input aria-label="Geometry zoom" type="range" min=".6" max="2" step=".1" value={zoom} onChange={e=>setZoom(+e.target.value)}/></label><button onClick={()=>{setAngle([.55,.3]);setZoom(1);setFocus('full')}}>Reset view</button></div>
 <p className="reactor-note">Gold: wafer · green: {mesh?Object.values(mesh.labels).filter(n=>n.startsWith('inlet')).length:'…'} inlets · orange: two outlets. {flow&&<>Coloured paths follow calculated velocity; white arrows show direction. Showing {Math.ceil(flow.lines.length/4)} selected inlet paths, not every recirculating region. Steady flow stays fixed when tracer time advances; diffusion is not shown by these paths.</>}</p>
 <details><summary>Flow source and method</summary><p>{flow?.method}</p><p>{flow?.limitations}</p><p>Original source: {mesh?.source}</p></details>
 </>:<><video className="reactor-video" controls preload="metadata" src="/media/tracer.mp4"/><p className="reactor-note">Saved original-mesh tracer simulation, 0–120 physical seconds. Fixed concentration scale 0–1. Separate from the selected evidence case.</p></>}
 </div>
}
