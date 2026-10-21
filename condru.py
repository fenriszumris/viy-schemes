# -*- coding: utf-8 -*-
import re,html
exec(open('/tmp/sch/loc_names.py',encoding='utf8').read())
PERS={'tash':'Таш','fenya':'Феня','dev':'Луиза','nars':'Нарси','less':'Лесс','adro':'Адро','urza':'Урза','bonny':'Бонни','oh':'Адриан (Страж)','girl_air':'Девушка в церкви Айрата','viy':'героиня','kap':'Капибара'}
ATTR={'near':'идёт рядом с героиней','mood':'настроение','zn_name':'знает имя','zn_vpotpam':'знает, что «Вий» — псевдоним героини','helpp':'обещал помочь','bad':'отношение испорчено','good':'отношение хорошее','lock':'находится в месте','note':'заметки'}
def atom(a):
    a=a.strip().strip('()')
    m=re.fullmatch(r'(.+?)\s*==\s*(True|1)',a)
    if m and not m.group(1).strip().startswith('razg_menu'): return atom(m.group(1))
    m=re.fullmatch(r'(.+?)\s*==\s*(False|0)',a)
    if m and not re.search(r'mood|level',m.group(1)): return atom('not '+m.group(1).strip())
    m=re.fullmatch(r'(mad_l|logic_l)\(\)\s*(>=|<=|>|<|==)\s*(\d+)',a)
    if m:
        op={'>=':'не ниже','<=':'не выше','>':'выше','<':'ниже','==':'равен'}[m.group(2)]
        return 'уровень %s у героини %s %s'%({'mad_l':'безумия','logic_l':'логики'}[m.group(1)],op,m.group(3))
    m=re.fullmatch(r'sanity\.ratio\(\)\s*(>=|<=|>|<)\s*([\d.]+)',a)
    if m:
        op={'>=':'не меньше','<=':'не больше','>':'больше','<':'меньше'}[m.group(1)]
        return 'доля логики у героини (логика/(логика+безумие)) %s %s'%(op,m.group(2))
    m=re.fullmatch(r'razg_menu\s*==\s*"(\w+)"',a)
    if m: return 'разговор ведётся из меню персонажа «%s»'%({'tash':'Таш','less':'Лесс','dev':'Луиза','nars':'Нарси','fen':'Феня','bonny':'Бонни'}.get(m.group(1),m.group(1)))
    m=re.fullmatch(r'blood\s*>\s*0',a)
    if m: return 'у героини есть кровопотеря (blood > 0)'
    m=re.fullmatch(r'v\.name\s*==\s*"(.+)"',a)
    if m: return 'имя героини в игре сейчас «%s»'%m.group(1)
    m=re.fullmatch(r'(\w+)\.zn_name',a)
    if m and m.group(1) in PERS: return '%s знает имя героини или своё (признак zn_name)'%PERS[m.group(1)] if False else 'признак «%s.zn_name» (имя уже известно)'%m.group(1)
    m=re.fullmatch(r'quests\["(\w+)"\]\.(keep|done|know|false)',a)
    if m: return 'квест «%s»: %s'%(m.group(1),{'keep':'взят','done':'выполнен','know':'о нём известно','false':'провален'}[m.group(2)])
    m=re.fullmatch(r'not (.+)',a)
    if m:
        inner=m.group(1).strip()
        mf=re.fullmatch(r'(td\d|vd\d|ld\d|devd|nars_d|\w+_d)\.d(\d+)',inner)
        if mf: return 'флаг %s ещё не стоит (смысл флага в коде не подписан)'%inner
        return 'неверно, что: '+atom(inner)
    m=re.fullmatch(r'"(\w+)" in (\w+)\.note',a)
    if m: return 'в заметках %s есть запись «%s»'%({'tash':'Таша','fenya':'Фени','dev':'Луизы','nars':'Нарси','less':'Лесса'}.get(m.group(2),m.group(2)),m.group(1))
    m=re.fullmatch(r'"(\w+)" not in (\w+)\.note',a)
    if m: return 'в заметках «%s» нет записи «%s»'%(PERS.get(m.group(2),m.group(2)),m.group(1))
    m=re.fullmatch(r'"(\w+)" in (?:vrem_memory|persistent\.memory)\["(\w+)"\]',a)
    if m: return 'в памяти «%s» есть запись «%s»'%(m.group(2),m.group(1))
    m=re.fullmatch(r'my_location(?:\.name)? == (\w+)',a)
    if m: return 'героиня находится: %s'%(L[m.group(1)][0] if m.group(1) in L else m.group(1))
    m=re.fullmatch(r'"(\w+)" in ([\w.]+)',a)
    if m: return 'в списке «%s» есть метка «%s»'%(m.group(2),m.group(1))
    m=re.fullmatch(r'(\w+)\.(near|zn_name|zn_vpotpam|helpp|bad|good)',a)
    if m and m.group(1) in PERS: return '%s: %s'%(PERS[m.group(1)],ATTR[m.group(2)])
    m=re.fullmatch(r'(\w+)\.mood\s*(>=|<=|>|<|==)\s*(-?\d+)',a)
    if m and m.group(1) in PERS:
        op={'>=':'не ниже','<=':'не выше','>':'выше','<':'ниже','==':'равно'}[m.group(2)]
        return 'настроение (%s) %s %s'%(PERS[m.group(1)],op,m.group(3))
    m=re.fullmatch(r'sanity\.get_level\("(\w+)"\)\s*>=\s*(\d+)',a)
    if m: return 'уровень «%s» у героини не ниже %s'%({'mad':'безумие','logic':'логика'}.get(m.group(1),m.group(1)),m.group(2))
    m=re.fullmatch(r'(td\d|vd\d|ld\d|devd|nars_d|\w+_d)\.d(\d+)',a)
    if m: return 'флаг %s уже стоит (смысл флага в коде не подписан)'%a
    m=re.fullmatch(r'(\w+)\.(\w+)',a)
    if m: return 'признак «%s» (смысл в коде не подписан)'%a
    return 'проверка в коде (смысл не расшифрован)'
def cond_ru(expr):
    parts=re.split(r'\s+(and|or)\s+',expr.strip())
    out=[]
    for p in parts:
        if p=='and': out.append('и')
        elif p=='or': out.append('или')
        else: out.append(atom(p))
    return ' '.join(out)

import glob
_SET={}
_RESET={}
def _scan():
    if _SET or _RESET: return
    for f in glob.glob('/tmp/viy/game/*.rpy'):
        ls=open(f,encoding='utf8',errors='ignore').read().split('\n');fn=f.split('/')[-1]
        lab=None
        for i,l in enumerate(ls):
            m=re.match(r'label (\w+):',l)
            if m: lab=m.group(1)
            m=re.search(r'\$ ([\w.]+)\s*(=|\+=|-=)\s*(\w+)',l)
            if m and re.search(r'\.d\d+$',m.group(1)):
                tgt=_RESET if (m.group(2)=='=' and m.group(3) in ('0','False')) else _SET
                tgt.setdefault(m.group(1),[]).append((lab,fn,i+1))
            m=re.search(r'\$ ([\w.]+)\.append\("(\w+)"\)',l)
            if m: _SET.setdefault('"%s" in %s'%(m.group(2),m.group(1)),[]).append((lab,fn,i+1))
            m=re.search(r'persistent_append\("(\w+)", *"(\w+)"\)',l)
            if m: _SET.setdefault('"%s" in mem:%s'%(m.group(1),m.group(2)),[]).append((lab,fn,i+1))
            m=re.search(r'\.remove\("(\w+)"\)',l)
            if m: _RESET.setdefault('"%s" in *'%m.group(1),[]).append((lab,fn,i+1))
def where(key):
    _scan()
    st=_SET.get(key)
    if not st: return None
    def fmt(x): return '«%s» (%s:%d)'%x
    t='устанавливается (мест: %d): %s'%(len(st),', '.join(fmt(x) for x in st[:3])+(' и ещё %d'%(len(st)-3) if len(st)>3 else ''))
    rs=_RESET.get(key)
    t+='; сбрасывается: '+(', '.join(fmt(x) for x in rs[:2]) if rs else 'нигде в коде не найдено')
    return t+'. Смысл флага в коде не назван'
_old_atom=atom
def atom(a):
    a=a.strip().strip('()')
    m=re.fullmatch(r'not (.+)',a)
    if m:
        inner=m.group(1).strip()
        w=_key(inner)
        if w: return 'ещё не выполнено: %s'%w
        return 'неверно, что: '+atom(inner)
    w=_key(a)
    return w if w else _old_atom(a)
def _key(a):
    m=re.fullmatch(r'(td\d|vd\d|ld\d|devd|\w+_d)\.d(\d+)',a)
    if m:
        w=where(a)
        return 'флаг %s (%s)'%(a,w if w else 'где ставится, в коде не найдено')
    m=re.fullmatch(r'"(\w+)" in ([\w.]+)',a)
    if m and not a.endswith('.note'):
        w=where(a)
        if w: return 'метка «%s» в списке «%s» (%s)'%(m.group(1),m.group(2),w)
    m=re.fullmatch(r'"(\w+)" in (?:vrem_memory|persistent\.memory)\["(\w+)"\]',a)
    if m:
        w=where('"%s" in mem:%s'%(m.group(1),m.group(2)))
        if w: return 'в памяти «%s» есть запись «%s» (%s)'%(m.group(2),m.group(1),w)
    return None
