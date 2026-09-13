/* Render existing art only. Keyboard and touch feed the same world controller. */
(async function(){
  'use strict';
  const canvas=document.querySelector('#game'), ctx=canvas.getContext('2d');
  const notice=document.querySelector('#notice'),message=document.querySelector('#message');
  const resume=document.querySelector('#resume'),retry=document.querySelector('#retry');
  const reset=document.querySelector('#reset');
  retry.addEventListener('click',()=>location.reload());
  const image=src=>new Promise((resolve,reject)=>{const i=new Image();i.onload=()=>resolve(i);i.onerror=()=>reject(new Error(src));i.src=src;});
  try {
    const response=await fetch('Revisions/10/data.json');if(!response.ok)throw new Error('animation metadata');
    const meta=await response.json(), sprites={};
    const [background,brick]=await Promise.all([image('Scene/limbus.png'),image('Scene/platform-fill.png'),
      ...Object.entries(meta.clips).map(async([name,clip])=>{sprites[name]=await Promise.all(clip.frames.map(image));})]);
    const player=new TiquePlay.Player(meta), input=new TiquePlay.Input(player);
    let paused=false,lastTime=0;
    document.querySelectorAll('button').forEach(b=>b.disabled=false);
    notice.hidden=true;canvas.dataset.ready='true';canvas.focus({preventScroll:true});
    function clear(){input.clear();document.querySelectorAll('[data-key]').forEach(b=>b.dataset.held='false');}
    function pause(value){paused=value;clear();lastTime=0;notice.hidden=!value;resume.hidden=!value;message.textContent='잠시 멈췄어요.';canvas.dataset.paused=String(value);}
    function continuePlay(){pause(false);canvas.focus({preventScroll:true});}
    resume.addEventListener('click',continuePlay);
    reset.addEventListener('click',()=>{player.reset();continuePlay();});
    canvas.addEventListener('pointerdown',()=>{if(paused)continuePlay();else canvas.focus({preventScroll:true});});
    window.addEventListener('keydown',e=>{
      if(e.ctrlKey||e.metaKey||e.altKey)return;
      if(e.code==='Escape'){e.preventDefault();if(!e.repeat)pause(!paused);return;}
      if(e.target.closest('button')&&(e.code==='Space'||e.code==='Enter'))return;
      if(paused)return;
      if(input.down(e.code,e.repeat))e.preventDefault();
    });
    window.addEventListener('keyup',e=>input.up(e.code));
    window.addEventListener('blur',()=>pause(true));
    document.addEventListener('visibilitychange',()=>{if(document.hidden)pause(true);});
    document.querySelectorAll('[data-key]').forEach(button=>{
      button.addEventListener('pointerdown',e=>{e.preventDefault();if(paused)continuePlay();button.setPointerCapture(e.pointerId);input.down(button.dataset.key);button.dataset.held='true';});
      const release=()=>{input.up(button.dataset.key);button.dataset.held='false';};
      button.addEventListener('pointerup',release);button.addEventListener('pointercancel',release);button.addEventListener('lostpointercapture',release);
      // Keyboard/assistive activation has no pointerdown event.
      button.addEventListener('click',e=>{if(e.detail===0){if(paused)continuePlay();input.down(button.dataset.key);input.up(button.dataset.key);}});
    });
    function render(){
      ctx.imageSmoothingEnabled=false;ctx.clearRect(0,0,640,360);ctx.drawImage(background,0,0,640,360);
      for(const p of player.platforms){
        if(p.floor)continue;
        ctx.save();ctx.beginPath();ctx.rect(p.x,p.y,p.w,p.h);ctx.clip();
        for(let x=p.x;x<p.x+p.w;x+=brick.width)ctx.drawImage(brick,x,p.y);
        ctx.restore();
        // A continuous cap makes the collision surface legible against the scrap pile.
        ctx.fillStyle='#a99570';ctx.fillRect(p.x,p.y,p.w,2);
        ctx.fillStyle='#242a2c';ctx.fillRect(p.x,p.y+p.h-2,p.w,2);
      }
      const s=player.snapshot(),x=Math.round(s.x),y=Math.round(s.y);
      if(s.grounded){ctx.fillStyle='#080d1090';ctx.beginPath();ctx.ellipse(x,y,10,2,0,0,Math.PI*2);ctx.fill();}
      ctx.save();ctx.translate(x,y);ctx.scale(s.facing,1);ctx.drawImage(sprites[s.clip][s.frame],-32,-56);ctx.restore();
      // DOM evidence mirrors what is drawn, without adding a debug panel to the scene.
      canvas.dataset.x=s.x.toFixed(2);canvas.dataset.y=s.y.toFixed(2);canvas.dataset.clip=s.clip;
      canvas.dataset.frame=String(s.frame);canvas.dataset.grounded=String(s.grounded);
      canvas.dataset.lastAction=s.lastAction;canvas.dataset.jumps=String(s.jumps);
    }
    function tick(time){
      if(lastTime&&!paused)player.update(Math.min(100,time-lastTime),input.axis);
      lastTime=time;render();requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  } catch(error){
    console.error('Play scene failed to load',error);canvas.dataset.ready='false';
    message.textContent='플레이 장면을 불러오지 못했어요. 로컬 서버를 확인하고 다시 불러와 주세요.';
    retry.hidden=false;
  }
})();
