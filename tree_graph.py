# -*- coding: utf-8 -*-
import re,html,zlib
import trees
from trees import LAB,body,ind,SKIP,KEY,SP
from condru import cond_ru
def clean(x): return re.sub(r'\{/?[a-z]+(=[^}]*)?\}','',x)
def q(x): return html.escape(x,quote=False).replace('"','&quot;')
def sh(x,n): 
    x=clean(x).replace('\\n',' ')
    return x if len(x)<=n else x[:n-1]+'…'
class G:
    def __init__(s,maxd=3):
        s.n=0;s.L=['flowchart TD'];s.entry={};s.maxd=maxd;s.cls=[];s.rets={};s.opts=[]
    def node(s,html_,kind='sc'):
        s.n+=1;i='N%d'%s.n
        if kind=='cd': s.L.append('%s{{"<div style=\'width:300px;white-space:normal;text-align:left\'>%s</div>"}}:::cd'%(i,html_))
        else: s.L.append('%s["<div style=\'width:%dpx;white-space:normal\'>%s</div>"]:::%s'%(i,340 if kind=='sc' else 280,html_,kind))
        return i
    def edge(s,a,b,lab=''):
        if lab: s.L.append('%s -->|"<div style=\'width:200px;white-space:normal;text-align:left\'>%s</div>"| %s'%(a,lab,b))
        else: s.L.append('%s --> %s'%(a,b))
    def link(s,pend,nid):
        for a,l in pend: s.edge(a,nid,l)
    def flush(s,buf,pend):
        if not buf: return pend
        lines=[b for b in buf]
        txt=[];eff=[]
        for k,t in lines:
            (txt if k=='t' else eff).append(t)
        h=''
        T=txt[:7]
        h+='<br/>'.join(T)
        if len(txt)>7: h+='<br/><i>… ещё реплик: %d (полностью в тексте ниже)</i>'%(len(txt)-7)
        for e in eff: h+='<br/><span style=\'font-size:12px;color:#92400e;font-weight:700\'>🚩 %s</span>'%e
        nid=s.node(h,'sc'); s.link(pend,nid); return [(nid,'')]
    def run(s,lab):
        fn,i,_=body(lab)
        a=s.node('Начало ветки <small style=\'color:#6b7280\'>%s</small>'%q(lab),'an')
        lines=body(lab)[2]
        return s.blk(lines,0,len(lines),[(a,'')],0)
    def blk(s,lines,st,e,pend,depth):
        k=st;buf=[]
        while k<e:
            raw=lines[k];t=raw.strip()
            if not t or t.startswith('#'): k+=1;continue
            base=ind(raw);j=k+1
            while j<e and (not lines[j].strip() or ind(lines[j])>base): j+=1
            if t.startswith('menu'):
                pend=s.flush(buf,pend);buf=[]
                first=None
                for z in range(k+1,j):
                    if lines[z].strip(): first=ind(lines[z]);break
                idxs=[z for z in range(k+1,j) if lines[z].strip() and ind(lines[z])==first and lines[z].rstrip().endswith(':') and lines[z].strip().startswith('"')]
                c=s.node('Выбор игрока','ch'); s.link(pend,c)
                ex=[]
                for n,z in enumerate(idxs):
                    end=idxs[n+1] if n+1<len(idxs) else j
                    m=re.match(r'"(.*)"\s*(?:if (.*))?:$',lines[z].strip())
                    if not m: continue
                    lab='«%s»'%q(sh(m.group(1),80))
                    if m.group(2): lab+='<br/><small>если %s</small><br/><small style=\'color:#9ca3af\'>%s</small>'%(q(sh(cond_ru(m.group(2)),110)),q(sh(m.group(2),70)))
                    if len(idxs)>=4 and (end-z)>3:
                        key='opt%d_%d'%(zlib.crc32(''.join(lines[z:z+4]).encode())%100000,z)
                        r=s.node('→ Вариант «%s»<br/><i style=\'font-size:12px\'>нажмите: схема этого варианта ниже</i>'%q(sh(m.group(1),70)),'ret'); s.edge(c,r,lab); s.rets[r]=key
                        s.opts.append((key,sh(m.group(1),90),lines,z+1,end)); ex.append((r,'после варианта'))
                    else:
                        ex+=s.blk(lines,z+1,end,[(c,lab)],depth)
                pend=ex; k=j; continue
            m=re.match(r'(if|elif|else)\b(.*):$',t)
            if m:
                pend=s.flush(buf,pend);buf=[]
                # gather chain
                chain=[];z=k
                while z<e:
                    tz=lines[z].strip();mz=re.match(r'(if|elif|else)\b(.*):$',tz)
                    if not mz or (z!=k and (ind(lines[z])!=base or mz.group(1)=='if')): break
                    jz=z+1
                    while jz<e and (not lines[jz].strip() or ind(lines[jz])>base): jz+=1
                    chain.append((mz.group(1),mz.group(2).strip(),z,jz)); z=jz
                    while z<e and not lines[z].strip(): z+=1
                conds=[(kd,ce) for kd,ce,_,_ in chain if kd!='else']
                if len(conds)==1:
                    dt='<b>Если</b> %s<br/><small style=\'color:#9ca3af\'>%s</small>'%(q(sh(cond_ru(conds[0][1]),300)),q(sh(conds[0][1],90)))
                else:
                    dt='<b>Проверяется по порядку:</b>'+''.join('<br/><b>%d)</b> %s<br/><small style=\'color:#9ca3af\'>%s</small>'%(n+1,q(sh(cond_ru(ce),240)),q(sh(ce,80))) for n,(kd,ce) in enumerate(conds))
                d=s.node(dt,'cd'); s.link(pend,d)
                ex=[];has_else=False;cn=0
                for kind,ce,z0,z1 in chain:
                    if kind=='else': has_else=True;lab='иначе'
                    else:
                        cn+=1;lab=('да' if len(conds)==1 else str(cn))
                    ex+=s.blk(lines,z0+1,z1,[(d,lab)],depth)
                if not has_else: ex.append((d,'нет' if len(conds)==1 else 'ни одно'))
                pend=ex; k=chain[-1][3] if chain else j
                while k<e and not lines[k].strip(): k+=1
                continue
            m=re.match(r'(\w+) "(.*)"$',t) or re.match(r'()"(.*)"$',t)
            if m and not t.startswith('$'):
                buf.append(('t','<b>%s:</b> %s'%(q(SP.get(m.group(1),m.group(1) or 'Рассказчик')),q(sh(m.group(2),130)))));k+=1;continue
            m=re.match(r'(jump|call) (\w+)',t)
            if m:
                pend=s.flush(buf,pend);buf=[]
                l=m.group(2)
                if l in LAB:
                    r=s.node('→ Ветка <small>%s</small><br/><i style=\'font-size:12px\'>нажмите: перейти к схеме этой ветки ниже</i>'%q(l),'ret'); s.link(pend,r); s.rets[r]=l
                    ex=[(r,'после возврата')] if m.group(1)=='call' else []
                else:
                    g=s.node('Переход на метку <small>%s</small><br/><i>метка не найдена в коде</i>'%q(l),'gap'); s.link(pend,g); ex=[]
                pend=ex
                k+=1;continue
            if 'call_screen_strel' in t:
                pend=s.flush(buf,pend);buf=[]
                x=s.node('Возврат на экран переходов','ex'); s.link(pend,x); pend=[]; k+=1;continue
            if SKIP.match(t): k+=1;continue
            if t.startswith('$') and KEY.search(t): buf.append(('e','<code>%s</code>'%q(sh(t[1:].strip(),90))));k+=1;continue
            k+=1
        return s.flush(buf,pend)
def graph(lab,title,maxd=3):
    """returns list of (key,title,src,rets) in BFS order"""
    out=[];seen={lab:0};queue=[(lab,None,0)];DP={}
    CL=('ret fill:#fff7ed,stroke:#ea580c,color:#7c2d12','sc fill:#f0f9ff,stroke:#0369a1,color:#0f172a','ch fill:#fef3c7,stroke:#b45309,color:#0f172a','cd fill:#ede9fe,stroke:#7c3aed,color:#0f172a','an fill:#dcfce7,stroke:#15803d,color:#0f172a','ex fill:#e5e7eb,stroke:#6b7280,color:#0f172a','gap fill:#fff,stroke:#b91c1c,stroke-dasharray:4 3,color:#7f1d1d')
    while queue:
        key,opt,dp=queue.pop(0);g=G()
        if opt is None:
            g.run(key);ttl='Ветка <code>%s</code>'%key
        else:
            t,lines,z,end=opt
            a=g.node('Вариант выбора: <b>«%s»</b>'%q(t),'an')
            g.blk(lines,z,end,[(a,'')],0);ttl='Вариант выбора «%s»'%html.escape(t)
        for c in CL: g.L.append('classDef '+c)
        rets={}
        for r,t in g.rets.items():
            if t.startswith('opt'): rets[r]=t;continue
            if t not in seen:
                if dp<maxd: seen[t]=dp+1;queue.append((t,None,dp+1))
                else: seen[t]=-1
            rets[r]=t if seen[t]>=0 else None
        for (k2,t2,ls,z2,e2) in g.opts: queue.append((k2,(t2,ls,z2,e2),dp))
        out.append((key,ttl,'\n'.join(g.L),rets))
    return out
