verdict: continue
Rule 22(b) PASS on Planner review of the DEV diff (fetch_xml.py). Mechanical gate clean. Confirmed the proven-mechanism transport + both walk capture-contract folds at HEAD:
- nt path now shells out to `powershell -NoProfile -ExecutionPolicy Bypass -Command <script>` running `Invoke-WebRequest -UseDefaultCredentials -UseBasicParsing`, adding `-AllowUnencryptedAuthentication` only when `$PSVersionTable.PSVersion.Major -ge 6` (mirrors the proven q7 probe). curl removed on nt.
- w1-2 encoding: `[Console]::OutputEncoding = UTF8Encoding($false)` forces utf-8; Python captures utf-8 stdout -> body_bytes -> existing XML guard + mkstemp/os.replace (no cp1252 round-trip). URL passed via IP_FETCH_TARGET_URL env var (injection-safe). CREATE_NO_WINDOW (0x08000000) retained so powershell.exe does not flash a window.
- w1-1: status/body split on the FIRST newline (raw_output.find(b'\n')); WebException emits the response status so 404->not_found/401->auth_fail still map.
- Status taxonomy, response-is-XML guard, atomic write all unchanged.
Tests: 41 passed / 0 failed, including test_utf8_body_roundtrip (non-ASCII round-trip) and test_multiline_body_splits_on_first_newline. Proceeding to Step 2 (QA).
