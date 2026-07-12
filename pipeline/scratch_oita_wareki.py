import re

ERA_START = {'明治': 1868, '大正': 1912, '昭和': 1926, '平成': 1989, '令和': 2019}

def wareki_to_iso(s):
    if not s:
        return None
    s = s.strip()
    s = s.translate(str.maketrans('０１２３４５６７８９．〇', '0123456789.0'))
    if s in ('なし', '-', '−', '', '未詳', '不詳'):
        return None
    m = re.match(r'(明治|大正|昭和|平成|令和)(元|\d+)\s*[年\.]\s*(\d+)\s*[月\.]\s*(\d+)?\s*日?', s)
    if m:
        era, y, mo, d = m.groups()
        y = 1 if y == '元' else int(y)
        mo = int(mo)
        d = int(d) if d else 1
        year = ERA_START[era] + y - 1
        try:
            iso = f'{year:04d}-{mo:02d}-{d:02d}'
        except Exception:
            return None
        if iso > '2026-07-10':
            return None
        return iso
    # already western e.g. 2021.3.26 or 2021-03-26
    m2 = re.match(r'(\d{4})[-\./](\d{1,2})[-\./](\d{1,2})', s)
    if m2:
        y, mo, d = (int(x) for x in m2.groups())
        iso = f'{y:04d}-{mo:02d}-{d:02d}'
        if iso > '2026-07-10':
            return None
        return iso
    # short abbreviated era e.g. 令2.3.19 / 平31.3.19 / 昭44.11.3
    m3 = re.match(r'(明|大|昭|平|令)\s*(元|\d+)\s*\.\s*(\d+)\s*\.\s*(\d+)', s)
    if m3:
        era_c, y, mo, d = m3.groups()
        era_map = {'明': '明治', '大': '大正', '昭': '昭和', '平': '平成', '令': '令和'}
        era = era_map[era_c]
        y = 1 if y == '元' else int(y)
        mo = int(mo); d = int(d)
        year = ERA_START[era] + y - 1
        try:
            iso = f'{year:04d}-{mo:02d}-{d:02d}'
        except Exception:
            return None
        if iso > '2026-07-10':
            return None
        return iso
    return None

if __name__ == '__main__':
    tests = ['昭和44年11月3日', '平成7年3月28日', '令和5年7月27日', '令2.3.19', '平31.3.19', 'なし', '2021.3.26']
    for t in tests:
        print(t, '->', wareki_to_iso(t))
