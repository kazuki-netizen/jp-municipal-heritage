import sys
sys.path.insert(0, '/Users/miyazakihitohata/bunkazai/pipeline')
from scratch_shimane_pref_common2 import extract, write_jsonl

r = extract('/Users/miyazakihitohata/bunkazai/pipeline/cache/島根県/chibu/pref_chibu.html',
             '知夫村', '村指定',
             'https://www.pref.shimane.lg.jp/life/bunka/bunkazai/shimane/sityouson/chibu.html',
             '2026-07-12T08:43:11Z')
n = write_jsonl(r, '/Users/miyazakihitohata/bunkazai/pipeline/out/島根県/chibu.jsonl')
print(n)
print('null cat', sum(1 for x in r if x['category'] is None))
for x in r:
    print(x['name'], x['category'], x['subcategory'])
