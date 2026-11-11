# Validation record

## Repository refresh: November 11, 2026

Executed on Windows with Python 3.13:

- **4 desktop tests passed:** profile/history separation, URL and transport handling, a simulated GUI conversation and organizer flow, and draft preservation after connection failure.
- **7 gateway tests passed:** authentication/revocation, model validation/rate limits, request limits, job ownership, queue capacity, compatible response contract/upstream failure, and browser-origin restrictions with authentication preserved.
- JavaScript syntax checks passed for `web/app.js` and `web/download.js`.

The test suites use simulated upstream responses and temporary databases. They do not require or certify a live LM Studio model. The server test run emits an upstream Starlette warning about future HTTPX test-client compatibility; the tests currently pass.

GitHub Actions runs the Python suites on Windows and JavaScript syntax checks on Linux. A green workflow establishes these checks only; it does not establish production uptime or a security audit.

## Previous integration work: September 2026

- A browser client received a real response from the self-hosted gateway and LM Studio using a temporary key. That test does not establish current server availability.
- Browser smoke checks exercised simulated authenticated chat, model selection, safe text rendering, new conversations, tutorials, mobile layout, and installer reconstruction.
- The installer was smoke-installed in an isolated directory and the installed executable hash matched its source binary. A fresh launch on another Windows PC was not established by that check.

## Packaged desktop snapshot

The preserved installer is version **0.4.0**, built during the September delivery. It is unsigned and contains no model weights. The November repository refresh republishes that existing artifact; it is not a new binary build. The raw desktop executable is distributed as a release asset rather than a newly tracked source file.

Installer size: **51,872,499 bytes**.

SHA-256 of `Betelgeuse-Setup.exe`:

```text
9ac5354f63f1c4ac6cb176fdca3afa3e02656d4e805e9da9ad8ac8b435f8f6e5
```

The static download manifest contains individual part hashes. Combined bytes must match the installer hash above. Build scripts are included; exact binary reproducibility is not asserted.
