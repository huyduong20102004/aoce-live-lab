# U1 — actual Codex CLI benchmark

CLI codex-cli 0.160.0, requested model gpt-6.1-sol, reasoning high; ChatGPT authentication. Actual calls, not BENCH-PACKET-01 sample rows.

Same retrospective F01 task/evidence/schema; source actual run mv0nfj0v-fcf1b44e, lab SHA 68ae69680f53e68e541813c0f044c5d22067389a. A full archive/full prompt, B short context/short prompt, C targeted context/source guards. Three samples each, fixed counterbalanced order recorded in protocol.

| Sample | Input total | Cached | Uncached derived | Output | CLI seconds | Score | Gate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| A1 | 31791 | 0 | 31791 | 1208 | 45.846 | 10 | ACCEPT |
| B1 | 9304 | 0 | 9304 | 465 | 21.223 | 8 | ACCEPT |
| C1 | 9781 | 0 | 9781 | 887 | 35.291 | 8 | ACCEPT |
| B2 | 9302 | 0 | 9302 | 533 | 20.471 | 8 | ACCEPT |
| C2 | 9781 | 0 | 9781 | 749 | 27.301 | 8 | ACCEPT |
| A2 | 31789 | 0 | 31789 | 997 | 40.184 | 10 | ACCEPT |
| C3 | 9783 | 0 | 9783 | 893 | 32.775 | 8 | ACCEPT |
| A3 | 31787 | 0 | 31787 | 925 | 38.837 | 10 | ACCEPT |
| B3 | 9300 | 0 | 9300 | 569 | 23.214 | 8 | ACCEPT |

| Config | Input median [range] | Output median [range] | CLI seconds median [range] | Accepted | Money total / cost per accepted |
| --- | --- | --- | --- | --- | --- |
| A | 31789 [31787–31791] | 997 [925–1208] | 40.18411160004325 [38.83730040001683–45.84608359995764] | 3/3 | UNKNOWN / UNKNOWN |
| B | 9302 [9300–9304] | 533 [465–569] | 21.223197199986316 [20.47116400010418–23.214404799975455] | 3/3 | UNKNOWN / UNKNOWN |
| C | 9781 [9781–9783] | 887 [749–893] | 32.77544720005244 [27.300671999924816–35.29069559997879] | 3/3 | UNKNOWN / UNKNOWN |

Usage values are raw CLI turn.completed input/cached/output fields, not word-count estimates. `uncached_derived=input_total-cached` is a reporting partition using cached as a subset; monetary accounting remains UNKNOWN. Raw cache_write/reasoning fields retained in measurements. Reasoning/output fields are not added twice. Provider request count is UNKNOWN; one CLI invocation/one completed turn is not proof of one underlying API request.

CLI wall seconds include client startup/auth/network/model/final-output serialization; not pure model latency or CI billable minutes. No human QA review-minute measurement; automated checker timing is separate. Preparation probes excluded from A/B/C cohort and retained under calls/probe*.

Prompt and context change together, cache state/order and ephemeral cwd/backend variability are confounders. Shared schema and complete current evidence can protect short prompts, so outcomes must not be inferred from synthetic B cards. n3 per configuration cannot establish reliability/production savings; actual model backend snapshot beyond requested alias is not supplied.

[Ledger CSV](U1_actual-ledger.csv), [raw results](results.json), [protocol](protocol.json), [negative controls](negative-controls.json). Individual response/measurement/review files are in calls/.
