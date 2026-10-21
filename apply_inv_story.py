# -*- coding: utf-8 -*-
import re,json
s=open('inventory.html',encoding='utf8').read()
st=json.load(open('inv_story.json',encoding='utf8'))
s=re.sub(r' <span class="why">.*?</span>','',s)
s=re.sub(r'<p class="story">.*?</p>','',s)
s=re.sub(r'<p class="nostory[^"]*">.*?</p>','',s)
def f(m):
    b=m.group(0); n=re.search(r'class="rid">([^ <]+)',b).group(1)
    if n in st: p='<p class="story"><b>Простыми словами:</b> '+st[n]+'</p>'
    else: p='<p class="nostory muted">Связное описание этого предмета по сценам ещё не написано; ниже только места в коде.</p>'
    i=b.index('<p><b>Что это:</b>') if '<p><b>Что это:</b>' in b else b.index('</summary>')+10
    return b[:i]+p+b[i:]
s=re.sub(r'<details class="inv">.*?</details>',f,s,flags=re.S)
if '.story{' not in s: s=s.replace('</head>','<style>.story{background:#f5f3ff;border-left:3px solid #7048E8;padding:8px 12px;border-radius:6px}</style></head>',1)
open('inventory.html','w',encoding='utf8').write(s)
