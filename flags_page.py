# -*- coding: utf-8 -*-
import re,glob,html,sys,collections
sys.path.insert(0,'/tmp/sch')
import condru
V=312
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
def row(k):
    sets=SET.get(k,[]);chk=CHK.get(k,[])
    mm=meaning(k)
    m=re.fullmatch(r'"([^"]+)" in (?:mem:)?([\w\.]+)',k)
    title=esc(mm and 'Ставится: '+condru._simp(mm) or 'Смысл в коде не подписан')
    short=m.group(1) if m else k
    h='<details class="fl"><summary><span class="ft">%s</span> <span class="muted"><code>%s</code></span> <span class="b">ставится: %d</span> <span class="b">проверок: %d</span></summary><div class="fb">'%(title,esc(k),len(sets),len(chk))
    if mm: h+='<p class="muted">Смысл выведен по месту, где метка ставится (в коде не подписан).</p>'
    mq=re.fullmatch(r'"[^"]+" in mem:(\w+)',k)
    if mq and mq.group(1) in condru.QN: h+='<p>Квест: <a href="quests.html?v=%d#q_%s">«%s»</a></p>'%(V,mq.group(1),esc(condru.QN[mq.group(1)]))
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
            h+='<li>%s<br/><span class="muted">%s · <code>%s:%d</code></span><br/><span class="muted"><code>%s</code></span></li>'%(condru.cond_html(ce).replace('<br/>',' '),esc(cx),fn,ln,esc(ce[:110]))
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
