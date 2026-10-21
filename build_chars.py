# -*- coding: utf-8 -*-
# Собирает char_<slug>.html из replics.html (группы реплик) и live2d.rpy (pers). Запуск: python3 build_chars.py /путь/к/viy_demo/game
import re,sys,os,html
G=sys.argv[1]
rep=open('replics.html',encoding='utf8').read()
groups=[]
parts=re.split(r'(?=<details class="card"><summary><b>)',rep)[1:]
for p in parts:
    m=re.match(r'<details class="card"><summary><b>(.*?)</b> - (\d+) реплик',p)
    body=p[p.index('</summary>')+10:]
    body=body[:body.rfind('</details>')] if '</details>' in body else body
    groups.append((m.group(1),int(m.group(2)),body))
live=open(os.path.join(G,'live2d.rpy'),encoding='utf8').read()
pers={}
for m in re.finditer(r'^\s*\$ ([a-z_0-9]+) = pers\((.*)\)\s*$',live,re.M):
    a=m.group(2)
    d={k:v for k,v in re.findall(r'(\w+)\s*=\s*("[^"]*"|[-\w.]+)',a)}
    pers[m.group(1)]={k:v.strip('"') for k,v in d.items()}
# slug, заголовок, группы реплик, переменная pers, примечание
C=[
('less','Лесс',[0,1],'less',''),
('tash','Ташир Аргейто',[2],'tash','Подписи в коде: «???» и «Парень в белом»; полное имя в pers: Ташир Аргейто.'),
('luiza','Луиза',[3],'dev','В коде переменная dev, подпись «Девочка?».'),
('adrian','Адриан',[4],'oh','Подпись «Страж?»; в pers: namee «Страж», r_name «Адриан».'),
('slime','Слизень',[5],None,''),
('fenrira','Фенрира',[6],'fenya','Подпись в коде «Оборотница».'),
('narsi','Нарси',[7],'nars','Подпись в коде «Парень».'),
('sluzhka','Служка',[8],None,''),
('zhrec','«Жрец?»',[9],None,''),
('bonny','Бонни',[10],'bonny',''),
('cat_statue','Статуя кошки',[11],None,''),
('kap','Мистер Кап (Капибара)',[12],'kap',''),
('adro','Адро Сареброс',[13,14,15],'adro','Подпись «Эльф»; группы реплик: Эльф (sadr), e1 и Эльфийка (e2) - какие из e1/e2 тот же персонаж, из кода не видно, поэтому они приведены отдельно внизу.'),
('starichok','Старичок',[16],None,'Character g1.'),
('parenek','Паренёк',[17],None,'Character g2.'),
('devushka_airat','Девушка в Айрате',[18],'girl_air','Character d_air; в pers: «Девочка в айрате».'),
('chelovek_v_chernom','Человек в чёрном',[19],None,'Character priest.'),
('sova','Сова',[20],'sova',''),
('urza','Урза',[],'urza','Отдельных реплик с подписью в коде не найдено.'),
('karralak','Карралак Ар',[],'kar','Отдельных реплик с подписью в коде не найдено.'),
('kai','Кай',[],'kai','Отдельных реплик с подписью в коде не найдено.'),
('blu','Блу',[],'blu','Отдельных реплик с подписью в коде не найдено.'),
('viy','Вий (героиня)',[],'viy','Реплики героини (v, vm, vvv) в сводку реплик не входят.'),
('leni','Лени',[],'leni','В pers задано только место (lock); имя и подпись в коде не заданы.'),
]
def count(var,files):
    r={}
    for f in files:
        t=open(os.path.join(G,f),encoding='utf8',errors='ignore').read()
        n=len(re.findall(r'\b'+var+r'\.',t))
        if n: r[f]=n
    return r
files=[f for f in os.listdir(G) if f.endswith('.rpy')]
CSS='<style>.k{font-size:11px;color:#6b7280}.pf td,.pf th{padding:4px 8px;text-align:left;vertical-align:top}.pf code{font-size:11px;color:#6b7280}</style>'
def page(slug,title,gi,var,note):
    p=pers.get(var,{}) if var else {}
    h=['<!DOCTYPE html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta http-equiv="Cache-Control" content="no-cache, must-revalidate"><title>%s</title><link rel="stylesheet" href="style7.css?v=22">%s</head><body>'%(html.escape(title),CSS)]
    h.append('<header class="site"><div class="wrap"><h1>%s</h1><p>Всё на странице взято из кода viy_demo. Чего в коде нет, помечено прочерком или словами «не задано».</p><nav class="crumbs"><a href="characters.html?v=233">← Все персонажи</a> · <a href="index.html?v=232">Все схемы</a></nav></div></header><main>'%html.escape(title))
    h.append('<div class="card"><h2>Кто это</h2>')
    if note: h.append('<p>%s</p>'%html.escape(note))
    if p:
        rows=[('Как называют сначала (namee)',p.get('namee')),('Если узнали частично (izn_name)',p.get('izn_name')),('Настоящее имя (r_name)',p.get('r_name')),('Как зовёт героиню (nv)',p.get('nv')),('Где стоит (lock)',p.get('lock')),('Порог «хорошее отношение» / «плохое»',('%s / %s'%(p.get('v_good','10 (по умолчанию)'),p.get('n_bad','-4 (по умолчанию)'))))]
        h.append('<table class="pf">')
        for k,v in rows: h.append('<tr><th>%s</th><td>%s</td></tr>'%(k,html.escape(v) if v else '-'))
        h.append('</table>')
        h.append('<p class="k">Определение: переменная <code>%s</code>, live2d.rpy. Статичной картинки персонажа для этой страницы не подобрано (в папке проекта у многих персонажей только модели Live2D).</p>'%var)
        talk={'less':'day_1_less_razg.rpy','tash':'day_1_tash_razg.rpy','dev':'day_1_dev_razg.rpy','nars':'day_1_nars_razg.rpy','fenya':'day_1_fen_razg.rpy','bonny':'day_1_bonny_razg.rpy'}
        if var in talk: h.append('<p><b>Меню «разговоры»:</b> <code>%s</code></p>'%talk[var])
        nd=re.search(r'\b%s = pers\([^\n]*need_drop = (\{[^}]*\})'%var,live)
        if nd: h.append('<p><b>Можно отдать предмет</b> (перетащить из инвентаря): <span class="k">%s</span>. Предметы: <a href="inventory.html?v=232">Инвентарь</a>.</p>'%html.escape(nd.group(1)))
        c=count(var,files)
        if c:
            h.append('<p><b>Где в коде используется переменная</b> <code>%s</code> (обращений к полям): '%var+', '.join('<code>%s</code> %d'%(f,n) for f,n in sorted(c.items(),key=lambda x:-x[1])[:12])+'</p>')
    else:
        h.append('<p class="k">В списке pers (live2d.rpy) для этого персонажа записи нет, только подпись говорящего в коде.</p>')
    h.append('</div>')
    if gi:
        h.append('<div class="card"><h2>Реплики</h2><p class="muted">Строки взяты из сводки реплик, подпись в коде указана в названии группы. Развернуть группу, чтобы прочитать.</p>')
        for i in gi:
            t,n,b=groups[i]
            h.append('<details><summary><b>%s</b> - %d реплик</summary>%s</details>'%(t,n,b))
        h.append('</div>')
    h.append('</main></body></html>')
    open('char_%s.html'%slug,'w',encoding='utf8').write(''.join(h))
for s in C: page(*s)
# блок со ссылками для characters.html
V=sys.argv[2] if len(sys.argv)>2 else '233'
block='<div class="card" id="char-pages"><h2>Страницы персонажей</h2><ul>'+''.join('<li><a href="char_%s.html?v=%s">%s</a>%s</li>'%(s,V,html.escape(t),(' <span class="muted">(%d реплик)</span>'%sum(groups[i][1] for i in gi) if gi else ' <span class="muted">(реплик с подписью нет)</span>')) for s,t,gi,v,n in C)+'</ul></div>'
c=open('characters.html',encoding='utf8').read()
c=re.sub(r'<div class="card" id="char-pages">.*?</ul></div>','',c,flags=re.S)
c=c.replace('<main>','<main>'+block,1)
open('characters.html','w',encoding='utf8').write(c)
print(len(C),'pages')
