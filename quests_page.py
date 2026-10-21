# -*- coding: utf-8 -*-
import re,glob,html,sys,collections
sys.path.insert(0,'/tmp/sch')
import condru,trees
V=310
QN=condru.QN
FILES={}
for f in sorted(glob.glob('/tmp/viy/game/*.rpy')):
    FILES[f.split('/')[-1]]=open(f,encoding='utf8',errors='ignore').read().split('\n')
def esc(x): return html.escape(x)
def cl(x): return re.sub(r'\{/?[a-z]+(=[^}]*)?\}','',x).replace('\\n',' ').strip()
def enclosing(fn,i):
    ls=FILES[fn]
    for j in range(i,-1,-1):
        m=re.match(r'label (\w+):',ls[j])
        if m: return m.group(1)
    return ''
PT=collections.defaultdict(dict);RT=collections.defaultdict(dict)
for (qq,i),t in condru.DT.items(): PT[qq][i]=t
_dt=open('/tmp/viy/game/Diary_text.rpy',encoding='utf8',errors='ignore').read()
for m in re.finditer(r'quests\["(\w+)"\]\.diary\._rtext\[([\d\.\-]+)\]\s*=\s*\["((?:[^"\\]|\\.)*)"',_dt,re.S): RT[m.group(1)][m.group(2)]=cl(m.group(3))
EV=collections.defaultdict(lambda: collections.defaultdict(list))
SKIPF={'Diary_text.rpy','script _define.rpy'}
for fn,ls in FILES.items():
    if fn in SKIPF: continue
    for i,l in enumerate(ls):
        t=l.strip()
        if t.startswith('#'): continue
        for q in set(re.findall(r'quests\["(\w+)"\]',t)):
            lab=enclosing(fn,i);where='%s:%d'%(fn,i+1)
            try: cx=condru.ctx(lab,fn,i+1)
            except Exception: cx='в сцене «%s»'%lab
            m=re.search(r'quests\["%s"\]\.(status)\s*=\s*"(\w+)"'%q,t) or re.search(r'quests\["%s"\]\.(keep|done|know|false)\s*=\s*(\w+)'%q,t)
            if m and t.startswith('$'):
                a,v=m.group(1),m.group(2)
                if a=='status': txt={'keep':'квест берётся','done':'квест выполнен','false':'квест провален'}.get(v,'статус квеста «%s»'%v)
                else: txt={'keep':{'1':'квест берётся','True':'квест берётся','0':'квест снимается (не взят)'},'done':{'1':'квест выполнен','True':'квест выполнен','0':'признак «выполнен» снят'},'know':{'1':'о квесте становится известно','True':'о квесте становится известно','0':'знание о квесте снято'},'false':{'1':'квест провален','True':'квест провален','0':'признак «провален» снят'}}[a].get(v,'%s = %s'%(a,v))
                EV[q]['set'].append((txt,cx,where));continue
            m=re.search(r'quests\["%s"\]\.diary\.u_part\(\s*([\d\.\-]+)\s*(?:,\s*(\w+))?'%q,t)
            if m:
                EV[q]['part'].append((m.group(1),m.group(2) or '1',cx,where));continue
            m=re.search(r'quests\["%s"\]\.diary\._rtext\[([\d\.\-]+)\]\[1\]\s*=\s*(\w+)'%q,t)
            if m and t.startswith('$'):
                EV[q]['rt'].append((m.group(1),m.group(2),cx,where));continue
            m=re.search(r'quests\["%s"\]\.diary\._part_text\[([\d\.\-]+)\]\[1\]\s*=\s*(\w+)'%q,t)
            if m and t.startswith('$'):
                EV[q]['part'].append((m.group(1),m.group(2),cx,where));continue
            m=re.match(r'(?:\$ )?(?:if|elif)\s+(.*):$',t) or re.match(r'"[^"]*"\s*if\s+(.*):$',t)
            if m and 'quests["%s"]'%q in m.group(1):
                EV[q]['chk'].append((m.group(1),cx,where));continue
            if t.startswith('$') and re.search(r'quests\["%s"\]\._note|note_d'%q,t):
                EV[q]['note'].append((t[1:].strip()[:80],cx,where));continue
            EV[q]['other'].append((t[:90],cx,where))
def link(txt):
    return txt
def li(x): return '<li>%s</li>'%x
def part_label(q,i):
    tx=PT[q].get(i)
    return '«%s»'%esc(tx[:110]+('…' if len(tx)>110 else '')) if tx else '<span class="muted">(текст записи в коде не найден)</span>'
def card(q):
    n=QN[q];e=EV[q]
    h='<details class="qc" id="q_%s"><summary><span class="qn">%s</span> <span class="muted"><code>%s</code></span>'%(q,esc(n),q)
    bs=[]
    if e['set']: bs.append('<span class="b">события: %d</span>'%len(e['set']))
    if e['part']: bs.append('<span class="b">записи дневника: %d</span>'%len(e['part']))
    if e['chk']: bs.append('<span class="b">проверок: %d</span>'%len(e['chk']))
    h+=' '+' '.join(bs)+'</summary><div class="qb">'
    if PT[q]:
        h+='<h4>Записи дневника (этапы)</h4><ul class="parts">'
        for i in sorted(PT[q],key=float): h+='<li><b>№%s</b> %s</li>'%(i,part_label(q,i))
        h+='</ul>'
    if RT[q]:
        h+='<h4>Пункты списка «Что сделать»</h4><ul>'+''.join('<li>%s <span class="muted">(пункт %s)</span></li>'%(esc(RT[q][i]),i) for i in sorted(RT[q],key=float))+'</ul>'
    if e['set']:
        h+='<h4>Когда меняется состояние квеста</h4><ul>'+''.join(li('<b>%s</b> - %s <span class="muted"><code>%s</code></span>'%(esc(t),esc(c),w)) for t,c,w in e['set'])+'</ul>'
    if e['part']:
        h+='<h4>Когда открывается запись дневника</h4><ul>'+''.join(li('запись <b>№%s</b> %s%s - %s <span class="muted"><code>%s</code></span>'%(i,part_label(q,i),'' if v in('1','True') else ' (значение %s)'%esc(v),esc(c),w)) for i,v,c,w in e['part'])+'</ul>'
    if e['rt']:
        h+='<h4>Пункты списка отмечаются</h4><ul>'+''.join(li('%s: %s - %s <span class="muted"><code>%s</code></span>'%(esc(RT[q].get(i,'пункт '+i)),'отмечен' if v in('1','True') else ('сбрасывается (значение None)' if v=='None' else 'значение '+esc(v)),esc(c),w)) for i,v,c,w in e['rt'])+'</ul>'
    if e['chk']:
        h+='<h4>Где квест проверяется (условия)</h4><ul>'+''.join(li('%s <span class="muted">%s · <code>%s</code></span><br/><span class="muted"><code>%s</code></span>'%(condru.cond_html(c).replace('<br/>',' '),esc(cx),w,esc(c[:110]))) for c,cx,w in e['chk'])+'</ul>'
    if e['note']:
        h+='<h4>Заметки квеста</h4><ul>'+''.join(li('<code>%s</code> - %s <span class="muted"><code>%s</code></span>'%(esc(t),esc(c),w)) for t,c,w in e['note'])+'</ul>'
    if e['other']:
        h+='<details><summary class="muted">Прочие обращения (%d)</summary><ul>'%len(e['other'])+''.join(li('<code>%s</code> <span class="muted">%s · %s</span>'%(esc(t),esc(c),w)) for t,c,w in e['other'][:30])+'</ul></details>'
    if not any(e[k] for k in e) and not PT[q]: h+='<p class="muted">В коде нет обращений к этому квесту, кроме определения.</p>'
    return h+'</div></details>'
CSS='''<style>.qc{background:#fff;border:1px solid #d9dee8;border-radius:12px;padding:10px 14px;margin:10px 0;box-shadow:0 1px 2px rgba(0,0,0,.04)}.qc>summary{cursor:pointer;font-size:17px;display:flex;flex-wrap:wrap;gap:8px;align-items:baseline}.qn{font-weight:700}.b{font-size:12px;background:#ede9fe;color:#5b21b6;border-radius:10px;padding:1px 8px}.qb h4{margin:14px 0 4px;color:#374151}.qb ul,.qb ol{margin:4px 0 4px 20px}.qb li{margin:4px 0}.parts li{list-style:none}.qc code{font-size:11px;color:#6b7280;word-break:break-all}.qhow{background:#f5f3ff;border-left:3px solid #7048E8;padding:10px 14px;border-radius:6px;margin:10px 0}.tocq a{display:inline-block;margin:3px 8px 3px 0;padding:2px 10px;border:1px solid #d9dee8;border-radius:14px;text-decoration:none;background:#fff}</style>'''
def page():
    order=list(QN)
    withtext=[q for q in order if PT[q]]
    bare=[q for q in order if not PT[q]]
    h='<!DOCTYPE html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta http-equiv="Cache-Control" content="no-cache, must-revalidate"><title>Квесты</title><link rel="stylesheet" href="style7.css?v=%d">%s</head><body><header class="site"><div class="wrap"><h1>Квесты</h1><p>%d квестов из <code>script _define.rpy</code>: название в игре, записи дневника, когда квест берётся, выполняется, где проверяется.</p><nav class="crumbs"><a href="index.html?v=%d">← Все схемы</a></nav></div></header><main>'%(V,CSS,len(order),V)
    h+='<div class="card"><div class="qhow"><b>Как читать вызов <code>quests["quest_statue"].diary.u_part(3, 1)</code></b><br/>Это команда «открыть запись №3 в дневнике этого квеста» (определение: <code>Diary_def.rpy:93-104</code>). Первый аргумент - номер записи в дневнике квеста, второй - значение (по умолчанию 1 = запись открыта). Игра запоминает значение у записи, показывает уведомление «Обновлена запись…» если квест уже взят и значение изменилось, а если у записи есть пункт списка «Что сделать» - отмечает его выполненным. Для квестов с постоянной памятью номер записи также сохраняется между прохождениями.</div>'
    h+='<p class="tocq">'+''.join('<a href="#q_%s">%s</a>'%(q,esc(QN[q])) for q in order)+'</p></div>'
    h+='<div class="card"><h2>Квесты с записями в дневнике (%d)</h2>'%len(withtext)+''.join(card(q) for q in withtext)+'</div>'
    h+='<div class="card"><h2>Остальные квесты - без текста в дневнике (%d)</h2><p class="muted">У них в коде не найдено текстов записей; ниже то, что к ним обращается.</p>'%len(bare)+''.join(card(q) for q in bare)+'</div>'
    h+='</main><script>if(location.hash){var e=document.querySelector(location.hash);if(e){e.open=true;e.scrollIntoView();}}</script></body></html>'
    return h
open('/tmp/sch/quests.html','w',encoding='utf8').write(page())
ix=open('/tmp/sch/index.html',encoding='utf8').read()
if 'quests.html' not in ix:
    ix=ix.replace('<li><a href="inventory.html','<li><a href="quests.html?v=%d">Квесты</a><br><span class="muted">названия в игре, записи дневника, где берутся, выполняются и проверяются</span></li>\n<li><a href="inventory.html'%V,1)
open('/tmp/sch/index.html','w',encoding='utf8').write(ix)
print({q:{k:len(v) for k,v in EV[q].items()} for q in QN})
