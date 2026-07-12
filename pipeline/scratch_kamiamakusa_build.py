#!/usr/bin/env python3
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "熊本県", "kamiamakusa.jsonl")
SRC_URL = "http://www.city.kamiamakusa.kumamoto.jp/q/aview/408/1863.html"

YUKEI = "有形文化財"
SHISEKI = "記念物(史跡・名勝・天然記念物)"
MINZOKU = "民俗文化財"

# (name, description, category, subcategory, designated_date)
ROWS = [
    ("涼泉院殿月江宗白居士塚", "有馬家13代城主晴信の実弟、純実の墓と伝わる", YUKEI, "有形文化財", None),
    ("五輪塔群", "中世に築かれた大矢野氏の居城(中村城)周辺で発見された五輪塔群", YUKEI, "有形文化財", None),
    ("佐藤家墓碑群", "新田築立事業を行った佐藤家親子の墓 25基", YUKEI, "有形文化財", "1973-11-26"),
    ("値賀孫佐衛門追遠之碑", "佐賀唐津藩の寺沢氏家臣。値賀家の史実を刻銘", YUKEI, "有形文化財", None),
    ("隠れキリシタン墓碑群", "墓石の土座の中心に「干十字」刻印", YUKEI, "有形文化財", None),
    ("島原の乱時の鍛冶水盤", "武器の製造のために鍛冶職人が使用したと思われる", YUKEI, "有形文化財", None),
    ("キリシタン墓碑 平型", "天正15年(1587年)から慶長19年(1614年)に在住のキリシタンの墓碑と推考される", YUKEI, "有形文化財", None),
    ("澄泉寺跡五輪の塔群", "教良木城の一族の菩提寺の供養等。60数基", YUKEI, "有形文化財", None),
    ("開山塔", "開基 心田了会 座元禅士 嘉吉2年(1442)9月16日の刻字 昭和48年5月大松墓地から移転", YUKEI, "有形文化財", None),
    ("キリシタン墓碑 カマボコ型", "江戸時代初期の弾圧か天草・島原の乱以前に、湯島で死亡した日本人キリシタン布教師のものと推考されています", YUKEI, "有形文化財", None),
    ("佐藤家古文書", "紀州の出自「佐藤家」と「細川藩主」「島原・松平藩」との交流文書 肥後藩13通島原3通", YUKEI, "古文書", None),
    ("山崎信一氏所蔵文書", "天草島原の乱関係「細川忠光・光利」の書状／細川氏書状13通", YUKEI, "古文書", None),
    ("山崎冶千斗氏所蔵文書", "天草島原の乱関係「細川忠光・光利」の書状 2通", YUKEI, "古文書", None),
    ("布目瓦", "8世紀〜10世紀の瓦 2点", YUKEI, "考古資料", None),
    ("関戸家の井戸石蓋", "井戸の石蓋に「元和8年3月(1622)」と年号を刻記", YUKEI, "有形文化財", None),
    ("菅原神社万治元年札", "万冶元年(1658)の上棟式の記載がある棟札", YUKEI, "有形文化財", None),
    ("遍照院銅造梵鐘", "所有者 遍照院 製作年:宝永6年(1709)", YUKEI, "工芸品", None),
    ("松菊双鶴紋鏡", "大矢野城より出土", YUKEI, "考古資料", None),
    ("向陽寺雨乞いの鐘", "寛保3年3月(1743)二代目和尚の時作成。雨乞いに使用", YUKEI, "工芸品", None),
    ("大矢野城址", "天正年間後約300年大矢野城より出土した大矢野氏の居城", SHISEKI, "史跡", None),
    ("千崎古墳群", "箱式石棺15基、竪穴式石棺1基他", SHISEKI, "史跡", None),
    ("不知火塚", "弘化2年(1845)年 文化碑", YUKEI, "有形文化財", None),
    ("阿村がたきり踊り", "「おざや新地」(鏡町)干拓時のがたきり節・新地節", MINZOKU, "無形民俗文化財", None),
    ("合津神社獅子舞", "宇土「西岡神社」の流れを汲む。約150年の歴史", MINZOKU, "無形民俗文化財", None),
    ("菅原神社神楽太鼓踊り", "宝暦7年(1757)社殿創建に伴い伊勢神宮の楽士により指導", MINZOKU, "無形民俗文化財", None),
    ("大作山棒踊り", "「西南の役」時 地元青年団が薩摩武士より習った棒踊り", MINZOKU, "無形民俗文化財", None),
    ("小屋川内獅子舞", "大正9年から青年団が発足。五穀豊穣など祈願の獅子舞", MINZOKU, "無形民俗文化財", None),
    ("御手水の滝", "長さ約20m。太郎丸岳録沢の水が尾根を流れている", SHISEKI, "名勝", None),
    ("祝口観音の滝", "幅10〜15m。山肌を滑るように流れる滝大小の滝壷あり", SHISEKI, "名勝", None),
    ("今泉諏訪神社の大杉", "樹齢約450年。幹周り4m高さ約15mの大杉", SHISEKI, "天然記念物", None),
    ("野々川のモチノキ", "樹齢推定約300年。幹周り1.8m高さ約13.5mのモチノキの古木", SHISEKI, "天然記念物", None),
    ("二間戸小学校跡地のイチョウ", "樹齢約300年。幹周り5m高さ約21.5m位のイチョウの木", SHISEKI, "天然記念物", None),
    ("山田のたちばな", "樹齢約130年。幹周り1.08m高さ約7.5m小型柑たちばなの原木", SHISEKI, "天然記念物", None),
    ("山神の一本杉", "樹齢約600年。幹周り6m高さ約30m位の大杉。根元に祠あり", SHISEKI, "天然記念物", None),
]


def main():
    m = json.load(open(os.path.join(HERE, "cache", "熊本県", "kamiamakusa", "manifest.json"), encoding="utf-8"))
    entry = [v for v in m.values() if v["url"] == SRC_URL][0]
    fetched_at = entry["fetched_at"]

    out_rows = []
    for name, desc, category, subcat, date in ROWS:
        out_rows.append({
            "pref": "熊本県", "municipality": "上天草市", "name": name,
            "category": category, "subcategory": subcat, "designation": "市指定",
            "designated_date": date, "location": None,
            "description": desc,
            "source_url": SRC_URL, "source_format": "html", "fetched_at": fetched_at,
        })

    assert len(out_rows) == 34, len(out_rows)
    with open(OUT, "w", encoding="utf-8") as f:
        for r in out_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"wrote {len(out_rows)} rows to {OUT}")


if __name__ == "__main__":
    main()
