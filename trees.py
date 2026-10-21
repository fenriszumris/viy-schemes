# -*- coding: utf-8 -*-
import re,glob,html
SP={'v':'Героиня','a':'Рассказчик','aa':'Рассказчик','vm':'Мысль героини','vvv':'Героиня','n':'Нарси','t':'Таш','ls':'Лесс','lss':'Лесс','ka':'Капибара','b':'Бонни','d':'Луиза','f':'Феня','sov':'Сова','g1':'Горран','g2':'Алекс','l':'Лени','k':'Карралак','sadr':'Адро','e1':'Эльф (Риал)','e2':'Эльф'}
LAB={}
LINES={}
for f in glob.glob('/tmp/viy/game/*.rpy'):
    ls=open(f,encoding='utf8',errors='ignore').read().split('\n')
    fn=f.split('/')[-1]
    LINES[fn]=ls
    for i,l in enumerate(ls):
        m=re.match(r'label (\w+):',l)
        if m: LAB[m.group(1)]=(fn,i)
def ind(l): return len(l)-len(l.lstrip(' \t'))
def body(lab):
    fn,i=LAB[lab];out=[]
    for l in LINES[fn][i+1:]:
        if re.match(r'(label|screen|init)\b',l): break
        out.append(l)
    return fn,i,out
SKIP=re.compile(r'^(show|hide|with|play|stop|pause|scene|window|queue|voice|image|transform|\$ (set_|show_|change_music|play|renpy\.transition|sleep|persistent_append\("[^"]*", *"diary)|\$ razg|\$ screens|\$ blood_effect)')
KEY=re.compile(r'(mood|sanity|add_mad|add_logic|moral|blood|quests|persistent|inv_list|\.near|\.lock|\.zn_|\.d\d|\.bad|\.good|renpy\.full_restart|money|_note|memory)')
def esc(x): return html.escape(re.sub(r'\{/?[a-z]+(=[^}]*)?\}','',x))
def render(lab,depth=0,seen=None,maxd=3):
    seen=set() if seen is None else seen
    fn,i,lines=body(lab)
    seen.add(lab)
    html_,_=blk(lines,0,len(lines),seen,depth,maxd)
    return html_
def blk(lines,s,e,seen,depth,maxd):
    out=[];k=s
    while k<e:
        raw=lines[k];t=raw.strip()
        if not t or t.startswith('#'): k+=1;continue
        base=ind(raw)
        # extent of this statement's nested block
        j=k+1
        while j<e and (not lines[j].strip() or ind(lines[j])>base): j+=1
        if t.startswith('menu'):
            opts=[];q=k+1
            while q<j:
                r=lines[q];ts=r.strip()
                if ts and ind(r)==ind(lines[k+1]) if k+1<j else False:
                    pass
                q+=1
            # options: lines at the first-level indent inside menu ending with ':'
            first=None
            for q in range(k+1,j):
                if lines[q].strip(): first=ind(lines[q]);break
            idxs=[q for q in range(k+1,j) if lines[q].strip() and ind(lines[q])==first and lines[q].rstrip().endswith(':') and lines[q].strip().startswith('"')]
            h='<ul class="tr">'
            for n,q in enumerate(idxs):
                end=idxs[n+1] if n+1<len(idxs) else j
                m=re.match(r'"(.*)"\s*(?:if (.*))?:$',lines[q].strip())
                if not m: continue
                cond=' <span class="muted">(если <code>%s</code>)</span>'%html.escape(m.group(2)) if m.group(2) else ''
                inner,_=blk(lines,q+1,end,seen,depth,maxd)
                h+='<li><b>Вариант: «%s»</b>%s%s</li>'%(esc(m.group(1)),cond,inner)
            out.append('<div class="muted">Выбор:</div>'+h+'</ul>')
            k=j;continue
        m=re.match(r'(if|elif|else)\b(.*):$',t)
        if m:
            inner,_=blk(lines,k+1,j,seen,depth,maxd)
            c={'if':'Если','elif':'Иначе, если','else':'Иначе'}[m.group(1)]
            out.append('<div class="cond"><span class="muted">%s <code>%s</code>:</span>%s</div>'%(c,html.escape(m.group(2).strip()),inner))
            k=j;continue
        m=re.match(r'(\w+) "(.*)"$',t) or re.match(r'()"(.*)"$',t)
        if m and not t.startswith('$'):
            who=SP.get(m.group(1),m.group(1) or 'Рассказчик')
            out.append('<div class="sp"><b>%s:</b> %s</div>'%(who,esc(m.group(2))));k=j if False else k+1;continue
        m=re.match(r'(jump|call) (\w+)',t)
        if m:
            l=m.group(2)
            if l in LAB and l not in seen and depth<maxd:
                seen.add(l)
                fn,i,_=body(l)
                out.append('<details><summary>Переход на ветку <code>%s</code> <span class="muted">(%s:%d)</span></summary>%s</details>'%(l,fn,i+1,render(l,depth+1,seen,maxd)))
            else:
                out.append('<div class="muted">Переход на <code>%s</code>%s</div>'%(l,' (уже показана выше или глубже)' if l in LAB else ' (метка не найдена)'))
            k+=1;continue
        if 'call_screen_strel' in t: out.append('<div class="muted">Возврат на экран переходов.</div>');k+=1;continue
        if SKIP.match(t): k+=1;continue
        if t.startswith('$') and KEY.search(t): out.append('<div class="eff"><code>%s</code></div>'%html.escape(t[1:].strip()));k+=1;continue
        k+=1
    return ''.join(out),k
