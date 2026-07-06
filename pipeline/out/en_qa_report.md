# EN QA Report — bunkazai

**Date**: 2026-07-06  
**Model**: fugu-ultra  
**Input**: pipeline/out/en_qa_sample.jsonl (30 rows, 11 with withheld prose)  
**Sakana tokens consumed**: 184590  

## Score Summary

| Metric | Value |
|--------|-------|
| mean romaji_plausibility | 5.00 / 5 (n=30) |
| mean name_en_accuracy | 5.00 / 5 (n=30) |
| overall mean (avg of both) | 5.00 / 5 |
| description_grounding flags (yes) | 0 |
| prose_leak flags (yes) | 0 |

## Verdict: PASS

Criteria: mean ≥ 4.0 AND prose_leaks = 0 AND grounding_flags ≤ 2

## Per-Row Results

| jmh_id | romaji | name_en | grounding | grounding_note | prose_leak |
|--------|--------|---------|-----------|----------------|------------|
| JMH-012025-0012 | 5 | 5 | no | N/A | n/a |
| JMH-013323-0004 | 5 | 5 | no | N/A | no |
| JMH-012025-0065 | 5 | 5 | no | N/A | no |
| JMH-016624-0021 | 5 | 5 | no | N/A | n/a |
| JMH-012025-0011 | 5 | 5 | no |  | n/a |
| JMH-012025-0045 | 5 | 5 | no |  | n/a |
| JMH-012076-0007 | 5 | 5 | no |  | n/a |
| JMH-012025-0070 | 5 | 5 | no |  | no |
| JMH-012025-0027 | 5 | 5 | no |  | n/a |
| JMH-012335-0013 | 5 | 5 | no |  | no |
| JMH-012025-0077 | 5 | 5 | no |  | n/a |
| JMH-012335-0024 | 5 | 5 | no |  | no |
| JMH-012238-0003 | 5 | 5 | no | No ungrounded facts added. | no |
| JMH-012025-0010 | 5 | 5 | no | No ungrounded facts added. | n/a |
| JMH-015784-0001 | 5 | 5 | no | No ungrounded facts added. | n/a |
| JMH-012335-0021 | 5 | 5 | no | No ungrounded facts added. | no |
| JMH-012076-0009 | 5 | 5 | no | All facts in the English description are directly derivable from the provided structured fields. | n/a |
| JMH-013609-0018 | 5 | 5 | no | All facts in the English description are directly derivable from the provided structured fields. | n/a |
| JMH-012025-0034 | 5 | 5 | no | All facts in the English description are directly derivable from the provided structured fields. | n/a |
| JMH-013609-0022 | 5 | 5 | no | All facts in the English description are directly derivable from the provided structured fields. | n/a |
| JMH-016624-0017 | 5 | 5 | no | All facts in the description are derived from the structured fields. The phrase 'Ainu fortified site' is a standard translation gloss for the term 'chashi' found in the Japanese name. | n/a |
| JMH-012025-0058 | 5 | 5 | no | All facts in the description are directly derived from the structured fields. | n/a |
| JMH-012025-0048 | 5 | 5 | no | All facts in the description are directly derived from the structured fields. | n/a |
| JMH-016624-0023 | 5 | 5 | no | All facts in the description are directly derived from the structured fields. | n/a |
| JMH-012025-0017 | 5 | 5 | no | No unsupported additions; all facts are derivable from the structured JA fields. | n/a |
| JMH-013609-0012 | 5 | 5 | no | No unsupported additions; all facts are derivable from the structured JA fields. | no |
| JMH-012025-0022 | 5 | 5 | no | No unsupported additions; all facts are derivable from the structured JA fields. | n/a |
| JMH-012130-0006 | 5 | 5 | no | No unsupported additions; all facts are derivable from the structured JA fields. | no |
| JMH-012238-0005 | 5 | 5 | no | All facts in the English description are derivable from the structured Japanese fields. | no |
| JMH-012335-0030 | 5 | 5 | no | All facts in the English description are derivable from the structured Japanese fields. | no |

