#!/usr/bin/env python3
"""Build an MDAC payload.json from a stored profile.

Why: MDAC is fragile; we want repeatable ID-based fill without re-asking for
static info (passport/email/address).

Default profile path:
  <workspace>/private/mdac_profile.json
(where <workspace> is inferred from this script location)

Usage:
  mdac_build_payload.py --out payload.json [--arr YYYY-MM-DD] [--dep YYYY-MM-DD]

If --arr/--dep are omitted, uses profile.preferences.relative_trip_offsets_days
(default: arrive +1 day, depart +2 days from *today* in local timezone).

Output payload keys match scripts/mdac_fill_openclaw.py.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path


def workspace_root_from_here() -> Path:
    here = Path(__file__).resolve()
    # .../workspace/.agents/skills/mdac-helper/scripts/mdac_build_payload.py
    return here.parents[4]


def ddmmyyyy(d: date) -> str:
    return d.strftime("%d/%m/%Y")


def split_address(addr: str) -> tuple[str, str]:
    s = " ".join(str(addr).replace(",", " ").split())
    # Prefer a semantic split if we can
    if " BANDAR " in s:
        a1, a2 = s.split(" BANDAR ", 1)
        return a1.strip(), ("BANDAR " + a2.strip()).strip()
    # Otherwise split by length
    if len(s) <= 45:
        return s, ""
    cut = s.rfind(" ", 0, 45)
    if cut <= 0:
        cut = 45
    return s[:cut].strip(), s[cut:].strip()


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--profile", type=str, default=None, help="Path to mdac_profile.json")
    p.add_argument("--out", type=str, required=True, help="Output payload.json")
    p.add_argument("--arr", type=str, default=None, help="Arrival date YYYY-MM-DD")
    p.add_argument("--dep", type=str, default=None, help="Departure date YYYY-MM-DD")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    ws = workspace_root_from_here()
    profile_path = Path(args.profile) if args.profile else (ws / "private" / "mdac_profile.json")
    profile = json.loads(profile_path.read_text(encoding="utf-8"))

    # Dates
    today = datetime.now().date()
    offsets = (
        profile.get("preferences", {})
        .get("relative_trip_offsets_days", {})
    )
    arrive_offset = int(offsets.get("arrive", 1))
    depart_offset = int(offsets.get("depart", 2))

    if args.arr:
        arr_d = date.fromisoformat(args.arr)
    else:
        arr_d = today + timedelta(days=arrive_offset)

    if args.dep:
        dep_d = date.fromisoformat(args.dep)
    else:
        dep_d = today + timedelta(days=depart_offset)

    addr1, addr2 = split_address(profile.get("default_accommodation", {}).get("address", ""))

    payload = {
        "openUrl": False,

        # text inputs (by id)
        "name": profile.get("name_passport", ""),
        "passNo": profile.get("passport_no", ""),
        "dob": profile.get("dob", ""),
        "passExpDte": profile.get("passport_expiry", ""),
        "email": profile.get("email", ""),
        "confirmEmail": profile.get("email", ""),
        "mobile": profile.get("mobile_no", ""),
        "arrDt": ddmmyyyy(arr_d),
        "depDt": ddmmyyyy(dep_d),
        "vesselNm": profile.get("default_trip", {}).get("transport_no", ""),
        "accommodationAddress1": addr1,
        "accommodationAddress2": addr2,
        "accommodationPostcode": profile.get("default_accommodation", {}).get("postcode", ""),

        # dropdowns (by select id)
        # Prefer values; fallback logic in in-page JS matches by text.
        "selects": {
            "nationality": profile.get("nationality", "CHN"),
            "pob": profile.get("place_of_birth", "CHN"),
            "sex": "1" if str(profile.get("sex", "")).upper() == "MALE" else "2",
            "region": profile.get("mobile_country_region_code", ""),
            "trvlMode": "2" if str(profile.get("default_trip", {}).get("mode_of_travel", "")).upper() == "LAND" else "",
            "embark": profile.get("default_trip", {}).get("last_port", ""),
            "accommodationStay": "02" if "FRIEND" in str(profile.get("default_accommodation", {}).get("type", "")).upper() else "",
            "accommodationState": "01" if str(profile.get("default_accommodation", {}).get("state", "")).upper() == "JOHOR" else "",
            "accommodationCity": str(profile.get("default_accommodation", {}).get("city", "")),
        }
    }

    out_path = Path(args.out)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(str(out_path))


if __name__ == "__main__":
    main()
