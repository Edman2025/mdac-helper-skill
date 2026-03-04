# MDAC Helper Skill

马来西亚电子入境卡自动填写工具。

## 功能

- 自动填写马来西亚电子入境卡 (MDAC)
- 支持所有字段（文本框、下拉框、日期等）
- 自动处理滑块验证码后的字段重置
- 自动关闭日历弹层
- 生成确认邮件

## 使用方法

### 1. 准备 payload.json

```bash
# 使用现有的 mdac_profile.json
python3 scripts/mdac_build_payload.py --out payload.json
```

### 2. 填写表单

```bash
# 使用原始版本（基础功能）
python3 scripts/mdac_fill_openclaw.py payload.json

# 使用改进版本（推荐，增加等待时间和自动关闭日历）
python3 scripts/mdac_fill_openclaw_improved.py payload.json
```

### 3. 完成滑块验证码

- 滑块验证码成功后，表单会自动重新填写
- 直接点击 Submit 提交

## 改进版本说明 (mdac_fill_openclaw_improved.py)

基于 2026-03-04 的经验总结，改进版本增加了：

1. **增加等待时间：** City 下拉框 options 加载等待时间从 1.5 秒增加到 3 秒
2. **自动重新填写：** 滑块验证码后自动重新填写所有字段
3. **直接使用 selectedIndex：** 所有下拉框使用 selectedIndex 和 value 直接设置
4. **关闭日历弹层：** ESC×2 + blur 关闭日历弹层
5. **清理日历表格：** 清理所有日历相关的 DOM 元素
6. **使用 getElementById：** 比 ref 更可靠

## Payload 格式

```json
{
  "name": "ZHANG HUICONG",
  "passNo": "EK7534010",
  "dob": "11/07/1990",
  "passExpDte": "05/07/2033",
  "email": "hczhangforwork@163.com",
  "confirmEmail": "hczhangforwork@163.com",
  "mobile": "18117380235",
  "arrDt": "05/03/2026",
  "depDt": "06/03/2026",
  "vesselNm": "CW6",
  "accommodationAddress1": "15 JALAN STRAITS VIEW 8 STRAITS VIEW",
  "accommodationAddress2": "BANDAR JOHOR BAHRU",
  "accommodationPostcode": "80200",
  "selects": {
    "nationality": "CHN",
    "pob": "CHN",
    "sex": "1",
    "region": "86",
    "trvlMode": "2",
    "embark": "SGP",
    "accommodationStay": "02",
    "accommodationState": "01",
    "accommodationCity": "JOHOR BAHRU"
  }
}
```

## 常见问题

### Q: 为什么 City 下拉框不显示选项？

A: MDAC 的联动机制需要等待足够的时间。改进版本增加了等待时间到 3 秒。

### Q: 滑块验证码后字段被清空怎么办？

A: 改进版本会自动重新填写所有字段。

### Q: 日历弹层没有关闭怎么办？

A: 改进版本会自动关闭日历弹层。

## 更新日志

### 2026-03-04
- 增加等待时间到 3 秒
- 滑块验证码后自动重新填写
- 直接使用 selectedIndex 和 value 设置下拉框
- ESC×2 + blur 关闭日历弹层
- 清理所有日历表格

## 相关文档

- `/workspace-lifeops/travel/mdac-tutorial-2026-03-04.md` - 详细经验总结
- `references/mdac-field-ids.md` - 字段 ID 参考
- `references/mdac-gotchas.md` - 注意事项和常见问题
- `references/datepicker-close.md` - 日期选择器关闭方法

---

**更新时间：** 2026-03-04
**维护者：** 老三 (生活助理)