import sys, json, itertools
sys.setrecursionlimit(100000)
def lm(m): return 0 if m<=2 else 1 if m<=5 else 2 if m<=8 else 3
def ll(l): return 0 if l<=1 else 1 if l<=3 else 2 if l<=5 else 3
def clampm(x): return max(-10,min(20,x))
def clampl(x): return max(-10,min(15,x))
# state: (node, mad, logic, mood, blood, flags)
def trans(S,P):
    n,mad,lg,mo,bl,F=S
    madl=lm(mad)>=1; logl=ll(lg)>=1
    ratio=0.5 if mad+lg==0 else lg/(mad+lg)
    r=[]
    def T(d,dm=0,dl=0,dmo=0,db=0,rs=None,fl=(),nx=None,tm=None): r.append((d,dm,dl,dmo,db,rs,tuple(fl),nx,tm))
    if n=='entry':
        T('Игнорировать (ign_dev)',tm='EXIT_IGN')
        T('Разбудить / Пойти на голос',nx='conv')
    elif n=='conv':
        T('Еще чего! Хочу побыть здесь',dm=1,dmo=-3,nx='inless')
        T('Абсолютно согласна',dl=1,dmo=1,nx='1menu')
        T('Безразлично пожать плечами',dm=1,nx='1menu')
    elif n=='1menu':
        T('Ловушку?',nx='after1')
        if 'd1' not in F: T('Кто ты?',fl=['d1'],nx='1menu')
        T('Молча идти дальше',nx='name')
    elif n=='after1':
        T('(devd.d2=1; логика +1)',dl=1,nx='m988')
    elif n=='m988':
        T('Я все поняла!',nx='name')
        T('Стоп... Объясни толком',nx='question')
        T('Это абсолютно не важно',dl=-1,dm=1,nx='name')
    elif n=='question':
        if 'q5' not in F: T('Почему ты сбежала из дома?',fl=['q5'],nx='question')
        if 'q3' not in F: T('Церковь Ара?',fl=['q3'],nx='who_q')
        if 'q10' not in F: T('Стена? Ловушка?',fl=['q10'],nx='question')
        if 'q9' not in F and 'q5' in F: T('Он объяснил почему?',fl=['q9'],nx='expl')
        T('Конец (и авто-выход, когда остальных пунктов нет)',nx='name')
    elif n=='who_q':
        for (d,dm,dl,dmo) in whoisa(logl): T('Ара: '+d,dm=dm,dl=dl,dmo=dmo,nx='question')
    elif n=='expl':
        T('Понятно...',nx='expl2')
        T('Тебе стоит послушать его',nx='expl2')
        T('Думай своей головой',nx='expl2')
        T('Сначала стоит понять почему...',dl=1,nx='expl2')
    elif n=='expl2':
        T('Хорошо, я помогу',dmo=1,nx='question')
        T('Нет, у меня свои дела',dmo=-1,nx='question')
    elif n=='name':
        if P['VIYNAME']:
            T('Я не помню... называй меня Вий',dmo=-2,nx='viy')
            T('Я – Вий',nx='viy')
        else:
            T('Я не помню... называй меня [v]',dmo=1,nx='amnez')
            T('Я – [v]',dmo=1,nx='myname')
        T('Сапуля Те Ля Камоле Каптуче Холе',fl=['dvS'],nx='myname')
        T('Миранда',dmo=1,nx='myname')
    elif n=='amnez':
        base=[]
        if ratio<=0.5:
            T('(ratio ≤0.5: мы беззаботно) dev.mood −1; выбор: Конечно!',dm=1,dmo=-1-2,nx='amnez2')
            T('(ratio ≤0.5) Это сарказм',dl=(0 if 'sar' in F else 1),dmo=-1-1,rs='sar',nx='amnez2')
        elif ratio>=0.7:
            T('(ratio ≥0.7) dev.mood +1',dmo=1,nx='amnez2')
        else:
            T('(0.5<ratio<0.7) без стат',nx='amnez2')
    elif n=='amnez2':
        dmo=0
        if not P['LESSZN'] and madl: dmo=-1
        T('(зн_лес/мад-ветка)',dmo=dmo,nx='m784')
    elif n=='m784':
        T('Это... и правда нехорошо',dm=-1,dl=1,dmo=-1,nx='memory')
        T('Пожать плечами',nx='memory')
        T('Это весело!',dm=2,dl=-2,dmo=-3,nx='chaos')
    elif n=='chaos':
        T('Хм,.. Звучит хорошо!',dm=2,dl=-2,dmo=-3,nx='inless')
        T('Нет. Это звучит плохо.',dm=-2,dl=2,dmo=1,nx='memory')
        if 'cd2' not in F: T('А кто это?',dl=1,fl=['cd2'],nx='chaos')
    elif n=='memory':
        T('Хорошо...',dm=-1,dmo=2,nx='mem2')
        T('Со мной все в порядке – нет',dm=1,dmo=-1,nx='mem2')
    elif n=='mem2':
        if 'q3' not in F and logl: T('(devd2.d3==0 и логика≥1: вызов whoisara) → myname',nx='mem_who')
        else: T('(падение: renpy.full_restart())',tm='CRASH')
    elif n=='mem_who':
        for (d,dm,dl,dmo) in whoisa(logl): T('Ара: '+d,dm=dm,dl=dl,dmo=dmo,nx='myname')
    elif n=='inless':
        T('(mood −4)',dmo=-4,nx='inless_m')
    elif n=='inless_m':
        T('Увязаться за ней',dm=1,dmo=-1,nx='follow')
        T('Оставить в покое',tm='EXIT_LEAVE')
    elif n=='follow':
        T('Что ж... Нам не по пути',tm='EXIT_NOPATH')
        T('Окей',dmo=-1,nx='deal')
    elif n=='deal':
        T('Идет.',dmo=1,tm='END_TOGETHER')
        T('Еще чего!',dm=1,dmo=-1,tm='END_TOGETHER')
    elif n=='myname':
        if P['VIYNAME'] and 'dvS' not in F: T('(dv=Вий) mood −2',dmo=-2,nx='viy')
        elif 'dvS' in F:
            T('Шутка! Меня зовут Миранда!',dmo=-1,fl=['dvM'],nx='myname_x')
            T('Нет конечно! Меня зовут [v].',dmo=-1,nx=('viy' if P['VIYNAME'] else 'myname_x'))
            T('Конечно!! Меня зовут Сапуля!',nx='myname_x',fl=['dvS_end'])
        else: T('(диалог с Дев; Ташир если рядом)',nx='myname_x')
    elif n=='myname_x':
        if 'dvS' in F and 'dvS_end' not in F:
            # dv changed to Миранда/[v] -> loop myname once, then plain
            T('(myname повторно, dv≠Сапуля)',fl=['dvS_end'],nx='end_t')
        else: T('(Луиза идет с вами, dev.near=1)',tm='END_TOGETHER')
    elif n=='end_t': T('(конец диалога имени)',tm='END_TOGETHER')
    elif n=='viy':
        T('Я не шучу. Я – Вий.',dmo=-20,nx='run')
        if 'shut' not in F: T('Э... Шутка. (→ myname, dv=Вий → mood −2 → снова viyname)',dmo=-2,fl=['shut'],nx='viy')
    elif n=='run':
        T('Пытаться догнать',nx='chase')
        T('Игнорировать',tm='END_RUN')
    elif n=='chase':
        T('Изо всех сил (кровь +1)',db=1,tm='END_RUN')
        T('Отставить попытки',tm='END_RUN')
    return r
def whoisa(logl):
    o=[]
    if logl: o.append(('Не может быть все так хорошо.',-1,1,0))
    o.append(('Кажется они хорошие ребята.',-1,0,2))
    o.append(('Скука смертная...',1,-1,-4))
    return o
def run(P,mad0,lg0):
    memo={}
    def go(S):
        if S in memo: return memo[S]
        n=S[0]
        res={'cnt':0,'min':[10**9]*4,'max':[-10**9]*4,'sum':[0]*4,'ends':{}}
        memo[S]=res  # loops cut by flags; guard
        for (d,dm,dl,dmo,db,rs,fl,nx,tm) in trans(S,P):
            _,mad,lg,mo,bl,F=S
            nm=clampm(mad+dm); nl=lg if dl==0 else clampl(lg+dl)
            if rs and rs in F: nl=lg
            F2=frozenset(F|set(fl)|({rs} if rs else set()))
            dd=(nm-mad,nl-lg,dmo,db)
            if tm:
                sub={'cnt':1,'min':[0]*4,'max':[0]*4,'sum':[0]*4,'ends':{tm:1}}
            else:
                sub=go((nx,nm,nl,0,0,F2))
            res['cnt']+=sub['cnt']
            for i in range(4):
                res['min'][i]=min(res['min'][i],sub['min'][i]+dd[i]); res['max'][i]=max(res['max'][i],sub['max'][i]+dd[i])
                res['sum'][i]+=sub['sum'][i]+dd[i]*sub['cnt']
            for k,v in sub['ends'].items(): res['ends'][k]=res['ends'].get(k,0)+v
        return res
    return go(('entry',mad0,lg0,0,0,frozenset()))
if __name__=='__main__':
    allmin=[10**9]*4; allmax=[-10**9]*4
    for vn in (False,True):
      for lz in (False,True):
        for mad0 in (0,3,6,9):
          for lg0 in (0,2,4,6):
            P={'VIYNAME':vn,'LESSZN':lz}
            r=run(P,mad0,lg0)
            for i in range(4):
                allmin[i]=min(allmin[i],r['min'][i]); allmax[i]=max(allmax[i],r['max'][i])
            if mad0==0 and lg0==0 or (mad0,lg0)==(3,2) and not vn:
                print(vn,lz,mad0,lg0,r['cnt'],r['min'],r['max'],[round(s/r['cnt'],2) for s in r['sum']],r['ends'])
    print('ENVELOPE min(mad,logic,mood,blood)',allmin,'max',allmax)
