import json, re

SUB_MAP = {
    '有形文化財（建造物）': ('有形文化財', '建造物'),
    '有形文化財（彫刻）': ('有形文化財', '彫刻'),
    '有形文化財（絵画）': ('有形文化財', '絵画'),
    '有形文化財（工芸品）': ('有形文化財', '工芸品'),
    '有形文化財（古文書）': ('有形文化財', '古文書'),
    '有形文化財（考古資料）': ('有形文化財', '考古資料'),
    '有形文化財（歴史資料）': ('有形文化財', '歴史資料'),
    '無形文化財': ('無形文化財', None),
    '民俗文化財（有形）': ('民俗文化財', '有形民俗文化財'),
    '民俗文化財（無形）': ('民俗文化財', '無形民俗文化財'),
    '記念物（史跡）': ('記念物', '史跡'),
    '記念物（名勝）': ('記念物', '名勝'),
    '記念物（天然記念物）': ('記念物', '天然記念物'),
}

txt = open('/tmp/kirishima.txt', encoding='utf-8').read()
start = txt.index('市指定文化財')
end = txt.index('国登録文化財')
body = txt[start + len('市指定文化財'):end]

lines = [l for l in body.split('\n') if l.strip()]

records = []
cat = sub = None
i = 0
while i < len(lines):
    l = lines[i]
    if l in SUB_MAP:
        cat, sub = SUB_MAP[l]
        i += 1
        continue
    # name line, next line is (region) in parens
    name = l
    region = None
    if i + 1 < len(lines) and re.match(r'^（.+）$', lines[i + 1]):
        region = lines[i + 1].strip('（）')
        i += 2
    else:
        i += 1
    records.append({
        'pref': '鹿児島県', 'municipality': '霧島市', 'name': name,
        'category': cat, 'subcategory': sub, 'designation': '市指定',
        'designated_date': None, 'location': region,
        'description': None,
        'source_url': 'https://www.city-kirishima.jp/bunka/kyoiku/rekishi/bunkazai/shitebunkazai/bunkazai-itirannhyou.html',
        'source_format': 'html', 'fetched_at': '2026-07-12T10:59:00Z',
    })

with open('out/鹿児島県/kirishima.jsonl', 'w', encoding='utf-8') as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
print(len(records))
for r in records:
    print(r['name'], r['category'], r['subcategory'], r['location'])
