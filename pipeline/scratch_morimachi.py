import json

FETCHED = "2026-07-12T03:51:49Z"
PREF = "静岡県"
MUNI = "森町"

SRC45 = "https://www.town.morimachi.shizuoka.jp/gyosei/machinososhiki/shakaikyoikuka/bunkashinkogakari/2/776.html"
SRC46 = "https://www.town.morimachi.shizuoka.jp/gyosei/machinososhiki/shakaikyoikuka/bunkashinkogakari/2/774.html"
SRC44 = "https://www.town.morimachi.shizuoka.jp/gyosei/machinososhiki/shakaikyoikuka/bunkashinkogakari/2/775.html"
SRC47 = "https://www.town.morimachi.shizuoka.jp/gyosei/machinososhiki/shakaikyoikuka/bunkashinkogakari/2/1098.html"
SRC48 = "https://www.town.morimachi.shizuoka.jp/gyosei/machinososhiki/shakaikyoikuka/bunkashinkogakari/2/1097.html"
SRC49 = "https://www.town.morimachi.shizuoka.jp/gyosei/machinososhiki/shakaikyoikuka/bunkashinkogakari/2/773.html"
SRC50 = "https://www.town.morimachi.shizuoka.jp/gyosei/machinososhiki/shakaikyoikuka/bunkashinkogakari/2/1091.html"

# (category, subcategory, name, location, description, source_url, date)
rows = [
("有形文化財","建造物","小國神社本殿","森町一宮",None,SRC45,None),
("有形文化財","建造物","三嶋神社本殿","森町森",None,SRC45,None),
("有形文化財","建造物","金剛院山門","森町三倉（大河内）","大工黒川喜兵衛、天保8年(1837年)建立と伝えられる",SRC46,None),
("有形文化財","建造物","天宮神社神宮寺","森町天宮",None,SRC46,None),
("有形文化財","建造物","旧周智郡役所（現町立歴史民俗資料館）","森町","明治10年代建築の近代建築",SRC44,None),
("有形文化財","建造物","旧城下学校","森町","明治10年代建築の近代建築",SRC44,None),
("その他","町並み","城下の町並み","森町城下","町並み保存として昭和49年(1974年)に町指定",SRC44,"1974"),
("有形文化財","建造物","秋葉道の常夜燈","森町（秋葉道沿い）",None,SRC44,None),
("有形文化財","彫刻","木造子安地蔵","森町森　蓮華寺","像高132.1cm、江戸時代、木喰行道作",SRC47,None),
("有形文化財","彫刻","木造左大臣右大臣像","森町一宮　小國神社","2躯、江戸時代、木造彩色",SRC47,None),
("有形文化財","彫刻","木造唐獅子像","森町天宮　天宮神社","1対、江戸時代、木造彩色寄木造",SRC47,None),
("有形文化財","彫刻","不動明王及び小國鹿苑菩薩","森町一宮　蓮増院","不動明王は南北朝期、小國鹿苑菩薩は桃山期の作",SRC47,None),
("有形文化財","絵画","元三慈恵大師像","森町森　蓮華寺","1幅、江戸時代、絹本着色",SRC48,None),
("有形文化財","絵画","三十六歌仙扁額","森町天宮　天宮神社","34面、江戸時代、板絵着色",SRC48,None),
("有形文化財","工芸品","釣灯籠","森町天宮　天宮神社","1対、江戸時代元禄10年(1697年)、青銅製、遠州横須賀城主西尾忠成の奉納",SRC49,None),
("有形文化財","古文書","小國神社記録","森町一宮　小國神社","1冊、江戸時代延宝8年(1680年)",SRC49,None),
("有形文化財","書跡・典籍","世代万ねん","森町森（個人蔵）","1冊、江戸時代天保3年(1832年)、南鳳寺の由来と過去帳",SRC49,None),
("有形文化財","書跡・典籍","秋葉街道似多栗毛","森町森（個人蔵）","1冊、江戸後期",SRC49,None),
("有形文化財","書跡・典籍","遠淡海地志","森町森（個人蔵）","8冊、江戸後期天保5年(1834年)",SRC49,None),
("記念物","天然記念物","コウジミカン","森町鍛冶島","1本、中世〜江戸時代に食されてきた在来種",SRC50,None),
("記念物","名勝","葛布の滝（二の滝）","森町葛布","一の滝・二の滝・三の滝からなる、本宮山の霊水",SRC50,None),
]

out_path = "/Users/user/bunkazai/pipeline/out/静岡県/morimachi.jsonl"
with open(out_path, "w", encoding="utf-8") as f:
    for cat, subcat, name, loc, desc, src, year in rows:
        iso = f"{year}-01-01" if year else None
        rec = {
            "pref": PREF,
            "municipality": MUNI,
            "name": name,
            "category": cat,
            "subcategory": subcat,
            "designation": "町指定",
            "designated_date": None,  # town publishes no structured designation dates for these
            "location": loc,
            "description": desc,
            "source_url": src,
            "source_format": "html",
            "fetched_at": FETCHED,
        }
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

print(f"wrote {len(rows)} rows to {out_path}")
