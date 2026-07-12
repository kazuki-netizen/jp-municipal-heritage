import re, json
from bs4 import BeautifulSoup

CATMAP = {
    '建造物': ('有形文化財','建造物'),
    '絵画': ('有形文化財','絵画'),
    '彫刻': ('有形文化財','彫刻'),
    '工芸品': ('有形文化財','工芸品'),
    '書跡': ('有形文化財','書跡'),
    '書跡等': ('有形文化財','書跡'),
    '古文書': ('有形文化財','古文書'),
    '考古資料': ('有形文化財','考古資料'),
    '歴史資料': ('有形文化財','歴史資料'),
    '無形民俗文化財': ('民俗文化財','無形民俗文化財'),
    '有形民俗文化財': ('民俗文化財','有形民俗文化財'),
    '史跡': ('記念物(史跡・名勝・天然記念物)','史跡'),
    '名勝': ('記念物(史跡・名勝・天然記念物)','名勝'),
    '天然記念物': ('記念物(史跡・名勝・天然記念物)','天然記念物'),
}

WAREKI = {'M':1868,'T':1912,'S':1926,'H':1989,'R':2019,
          '明治':1868,'大正':1912,'昭和':1926,'平成':1989,'令和':2019}

def to_iso(s):
    if not s: return None
    s = s.replace('Ｓ','S').replace('Ｈ','H').replace('Ｍ','M').replace('Ｒ','R').replace('Ｔ','T')
    m = re.search(r'([SHMRT])(\d+)年\s*(\d+)月\s*(\d+)日', s)
    if m:
        era, y, mo, d = m.groups()
        year = WAREKI[era] + int(y) - 1
        return f"{year:04d}-{int(mo):02d}-{int(d):02d}"
    m = re.search(r'(明治|大正|昭和|平成|令和)(\d+|元)年(\d+)月(\d+)日', s)
    if m:
        era, y, mo, d = m.groups()
        y = 1 if y=='元' else int(y)
        year = WAREKI[era] + y - 1
        return f"{year:04d}-{int(mo):02d}-{int(d):02d}"
    return None

soup = BeautifulSoup(open('/Users/user/bunkazai/pipeline/cache/滋賀県/moriyama/page.html', encoding='utf-8', errors='ignore'), 'lxml')
tables = soup.find_all('table')
url = "http://moriyama-bunkazai.org/moriyama/spot3/"
out = []
for t in tables:
    rows = t.find_all('tr')
    d = {}
    for r in rows:
        cells = r.find_all(['td','th'])
        if len(cells) >= 2:
            key = cells[0].get_text(strip=True)
            val = cells[1].get_text(' ', strip=True)
            d[key] = val
    if '文化財の種類' not in d or '市指定' not in d['文化財の種類']:
        continue
    name = d.get('名称', '').strip()
    kind_raw = re.sub(r'^市指定', '', d['文化財の種類']).strip()
    if kind_raw not in CATMAP:
        for prefix in ('重要文化財', '文化財'):
            if kind_raw.startswith(prefix):
                cand = kind_raw[len(prefix):].strip()
                if cand in CATMAP:
                    kind_raw = cand
                    break
    cat, subcat = CATMAP.get(kind_raw, (None, kind_raw))
    date_iso = to_iso(d.get('文化財の指定日', ''))
    era = d.get('時代')
    loc = d.get('文化財の所在地')
    desc = f"時代:{era}" if era else None
    out.append({
        "pref": "滋賀県",
        "municipality": "守山市",
        "name": name,
        "category": cat,
        "subcategory": kind_raw,
        "designation": "市指定",
        "designated_date": date_iso,
        "location": loc if loc else None,
        "description": desc,
        "source_url": url,
        "source_format": "html",
        "fetched_at": "2026-07-12T00:00:00Z"
    })

print(len(out))
with open('/Users/user/bunkazai/pipeline/out/滋賀県/moriyama.jsonl', 'w', encoding='utf-8') as f:
    for o in out:
        f.write(json.dumps(o, ensure_ascii=False) + "\n")
nulls = sum(1 for o in out if o['designated_date'] is None)
print('nulls', nulls)
print(set(o['subcategory'] for o in out))
none_cat = [o for o in out if o['category'] is None]
print('none cat', len(none_cat), none_cat[:3])
