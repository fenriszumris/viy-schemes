# -*- coding: utf-8 -*-
import re,html
exec(open('/tmp/sch/loc_names.py',encoding='utf8').read())
PERS={'tash':'Таш','fenya':'Феня','dev':'Луиза','nars':'Нарси','less':'Лесс','adro':'Адро','urza':'Урза','bonny':'Бонни','viy':'героиня','kap':'Капибара'}
ATTR={'near':'идёт рядом с героиней','mood':'настроение','zn_name':'знает имя','zn_vpotpam':'знает, что «Вий» — псевдоним героини','helpp':'обещал помочь','bad':'отношение испорчено','good':'отношение хорошее','lock':'находится в месте','note':'заметки'}
def atom(a):
    a=a.strip().strip('()')
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
_SP={'v':'Героиня','a':'Рассказчик','aa':'Рассказчик','vm':'Мысль героини','n':'Нарси','t':'Таш','ls':'Лесс','lss':'Лесс','ka':'Капибара','b':'Бонни','d':'Луиза','l':'Лени','k':'Карралак','f':'Феня','sov':'Сова','g1':'Горран','g2':'Алекс','sadr':'Адро'}
def _scan():
    if _SET: return
    for f in glob.glob('/tmp/viy/game/*.rpy'):
        ls=open(f,encoding='utf8',errors='ignore').read().split('\n');fn=f.split('/')[-1]
        lab=None
        for i,l in enumerate(ls):
            m=re.match(r'label (\w+):',l)
            if m: lab=m.group(1)
            keys=[]
            m=re.search(r'\$ ([\w.]+)\s*(?:=|\+=)\s*(?!0\b|False)',l)
            if m and re.search(r'\.d\d+$',m.group(1)): keys.append(m.group(1))
            m=re.search(r'\$ ([\w.]+)\.append\("(\w+)"\)',l)
            if m: keys.append('"%s" in %s'%(m.group(2),m.group(1)))
            m=re.search(r'persistent_append\("(\w+)", *"(\w+)"\)',l)
            if m: keys.append('"%s" in mem:%s'%(m.group(1),m.group(2)))
            for k in keys:
                if k in _SET: continue
                near=[]
                for j in list(range(i-1,max(i-8,0),-1))+list(range(i+1,min(i+4,len(ls)))):
                    mm=re.match(r'\s+(\w+) "(.*)"\s*$',ls[j]) or re.match(r'\s+()"(.*)"\s*$',ls[j])
                    if mm and not ls[j].strip().startswith('$'):
                        near.append('%s: «%s»'%(_SP.get(mm.group(1),mm.group(1) or 'Рассказчик'),re.sub(r'\{[^}]*\}','',mm.group(2))[:70]))
                        break
                _SET[k]=(lab,fn,i+1,near[0] if near else '')
def where(key):
    _scan()
    r=_SET.get(key)
    if not r: return None
    lab,fn,n,near=r
    return 'ставится в ветке «%s» (%s:%d)%s'%(lab,fn,n,(', рядом реплика '+near) if near else '')
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
