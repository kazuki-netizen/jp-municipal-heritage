import json

SRC = 'https://www.town.okuizumo.shimane.jp/kosodate-kyoiku/kyoiku/bunkazai/1555547408973.html'
FETCHED = '2026-07-12T06:55:33Z'

# (name, category, subcategory, note)
items = [
("青木實三郎図画教育指導画","有形文化財","美術工芸品","大正から昭和初期の図画教育指導画"),
("忠貞作日本刀","有形文化財","美術工芸品","三沢氏時代の刀工代表作"),
("大源寺跡宝篋印塔","有形文化財","美術工芸品","1370年前後と推定される花崗岩製の石塔"),
("カネツキ免遺跡出土品","有形文化財","美術工芸品","奈良時代後期(大型円面硯・墨書土器他出土)、奥出雲多根自然博物館で展示中"),
("京ヶ崎銅製経筒","有形文化財","美術工芸品",None),
("双子谷野鈩跡及びケラ塊","記念物(史跡・名勝・天然記念物)","史跡","中世野鈩およびケラ"),
("岩屋古墳","記念物(史跡・名勝・天然記念物)","史跡","仁多郡内最大級の横穴式石室を持つ古墳時代後期の円墳"),
("亀石高殿鈩跡","記念物(史跡・名勝・天然記念物)","史跡","卜蔵家の近世鈩跡"),
("原たたら跡（叢雲たたら）","記念物(史跡・名勝・天然記念物)","史跡","かつて卜蔵家の主力鈩（昭和13年から終戦まで叢雲鈩）"),
("旧卜蔵氏庭園","記念物(史跡・名勝・天然記念物)","名勝","近世の有力鉄師卜蔵家が江戸初期に作庭した住宅庭園"),
("湯野神社大けやき","記念物(史跡・名勝・天然記念物)","天然記念物","樹齢400年"),
("蔵元のアカガシ","記念物(史跡・名勝・天然記念物)","天然記念物","樹高15m、幹周り4.7m"),
("前二ノ宮のクスノキ","記念物(史跡・名勝・天然記念物)","天然記念物","樹高25m、幹周り5.5m"),
("雲崎のインヨウチク自生地","記念物(史跡・名勝・天然記念物)","天然記念物","タケとササの交雑種"),
("羽内谷鉱山鉄穴流し本場設備","民俗文化財","有形民俗文化財","全国最後となる昭和47年まで稼業した本場設備の遺構"),
]

results = []
for name, cat, subcat, note in items:
    results.append({
        "pref": "島根県", "municipality": "奥出雲町", "name": name,
        "category": cat, "subcategory": subcat, "designation": "町指定",
        "designated_date": None, "location": None, "description": note,
        "source_url": SRC, "source_format": "html", "fetched_at": FETCHED,
    })

with open('/Users/miyazakihitohata/bunkazai/pipeline/out/島根県/okuizumo.jsonl', 'w') as f:
    for r in results:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
print(len(results))
