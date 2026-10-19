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


# ============ LESS CONVERSATION SCENE ============
# Sources verified 20.10.2026: script_2_less_conv.rpy (conv), script_2_less_conv_amul.rpy (amul), script_3_less_end.rpy (end)
# idx: 4 zn(less.zn_name), 5 d7, 6 d8, 7 d4(vd1.d4 stare counter), 8 reward(quest_airat note)
def T_less(n, st):
    mad, logic, blood, mood, zn, d7, d8, d4, reward = st[0], st[1], st[2], st[3], st[4], st[5], st[6], st[7], st[8]
    if n == 'start_cycle':
        nd4 = d4 + 1
        if nd4 == 4:  # conv:39-47 auto exit
            return [('(пялился 3 раза, на 4-й Лесс сдаётся) Настроение+1', 0,0,0,1,None,{'d4':4},'conv_2',None)]
        return [('«Пялиться дальше»', 0,0,0,0,None,{'d4':nd4},'start_cycle',None),
                ('«НАДОЕЛО»', 0,0,0,0,None,{'d4':nd4},'conv_2',None),
                ('«Бочком-бочком отсюда» (Настроение-2)', 0,0,0,-2,None,{'d4':nd4},None,'EXIT road_begin (Бочком)')]
    if n == 'conv_2':
        return [('«Не надо меня есть!» (Настр+1)', 0,0,0,1,None,{},'who_i_am',None),
                ('«Эээ... Кевин?»', 0,0,0,0,None,{},'wrong_name',None),
                ('«Я-я не помню»', 0,0,0,0,None,{},'not_remember2',None),
                ('«Подставить шею» (Без+1, Настр+1, Кровь+1)', 1,0,1,1,None,{},'who_i_am',None),
                ('«Я знаю твое имя!»', 0,0,0,0,None,{},'name_quest',None)]
    if n == 'name_quest':
        return [('(пустой ввод)', 0,0,0,0,None,{},'not_remember2',None),
                ('(верное имя)', 0,0,0,0,None,{},'name_right',None),
                ('(неверное имя)', 0,0,0,0,None,{},'wrong_name',None)]
    if n == 'wrong_name':
        return [('(неверное имя, Настр-2)', 0,0,0,-2,None,{},'not_remember2',None)]
    if n == 'not_remember2':
        return [('(укус, Кровь+1, Настр+1)', 0,0,1,1,None,{},'who_i_am',None)]
    if n == 'name_right':  # amul:1; less.mood - 4 - no-op (нет =), zn=True
        return [('«Безразлично улыбнуться» (Без+2)', 2,0,0,0,None,{'zn':1},'samsp',None),
                ('«Это случайность!» (Настр+5)', 0,0,0,5,None,{'zn':1},'amulmenu',None)]
    if n == 'samsp':
        return [('«А почему нет? Ты же шутишь»', 0,0,0,0,None,{},None,'BAD END «Шутка...»'),
                ('«Ээм... Нет?»', 0,0,0,0,None,{},'less_go',None)]
    if n == 'amulmenu':
        r = [('лупа: осмотреть амулет (Лог+1)', 0,1,0,0,'Осмотр окружения',{},'amulmenu',None)]  # amul:117, lupa_act=1
        return r + [('«Ч-что это?»', 0,0,0,0,None,{},'what_is_it',None),
                    ('«Не брать»', 0,0,0,0,None,{},'notake',None),
                    ('«Взять амулет»', 0,0,0,0,None,{},'take',None),
                    ('«Без лишних слов надеть»', 0,0,0,0,None,{},'dress',None)]
    if n == 'what_is_it':
        return [('(Лог+1, Без-1, Настр+1) «Это все что он делает?»', -1,1,0,1,None,{},'what_else',None),
                ('(Лог+1, Без-1, Настр+1) «Поняла... Спасибо»', -1,1,0,1,None,{},'amul_menu',None)]
    if n == 'what_else':
        return [('(Лог+1, Без-1)', -1,1,0,0,None,{},'amul_menu',None)]
    if n == 'amul_menu':
        return [('«Возьму»', 0,0,0,0,None,{},'take',None),
                ('«Ну его»', 0,0,0,0,None,{},'notake',None)]
    if n == 'take':
        return [('«Да (надеть сразу)»', 0,0,0,0,None,{},'who_i_am',None),
                ('«Убрать в карман» (Лог+1, Без-1, Настр+1)', -1,1,0,1,None,{},'who_i_am',None)]
    if n == 'dress':
        return [('(надела, Без+1, Настр-1)', 1,0,0,-1,None,{},'who_i_am',None)]
    if n == 'notake':
        return [('(Настр+1)', 0,0,0,1,None,{},'who_i_am',None)]
    if n == 'who_i_am':
        return [('«П...Подожди!»', 0,0,0,0,None,{},'stop',None),
                ('«Дать уйти»', 0,0,0,0,None,{},'less_go',None),
                ('«Схватить за плечо»', 0,0,0,0,None,{},'hand',None)]
    if n == 'stop':
        if mood < 0:
            return [('(остановить при Настр<0)', 0,0,0,0,None,{},'less_go',None)]
        return [('(остановить при Настр>=0)', 0,0,0,0,None,{},'less_name',None)]
    if n == 'less_name':  # zn=True here
        return [('«Видимо мы... знакомы?»', 0,0,0,0,None,{'zn':1},'we_meet',None),
                ('«Лесс? Странное имя»', 0,0,0,0,None,{'zn':1},'strange1',None),
                ('«Приятно познакомиться...»', 0,0,0,0,None,{'zn':1},'i_dont_know_name',None)]
    if n == 'strange1':
        return [('«По-моему, отличное имя!» (Без+1)', 1,0,0,0,None,{},'we_meet',None),
                ('«Я не понимаю. В смысле, лес?» (Лог+1)', 0,1,0,0,None,{},'strange2',None)]
    if n == 'strange2':
        return [('«Раздраженно посмотреть» (Без-1, Настр+1)', -1,0,0,1,None,{},'strange3',None),
                ('«Каменное лицо. Дзен» (Настр-1, Лог+1)', 0,1,0,-1,None,{},'strange3',None)]
    if n == 'strange3':
        return [('«А почему смерти?»', 0,0,0,0,None,{},'strange4',None),
                ('«Не стоит уточнять...» (Лог+1)', 0,1,0,0,'Не уточнять, почему лес смерти.',{},'we_meet',None)]
    if n == 'strange4':
        dm_mood = 2 if logic >= 2 else 1  # conv:558-570
        return [('«Шаг назад» (Настр+%d при Лог%s, затем Лог+1)' % (dm_mood, '>=2' if logic>=2 else '<2'), 0,1,0,dm_mood,None,{},'we_meet',None),
                ('«Пожать плечами и подставить горло» (Без+1, Настр+1, Кровь+1)', 1,0,1,1,None,{},'we_meet',None)]
    if n == 'we_meet':
        return [('«Значит будут» (Настр+1, Без-1)', -1,0,0,1,None,{},'i_dont_know_name',None),
                ('«Что такое друзья?» (Без+1)', 1,0,0,0,None,{},'i_dont_know_name',None)]
    if n == 'i_dont_know_name':
        return [('«Еще чего!» (Без+1)', 1,0,0,0,None,{},'less_end',None),
                ('(ввод: Вий/пусто, Без+1)', 1,0,0,0,None,{},'less_end',None),
                ('(ввод: своё имя, Лог+1, Без-1, Настр+1)', -1,1,0,1,None,{},'less_end',None)]
    if n == 'less_end':
        # conv:735-751: если mood>0 и mad<3 (get_level<1): Настр+1 (урза)
        if mood > 0 and mad <= 2:
            return [('(благодушный Лесс, Настр+1, метка урзы)', 0,0,0,1,None,{},'less_end_menu',None)]
        return [('(Лесс уходит)', 0,0,0,0,None,{},'less_end_menu',None)]
    if n == 'less_end_menu':
        if mood < 0:
            return [('«Попытаться остановить» (Настр<0)', 0,0,0,0,None,{},'gone',None),
                    ('«Оставить в покое»', 0,0,0,0,None,{},'gone',None)]
        return [('«Попытаться остановить»', 0,0,0,0,None,{},'cont',None),
                ('«Оставить в покое»', 0,0,0,0,None,{},'gone',None)]
    if n == 'cont':
        if mad >= 3:  # get_level("mad")>=1
            return [('(Без>=3: Лесс не слушает)', 0,0,0,0,None,{},'gone',None)]
        return [('(квест Айрат)', 0,0,0,0,None,{},'airat',None)]
    if n == 'airat':
        r = [('«Х-хорошо» (Настр-1 без reward / 0 с reward)', 0,0,0,(0 if reward else -1),None,{},'gone',None),
             ('«Еще чего!» (Настр-2)', 0,0,0,-2,None,{},'gone',None)]
        if not reward:
            r.insert(1, ('«А что мне за это будет?» (Настр+1, Лог+1, Без-1, +reward)', -1,1,0,1,None,{'reward':1},'airat',None))
        return r
    if n == 'gone':
        return [('(Лесс растворяется)', 0,0,0,0,None,{},None,'EXIT road_begin (gone)')]
    if n == 'hand':  # conv:986 mood-2
        return [('(схватила, Настр-2) «Отпустить» (Без-1)', -1,0,0,-2,None,{},'less_go',None),
                ('(схватила, Настр-2) «Удержать силой» (Настр-1)', 0,0,0,-3,None,{},'strength',None)]
    if n == 'strength':  # conv:1055 blood+1
        return [('(Кровь+1) «Отчаянно бороться»', 0,0,1,0,None,{},None,'BAD END «Тщетная борьба...»'),
                ('(Кровь+1) «Просто расслабиться» (Без+1, Лог-1)', 1,-1,1,0,'{i}Все в порядке, просто расслабиться.{/i}',{},'strength2',None),
                ('(Кровь+1) «Дико страшно... замереть» (Без-1, Лог+1)', -1,1,1,0,'{i}Дико страшно... Но стоить замереть.{/i}',{},'strength2',None)]
    if n == 'strength2':
        return [('«А сами-то! Как-то невежливо!» (Без+1, Настр+1)', 1,0,0,1,None,{},'less_go',None),
                ('«Промолчать» (Без-1)', -1,0,0,0,None,{},'less_go',None)]
    if n == 'less_go':
        r = [('«Со злости ударить дерево» (Лог-1, Без+1, Настр-2)', 1,-1,0,-2,None,{},'korn',None)]
        if blood > 0:
            r.append(('«Это было чертовски опасно...» (Лог+1, Без-1)', -1,1,0,0,None,{},'ushel',None))
        else:
            r.append(('«Что вообще произошло?» (Лог+1, Без-1)', -1,1,0,0,None,{},'ushel',None))
        r.append(('«Броситься за ним» (Без+1)', 1,0,0,0,None,{},'poter',None))
        return r
    if n == 'poter':
        return [('(имя: Вий, Без+1)', 1,0,0,0,None,{},None,'EXIT sluc (потеряшка)'),
                ('(имя: своё)', 0,0,0,0,None,{},None,'EXIT sluc (потеряшка)')]
    if n == 'korn':
        r = []
        if not d7 and not d8:
            r.append(('«Не шевелиться» (d7, Без+1)', 1,0,0,0,None,{'d7':1},'korn',None))
        if not d7 or d8:
            r.append(('«Обмякнуть, обмануть корни» (Без-1, Лог+1, Настр+1)', -1,1,0,1,'{i}Обмякнуть и попытаться обмануть корни.{/i}',{},'ushel',None))
        if d7 and not d8:
            r.append(('«Расслабиться и поспать» (Без+1, Настр+2)', 1,0,0,2,None,{},None,'END «Мирный сон...»'))
        if d8:
            r.append(('«В панике бороться до конца»', 0,0,0,0,None,{},None,'BAD END «Подкормка...»'))
        if not d8:
            r.append(('«Пытаться вырваться» (d8, Лог+1, Настр-1)', 0,1,0,-1,None,{'d8':1},'korn',None))
        if zn:
            r.append(('«Извиниться» (Лог+1, Настр+2)', 0,1,0,2,None,{},'ushel',None))
        return r
    if n == 'ushel':
        return [('(имя: Вий, Без+1)', 1,0,0,0,None,{},None,'EXIT road_begin (ushel)'),
                ('(имя: своё)', 0,0,0,0,None,{},None,'EXIT road_begin (ushel)')]
    return []

paths_less = enumerate_paths('start_cycle', INIT0, T_less)
summarize('LESS CONV SCENE', paths_less)
