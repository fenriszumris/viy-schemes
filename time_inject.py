# -*- coding: utf-8 -*-
# One-shot applier (repo style: apply_clk.py, enrich_inv.py): injects "Время" info into all pages.
# Grounding: static scan of /tmp/viy/game/*.rpy for real gametime effects:
#   my_location.name = X  -> +1 (setter at script.rpy:453)
#   change_day(_, N)      -> +N
#   gametime.gametime +/-= N (outside the engine setter)
# Engine lines excluded: script.rpy:453/537/545, live2d.rpy, screen-layer comparisons.
import re,glob,os,html,collections,sys

GAME='/tmp/viy/game'
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
        tot=sum(e[3] for e in effs)
        items='; '.join('%+d - %s:%d (%s)'%(e[3],e[0],e[1],e[2]) for e in effs)
        body='сценарно в этой части кода: <b>%+d</b> - %s.'%(tot,items)
    else:
        body='сценарных изменений в этой части кода <b>нет</b> (проверено поиском по всем .rpy).'
    tail=' Каждый переход стрелкой даёт ещё +1 сверху (script.rpy:453).'
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
 'quests.html':'Сроки квестов: «Нарси и Кап» - 20 ед. с момента взятия (script_4_tgavan_nars.rpy:615), девушка в Айрате уходит через 5 ед. (script.rpy:680).',
 'ends.html':'Концовка по времени: end_time при достижении 50 (script_av.rpy:98), end_time_nar при просрочке квеста «Нарси и Кап» (script_4_tgavan_nars.rpy:658).',
 'paths.html':'Каждый переход стрелкой на путях ниже стоит +1; смена места сценой внутри пути тоже +1.',
 'flags.html':'Флагов, зависящих от счётчика времени напрямую, нет; время влияет через сроки квестов и end_time.',
 'diary.html':'В дневнике отметок времени нет; срок квеста «Нарси и Кап» хранится в заметке квеста (note_d["time"]).',
 'inventory.html':'Пазл Бонни: вход -1, отладочные кнопки пазла -1 (script_npc_items.rpy:1667-1679).',
 'locations.html':'Переход между любыми двум локациями стоит +1 (script.rpy:453); специальных цен у отдельных локаций нет.',
 'characters.html':'Разговоры сами по себе время не тратят; тратят переходы и перечисленные на странице «Время в игре» сцены.',
 'index.html':'Счётчик времени gametime (0-50) показан в статы-экране рядом с безумием и логикой (script_newscreens.rpy:669).',
 'stats.html':'Время показано в игре в строке «Безумие: ... Логика ... Время ...» (script_newscreens.rpy:669).',
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

def route_time_cell(effs):
    if not effs:
        return '<td>0 сценарно</td>'
    tot=sum(e[3] for e in effs)
    small='; '.join('%+d %s:%d'%(e[3],e[0],e[1]) for e in effs)
    return '<td><b>%+d</b> сценарно<br/><span class="muted" style="font-size:11px">%s</span></td>'%(tot,small)

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
            cell='<td><b>%+d</b> сценарно<br/><span class="muted" style="font-size:11px">плюс +1 за каждый переход стрелкой</span></td>'%total
        else:
            effs=eff_in(chunks.get(name,[]))
            total+=sum(e[3] for e in effs)
            cell=route_time_cell(effs)
        k=r.find('</td>')+len('</td>')
        body+=r[:k]+cell+r[k:]
    tbl_new=tbl2[:tbl2.find('</tr>')+len('</tr>')]+body+'</table>'
    note='<p style="font-size:12px;color:#6b7280">Столбец «Время»: сценарные изменения счётчика gametime в сценах раздела (каждая со строкой кода). Сюда не входят +1 за каждый переход стрелкой (script.rpy:453) и +5 за сон (change_day).</p>'
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

if __name__=='__main__':
    print('effects total:',len(effects))
    for fn in ROUTE_COL:
        open(fn,'w',encoding='utf8').write(patch_route(fn,ROUTE_COL[fn]))
        print('route',fn,'ok')
    skip=set(ROUTE_COL)|{'time.html','todo.html'}
    for fn in sorted(glob.glob('*.html')):
        if fn in skip: continue
        open(fn,'w',encoding='utf8').write(patch_generic(fn))
    print('generic done')
