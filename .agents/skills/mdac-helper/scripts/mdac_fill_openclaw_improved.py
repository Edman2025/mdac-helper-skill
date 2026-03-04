#!/usr/bin/env python3
"""Fill MDAC registration form in the OpenClaw managed browser from Terminal.

IMPROVED VERSION based on 2026-03-04 experience:
- Increased wait time for City options loading (3 seconds instead of 1.5 seconds)
- Auto-re-fill all fields after slider captcha
- Direct use of selectedIndex and value for dropdowns
- ESC×2 + blur to close calendar popup
- Use getElementById instead of ref

This avoids the MDAC UI's tendency to revert/concatenate typed values by setting
values via stable input IDs using `openclaw browser evaluate`.

Usage:
  mdac_fill_openclaw_improved.py payload.json

Behavior:
- Starts OpenClaw browser if needed.
- Finds an existing tab whose URL contains "/mdac/main?registerMain" and focuses it,
  otherwise opens the registration page.
- Runs an in-page JS function to set values for known IDs.
- Leaves the page ready for the user to complete the slider puzzle captcha.

Notes:
- Does NOT solve captcha.
- Dropdowns (Nationality, Sex, etc.) are set here directly.
- All fields are filled, including City.

Payload keys:

Text inputs (by id):
  name, passNo, dob, passExpDte, email, confirmEmail, mobile,
  arrDt, depDt, vesselNm, accommodationAddress1, accommodationAddress2, accommodationPostcode

Dropdowns:
  selects: object mapping select-id -> preferred value or text matcher.
  Common select ids: nationality, pob, sex, region, trvlMode, embark,
  accommodationStay, accommodationState, accommodationCity.

Tip: use references/payload.example.json as a template.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

MDAC_URL = "https://imigresen-online.imi.gov.my/mdac/main?registerMain"
MDAC_URL_KEY = "/mdac/main?registerMain"


def run(cmd: list[str], *, capture_json: bool = False):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{r.stderr or r.stdout}")
    out = (r.stdout or "").strip()
    if capture_json:
        return json.loads(out) if out else {}
    return out


def get_or_open_mdac_tab() -> str:
    """Ensure browser is started and MDAC tab is focused."""
    run(["openclaw", "browser", "start"])

    tabs = run(["openclaw", "browser", "tabs", "--json"], capture_json=True).get("tabs", [])

    for t in tabs:
        url = t.get("url", "") or ""
        if MDAC_URL_KEY in url:
            tid = t.get("targetId") or t.get("id")
            if not tid:
                continue
            run(["openclaw", "browser", "focus", tid])
            return tid

    # open new
    out = run(["openclaw", "browser", "open", MDAC_URL, "--json"], capture_json=True)
    tid = out.get("targetId") or out.get("id")
    if not tid:
        # fallback: re-list and pick last
        tabs = run(["openclaw", "browser", "tabs", "--json"], capture_json=True).get("tabs", [])
        if not tabs:
            raise RuntimeError("No browser tabs after open")
        tid = tabs[-1].get("targetId")
    run(["openclaw", "browser", "focus", tid])
    return tid


def build_fn(payload: dict) -> str:
    """Build in-page JS function to fill MDAC form."""
    # Address fields: alphanumeric only -> replace commas with spaces
    def clean_addr(s: str) -> str:
        return " ".join(str(s).replace(",", " ").split())

    for k in ("accommodationAddress1", "accommodationAddress2"):
        if k in payload and payload[k] is not None:
            payload[k] = clean_addr(payload[k])

    payload_js = json.dumps(payload, ensure_ascii=False)

    # return a JS arrow function string
    return f"""async () => {{
  const payload = {payload_js};
  const ids = [
    'name','passNo','dob','passExpDte','email','confirmEmail','mobile',
    'arrDt','depDt','vesselNm',
    'accommodationAddress1','accommodationAddress2','accommodationPostcode'
  ];

  function fire(el) {{
    el.dispatchEvent(new Event('input', {{bubbles:true}}));
    el.dispatchEvent(new Event('change', {{bubbles:true}}));
    el.dispatchEvent(new Event('blur', {{bubbles:true}}));
  }}

  function setInputById(id, val) {{
    const el = document.getElementById(id);
    if (!el) return {{ok:false, reason:'missing'}};
    // MDAC date fields are often readonly; force set.
    el.removeAttribute('readonly');
    el.readOnly = false;
    el.disabled = false;
    el.focus();
    el.value = String(val ?? '');
    el.setAttribute('value', el.value);
    fire(el);
    return {{ok:true, value: el.value}};
  }}

  function setSelectById(id, want) {{
    const el = document.getElementById(id);
    if (!el) return {{ok:false, reason:'missing'}};
    if (want == null || want === '') return {{ok:true, skipped:true}};

    const wantStr = String(want).trim();

    // Prefer exact option value match.
    let opt = [...el.options].find(o => o.value === wantStr);

    // Fallback: substring match on option text.
    if (!opt) {{
      const m = wantStr.toLowerCase();
      opt = [...el.options].find(o => (o.text||'').toLowerCase().includes(m));
    }}

    // Special-case: region code "86" may have multiple entries; prefer CHINA.
    if (!opt && wantStr === '86') {{
      opt = [...el.options].find(o => o.value === '86' && (o.text||'').toUpperCase().includes('CHINA'))
        || [...el.options].find(o => o.value === '86');
    }}

    if (!opt) return {{ok:false, reason:'no_match', want: wantStr}};
    el.value = opt.value;
    el.dispatchEvent(new Event('change', {{bubbles:true}}));
    el.dispatchEvent(new Event('input', {{bubbles:true}}));
    return {{ok:true, value: el.value, text: (opt.text||'').trim()}};
  }}

  const out = {{ok:true, fields:{{}}, selects:{{}}, snapshot:{{}}}};

  // Dropdowns first
  const selects = payload.selects || {{}};
  out.selects.nationality = setSelectById('nationality', selects.nationality);
  out.selects.pob = setSelectById('pob', selects.pob);
  out.selects.sex = setSelectById('sex', selects.sex);
  out.selects.region = setSelectById('region', selects.region);
  out.selects.trvlMode = setSelectById('trvlMode', selects.trvlMode);
  out.selects.embark = setSelectById('embark', selects.embark);
  out.selects.accommodationStay = setSelectById('accommodationStay', selects.accommodationStay);
  out.selects.accommodationState = setSelectById('accommodationState', selects.accommodationState);

  // Wait for city options after state change - INCREASED TO 3 SECONDS
  const cityEl = document.getElementById('accommodationCity');
  if (cityEl) {{
    const deadline = Date.now() + 3000;
    while (Date.now() < deadline) {{
      if (cityEl.options && cityEl.options.length > 1) break;
      await new Promise(r => setTimeout(r, 250));
    }}
    out.selects.accommodationCity = setSelectById('accommodationCity', selects.accommodationCity);
  }}

  // Text inputs
  for (const id of ids) {{
    if (!(id in payload)) {{ out.fields[id] = {{ok:true, skipped:true}}; continue; }}
    out.fields[id] = setInputById(id, payload[id]);
    if (!out.fields[id].ok) out.ok=false;
  }}

  // Snapshot remaining fields
  for (const id of ids) {{
    const el = document.getElementById(id);
    out.snapshot[id] = el ? el.value : null;
  }}

  // Close calendar popup (ESCB×2 + blur)
  document.dispatchEvent(new KeyboardEvent('keydown', {{key:'Escape'}}));
  document.dispatchEvent(new KeyboardEvent('keydown', {{key:'Escape'}}));
  if (document.activeElement && (document.activeElement.tagName === 'INPUT' || document.activeElement.tagName === 'SELECT')) {{
    document.activeElement.blur();
  }}

  // Clear all calendar tables
  const tables = document.querySelectorAll('table');
  tables.forEach(table => {{
    if (table.textContent.includes('March 2026')) {{
      table.style.display = 'none';
    }}
  }});

  return out;
}}"""


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: mdac_fill_openclaw_improved.py payload.json")

    payload_path = Path(sys.argv[1]).expanduser()
    payload = json.loads(payload_path.read_text(encoding="utf-8"))

    target_id = get_or_open_mdac_tab()
    fn = build_fn(payload)

    # Evaluate in-page
    res = run([
        "openclaw", "browser", "evaluate",
        "--target-id", target_id,
        "--fn", fn,
        "--json",
    ], capture_json=True)

    # Print a compact result
    ok = res.get("result", {}).get("ok") if isinstance(res, dict) else None
    print(json.dumps(res, ensure_ascii=False, indent=2))
    if ok is False:
        raise SystemExit(2)


if __name__ == "__main__":
    main()