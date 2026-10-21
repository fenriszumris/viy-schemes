QUEUE (Kate via main, 21 Oct 2026), do in order, report only finished verified (live link+screenshot):
1. locations.html: RU names from scenes (loc_names.py, /tmp/locgraph.txt), cards with #id, arrows w/ RU dest links; post-process strel/location/clickables/chars: bare ids -> links to locations.
2. Characters are not clickables rows: tash(Ташир), bonny(+b_head,bonny_x,b_find,head,full_bones), sova, leni, nars, guard1, guard2, kap, cat, girl_air, dev_*, adro_screen, blu, fen_button -> clickables row = link to char page; char page gets "Где на него можно нажать" + "Что на него можно положить" (drop labels list, conditions, results, inventory links). Remaining labels to read: nars x5, kap done partly, adro_kill rest, guard2_diary(stub "123"), bonny_bones_strange (Bonny stalls: 'Ну, это кость... не знаю'), bonny_bonny_x, tash_tash_card.
3. Inventory: replace table with expandable <details> cards per item, no empty fields: with what it combines, where used (inventory + clickable targets), result, links. Do not invent.
4. "см. предмет"/item mentions everywhere -> working links to inventory.html#item.
5. Site-wide: RU main names (no raw screen/label as main names in tables), code in small grey font; unknown RU name -> mark uncertain.
6. Deep clickables branches: dev_button->airat conv, tash_game rest + script3_nazad_tash_razg_2menu, adro_screen suicide_kill.
7. Then character pages enrichment. bugs undefined-var check not done.
Notes: barrier+spalniki done v=261.
8. FULL RE-AUDIT of items and clickables vs code (Kate: "перепроверить вещи и кликабельные"; main: no selective-check completeness claims). Per object: all actions (click/look/take/go/drag), all menu choices, damage (blood/add_mad/mood), conditions, destinations, combos. Done so far: barrier, less_spal, табличка less_ter (choice, no blood counter), dev_door2 (click exits to airat_left), mant, lupa_button, sova, girl_air, adro_screen verified OK. Audit labels flagged with menu/mood: girl_osm ok; still check: dev_sleep(script_3_road_dev_airat2), tash_start_razg, start_osm1/less_osm, all drag labels, every inventory item. Keep unresolved gaps explicit.
Done so far: loc_names.py; locations.html NOT built yet.
9. Kate: "И кар. И нарс тоже", "Лени тоже" -> characters. kar (door kar_air: check kar_door_screen vs Карралак char page, don't guess) and nars. Characters need TALK TREES (replicas, answer options, conditions, consequences) on char pages. char_clicks.py builds click+drop sections; run order: apply_clk.py(NO, would overwrite rows) -> char_clicks.py -> post_site.py -> build_locs.py. Bump ?v= with sed (also V in scripts).
build: sh build_all.sh (never rerun apply_clk.py); then sed bump v and V in *.py
done: item links (post_site ilink), RU conditions in trees, unified drag list.
STATE 9:40: v=273 pushed. Done: locations, char click/drop sections, trees(tash,luiza,bonny,less,fen,nars) w/ RU conditions, inventory unified drag list, item links, Karralak related door. TODO next: RU names for objects/screens in clickables columns (Экран col, object code names -> RU), trees for leni/adro/kap/sova/others (dialogues not via razg_menu: use trees.render on their entry labels e.g. script_4_airat_leni_dialog), finish unread drop labels (nars igla etc), deep clickables sub-branches, remaining object audit (dev_sleep, tash_start_razg, less_osm), bugs undefined-var check. Report to main only after verifying live (no 'через 1-2 мин').
9:45: flags explained via setting sites (condru). Remaining unexplained: 'смысл не расшифрован' atoms like mad_l()/logic_l(): replace by reading defs.
9:46 fixed sova ratio (logic share). cond RU extended.
9:48 flags now list all set/reset sites, meaning not claimed.

## 9:57 new (Kate via main)
- DONE v281: guards trees, Блю (renamed), Губерт (char_slime renamed, tree), Кап page exists, Adro cabinet inspection on locations #tgavan_sar_cab with game images (sarcab.py).
- TODO site-wide: everywhere code is shown, main content must be Russian explanation, code only small hint. Mood checks (настроение/mood): per check explain scene, whose indicator, threshold, what depends. Items "где получается и зачем" in Russian prose, no raw labels. Audit all pages (strel, bugs, replics, scheme pages) for raw code as main text.
- Unknown meaning stays explicit gap.

## 10:11 status v289
- DONE: trees as per-branch flowcharts (tree_graph.py, lazy render), compact rounded cond blocks (condru.cond_html, SHORT mode+LEG legend), logic_l/mad_l thresholds from script.rpy:126-145, dev_leni meaning (condru.MEAN), cabinet renamed "Кабинет Адро (кабинет Лиассона...)".
- TODO next: mood-check section per character (scene, whose indicator, threshold, what depends; mood>=v_good(8) -> .good, <=n_bad -> .bad; less n_bad -5, others -10; oh=Адриан/Страж, adro, dev, nars). Script /tmp/m.py lists 34 mood conditions.
- TODO: site-wide code->Russian pass (strel, bugs, replics), items "где получается и зачем", remaining ~50 unknown flag conditions, final established vs undeciphered summary.

10:20 v297 live: derived flag meanings (condru derive + MEAN for tea/cap/dv/vinp), trees use plain-text conditions. Still unresolved: persistent.memory, tash_game, script3_tash_cards_per, sovet_kap, quests _note reward, hod_per, my_cards. Next: inventory prose x27, trees kar/urza/kai/cat/girl, bugs undefined-vars, final audit, Cloudflare prep. No report to main yet (needs screenshot, bundle with next).
10:27 v299: all char talk trees replaced with choice_tree.py (collapsible, choices only, no replies, no mermaid/links). Kate asked this for Leni.
10:35 v302: Leni = hub diagram (hub_tree.py/hub_embed.py); others restored to cards. Main rejected v299 (accordion). Do NOT convert other chars until Kate decides. Next: inventory prose, undefined vars, final audit, Cloudflare prep.
