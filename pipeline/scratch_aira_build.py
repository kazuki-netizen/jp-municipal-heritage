import json, re, os
from bs4 import BeautifulSoup

CACHE = 'cache/鹿児島県/aira'
manifest = json.load(open(f'{CACHE}/manifest.json'))
url_by_hash = manifest

FILES = {
    'shisiteisiseki.html': ('史跡', '記念物', '史跡', 61),
    'yuukeiminnzoku.html': ('有形民俗文化財', '民俗文化財', '有形民俗文化財', None),
    'mukeiminnzoku.html': ('無形民俗文化財', '民俗文化財', '無形民俗文化財', None),
    'tennenkinenbutu.html': ('天然記念物', '記念物', '天然記念物', None),
    'shishitei.html': (None, None, None, None),  # top hub, skip parsing items
}

TAG_RE = re.compile(r'〔市指定(.+?)〕')

records = []
for h, entry in manifest.items():
    if entry.get('http_status') != 200 or entry.get('format') != 'html':
        continue
    url = entry['url']
    tail = url.rsplit('/', 1)[-1]
    if tail not in FILES or tail in ('shishitei.html', 'shisihiteiyuukei.html'):
        continue
    label, cat_default, sub_default, total = FILES[tail]
    path = f"{CACHE}/{entry['filename']}"
    soup = BeautifulSoup(open(path, errors='ignore').read(), 'html.parser')
    txt = soup.get_text('\n', strip=True)
    lines = [l for l in txt.split('\n')]
    # locate content start (after 'ここから本文です。') and end (before '県・国指定文化財' or 'お問い合わせ')
    try:
        start = next(i for i, l in enumerate(lines) if l == 'ここから本文です。')
    except StopIteration:
        continue
    end_markers = ['県・国指定文化財', 'お問い合わせ']
    end = len(lines)
    for i in range(start, len(lines)):
        if lines[i] in end_markers:
            end = i
            break
    body = lines[start:end]
    text_body = '\n'.join(body)
    # split into blocks at lines containing the tag
    idxs = [i for i, l in enumerate(body) if TAG_RE.search(l)]
    for j, i in enumerate(idxs):
        line = body[i]
        m = TAG_RE.search(line)
        tag = m.group(1)
        name = line[:m.start()].strip()
        block_end = idxs[j + 1] if j + 1 < len(idxs) else len(body)
        block = body[i + 1:block_end]
        # drop the '（JPG：...）' caption line if present
        block = [l for l in block if not re.match(r'^（[A-Z]+[：:]', l)]
        loc = None
        desc_lines = []
        k = 0
        while k < len(block):
            if block[k].startswith('所在地'):
                if k + 1 < len(block):
                    loc = block[k + 1].split('（外部サイトへリンク）')[0].strip()
                break
            if block[k] == 'ページの先頭へ戻る':
                break
            desc_lines.append(block[k])
            k += 1
        cat, sub = cat_default, sub_default
        if tag != label and tag:
            sub = tag
            if '有形' in tag and '民俗' not in tag:
                cat = '有形文化財'
            elif '無形' in tag and '民俗' not in tag:
                cat = '無形文化財'
            elif '民俗' in tag:
                cat = '民俗文化財'
            elif tag in ('史跡', '名勝', '天然記念物'):
                cat = '記念物'
        records.append({
            'pref': '鹿児島県', 'municipality': '姶良市', 'name': name,
            'category': cat, 'subcategory': sub, 'designation': '市指定',
            'designated_date': None, 'location': loc,
            'description': '；'.join(desc_lines) or None,
            'source_url': url, 'source_format': 'html',
            'fetched_at': entry.get('fetched_at'),
        })

with open('out/鹿児島県/aira.jsonl', 'w', encoding='utf-8') as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
print(len(records))
for r in records:
    print(r['name'], '|', r['category'], r['subcategory'], '|', r['location'])
