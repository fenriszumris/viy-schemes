# -*- coding: utf-8 -*-
import re,json,os
s=open('clickables.html',encoding='utf8').read()
st=json.load(open('clk_story.json',encoding='utf8'))
IMG={'bonny_1':'bonny_1','mant':'mant','barier_drag':'barier_drag','kremen':'kremen','hand_blood':'hand_blood','facel':'facel_image','cloath_v':'cloath'}
s=s.replace('<th>Что запускает</th>','<th>Что запускает</th><th>Простыми словами</th>') if '<th>Простыми словами</th>' not in s else s
s=re.sub(r'<td class="cs">.*?</td>','',s,flags=re.S)
s=re.sub(r'<img class="cimg"[^>]*>','',s)
def f(m):
    r=m.group(0); n=re.search(r'<td><code>([^<]+)</code>',r).group(1)
    if n in IMG and os.path.exists('img/clk/%s.png'%IMG[n]):
        r=r.replace('<td><code>','<td><img class="cimg" src="img/clk/%s.png" alt="%s" style="display:block;max-width:90px;max-height:90px;margin-bottom:4px"><code>'%(IMG[n],n),1)
    t=st.get(n)
    cell='<td class="cs">'+(t if t else '<span class="muted">Описание ещё не написано, ниже только код.</span>')+'</td>'
    return r[:-5]+cell+'</tr>'
s=re.sub(r'<tr><td>(?:<img[^>]*>)?<code>.*?</tr>',f,s,flags=re.S)
if '.stats code{' not in s: s=s.replace('</head>','<style>.stats code{font-size:11px;color:#6b7280}.stats td.cs{min-width:260px;font-size:14px}.stats td{font-size:12px}</style></head>',1)
open('clickables.html','w',encoding='utf8').write(s)
