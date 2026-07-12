import json
rows = [
(1,"天照皇大神宮の欅","記念物","天然記念物","1998-10-23"),
(2,"久山町役場の兵事関係文書","民俗文化財","有形民俗文化財","1998-10-23"),
(3,"旧水取宮境内地のイチョウ","記念物","天然記念物","1998-10-23"),
(4,"旧水取宮境内地の大藤","記念物","天然記念物","1998-10-23"),
(5,"原石棺群","記念物","史跡","2001-02-22"),
(6,"石黒池のオグラコウホネ・ヒメコウホネ","記念物","天然記念物","2001-10-17"),
(7,"銅造釈迦如来坐像","有形文化財","彫刻","2010-02-23"),
(8,"木造十一面観音立像","有形文化財","彫刻","2010-02-23"),
(9,"木造地蔵菩薩立像","有形文化財","彫刻","2010-02-23"),
(10,"木造天部形立像","有形文化財","彫刻","2010-02-23"),
(11,"宋風獅子","有形文化財","彫刻","2010-02-23"),
(12,"薩摩塔","有形文化財","薩摩塔","2010-02-23"),
]
url = "https://www.town.hisayama.fukuoka.jp/gyosei/kanko_bunka_sports/rekishi_bunkazai/choshitei/index.html"
out=[]
for no,name,cat,sub,date in rows:
    out.append({"pref":"福岡県","municipality":"久山町","name":name,"category":cat,"subcategory":sub,
        "designation":"町指定","designated_date":date,"location":None,
        "description":f"町指定文化財第{no}号",
        "source_url":url,"source_format":"html","fetched_at":"2026-07-12T00:00:00Z"})
with open("/Users/user/bunkazai/pipeline/out/福岡県/hisayama.jsonl","w",encoding="utf-8") as f:
    for r in out: f.write(json.dumps(r,ensure_ascii=False)+"\n")
print(len(out))
