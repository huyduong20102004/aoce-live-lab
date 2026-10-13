# Actual AI benchmark validation

66/66 checks OK, errors=0.

| Check | Actual result | Detail |
| --- | --- | --- |
| Nine U1 samples and sixteen original U2 responses | OK | No fixture samples substituted for real CLI invocations |
| Frozen input actual-evidence.json | OK | Original declared input hash |
| Frozen input archive-reference.md | OK | Original declared input hash |
| Frozen input decision.schema.json | OK | Original declared input hash |
| Frozen input probe.schema.json | OK | Original declared input hash |
| Frozen input probe.txt | OK | Original declared input hash |
| Frozen input summary.schema.json | OK | Original declared input hash |
| Frozen input U1-A.txt | OK | Original declared input hash |
| Frozen input U1-B.txt | OK | Original declared input hash |
| Frozen input U1-C.txt | OK | Original declared input hash |
| Frozen input U2-fixtures.json | OK | Original declared input hash |
| Frozen input U2-v1-prompt.txt | OK | Original declared input hash |
| Frozen input U2-v1-RG-01.txt | OK | Original declared input hash |
| Frozen input U2-v1-RG-02.txt | OK | Original declared input hash |
| Frozen input U2-v1-RG-03.txt | OK | Original declared input hash |
| Frozen input U2-v1-RG-04.txt | OK | Original declared input hash |
| Frozen input U2-v1-RG-05.txt | OK | Original declared input hash |
| Frozen input U2-v1-RG-06.txt | OK | Original declared input hash |
| Frozen input U2-v1-RG-07.txt | OK | Original declared input hash |
| Frozen input U2-v1-RG-08.txt | OK | Original declared input hash |
| Frozen input U2-v3-prompt.txt | OK | Original declared input hash |
| Frozen input U2-v3-RG-01.txt | OK | Original declared input hash |
| Frozen input U2-v3-RG-02.txt | OK | Original declared input hash |
| Frozen input U2-v3-RG-03.txt | OK | Original declared input hash |
| Frozen input U2-v3-RG-04.txt | OK | Original declared input hash |
| Frozen input U2-v3-RG-05.txt | OK | Original declared input hash |
| Frozen input U2-v3-RG-06.txt | OK | Original declared input hash |
| Frozen input U2-v3-RG-07.txt | OK | Original declared input hash |
| Frozen input U2-v3-RG-08.txt | OK | Original declared input hash |
| Actual model call U1-A1 | OK | Exit0, complete usage from raw event, response schema, fixed model/effort/input hashes, zero action tools, ChatGPT auth |
| Actual model call U1-B1 | OK | Exit0, complete usage from raw event, response schema, fixed model/effort/input hashes, zero action tools, ChatGPT auth |
| Actual model call U1-C1 | OK | Exit0, complete usage from raw event, response schema, fixed model/effort/input hashes, zero action tools, ChatGPT auth |
| Actual model call U1-B2 | OK | Exit0, complete usage from raw event, response schema, fixed model/effort/input hashes, zero action tools, ChatGPT auth |
| Actual model call U1-C2 | OK | Exit0, complete usage from raw event, response schema, fixed model/effort/input hashes, zero action tools, ChatGPT auth |
| Actual model call U1-A2 | OK | Exit0, complete usage from raw event, response schema, fixed model/effort/input hashes, zero action tools, ChatGPT auth |
| Actual model call U1-C3 | OK | Exit0, complete usage from raw event, response schema, fixed model/effort/input hashes, zero action tools, ChatGPT auth |
| Actual model call U1-A3 | OK | Exit0, complete usage from raw event, response schema, fixed model/effort/input hashes, zero action tools, ChatGPT auth |
| Actual model call U1-B3 | OK | Exit0, complete usage from raw event, response schema, fixed model/effort/input hashes, zero action tools, ChatGPT auth |
| Actual model call U2-v1-RG-01 | OK | Exit0, complete usage from raw event, response schema, fixed model/effort/input hashes, zero action tools, ChatGPT auth |
| Actual model call U2-v3-RG-01 | OK | Exit0, complete usage from raw event, response schema, fixed model/effort/input hashes, zero action tools, ChatGPT auth |
| Actual model call U2-v1-RG-02 | OK | Exit0, complete usage from raw event, response schema, fixed model/effort/input hashes, zero action tools, ChatGPT auth |
| Actual model call U2-v3-RG-02 | OK | Exit0, complete usage from raw event, response schema, fixed model/effort/input hashes, zero action tools, ChatGPT auth |
| Actual model call U2-v1-RG-03 | OK | Exit0, complete usage from raw event, response schema, fixed model/effort/input hashes, zero action tools, ChatGPT auth |
| Actual model call U2-v3-RG-03 | OK | Exit0, complete usage from raw event, response schema, fixed model/effort/input hashes, zero action tools, ChatGPT auth |
| Actual model call U2-v1-RG-04 | OK | Exit0, complete usage from raw event, response schema, fixed model/effort/input hashes, zero action tools, ChatGPT auth |
| Actual model call U2-v3-RG-04 | OK | Exit0, complete usage from raw event, response schema, fixed model/effort/input hashes, zero action tools, ChatGPT auth |
| Actual model call U2-v1-RG-05 | OK | Exit0, complete usage from raw event, response schema, fixed model/effort/input hashes, zero action tools, ChatGPT auth |
| Actual model call U2-v3-RG-05 | OK | Exit0, complete usage from raw event, response schema, fixed model/effort/input hashes, zero action tools, ChatGPT auth |
| Actual model call U2-v1-RG-06 | OK | Exit0, complete usage from raw event, response schema, fixed model/effort/input hashes, zero action tools, ChatGPT auth |
| Actual model call U2-v3-RG-06 | OK | Exit0, complete usage from raw event, response schema, fixed model/effort/input hashes, zero action tools, ChatGPT auth |
| Actual model call U2-v1-RG-07 | OK | Exit0, complete usage from raw event, response schema, fixed model/effort/input hashes, zero action tools, ChatGPT auth |
| Actual model call U2-v3-RG-07 | OK | Exit0, complete usage from raw event, response schema, fixed model/effort/input hashes, zero action tools, ChatGPT auth |
| Actual model call U2-v1-RG-08 | OK | Exit0, complete usage from raw event, response schema, fixed model/effort/input hashes, zero action tools, ChatGPT auth |
| Actual model call U2-v3-RG-08 | OK | Exit0, complete usage from raw event, response schema, fixed model/effort/input hashes, zero action tools, ChatGPT auth |
| Actual model call U2-v1-RG-01-complete | OK | Exit0, complete usage from raw event, response schema, fixed model/effort/input hashes, zero action tools, ChatGPT auth |
| Actual model call U2-v3-RG-01-complete | OK | Exit0, complete usage from raw event, response schema, fixed model/effort/input hashes, zero action tools, ChatGPT auth |
| U1 independently recalculated config A | OK | 3samples, medians/ranges/usage partition match raw metadata; money/reviewer time not invented |
| U1 independently recalculated config B | OK | 3samples, medians/ranges/usage partition match raw metadata; money/reviewer time not invented |
| U1 independently recalculated config C | OK | 3samples, medians/ranges/usage partition match raw metadata; money/reviewer time not invented |
| U2 original fixture/version denominators | OK | Supplemental complete-positive excluded from original8 per version |
| Complete positive control accepted | OK | Same richer synthetic fixture for both versions, original RG01 retained |
| Four nonvacuous negative controls detected | OK | Actual accepted outputs corrupted by stale run/wrong department/arbitrary delete/toast oracle |
| Benchmark source revision matches historical runner evidence and Git history | OK | Frozen benchmark revision=68ae69680f53e68e541813c0f044c5d22067389a; current clean HEAD=c27f9b8eff44a4875f2922831890dc8d8abf1851; later app/CI commits are separate from the benchmark cohort |
| U1 actual runner evidence hash matches | OK | Underlying F01 reporter evidence not fabricated by model |
| No app credentials/capabilities in AI inputs or outputs | OK | Private-value comparison done locally; secret values never logged |
| Submission links resolve | OK | Original and AI supplementary document links present; frozen input archive is data, validated by source hash |

Schema checks do not replace semantic policy review. Actual model calls use synthetic U2 fixtures; app runtime evidence and model evaluations remain distinct. No provider invoice/monetary saving inference.
