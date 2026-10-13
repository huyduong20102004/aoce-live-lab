# U6 — Locator fixes, unknown-write recovery và validation

Mode: DRY-RUN / DESIGN-REVIEWED (AI). Sources: INC-61/62/63/64, LAB-AOCE-05, AC-EMP-01/02, LAB-AOCE-03, POLICY-PACKET-AOCE. Pseudocode chưa implementation/live pass; UI elements ngoài DOM card phải inspect live trước dùng. Draft và triage: [draft](review/00_analysis-first-draft.md), [incidents](U6_incident-triage.md).

## INC-61 — Scoped locator và condition wait

```ts
// Pseudocode sau khi reviewed fixture đã điền Employee ID/Department.
const dialog = page.getByRole('dialog', { name: 'Create employee', exact: true });
await expect(dialog).toHaveCount(1);
await expect(dialog).toBeVisible();
const save = dialog.getByRole('button', { name: 'Save', exact: true });
await expect(save).toHaveCount(1);
// Click auto-waits visibility/stability/enabled/receives-events; deadline vẫn enforced.
// Nếu cần explicit overlay wait, locator phải từ inspect DOM mới, không invent CSS.
await save.click(); // Journal write intent và dispatch trong reviewed runner fixture.
await reviewedSearchExactEmployeeId(employeeId); // Helper contract, chưa endpoint.
const row = page.getByRole('row').filter({
  has: page.getByRole('cell', { name: employeeId, exact: true }),
});
await expect(row).toHaveCount(1);
await expect(row.getByRole('cell', { name: 'QA', exact: true })).toBeVisible();
```

Scope dialog giải ambiguity dựa INC-61; không dùng first/force/fixed sleep. [Actionability](https://playwright.dev/docs/actionability) kiểm action target, không business transaction; [retrying assertions](https://playwright.dev/docs/test-assertions) kiểm expected row/department đến test deadline. Overlay hidden selector Not specified, phải inspect nếu explicit wait; không bịa `.overlay`.

Unique-ID assertion cần approved setup lookup/reservation, không chỉ row count sau create; giữ F01 precondition/source assertion trong spec. Nếu click timeout sau possible dispatch thì chuyển UNKNOWN write recovery; không automatic second click.

## INC-63 — Iframe/virtualization

```ts
const frame = page.frameLocator('iframe[title="Employee directory"]');
// Card chỉ nói Search textbox trong iframe, không cấp accessible name.
// Nếu inspect xác nhận đây là duy nhất textbox, dùng role; nếu nhiều, block để inspect.
const search = frame.getByRole('textbox');
await expect(search).toHaveCount(1);
await search.fill(employeeId);
await reviewedApplyExactSearch(frame); // Trigger contract chưa specified; không invent Enter/button.
const row = frame.getByRole('row').filter({
  has: frame.getByRole('cell', { name: employeeId, exact: true }),
});
await expect(row).toHaveCount(1);
await expect(row.getByRole('cell', { name: 'Engineering', exact: true })).toBeVisible();
```

Frame selector từ INC-63; row/cell roles cần live DOM xác nhận (pseudocode). Search giúp render target; scroll/search không assertion. Nếu UI không row sau bounded wait: record lookup existing chỉ hỗ trợ triage, outcome UNKNOWN/FAILED theo runner evidence, không F02 pass. [Frames docs](https://playwright.dev/docs/frames) hỗ trợ scope qua frameLocator. Không force virtualized missing target hoặc đổi oracle thành API exists.

## INC-62 — Recovery state table

Budget chung: 20 phút tổng, read recovery tối đa 1 (initial lookup + tối đa 1 recovery; mọi read trong tổng wall-time), runner retry tối đa 1 khi safe, default 0 trong CI. Nếu runtime contract lớp quy read limit khác cần review, không multiplicative retry ở wrappers. Owner đề xuất QA recovery; unresolved cleanup owner QA data.

| State / evidence | Allowed actions | Blocked actions | Transition / report / termination |
| --- | --- | --- | --- |
| WRITE-INTENT: durable exact owner ledger trước Save | Reviewed first write khi preflight/lease đủ | Write không ledger/owner | WRITE-DISPATCHED, timestamp/ref tracked |
| WRITE-UNKNOWN: client timeout t1500 | lookup_owned_record exact ID, read_run_result; read-only recovery ≤1 | Save lại, create another record để bypass, cleanup chưa verified owner | Freeze; UNKNOWN đến authoritative reconciliation |
| CREATED-OWNED: t2600 lookup ref62/QA | inspect/search exact ID+QA; read matching runner; cleanup helper khi state safe | Duplicate Save; pass từ lookup-only | VERIFY-PENDING; record exists không chứng minh AC-EMP-02 |
| VERIFY-PENDING: search t2100 chưa row | Condition-based read assertions tới lab timeout/remaining budget | Tăng retries vô hạn, nới oracle/toast, invent index SLA | Matching assertion pass/fail hoặc UNKNOWN khi reporter thiếu |
| VERIFIED hoặc failed assertion nhưng created owned known | cleanup_owned_record exact ref với ledger/token; lookup state nếu helper outcome unknown trong read budget | Delete prefix/unowned records; runner retry trước cleanup resolved | Cleanup success→operational resolved; assertion outcome giữ nguyên |
| AUTHORITATIVE-NOT-FOUND: possible alternative fixture state | No-record proof lưu; cleanup N/A nếu no write proved; assess safe new attempt setup | Tự coi delayed/inconclusive lookup là authoritative absent | Retry chỉ khi reviewed semantics xác nhận old write cannot later commit và safe setup/cleanup; nếu chưa có contract→STOP UNKNOWN |
| LOOKUP-INCONCLUSIVE/owner mismatch/budget exhausted | Ghi durable unresolved ref/owner/next proof; stop mutating | Retry write, arbitrary delete, report passed | UNKNOWN/BLOCKED; external lab owner reconcile lease |
| CLEANUP-FAILED/UNKNOWN | Báo assertion outcome riêng, unresolved issue; external authorized reconcile | Suppress error hoặc new runner attempt | STOP operational failure/unknown, no rerun đến safe |

Tại timeline thực tế của fixture INC-62: t2600 đã created owned → chỉ verify/search rồi cleanup; chưa đủ evidence kết luận pass vì runner/search/cleanup chưa có. Cleanup intent không thành cleanup success. Không invent lookup URL hoặc direct DB rights; chỉ synthetic tool-card helper.

## INC-64 report mẫu

```text
Mode: DRY-RUN; Label: SIMULATED BLOCKED-ENVIRONMENT
Source: INC-64; selected count/revision/build Not specified
Browser startup permission exception trước test body; no application assertions.
Reporter incomplete; no click/write evidence supplied, ledger status UNKNOWN nếu không có proof riêng.
No app flaky/root-cause-fixed verdict. Owner proposed: lab operator.
Next proof: runner user/permissions/dependency logs, authorized no-write ledger,
then one reviewed execution with reporter/unchanged oracle after environment repair.
```

## Before/after validation plan và negative controls

1. Baseline giữ code lab-a6/config/prompt/build/inputs khi tái hiện INC-61; fixed code là revision mới phải ghi rõ. Hai revisions khác nhau được so sánh trên cùng non-fix inputs, không nói same revision giữa before/after. INC-63/64 không cấp revision nên ghi unknown đến trainer cấp.
2. Tái hiện có phép trong isolated-lab; fresh run/attempt IDs, independent F02 seed, separate Viewer context; không reuse prior result. Lưu trace/reporter/assertion/owned cleanup và exact fixed revision.
3. Đề xuất ≥3 isolated samples/incident mỗi before/after để kiểm design, vẫn không proof reliability. Với unknown write không intentionally blind resend; use authorized synthetic fault injection hoặc recorded packets nếu chưa permission live.
4. Giữ oracle source; timing limits là lab config. Report mọi attempts và blocked samples, không rerun đến xanh. Positive path INC-61 scoped Save + exact ID/QA và INC-63 exact ID/Engineering phải distinguish negatives.

| Negative control | Expected behavior | Detects |
| --- | --- | --- |
| NC-U6-01 exact ID nhưng department Sales | AC-EMP-02/LAB-AOCE-03 assertion reject | Toast/API-exists false pass, mất department |
| NC-U6-02 row khác ID, cùng department đúng | Exact target row count=0 hoặc mismatch, reject | Fuzzy row hoặc `.first()` bỏ ID |
| NC-U6-03 second Save requested sau timeout, lookup inconclusive | Controller blocks mutation, UNKNOWN | Blind retry unknown write |
| NC-U6-04 permission exception trước body | BLOCKED-ENVIRONMENT, not app fail/pass | Environment mislabeled flaky |

Review log: ACCEPT dialog scope/actionability thay force (INC-61); REJECT invented iframe search button/Enter (INC-63 trigger unknown); ACCEPT clarify before/after revisions (lab-a6 fixed diff phải revision mới); REJECT authoritative absence alone⇒retry khi eventual server commit semantics unknown (LAB-AOCE-05). Local checks count incidents/controls/links; no live reproduction or tests. Human/lab approval và runtime evidence pending.
