/* World controller: authored animation assets remain independent of physics. */
(function (scope) {
  'use strict';
  const STEP = 1000 / 120;
  const DEFAULTS = Object.freeze({width:640, height:360, spawnX:106, spawnY:252,
    walkSpeed:42, jumpSpeed:220, doubleJumpSpeed:205, gravity:800,
    dashSpeed:260, dashActiveMs:160, dashCooldownMs:300,
    coyoteMs:120, jumpBufferMs:100, footHalfWidth:7});
  const PLATFORMS = Object.freeze([
    {x:0, y:252, w:640, h:108, floor:true},
    {x:196, y:228, w:88, h:12},
    {x:330, y:202, w:80, h:12},
    {x:462, y:228, w:88, h:12}
  ]);
  const total = values => values.reduce((a,b)=>a+b,0);
  function frameAt(ms, durations, offset=0) {
    for(let i=offset;i<durations.length;i++) {if(ms<durations[i]) return i; ms-=durations[i];}
    return durations.length-1;
  }
  class Player {
    constructor(meta, options={}, platforms=PLATFORMS) {
      this.meta=meta; this.config={...DEFAULTS,...options};
      this.platforms=platforms.map(p=>({...p})); this.reset();
    }
    reset() {
      Object.assign(this,{x:this.config.spawnX,y:this.config.spawnY,vy:0,facing:1,
        grounded:false,jumps:0,clock:0,accumulator:0,axis:0,walkAge:0,
        airAge:1000,landAge:1000,airClip:'Jump',attackAge:Infinity,
        dashAge:Infinity,dashReady:true,dashUntil:0,coyoteUntil:-Infinity,
        jumpUntil:-Infinity,lastAction:'idle',events:[]});
      this.grounded=this.platforms.some(p=>this.overlaps(p)&&Math.abs(this.y-p.y)<0.001);
    }
    overlaps(p) {return this.x+this.config.footHalfWidth>p.x && this.x-this.config.footHalfWidth<p.x+p.w;}
    event(name) {
      this.lastAction=name; this.events.push({name,ms:this.clock,x:this.x,y:this.y});
      if(this.events.length>32)this.events.shift();
    }
    get dashing() {return this.dashAge<this.config.dashActiveMs;}
    get attacking() {return this.attackAge<total(this.meta.clips.Attack.durations);}
    jump() {this.jumpUntil=this.clock+this.config.jumpBufferMs;return this.consumeJump();}
    consumeJump() {
      if(this.jumpUntil<this.clock || this.dashing)return false;
      const first=this.grounded || (this.jumps===0 && this.clock<=this.coyoteUntil);
      if(!first && this.jumps>=2)return false;
      const coyote=first&&!this.grounded;
      // A jump after grace expires spends the only airborne jump, including walk-offs.
      this.jumps=first?1:2;
      this.vy=-(first?this.config.jumpSpeed:this.config.doubleJumpSpeed);
      this.grounded=false;this.coyoteUntil=-Infinity;this.jumpUntil=-Infinity;
      this.airClip=first?'Jump':'DoubleJump';this.airAge=0;this.attackAge=Infinity;
      this.event(coyote?'coyote-jump':first?'jump':'double-jump');return true;
    }
    attack() {
      if(this.dashing||this.attacking)return false;
      this.attackAge=0;this.event('attack');return true;
    }
    dash() {
      if(!this.dashReady || this.dashing || this.clock<this.dashUntil)return false;
      this.dashReady=false;this.dashAge=0;this.vy=0;this.attackAge=Infinity;
      this.dashUntil=this.clock+this.config.dashCooldownMs;this.event('dash');return true;
    }
    update(ms, axis=0) {
      // Fixed simulation tick; rendering rate cannot change ledge grace or jump height.
      this.accumulator+=Math.max(0,Math.min(ms,250));
      while(this.accumulator+1e-7>=STEP) {this.step(STEP,Math.sign(axis));this.accumulator-=STEP;}
    }
    step(ms,axis) {
      const dt=ms/1000, c=this.config, wasGrounded=this.grounded;
      this.clock+=ms;this.airAge+=ms;this.landAge+=ms;this.axis=axis;
      this.consumeJump();
      const dash=this.dashing, attack=this.attacking;
      if(axis&&!dash&&!attack)this.facing=axis;
      const speed=dash?this.facing*c.dashSpeed:attack&&this.grounded?0:axis*c.walkSpeed;
      const oldX=this.x, oldY=this.y;
      this.x=Math.max(16,Math.min(c.width-16,this.x+speed*dt));
      if(!dash || this.grounded) {
        this.y+=this.vy*dt+c.gravity*dt*dt/2;this.vy+=c.gravity*dt;
      }
      this.grounded=false;
      if(this.vy>=0) {
        // Swept feet against one-way tops; fast falls cannot tunnel through a ledge.
        const landing=this.platforms.filter(p=>this.overlaps(p)&&oldY<=p.y+0.001&&this.y>=p.y)
          .sort((a,b)=>a.y-b.y)[0];
        if(landing) {
          this.y=landing.y;this.vy=0;this.grounded=true;this.jumps=0;
          this.coyoteUntil=-Infinity;
          if(!wasGrounded) {this.landAge=0;this.event('land');}
        }
      }
      if(wasGrounded&&!this.grounded&&this.vy>=0&&this.jumps===0) {
        this.coyoteUntil=this.clock+c.coyoteMs;this.airAge=1000;this.airClip='Jump';this.event('walk-off');
      }
      if(this.grounded&&!dash&&!attack&&this.x!==oldX) {
        // Advance by distance, keeping the accepted 25 px/s walk's stride relationship.
        this.walkAge+=Math.abs(this.x-oldX)/this.meta.physics.walkSpeed*1000;
      } else if(this.grounded&&!axis&&!dash&&!attack)this.walkAge=0;
      this.attackAge+=ms;this.dashAge+=ms;
      if(this.grounded&&!this.dashing&&this.clock>=this.dashUntil)this.dashReady=true;
      this.consumeJump();
      if(this.y>c.height+96) {this.reset();this.event('respawn');}
    }
    pose() {
      const clips=this.meta.clips;
      if(this.dashing)return {clip:'Dash',frame:Math.min(6,frameAt(this.dashAge,clips.Dash.durations,3))};
      if(this.attacking)return {clip:'Attack',frame:frameAt(this.attackAge,clips.Attack.durations)};
      if(!this.grounded) {
        if(this.airClip==='DoubleJump')return {clip:'DoubleJump',frame:this.airAge<45?2:this.airAge<90?3:this.vy<-35?4:this.vy<0?5:this.vy<35?6:this.vy<140?7:8};
        return {clip:'Jump',frame:this.airAge<40?3:this.vy<-40?(this.airAge<145?4:5):this.vy<0?6:this.vy<40?7:this.vy<140?8:9};
      }
      if(this.axis)return {clip:'Walk',frame:frameAt(this.walkAge%total(clips.Walk.durations),clips.Walk.durations)};
      if(this.landAge<120)return {clip:this.airClip,frame:frameAt(this.landAge,clips[this.airClip].durations,this.airClip==='Jump'?10:9)};
      return {clip:'Idle',frame:0};
    }
    snapshot() {return {...this.pose(),x:this.x,y:this.y,grounded:this.grounded,jumps:this.jumps,
      facing:this.facing,dashReady:this.dashReady,lastAction:this.lastAction,coyoteRemaining:Math.max(0,this.coyoteUntil-this.clock)};}
  }
  class Input {
    constructor(player){this.player=player;this.held=new Set();}
    get axis(){return Number(this.held.has('ArrowRight'))-Number(this.held.has('ArrowLeft'));}
    down(code,repeat=false) {
      if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','Space','ShiftLeft','ShiftRight','KeyJ','KeyR'].includes(code))return false;
      if(repeat||this.held.has(code))return true;
      this.held.add(code);
      if(code==='Space'||code==='ArrowUp')this.player.jump();
      if(code==='ShiftLeft'||code==='ShiftRight')this.player.dash();
      if(code==='KeyJ')this.player.attack();
      if(code==='KeyR'){this.player.reset();this.clear();}
      return true;
    }
    up(code){this.held.delete(code);}
    clear(){this.held.clear();}
  }
  const api={Player,Input,DEFAULTS,PLATFORMS,STEP};
  if(typeof module!=='undefined'&&module.exports)module.exports=api;else scope.TiquePlay=api;
})(typeof globalThis!=='undefined'?globalThis:this);
