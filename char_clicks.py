# -*- coding: utf-8 -*-
import re,json,html
exec(open('loc_names.py',encoding='utf8').read())
V=317
st=json.load(open('clk_story.json',encoding='utf8'))
CH={'tash':'tash','bonny':'bonny','sova':'sova','leni':'leni','nars':'narsi','guard1':'starichok','guard2':'parenek','kap':'kap','cat':'cat_statue','girl_air':'devushka_airat','dev_button':'luiza','dev_sleep':'luiza','adro_screen':'adro','blu':'blu','fen_button':'fenrira'}
REL={'karralak':['kar_air'],'tash':['tash_cards','mant','bonny_1'],'bonny':['b_head','bonny_x','b_find','head','full_bones'],'luiza':['dev_door','dev_door2'],'kap':['cap_ch']}
NAME={'tash':'Ташир (Таш)','bonny':'Бонни','sova':'Сова','leni':'Лени','narsi':'Нарси','starichok':'Горран (старший страж)','parenek':'Алекс (страж)','kap':'Капибара','cat_statue':'Статуя кошки','devushka_airat':'Девушка в церкви Айрата','luiza':'Луиза','adro':'Адро','blu':'Блю','fenrira':'Фенрира'}
NOT='ветка не разобрана: известно только условие запуска (предмет брошен на этот объект)'
DROP={
'tash':[('diary','script_inv.rpy:18','Таш: «Я не читаю чужие вещи!». Если он знает, что «Вий» это её псевдоним (<code>tash.zn_vpotpam</code>, квест viy_quest, часть 5), вспоминает это; иначе: «С каких пор ты носишь дневник?».'),
('table_chaos','script_inv.rpy:1','Таш не знает, что это за табличка; если героиня на входе в хаос (<code>chaos_enter</code>), он гадает, не хочет ли Урза гостей. «Демо-демо-демо… без понятия».'),
('bonny_1','script3_nazad.rpy:1907','Ветка <code>bonny_1_tash</code> (с меню <code>bonny_1_tash_menu</code>), описана в строке объекта <a href="clickables.html?v=%d#o_bonny_1">bonny_1</a>.'%V),
('tash_card','script3_nazad.rpy:1838','Ветка <code>tash_tash_card</code>; описание предмета в инвентаре.')],
'bonny':[('bones_strange','script_npc_items.rpy:1909','Героиня показывает «штучку из твоих костей»; Бонни долго разглядывает, потом говорит «Ну, это кость», а на вопрос героини ссылается на отсутствие магического анализа и «не знаю» и прячется (ничего не раскрывает).'),
('bonny_x','script_npc_items.rpy:1877','Если в заметках квеста нет «no_all»: кость положена на место, Бонни шипит и ругается, что кости растащили и перемешали, а чтобы встать, ей нужно собрать их по порядку; героиня возмущена («зачем я в этом копалась?»). Остальные ветки (есть «no_all») не разобраны.'),
('b_head','script_npc_items.rpy:1844','«А это случаем не твоё тело?»: если ещё нет заметки «make1», Бонни жалуется на мешанину и валяющийся череп, просит упорядочить кости; если нет «this», героиня ворчит про гниль и записывается «this», дневник <code>u_part(3,1)</code>. Остальные ветки не разобраны.')],
'kap':[('diary','script_4_kapibar.rpy:886','Капибара: «Что это?», признаётся, что не умеет читать («Я не умею читать»), героиня извиняется; возврат на экран переходов.'),
('hat','script_4_kapibar.rpy:713','Если у квеста «quest_kap» нет метки keep, героиня показывает шляпу; Капибара узнаёт цилиндр, подарок мамы, просит вернуть, платить ему нечем кроме благодарности. Выбор: «Нет...» (он расстраивается, шляпа остаётся) или «Хорошо» (<code>sanity.moral</code> +1, <code>quest_kap.done = 1</code>, он обнимает и даёт 3 «kapik»; шляпа из инвентаря убирается).'),
('kap_sliv','script_4_kapibar.rpy:826','Капибара узнаёт сливочную капибару: «Отличная штука!». Выбор: «Да! Большое спасибо!» (просто благодарность, он отвечает «Всегда пожалуйста!») или «А может быть вы сами выпьете?»; остальное в ветке этой записью не разобрано.'),
('kapik','script_4_kapibar.rpy:864','«Капик?»: героиня спрашивает, почему он продаёт за эту валюту; Капибара вспоминает детство и волшебный магазин, где всё продавалось за деньги, и что ему помогает один человек, обещавший помочь открыть такое место. Продолжение не разобрано.'),
('money','script_4_kapibar.rpy:459','Героиня вводит сумму (<code>renpy.input</code>). Не число: «Что я только что ему предложила?» и ввод заново. 0: «Я передумала», возврат в меню. Если больше, чем есть денег (<code>money</code>): отдельная реплика, остальное не разобрано.'),
('amul','script_inv_text.rpy (need_drop)','Метка <code>kap_amul</code> по условию предмета; ветка не разобрана.')],
'narsi':[('diary','script_4_tgavan_nars.rpy:483','Нарси: «Записываешь?», шутит про весточки; если в квесте «nars_quest» дневниковая запись [0][1] равна 1, спрашивает, не принесла ли она его как что-то интересное, с выбором ответа. Ветка не дочитана.'),
('hat','script_4_tgavan_nars.rpy:537','«Кажется, я видел такой на ком-то»: он вспоминает странного маленького пушистого паренька из Айрата, шутит про «потискал»; если в «nars_quest» дневниковая запись [0][1] равна 1, есть продолжение, не разобрано.'),
('igla','script_4_tgavan_nars.rpy:788',NOT),
('kapik','script_4_tgavan_nars.rpy:582','«Это не золото, не мифрил, даже не медь… это медведь? Или капибара?»; героиня на вопрос «откуда?» выбирает ответ «Из Кап и Бара»; если у «nars_kap» нет keep, есть продолжение, не разобрано.'),
('table_chaos','script_4_tgavan_nars.rpy:674','Нарси восхищён, что ему принесли табличку («Ты гений!»), осматривает: «от неё Хаосом разит… и ещё чем-то странным»; хочется достать артефакторский набор, но лень. Продолжение не разобрано.')],
'adro':[('adr_zn','script3_tgavan_oh.rpy:1610','Героиня показывает знак Адриана; Адро не впечатлён, настроение −1, говорит, что занимается только официальными делами, а посетителям нужно записываться.'),
('kill','script3_tgavan_oh.rpy:1627','В первый раз (флаг «kill» в <code>adro_d</code>) героиня показывает план убийства; он ностальгически улыбается («Лиассон всё-таки решился обратиться к профессионалу… к самому Нарси»). Остальное не разобрано.'),
('wg_zn','script3_tgavan_oh.rpy:1557','Если часть 6 квеста <code>invest_quest</code> выполнена: «он запомнил моё лицо». Если часть 1 не выполнена и квест активен, она показывает знак и говорит, что помогает Белой страже; Адро: «Стража сочла разумным делегировать новичка… своё слово я сдержу».')],
'starichok':[('propusk','script_5_airat.rpy:399','Героиня отдаёт пропуск; стражи шутят про возраст «старика», пославшего её; старший страж забирает пропуск и разрешает пройти: «только осторожнее».')],
'parenek':[('propusk','script_5_airat.rpy:390','Героиня говорит, что у неё пропуск; Алекс отвечает, что она перепутала, нужен другому стражу, а тот (старший) говорит: «Я проверю».'),
('diary','script_npc_items.rpy:1047','Заглушка: в коде только реплика «123», затем экран переходов.')]}
# inventory link
def il(i): return '<a href="inventory.html?v=%d#i_%s">%s</a>'%(V,i,INV.get(i,i))
INV={}
inv=open('inventory.html',encoding='utf8').read()
for m in re.finditer(r'<summary>(?:<img[^>]*>)?<span><b>(.*?)</b><br><span class="rid">(\w+) ·',inv,re.S): INV[m.group(2)]=m.group(1).replace('\\&quot;','&quot;')
ck=open('clickables.html',encoding='utf8').read()
ck_orig=open('clk_rows_orig.txt',encoding='utf8').read()
def rowcell(o):
    m=re.search(r'<tr id="o_%s">(.*?)</tr>'%o,ck_orig,re.S)
    return m.group(1) if m else ''
blocks={}
for o,sl in CH.items():
    row=rowcell(o)
    tds=re.findall(r'<td[^>]*>(.*?)</td>',row,re.S)
    where=re.sub(r'\s*\(:\d+\)','',tds[2]) if len(tds)>2 else ''
    act=tds[3] if len(tds)>3 else ''
    story=st.get(o,'')
    b='<h3>Объект <code>%s</code></h3><p class="muted">Где показывается: %s</p>'%(o,where)
    if act and not act.startswith('Это персонаж'): b+='<p class="muted">Что запускает: %s</p>'%act
    if story: b+='<p>%s</p>'%story
    blocks.setdefault(sl,[]).append(b)
def sect(sl):
    h='<!--CLK--><div class="card" id="clk"><h2>Где на него можно нажать</h2>'+(''.join(blocks.get(sl,[])) or '<p>Отдельного кликабельного объекта самого персонажа в экранах не найдено. Связана дверь в коридоре церкви: по клику «Постучаться» сцена переходит к нему, если Лени стоит в его комнате (условие <code>leni.lock</code>); подробности в строке двери.</p>')
    rel=[o for k,v in REL.items() if k==sl or (sl=='bonny' and k=='bonny') for o in v] if sl in REL else []
    if sl=='tash': rel=REL['tash']
    if sl=='luiza': rel=REL['luiza']
    if rel: h+='<p class="muted">Связанные объекты (не сам персонаж): '+', '.join('<a href="clickables.html?v=%d#o_%s"><code>%s</code></a>'%(V,o,o) for o in rel)+'</p>'
    h+='</div><div class="card"><h2>Что на него можно положить</h2>'
    d=DROP.get(sl)
    if d:
        h+='<p class="muted">Если перетащить предмет X на этот объект, игра переходит на метку «объект_X» или «X_объект» (или заданную предметом).</p><ul>'
        for i,loc,t in d:
            h+='<li><b>%s</b> <span class="muted"><code>%s</code></span><br>%s</li>'%(il(i),loc,t)
        h+='</ul>'
    else: h+='<p class="muted">Для этого объекта подходящих меток «предмет на объект» в коде не найдено.</p>'
    return h+'</div><!--/CLK-->'
for sl in sorted(set(CH.values())|{'karralak'}):
    f='char_%s.html'%sl
    s=open(f,encoding='utf8').read()
    s=re.sub(r'<!--CLK-->.*?<!--/CLK-->','',s,flags=re.S)
    s=s.replace('</main>',sect(sl)+'</main>',1)
    open(f,'w',encoding='utf8').write(s)
# clickables rows -> link
def repl(m):
    o=m.group(2);sl=CH[o]
    cells=re.findall(r'<td[^>]*>.*?</td>',m.group(3),re.S)
    link='Это персонаж: <a href="char_%s.html?v=%d#clk">%s</a>. Где на него нажать и что на него можно положить, на его странице.'%(sl,V,NAME[sl])
    return '<tr id="o_%s">%s%s%s<td class="cs">%s</td></tr>'%(o,cells[0],cells[1],cells[2],link)
ck2=re.sub(r'(<tr id="o_(%s)">((?:(?!</tr>).)*)</tr>)'%'|'.join(CH),repl,ck,flags=re.S)
open('clickables.html','w',encoding='utf8').write(ck2)
