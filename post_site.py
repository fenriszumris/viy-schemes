# -*- coding: utf-8 -*-
# idempotent post-processing: row anchors + location links
import re,glob
exec(open('loc_names.py',encoding='utf8').read())
V=267
def rowids(s):
    def f(m):
        return '<tr id="o_%s">'%m.group(2)+m.group(1)
    s=re.sub(r'<tr id="o_\w+">','<tr>',s)
    return re.sub(r'<tr>((?:<td[^>]*>(?:(?!</td>).)*?<code>(\w+)</code>))',f,s,flags=re.S)
def unlink(s): return re.sub(r'<a class="loclink"[^>]*>[^<]*</a><span class="lid"> (\w+)</span>',r'\1',s)
ids=sorted(L,key=len,reverse=True)
pat=re.compile(r'(?<![\w/.#"-])('+'|'.join(ids)+r')(?![\w-])')
def link(s):
    s=unlink(s)
    parts=re.split(r'(<[^>]+>)',s)
    out=[];skip=0;intag=None
    for p in parts:
        if p.startswith('<'):
            t=re.match(r'</?(\w+)',p)
            if t:
                n=t.group(1).lower()
                if n in('a','script','style','title') :
                    skip=0 if p.startswith('</') else 1
                if n=='code':
                    intag=None if p.startswith('</') else 1
            out.append(p);continue
        if skip: out.append(p);continue
        if intag:
            # inside code: only if whole segment equals id
            q=p.strip()
            if q in L: p=p.replace(q,'<a class="loclink" href="locations.html?v=%d#%s">%s</a><span class="lid"> %s</span>'%(V,q,L[q][0],q))
            out.append(p);continue
        out.append(pat.sub(lambda m:'<a class="loclink" href="locations.html?v=%d#%s">%s</a><span class="lid"> %s</span>'%(V,m.group(1),L[m.group(1)][0],m.group(1)),p))
    return ''.join(out)
if __name__=='__main__':
    for f in ['clickables.html','strel.html','location.html']+glob.glob('char_*.html'):
        s=open(f,encoding='utf8').read();n=rowids(s) if f=='clickables.html' else s
        n=link(n)
        if n!=s: open(f,'w',encoding='utf8').write(n);print('upd',f)
