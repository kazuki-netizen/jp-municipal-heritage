import sys
sys.path.insert(0, '/Users/miyazakihitohata/bunkazai/pipeline')
from scratch_shimane_pref_common2 import extract, write_jsonl

r = extract('/Users/miyazakihitohata/bunkazai/pipeline/cache/島根県/nishinoshima/pref_nishinoshima.html',
             '西ノ島町', '町指定',
             'https://www.pref.shimane.lg.jp/life/bunka/bunkazai/shimane/sityouson/nisinoshima.html',
             '2026-07-12T08:43:08Z')
n = write_jsonl(r, '/Users/miyazakihitohata/bunkazai/pipeline/out/島根県/nishinoshima.jsonl')
print(n)
print('null cat', sum(1 for x in r if x['category'] is None))
