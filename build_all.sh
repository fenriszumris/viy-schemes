cd /tmp/sch
python3 char_clicks.py && python3 rowtitles.py && python3 char_trees.py >/dev/null && python3 moods.py >/dev/null && python3 build_inv_use.py && python3 post_site.py >/dev/null && python3 sarcab.py
python3 build_locs.py
python3 quests_page.py >/dev/null
python3 flags_page.py >/dev/null
