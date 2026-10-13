# PR draft — Preserve employee oracle while reducing context

Mode: DRY-RUN / SIMULATED PR body, không đã mở PR. Sources: GIT-PACKET-04, AC-EMP-01/02, LAB-AOCE-05, VC-41–44. Proposed branch: fix/aoce-context-oracle-v3. Revision cuối: NOT CREATED. Human approval pending.

Candidate nén context đã đề xuất bỏ department và đổi ID+department search assertion thành Success toast. Điều này có thể nhận employee department sai là pass. Thay đổi được chọn giữ employee ID, department, actor, source/run và ownership trong selector; prompt gọn vẫn yêu cầu search row exact ID+selected department và matching runner evidence.

Final scope gồm prompt v3/selector theo budget 250 từ, regression wrong department/stale run/missing source, và sanitized validation summary gắn revision cuối. Không chấp thuận three retries hay bỏ ownership check. Bản thiết kế dùng retries=0 để chẩn đoán; exception ≤1 runner retry cần proven safe setup/cleanup và controller budget.

Validation evidence hiện có là packet giả lập: VC-41 typecheck exit 0 ở lab-a1; VC-42 chỉ liệt kê ba tests ở lab-a1; VC-43 browser startup exception trước test body; VC-44 candidate revision khác lab-a1 và chưa checks. **Không có live pass cho candidate.** Cần typecheck, RG-01/03/04/08 và negative controls, discovery count, selected runtime execution với unchanged oracle, reporter/assertion/artifact linkage và cleanup cho revision cuối. Local checks của bài nộp chỉ ở [report](../../evidence/validation-report.md).

Rủi ro còn lại: prompt hợp lệ chưa bảo đảm controller enforcement; context cap có thể cắt mất role/source; environment issue có thể vẫn chặn runtime; lookup/search SLA chưa cấp. Gate pilot: đầy đủ source fields, negatives reject đúng, current-revision evidence, no unresolved write/cleanup và namespace được trainer review.

Rollback: revert scoped commits để về prompt/selector đã review, giữ source snapshots và audit logs. Code rollback không undo employee writes: pause write, reconcile exact owned ledger rồi cleanup theo approved helper; unknown ownership/outcome chuyển QA data xử lý. Không reset/xóa dữ liệu bằng prefix. Owner đề xuất QA context + lab maintainer; quyết định/assignment chưa được người thật xác nhận.

Review decision log: ACCEPT restore department (AC-EMP-02); REJECT toast proof (AC-EMP-01/02); ACCEPT 250 budget có manifest separate (U2); REJECT VC-42 là execution evidence (VC-42/44). Chi tiết locations và >=3 findings trong [change review](U4_change-review.md).
