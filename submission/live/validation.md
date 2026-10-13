# Local live validation

Generated 2026-10-09T15:29:50.641416+07:00. Source revision `68ae69680f53e68e541813c0f044c5d22067389a`.

29/29 checks OK; 0 errors.

| Check | Actual result | Evidence/limitation |
| --- | --- | --- |
| Actual source revision and clean Git tree | OK | 68ae69680f53e68e541813c0f044c5d22067389a |
| No credentials/raw auth/state/artifacts tracked | OK | Only reviewed source paths tracked |
| Original source packets unchanged | OK | Handout/content hashes match original snapshot |
| Actual TypeScript check | OK | Compiler command and current revision captured |
| Actual controller regression | OK | 15 deterministic tests incl RG01–08, negative controls and auth redaction; not model calls |
| Runtime missing-secret/no-tests/forged-trigger gates | OK | Actual child script exits; no app writes |
| Run evidence integrity mv0msou8-a3f5c23f | OK | revision=f9a0f8721ec9e11667050b1192abe686da7810ae; cases=3; owned IDs=3; screenshot hashes checked |
| Run evidence integrity mv0mv3dh-4849517b | OK | revision=b4f9af08af98236f698b11b9471138fb7d0b47bc; cases=3; owned IDs=3; screenshot hashes checked |
| Run evidence integrity mv0mv87p-723cef25 | OK | revision=b4f9af08af98236f698b11b9471138fb7d0b47bc; cases=11; owned IDs=33; screenshot hashes checked |
| Run evidence integrity mv0mxt3m-5c736751 | OK | revision=b4f9af08af98236f698b11b9471138fb7d0b47bc; cases=3; owned IDs=3; screenshot hashes checked |
| Run evidence integrity mv0mzz1g-18362a62 | OK | revision=8da3165ce08ebc090dbd13679214fcbf5c7edfe9; cases=3; owned IDs=3; screenshot hashes checked |
| Run evidence integrity mv0n03oi-a9547ca3 | OK | revision=8da3165ce08ebc090dbd13679214fcbf5c7edfe9; cases=11; owned IDs=33; screenshot hashes checked |
| Run evidence integrity mv0n31fl-c686a80c | OK | revision=d250e708264345ad2c6b700e9c66d19232c012c3; cases=3; owned IDs=3; screenshot hashes checked |
| Run evidence integrity mv0n361t-b648196b | OK | revision=d250e708264345ad2c6b700e9c66d19232c012c3; cases=11; owned IDs=33; screenshot hashes checked |
| Run evidence integrity mv0n59ry-c4fc10dc | OK | revision=d250e708264345ad2c6b700e9c66d19232c012c3; cases=3; owned IDs=3; screenshot hashes checked |
| Run evidence integrity mv0n72e1-3c08d864 | OK | revision=39902a624538d91b9ce0c6bbbb92260481b2abe2; cases=3; owned IDs=3; screenshot hashes checked |
| Run evidence integrity mv0n77qg-c63b0265 | OK | revision=39902a624538d91b9ce0c6bbbb92260481b2abe2; cases=11; owned IDs=33; screenshot hashes checked |
| Run evidence integrity mv0n9aob-6bcdfc74 | OK | revision=39902a624538d91b9ce0c6bbbb92260481b2abe2; cases=3; owned IDs=3; screenshot hashes checked |
| Run evidence integrity mv0nfj0v-fcf1b44e | OK | revision=68ae69680f53e68e541813c0f044c5d22067389a; cases=3; owned IDs=3; screenshot hashes checked |
| Run evidence integrity mv0nfnvq-faeb5798 | OK | revision=68ae69680f53e68e541813c0f044c5d22067389a; cases=11; owned IDs=33; screenshot hashes checked |
| Run evidence integrity mv0nhq5q-5bc239db | OK | revision=68ae69680f53e68e541813c0f044c5d22067389a; cases=3; owned IDs=3; screenshot hashes checked |
| Current revision has manual three-flow smoke | OK | Actual runner assertions, no discovery-only substitution |
| Current revision full robustness suite | OK | 3 business cases +8 controls; negative-control passes are detection results |
| Historical failures retained | OK | mv0mm4yl-1e3694b0, mv0mmqly-2d3e1e4a, mv0mnbio-7d9ddcf5, mv0mnwwh-acbc4787, mv0mpki6-2c57eadc; not overwritten as pass |
| Actual OS scheduled launch, separate from manual | OK | Requires manifest task marker plus observed Task Scheduler result0; no GitHub scheduled claim |
| Export does not contain actual private secrets | OK | Local secret comparison performed without logging secret values |
| No remaining E2E owned employees | OK | State inspected locally; values/credentials not exported |
| Unowned demo employee preserved | OK | Cross-owner cleanup negative control protected demo |
| Submission and lab Markdown links resolve | OK | Dry-run and live-local references present |

No production reliability/provider-price/AI-model benchmark or GitHub hosted run claim. Controller regressions use synthetic input fixtures, but actual checker execution is captured. Windows scheduled evidence is OS-local and needs an active signed-in session and powered-on machine.
