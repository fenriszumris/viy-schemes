# -*- coding: utf-8 -*-
import re,html
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
        s.n=0;s.L=['flowchart TD'];s.entry={};s.maxd=maxd;s.cls=[]
    def node(s,html_,kind='sc'):
        s.n+=1;i='N%d'%s.n
        if kind=='cd': s.L.append('%s{"<div style=\'width:260px;white-space:normal\'>%s</div>"}:::cd'%(i,html_))
        else: s.L.append('%s["<div style=\'width:%dpx;white-space:normal\'>%s</div>"]:::%s'%(i,340 if kind=='sc' else 280,html_,kind))
        return i
    def edge(s,a,b,lab=''):
        if lab: s.L.append('%s -->|"%s"| %s'%(a,lab,b))
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
    def run(s,lab,pend,depth,label_edge=''):
        # anchor for label
        fn,i,_=body(lab)
        a=s.node('Ветка <small style=\'color:#6b7280\'>%s</small>'%q(lab),'an'); s.entry[lab]=a
        for p,l in pend: s.edge(p,a,l or label_edge)
        _,lines=fn,body(lab)[2]
        return s.blk(lines,0,len(lines),[(a,'')],depth)
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
                d=s.node('Проверка условия','cd'); s.link(pend,d)
                ex=[];has_else=False
                for kind,ce,z0,z1 in chain:
                    if kind=='else': has_else=True;lab='иначе'
                    else: lab=('Если ' if kind=='if' else 'Иначе, если ')+q(sh(cond_ru(ce),120))+'<br/><small style=\'color:#9ca3af\'>%s</small>'%q(sh(ce,70))
                    ex+=s.blk(lines,z0+1,z1,[(d,lab)],depth)
                if not has_else: ex.append((d,'иначе (ничего не происходит)'))
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
                if l in s.entry:
                    for p,la in pend: s.edge(p,s.entry[l],la or 'переход')
                    ex=[]
                elif l in LAB and depth<s.maxd:
                    ex=s.run(l,pend,depth+1,'переход')
                elif l in LAB:
                    g=s.node('Дальше ветка <small>%s</small><br/><i>глубже трёх уровней: не показано</i>'%q(l),'gap'); s.link(pend,g); ex=[]
                else:
                    g=s.node('Переход на метку <small>%s</small><br/><i>метка не найдена в коде</i>'%q(l),'gap'); s.link(pend,g); ex=[]
                pend=ex if m.group(1)=='call' else []
                k+=1;continue
            if 'call_screen_strel' in t:
                pend=s.flush(buf,pend);buf=[]
                x=s.node('Возврат на экран переходов','ex'); s.link(pend,x); pend=[]; k+=1;continue
            if SKIP.match(t): k+=1;continue
            if t.startswith('$') and KEY.search(t): buf.append(('e','<code>%s</code>'%q(sh(t[1:].strip(),90))));k+=1;continue
            k+=1
        return s.flush(buf,pend)
def graph(lab,title):
    g=G()
    fn,i,_=body(lab)
    st=g.node('<b>%s</b>'%q(title),'st')
    g.run(lab,[(st,'')],0)
    g.L.append('classDef sc fill:#f0f9ff,stroke:#0369a1,color:#0f172a')
    g.L.append('classDef ch fill:#fef3c7,stroke:#b45309,color:#0f172a')
    g.L.append('classDef cd fill:#ede9fe,stroke:#7c3aed,color:#0f172a')
    g.L.append('classDef an fill:#f3f4f6,stroke:#9ca3af,color:#374151')
    g.L.append('classDef st fill:#dcfce7,stroke:#15803d,color:#0f172a')
    g.L.append('classDef ex fill:#e5e7eb,stroke:#6b7280,color:#0f172a')
    g.L.append('classDef gap fill:#fff,stroke:#b91c1c,stroke-dasharray:4 3,color:#7f1d1d')
    return '\n'.join(g.L),g.n
