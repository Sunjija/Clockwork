using System;
using System.Collections.Generic;

namespace TiqueReturn
{
    [Serializable] public sealed class PuzzleBook { public PuzzleRoom[] levels; }
    [Serializable] public sealed class PuzzleRoom
    {
        public string[] rows;
        public int start;
        public int[] boxes, types, goals;
        public string solution;
        public int pushes, moves, states;
    }
    public sealed class CorePuzzle
    {
        public readonly PuzzleRoom room;
        public int player, previousPlayer, moves, pushes;
        public int[] boxes, previousBoxes;
        public int lastDirection=1;
        public float motion;
        public string feedback="";
        readonly Stack<Snapshot> history=new Stack<Snapshot>();
        struct Snapshot { public int player,moves,pushes; public int[] boxes; }
        public CorePuzzle(PuzzleRoom room) { this.room=room; Reset(); }
        public bool Wall(int p) => p<0 || p>=49 || room.rows[p/7][p%7]=='#';
        public static int Next(int p,int direction)
        {
            int x=p%7,y=p/7;
            if(direction==0)x--;if(direction==1)x++;if(direction==2)y--;if(direction==3)y++;
            return x<0||x>=7||y<0||y>=7?-1:y*7+x;
        }
        public bool GoalFilled(int g)
        {
            for(int b=0;b<boxes.Length;b++)if(boxes[b]==room.goals[g]&&room.types[b]==room.types[g])return true;
            return false;
        }
        public bool Solved { get {for(int i=0;i<room.goals.Length;i++)if(!GoalFilled(i))return false;return true;} }
        public int UndoCount => history.Count;
        public void Reset()
        {
            player=previousPlayer=room.start;boxes=(int[])room.boxes.Clone();previousBoxes=(int[])boxes.Clone();
            moves=pushes=0;motion=0;history.Clear();feedback="";
        }
        public bool Undo()
        {
            if(history.Count==0)return false;
            Snapshot s=history.Pop();player=previousPlayer=s.player;boxes=s.boxes;previousBoxes=(int[])boxes.Clone();
            moves=s.moves;pushes=s.pushes;motion=0;feedback="한 수 되돌렸어요.";return true;
        }
        public bool Move(int direction)
        {
            if(direction<0||direction>3||Solved)return false;
            lastDirection=direction;
            int target=Next(player,direction),box=Array.IndexOf(boxes,target);
            if(Wall(target)){feedback="";return false;}
            int end=target;
            if(box>=0)
            {
                int next=Next(target,direction);
                if(Wall(next)||Array.IndexOf(boxes,next)>=0){feedback="막혔어요. Z로 되돌릴 수 있어요.";return false;}
                end=next;
                if(room.types[box]==1)
                {
                    while(true){next=Next(end,direction);if(Wall(next)||Array.IndexOf(boxes,next)>=0)break;end=next;}
                }
            }
            history.Push(new Snapshot{player=player,boxes=(int[])boxes.Clone(),moves=moves,pushes=pushes});
            previousPlayer=player;previousBoxes=(int[])boxes.Clone();player=target;moves++;
            motion=box>=0&&room.types[box]==1?.27f:.15f;
            if(box>=0){boxes[box]=end;pushes++;feedback=room.types[box]==1?"구슬은 소켓을 지나쳐도, 막힐 때까지 움직여요.":"추를 한 칸 밀었어요.";}
            else feedback="";
            if(Solved)feedback="회로 연결 완료.";
            return true;
        }
    }
}
