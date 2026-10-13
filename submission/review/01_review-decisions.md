# Review step 2 — Đối chiếu sau draft đã lưu

Ngày 2026-10-07 (UTC+7). Reviewer: Codex tự review, không independent QA/peer. Draft input có thật: [00_analysis-first-draft.md](00_analysis-first-draft.md). Sources là handout/course content và official docs được đọc trong phiên. Không claim model benchmark calls hoặc human approval. Các accept/reject là QA decisions đề xuất của lời giải AI.

| ID | Finding / proposal | Source | Accept/reject và correction thực tế |
| --- | --- | --- | --- |
| RV-01 | Draft U7 ghi subtotal0.99 | 10 row subtotals METRIC-PACKET-07 | ACCEPT correction0.89; Decimal script và U7 memo/metrics dùng0.89, draft giữ nguyên để truy vết |
| RV-02 | U1 intermediate B schema1/tổng2 dù thiếu synthetic label/unknowns | OUTPUT-PACKET-01 và schema/label rubric | ACCEPT correction schema0/tổng1 cho B1–3; ledger generator và final table đã sửa; gate vẫn REJECT |
| RV-03 | Cost C phải gồm C3 dù rejected/missing | RATE-SYN-01 và C3 | ACCEPT all-row lower bound0.254075, CPE accepted≥0.1270375; REJECT dùng C1/C2 total0.176075 làm config total |
| RV-04 | Current-pass từ EV-other-1 | U1 C3 / RG-03 | REJECT; pointer belongs previous run, require exact linkage và UNKNOWN gap |
| RV-05 | Actor trong CTX-03 tự đủ chứng minh HR Admin | CTX-03/REQ/RG-08 | REJECT; actor source REQ/prompt v1 + live role preflight, compact/source manifest ghi rõ |
| RV-06 | v2 retry-until-success/clean-old giữ nghĩa v1 | U2 v1/v2/LAB-AOCE-05 | REJECT; v3 freeze unknown write, exact ownership và bounded budgets |
| RV-07 | F03 dùng HR enabled observation hoặc UI security proof | OBS-34/LAB-AOCE-04 | REJECT; separate Viewer context, UI fixture boundary, backend unknown |
| RV-08 | Conflict chọn budget400 và Success toast để gọn | U4 conflict/U2 budget250/AC-EMP-02 | REJECT; merged250 + ID/department + matching evidence + UNKNOWN, source manifest separate |
| RV-09 | VC-41/42 chứng minh candidate runtime | VC-41–44 | REJECT; old revision typecheck/discovery, VC-43 infra blocked, candidate pending |
| RV-10 | always cleanup bảo đảm force cancellation | CI-55 / U5 scaffold | REJECT; add durable ledger/external reconciler prerequisites và explicit no guarantee |
| RV-11 | Group theo branch hoặc no-tests exit0 | CI-53/56/RUN-B | REJECT; environment group, no pass-with-no-tests, discovery expected set và evidence gate |
| RV-12 | Upload test-results nguyên thư mục không cần sensitivity boundary | U4 auth inventory / Playwright CI artifact docs | REJECT; safe export contract/restrictive store, no auth source/log; no public raw trace |
| RV-13 | IFC textbox trigger/overlay CSS có thể đoán | INC-61/63 DOM cards | REJECT; locator only sourced values, inspect uniqueness, reviewedApplyExactSearch chưa trigger cụ thể |
| RV-14 | authoritative not-found đủ cho late-write retry | INC-62 / LAB-AOCE-05 | REJECT tự động; late commit semantics chưa cấp, cần proven safe before rerun |
| RV-15 | Before/after fix same revision | INC-61 lab-a6 / VC-44 semantics | ACCEPT clarification: giữ same non-fix config/inputs, fix revision khác phải recorded |
| RV-16 | E08 cleanup unknown nghĩa full evidence pass denominator4 | METRIC-PACKET-07 full rubric/dictionary | REJECT cho defined metric; 5 full-evidence passes, cleanup và usage report riêng |
| RV-17 | Missing SL-04 thêm case failed/zero delay | Schedule packet SL-04 | REJECT; separate4-slot denominator, delay UNKNOWN, case selected vẫn10 |
| RV-18 | Dates/owners được assign / production-ready | U7 draft, lack runtime/assignment | REJECT; proposed owners/dates, conditional pilot, runtime pending |
| RV-19 | Validator initial regex lấy thêm prose C3 output card vào usage table | Handout có hai bảng chứa row C3 | ACCEPT fix select đúng 9-column BENCH usage table; arithmetic đối chiếu source không đổi |
| RV-20 | Typecheck đầu thiếu explicit Node types/lib trong temporary compiler setup | [Initial compiler diagnostics](../evidence/typecheck-initial-attempt.txt) | ACCEPT setup correction: working dir đúng temporary package, @types/node22, --types node + ESNext.Disposable lib; config source không đổi; [final output](../evidence/typecheck-output.txt) exit0 |

Chưa có external peer/human QA xác nhận các quyết định. [Validation report](../evidence/validation-report.md) chỉ actual local checks; source packets giữ nguyên. Không backdate human manual-first. Trainer cần review riêng nếu dùng để chấm completion.
