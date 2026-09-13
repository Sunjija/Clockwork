'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {Player,Input}=require('../Scene/play-controller.js');
const root=path.resolve(__dirname,'..');
const meta=JSON.parse(fs.readFileSync(path.join(root,'Revisions/10/data.json')));
const reports=[];
function check(name,run){run();reports.push({name,passed:true});}
function step(p,ms,axis=0){for(let t=0;t<ms;t+=10)p.update(Math.min(10,ms-t),axis);}
function ledge(){return new Player(meta,{spawnX:126,spawnY:100},[{x:0,y:100,w:120},{x:0,y:300,w:640}]);}
function walkOff(p){for(let i=0;i<20&&p.grounded;i++)p.update(10,1);assert.equal(p.grounded,false);}
check('left/right travel, world bounds and static original idle',()=>{
 const p=new Player(meta);step(p,1000,1);assert.ok(Math.abs(p.x-148)<.01);step(p,1000,-1);assert.ok(Math.abs(p.x-106)<.01);
 step(p,5000,-1);assert.equal(p.x,16);step(p,100);assert.deepEqual(p.pose(),{clip:'Idle',frame:0});
});
check('walk-off + 80 ms: coyote first jump retains double jump, third jump denied',()=>{
 const p=ledge();walkOff(p);step(p,80);assert.equal(p.jump(),true);assert.equal(p.lastAction,'coyote-jump');assert.equal(p.jumps,1);
 step(p,100);assert.equal(p.jump(),true);assert.equal(p.jumps,2);assert.equal(p.jump(),false);
});
check('walk-off + 140 ms: grace expires and only airborne jump remains',()=>{
 const p=ledge();walkOff(p);step(p,140);assert.ok(p.clock>p.coyoteUntil);p.jump();assert.equal(p.lastAction,'double-jump');assert.equal(p.jumps,2);assert.equal(p.jump(),false);
});
check('jump buffer within 100 ms is consumed once on landing',()=>{
 const p=new Player(meta,{spawnX:50,spawnY:96},[{x:0,y:100,w:640}]);p.vy=100;p.jumps=2;
 assert.equal(p.jump(),false);step(p,50);assert.equal(p.jumps,1);assert.ok(p.vy<0);assert.equal(p.grounded,false);
 assert.equal(p.events.filter(e=>e.name==='jump').length,1);
});
check('expired jump buffer does not cause an unrequested bounce',()=>{
 const p=new Player(meta,{spawnX:50,spawnY:0},[{x:0,y:100,w:640}]);p.jumps=2;p.jump();step(p,700);
 assert.equal(p.grounded,true);assert.equal(p.jumps,0);assert.equal(p.events.some(e=>e.name==='jump'),false);
});
check('dash off ledge falls instead of snapping back; air dash cannot repeat',()=>{
 const p=ledge();p.dash();step(p,200);assert.equal(p.grounded,false);assert.ok(p.y>100);assert.equal(p.dash(),false);
 step(p,800);assert.equal(p.grounded,true);assert.equal(p.y,300);assert.equal(p.dash(),true);
});
check('fast fall lands on a thin platform without collision tunneling',()=>{
 const p=new Player(meta,{spawnX:240,spawnY:80},[{x:196,y:228,w:88,h:12}]);p.vy=900;
 step(p,200);assert.equal(p.grounded,true);assert.equal(p.y,228);
 p.jump();step(p,600);assert.equal(p.grounded,true);assert.equal(p.y,228);
});
check('air attack preserves gravity; ground attack keeps feet planted',()=>{
 const p=new Player(meta);p.attack();const x=p.x;step(p,300,1);assert.equal(p.x,x);assert.equal(p.pose().clip,'Attack');
 step(p,300);p.jump();p.attack();step(p,150);assert.equal(p.pose().clip,'Attack');assert.ok(p.y<252);step(p,700);assert.equal(p.grounded,true);
});
check('key assignments, repeat suppression, opposite arrows and focus cleanup',()=>{
 const p=new Player(meta),i=new Input(p);i.down('ArrowRight');assert.equal(i.axis,1);i.down('ArrowLeft');assert.equal(i.axis,0);i.up('ArrowRight');assert.equal(i.axis,-1);
 i.down('Space');i.down('Space',true);assert.equal(p.jumps,1);i.up('Space');i.down('Space');assert.equal(p.jumps,2);
 i.clear();assert.equal(i.axis,0);i.down('KeyR');assert.equal(p.grounded,true);assert.equal(p.jumps,0);
 i.down('KeyJ');assert.equal(p.pose().clip,'Attack');i.down('ShiftLeft');assert.equal(p.pose().clip,'Dash');
});
check('30/60/144 Hz renders give the same trajectory and position',()=>{
 const results=[30,60,144].map(fps=>{const p=new Player(meta);p.jump();for(let n=0;n<fps;n++)p.update(1000/fps,1);return [p.x,p.y,p.vy,p.grounded];});
 for(const r of results.slice(1))for(let n=0;n<3;n++)assert.ok(Math.abs(r[n]-results[0][n])<1e-7);
});
check('every animation pose stays within its authored frame range',()=>{
 const p=new Player(meta);for(let n=0;n<1500;n++){if(n%90===0)p.jump();if(n%133===0)p.dash();if(n%177===0)p.attack();p.update(10,n%200<100?1:-1);const s=p.pose();assert.ok(s.frame>=0&&s.frame<meta.clips[s.clip].frames.length);}
});
const report={tests:reports.length,passed:reports.length,settings:new Player(meta).config,checks:reports};
fs.writeFileSync(path.join(root,'QA/play-controller.json'),JSON.stringify(report,null,2));
console.log(JSON.stringify(report,null,2));
