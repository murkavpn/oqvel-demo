# OQVEL public demonstration

Public URL: https://murkavpn.github.io/oqvel-demo/

This repository contains an audited static export only. The private application source, backend, environment files, databases, payment configuration and credentials are excluded.

Payments (including Telegram purchase actions), authentication, registration, recovery, activation and subscription operations are unavailable. The demo sends no API requests and has no forms. Public informational links remain available.

GitHub Actions verifies every file against the SHA-256 manifest, unpacks the static release, builds it with Astro, verifies the resulting output again and deploys only `dist` using GitHub Pages. No production API is configured. CSP blocks connections and form submissions.

## Update after UI changes

1. In the private local application, run checks, tests and `npm run build:demo` with `GITHUB_REPOSITORY=murkavpn/oqvel-demo`.
2. Run `node scripts/export-demo.mjs <absolute-release-folder>`.
3. Replace `demo-static.tar.gz` and `demo-manifest.json` together in this repository. Update the build/audit helpers only when they have changed.
4. The main-branch Actions workflow audits, builds and deploys. Confirm its green result, then open the real HTTPS URL and run desktop/mobile QA.

The original private repository remains private. This workflow cannot deploy the production backend or modify the existing Cloudflare site.
