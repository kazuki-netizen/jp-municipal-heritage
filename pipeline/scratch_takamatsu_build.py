import json, re, subprocess

SP = '/private/tmp/claude-501/-Users-miyazakihitohata/3df58887-c317-49b8-ac70-21b70159396b/scratchpad'
CWD = '/Users/miyazakihitohata/bunkazai/pipeline'
FETCHED = '2026-07-12T18:20:00Z'
BASE = 'https://www.city.takamatsu.kagawa.jp/kurashi/kosodate/bunka/bunkazai/shiteibunkazai'

SUBS = {
 'chokoku': ('彫刻', BASE + '/chokoku/index.html'),
 'kaiga': ('絵画', BASE + '/kaiga/index.html'),
 'kenzo': ('建造物', BASE + '/kenzo/index.html'),
 'kogeihin': ('工芸品', BASE + '/kogeihin/index.html'),
 'koko': ('考古資料', BASE + '/koko/index.html'),
 'komonjo': ('古文書', BASE + '/komonjo/index.html'),
 'meisho': ('名勝', BASE + '/meisho/index.html'),
 'mukei': ('無形文化財', BASE + '/mukei/index.html'),
 'mukei_minzoku': ('無形民俗文化財', BASE + '/mukei_minzoku/index.html'),
 'shiseki': ('史跡', BASE + '/shiseki/index.html'),
 'shoseki': ('書跡', BASE + '/shoseki/index.html'),
 'tennen': ('天然記念物', BASE + '/tennen/index.html'),
 'yukei_minzoku': ('有形民俗文化財', BASE + '/yukei_minzoku/index.html'),
}
REKISHI_SRC = 'https://www.city.takamatsu.kagawa.jp/kurashi/kosodate/bunka/bunkazai/shiteibunkazai/rekishi/index.html'

CAT_MAP = {
 '彫刻': ('有形文化財', '彫刻'),
 '絵画': ('有形文化財', '絵画'),
 '建造物': ('有形文化財', '建造物'),
 '工芸品': ('有形文化財', '工芸品'),
 '考古資料': ('有形文化財', '考古資料'),
 '古文書': ('有形文化財', '古文書'),
 '名勝': ('記念物(史跡・名勝・天然記念物)', '名勝'),
 '無形文化財': ('無形文化財', '無形文化財'),
 '無形民俗文化財': ('民俗文化財', '無形民俗文化財'),
 '史跡': ('記念物(史跡・名勝・天然記念物)', '史跡'),
 '書跡': ('有形文化財', '書跡'),
 '天然記念物': ('記念物(史跡・名勝・天然記念物)', '天然記念物'),
 '有形民俗文化財': ('民俗文化財', '有形民俗文化財'),
 '歴史資料': ('有形文化財', '歴史資料'),
}

def h2t(path):
    return subprocess.run(['python3', '_h2t.py', path], cwd=CWD, capture_output=True, text=True).stdout

def parse_table(text):
    lines = text.split('\n')
    tables = []
    i = 0
    while i < len(lines):
        if lines[i] == '=== TABLE ===':
            j = lines.index('=== /TABLE ===', i)
            tables.append(lines[i+1:j])
            i = j
        i += 1
    return tables

results = []

def add_row(row_str, subcat_label, src_url):
    parts = [p.strip() for p in row_str.split('|')]
    if len(parts) < 4:
        return
    num, kubun, name, loc = parts[0], parts[1], parts[2], parts[3]
    if not kubun.startswith('市指定'):
        return  # exclude 市登録, 県指定, 国指定, 重要文化財, 国宝, 特別史跡, 特別名勝
    cat, subcat = CAT_MAP.get(subcat_label, (None, subcat_label))
    results.append({
        "pref": "香川県", "municipality": "高松市", "name": name,
        "category": cat, "subcategory": subcat, "designation": "市指定",
        "designated_date": None, "location": loc or None,
        "description": None,
        "source_url": src_url, "source_format": "html", "fetched_at": FETCHED,
    })

# rekishi (already cached)
text = h2t('cache/香川県/takamatsu/d02e44089f251ab3.html')
for t in parse_table(text):
    for row in t[1:]:
        add_row(row, '歴史資料', REKISHI_SRC)

for sub, (label, url) in SUBS.items():
    path = f'{SP}/takamatsu_{sub}.html'
    text = h2t(path)
    for t in parse_table(text):
        for row in t[1:]:
            add_row(row, label, url)

with open(f'{CWD}/out/香川県/takamatsu.jsonl', 'w') as f:
    for r in results:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
print(len(results))
