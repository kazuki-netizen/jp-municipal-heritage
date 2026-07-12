import json

SRC = "https://www.city.omaezaki.shizuoka.jp/kurashi/sports_bunka/bunka_gejutsu/bunkazai/ichiran.html"
FETCHED = "2026-07-12T03:51:38Z"
PREF = "静岡県"
MUNI = "御前崎市"

# (category, subcategory, name)
rows = [
("有形文化財","建造物","白羽神社本殿（入母屋造）"),
("有形文化財","建造物","駒形神社本殿（入母屋造）"),
("有形文化財","建造物","旧妙音庵薬師堂（附:薬師三尊・十二神将）"),
("有形文化財","建造物","池宮神社本殿"),
("有形文化財","建造物","高松神社本殿（入母屋造）"),
("有形文化財","建造物","岩地八幡神社本殿"),

("有形文化財","彫刻","地蔵菩薩尊像（青銅製立像1躯）"),
("有形文化財","彫刻","薬師如来立像（1躯）・日光菩薩立像（1躯）・月光菩薩立像（1躯）・十二神将立像（12躯）"),
("有形文化財","彫刻","玄翁堂の木造十一面観音菩薩像（立像1躯・座像1躯）"),
("有形文化財","彫刻","大日寺の大日如来座像（1躯）"),
("有形文化財","彫刻","岩地八幡神社神像（1躯）"),

("有形文化財","古文書","武田家朱印状（3通）"),
("有形文化財","古文書","中山家文書（39通）"),
("有形文化財","古文書","本間家文書（15通）"),
("有形文化財","古文書","水野家文書（1通）"),

("有形文化財","絵画","千羽の鶴（1点）"),

("有形文化財","歴史資料","いもじいさんの碑（顕彰碑・宝篋印塔各1基）"),
("有形文化財","歴史資料","御用提灯と収納箱（4点）"),
("有形文化財","歴史資料","旧朝比奈小学校の青い目の人形"),

("有形文化財","書跡","徳川慶喜揮毫の池宮神社扁額"),

("民俗文化財","有形民俗文化財","石造十一面観音菩薩立像（附:石造三十三観音像）"),

("記念物","史跡","星の糞遺跡（823平方メートル）"),
("記念物","史跡","薩田ケ谷横穴群"),

("記念物","天然記念物","いちょうの木（1本）"),
("記念物","天然記念物","イスノキ群生林（十数本）"),
("記念物","天然記念物","マキの木（1本）"),
("記念物","天然記念物","旧朝比奈小学校の黒松（1本）"),
]

out_path = "/Users/miyazakihitohata/bunkazai/pipeline/out/静岡県/omaezaki.jsonl"
with open(out_path, "w", encoding="utf-8") as f:
    for cat, subcat, name in rows:
        rec = {
            "pref": PREF,
            "municipality": MUNI,
            "name": name,
            "category": cat,
            "subcategory": subcat,
            "designation": "市指定",
            "designated_date": None,
            "location": None,
            "description": None,
            "source_url": SRC,
            "source_format": "html",
            "fetched_at": FETCHED,
        }
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

print(f"wrote {len(rows)} rows to {out_path}")
