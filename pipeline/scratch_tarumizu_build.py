import json

records = [
    {
        'pref': '鹿児島県', 'municipality': '垂水市', 'name': '宝塔',
        'category': '記念物', 'subcategory': '史跡', 'designation': '市指定',
        'designated_date': None, 'location': '垂水市（月海寺跡）',
        'description': '天文13年(1544)伊地知重武による垂水平定を機に建立されたと推定される塔。笠石に梵字が刻まれていたが塔身は風化。',
        'source_url': 'https://www.city.tarumizu.lg.jp/bunka/kurashi/kosodate/roman/documents/shiseki_f2.pdf',
        'source_format': 'pdf', 'fetched_at': '2026-07-12T13:20:00Z',
    },
    {
        'pref': '鹿児島県', 'municipality': '垂水市', 'name': 'お長屋',
        'category': '記念物', 'subcategory': '史跡', 'designation': '市指定',
        'designated_date': None, 'location': '垂水市（垂水小学校校門脇）',
        'description': '鹿児島県有形文化財（建造物）にも指定。江戸初期建造の多聞櫓構造をもつ武家建築で、正面15間・梁間3間半。',
        'source_url': 'https://www.city.tarumizu.lg.jp/bunka/kurashi/kosodate/roman/documents/shiseki_f6.pdf',
        'source_format': 'pdf', 'fetched_at': '2026-07-12T13:20:00Z',
    },
    {
        'pref': '鹿児島県', 'municipality': '垂水市', 'name': '垂水島津家墓所',
        'category': '記念物', 'subcategory': '史跡', 'designation': '市指定',
        'designated_date': None, 'location': '垂水市田神字上ノ平添328-2（心翁寺）',
        'description': '垂水島津家歴代領主・一族の墓所。面積1,741平方メートル。夫婦墓碑並立や六面地蔵塔などが特徴。',
        'source_url': 'https://www.city.tarumizu.lg.jp/bunka/kurashi/kosodate/roman/tarumzusimadubosyo.html',
        'source_format': 'html', 'fetched_at': '2026-07-12T13:20:00Z',
    },
]

with open('out/鹿児島県/tarumizu.jsonl', 'w', encoding='utf-8') as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
print(len(records))
