# MDAC datepicker close behavior

The MDAC page uses a datepicker widget that can remain open and obscure the date fields, causing the user to think dates are "not saved".

## Reliable close sequence

1) **Press Escape** once or twice.
2) **Force blur** the active element:

```js
try { document.activeElement?.blur?.(); } catch (e) {}
```

3) If the popup persists, click a safe empty area (e.g., top-left corner) to remove focus.

## Why hiding by CSS may fail

The datepicker UI is sometimes rendered outside common selectors or as a positioned element without a stable class. Attempting to hide `.datepicker` / `.ui-datepicker` may return zero matches.

## Best practice in automation

After filling date fields programmatically, always run the close sequence before:
- taking a verification screenshot
- asking the user to solve the slider captcha
- clicking Submit
