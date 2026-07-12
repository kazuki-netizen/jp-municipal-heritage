import json, re, subprocess, sys
sys.path.insert(0, '.')
from scratch_oita_wareki import wareki_to_iso

out = subprocess.run(['python3', '_h2t.py', 'cache/大分県/usa/778f89baae117973.html'],
                      capture_output=True, text=True).stdout
lines = out.split('\n')
tables = []
i = 0
while i < len(lines):
    if lines[i] == '=== TABLE ===':
        j = lines.index('=== /TABLE ===', i)
        tables.append(lines[i+1:j])
        i = j+1
    else:
        i += 1

t3 = tables[3]  # 市指定 table (国=tables[1], 県=tables[2] presumably; verify below)

SRC = 'https://www.city.usa.oita.jp/sougo/soshiki/18/shakaikyoiku/3/bunkazai/2149.html'
manifest = json.load(open('cache/大分県/usa/manifest.json'))
FETCHED = list(manifest.values())[0]['fetched_at']

SECTION_MAP = {
    '有形文化財': '有形文化財',
    '有形民俗文化財': ('民俗文化財', '有形民俗文化財'),
    '無形民俗文化財': ('民俗文化財', '無形民俗文化財'),
    '史 跡': ('記念物(史跡・名勝・天然記念物)', '史跡'),
    '天然記念物': ('記念物(史跡・名勝・天然記念物)', '天然記念物'),
}
EXCLUDE_SECTIONS = {'登録有形文化財', '登録 史跡', '選択 無形民俗文化財'}

results = []
cur_section = None
for line in t3:
    if '|' not in line:
        sec = line.strip()
        if sec in SECTION_MAP:
            cur_section = sec
        elif sec in EXCLUDE_SECTIONS:
            cur_section = None  # skip subsequent rows until next known section
        continue
    if cur_section is None:
        continue
    cells = [c.strip() for c in line.split('|')]
    if len(cells) < 4 or cells[0] == 'No':
        continue
    no, name, date_raw, owner = cells[0], cells[1], cells[2], cells[3]
    if not re.match(r'^\d+$', no):
        continue
    name = re.sub(r'（\d+）$|\(\d+\)$', '', name).strip()
    # date may have multiple dates (追加指定 etc) - take first
    date_first = re.split(r'(?<=日)', date_raw)[0]
    date = wareki_to_iso(date_first)
    mapping = SECTION_MAP[cur_section]
    if cur_section == '有形文化財':
        cat, subcat = '有形文化財', '有形文化財'
    else:
        cat, subcat = mapping
    desc = f'指定番号{no}号'
    if owner:
        desc += f'、所有者等: {owner}'
    results.append({
        "pref": "大分県", "municipality": "宇佐市", "name": name,
        "category": cat, "subcategory": subcat, "designation": "市指定",
        "designated_date": date, "location": None, "description": desc,
        "source_url": SRC, "source_format": "html", "fetched_at": FETCHED,
    })

with open('out/大分県/usa.jsonl', 'w') as f:
    for r in results:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')

print('total:', len(results))
from collections import Counter
print(Counter((r['category'], r['subcategory']) for r in results))
print('nulls date:', sum(1 for r in results if r['designated_date'] is None))
