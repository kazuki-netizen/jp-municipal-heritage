import re

def wareki_to_iso(s):
    if not s:
        return None
    s = s.strip()
    m = re.match(r'(明治|大正|昭和|平成|令和)(元|[0-9０-９]+)年(\d{1,2}|[0-9０-９]{1,2})月(\d{1,2}|[0-9０-９]{1,2})日', s)
    if not m:
        # try western
        m2 = re.match(r'(\d{4})[年/-](\d{1,2})[月/-](\d{1,2})日?', s)
        if m2:
            y,mo,d = m2.groups()
            return f"{int(y):04d}-{int(mo):02d}-{int(d):02d}"
        return None
    era, y, mo, d = m.groups()
    y = 1 if y == '元' else int(str(y).translate(str.maketrans('０１２３４５６７８９','0123456789')))
    mo = int(str(mo).translate(str.maketrans('０１２３４５６７８９','0123456789')))
    d = int(str(d).translate(str.maketrans('０１２３４５６７８９','0123456789')))
    base = {'明治':1867,'大正':1911,'昭和':1925,'平成':1988,'令和':2018}[era]
    year = base + y
    return f"{year:04d}-{mo:02d}-{d:02d}"

if __name__ == '__main__':
    tests = ['昭和47年5月15日','平成27年10月7日','令和2年3月10日','平成元年4月1日']
    for t in tests:
        print(t, '->', wareki_to_iso(t))
