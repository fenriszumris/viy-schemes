import sys
sys.setrecursionlimit(100000)

# State vector: (mad, logic, blood, mood, zn, d7, d8, d4, reward, usedL)
# usedL: frozenset of logic reasons already used (add_logic dedups by reason; add_mad does not)

def clamp(v, lo, hi): return max(lo, min(hi, v))

# Transition = (desc, dm, dl, db, dmo, lreason, updates, next, term)
# updates: dict applied to state indexes by name
IDX = {'zn':4,'d7':5,'d8':6,'d4':7,'reward':8}

def step(st, t):
    desc, dm, dl, db, dmo, lreason, upd, nxt, term = t
    s = list(st)
    usedL = set(s[9])
    if lreason:
        if lreason in usedL:
            dl = 0
        else:
            usedL.add(lreason)
    s[0] = clamp(s[0]+dm, -10, 20)
    s[1] = clamp(s[1]+dl, -10, 15)
    s[3] += dmo
    s[2] += db
    for k, v in upd.items():
        s[IDX[k]] = v
    s[9] = frozenset(usedL)
    blood_exit = db and s[2] >= 3
    return tuple(s), blood_exit

def enumerate_paths(start, init, TRANS, maxdepth=80):
    out = []
    seen = set()
    def rec(node, st, path, prob, depth):
        if depth > maxdepth: return
        key = (node, st)
        if key in seen: return
        seen.add(key)
        ts = TRANS(node, st)
        p = prob / len(ts)
        for t in ts:
            ns, bexit = step(st, t)
            np_ = path + [t[0]]
            if t[8] or bexit:
                out.append({'term': 'EXIT_BLOOD(sm_blood)' if bexit else t[8],
                            'path': np_, 'prob': p,
                            'd': (ns[0]-init[0], ns[1]-init[1], ns[2]-init[2], ns[3]-init[3])})
            else:
                rec(t[7], ns, np_, p, depth+1)
    rec(start, init, [], 1.0, 0)
    return out

def summarize(name, paths):
    print('=== %s: %d terminal paths ===' % (name, len(paths)))
    for i, stat in enumerate(['mad','logic','blood','mood']):
        vals = [p['d'][i] for p in paths]
        exp = sum(p['prob']*p['d'][i] for p in paths)
        print('  %-6s min %+d  max %+d  mean %+.1f' % (stat, min(vals), max(vals), exp))
    tp = {}
    for p in paths: tp[p['term']] = tp.get(p['term'],0)+1
    print('  terminals:', tp)

# ============ START SCENE ============
# idx: 0 mad,1 logic,2 blood,3 mood,4 zn,5 d7,6 d8,7 d4(lupa_start used),8 reward(lupa_zeml used)
def T_start(n, st):
    if n=='start_menu':
        r=[('лупа: осмотреться (Логика+1)',0,1,0,0,'Осмотр окружения',{'d4':1},'start_menu',None)] if not st[7] else []
        return r+[('«лечь поспать» (Безумие+1)',1,0,0,0,None,{},'c1_sleep',None),
                  ('«укусить себя за руку» (Безумие+1)',1,0,0,0,None,{},'c1_hand',None),
                  ('«Пойти дальше»',0,0,0,0,None,{},None,'TO_LESS')]
    if n=='c1_sleep':
        return [('«Что это вообще сейчас было?»',0,0,0,0,None,{},'son',None),
                ('«Пожать плечами»',0,0,0,0,None,{},None,'TO_LESS')]
    if n=='son':
        return [('«Не стоит больше вспоминать» (Логика+1)',0,1,0,0,'Рациональное решение прекратить вспоминать',{},None,'TO_LESS'),
                ('«Пытаться вспомнить дальше»',0,0,0,0,None,{},'sud_memory',None)]
    if n=='sud_memory':
        return [('«Что за чертовщина...» (Безумие-1)',-1,0,0,0,None,{},'head_ache',None),
                ('«Да бросьте, все в порядке!» (Безумие+1)',1,0,0,0,None,{},'head_ache',None)]
    if n=='head_ache':
        return [('«Х-хватит...» (Кровь+1, Логика+1)',0,1,1,0,'Рациональное решение прекратить',{},None,'TO_LESS'),
                ('«Идти до конца!» (Кровь+1, Безумие+1)',1,0,1,0,None,{},None,'DEATH «Вспомнить все...»')]
    if n=='c1_hand':
        return [('«Укусить еще сильнее» (Безумие+1)',1,0,0,0,None,{},'hand_next',None),
                ('«Хватит экспериментов» (Логика+1, Безумие-1)',-1,1,0,0,'Осознание реальности',{},None,'TO_LESS')]
    if n=='hand_next':
        return [('(корни хватают, Кровь+1)',0,0,1,0,None,{},'zeml_menu',None)]
    if n=='zeml_menu':
        r=[('лупа: осмотреть ситуацию (Логика+1)',0,1,0,0,'Осмотр ситуации',{'reward':1},'zeml_menu',None)] if not st[8] else []
        return r+[('«Бежать» (Логика+1)',0,1,0,0,'Рациональное решение - бежать',{},'zeml_ran',None),
                  ('«Зашипеть в ответ» (Безумие+1)',1,0,0,0,None,{},'zeml_sh',None),
                  ('«Ничего не делать» (Безумие+1)',1,0,0,0,None,{},None,'DEATH «Подкормка...»')]
    if n=='zeml_sh':
        return [('«Продолжать шипеть» (Безумие+1)',1,0,0,0,None,{},'shh',None),
                ('«Бежать»',0,0,0,0,None,{},'zeml_ran',None)]
    if n=='zeml_ran':
        return [('«Пожалуйста! Не трогайте меня!»',0,0,0,0,None,{},None,'TO_LESS'),
                ('«Ничего не делать» (Безумие+1)',1,0,0,0,None,{},None,'DEATH «Подкормка...»')]
    if n=='shh':
        return [('«П-помогите!»',0,0,0,0,None,{},None,'TO_LESS'),
                ('«Замереть на месте»',0,0,0,0,None,{},None,'TO_LESS'),
                ('«Вот, шиплю, а меня схватило!» (Безумие+1)',1,0,0,0,None,{},None,'TO_LESS')]

INIT0 = (0,0,0,0,0,0,0,0,0,frozenset())
paths_start = enumerate_paths('start_menu', INIT0, T_start)
summarize('START SCENE', paths_start)
