import sys, itertools, json
sys.setrecursionlimit(100000)
def lm(m): return 0 if m<=2 else 1 if m<=5 else 2 if m<=8 else 3
def ll(l): return 0 if l<=1 else 1 if l<=3 else 2 if l<=5 else 3
# state: (node, mad, logic, oh, less, flags(frozenset), usedL(frozenset))
def trans(n, S, P):
    node, mad, lg, oh, less, F, UL = S
    A=P['AMUL']; mlv=lm(mad); llv=ll(lg)
    madl = mlv>=1; logl = llv>=1
    r=[]  # (desc, dmad, dlogic, doh, dless, reason, addflags, next, term)
    def T(d,dm=0,dl=0,do=0,dle=0,rs=None,fl=(),nx=None,tm=None): r.append((d,dm,dl,do,dle,rs,tuple(fl),nx,tm))
    if n=='entry':
        T('Постучать',do=-2,dle=-1,nx='f1'); T('Окликнуть',nx='f1'); T('Развернуться и уйти',dm=1,tm='EXIT')
    elif n=='f1': T('(Адриан: «Стойте и не двигайтесь»)',nx='1door')
    elif n=='1door':
        T('Замереть',do=1,nx='p2')
        if mlv>=1 and 'o1d1' not in F: T('Эй, не приказывай мне!',dm=1,do=-1,fl=['o1d1'],nx='1door')
        T('Осторожно спросить (Вы мне угрожаете?)',nx='p2')
        if llv>=1: T('Можете объяснить, где я?',do=1,nx='p2')
        T('Уйти обратно',tm='EXIT')
    elif n=='p2': T('(Адриан объясняет правила)',nx='2door')
    elif n=='2door':
        T('Я послушаю!',do=(1 if logl else 0),dm=-1,dl=1,rs='adr',nx='rools')
        T('Неа, я сама.',dm=1,dl=-1,rs='noadr',nx='noadr')
        T('Я, пожалуй, уберусь отсюда.',tm='EXIT')
    elif n=='rools': T('(Адриан представляется, спрашивает имя)',do=(-1 if madl else 1),nx='name_menu')
    elif n=='name_menu':
        if P['VIYNAME']: T('Меня зовут [v] (имя = Вий)',nx='viy_razg')
        else: T('Меня зовут [v].',nx='adr_razg')
        if 'od1d2' not in F: T('Я... Миранда.',do=-1,fl=['od1d2'],nx='name_menu')
        if 'od1d1' not in F and madl: T('Сапуля Те Ля Камоле Каптуче Холе.',dm=1,rs=None,fl=['od1d1'],nx='sapulya')
        if P['VIYZN'] and not P['VIYNAME']: T('Вий.',nx='viy_razg')
        T('Я хочу оставаться анонимной.',do=(1 if logl else 0),nx='adr_razg')
    elif n=='sapulya':
        T('Прошу прощения.',dm=-1,do=1,nx='name_menu')
        T('Но это правда мое имя!!',dm=1,dl=-1,do=-2,rs='sapulya',nx='noadr')
        T('Ладно, ладно! Это шутка!',nx='name_menu')
    elif n=='noadr': T('(Адриан открывает дверь)',do=-3,nx='noadr_door')
    elif n=='noadr_door':
        T('Пройти внутрь',tm='EXIT')
        T('Уйти назад',tm='EXIT')
        if 'od2d2' not in F: T('Почему там так темно?',fl=['od2d2'],nx='noadr_door')
        if 'od3d5' not in F: T('Мы можем еще поговорить?',fl=['od3d5'],nx='noadr_door')
    elif n=='adr_razg':
        d=0
        if A!=2:
            if logl: d=1
            elif madl: d=-1
        T('(Адриан: правила города)',do=d,nx='menu')
    elif n=='menu':
        if 'kmad' not in F:
            d=1-(1 if mlv>=2 else 0)
            T('Что такое Белая Стража?',do=d,fl=['kmad'],nx='menu')
        if 'od3d2' not in F: T('Вы упоминали Мастера.',fl=['od3d2'],nx='menu')
        if 'od3d10' not in F and 'kmad' in F: T('Здесь совсем нет запретов...',fl=['od3d10'],nx='menu')
        T('Спросить о нем самом',nx='about')
        if 'znv' in F and 'od3d11' not in F: T('Вы можете больше рассказать мне обо мне?',fl=['od3d11'],nx='o_viy_zn')
        if oh<0 and A==0: T('Я все узнала что хотела. (Адриан гасит свет)',nx='noadr')
        else:
            d=0
            if not madl and logl: d=1
            T('Я все узнала что хотела.',do=d,nx='vhod')
    elif n=='o_viy_zn':
        T('Звучит прекрасно!',do=-5,nx='menu'); T('Это нехорошо. Мне не нравится.',do=3,nx='menu')
    elif n=='about':
        if logl and 'od3d6' not in F: T('Вы... Не кажетесь мне преступником.',do=1,fl=['od3d6'],nx='about')
        if 'od3d6' in F and 'od3d7' not in F: T('Вы бы хотели отсюда уйти?',do=(1 if oh>0 else 0),fl=['od3d7'],nx='about')
        if 'od3d8' not in F: T('Вы тоже темный маг?',do=-2,fl=['od3d8'],nx='about')
        T('Вернуться к предыдущей теме.',nx='menu')
    elif n=='vhod':
        T('Пожалуй... Я вернусь назад.',tm='EXIT')
        T('Я... Хочу войти.',nx='potion')
    elif n=='potion':
        T('Взять очень осторожно.',tm='CRASH')
        d2=sum(1 for x in F if x.startswith('od6d2_'))
        k = d2
        def nxt():
            return k
        if A!=0:
            if k==0: T('Наплевать на предупреждение.',dm=1,do=-1,fl=['od6d2_1'],nx='potion')
            elif k==1: T('Наплевать на предупреждение.',dm=1,do=-1,fl=['od6d2_2'],nx='potion')
            else: T('Наплевать на предупреждение.',dm=1,do=-1,tm='EXIT')
        else:
            if k==0: T('Наплевать на предупреждение.',dm=1,do=-1,fl=['od6d2_1'],nx='potion')
            else: T('Наплевать на предупреждение.',dm=1,do=-1,tm='EXIT')
        T('Я не буду это пить!',tm='EXIT')
    elif n=='viy_razg': T('(Адриан о Вие)',do=-4,fl=['znv'],nx='viy_menu')
    elif n=='viy_menu':
        if P['PMEM']:
            T('Я потеряла память, но кое-что помню... (не нравится)',dm=-1,dl=1,do=3,nx='adr_razg')
            T('Я потеряла память... интересным человеком.',dm=1,dl=-1,nx='viy_please')
        if 'od3d9' not in F: T('Я не знаю кто я.',do=3,fl=['od3d9'],nx='sm_name')
        if 'od3d9' not in F: T('Я... Ага. (Скрыть потерю памяти)',nx='viy_please')
    elif n=='sm_name':
        T('Нет. Мое имя - это Вий!',dm=1,nx='viy_menu'); T('Хорошо... (ввод имени)',nx='viy_menu')
    elif n=='viy_please':
        T('Ха! Не приказывай мне!',dm=1,do=-1,nx='noadr'); T('Хорошо, я попробую!',do=2,nx='adr_razg')
    return r

def clamp(v,lo,hi): return max(lo,min(hi,v))
def step(S,t):
    node,mad,lg,oh,less,F,UL=S
    d,dm,dl,do,dle,rs,fl,nx,tm=t
    ul=set(UL)
    if rs:
        if rs in ul: dl=0
        else: ul.add(rs)
    mad2=clamp(mad+dm,-10,20); lg2=clamp(lg+dl,-10,15)
    return (nx,mad2,lg2,oh+do,less+dle,frozenset(set(F)|set(fl)),frozenset(ul))

def run(P):
    memo={}; onst=set()
    def solve(S):
        if S in memo: return memo[S]
        if S in onst: return None
        onst.add(S)
        ts=trans(S[0],S,P); k=len(ts)
        res={'c':0,'terms':{},'mn':[10**9]*4,'mx':[-10**9]*4,'ps':[0.0]*4}
        for t in ts:
            S2=step(S,t)
            dd=[S2[1]-S[1],S2[2]-S[2],S2[3]-S[3],S2[4]-S[4]]
            if t[8]:
                sub={'c':1,'terms':{t[8]:1},'mn':[0]*4,'mx':[0]*4,'ps':[0.0]*4}
            else:
                sub=solve(S2)
                if sub is None or sub['c']==0: continue
            res['c']+=sub['c']
            for a,b in sub['terms'].items(): res['terms'][a]=res['terms'].get(a,0)+b
            for i in range(4):
                res['mn'][i]=min(res['mn'][i],dd[i]+sub['mn'][i]); res['mx'][i]=max(res['mx'][i],dd[i]+sub['mx'][i])
                res['ps'][i]+=(dd[i]+sub['ps'][i])/k
        onst.discard(S); memo[S]=res; return res
    S0=('entry',P['mad'],P['logic'],0,0,frozenset(),frozenset())
    R=solve(S0)
    return R,len(memo),memo,S0

if __name__=='__main__':
    out=[]
    for mad,lg in [(0,0),(3,0),(0,2)]:
        for A in (0,2):
            for vz in (False,True):
                for pm in (False,True):
                    P=dict(mad=mad,logic=lg,AMUL=A,VIYZN=vz,PMEM=pm,VIYNAME=False)
                    R,n,_,_=run(P)
                    print('start m%d l%d amul%d viyzn%d pmem%d: paths %d states %d  mad %+d..%+d (%.2f)  logic %+d..%+d (%.2f)  oh %+d..%+d (%.2f)  less %+d..%+d  terms %s'%(mad,lg,A,vz,pm,R['c'],n,R['mn'][0],R['mx'][0],R['ps'][0],R['mn'][1],R['mx'][1],R['ps'][1],R['mn'][2],R['mx'][2],R['ps'][2],R['mn'][3],R['mx'][3],R['terms']),flush=True)
