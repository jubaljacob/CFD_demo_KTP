import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {verdict} from '../src/metrics.js';
const read=p=>JSON.parse(readFileSync(new URL('../public/'+p,import.meta.url)));
const study=read('data/study.json');
test('included evidence retains its exported fingerprints',()=>{
 for(const file of read('data/download-checksums.json')){
  const data=readFileSync(new URL('../public/'+file.path,import.meta.url));
  assert.equal(createHash('sha256').update(data).digest('hex'),file.sha256,file.path);
 }
});
test('arrival metrics and minimum curves reproduce the raw nine-probe histories',()=>{
 for(const run of study.runs.slice(0,2)){
  const rows=readFileSync(new URL('../public/evidence/'+run.id+'/probes.txt',import.meta.url),'utf8').split('\n').filter(l=>l.trim()&&!l.startsWith('#')).map(l=>l.trim().split(/\s+/).map(Number));
  const zero=[0,...Array(9).fill(0)];const full=[zero,...rows];
  assert.equal(run.curve.length,full.length);
  full.forEach((r,i)=>{assert.equal(run.curve[i].time_s,r[0]);assert.ok(Math.abs(run.curve[i].minimum_label-Math.min(...r.slice(1)))<1e-12)});
  const i=full.findIndex(r=>r.slice(1).every(v=>v>=.9));const a=full[i-1],b=full[i];
  const arrival=a[0]+Math.max(...a.slice(1).map((v,j)=>v>=.9?0:(.9-v)/(b[j+1]-v)))*(b[0]-a[0]);
  assert.ok(Math.abs(arrival-run.measurement.arrival_time_s)<1e-8);
  assert.ok(full.slice(i).every(r=>r.slice(1).every(v=>v>=.9)));
 }
});
test('target assessment rejects invalid evidence and handles both target outcomes',()=>{
 assert.match(verdict(study.runs[0],35),/^Target met/);
 assert.match(verdict(study.runs[0],30),/^Target not met/);
 assert.match(verdict(study.runs[1],30),/^Target met/);
 assert.match(verdict(study.runs.find(r=>r.id==='tracer-fine'),35),/^Insufficient evidence/);
 assert.match(verdict(study.runs[0],NaN),/^Enter/);
 assert.match(verdict(study.runs[0],-1),/^Enter/);
});
test('geometry and velocity exports represent four and five inlet configurations',()=>{
 for(const [key,count] of [['four',4],['five',5]]){
  const geometry=read('data/geometry-'+key+'.json'),flow=read('data/flow-'+key+'.json');
  assert.equal(Object.values(geometry.labels).filter(n=>n.startsWith('inlet')).length,count);
  assert.equal(geometry.faces.length,geometry.regions.length);
  assert.ok(geometry.faces.every(f=>f.every(i=>i>=0&&i<geometry.points.length)));
  assert.equal(flow.lines.length,count*20);
  assert.ok(flow.lines.every(l=>l.every(p=>p.length===4&&p.every(Number.isFinite)&&p[3]>=0)));
 }
});
