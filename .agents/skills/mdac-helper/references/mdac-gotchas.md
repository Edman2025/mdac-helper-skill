# MDAC gotchas (observed)

## 1) Datepicker popups persist
Even after filling dates programmatically, calendar popups may remain visible.

**Close sequence (safe):**
- Press `Escape` 1–2 times
- `document.activeElement?.blur?.()`
- Click a safe area (e.g., near captcha) to remove focus

Avoid heuristic DOM hiding by month/day text: it can accidentally hide layout containers.

## 2) Region (phone country code) can reset
The `select#region` may revert to `(86) CHINA` after other field changes.

Mitigation:
- Always re-assert `region='65'` at the end of the fill routine.
- Verify via `region.selectedOptions[0].textContent`.

## 3) City dropdown loads async
`select#accommodationCity` may initially have only 1 option. After setting state, wait ~1s then set city value (`0118` for JOHOR BAHRU).

## 4) Captcha + post-captcha revalidation
Slider puzzle must be solved by the user.

Important: after the captcha is marked as successful, the page may trigger a validation/DOM refresh that causes critical fields (especially dates and `region`) to visually reset.

Mitigation:
- After captcha success **immediately re-assert**:
  - `dob`, `passExpDte`, `arrDt`, `depDt`
  - `region='65'` (or desired code)
- Then click **Submit**.
