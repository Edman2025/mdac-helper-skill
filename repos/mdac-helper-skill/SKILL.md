---
name: mdac-helper
description: Fill Malaysia Digital Arrival Card (MDAC) registration form at imigresen-online.imi.gov.my reliably during browser automation. Use when fields keep reverting/concatenating, by setting values via stable input element IDs (dob, passExpDte, email, confirmEmail, mobile, arrDt, depDt, vesselNm, accommodationAddress1/2, accommodationPostcode). Does NOT solve captcha; prompts user to complete slider puzzle manually.
---

# MDAC helper

## Workflow

1) Open MDAC registration page:
- https://imigresen-online.imi.gov.my/mdac/main?registerMain

2) Select dropdowns normally (Nationality, Sex, Country/Region code, Mode of Travel, Last Port, Accommodation, State, City).

3) Build a `payload.json`.

- If a local profile exists at `<workspace>/private/mdac_profile.json`, prefer it (contains static passport/email/address).
- Use `scripts/mdac_build_payload.py --out payload.json`.
  - If the user says “明天去、后天回”, assume **arrive=today+1**, **depart=today+2** (DD/MM/YYYY).
  - Default checkpoint preference (if not specified): **Woodlands / Causeway**.

4) Fill text inputs via DOM IDs (reliable; avoids UI “revert/concatenate” issues).

Options:
- **Terminal one-command (OpenClaw browser)**: run `scripts/mdac_fill_openclaw.py payload.json`.
- **Agent automation**: use `scripts/fill_mdac_ids.js` via `browser.act kind=evaluate`.
- **User-assisted**: run `scripts/mdac_oneclick.py payload.json` to copy a JS snippet to clipboard; paste into the page DevTools Console.

5) Ask user to complete the slider puzzle captcha.

6) User completes the slider puzzle captcha.

7) **Post-captcha revalidation (important):** immediately re-run the ID-based fill for critical fields (dates + region code) because the page can re-render and visually reset them after captcha success.

8) Click Submit.

## Datepicker (calendar popup) close

After filling date fields, ensure the calendar popup is closed before verification or captcha:
- Press **Escape** (once or twice)
- Force blur: `document.activeElement?.blur?.()`

Details: see `references/datepicker-close.md` and `references/mdac-gotchas.md`.

## Notes / Gotchas (经验教训)

- **日期输入框是 readonly**（dob/passExpDte/arrDt/depDt），直接 `.value=` 可能不生效：需要先移除 readonly 再触发 input/change。
- **下拉框也必须自动化**（Nationality / Place of Birth / Sex / Region code / Mode / Last Port / Accommodation / State / City），否则会漏填。
- **Region code 存在重复 value**（例如 value=1 可能对应多个国家）：选择时要优先按 *value + option text* 精确匹配；区号 **65 必须选 SINGAPORE**。
- State → City 有联动：先 set State，再等待 City options 加载后再选 City。
- Address 字段只允许字母数字空格；把逗号替换为空格。
- 如果字段看起来填了但提交/验证码后被重置：立刻重跑“ID + select”填充一遍再点 Submit。
