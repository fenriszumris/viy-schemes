# -*- coding: utf-8 -*-
import re,glob,html,sys
sys.path.insert(0,'/tmp/sch')
import condru
from condru import cond_html
from trees import SP
V=302
SL={'less':'less','dev':'luiza','oh':'adrian','nars':'narsi','tash':'tash','adro':'adro','girl_air':'devushka_airat','fenya':'fenrira','bonny':'bonny','urza':'urza','kap':'kap'}
NAME={'less':'Лесс','dev':'Луиза','oh':'Адриан (Страж)','nars':'Нарси','tash':'Таш','adro':'Адро','girl_air':'Девушка в церкви Айрата','fenya':'Феня','bonny':'Бонни','urza':'Урза','kap':'Капибара'}
THR={'less':(8,-5),'dev':(8,-10),'oh':(8,-10),'tash':(8,-10),'adro':(8,-10),'girl_air':(8,-10),'urza':(100,-100)}
files={}
for f in sorted(glob.glob('/tmp/viy/game/*.rpy')):
    files[f.split('/')[-1]]=open(f,encoding='utf8',errors='ignore').read().split('\n')
def ind(l): return len(l)-len(l.lstrip(' \t'))
chk={};chg={}
FIRST={}
for fn_,ls_ in files.items():
    lb=None
    for l_ in ls_:
        mm_=re.match(r'label (\w+):',l_)
        if mm_: lb=mm_.group(1);continue
        mt=re.match(r'\s*(\w+) "(.*)"\s*$',l_) or re.match(r'\s*()"(.*)"\s*$',l_)
        if lb and lb not in FIRST and mt and not l_.strip().startswith('$'): FIRST[lb]=re.sub(r'\{[^}]*\}','',mt.group(2))[:90]

for fn,ls in files.items():
    lab=None
    for i,l in enumerate(ls):
        m=re.match(r'label (\w+):',l)
        if m: lab=m.group(1)
        t=l.strip()
        m=re.match(r'(?:(?:if|elif|while)\s+(.*)|"[^"]*"\s*if\s+(.*)):\s*$',t)
        cond=(m.group(1) or m.group(2)) if m else None
        if cond:
            for p in set(re.findall(r'\b(\w+)\.mood\b',cond)):
                if p=='self' or p not in NAME: continue
                # consequence: first spoken line in block
                base=ind(l);cons=[]
                for j in range(i+1,min(i+40,len(ls))):
                    if ls[j].strip() and ind(ls[j])<=base: break
                    mm=re.match(r'\s*(\w+) "(.*)"\s*$',ls[j]) or re.match(r'\s*()"(.*)"\s*$',ls[j])
                    if mm and not ls[j].strip().startswith('$'):
                        cons.append((SP.get(mm.group(1),mm.group(1) or 'Рассказчик'),re.sub(r'\{[^}]*\}','',mm.group(2))[:110]))
                        if len(cons)>=2: break
                chk.setdefault(p,[]).append((fn,i+1,lab,cond,cons))
        m=re.search(r'\$\s*(\w+)\.mood\s*(\+=|-=|=)\s*(-?\d+)',l)
        if m and m.group(1) in NAME: chg.setdefault(m.group(1),[]).append((fn,i+1,lab,m.group(2),m.group(3)))
def block(p):
    g,b=THR.get(p,(None,None))
    h='<!--MOOD--><div class="card" id="mood"><h2>Где проверяется настроение</h2>'
    h+='<p>Настроение - число у персонажа (<code>%s.mood</code>), оно растёт и падает от выборов героини. '%p
    if g is not None: h+='По определению персонажа (live2d.rpy:46-48, 405-425) при настроении не ниже %d включается признак «хорошее отношение» (<code>%s.good</code>), при настроении не выше %d - «плохое отношение» (<code>%s.bad</code>); признак, однажды включившись, сам не выключается, а второй уже не включится, пока стоит первый. '%(g,p,b,p)
    h+='Ниже: каждая проверка настроения в коде. Для каждой указано: в какой сцене, какое условие по-русски, какие реплики идут следом в этой ветке (это указатель, не объяснение смысла), и место в коде мелким шрифтом.</p>'
    cs=chk.get(p,[])
    if cs:
        h+='<table><tr><th>Сцена (метка)</th><th>Условие по-русски</th><th>Что идёт в ветке</th></tr>'
        for fn,n,lab,cond,cons in cs:
            h+='<tr><td>%s<code>%s</code><br/><span class="muted"><code>%s:%d</code></span></td><td>%s<br/><small class="muted"><code>%s</code></small></td><td>%s</td></tr>'%(('<i>начало сцены: «%s»</i><br/>'%html.escape(FIRST[lab])) if lab in FIRST else '',lab or '-',fn,n,cond_html(cond).replace('<br/>','; '),html.escape(cond),'<br/>'.join('<b>%s:</b> %s'%(html.escape(a),html.escape(b)) for a,b in cons) or '<span class="muted">реплик в ветке нет (только действия)</span>')
        h+='</table>'
    else: h+='<p>Проверок настроения этого персонажа в условиях кода не найдено.</p>'
    cg=chg.get(p,[])
    h+='<h3>Где настроение меняется напрямую</h3>'
    if cg: h+='<ul>'+''.join('<li>%s: <b>%s%s</b> в сцене <code>%s</code> <span class="muted"><code>%s:%d</code></span></li>'%(NAME[p],{'+=':'+','-=':'-','=':'устанавливается '}[op],v,lab,fn,n) for fn,n,lab,op,v in cg)+'</ul>'
    else: h+='<p class="muted">Прямых изменений вида «%s.mood += N» в коде не найдено; настроение может меняться через общие функции (смысл таких вызовов здесь не разбирался).</p>'%p
    return h+'</div><!--/MOOD-->'
if __name__=='__main__':
    for p,sl in SL.items():
        f='char_%s.html'%sl
        try: s=open(f,encoding='utf8').read()
        except: print('no',f);continue
        if not chk.get(p) and not chg.get(p): continue
        s=re.sub(r'<!--MOOD-->.*?<!--/MOOD-->','',s,flags=re.S)
        s=s.replace('<!--TREE-->',block(p)+'<!--TREE-->',1) if '<!--TREE-->' in s else s.replace('</main>',block(p)+'</main>',1)
        open(f,'w',encoding='utf8').write(s);print(sl,len(chk.get(p,[])),len(chg.get(p,[])))
