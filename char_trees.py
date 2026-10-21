# -*- coding: utf-8 -*-
import re,sys
sys.path.insert(0,'/tmp/sch')
import trees
V=276
T={'tash':('tash_razg_menu','tash','tash.near','кнопка-сообщение рядом с фигурой Таша (<code>tashir_button2</code>)'),
'fenrira':('fen_razg_menu','fenya','fenya.near','кнопка-сообщение (<code>fen_button2</code>)'),
'luiza':('dev_razg_menu','dev','dev.near','кнопка-сообщение (<code>dev_button2</code>); клик по самой фигуре открывает/закрывает экран <code>dev_screen</code>'),
'narsi':('nars_razg_menu','nars','nars.near','кнопка-сообщение (<code>nars_button2</code>)'),
'bonny':('bonny_razg_menu',None,None,None),
'less':('less_razg_menu',None,None,None),
'leni':('script_4_airat_leni_dialog',None,None,None),
'adro':('script_4_tgavan_to_adro',None,None,None),
'kap':('script4_kapibar_start_menu',None,None,None),
'sova':('script3_sova_sova',None,None,None)}
for sl,(lab,pers,near,btn) in T.items():
    f='char_%s.html'%sl
    try: s=open(f,encoding='utf8').read()
    except: print('no',f);continue
    fn,i,_=trees.body(lab)
    h='<!--TREE--><div class="card" id="tree"><h2>Дерево разговора</h2>'
    if pers:
        h+='<p class="muted">Когда персонаж идёт рядом с героиней (<code>%s</code>), у его фигуры справа есть %s: клик ведёт в меню разговора <code>%s</code> (%s:%d). Клик по фигуре переключает «идёт рядом» (знак <code>%s</code> умножается на −1).</p>'%(near,btn,lab,fn,i+1,near)
    else:
        h+='<p class="muted">Меню разговора <code>%s</code> (%s:%d).</p>'%(lab,fn,i+1)
    h+='<p class="muted">Показаны реплики, варианты ответа, условия и последствия (флаги, настроение, безумие) по коду. Вложенные ветки раскрываются; повторные переходы на уже показанные ветки не раскрываются, глубина ограничена тремя уровнями, глубже написано «метка», это явный пробел.</p>'
    h+=trees.render(lab,0,None,3)+'</div><!--/TREE-->'
    s=re.sub(r'<!--TREE-->.*?<!--/TREE-->','',s,flags=re.S)
    s=s.replace('</main>',h+'</main>',1)
    open(f,'w',encoding='utf8').write(s);print(sl,len(h))
