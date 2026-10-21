# -*- coding: utf-8 -*-
import json,html
import hub_tree
JS='''<style>.widechart{overflow-x:auto}.widechart svg{max-width:none !important}.hubbtn{font-size:13px;padding:3px 10px;border-radius:8px;border:1px solid #c6ccd6;background:#fff;cursor:pointer;margin-right:6px}</style>
<script type="module">
import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
mermaid.initialize({startOnLoad:false,securityLevel:'loose',flowchart:{htmlLabels:true,curve:'basis',useMaxWidth:false,nodeSpacing:26,rankSpacing:44,diagramPadding:14},theme:'default',themeVariables:{fontSize:'16px'}});
const D=JSON.parse(document.getElementById('hubdata').textContent);
const EXP=new Set(D.open);
function hubnode(id){const h=D.hubs[id];const a=EXP.has(id)?'▾':'▸';
 return id+'["<div style=\\'width:200px;white-space:normal;text-align:center;padding:6px 8px\\'><b>Выбор игрока '+a+'</b><br/><small>вариантов: '+h.n+'</small><br/><small style=\\'color:#6b7280\\'>'+h.opts.map(function(x){return '«'+x+'»';}).join(', ')+(h.n>2?', …':'')+'</small></div>"]:::hub';}
function build(){
 const L=['flowchart TB'];const shown=new Set();const q=[];
 L.push('START(["Начало разговора"]):::an');
 D.start.forEach(function(l){L.push(l);});
 D.startTargets.forEach(function(t){q.push(t);});
 const seen=new Set();
 while(q.length){const id=q.shift();if(seen.has(id))continue;seen.add(id);L.push(hubnode(id));
  if(EXP.has(id)){const h=D.hubs[id];h.exp.forEach(function(l){L.push(l);});h.targets.forEach(function(t){q.push(t);});}}
 [['hub','fill:#fef3c7,stroke:#b45309,stroke-width:2px,color:#0f172a'],['op','fill:#fffbeb,stroke:#d97706,color:#0f172a'],['cd','fill:#ede9fe,stroke:#7c3aed,color:#0f172a'],['ex','fill:#e5e7eb,stroke:#6b7280,color:#374151'],['an','fill:#dcfce7,stroke:#15803d,color:#0f172a'],['jn','fill:#fff,stroke:#9ca3af']].forEach(function(c){L.push('classDef '+c[0]+' '+c[1]);});
 return L.join('\\n');}
let FIRST=true;
async function render(){
 const f=document.getElementById('hubchart');const wc=f.parentElement;const keep=wc.scrollLeft;f.removeAttribute('data-processed');f.textContent=build();
 await mermaid.run({nodes:[f]});
 for(const ss of document.styleSheets){let r;try{r=ss.cssRules;}catch(e){continue;}
  for(let i=r.length-1;i>=0;i--){const x=r[i];if(x.selectorText&&/\\.(hub|op|cd|ex|an|jn)( span| > \\*)$/.test(x.selectorText)&&x.style&&x.style.getPropertyPriority('color')==='important')x.style.removeProperty('color');}}
 document.querySelectorAll('#hubchart g.node').forEach(function(g){const m=/^flowchart-(H\\d+)-\\d+$/.exec(g.id||'');
  if(m){g.style.cursor='pointer';g.addEventListener('click',function(){if(EXP.has(m[1]))EXP.delete(m[1]);else EXP.add(m[1]);render();});}});
 if(FIRST){FIRST=false;const st=[...document.querySelectorAll('#hubchart g.node')].filter(function(g){return /^flowchart-START-/.test(g.id);})[0];
  if(st){const a=st.getBoundingClientRect(),b=wc.getBoundingClientRect();wc.scrollLeft=Math.max(0,wc.scrollLeft+(a.left+a.width/2)-(b.left+b.width/2));}}else{wc.scrollLeft=keep;}}
window.hubAll=function(on){EXP.clear();if(on)Object.keys(D.hubs).forEach(function(h){EXP.add(h);});render();};
render();
</script>'''
def block(lab,owner,openhubs='first'):
    d=hub_tree.build(lab,owner)
    st=[]
    import re
    for l in d['start']:
        pass
    # start targets: hubs referenced from start lines
    tg=[]
    for l in d['start']:
        m=re.search(r'--> (H\d+)$',l)
        if m and m.group(1) not in tg: tg.append(m.group(1))
    allh=list(d['hubs'])
    openl=tg[:1] if openhubs=='first' else (allh if openhubs=='all' else [])
    data={'start':d['start'],'startTargets':tg,'hubs':d['hubs'],'open':openl}
    h='<p class="muted">Схема только мест выбора. Нажмите на жёлтый блок «Выбор игрока», чтобы раскрыть его варианты на месте; повторное нажатие сворачивает. Фиолетовые скруглённые блоки - условия. Значки: <span style="color:#e41a1c;font-weight:700">настроение</span> · <span style="color:#7048e8;font-weight:700">безумие</span> · <span style="color:#1c7ed6;font-weight:700">логика</span>; плюсы вверху справа карточки, минусы внизу слева. Оранжевый мелкий текст - что запоминается. Реплик здесь нет.</p>'
    h+='<p><button class="hubbtn" onclick="hubAll(true)">Развернуть все</button><button class="hubbtn" onclick="hubAll(false)">Свернуть все</button></p>'
    h+='<div class="widechart"><div id="hubchart" class="mermaid"></div></div>'
    h+='<script type="application/json" id="hubdata">'+json.dumps(data,ensure_ascii=False).replace('</','<\\/')+'</script>'+JS
    leg=''.join('<li><code>%s</code>: %s</li>'%(html.escape(k),html.escape(v)) for k,v in d['leg'].items())
    if leg: h+='<details><summary><b>Откуда берутся метки этой схемы</b></summary><ul>'+leg+'</ul></details>'
    return h
