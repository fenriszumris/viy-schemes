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
