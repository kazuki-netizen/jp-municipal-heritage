import re

ERA_START = {
    '明治': 1868,
    '大正': 1912,
    '昭和': 1926,
    '平成': 1989,
    '令和': 2019,
}

KANNUM = {'元':1,'〇':0,'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'十':10}

def wareki_to_iso(s):
    if not s:
        return None
    s = s.strip()
    if s in ('なし', '-', '−', '', 'unknown'):
        return None
    m = re.match(r'(明治|大正|昭和|平成|令和)(元|\d+)年(\d+)月(\d+)?日?', s)
    if not m:
        return None
    era, y, mo, d = m.groups()
    y = 1 if y == '元' else int(y)
    year = ERA_START[era] + y - 1
    mo = int(mo)
    d = int(d) if d else 1
    try:
        return f'{year:04d}-{mo:02d}-{d:02d}'
    except Exception:
        return None

if __name__ == '__main__':
    tests = ['昭和28年8月31日', '平成元年7月1日', '平成元年7月1', '令和5年8月18日', 'なし', '平成8年3月1']
    for t in tests:
        print(t, '->', wareki_to_iso(t))
