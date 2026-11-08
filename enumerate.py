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


# ============ ROAD SCENE (script3_road.rpy) ============
# Sources verified 20.10.2026: script3_road.rpy (road), script.rpy (krug, setblood, add_logic/add_mad)
# idx: 4 day(1=день), 5 elfs_krug(удары о барьер), 6 circles(kr_less_per), 7 -, 8 meet_kr
# Факты из кода:
#  road:41  «Стоит переждать» add_logic(1) БЕЗ reason -> без дедупа, но только ночью; после совы day (sova:90)
#  road:144-146 удар о барьер: add_mad(1) один раз (гейт elfs_krug)
#  road:169-171 с 4-го удара (elfs_krug>=4 после +=1): setblood(blood+1) каждый удар; blood>=3 -> sm_blood (script.rpy:289)
#  script.rpy:292-299 krug(1) вызывается ТОЛЬКО в script_3_hzdorog: круг +1 за заход через script_3_road/roadway
#    (вход в сцену, «Нет проблем» ночью, sluc-вперёд). Возвраты от барьера и от встречи с Лессом идут через
#    call_screen_strel и круг НЕ добавляют.
#  road:336-390 kr_less: статов нет; less_delo -> меню без эффектов (встреча повторяется), иначе meet_kr=1
#  kr_bur/bur_menu/bur_osm (road:253-330) НЕДОСТУЖНЫ: единственный jump закомментирован (road:252)
CAP_CIRCLES=6; CAP_HITS=6
def T_road(n, st):
    mad, logic, blood, mood, day, hits, circ, _x, meet = st[0], st[1], st[2], st[3], st[4], st[5], st[6], st[7], st[8]
    if n=='entry':
        return [('(вход днём)',0,0,0,0,None,{'zn':1,'d8':1},'hz',None),
                ('(вход ночью)',0,0,0,0,None,{'zn':0},'nm',None)]
    if n=='nm':
        return [('«Не вижу никаких проблем»',0,0,0,0,None,{'d8':circ+1},'hz',None),
                ('«Стоит переждать» (Логика+1)',0,1,0,0,None,{},None,'EXIT script3_sova_begin (сон/сова)')]
    if n=='hz':
        if circ >= 4:
            return [('(круг %d >= 4: встреча с Лессом)'%circ,0,0,0,0,None,{},'kr_less',None)]
        r=[('«Куда-нибудь» (случайный выбор)',0,0,0,0,None,{},'sluc',None),
           ('Направо — к Тёмной Гавани',0,0,0,0,None,{},None,'EXIT script_3_tgavan_road_begin')]
        if hits < CAP_HITS:
            r.append(('Вперёд — удариться о барьер',0,0,0,0,None,{},'bar',None))
        return r
    if n=='bar':
        nh = hits + 1
        dm = 1 if hits == 0 else 0
        db = 1 if nh >= 4 else 0
        d = 'удар #%d'%nh + (' (Безумие+1)' if dm else '') + (' (Кровь+1)' if db else '')
        return [(d, dm,0,db,0,None,{'d7':nh},'hz',None)]  # возврат через strel, круг не растёт
    if n=='sluc':
        if circ + 1 > CAP_CIRCLES:
            return [('(случайно: назад)',0,0,0,0,None,{},None,'EXIT script3_nazad_begin')]
        # вперёд: снова script_3_road -> (ночью меню / днём roadway) -> hzdorog: круг +1
        nxt = 'hz' if day else 'nm'
        upd = {'d8':circ+1} if day else {}
        return [('(случайно: вперёд, снова перекрёсток)',0,0,0,0,None,upd,nxt,None),
                ('(случайно: назад)',0,0,0,0,None,{},None,'EXIT script3_nazad_begin')]
    if n=='kr_less':
        if meet:
            return [('(Лесс уже ушёл: тишина)',0,0,0,0,None,{},'hz',None)]
        return [('(встреча: «есть дело» — меню без эффектов)',0,0,0,0,None,{},'hz',None),
                ('(встреча: дела нет — Лесс уходит)',0,0,0,0,None,{'reward':1},'hz',None)]
    return []

paths_road = enumerate_paths('entry', INIT0, T_road, maxdepth=40)
summarize('ROAD SCENE', paths_road)
print('  max-blood path:')
for p in paths_road:
    if p['d'][2] == max(q['d'][2] for q in paths_road):
        print('   ', p['term'], p['d'], ' | '.join(p['path'])); break
print('  max-logic path:')
for p in paths_road:
    if p['d'][1] == max(q['d'][1] for q in paths_road):
        print('   ', p['term'], p['d'], ' | '.join(p['path'])); break


# ============ TASHA SCENE (script3_nazad.rpy + tash_game.rpy + day_1_tash_razg.rpy) ============
# Sources verified 20.10.2026: script3_nazad.rpy (2079 lines, full read), tash_game.rpy (1046), day_1_tash_razg.rpy (61)
# idx3 = НАСТРОЕНИЕ ТАШИ (tash.mood) — в этой сцене less.mood не меняется, крови нет.
# Гейты (одноразовые d-флаги кода):
IDX.update({'td1':10,'td3':11,'td4':12,'td5':13,
 't22':14,'t23':15,'t24':16,'t25':17,'t26':18,'t27':19,
 't31':20,'t32':21,'t34':22,'t38':23,'t312':24,'t37':25,'t33':26,'t35':27,'t310':28,'t39':29,
 't42':30,'t43':31,'t44':32,'t45':33,'t46':34,
 't51':35,'t52':36,'t53':37,'t54':38,'t55':39,
 't61':40,'t62':41,'t64':42,'tpr':43,
 'vd5':44,'played':45,'games':46,'uzn':47,'rt':48,'znl':49,'blu':50,'vd3':51,
 't65':52,'note_u':53,'note_um':54,'t313':55})

def mlev(m): return 0 if m<=2 else (1 if m<=5 else (2 if m<=8 else 3))   # script.rpy:153-161
def llev(l): return 0 if l<=1 else (1 if l<=3 else (2 if l<=5 else 3))   # script.rpy:162-168
def ratio05(mad,logic):
    t = mad+logic
    return (0.5 if t==0 else logic/t) > 0.5                               # script.rpy:134-139

CAP_GAMES = 3  # рематчи и повторные партии в коде не ограничены; кап для оценки (на странице пометка)

# Факты из кода:
#  nazad:213 +2 (первое «Подойти»), 249 -1 (игнор), 266 +1, 275 -3 (наутёк, vd1.d5), 323 +1,
#  402 +1, 413 -3, 420 +1, 462 +1 («Привет.»), 484 -1, 506+508 +1/Без+1 («Улыбнуться»), 513 -1,
#  533 -5 (sad), 563 +5 (извиниться), 582 +10 («Ладно» карты), 603 -3 (gone), 618 +2,
#  658 -1 («Нет.»), 732 +10, 744 -10, 954 +10, 968 -10, 1350 +5 (рематч),
#  1383 Без+1 («не понимаю друзей», гейт Без>=3), 1454 Лог+1 reason, 1465 Без-1, 1485-1486 Без-1 Лог+1,
#  1556 Без-1 («Настаиваю»), 1565 -5 (ser2), 1614 +1 (некромант при Без>=3), 1655 -1 (Лесс),
#  1666 CRASH ssanity («Кто такой Урза?») — NameError всегда; 1685 -1, 1697 -1,
#  1720 +3 («Извини...»), 1733 +3 / 1737 -1 (авто-проверка reason tpp==2),
#  1756 -1, 1765 Лог+1/1766 -1, 1771 +1 (t_pr), 1784 Лог+1/1789 -1, 1796 Без+1/1801 -1, 1815 +3 («Прости»),
#  1953 +1 (tash_tash_card, инвентарь), 2013 +1 (bonny), 2056 +1 (mant)
#  1032 Лог+1 reason «спросить об Урзе» (urzamore); 1043 jump urzali — LABEL НЕ СУЩЕСТВУЕТ -> crash
#  1098 Без+1 / 1104 Без-1 (urza2 разлом) -> return (конец); 1087 «blu» -> urza3 КОНЕЦ ДЕМОВЕРСИИ
#  tash_game:89 Без-1 («А правила!?»), 101 Без+1 («Поехали!»), cards_stop:208 -3
#  day_1_tash_razg:13 +1 («Как насчет карт?»)
#  nazad:930: флаги tash_game / script3_tash_cards_per не назначаются ни в одном .rpy сцены —
#  считались False => внутреннее меню (nazad:948-987) недостижимо (мёртвый код), «Хватит болтать!» -> end/2cards.

def T_tasha(n, st):
    mad, logic, tmood = st[0], st[1], st[3]
    g = lambda name: st[IDX[name]]
    ml, ll = mlev(mad), llev(logic)
    if n == 'entry':
        r = []
        for znl in (1, 0):
            for blu in (0, 1):
                lbl = '(вход%s%s)' % ('' if znl else ', Лесс незнаком', ', «blu» дежавю' if blu else '')
                r.append((lbl, 0,0,0,0,None,{'rt':0,'znl':znl,'blu':blu},'menu_main',None))
        for znl in (1, 0):
            for blu in (0, 1):
                lbl = '(вход-разговор razg_menu=tash%s%s)' % ('' if znl else ', Лесс незнаком', ', «blu»' if blu else '')
                r.append((lbl, 0,0,0,0,None,{'rt':1,'znl':znl,'blu':blu},'t_razg_menu',None))
        return r
    if n == 'menu_main':  # nazad:196
        return [('«Игнорировать его.» (Тм-1)', 0,0,0,-1,None,{},'go_menu',None),
                ('«Подойти познакомиться.» (Тм+2, 1-й раз)', 0,0,0,2,None,{},'hello_menu',None)]
    if n == 'go_menu':  # nazad:264
        return [('«Остановиться и поговорить.» (Тм+1)', 0,0,0,1,None,{},'stop_menu',None),
                ('«Прибавить шагу.»', 0,0,0,0,None,{},'run_menu',None),
                ('«Пуститься наутек.» (Тм-3, vd1.d5)', 0,0,0,-3,None,{'vd5':1},'gone',None)]
    if n == 'run_menu':  # nazad:312
        return [('«Постараться убежать от него.»', 0,0,0,0,None,{},'sad',None),
                ('«У меня нет на тебя времени!» (Тм+1)', 0,0,0,1,None,{},'help_menu',None),
                ('«Остановиться и выяснить, чего он пристал.»', 0,0,0,0,None,{},'razg_2menu',None)]
    if n == 'help_menu':  # nazad:331
        r = []
        if not g('td3'):
            r.append(('«Ты правда хочешь помочь?» (1 раз)', 0,0,0,0,None,{'td3':1},'help_menu',None))
        r.append(('«Нет, спасибо, не надо.»', 0,0,0,0,None,{},'withyou',None))
        r.append(('«Хорошо, я буду рада помощи.»', 0,0,0,0,None,{},None,'EXIT strel (Таша помогает: near+helpp)'))
        r.append(('«Остановиться и нормально поговорить» (td4.d5)', 0,0,0,0,None,{'td5':1},
                  'stop_menu' if not g('t46') else 'razg_2menu', None))
        return r
    if n == 'withyou':  # nazad:374
        r = []
        if not g('td4'):
            r.append(('«Что?! Зачем?!» (1 раз)', 0,0,0,0,None,{'td4':1},'withyou',None))
        r.append(('«Ни в коем случае!»', 0,0,0,0,None,{},'ny_menu',None))
        r.append(('«Л-ладно, иди.» (Тм+1)', 0,0,0,1,None,{},None,'EXIT strel (Таша с тобой: near)'))
        return r
    if n == 'ny_menu':  # nazad:389
        return [('«Я... Ты мне просто не нравишься.»', 0,0,0,0,None,{},'sad',None),
                ('«Я не могу сказать. Но не надо.» (Тм+1)', 0,0,0,1,None,{},'gone',None),
                ('«Просто нет.» (Тм-3)', 0,0,0,-3,None,{},'gone',None)]
    if n == 'gone':  # nazad:602 Тм-3 -> 2gone -> gubert
        return [('(Таша уходит, Тм-3) → Губерт', 0,0,0,-3,None,{},None,'EXIT script3_nazad_gubert')]
    if n == 'stop_menu':  # nazad:448 (vd1.d3=1)
        return [('«Чего тебе!?»', 0,0,0,0,None,{'vd3':1},'2cards',None),
                ('«Привет.» (Тм+1)', 0,0,0,1,None,{'vd3':1},'stop2_menu',None)]
    if n == 'stop2_menu':  # nazad:468
        return [('«Я... Просто испугалась.» (Тм-1)', 0,0,0,-1,None,{},'scared_menu',None),
                ('«Не знаю! Улыбнуться.» (Тм+1, Без+1)', 1,0,0,1,None,{},'hello_menu',None),
                ('«Потому что я не хочу с тобой разговаривать!» (Тм-1)', 0,0,0,-1,None,{},'sad',None)]
    if n == 'scared_menu':  # nazad:487
        r = [('«Ты похож на Лесса...»' if g('znl') else '«Ты похож на того странного незнакомца...»', 0,0,0,0,None,{},'hello_menu',None)]
        r.append(('«Ты мне не нравишься.»', 0,0,0,0,None,{},'sad',None))
        return r
    if n == 'sad':  # nazad:526 Тм-5
        return [('(Таша расстроился, Тм-5) «Остановить его.»', 0,0,0,-5,None,{},'sorry_menu',None),
                ('(Таша расстроился, Тм-5) «Дать уйти.»', 0,0,0,-5,None,{},'gone',None)]
    if n == 'sorry_menu':  # nazad:559
        return [('«Извиниться.» (Тм+5)', 0,0,0,5,None,{},'sorry2_menu',None),
                ('«Нет, ничего.»', 0,0,0,0,None,{},'gone',None)]
    if n == 'sorry2_menu':  # nazad:567
        r = [('«Прости, но у меня нет времени.»', 0,0,0,0,None,{},'gone',None)]
        if g('games') < CAP_GAMES:
            r.append(('«Ладно.» (Тм+10, карты)', 0,0,0,10,None,{},'tash_game',None))
        return r
    if n == 'hello_menu':  # nazad:616
        return [('«Я тоже очень рада!» (Тм+2)', 0,0,0,2,None,{},'2razg',None),
                ('«...»', 0,0,0,0,None,{},'2razg',None)]
    if n == '2razg':  # nazad:630
        r = []
        if not g('td1'):
            r.append(('«У меня и своих полно...» (1 раз)', 0,0,0,0,None,{'td1':1},'2razg',None))
        else:
            r.append(('«Нет.» (Тм-1)', 0,0,0,-1,None,{},None,'EXIT script3_nazad_gubert (через 2gone)'))
        r.append(('«Конечно помогу! Что хочешь?»', 0,0,0,0,None,{},'2cards',None))
        r.append(('«Узнать подробности.»', 0,0,0,0,None,{},'2cards',None))
        return r
    if n == '2cards':  # nazad:729
        r = []
        if g('games') < CAP_GAMES:
            r.append(('«Хорошо, давай сыграем.» (Тм+10)', 0,0,0,10,None,{},'tash_game',None))
        r += [('«Нет!» (Тм-10)', 0,0,0,-10,None,{},'sad',None),
             ('«П-подожди... Давай сначала поговорим!»', 0,0,0,0,None,{},'razg_2menu',None)]
        if not g('td5'):
            r.append(('«З...Зачем?» (1 раз)', 0,0,0,0,None,{'td5':1},'2cards',None))
        return r
    if n == 'razg_2menu':  # nazad:767
        r = []
        if not g('t22'):
            r.append(('«Как тебя зовут?»', 0,0,0,0,None,{'t22':1},'razg_2',None))
        if not g('t23') and g('t22'):
            r.append(('«У меня уже были проблемы с памятью?»', 0,0,0,0,None,{'t23':1},'razg_2menu',None))
        if g('t23') and not g('t26'):
            r.append(('«Много что поменялось?» (urza.zn)', 0,0,0,0,None,{'t26':1,'uzn':1},
                      'razg_2menu' if g('rt') else 'canurza', None))
        if g('t23') and not g('t24'):
            r.append(('«И что тогда со мной случилось в Лесу?»', 0,0,0,0,None,{'t24':1},'razg_2menu',None))
        if not g('t25') and (g('t24') or g('t32')):
            r.append(('«Ты так любишь карты?»', 0,0,0,0,None,{'t25':1},'razg_2menu',None))
        if ll >= 1 and not g('t27'):
            r.append(('«А тебя не смущает, что мы в этом лесу?» (Лог>=2)', 0,0,0,0,None,{'t27':1},'razg_2menu',None))
        if g('rt'):
            r.append(('«Назад» (в меню разговоров)', 0,0,0,0,None,{},'t_razg_menu',None))
        else:
            r.append(('«Хватит болтать!»', 0,0,0,0,None,{},'end' if g('played') else '2cards',None))
        return r
    if n == 'razg_2':  # nazad:1205
        return [('«Я потеряла память.»', 0,0,0,0,None,{},'nomemory',None),
                ('«Сделать морду кирпичом.»', 0,0,0,0,None,{},'razg_2menu',None),
                ('«Да! Классная же традиция!» (Без+1)', 1,0,0,0,None,{},'razg_2menu',None)]
    if n == 'nomemory':  # nazad:1241 (persistent.memory меняет пару опций, итоги те же)
        nxt = 'razg_2menu' if g('rt') else 'withyou'
        return [('«Я кое-что помню, но хотелось бы знать больше.» (memory)', 0,0,0,0,None,{},'2help',None),
                ('«Мне не нравится то что я помню.» (memory)', 0,0,0,0,None,{},nxt,None),
                ('«Я ничего не помню... Но хочу знать кто я...» (не memory)', 0,0,0,0,None,{},'2help',None),
                ('«Я ничего не помню. Но может так и лучше.» (не memory)', 0,0,0,0,None,{},nxt,None)]
    if n == '2help':  # nazad:1293 (urza.zn_name=True, заметки urza/urza_memory)
        nxt = 'razg_2menu' if g('rt') else '2help_menu'
        return [('(Урза может вернуть память)', 0,0,0,0,None,{'uzn':1,'note_u':1,'note_um':1},nxt,None)]
    if n == '2help_menu':  # nazad:1315
        r = []
        if ll >= 1 and not g('t32'):
            r.append(('«Расскажи о нем побольше.» (Лог>=2, без +Лог!)', 0,0,0,0,None,{'t32':1},'2help_menu',None))
        r.append(('«Да, это отличная идея!»', 0,0,0,0,None,{},'urza',None))
        r.append(('«Нет, я не думаю, что стоит.»', 0,0,0,0,None,{},'razg_2menu',None))
        return r
    if n == 'canurza':  # nazad:991
        r = [('«Ты... Можешь отвести меня к этому Урзе?»', 0,0,0,0,None,{'t31':1},'urza_question',None)]
        if not g('t32'):
            r.append(('«Расскажешь о нем побольше?»', 0,0,0,0,None,{},'urzamore',None))
        r.append(('«Я бы хотела спросить о другом.»', 0,0,0,0,None,{'t34':1},'razg_2menu',None))
        return r
    if n == 'urza_question':  # nazad:1012
        r = [('«Да, давай сейчас!»', 0,0,0,0,None,{},'urza',None),
             ('«Нет, не сейчас»', 0,0,0,0,None,{},'razg_2menu',None),
             ('«Может, сначала еще поговорим?»', 0,0,0,0,None,{'t31':1},'razg_2menu',None)]
        if ll >= 1 and not g('t32'):
            r.append(('«Сначала расскажи о нем побольше...» (Лог>=2)', 0,0,0,0,None,{},'urzamore',None))
        return r
    if n == 'urzamore':  # nazad:1030 Лог+1 reason; при td3.d1 -> urzali (МЕТКА НЕ НАЙДЕНА)
        nxt = None
        term = None
        if g('t31'):
            term = 'CRASH: label script3_nazad_tash_urzali не найден (nazad:1043)'
        return [('(рассказ об Урзе, Лог+1)', 0,1,0,0,'спросить об Урзе',{'t32':1},nxt or 'canurza',term)]
    if n == 'urza':  # nazad:1045 (near+helpp)
        return [('(идём к разлому)', 0,0,0,0,None,{},'urza3' if g('blu') else 'urza2',None)]
    if n == 'urza2':  # nazad:1091
        return [('«Прекрасно!» (Без+1)', 1,0,0,0,'Проход в какую-то дичь - это прекрасно!',{},None,'EXIT return после разлома (urza2:1115)'),
                ('«Сомнительно.» (Без-1)', -1,0,0,0,'Проход в какую-то дичь - это сомнительно!',{},None,'EXIT return после разлома (urza2:1115)')]
    if n == 'urza3':  # nazad:1116
        return [('(заколоченный тупик)', 0,0,0,0,None,{},None,'КОНЕЦ ДЕМОВЕРСИИ (urza3, «blu» в avt_d)')]
    if n == 'tash_game':  # tash_game:86
        return [('«А правила!?» (Без-1)', -1,0,0,0,None,{},'game_mid',None),
                ('«Поехали!» (Без+1)', 1,0,0,0,None,{},'game_mid',None)]
    if n == 'game_mid':  # партия: можно бросить (cards_stop Тм-3) или доиграть
        ng = g('games') + 1
        if g('rt'):
            return [('(партия #%d, бросить, Тм-3)' % ng, 0,0,0,-3,None,{'games':ng},'t_razg_menu',None),
                    ('(партия #%d, доиграть)' % ng, 0,0,0,0,None,{'games':ng},'t_razg_menu',None)]
        return [('(партия #%d, бросить, Тм-3)' % ng, 0,0,0,-3,None,{'games':ng},'razg_2menu',None),
                ('(партия #%d, доиграть)' % ng, 0,0,0,0,None,{'games':ng,'played':1},'igra_over',None)]
    if n == 'igra_over':  # nazad:1339 (заметка game)
        r = [('«Эм, хватит.»', 0,0,0,0,None,{},'end',None)]
        if g('games') < CAP_GAMES:
            r.append(('«Да! Почему нет?» (Тм+5, рематч)', 0,0,0,5,None,{},'tash_game',None))
        r.append(('«Может поговорим?»', 0,0,0,0,None,{},'razg_2menu',None))
        return r
    if n == 'end':  # nazad:1370
        r = []
        if not g('t38'):
            r.append(('«У тебя есть друзья?»', 0,0,0,0,None,{'t38':1},'end',None))
        if ml >= 1 and not g('t312') and g('t38'):
            r.append(('«Я... Не понимаю что такое друзья.» (Без>=3, Без+1)', 1,0,0,0,None,{'t312':1},'end',None))
        if g('t38') and not g('t37'):
            r.append(('«Врагов?»', 0,0,0,0,None,{'t37':1},'end',None))
        if ll >= 1 and not g('t33'):
            r.append(('«Думаешь, кто-то бы пришел в такое место поиграть?» (Лог>=2)', 0,0,0,0,None,{'t33':1},'end',None))
        if g('t33') and not g('t35'):
            r.append(('«Ты... правда не боишься?» (Лог+1, Без-1)', -1,1,0,0,'Ты... правда не боишься?',{'t35':1},'end',None))
        if not g('t310'):
            r.append(('«А почему твои друзья не могут прийти?»', 0,0,0,0,None,{'t310':1},'end',None))
        if not g('t39') and ratio05(mad, logic):
            r.append(('«Ты что, никогда не бываешь серьезным?» (Без-1, Лог+1, ratio>0.5)', -1,1,0,0,None,{'t39':1},'ser',None))
        r.append(('«Промолчать.»', 0,0,0,0,None,{},'end_out',None))
        return r
    if n == 'end_out':  # nazad:1490 (после меню)
        return [('(«Эх... Спасибо что сыграла!»)', 0,0,0,0,None,{},'2urza' if ll >= 1 else 'withyou',None)]
    if n == '2urza':  # nazad:1523
        return [('«Хорошая идея.»', 0,0,0,0,None,{},'urza',None),
                ('«Нет, не стоит...»', 0,0,0,0,None,{},None,'EXIT strel (Таша исчез после отказа от Урзы)')]
    if n == 'ser':  # nazad:1544
        return [('«Настаиваю.» (Без-1, затем Тм-5)', -1,0,0,-5,None,{},'ser2_men',None),
                ('«Нет-нет!»', 0,0,0,0,None,{},'end',None)]
    if n == 'ser2_men':  # nazad:1587
        r = []
        if not g('t42'):
            r.append(('«Так кто ты?»', 0,0,0,0,None,{'t42':1},'ser2_men',None))
        if g('t42') and not g('t62'):
            r.append(('«Ты... Некромант?» (Тм+1 при Без>=3)', 0,0,0,1 if ml >= 1 else 0,None,{'t62':1},'ser2_men',None))
        if not g('t64') and g('znl'):
            r.append(('«Что ты знаешь о Лессе?» (Тм-1)', 0,0,0,-1,None,{'t64':1},'ser2_men',None))
        if not g('t65') and g('uzn'):
            r.append(('«Кто такой Урза?» (nazad:1666 ssanity)', 0,0,0,0,None,{},None,'CRASH NameError ssanity (nazad:1666)'))
        if not g('t42'):
            pass  # «Что тебе от меня нужно?» делит гейт t42 с «Так кто ты?» — одна из двух
        r2 = []
        if not g('t42'):
            r2.append(('«Что тебе от меня нужно?» (Тм-1)', 0,0,0,-1,None,{'t42':1},'ser2_men',None))
        if not g('t43'):
            r2.append(('«Ты бы действительно помог мне?» (Тм-1)', 0,0,0,-1,None,{'t43':1},'ser2_men',None))
        if not g('t44') and g('t42'):
            r2.append(('«У меня есть причина...»', 0,0,0,0,None,{'t44':1,'t61':1},'reason_ser',None))
        if not g('t61') and g('t42'):
            r2.append(('«Извини...» (Тм+3, t_pr)', 0,0,0,3,None,{'t61':1,'tpr':1},'ser2_men',None))
        r2.append(('«А давай ты снова... перестанешь быть таким?» (afterser, gubert:5)', 0,0,0,0,None,{},'end',None))  # afterser: set_tash st, jump script3_nazad_tash_end — НЕ выход
        return r[:2] + r[2:] + r2 if False else r + r2
    if n == 'reason_ser':  # nazad:1727
        tpp = g('t51') + g('t52') + g('t53') + g('t54') + g('t55')
        if tpp == 2 and g('tpr'):
            return [('(2 причины + извинение: Тм+3)', 0,0,0,3,None,{},'ser2_men',None)]
        if tpp == 2 and not g('tpr'):
            return [('(2 причины без извинения: Тм-1)', 0,0,0,-1,None,{},'ser2_men',None)]
        r = []
        if not g('t51'):
            r.append(('«Я потеряла память.» (Тм-1)', 0,0,0,-1,None,{'t51':1},'reason_ser',None))
        if not g('t52'):
            r.append(('«Я хотела поговорить нормально.» (Лог+1, Тм-1)', 0,1,0,-1,None,{'t52':1},'reason_ser',None))
        if not g('t53'):
            r.append(('«Я... Я хотела лучше узнать тебя.» (Тм+1, t_pr)', 0,0,0,1,None,{'t53':1,'tpr':1},'reason_ser',None))
        if not g('t54'):
            r.append(('«Я хотела узнать о мире...» (Лог+1, Тм-1)', 0,1,0,-1,None,{'t54':1},'reason_ser',None))
        if not g('t55'):
            r.append(('«Я просто попросила. Мне было интересно.» (Без+1, Тм-1)', 1,0,0,-1,'Просто спросила!',{'t55':1},'reason_ser',None))
        if tpp == 1:
            r.append(('«Я... Прости.» (Тм+3, t_pr)', 0,0,0,3,None,{'tpr':1},'ser2_men',None))
        return r
    if n == 't_razg_menu':  # day_1_tash_razg:1 (razg_menu="tash")
        r = []
        if g('note_u'):
            r.append(('«По поводу этого Урзы...»', 0,0,0,0,None,{},'t_urza_menu',None))
        if g('games') < CAP_GAMES:
            r.append(('«Как насчет карт?» (Тм+1)', 0,0,0,1,None,{},'tash_game',None))
        r.append(('«Просто поболтать»', 0,0,0,0,None,{},'razg_2menu',None))
        r.append(('«На сегодня хватит разговоров!»', 0,0,0,0,None,{},None,'EXIT strel (разговоры окончены)'))
        return r
    if n == 't_urza_menu':  # day_1_tash_razg:26
        r = []
        if g('note_um') and not g('t313'):
            r.append(('«Он может вернуть мне память?» (1 раз)', 0,0,0,0,None,{'t313':1},'t_urza_menu',None))
        if not g('t32'):
            r.append(('«Расскажи о нем побольше.» (без +Лог!)', 0,0,0,0,None,{'t32':1},'t_urza_menu',None))
        r.append(('«Ты можешь отвести меня к нему?» (у перекрёстка)', 0,0,0,0,None,{},'urza',None))
        r.append(('«Ты можешь отвести меня к нему?» (не у перекрёстка — позже)', 0,0,0,0,None,{},'t_urza_menu',None))
        return r
    return []

INIT_T = tuple([0]*9 + [frozenset()] + [0]*46)
paths_tasha = enumerate_paths('entry', INIT_T, T_tasha, maxdepth=90)
summarize('TASHA SCENE (idx3 = Настроение Таши)', paths_tasha)
for nm, i, fn in [('min tmood',3,min), ('max tmood',3,max), ('max logic',1,max), ('min mad',0,min), ('max mad',0,max)]:
    best = fn(q['d'][i] for q in paths_tasha)
    for p in paths_tasha:
        if p['d'][i] == best:
            print('  %s (%+d):' % (nm, best), p['term'], p['d'])
            print('     ', ' | '.join(p['path'])); break
