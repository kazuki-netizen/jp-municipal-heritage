import json

CAT_MAP = {
 '史跡': ('記念物(史跡・名勝・天然記念物)','史跡'),
 '天然記念物': ('記念物(史跡・名勝・天然記念物)','天然記念物'),
 '無形民俗文化財': ('民俗文化財','無形民俗文化財'),
 '古文書': ('有形文化財','古文書'),
 '工芸品': ('有形文化財','工芸品'),
 '考古資料': ('有形文化財','考古資料'),
}

SRC = 'https://www.iinan.jp/site/history/5318.html'
FETCHED = '2026-07-12T06:55:34Z'

items = [
("琴引山及び由來八幡宮","史跡","頓原"),
("比丘尼塚古墳","史跡","ハ神"),
("大万木山の自然林(ブナ)","天然記念物","頓原"),
("八幡宮の大杉","天然記念物","頓原"),
("大なんてん","天然記念物","角井"),
("角井八幡宮の御田植行事","無形民俗文化財","角井"),
("飯石郡小田村御検地帳","古文書","上赤名"),
("飯石郡野萱村御検地帳","古文書","上赤名"),
("飯石郡上来島村御検地帳","古文書","上赤名"),
("飯石郡下来島村御検地帳","古文書","上赤名"),
("長者原古墳","史跡","下赤名"),
("赤穴家文書","古文書","上赤名"),
("泉原たたら跡","史跡","都加賀"),
("坂本難波家文書","古文書","上来島"),
("貝正近作刀","工芸品","上来島"),
("越道難波家文書","古文書","谷"),
("大元杉","天然記念物","上赤名"),
("銀杏と杉の連理","天然記念物","上赤名"),
("祝原のサクラ","天然記念物","下来島"),
("塩谷のカツラ","天然記念物","谷"),
("五明田遺跡縄文土器","考古資料","頓原・ハ神"),
("奥畑のナツツバキ","天然記念物","頓原"),
("都加賀のマユミ","天然記念物","都加賀"),
("中原古墳","史跡","ハ神"),
]

results = []
for name, subcat, loc in items:
    cat, _ = CAT_MAP[subcat]
    results.append({
        "pref": "島根県", "municipality": "飯南町", "name": name,
        "category": cat, "subcategory": subcat, "designation": "町指定",
        "designated_date": None, "location": loc or None, "description": None,
        "source_url": SRC, "source_format": "html", "fetched_at": FETCHED,
    })

with open('/Users/miyazakihitohata/bunkazai/pipeline/out/島根県/iinan.jsonl', 'w') as f:
    for r in results:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
print(len(results))
