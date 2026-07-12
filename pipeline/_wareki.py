import re

ERA_BASE = {
    '明治': 1868, '大正': 1912, '昭和': 1926, '平成': 1989, '令和': 2019,
}

def wareki_to_iso(s):
    if not s:
        return None
    s = s.strip()
    m = re.match(r'(明治|大正|昭和|平成|令和)(元|\d+)年(\d+)月(\d+)日', s)
    if not m:
        return None
    era, y, mo, d = m.groups()
    y = 1 if y == '元' else int(y)
    year = ERA_BASE[era] + y - 1
    try:
        return f"{year:04d}-{int(mo):02d}-{int(d):02d}"
    except Exception:
        return None

if __name__ == '__main__':
    tests = ['昭和45年3月20日', '令和2年2月28日', '平成元年4月1日', '令和7年7月29日']
    for t in tests:
        print(t, '->', wareki_to_iso(t))
