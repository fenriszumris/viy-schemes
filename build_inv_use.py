# -*- coding: utf-8 -*-
import re,json
V=273
src=open('char_clicks.py',encoding='utf8').read()
pre=src[:src.find('# inventory link')]
g={}
exec("import re,json,html\nV=%d\n"%V+pre[pre.find("CH={"):],g)
DROP=g['DROP'];NAME=g['NAME'];CH=g['CH']
use=json.load(open('item_use.json',encoding='utf8'))
slug={'kap':'kap','tash':'tash','nars':'narsi','adro':'adro','guard1':'starichok','guard2':'parenek','bonny':'bonny'}
OBJ={'cloath_v':('дерево, к которому героиня прислоняет ткань (объект <code>cloath_v</code>)','script_npc_items.rpy'),'cap_ch':('чайник (объект <code>cap_ch</code>)',''),'gub_osm':('объект <code>gub_osm</code> в сцене Губерта','')}
EXTRA={('diary','igla'):'Капля с иглы попадает на дневник, его край обугливается. Героиня: «Похоже, это действительно не шутки».',('igla','diary'):'Капля с иглы попадает на дневник, его край обугливается. Героиня: «Похоже, это действительно не шутки».',
('kremen','facel'):'Героиня понимает, что так можно зажечь факел. Выбор: «Позже» (ничего не происходит) или «Конечно!» (предмет «факел» заменяется на горящий факел).',
('facel','kremen'):'Героиня понимает, что так можно зажечь факел. Выбор: «Позже» (ничего не происходит) или «Конечно!» (предмет «факел» заменяется на горящий факел).',
('cloath','cloath_v'):'Героиня сомневается, зачем перевязывать дерево, но «это возможно». Выбор: «Перевязать» (ткань убирается из активных предметов, в заметки предмета записывается «bint», настроение Лесса +2) или «Нахрен надо» (ткань остаётся у неё).',
('cap','cap_ch'):'Героиня набирает ещё кружечку чая: предмет «чай» становится активным, кружка (cap) перестаёт быть активной; страж говорит «Приятного!».',
('kremen','gub_osm'):'Переход на ветку <code>gub_osm_facel_fire</code>.',
('facel_fire','gub_osm'):'Героиня пытается поджечь объект: «Пшшш…», настроение Лесса −2, «Эта штука не горит, совсем».'}
NOTE='ветка не разобрана: известно только условие (предмет брошен на этот объект)'
def il(i): return '<a href="#i_%s">%s</a>'%(i,i)
s=open('inventory.html',encoding='utf8').read()
s=re.sub(r'<p><b>Можно отдать[^<]*</b></p>\s*<ul>.*?</ul>','',s,flags=re.S)
INV={}
for m in re.finditer(r'<summary>(?:<img[^>]*>)?<span><b>(.*?)</b><br><span class="rid">(\w+) ·',s,re.S): INV[m.group(2)]=m.group(1).replace('\\&quot;','&quot;')
def tgt(t):
    if t in INV: return '<a href="#i_%s">%s</a>'%(t,INV[t]),'предмет'
    if t in slug: return '<a href="char_%s.html?v=%d#clk">%s</a>'%(slug[t],V,NAME[slug[t]]),'персонаж'
    if t in OBJ: return '<a href="clickables.html?v=%d#o_%s">%s</a>'%(V,t,OBJ[t][0]),'объект'
    return '<code>%s</code>'%t,'объект'
def block(it):
    rows=use.get(it,[])
    if it=='amul': rows=rows+[['kap','kap_amul','script_inv_text.rpy',9]]
    if not rows: return ''
    h='<!--USE--><div class="use"><b>Куда можно перетащить этот предмет</b><ul>'
    for t,lab,f,n in rows:
        text=None
        for it2,loc,tx in DROP.get(slug.get(t,t),[]):
            if it2==it: text=tx
        for k in (it,t):
            pass
        text=text or EXTRA.get((it,t)) or NOTE
        # tash/nars name mapping for DROP keys
        nm,kind=tgt(t)
        h+='<li>%s <span class="muted">(%s)</span>: %s <span class="muted"><code>%s</code>, %s:%s</span></li>'%(nm,kind,text,lab,f,n)
    return h+'</ul></div><!--/USE-->'
def f(m):
    it=m.group(2);body=re.sub(r'<!--USE-->.*?<!--/USE-->','',m.group(3),flags=re.S)
    return m.group(1)+body+block(it)+'</details>'
s=re.sub(r'(<details class="inv" id="i_(\w+)">)(.*?)</details>',f,s,flags=re.S)
open('inventory.html','w',encoding='utf8').write(s);print(s.count('<!--USE-->'))
