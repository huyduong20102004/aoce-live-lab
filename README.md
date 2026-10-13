# AOCE PortalLite — local live lab

[![GitHub Actions](https://github.com/huyduong20102004/aoce-live-lab/actions/workflows/lab.yml/badge.svg)](https://github.com/huyduong20102004/aoce-live-lab/actions/workflows/lab.yml)

**Bài nộp:** [Mục lục 7 lab và evidence](submission/README.md). Repo Public này gồm source app/tests, 17 deliverables và bằng chứng đã lọc. [Hướng dẫn CI](docs/GITHUB-CI.md). Badge phản ánh workflow status; PR static checks không thay live browser assertions.

**Hosted CI đã thực thi:** [PR checks](https://github.com/huyduong20102004/aoce-live-lab/actions/runs/38337908837) và [manual Chromium smoke3/3](https://github.com/huyduong20102004/aoce-live-lab/actions/runs/38338108312). [Permanent sanitized CI evidence](submission/hosted-ci/README.md). Scheduled daily run được gated theo manual-validated SHA; không gọi manual event là schedule proof.

Webapp và test project do Codex tạo để thực thi AC-EMP-01/02 và LAB-AOCE-03/04/05 trên máy này. App chạy tại **http://127.0.0.1:4173**. Source, data và quyền của lab tách với các packets giả lập; xem [local contract](docs/LOCAL-LAB-CONTRACT.md).

## Khởi động

```powershell
npm ci
npm run lab:init
node node_modules/playwright/cli.js install chromium
npm start
```

`lab:init` chỉ tạo .env với password random và seed3 nhân viên local khi chưa có; không reset dữ liệu cũ. Accounts: admin-lab và viewer-lab. Xem password tại .env trong project trên máy; không commit/chia sẻ raw file. UI đăng nhập có Username/Password, Admin create/edit, Viewer disabled create. Server chỉ bind loopback, không cần public hosting.

## Kiểm chứng

```powershell
npm run typecheck
npm run context:regression
npm run lab:smoke
npm test
npm run lab:metrics
```

Run scripts yêu cầu source committed/clean và finalSHA thật, tạo unique run, preflight roles/build/namespace/lease, discovery, runner, always read-first exact owned reconciliation, manifest/evidence gate và sanitized export. Smoke3 flows; full suite bổ sung control locator/unknown-write/iframe/negative oracles/role403/ownership/environment fault. Retry0. Tests tự khởi động server nếu chưa có, dừng server do test tự tạo sau run; server được start ngoài test được giữ để bạn dùng.

Private raw evidence/state/grants: .lab ignored. Layout local ban đầu export sanitized evidence sang ../bai-nop-AOCE/live/runs. Trong GitHub CI dùng LAB_EVIDENCE_DIR=evidence-export/live để giữ export trong checkout; file này cũng được ignore khỏi source. Runtime tests không gọi model. [Benchmark Codex CLI thực tế U1/U2](submission/live/ai/README.md) là cohort riêng và monetary billing vẫn UNKNOWN. GitHub PR/manual run evidence được ghi khi Actions thực sự hoàn tất, không suy từ local green.

Watchdog: `npm run lab:watchdog` reconcile expired-owned runs, giữ nonzero khi unknown/unresolved. Không delete mọi nhân viên. Task Scheduler setup/status scripts sẽ ghi proof riêng khi khả dụng; daily smoke01:17 Việt Nam dùng giờ UTC+7, chỉ bật sau manual success. Forced cancellation vẫn có thể bỏ in-job cleanup; watchdog là cơ chế ngoài job khi server/credentials còn sẵn.

Nguồn kỹ thuật đối chiếu2026-10-09: [Playwright reporters](https://playwright.dev/docs/test-reporters), [Playwright CI](https://playwright.dev/docs/ci-intro), [Playwright local server](https://playwright.dev/docs/test-webserver). UI/controller/API endpoints/fault semantics là contract local mới, không source product được trainer chứng nhận.

## Bài nộp và bằng chứng

- [Bài giải 7 lab theo folder](submission/labs/README.md).
- [Bằng chứng live mới nhất](submission/live/recovery/README.md).
- [Mục lục đầy đủ](submission/README.md).
