# -*- coding: utf-8 -*-
import re,html,json,collections
import trees
from trees import LAB,body,ind,SKIP,KEY
import condru
import condru
def fx(t):
    t=re.sub(r'в сцене, начинающейся словами «Из-за монументального стола[^»]*»','в сцене первой встречи с Лени (он выглядывает из-за стола)',t)
    t=re.sub(r'в сцене, начинающейся словами «([^»]{0,34})[^»]*»',lambda m:'в сцене, начинающейся словами «'+m.group(1)+'…»',t)
    return t
def cond_html(e): return fx(condru.cond_html(e))
def cond_plain(e): return fx(condru.cond_plain(e))
def clean(x): return re.sub(r'\{/?[a-z]+(=[^}]*)?\}','',x).replace('\\n',' ')
def q(x): return html.escape(x,quote=False).replace('"','&quot;')
def sh(x,n):
    x=clean(x); return x if len(x)<=n else x[:n-1]+'…'
CH={'less':'Лесс','dev':'Луиза','nars':'Нарси','tash':'Таш','fenya':'Феня','bonny':'Бонни','leni':'Лени','sova':'Сова','adro':'Адро','kap':'Кап','blu':'Блю','guard1':'Горран','guard2':'Алекс','slime':'Губерт','oh':'Адриан'}
def eff(t,owner):
    t=t[1:].strip()
    m=re.match(r'(\w+)\.mood\s*([+-])=\s*(\d+)',t)
    if m:
        who=m.group(1);n=int(m.group(3))*(1 if m.group(2)=='+' else -1)
        return ('mood',n) if who==owner else ('txt','настроение %s %s%d'%(CH.get(who,who),'+' if n>0 else '−',abs(n)))
    m=re.match(r'add_mad\((-?\d+)',t)
    if m: return ('mad',int(m.group(1)))
    m=re.match(r'add_logic\((-?\d+)',t)
    if m: return ('log',int(m.group(1)))
    m=re.match(r'([\w\.\[\]"]+)\s*=\s*(True|1|"[^"]*")\s*$',t)
    if m:
        d=cond_plain(m.group(1))
        d=re.sub(r'^уже произошло \(ставится (.*)\)$',r'\1',d)
        return ('txt','запоминается: '+d)
    m=re.match(r'([\w\.\[\]"]+)\s*=\s*(False|0)\s*$',t)
    if m: return ('txt','сбрасывается: '+re.sub(r'^уже произошло \(ставится (.*)\)$',r'\1',cond_plain(m.group(1))))
    return ('txt','изменение: '+sh(t,60))
C={'mood':'rgb(228,26,28)','mad':'rgb(112,72,232)','log':'rgb(28,126,214)'}
BG={'mood':'rgb(255,235,235)','mad':'rgb(237,231,251)','log':'rgb(227,242,250)'}
def chip(k,n): return '<span style=\'background:%s;color:%s;font-weight:700;border-radius:5px;padding:0 3px\'>%s%s%d</span>'%(BG[k],C[k],'▲+' if n>0 else '▼−',0,abs(n)) if False else '<span style=\'background:%s;color:%s;font-weight:700;border-radius:5px;padding:0 3px\'>%s%d</span>'%(BG[k],C[k],'▲+' if n>0 else '▼−',abs(n))
def has_stop(items):
    for it in items:
        if it[0] in ('menu','end','closed'): return True
        if it[0]=='cond' and any(has_stop(b[1]) for b in it[1]): return True
    return False
def flat(items):
    out=[]
    for it in items:
        if it[0]=='eff':
            e=it[1]
            if e[0] in C: out.append({'mood':'настроение','mad':'безумие','log':'логика'}[e[0]]+(' +' if e[1]>0 else ' −')+str(abs(e[1])))
            else: out.append(e[1])
        elif it[0]=='cond':
            for h,sub,t in it[1]: out+=flat(sub)
    return out
class B:
    def __init__(s,owner):
        s.owner=owner;s.hubs={};s.first={};s.memo={};s.stack=[];s.nh=0
    def hub2(s,*a): return s.hub(*a)
    def hub(s,lab,line,opts,rest):
        key=(lab,line)
        if key in s.hubs: return s.hubs[key]['id']
        s.nh+=1;hid='H%d'%s.nh
        H={'id':hid,'lab':lab,'n':len(opts),'exp':[],'targets':[],'opts':[o[0] for o in opts[:2]]}
        s.hubs[key]=H
        s.first.setdefault(lab,hid)
        cnt=[0]
        def nid(): cnt[0]+=1;return '%s_%d'%(hid,cnt[0])
        tails=[]
        for text,cond,items in opts:
            c=nid()
            if cond:
                cc=nid();s.condnode(H,cc,cond);H['exp'].append('%s --> %s'%(hid,cc));src=cc
            else: src=hid
            once=text.endswith(' \u2460')
            tx=text[:-2] if once else text
            tails+=s.card(H,c,'«%s»'%q(sh(tx,80))+(' <b style=\'color:#7c3aed;font-size:18px\'>\u2460</b>' if once else ''),items,src,nid)
        if tails:
            if rest:
                j=nid();H['exp'].append('%s(["далее"]):::ex'%j)
                for t in tails: H['exp'].append('%s --> %s'%(t,j))
                t2=s.follow(H,[j],rest,nid)
                s.endtails(H,t2,nid)
            else: s.endtails(H,tails,nid)
        return hid
    def condnode(s,H,cc,html_):
        H['exp'].append('%s(["<div style=\'width:240px;white-space:normal;text-align:left;padding:10px 16px\'>%s</div>"]):::cd'%(cc,html_))
    def endtails(s,H,tails,nid):
        if not tails: return
        e=nid();H['exp'].append('%s["дальше без новых выборов"]:::ex'%e)
        for t in tails: H['exp'].append('%s --> %s'%(t,e))
    def card(s,H,c,title,items,src,nid):
        ups=[];dns=[];txt=[]
        k=0
        while k<len(items) and items[k][0]=='eff':
            e=items[k][1];k+=1
            if e[0] in C: (ups if e[1]>0 else dns).append((e[0],e[1]))
            else: txt.append(e[1])
        rest=items[k:]
        body_=title
        for t in txt:
            P='запоминается: при выборе варианта «'
            inner_=re.sub(r'<[^>]+>','',title).replace('\u2460','').strip()[1:-1].strip().rstrip('»').strip()
            if t.startswith(P+inner_[:25]): continue
            body_+='<br/><span style=\'font-size:12px;color:#92400e;font-weight:700\'>%s</span>'%q(t)
        pad='padding:%s 10px %s 10px'%('18px' if ups else '4px','18px' if dns else '4px')
        h='<div style=\'position:relative;display:inline-block;width:240px;white-space:normal;text-align:left;%s\'>%s'%(pad,body_)
        if ups: h+='<span style=\'position:absolute;top:2px;right:3px;font-size:14px;white-space:nowrap\'>%s</span>'%' '.join(chip(a,b) for a,b in ups)
        if dns: h+='<span style=\'position:absolute;bottom:2px;left:3px;font-size:14px;white-space:nowrap\'>%s</span>'%' '.join(chip(a,b) for a,b in dns)
        h+='</div>'
        H['exp'].append('%s["%s"]:::op'%(c,h)); H['exp'].append('%s --> %s'%(src,c))
        return s.follow(H,[c],rest,nid)
    def follow(s,H,cur,items,nid):
        k=0
        while k<len(items):
            it=items[k]
            if it[0]=='menu':
                for c in cur: H['exp'].append('%s --> %s'%(c,it[1]))
                H['targets'].append(it[1]);return []
            if it[0]=='closed': return []
            if it[0]=='end':
                e=nid();H['exp'].append('%s["%s"]:::ex'%(e,it[1]))
                for c in cur: H['exp'].append('%s --> %s'%(c,e))
                return []
            if it[0]=='eff':
                effs=[]
                while k<len(items) and items[k][0]=='eff': effs.append(items[k]);k+=1
                d=nid();cur=s.card(H,d,'<i>затем</i>',effs,cur[0],nid) if len(cur)==1 else s.cardm(H,d,effs,cur,nid)
                continue
            if it[0]=='cond' and not has_stop([it]):
                run=[]
                while k<len(items) and items[k][0]=='cond' and not has_stop([items[k]]):
                    run.append(items[k]);k+=1
                lines=[]
                for r in run:
                    for head,sub,t in r[1]:
                        fl=flat(sub)
                        if fl: lines.append('<div style=\'margin:4px 0\'>%s<br/><span style=\'font-size:12px;color:#92400e;font-weight:700\'>%s</span></div>'%(head,q('; '.join(fl))))
                if lines:
                    d=nid();H['exp'].append('%s(["<div style=\'width:300px;white-space:normal;text-align:left;padding:10px 16px\'><b>Пока идёт сцена, по условиям:</b>%s</div>"]):::cd'%(d,''.join(lines)))
                    for c in cur: H['exp'].append('%s --> %s'%(c,d))
                    cur=[d]
                continue
            if it[0]=='cond':
                new=[];has_else=any(h.startswith('<b>иначе') for h,_,_ in it[1])
                for head,sub,term in it[1]:
                    cc=nid();s.condnode(H,cc,head)
                    for c in cur: H['exp'].append('%s --> %s'%(c,cc))
                    if not sub: new.append(cc)
                    elif sub[0][0]=='eff' : new+=s.card(H,nid(),'<i>затем</i>',sub,cc,nid)
                    else: new+=s.follow(H,[cc],sub,nid)
                if not has_else: new+=cur
                if len(new)>1:
                    jn=nid();H['exp'].append('%s((" ")):::jn'%jn)
                    for c in new: H['exp'].append('%s --> %s'%(c,jn))
                    new=[jn]
                cur=new
            k+=1
        return cur
    def cardm(s,H,d,effs,cur,nid):
        j=nid();H['exp'].append('%s(["далее"]):::ex'%j)
        for c in cur: H['exp'].append('%s --> %s'%(c,j))
        return s.card(H,d,'<i>затем</i>',effs,j,nid)
    # ---- walk
    def walk(s,lab):
        if lab in s.memo: return s.memo[lab]
        if lab in s.stack:
            h=s.first.get(lab)
            return ([('menu',h)] if h else [('end','возврат к началу этой же сцены')]),True
        s.stack.append(lab)
        fn,i,lines=body(lab)
        r=s.blk(lab,lines,0,len(lines))
        s.stack.pop();s.memo[lab]=r;return r
    def blk(s,lab,lines,st,e):
        items=[];k=st
        while k<e:
            raw=lines[k];t=raw.strip()
            if not t or t.startswith('#'): k+=1;continue
            base=ind(raw);j=k+1
            while j<e and (not lines[j].strip() or ind(lines[j])>base): j+=1
            if t.startswith('menu'):
                first=None
                for z in range(k+1,j):
                    if lines[z].strip(): first=ind(lines[z]);break
                idxs=[z for z in range(k+1,j) if lines[z].strip() and ind(lines[z])==first and lines[z].rstrip().endswith(':') and lines[z].strip().startswith('"')]
                rest,rterm=s.blk(lab,lines,j,e)
                s.first.setdefault(lab,'H%d'%(s.nh+1))
                opts=[]
                for n,z in enumerate(idxs):
                    end=idxs[n+1] if n+1<len(idxs) else j
                    m=re.match(r'"(.*)"\s*(?:if (.*))?:$',lines[z].strip())
                    if not m: continue
                    it,term=s.blk(lab,lines,z+1,end)
                    if term: it=it+[('closed',)]
                    cond=None
                    once=False
                    if m.group(2):
                        chh=cond_html(m.group(2)).replace('ещё не произошло (ставится при выборе варианта «%s»)'%q(m.group(1)),'ОНЦЕ').replace('ещё не произошло (ставится при выборе варианта «%s»)'%q(sh(m.group(1),70)),'ОНЦЕ')
                        parts=chh.split('<br/><b>и одновременно</b><br/>')
                        if 'ОНЦЕ' in parts:
                            once=True;parts=[p for p in parts if p!='ОНЦЕ']
                        chh='<br/><b>и одновременно</b><br/>'.join(parts)
                        if parts and chh and 'ОНЦЕ' not in chh and '(' not in chh[:0]:
                            cond='Вариант виден, если:<br/>%s<br/><small style=\'color:#9ca3af\'>%s</small>'%(chh,q(sh(m.group(2),80)))
                    text=m.group(1)+(' \u2460' if once else '')
                    opts.append((text,cond,it))
                hid=s.hub2(lab,k,opts,rest)
                items.append(('menu',hid));return items,True
            m=re.match(r'(if|elif|else)\b(.*):$',t)
            if m:
                chain=[];z=k
                while z<e:
                    tz=lines[z].strip();mz=re.match(r'(if|elif|else)\b(.*):$',tz)
                    if not mz or (z!=k and (ind(lines[z])!=base or mz.group(1)=='if')): break
                    jz=z+1
                    while jz<e and (not lines[jz].strip() or ind(lines[jz])>base): jz+=1
                    chain.append((mz.group(1),mz.group(2).strip(),z,jz));z=jz
                    while z<e and not lines[z].strip(): z+=1
                nxt=chain[-1][3] if chain else j
                br=[];alls=True;has_else=False
                for kd,ce,z0,z1 in chain:
                    it,term=s.blk(lab,lines,z0+1,z1)
                    if kd=='else': head='<b>иначе</b>';has_else=True
                    else: head='%s<br/>%s<br/><small style=\'color:#9ca3af\'>%s</small>'%('<b>Если</b>' if kd=='if' else '<b>Если не так, то</b>',cond_html(ce),q(sh(ce,80)))
                    if it or not term: br.append((head,it,term))
                    alls=alls and term
                if br: items.append(('cond',br))
                if alls and has_else: return items,True
                k=nxt;continue
            m=re.match(r'(jump|call) (\w+)',t)
            if m:
                l=m.group(2)
                if l in LAB:
                    sub,term=s.walk(l)
                    items+=sub
                    if m.group(1)=='jump' or term: return items,True
                else:
                    items.append(('end','переход на метку «%s» (не найдена в коде)'%q(l)))
                    if m.group(1)=='jump': return items,True
                k=j;continue
            if t.startswith('return'): items.append(('end','возврат из сцены'));return items,True
            if 'call_screen_strel' in t:
                items.append(('end','возврат на экран переходов'));return items,True
            if t.startswith('$') and not SKIP.match(t) and KEY.search(t):
                items.append(('eff',eff(t,s.owner)))
            k=j if t.startswith('$') else k+1
            if not t.startswith('$'): k=k
        return items,False
def build(lab,owner):
    condru.LEG.clear()
    b=B(owner)
    items,_=b.walk(lab)
    # start pseudo hub
    S={'id':'S','exp':[],'targets':[]}
    cnt=[0]
    def nid(): cnt[0]+=1;return 'S_%d'%cnt[0]
    b.follow(S,['START'],items,nid)
    hubs={h['id']:{'n':h['n'],'lab':h['lab'],'opts':h['opts'],'exp':h['exp'],'targets':h['targets']} for h in b.hubs.values()}
    return {'start':S['exp'],'hubs':hubs,'leg':dict(condru.LEG)}
