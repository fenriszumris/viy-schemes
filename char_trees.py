# -*- coding: utf-8 -*-
import re,sys
sys.path.insert(0,'/tmp/sch')
import trees
import html
import tree_graph
import json
V=294
TGJS='<style>.widechart svg{max-width:none !important}.widechart .mermaid:not([data-processed]){width:auto!important;height:60px;overflow:hidden!important;font-size:0!important;color:transparent}.widechart .mermaid:not([data-processed])::before{content:"Схема загружается…";font-size:14px;color:#6b7280}.widechart .mermaid{overflow:visible!important;width:max-content!important;min-width:0!important}.tgb{border-top:1px solid #e5e7eb;margin-top:10px;padding-top:6px}</style><script type="module">import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs";mermaid.initialize({startOnLoad:false,securityLevel:"loose",maxTextSize:900000,maxEdges:5000,flowchart:{htmlLabels:true,curve:"basis",useMaxWidth:false,nodeSpacing:24,rankSpacing:40,diagramPadding:10},theme:"default",themeVariables:{fontSize:"16px"}});const B=JSON.parse(document.getElementById("tgdata").textContent);let z=1;const els=[];function go(i){const f=els[i];if(f.dataset.done)return f._p;f.dataset.done=1;f._p=mermaid.run({nodes:[f]}).then(function(){f.style.zoom=z;const n0=f.querySelector("g.node.sc")||f.querySelector("g.node"),pp=f.parentNode;if(n0){const b=pp.getBoundingClientRect(),a=n0.getBoundingClientRect();pp.scrollLeft+=a.left+a.width/2-(b.left+b.width/2);}const R=B[i].rets;for(const k in R){if(!R[k])continue;const g=f.querySelector("g.node[id^=flowchart-"+k+"-]");if(!g)continue;g.style.cursor="pointer";g.addEventListener("click",function(){Promise.all(els.map(function(_,j){return go(j);})).then(function(){const t=document.getElementById("tgb_"+R[k]);if(t){t.scrollIntoView({block:"start",behavior:"smooth"});t.style.background="#fef9c3";setTimeout(function(){t.style.background="";},2500);}});});}});}const io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){go(+e.target.dataset.i);io.unobserve(e.target);}});},{rootMargin:"600px"});for(let i=0;i<B.length;i++){const f=document.getElementById("tgc"+i);f.textContent=document.getElementById("tgs"+i).textContent.split("<\\\\/").join("</");f.dataset.i=i;els.push(f);io.observe(f);}window.tgz=function(k){if(k==="100")z=1;else z=Math.max(0.2,Math.min(2,z*k));els.forEach(function(f){f.style.zoom=z;});};window.tgGo=go;</script>'
T={'tash':('tash_razg_menu','tash','tash.near','кнопка-сообщение рядом с фигурой Таша (<code>tashir_button2</code>)'),
'fenrira':('fen_razg_menu','fenya','fenya.near','кнопка-сообщение (<code>fen_button2</code>)'),
'luiza':('dev_razg_menu','dev','dev.near','кнопка-сообщение (<code>dev_button2</code>); клик по самой фигуре открывает/закрывает экран <code>dev_screen</code>'),
'narsi':('nars_razg_menu','nars','nars.near','кнопка-сообщение (<code>nars_button2</code>)'),
'bonny':('bonny_razg_menu',None,None,None),
'less':('less_razg_menu',None,None,None),
'leni':('script_4_airat_leni_dialog',None,None,None),
'adro':('script_4_tgavan_to_adro',None,None,None),
'kap':('script4_kapibar_start_menu',None,None,None),
'sova':('script3_sova_sova',None,None,None),
'blu':('blu_label',None,None,None),
'slime':('script3_nazad_slime_menu',None,None,None),
'starichok':('script_5_airat_guard',None,None,None),
'parenek':('script_5_airat_guard',None,None,None)}
for sl,(lab,pers,near,btn) in T.items():
    f='char_%s.html'%sl
    try: s=open(f,encoding='utf8').read()
    except: print('no',f);continue
    fn,i,_=trees.body(lab)
    h='<!--TREE--><div class="card" id="tree"><h2>Дерево разговора</h2>'
    if pers:
        h+='<p class="muted">Когда персонаж идёт рядом с героиней (<code>%s</code>), у его фигуры справа есть %s: клик ведёт в меню разговора <code>%s</code> (%s:%d). Клик по фигуре переключает «идёт рядом» (знак <code>%s</code> умножается на −1).</p>'%(near,btn,lab,fn,i+1,near)
    else:
        h+='<p class="muted">Меню разговора <code>%s</code> (%s:%d).%s</p>'%(lab,fn,i+1,' Это одна общая сцена для двух стражников: Горрана (старший, реплики g1) и Алекса (младший, реплики g2); реплики каждого подписаны своим именем.' if sl in ('starichok','parenek') else '')
    h+='<p class="muted">Показаны реплики, варианты ответа, условия и последствия (флаги, настроение, безумие) по коду. Вложенные ветки раскрываются; повторные переходы на уже показанные ветки не раскрываются, глубина ограничена тремя уровнями, глубже написано «метка», это явный пробел. Условия двух видов: расшифрованные (понятное русское условие; чтение кода) и нерасшифрованные: у флагов указано только, где они ставятся и сбрасываются, а смысл в коде не назван, его я не придумываю; «проверка в коде (смысл не расшифрован)» значит, что выражение пока не разобрано.</p>'
    br=tree_graph.graph(lab,'Начало разговора')
    h+='<p><b>Схема разговора.</b> Узлы: зелёные - начало ветки, голубые - реплики и что записывается (🚩, код мелко), жёлтые - выбор игрока, фиолетовые скруглённые блоки - проверка условия (условие по-русски, каждое требование с новой строки через «и одновременно» / «или», код мелко серым; на стрелках «да»/«нет»; откуда берутся флаги и метки - в раскрывающемся списке под схемой), оранжевые «→ Ветка» - переход в другую ветку (нажмите: прокрутит к её схеме ниже), красный пунктир - пробел (ветка глубже трёх уровней или метка не найдена). Каждая ветка нарисована отдельной схемой, поэтому они небольшие.</p><p><button onclick="tgz(0.8)">Меньше</button> <button onclick="tgz(1.25)">Больше</button> <button onclick="tgz(\'100\')">100%</button></p>'
    data=[]
    for n,(l,ttl,src,rets,leg) in enumerate(br):
        data.append({'rets':rets})
        h+='<div class="tgb" id="tgb_%s"><b>%s</b><div class="widechart" style="overflow:auto"><div id="tgc%d" class="mermaid"></div></div><script type="text/plain" id="tgs%d">%s</script>%s</div>'%(l,('Начало разговора: ' if n==0 else '')+ttl,n,n,src.replace('</','<\\/'),('<details><summary>Откуда берутся флаги и метки этой схемы</summary><ul>'+''.join('<li><code>%s</code>: %s</li>'%(html.escape(k),html.escape(v)) for k,v in leg.items())+'</ul></details>') if leg else '')
    h+='<script type="application/json" id="tgdata">'+json.dumps(data)+'</script>'+TGJS
    h+='<details><summary><b>Те же реплики подряд текстом</b> (полный текст)</summary>'+trees.render(lab,0,None,3)+'</details></div><!--/TREE-->'
    s=re.sub(r'<!--TREE-->.*?<!--/TREE-->','',s,flags=re.S)
    s=s.replace('</main>',h+'</main>',1)
    open(f,'w',encoding='utf8').write(s);print(sl,len(h))
