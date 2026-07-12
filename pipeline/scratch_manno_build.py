import json, sys
sys.path.insert(0, '/Users/miyazakihitohata/bunkazai/pipeline')
from scratch_shimane_wareki import wareki_to_iso

FETCHED = '2026-07-12T23:00:00Z'
BASE = 'https://www.town.manno.lg.jp/site/bunkazai'

CAT = {
 '建造物': ('有形文化財','建造物'),
 '絵画': ('有形文化財','絵画'),
 '彫刻': ('有形文化財','彫刻'),
 '書跡': ('有形文化財','書跡'),
 '考古資料': ('有形文化財','考古資料'),
 '無形民俗文化財': ('民俗文化財','無形民俗文化財'),
 '天然記念物': ('記念物(史跡・名勝・天然記念物)','天然記念物'),
}

# (id, name, subcat, loc, date_raw)
rows = [
 (4520,'金剛寺十三重塔','建造物','まんのう町炭所東','平成22年11月30日'),
 (4521,'絹本著色阿弥陀三尊像','絵画',None,'昭和59年8月1日'),
 (4522,'絹本著色阿弥陀如来像','絵画',None,'平成9年7月1日'),
 (4524,'木造地蔵菩薩立像','彫刻',None,'昭和58年3月24日'),
 (4525,'木造薬師如来立像','彫刻',None,'昭和58年3月24日'),
 (4526,'木造薬師如来坐像','彫刻',None,'平成19年2月27日'),
 (4527,'蓮如筆執持鈔文（紙本墨書）','書跡',None,'平成9年7月1日'),
 (4530,'金剛寺遺物','考古資料','まんのう町炭所東','平成21年3月31日'),
 (4532,'弘安寺廃寺遺物','考古資料','まんのう町四条','平成22年3月31日'),
 (4533,'佐岡遺跡出土銅剣','考古資料','まんのう町長尾','平成29年11月28日'),
 (4534,'三島神社湯立神楽','無形民俗文化財','まんのう町長尾','平成18年3月13日'),
 (4535,'生間のイスノキ','天然記念物','まんのう町生間','平成24年2月29日'),
 (4536,'山脇、香川家のツバキ','天然記念物','まんのう町山脇','平成24年2月29日'),
 (4724,'安造田東3号墳遺物','考古資料','まんのう町羽間','平成19年11月30日'),
 (4727,'四つ足堂','建造物','まんのう町勝浦','平成18年2月10日'),
 (4728,'十三仏笠塔婆','建造物','まんのう町四条','平成14年3月19日'),
 (5356,'下福家のモミジ','天然記念物','まんのう町勝浦','令和7年2月26日'),
]

results = []
for id_, name, subcat, loc, date_raw in rows:
    cat, sc = CAT[subcat]
    iso = wareki_to_iso(date_raw)
    results.append({
        "pref": "香川県", "municipality": "まんのう町", "name": name,
        "category": cat, "subcategory": sc, "designation": "町指定",
        "designated_date": iso, "location": loc, "description": None,
        "source_url": f'{BASE}/{id_}.html', "source_format": "html", "fetched_at": FETCHED,
    })

with open('/Users/miyazakihitohata/bunkazai/pipeline/out/香川県/manno.jsonl', 'w') as f:
    for r in results:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
print(len(results))
print('null dates:', [r['name'] for r in results if r['designated_date'] is None])
