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

# ---- short mode for diagrams ----
SHORT=False
LEG={}
_long_key=_key
MEAN={'"dev_leni" in airat_sp':('Лени уже увидел Луизу рядом с героиней (метка «dev_leni»)','ставится в момент, когда Лени впервые видит Луизу рядом с героиней (script_4_airat.rpy:626-627, реплика «Л-л-л-луиза?!»); нигде не сбрасывается; читается в разговоре с Луизой (day_1_dev_razg.rpy:39) как условие темы про Лени','Лени ещё не видел Луизу рядом с героиней (метки «dev_leni» нет)')}
def _key(a):
    if not SHORT: return _long_key(a)
    m=re.fullmatch(r'(td\d|vd\d|ld\d|devd|\w+_d)\.d(\d+)',a)
    if m:
        w=where(a); LEG[a]=w or 'где ставится, в коде не найдено'
        return 'флаг «%s» стоит'%a
    if a in MEAN: LEG[a]=MEAN[a][1]; return MEAN[a][0]
    m=re.fullmatch(r'"(\w+)" in ([\w.]+)',a)
    if m and not a.endswith('.note'):
        w=where(a)
        if w: LEG[a]=w; return 'метка «%s» уже записана'%m.group(1)
    m=re.fullmatch(r'"(\w+)" in (?:vrem_memory|persistent\.memory)\["(\w+)"\]',a)
    if m:
        w=where('"%s" in mem:%s'%(m.group(1),m.group(2)))
        if w: LEG[a]=w; return 'в памяти «%s» есть запись «%s»'%(m.group(2),m.group(1))
    return None
_atom2=atom
def atom(a):
    a=_strip_par(a)
    if SHORT:
        m=re.fullmatch(r'not (.+)',a)
        if m:
            inner=m.group(1).strip()
            k=_key(inner)
            if k: return MEAN[inner][2] if inner in MEAN else k.replace('уже произошло','ещё не произошло').replace('стоит','не стоит').replace('уже записана','ещё не записана').replace('есть запись','нет записи')
    # logic/mad levels via definitions (script.rpy:126-145)
    LV={'mad':{1:3,2:6,3:9},'logic':{1:2,2:4,3:6}}
    NM={'mad':'безумия','logic':'логики'}
    def pts(kind,op,n):
        t=LV[kind]
        if op in('>=',) : return 'не ниже' if False else None
    mm=re.fullmatch(r'(?:not )?(mad_l|logic_l)\(\)',a)
    if mm:
        kind='mad' if mm.group(1)=='mad_l' else 'logic'
        if a.startswith('not'): return 'уровень %s героини равен 0 (%s)'%(NM[kind],'безумие 0-2' if kind=='mad' else 'логика 0-1')
        return 'уровень %s героини не ниже 1 (%s %d и больше)'%(NM[kind],'безумие' if kind=='mad' else 'логика',LV[kind][1])
    mm=re.fullmatch(r'(?:sanity\.get_level\("(mad|logic)"\)|(mad_l|logic_l)\(\))\s*(>=|<=|>|<|==|!=)\s*(\d+)',a)
    if mm:
        kind=mm.group(1) or ('mad' if mm.group(2)=='mad_l' else 'logic')
        op=mm.group(3);n=int(mm.group(4));t=LV[kind]
        lo={0:0,1:t[1],2:t[2],3:t[3]};hi={0:t[1]-1,1:t[2]-1,2:t[3]-1,3:None}
        w=NM[kind];p='безумие' if kind=='mad' else 'логика'
        if op=='>=': need=n
        elif op=='>': need=n+1
        else: need=None
        if need is not None:
            if need<=0: return 'уровень %s героини любой'%w
            if need>3: return 'невозможно: уровень %s не бывает выше 3'%w
            return 'уровень %s героини не ниже %d (%s %d и больше)'%(w,need,p,t[need])
        if op in('<','<='):
            top=n-1 if op=='<' else n
            if top<0: return 'невозможно'
            return 'уровень %s героини не выше %d (%s %s)'%(w,top,p,('не больше %d'%hi[top]) if hi[top] is not None else 'любое')
        if op=='==': return 'уровень %s героини равен %d (%s %s)'%(w,n,p,('от %d до %d'%(lo[n],hi[n])) if hi[n] is not None else '%d и больше'%lo[n])
        if op=='!=': return 'уровень %s героини не равен %d'%(w,n)
    if re.fullmatch(r'not (mad_l|logic_l)\(\)',a): pass
    mm=re.fullmatch(r'"(\w+)" in inv_list\["(\w+)"\]\.note',a)
    if mm: return 'в заметках предмета «%s» есть запись «%s»'%(mm.group(2),mm.group(1))
    mm=re.fullmatch(r'not "(\w+)" in inv_list\["(\w+)"\]\.note',a)
    if mm: return 'в заметках предмета «%s» нет записи «%s»'%(mm.group(2),mm.group(1))
    mm=re.fullmatch(r'(\w+)\.lock\s*==\s*(\w+)\.lock',a)
    if mm: return '%s и %s сейчас в одном месте (у персонажей поле «lock» = место)'%(PERS.get(mm.group(1),mm.group(1)),PERS.get(mm.group(2),mm.group(2)))
    mm=re.fullmatch(r'(\w+)\.lock\s*==\s*"([^"]+)"',a)
    if mm: return '%s сейчас в месте «%s»'%(PERS.get(mm.group(1),mm.group(1)),mm.group(2))
    return _atom2(a)
def _split_top(e,word):
    out=[];d=0;cur='';i=0
    toks=re.split(r'(\s+(?:and|or)\s+|\(|\))',e)
    for t in toks:
        if t=='(':d+=1;cur+=t
        elif t==')':d-=1;cur+=t
        elif d==0 and re.fullmatch(r'\s+%s\s+'%word,t or ''): out.append(cur);cur=''
        else: cur+=t
    out.append(cur);return [x.strip() for x in out if x.strip()]
def _strip_par(e):
    e=e.strip()
    while e.startswith('(') and e.endswith(')'):
        d=0;ok=True
        for i,ch in enumerate(e):
            d+=ch=='(';d-=ch==')'
            if d==0 and i<len(e)-1: ok=False;break
        if not ok: break
        e=e[1:-1].strip()
    return e
def cond_html(expr,lvl=0):
    """Russian condition, atoms on separate lines, logical AND/OR explicit and correctly grouped."""
    global SHORT
    old=SHORT;SHORT=True
    try:
        def f(e,lv):
            e=_strip_par(e)
            ors=_split_top(e,'or')
            if len(ors)>1:
                parts=[f(x,lv+1) for x in ors]
                return ('<br/><b>или</b><br/>').join(('(%s)'%p if '<br/>' in p else p) for p in parts)
            ands=_split_top(e,'and')
            if len(ands)>1:
                return ('<br/><b>и одновременно</b><br/>').join(('(%s)'%p if '<b>или</b>' in p else p) for p in (f(x,lv+1) for x in ands))
            return atom(e)
        return f(expr,0)
    finally: SHORT=old

# ---- derive meaning from set sites ----
_FILES={}
def _lines(fn):
    if fn not in _FILES: _FILES[fn]=open('/tmp/viy/game/'+fn,encoding='utf8',errors='ignore').read().split('\n')
    return _FILES[fn]
def _ind(l): return len(l)-len(l.lstrip(' \t'))
def _clean(t): return re.sub(r'\{[^}]*\}','',t).replace('\\n',' ').strip()
def ctx(lab,fn,line):
    ls=_lines(fn);i=line-1;base=_ind(ls[i])
    j=i-1
    while j>=0:
        l=ls[j]
        if l.strip() and not l.strip().startswith('#'):
            if re.match(r'label \w+:',l): break
            if _ind(l)<base:
                t=l.strip()
                m=re.match(r'"(.*?)"\s*(?:if .*)?:$',t)
                if m: return 'при выборе варианта «%s»'%_clean(m.group(1))[:70]
                base=_ind(l)
        j-=1
    # scene: first speech after label
    k=j+1 if j>=0 else 0
    for z in range(k,min(k+60,len(ls))):
        m=re.match(r'\s*(\w+) "(.*)"\s*$',ls[z]) or re.match(r'\s*()"(.*)"\s*$',ls[z])
        if m and not ls[z].strip().startswith('$'): return 'в сцене, начинающейся словами «%s»'%_clean(m.group(2))[:70]
    return 'в сцене «%s»'%lab
def derive(key):
    _scan();st=_SET.get(key)
    if not st: return None
    cs=[]
    for lab,fn,ln in st[:3]:
        c=ctx(lab,fn,ln)
        if c not in cs: cs.append(c)
    t=' / '.join(cs)+(' (и ещё в %d местах)'%(len(st)-3) if len(st)>3 else '')
    return t
_orig_scan=_scan
def _scan():
    if _SET or _RESET: return
    _orig_scan()
    for f in glob.glob('/tmp/viy/game/*.rpy'):
        ls=open(f,encoding='utf8',errors='ignore').read().split('\n');fn=f.split('/')[-1];lab=None
        for i,l in enumerate(ls):
            m=re.match(r'label (\w+):',l)
            if m: lab=m.group(1)
            m=re.search(r'\$ ([A-Za-z_]\w*)\s*=\s*(True|1|"[^"]*")\s*$',l)
            if m: _SET.setdefault(m.group(1),[]).append((lab,fn,i+1))
_old2=_key
def _key(a):
    if not SHORT: return _old2(a)
    r=_old2(a)
    k=a
    m=re.fullmatch(r'([A-Za-z_]\w*)\s*(?:==\s*(?:True|1))?',a)
    if r is None and m and m.group(1) not in ('persistent',):
        k=m.group(1)
    if r is None and k in _SET.keys()|{k} :
        d=derive(k)
        if d: LEG[a]='выведено по месту, где это ставится: '+d+'. Не сбрасывается.' if k not in _RESET else 'выведено по месту, где это ставится: '+d; return 'уже произошло (ставится '+d.split(' / ')[0]+')'
    if r and a in _SET and LEG.get(a,'').startswith('устанавливается'):
        d=derive(a)
        if d: LEG[a]=LEG[a]+'. Выведено по месту установки: '+d
        if d and r.startswith('флаг'): return 'уже произошло (ставится '+d.split(' / ')[0]+')'
        if d and r.startswith('метка'): return 'уже произошло (ставится '+d.split(' / ')[0]+')'
        if d and r.startswith('в памяти'): return 'уже произошло (ставится '+d.split(' / ')[0]+')'
    return r

def cond_plain(expr):
    h=cond_html(expr).replace('<br/><b>и одновременно</b><br/>',' И ').replace('<br/><b>или</b><br/>',' ИЛИ ')
    return re.sub(r'<[^>]+>','',h)

MEAN.update({
 'inv_list["tea"]._active':('чашка чая у героини в руках (предмет «tea» активен)','ставится в 1 при передаче чашки чая Горраном (script_5_airat.rpy:241), там же «cap» сбрасывается в 0','чашки чая у героини в руках нет'),
 'inv_list["cap"]._active':('предмет «cap» (капибара-вариант) активен','выставляется в 0 при получении чая (script_5_airat.rpy:242); где ставится 1 - не проверено','предмет «cap» не активен'),
 'dv == "Сапуля"':('Луизе героиня назвалась именем «Сапуля»','dv хранит имя, которым героиня назвалась Луизе (script3_airat.rpy:541-555); значение «Сапуля» вводит игрок или выбранный вариант - источник именно этой строки не проверен','Луизе героиня назвалась другим именем'),
 'dv == "Вий"':('Луизе героиня назвалась именем «Вий»','dv = "Вий", когда имя героини равно «Вий» (script3_airat.rpy:541, 555); Луиза реагирует испугом','Луизе героиня назвалась не «Вий»'),
 'vinp == "Вий"':('игрок ввёл имя «Вий»','vinp - строка, введённая в окне «Меня зовут...» (script_3_less_end.rpy:65-67)','игрок ввёл другое имя'),
 'vinp == ""':('игрок оставил имя пустым','vinp - строка из окна «Меня зовут...» (script_3_less_end.rpy:65-67)','игрок ввёл какое-то имя'),
})

# ---- quests: names from the game, direct Russian, links ----
QN={}
for _l in open('/tmp/viy/game/script _define.rpy',encoding='utf8',errors='ignore'):
    _m=re.search(r'quests\["(\w+)"\]\s*=\s*quest\(name\s*=\s*"\w+",\s*name_quest\s*=\s*"([^"]+)"',_l)
    if _m: QN[_m.group(1)]=_m.group(2)
def qref(q):
    n=QN.get(q)
    if not n: return '«%s» (название в игре не задано)'%q
    return '«<a href=\'quests.html?v=%d#q_%s\' title=\'%s\'>%s</a>»'%(V,q,q,n) if SHORT else '«%s»'%n
_QW={'keep':('взят','не взят'),'done':('выполнен','не выполнен'),'know':('о нём известно','о нём не известно'),'false':('провален','не провален')}
_atom_q=atom
def atom(a):
    a=a.strip()
    m=re.fullmatch(r'(not\s+)?quests\["(\w+)"\]\.(keep|done|know|false)',a)
    if m:
        w=_QW[m.group(3)][1 if m.group(1) else 0]
        return 'Квест %s %s'%(qref(m.group(2)),w)
    return _atom_q(a)
V=314

# ---- quest diary entries (text from Diary_text.rpy, multi-line aware) ----
DT={}
_dt=open('/tmp/viy/game/Diary_text.rpy',encoding='utf8',errors='ignore').read()
for _m in re.finditer(r'quests\["(\w+)"\]\.diary\._part_text\[([\d\.\-]+)\]\s*=\s*\["((?:[^"\\]|\\.)*)"',_dt,re.S):
    DT[(_m.group(1),_m.group(2))]=re.sub(r'\s+',' ',re.sub(r'\{/?[a-z]+(=[^}]*)?\}','',_m.group(3).replace('\\n',' ').replace('\\',' '))).strip()
def _short(t,n=60): return t if len(t)<=n else t[:n-1]+'…'
_atom_q2=atom
def atom(a):
    a=a.strip()
    m=re.fullmatch(r'(not\s+)?quests\["(\w+)"\]\.diary\._part_text\[([\d\.\-]+)\]\[1\]',a)
    if m:
        t=DT.get((m.group(2),m.group(3)))
        return 'В дневнике квеста %s запись №%s %sоткрыта%s'%(qref(m.group(2)),m.group(3),'ещё не ' if m.group(1) else '',(': «%s»'%_short(t)) if t else '')
    return _atom_q2(a)
V=314

# ---- simple wording of derived conditions ----
def _simp(d):
    d=re.sub(r'при выборе варианта «',r'выбран вариант «',d)
    d=re.sub(r'в сцене, начинающейся словами «',r'в сцене со словами «',d)
    return d
_atom_s=atom
def atom(a):
    r=_atom_s(a)
    for pat,pos,neg in ((r'уже произошло \(ставится (.*)\)','Уже было: ','Метка уже стоит. Ставится: '),(r'ещё не произошло \(ставится (.*)\)','Ещё не было: ','Метка ещё не стоит. Ставится: ')):
        m=re.fullmatch(pat,r,re.S)
        if m:
            d=m.group(1)
            single=d.startswith('при выборе варианта') and ' / ' not in d and 'и ещё' not in d
            return (pos if single else neg)+_simp(d)
    return r
V=314
