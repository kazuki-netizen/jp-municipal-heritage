import json
rows = [
("八剣神社湯立神楽","民俗文化財","無形民俗文化財","1971-03-01","鞍手町大字中山"),
("六嶽神楽","民俗文化財","無形民俗文化財","1971-03-01","鞍手町大字室木"),
("山ヶ崎道中楽","民俗文化財","無形民俗文化財","1971-03-01","鞍手町大字中山"),
("剣神社遷宮行列","民俗文化財","無形民俗文化財","1971-03-01","鞍手町大字木月"),
("永谷万年願盆綱引き","民俗文化財","無形民俗文化財","1971-03-01","鞍手町大字永谷"),
("高木薬師如来","有形文化財","彫刻","1972-06-06","鞍手町大字新北"),
("十六神社のクスノキ","記念物","天然記念物","1998-04-01","鞍手町大字八尋"),
("長谷の三尊檜","記念物","天然記念物","2009-04-01","鞍手町大字長谷"),
]
url = "https://www.town.kurate.lg.jp/bunka/bunka_siteibunkazai.html"
out=[]
for name,cat,sub,date,loc in rows:
    out.append({"pref":"福岡県","municipality":"鞍手町","name":name,"category":cat,"subcategory":sub,
        "designation":"町指定","designated_date":date,"location":loc,"description":None,
        "source_url":url,"source_format":"html","fetched_at":"2026-07-12T00:00:00Z"})
with open("./pipeline/out/福岡県/kurate.jsonl","w",encoding="utf-8") as f:
    for r in out: f.write(json.dumps(r,ensure_ascii=False)+"\n")
print(len(out))
