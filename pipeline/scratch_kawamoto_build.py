import json, sys
sys.path.insert(0, '/Users/user/bunkazai/pipeline')
from scratch_shimane_wareki import wareki_to_iso

SRC = 'https://www.town.shimane-kawamoto.lg.jp/gyosei/town_administration/culture_history/kawamototyoubunnkazaibunnpuzu'
FETCHED = '2026-07-12T06:55:35Z'

# (subcat_code, date, name, count, loc, owner, note)
rows = [
('建','昭和54年5月30日','谷戸経塚','1基','谷戸','丸狷三（丸吉兵衛）','文政2年（1819）造営'),
('建','平成2年1月8日','鶴池山正蓮寺の楼門','1棟','南佐木','代務住職武田正俊','寛延4年（1751）建'),
('建','平成6年4月1日','鶴池山正蓮寺の経堂','1棟','南佐木','住職服部成明','廻り経堂（三間四方）仏像3体'),
('古','平成1年3月30日','全長寺文書','16通','川本','全長寺','吉川元春威状など'),
('古','平成1年3月30日','坂原家文書','176通','川本','川本町教委','年貢割附書85通、年貢皆済目録91通ほか'),
('天','平成17年5月10日','イズモコバイモ','','谷戸','島根県上坂二三男松本安江','921平米、島根県固有の植物で島根県版レッドデータブックに掲載され、絶滅が危惧されているイズモコバイモの自生地'),
]

CAT_MAP = {
 '建': ('有形文化財','建造物'), '古': ('有形文化財','古文書'),
 '天': ('記念物(史跡・名勝・天然記念物)','天然記念物'),
}

results = []
for code, date, name, count, loc, owner, note in rows:
    cat, subcat = CAT_MAP[code]
    iso = wareki_to_iso(date)
    desc_parts = []
    if count:
        desc_parts.append(f'員数{count}')
    desc_parts.append(f'所持者・保持者{owner}')
    if note:
        desc_parts.append(note)
    desc = '、'.join(desc_parts)
    results.append({
        "pref": "島根県", "municipality": "川本町", "name": name,
        "category": cat, "subcategory": subcat, "designation": "町指定",
        "designated_date": iso, "location": loc or None, "description": desc,
        "source_url": SRC, "source_format": "html", "fetched_at": FETCHED,
    })

with open('/Users/user/bunkazai/pipeline/out/島根県/kawamoto.jsonl', 'w') as f:
    for r in results:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
print(len(results))
