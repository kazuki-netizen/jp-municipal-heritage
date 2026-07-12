# 石川県 市町村指定文化財 Gap-fill記録

作業日: 2026-07-12
方法: WebSearch(受動)→curl(-m 20 -L, ≥2.5s delay, GET only, robots.txt確認)。SPA/JS-only等はcurl不可のため対象外。null-over-guess方針(確証のない項目は追加しない)。

## 対象と結果サマリー

| 市町村 | slug | 着手前 | 着手後 | 差分 | 状態 |
|--------|------|--------|--------|------|------|
| 能登町 | noto | 0 | 0 | +0 | 未解決(個別品目名一覧が公式サイトに存在しない) |
| 川北町 | kawakita | 2 | 3 | +1 | 部分解決 |
| 穴水町 | anamizu | (未作成) | 4 | +4 | 新規作成・部分解決 |
| 白山市 | hakusan | 312 | 312 | +0 | 未着手(低優先のため時間内に再調査せず) |

## 能登町(noto) — 未解決

- 公式ページ(https://www.town.noto.lg.jp/kakuka/1012/gyomu/kyouikufront/gyoumuannai/rekishibunka/rekishibunkazai/4804.html)は2026年5月14日更新の最新版でも、リンク先PDFは分野別集計表(建築18/絵画39/彫刻46/工芸品32/書籍典籍6/古文書11/考古資料15/歴史資料20/無形文化財1/無形民俗14/有形民俗15/史跡23/名勝4/天然記念物77、町計320〜321件)のみで、個別品目名を含む一覧は確認できなかった。
- WebSearchで新たに見つけた候補PDF(https://www.town.noto.lg.jp/open/info/0000021239.pdf)は404で取得不可。
- 能登町例規集(独自の d1-law.com ベースの検索システム、g-reiki.net ではない)は静的URLでの直接アクセスができず、curlでは条例別表を辿れなかった。
- 「文化財保存活用地域計画」公表ページ(https://www.town.noto.lg.jp/kakuka/1007/4010.html)にリンクされているPDFは農林振興地域整備計画(農地関連)であり、文化財とは無関係だった。
- 文化遺産オンライン(bunka.nii.ac.jp)の能登町ページは国指定10件のみの収録で、市町村指定は掲載されていない。
- 結論: 個別品目名を含む一次ソースが公式サイト上に存在しないことを再確認。gap-fill対象として今後も未解決。

## 川北町(kawakita) — 2件→3件

- 新規追加: 「草深甚四郎碑」(町指定、記念物/史跡)。町公式サイトの町紹介ページ(https://www.town.kawakita.ishikawa.jp/kanko1/entry-185.html、旧youranサブサイトとは別の現行サイト)で「川北町指定文化財」と明記されているのを発見。
- 同じ「川北町の歴史」ページ(entry-17.html)で言及されている「芭蕉の渡し」「明治天皇御休所」は指定文化財である旨の明記がなく、null-over-guess方針により追加を見送った。
- 網羅的な指定文化財一覧ページは依然として公式サイト上に存在せず、部分収録(3件)にとどまる。

## 穴水町(anamizu) — 新規4件

- 例規集(g-reiki.net/anamizu)で「穴水町文化財保護条例」本文を確認したが、条例は指定手続きのみを定めるもので個別品目の別表は無かった。
- 「地域計画の公表について」ページは農地地域計画のページであり、文化財の保存活用地域計画とは無関係な誤ヒットだった。
- 「歴史・文化財」トップページ(life/sub/1/18/68/)には埋蔵文化財の取扱いに関する告知のみで、指定文化財一覧は無い。
- 穴水町歴史民俗資料館(長家史料館)の展示品紹介ページ(page/100477.html、kankou-kyouiku/rekishiminnzokushiryoukann{2,3,4,5}.html)を個別に確認し、「町指定文化財」と明記された4件を収録:
  - 甲小寺遺跡出土品(考古資料)
  - 能面(尉面・女面・かく面)(工芸品)
  - 御朱采配(工芸品)
  - 金そう印馬幟(工芸品)
  - (展示品3「長家文書」は県指定のため除外)
- いしかわ文化財ナビ(bunkazainavi.pref.ishikawa.lg.jp)は検索フォームがPOST方式(/searchsimple)で、GETパラメータでの絞込結果取得を試みたが常に同一の空ページ(4,923,620バイト固定)が返り、GET onlyの制約下では利用不可と判断し断念した。
- 網羅的な一覧は依然として無く、部分収録(4件)にとどまる。

## 白山市(hakusan) — 未着手

- 低優先指定のため、時間内に教育委員会サイトの分野別ページ再確認を実施できなかった。既存312件のまま。

## 使用ソース一覧

- https://www.town.kawakita.ishikawa.jp/kanko1/entry-185.html (川北町公式・町の紹介)
- https://www.town.kawakita.ishikawa.jp/kanko1/entry-17.html (川北町の歴史)
- https://www.town.anamizu.lg.jp/page/100477.html, kankou-kyouiku/rekishiminnzokushiryoukann{2,4,5}.html (穴水町歴史民俗資料館展示品紹介)
- https://www1.g-reiki.net/anamizu/reiki_honbun/i138RG00000258.html (穴水町文化財保護条例、参照のみ・品目情報なし)
- https://www.town.noto.lg.jp/kakuka/1012/gyomu/kyouikufront/gyoumuannai/rekishibunka/rekishibunkazai/4804.html (能登町公式、集計のみ)


# 高難度gap-fill 第2次 (2026-07-12)

## 能登町(noto) — 0 → 32件（公式320の部分回収）

- いしかわ文化財ナビの正ホストは `www.bunkazainavi.pref.ishikawa.lg.jp`（前回試行の `bunkazainavi.pref...` はDNS解決不可）。robots.txtは全面許可だが、検索は POST /searchsimple（CSRFトークン必須）で、GETは405。地図(/map)は利用規約同意ページ経由、データ取得は /movemapbounds・/document/{gid}/{type} のGETエンドポイントがあるもののgid列挙手段がなく断念。なお同ナビの対象は埋蔵文化財・史跡・天然記念物・指定建造物系のみで、町指定320件の大半（美術工芸品）はそもそも対象外。
- 町公式ページ4804.html添付の「能登町指定文化財集計」PDF(material/files/group/13/0000021240.pdf、令和4年3月現在)を目視読取。分類別件数に加えて各分類の「主な指定物件」として町指定の実名29件が記載されており、これを収録（指定年月日・所在地の記載なし）。
- 文化庁「地方指定文化財データベース」(文化遺産オンライン online.bunka.go.jp、robots.txt Crawl-Delay:3遵守)の市区町村検索(GET) `heritages/search/prefecture_cd:17/city_code:17463` で能登町指定3件を発見し、詳細ページから指定年月日付きで収録: 菅原神社の懸仏(2020-06-05)、願成寺の黄檗鉄眼版大般若波羅蜜多経および収納木製箪笥(2019-03-05)、日枝神社の銅造聖観音懸仏(2016-05-10)。うち日枝神社の懸仏は集計PDFの工芸品代表例と同一物件とみられるため、PDF側からの重複収録はしていない。
- 残り約288件は非公開。能登町文化財保存活用地域計画は未策定、県公表の目録は国・県指定のみ、令和6年能登半島地震関連の被災文化財リストにも市町指定の個別名の公開一覧は見つからなかった。

## 使用ソース（第2次）
- https://www.town.noto.lg.jp/material/files/group/13/0000021240.pdf （能登町指定文化財集計・令和4年3月）
- https://online.bunka.go.jp/heritages/detail/516397, /408925, /288650 （文化庁 地方指定文化財データベース）
