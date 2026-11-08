# -*- coding: utf-8 -*-
# Добавляет к каждому месту в inventory.html русское пояснение сцены по соседним строкам кода. Запуск: python3 enrich_inv.py /путь/game
import re,sys,os,html
G=sys.argv[1]
cache={}
def lines(f):
    if f not in cache:
        cache[f]=open(os.path.join(G,f),encoding='utf8',errors='ignore').read().split('\n')
    return cache[f]
dlg=re.compile(r'^\s+(?:[a-z_0-9]+|centered)\s+"(.+?)"\s*(?:with .*)?$')
chs=re.compile(r'^\s+"(.+?)"(?:\s+if .+)?:\s*$')
def ctx(f,n):
    L=lines(f); i=min(n-1,len(L)-1)
    label=None
    for j in range(i,-1,-1):
        m=re.match(r'^label\s+([A-Za-z0-9_.]+)',L[j])
        if m: label=m.group(1); break
    said=None; choice=None
    for j in range(i,max(-1,i-25),-1):
        if choice is None:
            m=chs.match(L[j])
            if m and j<i+1: choice=m.group(1)
        if said is None:
            m=dlg.match(L[j])
            if m and j<=i: said=m.group(1)
        if said and choice: break
    parts=[]
    if label: parts.append('сцена <code>%s</code>'%html.escape(label))
    if choice: parts.append('выбор «%s»'%html.escape(choice[:70]))
    if said: parts.append('рядом в сцене звучит: «%s»'%html.escape(said[:110]))
    return '; '.join(parts)
s=open('inventory.html',encoding='utf8').read()
s=re.sub(r' <span class="why">.*?</span>','',s)
def li(m):
    f,n=m.group(2),int(m.group(3))
    c=ctx(f,n)
    if not c: return m.group(0)
    return m.group(1)+m.group(2)+':'+m.group(3)+'</a> <span class="why">'+c+'.</span> '+m.group(4)
s=re.sub(r'(<li><a href="[^"]+">)([^<:]+\.rpy):(\d+)</a> (<code>)',lambda m:li(re.match(r'(.*)',m.group(0)) and type('M',(),{'group':lambda self,k:[m.group(0),m.group(1),m.group(2),m.group(3),m.group(4)][k]})()),s)
if '.why{' not in s:
    s=s.replace('</head>','<style>.why{font-size:14px;color:#1f2937;display:block;margin:2px 0}</style></head>',1)
open('inventory.html','w',encoding='utf8').write(s)
