from datetime import datetime
BASE = {'明治': 1867, '大正': 1911, '昭和': 1925, '平成': 1988, '令和': 2018}
def wareki(nengo, y, m, d):
    year = BASE[nengo] + (1 if y == '元' else int(y))
    try:
        return f'{datetime(year, int(m), int(d)):%Y-%m-%d}'
    except ValueError:
        return None
