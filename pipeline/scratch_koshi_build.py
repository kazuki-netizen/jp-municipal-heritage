#!/usr/bin/env python3
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "熊本県", "koshi.jsonl")

YUKEI = "有形文化財"
SHISEKI = "記念物(史跡・名勝・天然記念物)"
MINZOKU = "民俗文化財"

# (name, category, subcat, url, description)
ROWS = [
    ("厳照寺の板碑群・石幢", YUKEI, "有形文化財", "https://www.city.koshi.lg.jp/kiji00320186/index.html", None),
    ("石立石棺", SHISEKI, "史跡", "https://www.city.koshi.lg.jp/kiji00320190/index.html", None),
    ("御手洗遺跡", SHISEKI, "史跡", "https://www.city.koshi.lg.jp/kiji00320191/index.html", None),
    ("黒松古墳群", SHISEKI, "史跡", "https://www.city.koshi.lg.jp/kiji00320194/index.html", None),
    ("竹迫日吉神社 楼門及び社殿", YUKEI, "建造物", "https://www.city.koshi.lg.jp/kiji00320198/index.html", "豊岡の原口区にあり、竹迫近郷の氏神社として尊崇されている"),
    ("桑鶴遺跡", SHISEKI, "史跡", "https://www.city.koshi.lg.jp/kiji00320214/index.html", None),
    ("合志町高千穂神楽", MINZOKU, "無形民俗文化財", "https://www.city.koshi.lg.jp/kiji00320215/index.html", None),
    ("笹塚古墳", SHISEKI, "史跡", "https://www.city.koshi.lg.jp/list00462.html", None),
    ("合志親為肖像図", YUKEI, "絵画", "https://www.city.koshi.lg.jp/list00462.html", None),
    ("合志郡絵図", YUKEI, "古文書", "https://www.city.koshi.lg.jp/list00462.html", None),
    ("竹迫城絵図", YUKEI, "古文書", "https://www.city.koshi.lg.jp/list00462.html", None),
    ("医音寺跡", SHISEKI, "史跡", "https://www.city.koshi.lg.jp/list00462.html", "竹迫の上町区にある、中世の墓石、板碑などが残る寺院跡"),
    ("虚空蔵さん", YUKEI, "彫刻", "https://www.city.koshi.lg.jp/list00462.html", "商売繁盛、理財、家内安全、学業成就にご利益があるとされ、こくんぞさんの名称で親しまれている"),
    ("須屋神社三十六歌仙絵馬", YUKEI, "絵画", "https://www.city.koshi.lg.jp/list00462.html", "寛政4年（1792）、須屋神社に三十六歌仙絵馬が奉納された"),
    ("木瀬遺跡", SHISEKI, "史跡", "https://www.city.koshi.lg.jp/list00462.html", None),
    ("天神平の樟", SHISEKI, "天然記念物", "https://www.city.koshi.lg.jp/list00462.html", "上庄区にある、合志市で最も大きな樹木"),
    ("生坪塚山古墳", SHISEKI, "史跡", "https://www.city.koshi.lg.jp/list00462.html", None),
    ("豊岡宮本横穴群", SHISEKI, "史跡", "https://www.city.koshi.lg.jp/list00462.html", None),
    ("平島の大太鼓", YUKEI, "工芸品", "https://www.city.koshi.lg.jp/list00462.html", None),
    ("今町座組阿弥陀如来像", YUKEI, "彫刻", "https://www.city.koshi.lg.jp/list00462.html", None),
    ("竹迫観音祭", MINZOKU, "無形民俗文化財", "https://www.city.koshi.lg.jp/list00460.html", "毎年7月の第2土曜夕方から、竹迫町内で行われる、県内で最も早い夏祭り"),
]


def main():
    m = json.load(open(os.path.join(HERE, "cache", "熊本県", "koshi", "manifest.json"), encoding="utf-8"))
    fallback_fetch = max(v["fetched_at"] for v in m.values())
    by_url = {v["url"]: v["fetched_at"] for v in m.values()}

    out_rows = []
    for name, category, subcat, url, desc in ROWS:
        out_rows.append({
            "pref": "熊本県", "municipality": "合志市", "name": name,
            "category": category, "subcategory": subcat, "designation": "市指定",
            "designated_date": None, "location": None,
            "description": desc,
            "source_url": url, "source_format": "html",
            "fetched_at": by_url.get(url, fallback_fetch),
        })

    with open(OUT, "w", encoding="utf-8") as f:
        for r in out_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"wrote {len(out_rows)} rows to {OUT}")


if __name__ == "__main__":
    main()
