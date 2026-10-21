# -*- coding: utf-8 -*-
import html
from PIL import Image,ImageDraw,ImageFont
F=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',30)
G='/tmp/viy/game/images/'
bg=Image.open(G+'bg/sar_cab.png').convert('RGBA')
H=[ # id, x,y, title, text
('diary',654,670,'Дневник Лиассона (тетрадь в кожаном переплёте)','sar_cab_diary','script_4_tgavan_adro.rpy:182',
 'Героиня читает записи с 10 по 19 октября 3853 года: влюблённость Лиассона, смерть старейшины Гарбока, приезд и гибель любимой, перехват сделки по яду Скорпикоры, ужин с братом. Запись обрывается на «Во всем винов…». Выборов нет. Если выполняется <code>logic_l()</code> (уровень логики; порог в этой проверке не расшифрован), добавляются реплики героини про череду смертей и про то, кого он обвиняет. В конце в список <code>adro_dialog</code> добавляется метка <code>diary_osm</code>; она открывает вопросы в разговоре с Адро.'),
('kamletter',757,684,'Пачка писем, перевязанных лентой','sar_cab_kamletter','script_4_tgavan_adro.rpy:125',
 'Любовные письма Лиассона и холодные ответы семьи Каэрнос. Показывается экран письма предмета «father_letter» (<code>_vrem_active = 1</code>). Выборов нет. Последнее письмо: Лиассон собирался покинуть семью. В <code>adro_dialog</code> добавляется <code>letter_kamletter</code>.'),
('letter',799,682,'Письмо Нарси Лиассону','sar_cab_letter','script_4_tgavan_adro.rpy:163',
 'Письмо вора Нарси о добытой партии яда (50 кило, 530 флаконов), с подписью Лиассона о получении от 19 октября 3853 года. Выборов нет. В <code>adro_dialog</code> добавляется <code>letter_osm</code>.'),
('paper',1062,672,'Бумаги на столе (счета и переписки)','sar_cab_paper','script_4_tgavan_adro.rpy:100',
 'Счета и деловые переписки с признаками контрабанды; среди них списки имён с пометками про заказные убийства (имя Нарси встречается чаще других; Лиассон заказывал убийство брата Адро) и более свежие черновики по легализации доходов. Включаются предметы «papers», «kill» и «lias_closed» (<code>_active</code>/<code>_acive_vrem</code>), показываются крупные картинки. Если выполняется <code>logic_l()</code>, добавляются две реплики героини про черновики. В <code>adro_dialog</code> добавляется <code>paper_osm</code>.'),
('tea1',392,695,'Чайник и кружка «От К.Р.»','sar_cab_tea1','script_4_tgavan_adro.rpy:279',
 'Остывший чайник и чистая кружка с надписью «От К.Р. С любовью. Вспоминай Солнце при каждом глотке». Выборов нет. В <code>adro_dialog</code> добавляется <code>tea1_osm</code>.'),
('tea',917,668,'Две чайные чашки','sar_cab_tea','script_4_tgavan_adro.rpy:290',
 'Две наполовину пустые чашки; от одной слабо пахнет приторно-сладким. Если <code>logic_l()&gt;1</code>, добавляется «от второй не пахло, обычный чай». Выборов нет. В <code>adro_dialog</code> добавляется <code>tea_osm</code>.'),
('potions',378,779,'Полка с зельями и ядом Скорпикоры','sar_cab_potions','script_4_tgavan_adro.rpy:257',
 'Героиня перечисляет флаконы (кленовый сироп, яд Скорпикоры, молоко виверны, земля Гавани). Выбор: «Осмотреть бутылочку Яда Скорпикоры» (гравировка «НМВ», флакон полный, крышка залита нетронутым сургучом; добавляется <code>poison_closed_osm</code>; при <code>logic_l()&gt;1</code> ещё реплика героини) или «Не нужно» (ничего не трогает). В любом случае добавляется <code>poison_osm</code>.'),
('pink',1453,679,'Полка с любовными романами','sar_cab_pink','script_4_tgavan_adro.rpy:212',
 'Выбор «Не трогать» / «Открыть». Если открыть: книга на певучем языке, который героиня может читать, наброски на полях, листок на последней странице. Второй выбор «Не трогать» / «Открыть»: если открыть, добавляется <code>toKP_letter</code> и читается письмо Лиассона Камилле (прощальное, «мы встретимся в следующей жизни»); при <code>logic_l()&gt;1</code> две реплики героини про яд и Камиллу. В конце добавляется <code>pink_osm</code>.'),
]
import os
out=['<h3>Осмотр кабинета (что можно осмотреть)</h3><p><b>Почему «кабинет Адро».</b> Так это место называет Кейт. В коде это кабинет Лиассона (убитого посла, брата Адро) в доме Сареброса. Связь с Адро по сценам: после подписания контракта Адро говорит «Осмотрите здесь все ... Каждая мелочь в этом кабинете была частью системы Лиассона» и уходит за дверь («Я буду за дверью», script_4_tgavan_begin_adro, script_4_tgavan_adro.rpy:1-39); дальше героиня осматривает комнату сама, а находки потом обсуждаются с Адро. В начальной сцене также описаны стеллажи с книгами, а при <code>logic_l()</code> - томик поэзии и плетёный брелок «К.Р.» (отдельных областей нажатия для них нет).</p><p>Это осмотр самого помещения, не действия над Адро. Восемь областей на экране кабинета (<code>sar_cab_screen</code>, script_newscreens.rpy:735): при наведении область подсвечивается, нажатие запускает сцену осмотра. Картинки взяты из ресурсов игры (<code>images/bg/sar_cab.png</code> и <code>images/sar_cab/*_hover.png</code>). Метки в списке <code>adro_dialog</code> потом открывают реплики в разговоре с <a href="char_adro.html">Адро</a>.</p>']
ov=bg.copy(); d=ImageDraw.Draw(ov)
for n,(i,x,y,t,lab,src,tx) in enumerate(H,1):
    pass
    hv=Image.open(G+'sar_cab/sar_cab_%s_hover.png'%i if i!='diary' else G+'sar_cab/sar_cab_diary_hover.png').convert('RGBA')
    ov.alpha_composite(hv,(x,y))
    d.rectangle([x-3,y-3,x+hv.width+3,y+hv.height+3],outline=(255,60,60,255),width=4)
    d.ellipse([x-18,y-44,x+22,y-4],fill=(255,60,60,255)); d.text((x+2,y-24),str(n),font=F,fill=(255,255,255,255),anchor='mm')
ov.convert('RGB').resize((1280,720)).save('img/sarcab/overview.jpg',quality=85)
out.append('<p><img src="img/sarcab/overview.jpg" style="max-width:100%;border-radius:6px" alt="Кабинет Сареброса, области осмотра"></p>')
for n,(i,x,y,t,lab,src,tx) in enumerate(H,1):
    y2=y
    hv=Image.open(G+'sar_cab/sar_cab_%s_hover.png'%i).convert('RGBA')
    pad=40
    box=(max(0,x-pad),max(0,y2-pad),min(1920,x+hv.width+pad),min(1080,y2+hv.height+pad))
    c=bg.crop(box); c.alpha_composite(hv,(x-box[0],y2-box[1]))
    c=c.convert('RGB'); c=c.resize((c.width*2,c.height*2))
    c.save('img/sarcab/%s.jpg'%i,quality=88)
    out.append('<div class="card" id="sc_%s" style="margin:8px 0"><img src="img/sarcab/%s.jpg" style="float:left;margin:0 12px 6px 0;max-width:240px;border-radius:6px" alt="%s"><b>%d. %s</b><br><span class="muted">метка <code>%s</code> (%s)</span><p>%s</p><div style="clear:both"></div></div>'%(i,i,html.escape(t),n,html.escape(t),lab,src,tx))
open('sarcab_block.html','w',encoding='utf8').write('\n'.join(out))
