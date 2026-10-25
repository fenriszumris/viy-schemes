# -*- coding: utf-8 -*-
# One-shot applier (repo style: apply_clk.py, enrich_inv.py): injects "Время" info into all pages.
# Grounding: static scan of /tmp/viy/game/*.rpy for real gametime effects:
#   my_location.name = X  -> +1 (setter at script.rpy:453)
#   change_day(_, N)      -> +N
#   gametime.gametime +/-= N (outside the engine setter)
# Engine lines excluded: script.rpy:453/537/545, live2d.rpy, screen-layer comparisons.
import re,glob,os,html,collections,sys

GAME=sys.argv[1] if len(sys.argv)>1 else '/tmp/viy/game'
effects=[]  # (file, line, label, delta, kind, detail)
for fn in sorted(glob.glob(GAME+'/*.rpy')):
    base=os.path.basename(fn)
    cur='(init)'
    for i,line in enumerate(open(fn,encoding='utf8',errors='ignore'),1):
        m=re.match(r'label ([\w.]+)',line)
        if m: cur=m.group(1)
        s=line.strip()
        if s.startswith('#'): continue
        if base=='script.rpy' and i in (453,537,545): continue  # the +1 engine itself
        m=re.search(r'my_location\.name\s*=(?![=])\s*(\w+)',s)
        if m:
            effects.append((base,i,cur,1,'move',m.group(1)))
            continue
        m=re.search(r'change_day\("(\w+)",\s*(\d+)\)',s)
        if m:
            effects.append((base,i,cur,int(m.group(2)),'change_day','день'))
            continue
        m=re.search(r'gametime\.gametime\s*([+-])=\s*(\d+)',s)
        if m and 'def ' not in s:
            d=int(m.group(2))*(1 if m.group(1)=='+' else -1)
            effects.append((base,i,cur,d,'direct',''))
            continue
        if re.search(r'gametime\.gametime\s*=\s*0\b',s):
            effects.append((base,i,cur,0,'reset','сброс'))

def eff_in(scope):  # scope: list of (file, lo, hi)
    out=[]
    for f,lo,hi in scope:
        for e in effects:
            if e[0]==f and lo<=e[1]<=hi: out.append(e)
    return sorted(out,key=lambda e:(e[0],e[1]))

BLOCK_RE=re.compile(r'<div class="timeblock".*?</div>\n?',re.S)

def block_html(effs,extra='',scoped=True):
    style='margin:8px 0 14px;padding:8px 12px;border:1px solid #d9dee8;border-radius:8px;background:#f8fafc;font-size:13px;color:#374151'
    head='⏱ <b>Время</b> (счётчик gametime, лимит 50 - <a href="time.html">механика и все сроки</a>): '
    if not scoped:
        body='у этой страницы нет отдельного сценарного учёта времени.'
    elif effs:
        items='; '.join(('=0 (сброс) - %s:%d (%s)'%(e[0],e[1],e[2])) if e[4]=='reset' else ('%+d - %s:%d (%s)'%(e[3],e[0],e[1],e[2])) for e in effs)
        note=' Точки относятся к разным действиям и веткам сцен - это не стоимость одного прохождения.' if len(effs)>1 else ''
        body='сценарные точки расхода в этой части кода: %s.%s'%(items,note)
    else:
        body='сценарных изменений в этой части кода <b>нет</b> (проверено поиском по всем .rpy).'
    tail=' Любое перемещение между локациями - по стрелке или по сценарию - стоит +1 (script.rpy:447-453).'
    if extra: tail+=' '+extra
    return '<div class="timeblock" style="%s">%s</div>\n'%(style,head+body+tail)

# ---- per-page scopes: file -> list of (file, lo, hi); parsed from intro or set manually
MANUAL={
 'airat1.html':[('script_4_airat.rpy',1,514)],
 'airat2.html':[('script_4_airat.rpy',515,1069)],
 'airat3.html':[('script_4_airat.rpy',1070,1481)],
 'airat4.html':[('script_4_airat.rpy',1482,1860)],
 'airat5.html':[('script_5_airat.rpy',1,9999)],
 'dev.html':[('script3_airat.rpy',1,9999)],
 'dev2.html':[('day_1_dev_razg.rpy',1,9999)],
 'tgavan.html':[('script3_tgavan_begin.rpy',1,9999)],
 'gar.html':[('script4_tgavan_gar.rpy',1,9999)],
 'less.html':[('script_2_less_conv.rpy',1,9999),('script_2_less_conv_amul.rpy',1,9999),('script_3_less_end.rpy',1,9999)],
 'tasha.html':[('script3_nazad.rpy',1,9999),('tash_game.rpy',1,9999),('day_1_tash_razg.rpy',1,9999)],
 'kapibar.html':[('script_4_kapibar.rpy',1,9999)],
 'nars.html':[('script_4_tgavan_nars.rpy',1,9999)],
 'sova.html':[('script3_sova.rpy',1,9999),('script_memory.rpy',1,9999)],
 'road.html':[('script3_road.rpy',1,9999)],
 'chaos.html':[('script3_gubert.rpy',1,9999),('script3_nazad.rpy',1,9999)],
 'gubert.html':[('script3_gubert.rpy',1,9999)],
 'bonny.html':[('script_npc_items.rpy',1500,1800)],
 'adrc.html':[('script3_tgavan_oh.rpy',1,9999)],
 'adro.html':[('script3_tgavan_oh.rpy',1,9999)],
 'adro2.html':[('script3_tgavan_oh.rpy',1,9999)],
 'sarcab_block.html':[('script_4_tgavan_adro.rpy',1,9999)],
 'gavan.html':[('script3_tgavan_oh.rpy',1,9999)],
 'start.html':[('script_1_less_begin.rpy',1,9999)],
 'location.html':[('script_1_less_begin.rpy',1,9999)],
}
GENERIC_EXTRA={
 'quests.html':'Сроки квестов проверяются в сеттере счётчика при каждом его изменении: «Нарси и Кап» - note_d["time"] = момент взятия + 20 (script_4_tgavan_nars.rpy:615), просрочка вызывает end_time_nar (script.rpy:676-678); девушка в Айрате уходит через 5 ед. после взятия (script.rpy:679-681, girl_air.lock = None).',
 'ends.html':'Срабатывания по времени живут в сеттере счётчика, а не в метках: end_time при gametime >= 50 (script.rpy:674-675; метка script_av.rpy:98) показывает «NORMAL END. Конец Демоверсии» и возвращает управление на карту (call_screen_strel), в ends_list не записывается; end_time_nar - не концовка, а сцена ухода Нарси при просрочке квеста (script.rpy:676-678; метка script_4_tgavan_nars.rpy:658), игра продолжается.',
 'paths.html':'Любая смена локации на путях ниже стоит +1 - и переход стрелкой, и смена места сценой (единый сеттер my_location.name, script.rpy:447-453). Сброс в 0 к началу управления: script_1_less_begin.rpy:75.',
 'flags.html':'Флагов, зависящих от счётчика времени напрямую, нет; время влияет через сроки квестов и end_time.',
 'diary.html':'В дневнике отметок времени нет; срок квеста «Нарси и Кап» хранится в заметке квеста (note_d["time"]).',
 'inventory.html':'Пазл Бонни: вход -1, отладочные кнопки пазла -1 (script_npc_items.rpy:1667-1679).',
 'locations.html':'Переход между любыми двум локациями стоит +1 (script.rpy:453); специальных цен у отдельных локаций нет.',
 'characters.html':'Разговоры сами по себе время не тратят; тратят переходы и перечисленные на странице «Время в игре» сцены.',
 'index.html':'Счётчик времени gametime (0-50) показан в статы-экране рядом с безумием и логикой (script_newscreens.rpy:669).',
 'stats.html':'Счётчик и его сроки: class_gametime с лимитом 50 (script _define.rpy:217, script.rpy:661-681); в игре время в строке «Безумие: ... Логика ... Время ...» (script_newscreens.rpy:669). Суммы на странице - по всем сценам сразу, без проверки совместимости веток (оговорка в тексте).',
 'strel.html':'Сам экран strel расхода не добавляет: +1 даёт смена локации через сеттер my_location.name (script.rpy:447-453), куда переходят и стрелки (script.rpy:537), и сценарные переходы.',
 'demo-limits.html':'Лимит демо: 50 единиц времени, затем end_time (script _define.rpy:217, script_av.rpy:98).',
}
ROUTE_COL={'route_gavan.html':{
    'Дверь Адриана':[('script3_tgavan_begin.rpy',1,9999)],
    'Тёмная Гавань: Адриан':[('script3_tgavan_oh.rpy',400,430)],
    'Адро: ворота, допрос, контракт':[('script3_tgavan_oh.rpy',690,730),('script3_tgavan_oh.rpy',1120,1240),('script_4_tgavan_adro.rpy',1,60)],
    'Адро: кабинет Лиассона':[('script_tgavan.rpy',1,9999)],
    'Адриан: разговор о деле':[],
 },
 'route_karralak.html':{
    'Айрат: коридор и Лени':[('script_4_airat.rpy',515,1069)],
    'Айрат: Карралак, лазарет, Феня':[('script_4_airat.rpy',1070,1481)],
    'Айрат: стража, кошка, статуя':[('script_5_airat.rpy',1,9999)],
 },
 'route_luiza.html':{
    'Луиза на дороге':[('script3_airat.rpy',1,9999)],
    'Луиза: разговоры по кнопке':[('day_1_dev_razg.rpy',1,9999)],
    'Айрат: вход, церковь, Миранда':[('script_4_airat.rpy',1,1481)],
    'Айрат: дом Луизы и концовки':[('script_4_airat.rpy',1482,1860)],
 },
 'route_nars.html':{
    'Нарси и бар':[('script_4_tgavan_nars.rpy',1,9999)],
 },
}

ROUTE_POINT_NOTE={}
def route_time_cell(effs):
    if not effs:
        return '<td>0 сценарно</td>'
    parts=[]
    for e in effs:
        d='%+d %s:%d'%(e[3],e[0],e[1])
        n=ROUTE_POINT_NOTE.get((e[0],e[1]))
        parts.append(d+(' - '+n if n else ''))
    return '<td>по точкам:<br/><span class="muted" style="font-size:11px">%s</span></td>'%('; '.join(parts))

def patch_route(fn,chunks):
    t=open(fn,encoding='utf8').read()
    t=BLOCK_RE.sub('',t)
    i=t.find('<table class="stats">')
    if i<0: return 'NO-TABLE'
    j=t.find('</table>',i)+len('</table>')
    tbl=t[i:j]
    # header: add Время after Сцена
    tbl2=tbl.replace('<th>Сцена</th>','<th>Сцена</th><th>Время</th>',1)
    rows=re.findall(r'(<tr>.*?</tr>)',tbl2,re.S)
    total=0
    body=''
    for r in rows[1:]:
        m=re.search(r'<td[^>]*>(.*?)</td>',r,re.S)
        name=re.sub(r'<[^>]+>','',m.group(1)).strip() if m else ''
        if name.startswith('Итого'):
            cell='<td>по выбранным веткам<br/><span class="muted" style="font-size:11px">суммы одного прохождения нет - см. условия точек выше; плюс +1 за каждое перемещение стрелкой</span></td>'
        else:
            effs=eff_in(chunks.get(name,[]))
            total+=sum(e[3] for e in effs)
            cell=route_time_cell(effs)
        k=r.find('</td>')+len('</td>')
        body+=r[:k]+cell+r[k:]
    tbl_new=tbl2[:tbl2.find('</tr>')+len('</tr>')]+body+'</table>'
    note='<p style="font-size:12px;color:#6b7280">Столбец «Время»: сценарные изменения счётчика gametime в сценах раздела - строка кода и условие; точки относятся к разным веткам, это не стоимость одного прохождения. Сюда не входят +1 за каждое перемещение стрелкой (script.rpy:453) и ночёвка у Капибара +5 (script_4_kapibar.rpy:227) - она вне этих маршрутов.</p>'
    t=t[:i]+tbl_new+'\n'+note+t[j:]
    return t

def patch_generic(fn):
    t=open(fn,encoding='utf8').read()
    t=BLOCK_RE.sub('',t)
    scope=MANUAL.get(fn)
    effs=eff_in(scope) if scope else []
    block=block_html(effs,GENERIC_EXTRA.get(fn,''),scoped=bool(scope))
    # insert after the nav paragraph containing "Все схемы", else after </h1>
    m=re.search(r'(<p[^>]*>(?:(?!</p>).)*?Все схемы(?:(?!</p>).)*?</p>)',t,re.S)
    if m:
        ins=m.end()
    else:
        m=re.search(r'</h1>',t)
        ins=m.end() if m else t.find('<body>')+6
    t=t[:ins]+'\n'+block+t[ins:]
    return t

CHAR_SPECIAL={
 'char_viy.html':'Вий присутствует во всех сценах игры; отдельного счётчика у героини нет - сценарный учёт времени ведётся по сценам (см. <a href="time.html">«Время в игре»</a> и блоки ⏱ на страницах сцен).',
 'char_kai.html':'Отдельных реплик и сцен с участием Кая в коде нет (проверено поиском kai / kai2d по всем .rpy); связанных с ним сценарных изменений времени нет.',
}
CHAR_DESC={
 'char_adrian.html':[('+1','script3_tgavan_begin.rpy',811,'script_3_tgavan_adr_potion_menu','сцена у двери после прояснения картинки: приём my_location.name = my_location.name - +1 без смены локации'),('+1','script3_tgavan_oh.rpy',421,'script_3_tgavan_airat_adr_menu2','выход из комнаты Адриана через дверь в Гавань')],
 'char_adro.html':[('+1','script_4_tgavan_adro.rpy',54,'script_4_tgavan_to_adro','выбор «Вернуться к вещам» в диалоге Адро')],
 'char_blu.html':[('+1','script_av.rpy',69,'blu_label','финал сцены с Блю - выгоняет в chaos_enter')],
 'char_bonny.html':[('-1 и +1 (итого 0)','script_npc_items.rpy',1686,'puzzle_complete','выход из пазла без полной сборки (<16 костей): компенсация -1 и переход +1, строки 1686-1688'),('+1','script_npc_items.rpy',1700,'puzzle_complete','завершение сцены с собранным пазлом - переход к Бонни')],
 'char_kap.html':[('+5','script_4_kapibar.rpy',227,'script4_kapibar_start_menu','ночёвка у Капибара - change_day("day",5)')],
 'char_narsi.html':[('+1','script_4_tgavan_nars.rpy',3,'bar_nar_label','первый заход к бару Нарси (ветка not "meet")'),('+1','script_4_tgavan_nars.rpy',29,'bar_nar_label','вход в бар с Нарси в той же первой сцене'),('+1','script_4_tgavan_nars.rpy',475,'script_4_tgavan_nars_bar_nar_igl_menu','выбор ухода из бара в меню')],
 'char_sluzhka.html':[('+1','script_4_airat.rpy',586,'airat_church_corridor_arrows_up_next_label','вход в церковный коридор, только если героиня ещё не там (условие if not)')],
 'char_tash.html':[('+1','script3_nazad.rpy',688,'script3_nazad_tash_2gone','сцена со слаймом - переход'),('+1','script3_nazad.rpy',1018,'script3_nazad_tash_urza','сцена с Урзой, первый из двух переходов подряд'),('+1','script3_nazad.rpy',1042,'script3_nazad_tash_urza','та же сцена с Урзой, второй переход')],
 'char_urza.html':[('+1','script3_nazad.rpy',1018,'script3_nazad_tash_urza','сцена с Таш, первый из двух переходов подряд'),('+1','script3_nazad.rpy',1042,'script3_nazad_tash_urza','та же сцена, второй переход')],
}

def patch_char(fn,entry):
    t=open(fn,encoding='utf8').read()
    t=BLOCK_RE.sub('',t)
    style='margin:8px 0 14px;padding:8px 12px;border:1px solid #d9dee8;border-radius:8px;background:#f8fafc;font-size:13px;color:#374151'
    head='⏱ <b>Время</b> (счётчик gametime, лимит 50 - <a href="time.html">механика и все сроки</a>): '
    tail=' Любое перемещение между локациями - по стрелке или по сценарию - стоит +1 (script.rpy:447-453).'
    if fn in CHAR_SPECIAL:
        body=CHAR_SPECIAL[fn]
    elif fn in CHAR_DESC:
        parts=['%s - %s:%d (%s): %s'%(v,f,ln,lab,d) for v,f,ln,lab,d in CHAR_DESC[fn]]
        body='точки расхода в сценах персонажа, каждая привязана к своему действию или условию (альтернативы не суммируются):<br>· '+('<br>· '.join(parts))+'.'
    elif entry and entry['eff']:
        parts=[]
        for lab,(f,effs) in entry['eff'].items():
            for val,ln in effs:
                parts.append('%s - %s:%s (%s)'%(val,f,ln,lab))
        body='сценарные точки расхода в сценах персонажа: %s. Точки относятся к разным действиям и веткам - это не стоимость одного прохождения.'%('; '.join(parts))
    elif entry and entry['labels']:
        body='сценарных изменений в сценах персонажа <b>нет</b> (проверено поиском по всем .rpy; метки: %s).'%(', '.join(entry['labels']))
    else:
        body='у этой страницы нет отдельного сценарного учёта времени.'
    block='<div class="timeblock" style="%s">%s</div>\n'%(style,head+body+tail)
    m=re.search(r'(<p[^>]*>(?:(?!</p>).)*?Все схемы(?:(?!</p>).)*?</p>)',t,re.S)
    ins=m.end() if m else t.find('<body>')+6
    return t[:ins]+'\n'+block+t[ins:]

if __name__=='__main__':
    print('effects total:',len(effects))
    import json as _json
    analysis=_json.load(open('char_time_analysis.json',encoding='utf8'))
    skip=set(ROUTE_COL)|{'time.html','todo.html'}
    for fn in sorted(glob.glob('*.html')):
        if fn in skip: continue
        if fn.startswith('char_') and (fn in analysis or fn in CHAR_SPECIAL):
            content=patch_char(fn,analysis.get(fn))
        else:
            content=patch_generic(fn)
        with open(fn,'w',encoding='utf8') as fh:
            fh.write(content)
    print('generic+char done (route pages untouched)')
