# 埼玉県 町村指定文化財 カバレッジ (batch C: 21町村)

| slug | 自治体 | 取得件数 | 目標 | 備考 |
|------|--------|---------|------|------|
| moroyama | 毛呂山町 | 67 | 82(全体)/67(町指定のみ) | 官ページ上は82件だが国指定1+県指定9+県選定4を含む、町指定は65+2=67件 |
| ogose | 越生町 | 34 | ? |  |
| namegawa | 滑川町 | 32 | 35 | 目標35に対し32。CSSページ1枚のみキャッシュ、3件が未収録の可能性あり |
| ranzan | 嵐山町 | 40 | 40 | ✓ |
| ogawa | 小川町 | 80 | ? |  |
| kawajima | 川島町 | 8 | ? | 一覧ページ404。個別紹介ページ（仏像4件+祭囃子4件）から8件のみ取得。大幅欠損疑い |
| yoshimi | 吉見町 | 19 | ? | PDF（令和3年5月現在）から19件取得 |
| hatoyama | 鳩山町 | 8 | 10 | デジタル博物館形式から8件。公式10件との差あり |
| tokigawa | ときがわ町 | 36 | ? |  |
| yokoze | 横瀬町 | 48 | 46 | 目標46に対し48。2件多い可能性（重複または誤分類） |
| minano | 皆野町 | 66 | ? |  |
| nagatoro | 長瀞町 | 32 | 32 | ✓ |
| ogano | 小鹿野町 | 4 | 115 | メインのPDF(2007bunkazai.pdf)未キャッシュ。add-bunkazaiページから4件のみ。大幅欠損 |
| misato-kodama | 美里町 | 1 | ? | カテゴリ別リンク形式、町指定確認できたのは1件のみ。大幅欠損疑い |
| kamikawa | 神川町 | 27 | ? |  |
| kamisato | 上里町 | 51 | ? |  |
| yorii | 寄居町 | 53 | 53 | ✓ PDF(R7.4.1)から53件取得 |
| miyashiro | 宮代町 | 34 | ? |  |
| sugito | 杉戸町 | 22 | 34 | 埼玉県ODP CSV（dataset181）から22件。目標34に対し不足。CSVが古い可能性 |
| matsubushi | 松伏町 | 34 | 34 | ✓ |
| higashichichibu | 東秩父村 | 55 | ? |  |

## 取得ファイル一覧

- `out/埼玉県/moroyama.jsonl`: 67行
- `out/埼玉県/ogose.jsonl`: 34行
- `out/埼玉県/namegawa.jsonl`: 32行
- `out/埼玉県/ranzan.jsonl`: 40行
- `out/埼玉県/ogawa.jsonl`: 80行
- `out/埼玉県/kawajima.jsonl`: 8行
- `out/埼玉県/yoshimi.jsonl`: 19行
- `out/埼玉県/hatoyama.jsonl`: 8行
- `out/埼玉県/tokigawa.jsonl`: 36行
- `out/埼玉県/yokoze.jsonl`: 48行
- `out/埼玉県/minano.jsonl`: 66行
- `out/埼玉県/nagatoro.jsonl`: 32行
- `out/埼玉県/ogano.jsonl`: 4行
- `out/埼玉県/misato-kodama.jsonl`: 1行
- `out/埼玉県/kamikawa.jsonl`: 27行
- `out/埼玉県/kamisato.jsonl`: 51行
- `out/埼玉県/yorii.jsonl`: 53行
- `out/埼玉県/miyashiro.jsonl`: 34行
- `out/埼玉県/sugito.jsonl`: 22行
- `out/埼玉県/matsubushi.jsonl`: 34行
- `out/埼玉県/higashichichibu.jsonl`: 55行

**合計: 751行**

## 注意事項

- designation は「町指定」または「村指定」のみ（国指定・県指定・県選定は除外・カウント済み）
- 川島町(kawajima): 一覧ページ不在。個別ページから8件。実態は大幅に多い可能性
- 小鹿野町(ogano): メインPDF未キャッシュ。4件のみ（実態115件以上）
- 美里町(misato-kodama): カテゴリ別リンク形式で1件のみ確認
- 杉戸町(sugito): ODP CSVは22件。官サイト最新値は34件と乖離
- 横瀬町(yokoze): 48件取得で目標46より2件多い。重複・誤分類を要確認
- 令和7年11月以降の指定日は2026-07-07時点で将来日付（令和7=2025のため実際は有効）