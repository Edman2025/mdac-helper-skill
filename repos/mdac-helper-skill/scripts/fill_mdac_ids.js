// Fill MDAC text inputs by stable element IDs.
// Usage (conceptual): run in page context via browser.act({kind:'evaluate', fn: <this script wrapped in ()=>...>})
// Provide `payload` with desired values.

(function fillMDAC(payload) {
  const requiredIds = [
    'name',
    'passNo',
    'dob',
    'passExpDte',
    'email',
    'confirmEmail',
    'mobile',
    'arrDt',
    'depDt',
    'vesselNm',
    'accommodationAddress1',
    'accommodationAddress2',
    'accommodationPostcode',
  ];

  // Fields likely to visually reset after captcha success; safe to re-assert.
  const criticalIds = ['dob','passExpDte','arrDt','depDt','email','confirmEmail','mobile'];

  function fire(el) {
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
    el.dispatchEvent(new Event('blur', { bubbles: true }));
  }

  function set(id, val) {
    const el = document.getElementById(id);
    if (!el) return { ok: false, reason: 'missing' };
    // date fields are often readonly; force set
    el.removeAttribute?.('readonly');
    el.readOnly = false;
    el.disabled = false;
    el.focus();
    el.value = String(val ?? '');
    el.setAttribute?.('value', el.value);
    fire(el);
    return { ok: true, value: el.value };
  }

  function setSelect(id, want) {
    const el = document.getElementById(id);
    if (!el) return { ok: false, reason: 'missing' };
    if (want == null || want === '') return { ok: true, skipped: true };
    const wantStr = String(want).trim();
    let opt = [...el.options].find(o => o.value === wantStr);
    if (!opt) {
      const m = wantStr.toLowerCase();
      opt = [...el.options].find(o => (o.text || '').toLowerCase().includes(m));
    }
    if (!opt && wantStr === '65') {
      opt = [...el.options].find(o => o.value === '65' && (o.text || '').toUpperCase().includes('SINGAPORE'))
        || [...el.options].find(o => o.value === '65');
    }
    if (!opt) return { ok: false, reason: 'no_match', want: wantStr };
    el.value = opt.value;
    el.dispatchEvent(new Event('change', { bubbles: true }));
    el.dispatchEvent(new Event('input', { bubbles: true }));
    return { ok: true, value: el.value, text: (opt.text || '').trim() };
  }

  const out = { ok: true, fields: {}, selects: {}, critical: {}, snapshot: {} };

  // Optional dropdowns: payload.selects
  if (payload.selects) {
    const s = payload.selects;
    out.selects.nationality = setSelect('nationality', s.nationality);
    out.selects.pob = setSelect('pob', s.pob);
    out.selects.sex = setSelect('sex', s.sex);
    out.selects.region = setSelect('region', s.region);
    out.selects.trvlMode = setSelect('trvlMode', s.trvlMode);
    out.selects.embark = setSelect('embark', s.embark);
    out.selects.accommodationStay = setSelect('accommodationStay', s.accommodationStay);
    out.selects.accommodationState = setSelect('accommodationState', s.accommodationState);
    // City often depends on state; caller may re-run after state is set.
    out.selects.accommodationCity = setSelect('accommodationCity', s.accommodationCity);
  }

  for (const id of requiredIds) {
    if (!(id in payload)) continue;
    out.fields[id] = set(id, payload[id]);
    if (!out.fields[id].ok) out.ok = false;
  }

  // Helper: re-assert critical fields after captcha success / DOM refresh
  out.reassertCritical = () => {
    const res = {};
    for (const id of criticalIds) {
      if (!(id in payload)) continue;
      res[id] = set(id, payload[id]);
    }
    out.critical = res;
    return res;
  };

  // sanity snapshot
  for (const id of requiredIds) {
    const el = document.getElementById(id);
    out.snapshot[id] = el ? el.value : null;
  }

  return out;
})
