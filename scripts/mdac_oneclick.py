#!/usr/bin/env python3
"""Generate a one-shot MDAC form filler snippet and copy it to clipboard (macOS).

Usage:
  mdac_oneclick.py payload.json

The script reads JSON payload and puts a JavaScript snippet on the clipboard.
Paste the snippet into the browser DevTools Console *on the MDAC registration page*.

Why: The MDAC site sometimes reverts/concatenates typed values. Setting values via
stable input element IDs (dob, passExpDte, email, ...) is reliable.

Notes:
- This does NOT solve the slider puzzle captcha.
- Address fields should be alphanumeric only (replace commas with spaces).

Payload example keys:
  name, passNo, dob, passExpDte, email, confirmEmail, mobile,
  arrDt, depDt, vesselNm, accommodationAddress1, accommodationAddress2, accommodationPostcode

Optional:
  openUrl: true/false (default false) - if true, snippet will navigate to MDAC registerMain.
"""

import json
import sys
import subprocess
from pathlib import Path


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: mdac_oneclick.py payload.json")

    payload_path = Path(sys.argv[1]).expanduser()
    payload = json.loads(payload_path.read_text(encoding="utf-8"))

    # Basic sanitization
    def clean_addr(s: str) -> str:
        return " ".join(str(s).replace(",", " ").split())

    for k in ("accommodationAddress1", "accommodationAddress2"):
        if k in payload and payload[k] is not None:
            payload[k] = clean_addr(payload[k])

    open_url = bool(payload.pop("openUrl", False))

    js = f"""(() => {{
  const payload = {json.dumps(payload, ensure_ascii=False)};
  const openUrl = {str(open_url).lower()};

  if (openUrl && !location.href.includes('registerMain')) {{
    location.href = 'https://imigresen-online.imi.gov.my/mdac/main?registerMain';
    return 'Navigating to MDAC register page... rerun after page loads.';
  }}

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

  const out = {{ok:true, fields:{{}}, snapshot:{{}}}};

  for (const id of ids) {{
    const el = document.getElementById(id);
    if (!el) {{ out.fields[id] = {{ok:false, reason:'missing'}}; out.ok=false; continue; }}
    if (!(id in payload)) {{ out.fields[id] = {{ok:true, skipped:true}}; continue; }}
    el.focus();
    el.value = String(payload[id] ?? '');
    fire(el);
    out.fields[id] = {{ok:true, value: el.value}};
  }}

  for (const id of ids) {{
    const el = document.getElementById(id);
    out.snapshot[id] = el ? el.value : null;
  }}

  console.log('MDAC fill result:', out);
  return out;
}})();
"""

    try:
        subprocess.run(["pbcopy"], input=js.encode("utf-8"), check=True)
        print("OK: JS snippet copied to clipboard. Paste into DevTools Console on the MDAC page.")
    except Exception:
        print(js)
        print("\n(pbcopy not available; printed snippet above)")


if __name__ == "__main__":
    main()
"