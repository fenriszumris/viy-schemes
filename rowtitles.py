# -*- coding: utf-8 -*-
import re,json,html
st=json.load(open('clk_story.json',encoding='utf8'))
src=open('char_clicks.py',encoding='utf8').read()
g={};exec("import re\n"+src[src.find("CH={"):src.find("NOT=")],g)
CH=g['CH'];NAME=g['NAME']
s=open('clickables.html',encoding='utf8').read()
def title(o):
    if o in CH: return NAME[CH[o]]
    t=st.get(o,'')
    t=re.sub(r'<[^>]+>','',t.split(' (<code>')[0].split('. ')[0]).strip()
    t=re.sub(r'^Кнопка','Кнопка',t)
    return (t[:80]+'…') if len(t)>80 else (t or 'название не установлено из сцен')
def f(m):
    o=m.group(2);body=m.group(3)
    body=re.sub(r'<b class="rt">.*?</b><br>','',body)
    body=re.sub(r'^(<td[^>]*>)',r'\1<b class="rt">%s</b><br>'%html.escape(title(o)).replace('\\','\\\\'),body,count=1)
    return '<tr id="o_%s">%s</tr>'%(o,body)
s=re.sub(r'(<tr id="o_(\w+)">)(.*?)</tr>',f,s,flags=re.S)
open('clickables.html','w',encoding='utf8').write(s)
