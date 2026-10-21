# -*- coding: utf-8 -*-
import re,sys
sys.path.insert(0,'/tmp/sch')
import trees
import tree_graph
import json
V=283
TGJS='<style>.widechart svg{max-width:none !important}</style><script type="module">import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs";mermaid.initialize({startOnLoad:false,securityLevel:"loose",maxTextSize:900000,maxEdges:5000,flowchart:{htmlLabels:true,curve:"basis",useMaxWidth:false,nodeSpacing:26,rankSpacing:44,diagramPadding:14},theme:"default",themeVariables:{fontSize:"16px"}});const f=document.getElementById("tgchart");f.textContent=document.getElementById("tgsrc").textContent.split("<\\/").join("</");await mermaid.run({nodes:[f]});const sv=f.querySelector("svg");let z=1;function ap(){f.style.zoom=z;}window.tgz=function(k){if(k==="fit"){z=Math.min(1,(f.parentNode.clientWidth-20)/sv.getBoundingClientRect().width*z)}else if(k==="100"){z=1}else{z=Math.max(0.1,Math.min(2,z*k))}ap();};tgz("fit");if(z<0.5){z=0.5;ap();}</script>'
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
    src,nn=tree_graph.graph(lab,'Начало разговора')
    h+='<p><b>Схема разговора.</b> Узлы: голубые - реплики и последствия (🚩 - что записывается, код мелко), жёлтые - выбор игрока, фиолетовые - проверка условия (на стрелках условие по-русски, код мелко серым), серые - начало ветки, красный пунктир - пробел (ветка глубже трёх уровней или метка не найдена). Прокручивается вправо и вниз.</p><p><button onclick="tgz(0.7)">Меньше</button> <button onclick="tgz(1.4)">Больше</button> <button onclick="tgz(\'fit\')">Вписать в ширину</button> <button onclick="tgz(\'100\')">100%</button></p><div class="widechart" style="overflow:auto;max-height:900px"><div id="tgchart" class="mermaid"></div></div><script type="text/plain" id="tgsrc">'+src.replace('</','<\\/')+'</script>'
    h+=TGJS
    h+='<details><summary><b>Те же реплики подряд текстом</b> (полный текст)</summary>'+trees.render(lab,0,None,3)+'</details></div><!--/TREE-->'
    s=re.sub(r'<!--TREE-->.*?<!--/TREE-->','',s,flags=re.S)
    s=s.replace('</main>',h+'</main>',1)
    open(f,'w',encoding='utf8').write(s);print(sl,len(h))
