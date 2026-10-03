from __future__ import annotations
from dataclasses import dataclass, field
from collections import defaultdict
import csv, random, math

ACTIONS = ("gather", "share", "attack", "rest", "explore")

@dataclass
class AgentState:
    id: int; x: int; y: int
    energy: float = 100.0; resource: float = 0.0; health: float = 100.0
    alive: bool = True
    trust: dict[int,float] = field(default_factory=dict)

class World:
    def __init__(self, n=20, w=20, h=20, seed=42):
        self.rng=random.Random(seed); self.w=w; self.h=h; self.t=0
        self.resources={(x,y):self.rng.uniform(2,10) for x in range(w) for y in range(h)}
        self.agents={i:AgentState(i,self.rng.randrange(w),self.rng.randrange(h)) for i in range(n)}
        for a in self.agents.values(): a.trust={j:.5 for j in self.agents if j!=a.id}
        self.events=[]
    def obs(self,i):
        a=self.agents[i]; near=[]
        for b in self.agents.values():
            if b.id!=i and b.alive:
                d=abs(a.x-b.x)+abs(a.y-b.y)
                if d<=2: near.append((b.id,d,b.energy,b.resource))
        return dict(x=a.x,y=a.y,energy=a.energy,resource=a.resource,health=a.health,
                    local=self.resources[(a.x,a.y)],nearby=near)
    @staticmethod
    def state(o):
        e='L' if o['energy']<20 else 'M' if o['energy']<60 else 'H'
        r='P' if o['local']<4 else 'M' if o['local']<7 else 'R'
        n='0' if not o['nearby'] else 'F' if len(o['nearby'])<=2 else 'M'
        return f'{e}|{r}|{n}'
    def nearest(self,a):
        c=[(abs(a.x-b.x)+abs(a.y-b.y),b) for b in self.agents.values() if b.id!=a.id and b.alive]
        return min(c,key=lambda z:z[0])[1] if c and min(c,key=lambda z:z[0])[0]<=2 else None
    def act(self,i,action):
        a=self.agents[i]; before=a.energy; before_r=a.resource; ev=[]; a.energy-=1
        if action=='gather':
            p=(a.x,a.y); q=min(self.resources[p],self.rng.uniform(1,5)); self.resources[p]-=q; a.resource+=q; a.energy+=.4*q; ev.append(('gather',q,None))
        elif action=='share':
            b=self.nearest(a)
            if b and a.resource>=1:
                q=min(2,a.resource); a.resource-=q; b.resource+=q; a.trust[b.id]=min(1,a.trust.get(b.id,.5)+.08); ev.append(('share',q,b.id))
        elif action=='attack':
            b=self.nearest(a)
            if b: d=self.rng.uniform(5,20); b.health-=d; a.energy-=2; a.trust[b.id]=max(0,a.trust.get(b.id,.5)-.25); ev.append(('attack',d,b.id))
        elif action=='rest':
            q=self.rng.uniform(2,5); a.energy+=q; ev.append(('rest',q,None))
        elif action=='explore':
            dx,dy=self.rng.choice(((-1,0),(1,0),(0,-1),(0,1))); a.x=max(0,min(self.w-1,a.x+dx)); a.y=max(0,min(self.h-1,a.y+dy)); a.energy-=.5; ev.append(('explore',1,None))
        if a.energy<=0 or a.health<=0: a.alive=False; ev.append(('death',1,None))
        reward=.5*(a.energy-before)+(a.resource-before_r)
        if action=='share': reward+=2
        if action=='attack': reward-=1.5
        if not a.alive: reward-=30
        if a.energy<10: reward-=2
        self.events += [(self.t,i,*e) for e in ev]
        return reward,self.obs(i)
    def tick(self):
        self.t+=1
        for p,v in self.resources.items(): self.resources[p]=min(10,v+self.rng.uniform(.05,.2))
    def metrics(self):
        alive=[a for a in self.agents.values() if a.alive]; total=max(1,len(self.events));
        rs=[a.resource for a in alive]
        shares=sum(e[2]=='share' for e in self.events); attacks=sum(e[2]=='attack' for e in self.events)
        return dict(step=self.t,alive=len(alive),avg_energy=sum(a.energy for a in alive)/len(alive) if alive else 0,
                    avg_resource=sum(rs)/len(rs) if rs else 0,cooperation_rate=shares/total,conflict_rate=attacks/total,gini=gini(rs))

class Learner:
    def __init__(self,seed=0): self.r=random.Random(seed); self.q=defaultdict(lambda:{a:0. for a in ACTIONS}); self.alpha=.08; self.gamma=.92; self.eps=.25
    def act(self,s): return self.r.choice(ACTIONS) if self.r.random()<self.eps else max(ACTIONS,key=lambda a:self.q[s][a])
    def update(self,s,a,r,ns):
        td=r+self.gamma*max(self.q[ns].values())-self.q[s][a]; self.q[s][a]+=self.alpha*td; return td
    def decay(self): self.eps=max(.03,self.eps*.999)

def gini(xs):
    xs=sorted(max(0,float(x)) for x in xs); n=len(xs); total=sum(xs)
    if not xs or total==0:return 0.
    return 2*sum((i+1)*x for i,x in enumerate(xs))/(n*total)-(n+1)/n

class JAESystem:
    def __init__(self,n=30,w=30,h=30,seed=2026):
        self.env=World(n,w,h,seed); self.learners={i:Learner(seed+i) for i in range(n)}; self.history=[]
    def step(self):
        ids=[i for i,a in self.env.agents.items() if a.alive]; self.env.rng.shuffle(ids)
        for i in ids:
            s=self.env.state(self.env.obs(i)); ac=self.learners[i].act(s); r,no=self.env.act(i,ac); ns=self.env.state(no); self.learners[i].update(s,ac,r,ns); self.learners[i].decay()
        self.env.tick(); m=self.env.metrics(); self.history.append(m); return m
    def run(self,steps=2000):
        for _ in range(steps):
            if not any(a.alive for a in self.env.agents.values()): break
            m=self.step()
            if m['step']%100==0: print(m)
        return self.history
    def export(self,path='jae_v3_metrics.csv'):
        if not self.history:return
        with open(path,'w',newline='',encoding='utf-8-sig') as f:
            w=csv.DictWriter(f,fieldnames=self.history[0]); w.writeheader(); w.writerows(self.history)

if __name__=='__main__':
    s=JAESystem(); s.run(); s.export(); print('done: jae_v3_metrics.csv')
