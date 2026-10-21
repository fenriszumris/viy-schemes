# -*- coding: utf-8 -*-
import re,glob,html,sys,collections
sys.path.insert(0,'/tmp/sch')
import condru
V=317
condru._scan()
SET=condru._SET;RESET=condru._RESET
FILES={}
for f in sorted(glob.glob('/tmp/viy/game/*.rpy')): FILES[f.split('/')[-1]]=open(f,encoding='utf8',errors='ignore').read().split('\n')
esc=html.escape
def needle(k):
    m=re.fullmatch(r'"([^"]+)" in mem:(\w+)',k)
    if m: return re.compile(r'"%s" (?:not )?in (?:vrem_memory|persistent\.memory)\["%s"\]'%(re.escape(m.group(1)),m.group(2)))
    m=re.fullmatch(r'"([^"]+)" in ([\w\.]+)',k)
    if m: return re.compile(r'"%s" (?:not )?in %s(?![\w])'%(re.escape(m.group(1)),re.escape(m.group(2))))
    m=re.fullmatch(r'(\w+)\.d(\d+)',k)
    if m: return re.compile(r'(?<![\w\.])%s\.d%s(?![\w])'%(m.group(1),m.group(2)))
    if re.fullmatch(r'\w+',k): return re.compile(r'(?<![\w\.\"])%s(?![\w\"])'%k)
    return None

MN={}
for _l in FILES.get('script _define.rpy',[])+sum(FILES.values(),[]):
    _m=re.search(r'memoris_notes\["(\w+)"\] = memory_diary\(name = "([^"]+)"',_l)
    if _m: MN[_m.group(1)]=_m.group(2)
def _ind(l): return len(l)-len(l.lstrip(' '))
ASG=re.compile(r'(quests|memoris_notes)\["(\w+)"\](?:\.diary)?\.(_part_text|_rtext)\[(\d+)\](\[1\])?\s*=\s*(.*)$')
def consequence(fn,ln):
    ls=FILES[fn];base=_ind(ls[ln-1]);out=[]
    for j in range(ln,min(ln+8,len(ls))):
        l=ls[j]
        if not l.strip(): continue
        if _ind(l)<=base: break
        m=ASG.search(l.strip())
        if not m: continue
        kind,nm,fld,idx,sub,val=m.groups()
        if kind=='quests': who='квеста «%s»'%esc(condru.QN.get(nm,nm)); link='<a href="quests.html?v=%d#q_%s">к странице квеста</a>'%(V,nm)
        else: who='заметки «%s»'%esc(MN.get(nm,nm)); link=''
        sv=re.match(r'"(.*)"\s*$',val)
        if fld=='_part_text' and not sub and sv:
            out.append('В дневнике %s в записи №%s появляется текст: «%s». %s'%(who,idx,esc(sv.group(1).replace('\\n',' ').strip()),link))
        elif fld=='_rtext' and sv is None:
            lm=re.match(r'\[\s*"([^"]+)"',val)
            if lm: out.append('В дневнике %s в списке задач пункт №%s: «%s». %s'%(who,idx,esc(lm.group(1)),link))
        elif fld=='_part_text' and sub:
            out.append('В дневнике %s запись №%s отмечается как открытая. %s'%(who,idx,link))
        elif fld=='_rtext' and sub:
            out.append('В дневнике %s пункт задач №%s отмечается выполненным. %s'%(who,idx,link))
    return out

LABL={}
for _fn,_ls in FILES.items():
    for _i,_l in enumerate(_ls):
        _m=re.match(r'label (\w+):',_l)
        if _m: LABL[_m.group(1)]=(_fn,_i)
def first_line(lab):
    if lab not in LABL: return None
    fn,i=LABL[lab]
    for l in FILES[fn][i+1:i+40]:
        m=re.match(r'^\s*(?:\w+\s+)?"(.{8,}?)"\s*$',l)
        if m and not l.strip().startswith('$'): return m.group(1)
    return None
def scene_effects(fn,ln):
    ls=FILES[fn];base=_ind(ls[ln-1]);out=[];say=[]
    for j in range(ln,min(ln+25,len(ls))):
        l=ls[j]
        if not l.strip(): continue
        if _ind(l)<=base: break
        t=l.strip()
        m=re.match(r'^(?:\w+\s+)?"(.+)"\s*$',t)
        if m and not t.startswith('$') and len(say)<2 and not re.match(r'^"[^"]*"\s*:',t): say.append(m.group(1)); continue
        m=re.match(r'^(?:\$ )?(?:renpy\.)?(jump|call)\s+(\w+)',t)
        if m:
            fl=first_line(m.group(2))
            out.append('переход в сцену'+(' со словами «%s»'%esc(fl[:70]) if fl else ' «%s»'%m.group(2)));continue
        m=re.search(r'quests\["(\w+)"\]\.(keep|done|false)\s*=\s*(\d)',t)
        if m:
            q=condru.QN.get(m.group(1),m.group(1));on=m.group(3)!='0'
            w={'keep':('Квест «%s» берётся','Квест «%s» снимается'),'done':('Квест «%s» засчитывается выполненным','Квест «%s» снимается как выполненный'),'false':('Квест «%s» считается проваленным','Квест «%s»: провал снимается')}[m.group(2)][0 if on else 1]
            out.append(w%esc(q))
    res=[]
    if say: res.append('дальше в сцене идут реплики: '+' / '.join('«%s»'%esc(x[:80]) for x in say))
    res+=out[:4]
    return res
def enclosing(fn,ln):
    ls=FILES[fn];cur=_ind(ls[ln-1]);res=[];prev=[]
    # earlier branches of the same if/elif chain
    j=ln-2
    c=ls[ln-1].strip()
    if c.startswith('elif'):
        while j>=0:
            l=ls[j]
            if l.strip() and _ind(l)==cur and re.match(r'(if|elif)\b',l.strip()):
                prev.append(l.strip()); 
                if l.strip().startswith('if'): break
            if l.strip() and _ind(l)<cur: break
            j-=1
    j=ln-2
    while j>=0 and cur>0:
        l=ls[j]
        if l.strip() and _ind(l)<cur:
            if re.match(r'(if|elif|while)\b.*:$',l.strip()): res.append(l.strip()[l.strip().index(' ')+1:-1]); 
            cur=_ind(l)
        j-=1
    return res,prev
CHK=collections.defaultdict(list)
NEED={k:needle(k) for k in SET}
COND=re.compile(r'^(?:\$ )?(?:if|elif|while)\s+(.*):$|^"[^"]*"\s*if\s+(.*):$')
for fn,ls in FILES.items():
    lab=None
    for i,l in enumerate(ls):
        m=re.match(r'label (\w+):',l)
        if m: lab=m.group(1)
        t=l.strip()
        m=COND.match(t)
        if not m: continue
        ce=m.group(1) or m.group(2)
        for k,nd in NEED.items():
            if nd and nd.search(ce): CHK[k].append((ce,lab,fn,i+1))
def group_of(k):
    if k.startswith('"') and ' in mem:' in k: return ('mem','Записи памяти дневника','Метки внутри записей дневника (vrem_memory / persistent.memory): открывают или закрывают пункты этих записей; для квестов они связаны со страницей квестов.',k.split(' in mem:')[1])
    m=re.fullmatch(r'"[^"]+" in ([\w\.]+)',k)
    if m:
        n=m.group(1)
        if n.endswith('.note'): return ('note','Заметки персонажей','Короткие записи в списке заметок персонажа (<code>.note</code>): что героиня о нём уже узнала.',n)
        return ('list','Метки пройденных реплик и осмотров','Строки в списках диалога (например <code>adro_dialog</code>): игра запоминает, какие темы и осмотры уже были.',n)
    if re.fullmatch(r'\w+\.d\d+',k): return ('dn','Числовые флаги разговоров (dN)','Флаги вида <code>td3.d2</code>: объект-набор флагов одного персонажа или сцены, номер - порядковый номер флага. Смысл в коде нигде не подписан - его можно только вывести из места, где флаг ставится.',k.split('.')[0])
    if re.fullmatch(r'\w+',k): return ('var','Простые переменные игры','Обычные переменные, которые игра выставляет в сцене и читает позже.',k)
    return ('other','Прочее','',k)
G=collections.OrderedDict()
for k in SET:
    gk,gt,gd,sub=group_of(k)
    G.setdefault((gk,gt,gd),collections.OrderedDict()).setdefault(sub,[]).append(k)
order=['mem','list','note','dn','var','other']
ORD=sorted(G,key=lambda x:order.index(x[0]))
def meaning(k):
    d=condru.derive(k)
    if not d: return None
    return d.split(' / ')[0]

def choice_of(k):
    mm=meaning(k)
    if mm:
        m=re.search(r'(?:выбран вариант|выбор\w* варианта) «(.*?)»',mm)
        if m: return m.group(1)
    return None

def guard_of(k):
    """Flag is 'shown once': every set site sits directly in an `if not <this flag>` block. Returns first spoken line of the first guarded block."""
    sets=SET.get(k,[])
    nd=NEED.get(k)
    if not sets or not nd: return None
    first=None
    for lab,fn,ln in sets:
        ls=FILES[fn];ind=_ind(ls[ln-1]);j=ln-2;ok=False
        while j>=0:
            l=ls[j]
            if l.strip() and _ind(l)<ind:
                t=l.strip()
                m=re.match(r'(?:\$ )?if\s+(.*):$',t)
                if m and nd.search(m.group(1)) and re.match(r'not\b',m.group(1).strip()) and ' and ' not in m.group(1) and ' or ' not in m.group(1): ok=True;gi=j
                break
            j-=1
        if not ok: return None
        if first is None:
            for l in ls[gi+1:gi+30]:
                m=re.match(r'^\s*(?:\w+\s+)?"(.{8,}?)"\s*$',l)
                if m and not l.strip().startswith('$'): first=m.group(1);break
    return first or ''
def short_key(k):
    c=choice_of(k)
    if c: return '«%s»'%c
    m=re.fullmatch(r'"([^"]+)" in mem:(\w+)',k)
    return 'метка «%s» (смысл в коде не назван)'%(m.group(1) if m else k)
MEMRE=re.compile(r'"(\w+)" (not )?in (?:vrem_memory|persistent\.memory)\["(\w+)"\]')
def plain_cond(ce,neg=False):
    """Russian game-meaning for a membership condition; None if not simple."""
    m=MEMRE.fullmatch(ce.strip())
    if not m: return None
    k='"%s" in mem:%s'%(m.group(1),m.group(3))
    notin=bool(m.group(2))^neg
    g=guard_of(k)
    if g is not None and not choice_of(k):
        return ('вступление сцены ещё не показывалось' if notin else 'вступление сцены уже показывалось')+((' («%s…»)'%g[:50]) if g else '')
    sk=short_key(k)
    return ('не выбрано ' if notin and choice_of(k) else 'не стоит ' if notin else 'выбрано ' if choice_of(k) else 'стоит ')+sk
def menu_question(fn,ln):
    ls=FILES[fn];j=ln-1
    ind=_ind(ls[j])
    while j>0:
        j-=1
        if ls[j].strip()=='menu:' and _ind(ls[j])<ind: break
        if ls[j].strip() and _ind(ls[j])<ind-8 and False: return None
    else: return None
    q=[]
    k=j-1
    while k>=0 and len(q)<2:
        t=ls[k].strip()
        m=re.match(r'^\w+\s+"(.*)"\s*$',t)
        if m: q.append(m.group(1))
        elif t and not t.startswith('$'): break
        k-=1
    return ' '.join(reversed(q)) if q else None
def row(k):
    sets=SET.get(k,[]);chk=CHK.get(k,[])
    mm=meaning(k)
    m=re.fullmatch(r'"([^"]+)" in (?:mem:)?([\w\.]+)',k)
    core=None
    if mm:
        core=condru._simp(mm)
        core=re.sub(r'^(?:Ставится: )?выбран вариант','Выбрано:',core)
    qn=None
    mq0=re.fullmatch(r'"[^"]+" in mem:(\w+)',k)
    if mq0 and mq0.group(1) in condru.QN: qn=condru.QN[mq0.group(1)]
    ch=choice_of(k)
    if ch: title=esc('«%s»'%ch)+(' <span class="muted">- вариант выбора в квесте «%s»</span>'%esc(qn) if qn else ' <span class="muted">- вариант выбора</span>')
    gd_=None if ch else guard_of(k)
    if gd_ is not None:
        title=esc('Вступление уже показывалось'+(': «%s…»'%gd_[:60] if gd_ else ''))+(' <span class="muted">- квест «%s»</span>'%esc(qn) if qn else '')
    else: title=esc((('«%s»: '%qn) if qn else '')+(core if core else 'смысл в коде не назван'))
    dtx=''
    for ce_,lab_,fn_,ln_ in chk:
        if fn_=='Diary_text.rpy':
            mt=re.search(r'появляется текст: «(.*?)»\.',' '.join(consequence(fn_,ln_)))
            if mt: dtx=mt.group(1);break
    if dtx: title+=' <span class="muted">→ в дневнике: «%s»</span>'%esc(dtx[:60]+('…' if len(dtx)>60 else ''))
    qline=None
    if ch and sets: qline=menu_question(sets[0][1],sets[0][2])
    short=m.group(1) if m else k
    h='<details class="fl"><summary><span class="ft">%s</span> <span class="muted"><code>%s</code></span> <span class="b">ставится: %d</span> <span class="b">проверок: %d</span></summary><div class="fb">'%(title,esc(k),len(sets),len(chk))
    if mm: h+='<p class="muted">Смысл выведен по месту, где метка ставится (в коде не подписан).</p>'
    mq=re.fullmatch(r'"[^"]+" in mem:(\w+)',k)
    if mq and mq.group(1) in condru.QN: h+='<p>Квест: <a href="quests.html?v=%d#q_%s">«%s»</a></p>'%(V,mq.group(1),esc(condru.QN[mq.group(1)]))
    if gd_ is not None: h+='<p class="muted">Метка ставится внутри блока «если её ещё нет», то есть нужна, чтобы эта сцена/вступление отыгрывалось один раз (по структуре кода; что ещё от неё зависит - в списке проверок).</p>'
    if qline: h+='<p>Вопрос в игре перед выбором: «%s»</p>'%esc(qline)
    if sets:
        h+='<h5>Где ставится</h5><ul>'
        for lab,fn,ln in sets[:8]:
            try: cx=condru.ctx(lab,fn,ln)
            except Exception: cx='в сцене «%s»'%lab
            h+='<li>%s <span class="muted"><code>%s:%d</code></span></li>'%(esc(condru._simp(cx)),fn,ln)
        if len(sets)>8: h+='<li class="muted">…и ещё %d</li>'%(len(sets)-8)
        h+='</ul>'
    if k in RESET: h+='<p>Где-то сбрасывается (есть присваивание «выключить»).</p>'
    if chk:
        h+='<h5>Где проверяется</h5><ul>'
        for ce,lab,fn,ln in chk[:8]:
            try: cx=condru.ctx(lab,fn,ln) if lab else 'в файле описания дневника'
            except Exception: cx='в сцене «%s»'%lab
            cons=consequence(fn,ln) if fn=='Diary_text.rpy' else []
            if cons:
                encl,prev=enclosing(fn,ln)
                parts=[]
                for e in encl:
                    parts.append(condru._simp(condru.cond_html(e).replace('<br/>',' ')) if False else re.sub('<[^>]+>','',condru.cond_html(e)).replace('\n',' ').strip())
                own=plain_cond(ce) or re.sub('<[^>]+>','',condru.cond_html(ce)).strip()
                parts.append(own)
                for p in reversed(prev):
                    pc=p.split(' ',1)[1].rstrip(':')
                    parts.append(plain_cond(pc,neg=True) or ('не выполнено: '+re.sub('<[^>]+>','',condru.cond_html(pc)).strip()))
                body='; '.join(x[0].lower()+x[1:] if x and x[0].isupper() and x[1:2].islower() else x for x in parts)
                h+='<li><b>Показывается, когда:</b> %s<br/>%s<br/><span class="muted">%s · <code>%s:%d</code> · <code>%s</code></span></li>'%(body,'<br/>'.join(c.replace('В дневнике','<b>Результат:</b> в дневнике') for c in cons),esc(cx),fn,ln,esc(ce[:110]))
            else:
                try: se=scene_effects(fn,ln)
                except Exception: se=[]
                eff=('<br/><b>Первые действия ветки (не все последствия):</b> '+'; '.join(se)) if se else ''
                h+='<li>%s%s<br/><span class="muted">%s · <code>%s:%d</code></span><br/><span class="muted"><code>%s</code></span></li>'%(condru.cond_html(ce).replace('<br/>',' '),eff,esc(cx),fn,ln,esc(ce[:110]))
        if len(chk)>8: h+='<li class="muted">…и ещё %d</li>'%(len(chk)-8)
        h+='</ul>'
    else: h+='<p class="muted">Проверок этой метки по коду не найдено (возможно, читается другим способом).</p>'
    return h+'</div></details>'
CSS='''<style>.fl{background:#fff;border:1px solid #d9dee8;border-radius:10px;padding:6px 12px;margin:6px 0}.fl>summary{cursor:pointer;display:flex;flex-wrap:wrap;gap:8px;align-items:baseline}.ft{font-weight:600}.b{font-size:12px;background:#ede9fe;color:#5b21b6;border-radius:10px;padding:1px 8px}.fb h5{margin:10px 0 3px;color:#374151}.fb ul{margin:4px 0 4px 20px}.fb code,.fl code{font-size:11px;color:#6b7280;word-break:break-all}.sg{margin:14px 0 4px;font-size:16px;color:#4338ca}.gtoc a{display:inline-block;margin:3px 8px 3px 0;padding:3px 12px;border:1px solid #d9dee8;border-radius:14px;background:#fff;text-decoration:none}</style>'''
def page():
    n=sum(len(v) for g in G.values() for v in g.values())
    h='<!DOCTYPE html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta http-equiv="Cache-Control" content="no-cache, must-revalidate"><title>Игровые метки</title><link rel="stylesheet" href="style7.css?v=%d">%s</head><body><header class="site"><div class="wrap"><h1>Игровые метки</h1><p>%d меток, которые игра ставит и потом проверяет. Сгруппированы по тому, как они устроены в коде. Смысл у большинства в коде не подписан: здесь он выведен по месту, где метка ставится, и помечен так.</p><nav class="crumbs"><a href="index.html?v=%d">← Все схемы</a> · <a href="quests.html?v=%d">Квесты</a></nav></div></header><main>'%(V,CSS,n,V,V)
    h+='<div class="card"><p class="gtoc">'+''.join('<a href="#g_%s">%s <span class="muted">(%d)</span></a>'%(gk,esc(gt),sum(len(v) for v in G[(gk,gt,gd)].values())) for gk,gt,gd in ORD)+'</p><p class="muted">Квесты (взят, выполнен, записи дневника) - отдельная страница, это другой механизм: объект <code>quests[…]</code>. Метки здесь - строки в списках и числовые флаги; не путать с метками переходов <code>label</code> в Ren\'Py.</p></div>'
    for gk,gt,gd in ORD:
        g=G[(gk,gt,gd)]
        h+='<div class="card" id="g_%s"><h2>%s</h2><p class="muted">%s</p>'%(gk,esc(gt),gd)
        for sub,keys in g.items():
            lab=sub
            if gk=='mem' and sub in condru.QN: lab='<a href="quests.html?v=%d#q_%s">%s</a> <span class="muted"><code>%s</code></span>'%(V,sub,esc(condru.QN[sub]),sub)
            else: lab='<code>%s</code>'%esc(sub)
            h+='<h3 class="sg">%s <span class="muted">(%d)</span></h3>'%(lab,len(keys))
            if gk=='dn' or len(keys)>6: h+='<details><summary class="muted">показать %d меток</summary>'%len(keys)+''.join(row(k) for k in keys)+'</details>'
            else: h+=''.join(row(k) for k in keys)
        h+='</div>'
    return h+'</main></body></html>'
open('/tmp/sch/flags.html','w',encoding='utf8').write(page())
ix=open('/tmp/sch/index.html',encoding='utf8').read()
if 'flags.html' not in ix:
    ix=ix.replace('<li><a href="quests.html','<li><a href="flags.html?v=%d">Игровые метки</a><br><span class="muted">какие метки есть, где ставятся и где проверяются, сгруппированы по устройству</span></li>\n<li><a href="quests.html'%V,1)
open('/tmp/sch/index.html','w',encoding='utf8').write(ix)
print(len(open('/tmp/sch/flags.html',encoding='utf8').read()))
