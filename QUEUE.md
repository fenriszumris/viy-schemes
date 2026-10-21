QUEUE (Kate via main, 21 Oct 2026), do in order, report only finished verified (live link+screenshot):
1. locations.html: RU names from scenes (loc_names.py, /tmp/locgraph.txt), cards with #id, arrows w/ RU dest links; post-process strel/location/clickables/chars: bare ids -> links to locations.
2. Characters are not clickables rows: tash(Ташир), bonny(+b_head,bonny_x,b_find,head,full_bones), sova, leni, nars, guard1, guard2, kap, cat, girl_air, dev_*, adro_screen, blu, fen_button -> clickables row = link to char page; char page gets "Где на него можно нажать" + "Что на него можно положить" (drop labels list, conditions, results, inventory links). Remaining labels to read: nars x5, kap done partly, adro_kill rest, guard2_diary(stub "123"), bonny_bones_strange (Bonny stalls: 'Ну, это кость... не знаю'), bonny_bonny_x, tash_tash_card.
3. Inventory: replace table with expandable <details> cards per item, no empty fields: with what it combines, where used (inventory + clickable targets), result, links. Do not invent.
4. "см. предмет"/item mentions everywhere -> working links to inventory.html#item.
5. Site-wide: RU main names (no raw screen/label as main names in tables), code in small grey font; unknown RU name -> mark uncertain.
6. Deep clickables branches: dev_button->airat conv, tash_game rest + script3_nazad_tash_razg_2menu, adro_screen suicide_kill.
7. Then character pages enrichment. bugs undefined-var check not done.
Notes: barrier+spalniki done v=261.
