using System;
using System.Collections.Generic;

namespace TiqueReturn
{
    // Read-only support layer. Call after Tick, passing the physical held direction,
    // not just the auto-repeat command: a held blocked arrow is one attempt.
    public sealed class AdaptiveGuidance
    {
        public const float TipDuration=4.8f, Cooldown=24f, StagnationThreshold=48f;
        public string Message { get; private set; }="";
        public string Key { get; private set; }="";
        public int Level { get; private set; }
        public float Remaining { get; private set; }
        public bool Visible => !suspended&&Remaining>0&&Message.Length>0;
        public int DisplayCount { get; private set; }
        public float ActiveStagnation => activeStagnation;
        public int ProcessedEvents { get; private set; }

        ReworkModel observed;
        CorePuzzle board;
        Journey phase;
        int room,eventCursor,moves,pushes,bestGoals;
        int blockedAttempts,undoCycles,resets,orbPasses,revisitCycles,armorHits,missedWindows;
        int held=-1,failedPlayer=-1,failedDirection=-1;
        bool failedLatch,suspended,windowActive,windowHit;
        CoreOpeningSource windowSource;
        float previousClock,now,nextAllowed,lastActivity=-100,activeStagnation;
        string pendingKey="",pendingMessage="";
        int pendingLevel,pendingPriority;
        readonly Dictionary<string,int> levels=new Dictionary<string,int>();
        readonly Dictionary<string,int> hazardHits=new Dictionary<string,int>();
        readonly Dictionary<string,int> visits=new Dictionary<string,int>();

        public void Observe(ReworkModel model,ReworkCommand command,int heldGridDirection=-1)
        {
            if(model==null)return;
            if(!ReferenceEquals(observed,model))
            {
                Reset();observed=model;phase=model.phase;room=model.roomIndex;board=model.puzzle;
                now=previousClock=model.clock;eventCursor=model.events.Count;
                Snapshot(model);ResetRoomEvidence(model);return;
            }
            suspended=model.paused;
            if(suspended)return;
            float dt=Math.Max(0,Math.Min(.25f,model.clock-previousClock));
            previousClock=model.clock;now=model.clock;Remaining=Math.Max(0,Remaining-dt);
            if(Remaining<=0){Message="";Key="";Level=0;}

            bool changedRoom=room!=model.roomIndex||!ReferenceEquals(board,model.puzzle);
            if(changedRoom)
            {
                room=model.roomIndex;board=model.puzzle;Dismiss();ResetRoomEvidence(model);
                Snapshot(model);
            }
            if(phase!=model.phase)
            {
                // Death/arrival clear the old toast, while hazard knowledge survives a retry.
                Dismiss();windowActive=false;failedLatch=false;lastActivity=-100;
                activeStagnation=0;
                if(model.phase==Journey.Puzzle)ResetRoomEvidence(model);
                if(model.phase==Journey.Combat)nextAllowed=Math.Max(nextAllowed,now+3f);
            }
            if(heldGridDirection!=held||heldGridDirection<0)failedLatch=false;
            held=heldGridDirection;

            bool activity=false;
            if(model.phase==Journey.Puzzle&&!changedRoom)
                activity=ObservePuzzle(model,command);
            ObserveEvents(model,ref activity);
            if(model.phase==Journey.Combat)ObserveWindow(model);

            if(activity)lastActivity=now;
            if(model.phase==Journey.Puzzle)
            {
                // Only time near genuine actions counts. Reading, AFK and held blocked
                // auto-repeat do not silently advance the failure clock.
                if(now-lastActivity<=1.2f)activeStagnation+=dt;
                if(activeStagnation>=StagnationThreshold)
                    Request("puzzle-stagnation",RoomTip(model.roomIndex,NextLevel("puzzle-stagnation")),1);
            }
            if(model.phase==Journey.Combat)RequestRetainedCombatEvidence();
            if(model.phase==Journey.Puzzle||model.phase==Journey.Combat)TryShow(model);
            else ClearPending();
            phase=model.phase;Snapshot(model);
        }

        bool ObservePuzzle(ReworkModel model,ReworkCommand command)
        {
            CorePuzzle p=model.puzzle;bool activity=false;
            bool reset=NewEvent(model,"room-reset");
            if(reset)
            {
                bool meaningful=moves>0||pushes>0;
                Dismiss();failedLatch=false;activeStagnation=0;visits.Clear();bestGoals=Filled(p);
                if(meaningful){resets++;activity=true;}
                if(resets>=2)Request("puzzle-reset",RoomTip(model.roomIndex,NextLevel("puzzle-reset")),3);
            }
            else if(command.undo&&p.moves<moves)
            {
                undoCycles++;activity=true;failedLatch=false;
                if(undoCycles>=3)Request("puzzle-undo",RoomTip(model.roomIndex,NextLevel("puzzle-undo")),2);
            }
            else if(p.moves>moves)
            {
                activity=true;failedLatch=false;
                if(p.pushes>pushes)
                {
                    string key=BoardKey(p);
                    int count=visits.TryGetValue(key,out int old)?old+1:1;visits[key]=count;
                    // Only a real push returning the parts to an earlier layout counts.
                    // Ordinary positioning walks never increment the revisit evidence.
                    if(count>1){revisitCycles++;if(revisitCycles>=3)
                        Request("puzzle-revisit",RoomTip(model.roomIndex,NextLevel("puzzle-revisit")),1);}
                    blockedAttempts=0;
                    if(Key=="puzzle-blocked")Dismiss();
                    else if(pendingKey=="puzzle-blocked")ClearPending();
                    if(OrbPassedSocket(p))
                    {
                        orbPasses++;
                        if(orbPasses>=2)Request("puzzle-orb",OrbTip(NextLevel("puzzle-orb")),4);
                    }
                }
                int goals=Filled(p);
                if(goals>bestGoals)
                {
                    bestGoals=goals;blockedAttempts=undoCycles=orbPasses=revisitCycles=0;
                    activeStagnation=0;Dismiss();
                }
            }
            else if(command.grid>=0&&p.blockedAge==0)
            {
                int target=CorePuzzle.Next(p.player,command.grid);
                // Ordinary wall bumps and input ignored during movement are not failures.
                bool blockedPush=!p.Wall(target)&&Array.IndexOf(p.boxes,target)>=0;
                if(blockedPush&&(!failedLatch||failedPlayer!=p.player||failedDirection!=command.grid))
                {
                    failedLatch=true;failedPlayer=p.player;failedDirection=command.grid;
                    blockedAttempts++;activity=true;
                    if(blockedAttempts>=3)
                        Request("puzzle-blocked",NextLevel("puzzle-blocked")==1?
                            "막힌 부품은 Z로 되돌려, 밀 방향을 바꿔 보세요.":
                            RoomTip(model.roomIndex,NextLevel("puzzle-blocked")),3);
                }
            }
            return activity;
        }

        bool NewEvent(ReworkModel model,string name)
        {
            for(int i=eventCursor;i<model.events.Count;i++)
                if(EventName(model.events[i])==name)return true;
            return false;
        }
        void ObserveEvents(ReworkModel model,ref bool activity)
        {
            if(eventCursor>model.events.Count)eventCursor=0;
            for(;eventCursor<model.events.Count;eventCursor++)
            {
                string e=EventName(model.events[eventCursor]);ProcessedEvents++;
                if(e=="attack"||e=="dash"||e=="jump"||e=="double-jump"||e.StartsWith("pylon-charge-",StringComparison.Ordinal))activity=true;
                if(e=="armor-contact")
                {
                    armorHits++;
                    if(armorHits>=3)Request("combat-armor",CombatTip("armor",NextLevel("combat-armor"),CoreOpeningSource.None),3);
                }
                if(e=="hurt-wave"||e=="hurt-charge"||e=="hurt-slam")
                {
                    string cause=e.Substring(5);hazardHits[cause]=HazardCount(cause)+1;
                    if(HazardCount(cause)>=2)RequestHazard(cause);
                }
                if(e=="boss-hit")
                {
                    windowHit=true;armorHits=missedWindows=0;hazardHits.Clear();Dismiss();
                }
            }
        }
        void ObserveWindow(ReworkModel model)
        {
            if(model.bossMove==IronMove.Open)
            {
                if(!windowActive){windowActive=true;windowHit=model.openHits>0;windowSource=model.openingSource;}
                if(model.openHits>0)windowHit=true;
            }
            else if(windowActive)
            {
                if(!windowHit)
                {
                    missedWindows++;
                    if(missedWindows>=2)Request("combat-core",CombatTip("core",NextLevel("combat-core"),windowSource),4);
                }
                windowActive=false;
            }
        }
        void RequestRetainedCombatEvidence()
        {
            if(hazardHits.Count==0)return;
            foreach(string cause in new[]{"wave","charge","slam"})
                if(HazardCount(cause)>=2)RequestHazard(cause);
        }
        int HazardCount(string cause)=>hazardHits.TryGetValue(cause,out int n)?n:0;
        void RequestHazard(string cause)
        {
            Request("combat-"+cause,CombatTip(cause,NextLevel("combat-"+cause),CoreOpeningSource.None),2);
        }
        void Request(string key,string message,int priority)
        {
            if(pendingKey.Length>0&&pendingPriority>priority)return;
            pendingKey=key;pendingMessage=message;pendingPriority=priority;pendingLevel=NextLevel(key);
        }
        void TryShow(ReworkModel model)
        {
            if(pendingKey.Length==0||Remaining>0||now<nextAllowed)return;
            // The pending request keeps its original evidence while attacks run.
            // Re-observation never restarts this delay or the actual-display cooldown.
            if(model.phase==Journey.Combat&&
                (model.bossMove!=IronMove.Rest&&model.bossMove!=IronMove.Recover||
                 model.bossMove==IronMove.Recover&&model.bossAge<.2f||
                 !model.hero.grounded||model.hero.Attacking||model.hero.Dashing||now-model.hurtAt<.7f))return;
            Key=pendingKey;Message=pendingMessage;Level=pendingLevel;
            levels[Key]=Level;Remaining=TipDuration;nextAllowed=now+Cooldown;DisplayCount++;
            if(Key=="puzzle-blocked")blockedAttempts=0;
            if(Key=="puzzle-undo")undoCycles=0;
            if(Key=="puzzle-reset")resets=0;
            if(Key=="puzzle-orb")orbPasses=0;
            if(Key=="puzzle-revisit")revisitCycles=0;
            if(Key=="puzzle-stagnation")activeStagnation=0;
            if(Key=="combat-armor")armorHits=0;
            if(Key=="combat-core")missedWindows=0;
            if(Key.StartsWith("combat-",StringComparison.Ordinal))
            {
                string cause=Key.Substring(7);if(hazardHits.ContainsKey(cause))hazardHits[cause]=0;
            }
            ClearPending();
        }
        int NextLevel(string key)=>Math.Min(3,levels.TryGetValue(key,out int n)?n+1:1);
        void Dismiss(){Message="";Key="";Level=0;Remaining=0;ClearPending();}
        void ClearPending(){pendingKey=pendingMessage="";pendingLevel=pendingPriority=0;}
        void Snapshot(ReworkModel model){moves=model.puzzle.moves;pushes=model.puzzle.pushes;}
        void ResetRoomEvidence(ReworkModel model)
        {
            blockedAttempts=undoCycles=resets=orbPasses=revisitCycles=0;activeStagnation=0;
            failedLatch=false;visits.Clear();levels.Clear();bestGoals=Filled(model.puzzle);
            visits[BoardKey(model.puzzle)]=1;
        }
        public void Reset()
        {
            Dismiss();observed=null;board=null;eventCursor=ProcessedEvents=DisplayCount=0;
            levels.Clear();hazardHits.Clear();visits.Clear();nextAllowed=0;
            blockedAttempts=undoCycles=resets=orbPasses=revisitCycles=armorHits=missedWindows=0;
            held=-1;failedLatch=suspended=windowActive=windowHit=false;lastActivity=-100;activeStagnation=0;
        }
        static string EventName(string value){int colon=value.IndexOf(':');return colon<0?value:value.Substring(colon+1);}
        static int Filled(CorePuzzle p){int count=0;for(int g=0;g<p.room.goals.Length;g++)if(p.GoalFilled(g))count++;return count;}
        static string BoardKey(CorePuzzle p)=>string.Join(",",p.boxes);
        static bool OrbPassedSocket(CorePuzzle p)
        {
            int b=p.lastPushedBox;if(b<0||p.room.types[b]!=1)return false;
            int start=p.previousBoxes[b],end=p.boxes[b];
            for(int cell=CorePuzzle.Next(start,p.lastDirection);cell>=0&&cell!=end;cell=CorePuzzle.Next(cell,p.lastDirection))
                for(int g=0;g<p.room.goals.Length;g++)if(p.room.types[g]==1&&p.room.goals[g]==cell)return true;
            return false;
        }
        static string OrbTip(int level)=>level==1?
            "구슬은 소켓에서 멈추지 않아요. 다음 칸을 막아 보세요.":
            "추나 다른 구슬을 소켓 다음 칸에 세워 보세요.";
        static string RoomTip(int index,int level)
        {
            string[][] tips={
                new[]{"추 뒤에 설 공간을 남긴 뒤, 한 칸씩 밀어 보세요.","추를 넣기 전에, 다른 추가 지나갈 길을 남겨 보세요.","막힌 추는 Z로 되돌려, 뒤로 돌아갈 길을 찾아보세요."},
                new[]{"구슬은 소켓 다음 칸에 장애물이 있어야 멈춰요.","추를 먼저 넣지 말고, 구슬을 멈추는 벽으로 써 보세요.","소켓 다음 칸에 추를 세워, 구슬을 멈춰 보세요."},
                new[]{"구슬끼리도 서로를 멈추는 벽이 될 수 있어요.","소켓에 들어간 구슬도 잠시 다시 옮겨 보세요.","추를 마지막에 넣고, 돌아갈 길을 먼저 남겨 보세요."}
            };
            return tips[Math.Min(2,Math.Max(0,index))][Math.Min(2,Math.Max(0,level-1))];
        }
        static string CombatTip(string cause,int level,CoreOpeningSource source)
        {
            string[] tips;
            switch(cause)
            {
                case "wave":tips=new[]{"턱이 내려오기 전에 점프해 충격파를 넘겨 보세요.","충격파가 가까워지기 전에 점프를 준비해 보세요.","이동하며 점프로 충격파를 넘겨 보세요."};break;
                case "charge":tips=new[]{"E로 기둥을 충전하고, 기둥 뒤로 유도해 보세요.","문지기와 기둥 사이가 아닌, 기둥 뒤에 서 보세요.","돌진이 기둥에 닿으면, 열린 노심에 X로 공격해요."};break;
                case "slam":tips=new[]{"낙하 지점이 정해지면 옆으로 빠져나와 보세요.","낙하를 피한 뒤, 열린 노심에 X로 반격해 보세요.","착지 뒤 짧게 노심이 열려요. 가까이 돌아와 보세요."};break;
                case "armor":tips=new[]{"닫힌 장갑은 막혀요. 낙하를 피하면 노심이 열려요.","E로 충전한 기둥에 돌진을 유도해 보세요.","붉은 노심이 열렸을 때, 가까이 붙어 X로 때려요."};break;
                default:tips=source==CoreOpeningSource.SlamCounter?
                    new[]{"낙하 뒤 열린 노심에, X로 한 번 반격해 보세요.","노심 쪽으로 가까이 돌아와, X로 한 번 때려 보세요.","착지 뒤 짧게 열려요. 노심 쪽으로 붙어 보세요."}:
                    new[]{"노심 쪽으로 붙어, 열린 동안 X로 공격해 보세요.","기둥에 부딪혀 노심이 열리면, X를 세 번 눌러요.","붉은 노심이 닫히기 전에 가까이 붙어 보세요."};break;
            }
            return tips[Math.Min(2,Math.Max(0,level-1))];
        }
        // QA/font coverage only; never called by the per-frame observation path.
        public static List<string> MessagesForAudit()
        {
            var messages=new List<string>{"막힌 부품은 Z로 되돌려, 밀 방향을 바꿔 보세요."};
            for(int r=0;r<3;r++)for(int level=1;level<=3;level++)messages.Add(RoomTip(r,level));
            for(int level=1;level<=3;level++)
            {
                messages.Add(OrbTip(level));
                foreach(string cause in new[]{"wave","charge","slam","armor","core"})
                    messages.Add(CombatTip(cause,level,CoreOpeningSource.Pylon));
                messages.Add(CombatTip("core",level,CoreOpeningSource.SlamCounter));
            }
            return messages;
        }
        public static int MeasureAt16(string message)
        {int width=0;foreach(char c in message)width+=c<128?8:16;return width;}
    }
}
