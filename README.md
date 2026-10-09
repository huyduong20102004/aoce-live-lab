# AOCE PortalLite — local live lab

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

Private raw evidence/state/grants: .lab ignored. Sanitized evidence: ../bai-nop-AOCE/live/runs. Model không chạy ở runtime; usage N/A, modelcalls0; không benchmark AI/pricing thực tế. GitHub workflow trong source là sẵn để tích hợp, actual remote runs cần connected remote.

Watchdog: `npm run lab:watchdog` reconcile expired-owned runs, giữ nonzero khi unknown/unresolved. Không delete mọi nhân viên. Task Scheduler setup/status scripts sẽ ghi proof riêng khi khả dụng; daily smoke01:17 Việt Nam dùng giờ UTC+7, chỉ bật sau manual success. Forced cancellation vẫn có thể bỏ in-job cleanup; watchdog là cơ chế ngoài job khi server/credentials còn sẵn.

Nguồn kỹ thuật đối chiếu2026-10-09: [Playwright reporters](https://playwright.dev/docs/test-reporters), [Playwright CI](https://playwright.dev/docs/ci-intro), [Playwright local server](https://playwright.dev/docs/test-webserver). UI/controller/API endpoints/fault semantics là contract local mới, không source product được trainer chứng nhận.
