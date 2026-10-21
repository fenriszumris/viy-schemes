# -*- coding: utf-8 -*-
import re,html
exec(open('loc_names.py',encoding='utf8').read())
V=312
DIR={'left':'налево','right':'направо','up':'вперёд (вверх)','bottom':'назад (вниз)'}
edges={}
for l in open('/tmp/locgraph.txt',encoding='utf8'):
    m=re.match(r'EDGE (\w+) (\w+) -> (\w+) (.*?)\s*script\S* ?(\S*)$',l.rstrip())
    if not m: continue
    s,d,t,rest,_=m.groups()
    if s not in L or t not in L: continue
    q=re.findall(r'"([^"]*)"',rest)
    cap=[x for x in q if x and not re.fullmatch(r'[a-z_0-9]+',x)]
    cap=re.sub(r'\{[^}]*\}','',cap[0]).replace('\\n',' ') if cap else ''
    k=(s,d,t,cap)
    edges.setdefault(s,[])
    if k not in edges[s]: edges[s].append(k)
# clickables rows
ck=open('clickables.html',encoding='utf8').read()
objs={}
def addid(m):
    return m.group(0)
rows=re.findall(r'<tr[^>]*>(.*?)</tr>',ck,re.S)
for r in rows:
    tds=re.findall(r'<td[^>]*>(.*?)</td>',r,re.S)
    if len(tds)<3: continue
    mo=re.search(r'<code>(\w+)</code>',tds[0])
    if not mo: continue
    for lid in re.findall(r'(\w+) \(:\d+\)',re.sub('<[^>]+>','',tds[2])):
        objs.setdefault(lid,[]).append(mo.group(1))
def nm(i): return L[i][0]
out=[]
for i,(ru,src,pages) in L.items():
    c='<div class="card" id="%s"><h2>%s</h2><p class="muted">Откуда название: %s. Код: <code>%s</code></p>'%(i,html.escape(ru),html.escape(src),i)
    es=edges.get(i,[])
    if es:
        c+='<h3>Переходы отсюда</h3><ul>'
        for s,d,t,cap in es:
            c+='<li>%s: <a href="#%s">%s</a>%s</li>'%(DIR[d],t,html.escape(nm(t)),(' (подпись стрелки «%s»)'%html.escape(cap)) if cap else '')
        c+='</ul>'
    inc=[(s,d,cap) for s,es2 in edges.items() for (s,d,t,cap) in es2 if t==i]
    if inc:
        c+='<h3>Сюда ведут</h3><ul>'+''.join('<li><a href="#%s">%s</a> (%s)</li>'%(s,html.escape(nm(s)),DIR[d]) for s,d,cap in inc)+'</ul>'
    if i in objs:
        c+='<h3>Кликабельные объекты на этой локации</h3><p>'+', '.join('<a href="clickables.html?v=%d#o_%s"><code>%s</code></a>'%(V,o,o) for o in dict.fromkeys(objs[i]))+'</p>'
    if pages:
        c+='<h3>Сцены</h3><ul>'+''.join('<li><a href="%s?v=%d">%s</a></li>'%(p,V,html.escape(cap)) for p,cap in pages)+'</ul>'
    if not es and not inc: c+='<p class="muted">Переходов в коде не найдено (в графе локация не используется).</p>'
    if i=='tgavan_alh': c+='<p class="muted">Эта локация объявлена, но в игре нигде не используется.</p>'
    if i=='tgavan_sar_cab': c+=open('sarcab_block.html',encoding='utf8').read()
    out.append(c+'</div>')
page='''<!DOCTYPE html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Локации</title>
<link rel="stylesheet" href="style7.css?v=%d"><style>code{font-size:11px;color:#6b7280}h3{font-size:14px;margin:10px 0 4px}</style></head><body>
<header class="site"><div class="wrap"><h1>Локации</h1><p>Места игры и переходы между ними. Русские названия взяты из подписей стрелок и реплик сцен; откуда именно, указано в каждой карточке. Где название не установлено из сцен, это оговорено.</p>
<nav class="crumbs"><a href="index.html?v=%d">← Все схемы</a> · <a href="strel.html?v=%d">Экран переходов</a> · <a href="clickables.html?v=%d">Кликабельные</a></nav></div></header><main>%s</main></body></html>'''%(V,V,V,V,'\n'.join(out))
open('locations.html','w',encoding='utf8').write(page)
print(len(out),sum(len(v) for v in edges.values()),len(objs))
