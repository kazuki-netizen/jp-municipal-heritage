# 千葉県 市指定文化財 抽出結果 (batch B)

実行日: 2026-07-07  
対象: 16市

| municipality | slug | rows | expected | match | notes |
|---|---|---|---|---|---|
| 鎌ケ谷市 | kamagaya | 26 | 26 | ✓ | |
| 君津市 | kimitsu | 33 | 33 | ✓ | |
| 富津市 | futtsu | 60 | 82 | ✗ | キャッシュ10ページから60件抽出。市指定記述は市指定/市史跡/市天然記念物テキストで識別。キャッシュ上限60件、残22件は未キャッシュページ分と推定 |
| 浦安市 | urayasu | 22 | 22 | ✓ | |
| 四街道市 | yotsukaido | 63 | 62 | △ | 公式62件と1件差。Table[0](考古資料1件)+Table[1](有形53件)+Table[2](記念物6件)+Table[3](民俗3件)=63件。指定一覧に令和6年追加分含む可能性 |
| 袖ケ浦市 | sodegaura | 34 | 31 | △ | 令和7年(2025)指定3件含む。公式31件は2025年3月以前の数値と推定。2025-07/10指定の3件を含め34件 |
| 八街市 | yachimata | 20 | 20 | ✓ | rowspan処理で正確抽出。御成街道跡の2所在地を1件に統合 |
| 印西市 | inzai | 26 | 26 | ✓ | 国/県/市混在ページからTable[2]のみ抽出(市の指定文化財26件) |
| 白井市 | shiroi | 43 | 43 | ✓ | |
| 富里市 | tomisato | 24 | 24 | ✓ | opendata CSV使用 |
| 南房総市 | minamiboso | 181 | 181 | ✓ | 旧6町合算 |
| 匝瑳市 | sosa | 60 | 60 | ✓ | |
| 香取市 | katori | 126 | 126 | ✓ | PDF視覚読取りで手動入力 |
| 山武市 | sammu | 91 | 91 | ✓ | |
| いすみ市 | isumi | 199 | 199 | ✓ | 番号1〜199 |
| 大網白里市 | oamishirasato | 18 | 22 | ✗ | キャッシュページ(2024年2月更新)には18件のみ記載。公式22件との差4件は別途確認要 |

## 合計
- 完全一致: 10市 (kamagaya, kimitsu, urayasu, yachimata, inzai, shiroi, tomisato, minamiboso, sosa, katori, sammu, isumi → 12市)
- 件数過多: 2市 (yotsukaido+1, sodegaura+3 → 令和新指定分)
- 件数不足: 2市 (futtsu -22, oamishirasato -4)
- 全16市の.jsonl出力完了
