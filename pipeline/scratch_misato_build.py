import json, sys
sys.path.insert(0, '/Users/user/bunkazai/pipeline')
from scratch_oda_build import wareki_oda

CAT_MAP = {
 '絵画': ('有形文化財','絵画'), '彫刻': ('有形文化財','彫刻'), '工芸品': ('有形文化財','工芸品'),
 '無形の民俗文化財': ('民俗文化財','無形民俗文化財'),
 '史跡': ('記念物(史跡・名勝・天然記念物)','史跡'),
 '天然記念物': ('記念物(史跡・名勝・天然記念物)','天然記念物'),
}

SRC = 'https://gov.town.shimane-misato.lg.jp/files/original/202401041206483096c421309.pdf'
FETCHED = '2026-07-12T06:55:44Z'

# (subcat, date, name, loc, owner, note)
rows = [
('絵画','昭52.11.30','絹本著色霊峰冨士乃図・絹本著色晩秋乃群鹿図','潮村','個人','日本画家・中原芳煙（1875-1915）筆'),
('彫刻','平14.12.26','尾原家の欄間と明かり障子','簗瀬','美郷町','室町時代'),
('彫刻','平16.9.1','木彫狛犬','宮内','田立建埋根命神社','永和3年在銘'),
('工芸品','平14.12.26','鰐口','信喜','多聞寺（毘沙門堂）','備中洲新見荘熊野権現鐘也應安六年歳次癸丑五月初八日願主靭久光の銘あり'),
('無形の民俗文化財','昭51.6.26','大和神楽「神迎･鐘馗の舞」','都賀本郷','大和神楽団',None),
('無形の民俗文化財','平16.9.1','都賀西神楽「山伏」','都賀西','都賀西神楽保存会',None),
('無形の民俗文化財','平16.9.1','都神楽「天の岩戸」','都賀行','都神楽団',None),
('史跡','平14.12.26','沖丈遺跡','乙原','島根県','約2,000㎡'),
('天然記念物','昭51.6.26','田立建理根命神社樫ノ木','宮内','田立建理根命神社','推定樹齢600年、胸高回5.0ｍ、根回7.9ｍ'),
('天然記念物','平14.12.26','別府八幡宮の大スギ','別府','別府八幡宮','推定樹齢400年、胸高回6.2ｍ、根回30ｍ'),
('天然記念物','平25.2.4','シダレザクラ','九日市','美郷町','推定樹齢120年、胸高周囲2.5ｍ、樹高約15ｍ'),
]

results = []
for subcat, date, name, loc, owner, note in rows:
    cat, _ = CAT_MAP[subcat]
    iso = wareki_oda(date)
    desc_parts = [f'所有者・保持者{owner}']
    if note:
        desc_parts.append(note)
    desc = '、'.join(desc_parts)
    results.append({
        "pref": "島根県", "municipality": "美郷町", "name": name,
        "category": cat, "subcategory": subcat, "designation": "町指定",
        "designated_date": iso, "location": loc or None, "description": desc,
        "source_url": SRC, "source_format": "pdf", "fetched_at": FETCHED,
    })

with open('/Users/user/bunkazai/pipeline/out/島根県/misato.jsonl', 'w') as f:
    for r in results:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
print(len(results))
