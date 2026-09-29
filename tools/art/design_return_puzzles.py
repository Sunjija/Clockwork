"""Original push/slide puzzle search. Validates layouts, never draws game art."""
from collections import deque
from pathlib import Path
import random, json, heapq

ROOT=Path(__file__).resolve().parents[2]
DIRS=[(-1,0),(1,0),(0,-1),(0,1)]
def solve(rows,start,boxes,types,goals,limit=35000):
 w=len(rows[0]);floor={y*w+x for y,row in enumerate(rows) for x,c in enumerate(row) if c!='#'}
 offsets=[-1,1,-w,w]
 def walk(p,b):
  routes={p:''};q=deque([p]);blocked=set(b)
  while q:
   t=q.popleft()
   for d,off in enumerate(offsets):
    n=t+off
    if n in floor and n not in blocked and n not in routes:routes[n]=routes[t]+str(d);q.append(n)
  return routes
 def done(b):return all(set(b[i] for i,t in enumerate(types) if t==kind)==set(goals[i] for i,t in enumerate(types) if t==kind) for kind in (0,1))
 def key(p,b):
  b=tuple(sorted(b[i] for i,t in enumerate(types) if t==0)+sorted(b[i] for i,t in enumerate(types) if t==1))
  return min(walk(p,b)),b
 k=key(start,boxes);queue=[(0,0,start,tuple(boxes),k)];seen={k:(0,0)};parents={k:None}
 while queue and len(seen)<limit:
  pushes,steps,p,b,k=heapq.heappop(queue)
  if seen.get(k)!=(pushes,steps):continue
  if done(b):
   parts=[]
   while parents[k]:k,segment=parents[k];parts.append(segment)
   return {'solution':''.join(reversed(parts)),'pushes':pushes,'moves':steps,'states':len(seen)}
  routes=walk(p,b)
  for i,pos in enumerate(b):
   for d,off in enumerate(offsets):
    behind=pos-off;to=pos+off
    if behind not in routes or to not in floor or to in b:continue
    if types[i]:
     while to+off in floor and to+off not in b:to+=off
    bb=list(b);bb[i]=to;bb=tuple(bb)
    if not types[i] and to not in goals:
     walls=[to+o not in floor for o in offsets]
     if (walls[0] or walls[1]) and (walls[2] or walls[3]):continue
    kk=key(pos,bb);segment=routes[behind]+str(d);cost=(pushes+1,steps+len(segment))
    if cost<seen.get(kk,(9999,99999)):
     seen[kk]=cost;parents[kk]=(k,segment);heapq.heappush(queue,(*cost,pos,bb,kk))
 return None

def main():
 rng=random.Random(34027)
 selected=[]
 targets=[((0,0),6,10),((0,1),8,13),((0,1,1),9,18)]
 for stage,(types,low,high) in enumerate(targets):
  best=None
  for attempt in range(12000):
   w=7;rows=[list('#######')]+[list('#.....#') for _ in range(5)]+[list('#######')]
   for p in rng.sample([y*w+x for y in range(1,6) for x in range(1,6)],rng.randint(2,5)):
    rows[p//w][p%w]='#'
   rows=[''.join(r) for r in rows];floor=[y*w+x for y,r in enumerate(rows) for x,c in enumerate(r) if c!='#']
   if len(floor)<2*len(types)+1:continue
   coords=rng.sample(floor,2*len(types)+1);start=coords[0];boxes=coords[1:len(types)+1];goals=coords[len(types)+1:]
   if any((p-w not in floor or p+w not in floor) and (p-1 not in floor or p+1 not in floor) for p in boxes):continue
   result=solve(rows,start,boxes,types,goals)
   if not result or not low<=result['pushes']<=high or result['moves']<low*2:continue
   best={'rows':rows,'start':start,'boxes':boxes,'types':list(types),'goals':goals,**result}
   print('STAGE',stage+1,'attempt',attempt,json.dumps(best),flush=True);selected.append(best);break
  if best is None:raise RuntimeError('Could not find stage '+str(stage))
 destination=ROOT/'unity/TiqueReturnPrototype/Assets/Resources/ReturnV2/puzzles.json'
 destination.parent.mkdir(exist_ok=True,parents=True)
 destination.write_text(json.dumps({'levels':selected},indent=2)+'\n',encoding='utf8')
if __name__=='__main__':main()
