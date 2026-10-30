# -*- coding: utf-8 -*-
import re,html
import trees
from trees import LAB,body,ind,SKIP,KEY
import condru
from condru import cond_html,cond_plain
def clean(x): return re.sub(r'\{/?[a-z]+(=[^}]*)?\}','',x).replace('\\n',' ')
def q(x): return html.escape(x,quote=False)
def sh(x,n):
    x=clean(x); return x if len(x)<=n else x[:n-1]+'…'
CH={'less':'Лесс','ls':'Лесс','dev':'Луиза','nars':'Нарси','tash':'Таш','fenya':'Феня','bonny':'Бонни','leni':'Лени','sova':'Сова','adro':'Адро','kap':'Кап','blu':'Блю','guard1':'Горран','guard2':'Алекс','slime':'Губерт','oh':'Адриан'}
def eff(t):
    t=t[1:].strip()
    m=re.match(r'(\w+)\.mood\s*([+-])=\s*(\d+)',t)
    if m: return ('mood','настроение %s: %s%s'%(CH.get(m.group(1),m.group(1)),'+' if m.group(2)=='+' else '−',m.group(3)),m.group(2))
    m=re.match(r'add_mad\((-?\d+)',t)
    if m: n=int(m.group(1));return ('mad','безумие %s%d'%('+' if n>=0 else '−',abs(n)),'')
    m=re.match(r'add_logic\((-?\d+)',t)
    if m: n=int(m.group(1));return ('log','логика %s%d'%('+' if n>=0 else '−',abs(n)),'')
    m=re.match(r'([\w\.\[\]"]+)\s*=\s*(True|1|"[^"]*")\s*$',t)
    if m: return ('flag','⚑ запоминается: '+cond_plain(m.group(1)),'')
    m=re.match(r'([\w\.\[\]"]+)\s*=\s*(False|0)\s*$',t)
    if m: return ('flag','⚑ сбрасывается: '+cond_plain(m.group(1)),'')
    return ('code','⚑ <code>%s</code>'%q(sh(t,70)),'')
class R:
    def __init__(s,budget=900): s.budget=budget;s.n=0
    def chip(s,t):
        k,txt,_=eff(t)
        txt=re.sub(r'запоминается: уже произошло \(ставится (.*)\)$',r'запоминается: \1',txt)
        txt=txt if k=='flag' and txt.startswith('⚑') and '<code>' not in txt else txt
        return '<span class="chip %s">%s</span>'%(k,txt if k=='code' else q(txt))
    def run(s,lab,path,depth):
        fn,i,lines=body(lab)
        return s.blk(lines,0,len(lines),path+(lab,),depth)
    def blk(s,lines,st,e,path,depth):
        k=st;out=[]
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
                opts=''
                for n,z in enumerate(idxs):
                    end=idxs[n+1] if n+1<len(idxs) else j
                    m=re.match(r'"(.*)"\s*(?:if (.*))?:$',lines[z].strip())
                    if not m: continue
                    s.n+=1
                    inner=s.blk(lines,z+1,end,path,depth)
                    cond=''
                    if m.group(2):
                        ch_=cond_html(m.group(2)).replace('ещё не произошло (ставится при выборе варианта «%s»)'%q(sh(m.group(1),70)),'этот вариант ещё не выбирался').replace('ещё не произошло (ставится при выборе варианта «%s»)'%q(m.group(1)),'этот вариант ещё не выбирался')
                        cond='<div class="cb">Вариант виден, если:<br/>%s<br/><small>%s</small></div>'%(ch_,q(sh(m.group(2),90)))
                    sm='<summary>«%s»%s</summary>'%(q(sh(m.group(1),90)),' <span class="cnd">🔒 есть условие</span>' if cond else '')
                    opts+='<details class="op">%s%s%s</details>'%(sm,cond,('<div class="in">%s</div>'%inner) if inner else '<div class="in end">дальше без новых выборов</div>')
                out.append('<details class="ch" open><summary>Выбор игрока · вариантов: %d</summary>%s</details>'%(len(idxs),opts))
                k=j;continue
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
                parts=''
                for kd,ce,z0,z1 in chain:
                    inner=s.blk(lines,z0+1,z1,path,depth)
                    if not inner: continue
                    if kd=='else': head='<b>иначе</b>'
                    else: head='<b>%s</b><br/>%s<br/><small>%s</small>'%('Если' if kd=='if' else 'Если не так, то',cond_html(ce),q(sh(ce,90)))
                    parts+='<details class="cd"><summary class="cb">%s</summary><div class="in">%s</div></details>'%(head,inner)
                if parts: out.append(parts)
                k=chain[-1][3] if chain else j
                while k<e and not lines[k].strip(): k+=1
                continue
            m=re.match(r'(jump|call) (\w+)',t)
            if m:
                l=m.group(2)
                if l in LAB:
                    if l in path: out.append('<div class="note">↩ возврат к выбору, раскрытому выше</div>')
                    elif depth>=6 or s.n>s.budget: out.append('<div class="note">дальше идёт продолжение сцены (глубже не раскрыто)</div>')
                    else:
                        inner=s.run(l,path,depth+1)
                        if inner: out.append(inner)
                if m.group(1)=='jump': break
                k+=1;continue
            if t.startswith('$') and not SKIP.match(t) and KEY.search(t):
                c=s.chip(t)
                if c: out.append(c)
            k+=1
        return ''.join(out)
CSS='''<style>.ctree details{margin:6px 0}.ctree summary{cursor:pointer}.ctree .ch>summary{font-weight:700;background:#fef3c7;border:1px solid #b45309;border-radius:10px;padding:6px 10px}.ctree .op{border-left:3px solid #b45309;margin-left:10px;padding-left:8px}.ctree .op>summary{padding:4px 6px;border-radius:8px;background:#fffbeb}.ctree .in{margin-left:8px;padding-left:8px;border-left:2px dotted #d1d5db}.ctree .in.end,.ctree .note{color:#6b7280;font-size:13px;margin:4px 0}.ctree .cb{background:#ede9fe;border:1px solid #7c3aed;border-radius:16px;padding:6px 12px;display:block;font-size:14px}.ctree .cd>summary{list-style:none}.ctree small{color:#9ca3af}.ctree .chip{display:inline-block;margin:2px 4px 2px 0;padding:1px 8px;border-radius:10px;font-size:13px;background:#f3f4f6;border:1px solid #d1d5db}.ctree .chip.mood{background:#ffebeb;border-color:#e41a1c}.ctree .chip.mad{background:#ede9fe}.ctree .chip.log{background:#dbeafe}.ctree .chip.flag{background:#fff7ed;border-color:#ea580c}.ctree .cnd{font-size:12px;color:#7c3aed}</style>'''
def tree(lab):
    condru.LEG.clear()
    r=R();h=r.run(lab,(),0)
    return CSS+'<div class="ctree">'+h+'</div>',r.n
if __name__=='__main__':
    h,n=tree('script_4_airat_leni_dialog');print(len(h),n)
