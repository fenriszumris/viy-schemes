import re
s=open('inventory.html',encoding='utf8').read()
def f(m):
    return '<details class="inv" id="i_%s"><summary>%s'%(m.group(3),m.group(2))
s=re.sub(r'<details class="inv"(?: id="i_\w+")?><summary>((?:(?!</summary>).)*?class="rid">(\w+) ·.*?)(?=</summary>)',lambda m:'<details class="inv" id="i_%s"><summary>%s'%(m.group(2),m.group(1)),s,flags=re.S)
open('inventory.html','w',encoding='utf8').write(s);print(s.count('id="i_'))
