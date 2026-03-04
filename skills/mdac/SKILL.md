---
name: mdac
description: 马来西亚 MDAC（Malaysia Digital Arrival Card）在线填表一气呵成流程：从本地 private 档案读取个人信息，打开官网填写 Registration 表单，处理日期选择器（日历浮层）与提交前校验，最后人工完成拼图验证并提交。
---

# MDAC（马来西亚入境卡）一气呵成 SOP

## 何时用
- 用户说“填 MDAC/入境卡/到马来西亚”并且要你**直接上官网填表**。

## 关键文件（本机）
- 个人档案：`/Users/edman_openclaw/.openclaw/workspace/private/mdac_profile.json`
  - 默认：**陆路 LAND + Woodlands / Causeway**（如用户未另行说明）。

## 官方入口
- 直接用：`https://imigresen-online.imi.gov.my/mdac/main?registerMain`

## 一气呵成流程（强约束，按顺序）

### 0) 先确认行程窗口（必须）
MDAC 页面提示：行程需在提交日起 **3 天内**。
- 若用户只说“周六去周日回”但没说日期：先问清楚具体日期。
- 例：周六 07/03/2026 入境，周日 08/03/2026 离境。

### 1) 打开页面并获取字段 ID（不要依赖 aria ref）
页面输入框的 DOM id（稳定）：
- `name`, `passNo`, `dob`, `passExpDte`, `email`, `confirmEmail`, `mobile`
- `arrDt`, `depDt`, `vesselNm`
- `accommodationAddress1`, `accommodationAddress2`, `accommodationPostcode`
下拉框 DOM id：
- `nationality`, `pob`, `sex`, `region`
- `trvlMode`, `embark`
- `accommodationStay`, `accommodationState`, `accommodationCity`

**填表要用 browser.act(kind=evaluate) 设置 value + dispatch input/change**，否则 UI 看似填了，表单值可能没落地。

### 2) 填表（推荐一次性 evaluate 批量写入）
- 从 `mdac_profile.json` 读出字段
- 文本框：focus → set value → dispatch `input` + `change` → blur
- 下拉框：直接 set `select.value` → dispatch `change`

### 3) 日期选择器（日历浮层）处理（必做）
此站点 datepicker 很粘，**不收起会挡住提交/校验**。
按下面顺序处理：
1. 写入所有日期字段：`dob`, `passExpDte`, `arrDt`, `depDt`（格式 DD/MM/YYYY）
2. `Tab` 切走焦点 + `Escape` 关闭弹层
3. 若日历仍不消失：在 evaluate 中隐藏 datepicker（不改值，只隐藏浮层）
   - `document.querySelectorAll('.datepicker, .ui-datepicker, .bootstrap-datetimepicker-widget').forEach(el=>el.style.display='none')`
   - 可补一条：把包含 `Su Mo Tu...` 的日历表格也 `display:none`
4. 再次 evaluate 校验 4 个日期字段 `el.value` 非空

### 4) 让用户完成人工验证（拼图滑块）
页面底部有 **Drag To Verify / Slide the Puzzle**：
- 这是人机验证，必须用户手动拖动。
- 你要发一句明确指令：
  - “请拖动拼图滑块验证完成后回我：验证码好了”

### 5) 提交 + 回执
- 用户确认“验证码好了”后，点击 Submit。
- 成功页会显示：`SUCCESSFULLY REGISTERED.` 以及“ACKNOWLEDGEMENT EMAIL WILL BE SENT TO …”。
- 该页通常不直接展示 reference number：
  - 指引用户去邮箱收 acknowledgement
  - 或用导航里的 **Check Registration** 再查

## 经验坑位（务必记住）
- **不要相信截图**：用 evaluate 读 `document.getElementById(id).value` 做最终校验。
- 日期字段最容易“看着有/实际上空”：必须写入后立即读回确认。
- 若出现多个日历浮层叠在页面上：直接隐藏 `.datepicker` 是最快稳定的“收起”。
