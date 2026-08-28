---
name: emoji-sticker-cn
description: This skill should be used when the user wants to create Chinese-platform compliant emoji/sticker packs (微信表情开放平台 / 小红书 / 抖音), covering image generation, platform-specific resizing and cropping, sequential naming, upload metadata, and sensitive-word compliance checks. It fills the gap that most emoji skills ignore Chinese platform specs and content compliance. Also triggers on 更新表情包规则 / 巡检表情包规范 to run the rule-inspection workflow.
version: 2.0.0
license: MIT
trigger: "表情包|贴纸|表情上架|动态表情|GIF表情|更新表情包规则|巡检表情包规范"
agent_created: true
---

# 中文表情包生成 · 合规助手 (emoji-sticker-cn)

## Overview
帮你把「一张图 / 一段描述」变成**可直接上架或发布的中文平台表情包**,重点解决现有表情包 skill 普遍忽略的两件事:
1. **中文平台尺寸规范**(微信有完整上架规范,抖音 / 小红书是内联图片)
2. **内容合规**(违禁词 / 极限词校验,尤其公众号 / 小红书 / 抖音)

生成模型层**不重造**——直接复用宿主环境的文生图 / 图生图工具(WorkBuddy 下为 `ImageGen`,约 5–10 credits/张;OpenClaw 等其他环境用各自可用的生图工具);本 skill 只做「合规流水线」这一增量。

> 可移植约定:凡提到 `ImageGen` / `multi-wordcheck`,指「宿主环境有则用,无则降级」——生图无专用工具时让用户自备图;`multi-wordcheck` 未安装时降级用 `references/中文平台违禁词合规参考.md` 校验并提示局限。

## 硬约束速查(前置硬性约束,产出必须逐条满足)

### 微信表情开放平台(上架主目标)
| 资产 | 尺寸 | 格式 / 上限 | 背景 |
|---|---|---|---|
| 主图 | 240×240 | PNG/JPG/GIF,≤500KB | **透明底(硬性,白边驳回)** |
| 聊天面板图标 | 50×50 | PNG,≤100KB | 透明底 |
| 封面图 | 240×240 | PNG,≤500KB | 透明底 |
| 详情页横幅 | 750×400 | PNG/JPG,≤500KB | **禁透明底、禁纯白底** |
| 缩略图 | 120×120(专辑)/ 240×240(单品) | PNG,≤200KB | 透明底 |
| 赞赏引导图 | 750×560 | — | — |
| 致谢图 | 750×750 | GIF/PNG,≤500KB | — |
| 特效 | ≤480×480、≤24 帧 | PNG,整体≤5MB | — |
- 成套:**8–24 张**(单品可 1 张);动态须无缝循环;单品名 ≤ 4 汉字。
- 命名:文件用英文 / 数字序号(`01.png`…`24.png`),单品名(展示名)≤ 4 汉字。

### 小红书 / 抖音(内联,无正式商店)
- 小红书:1080×1080(笔记配图);GIF 常被转静态,优先静态图。
- 抖音:240–1000px,GIF/WebP ≤5MB(经验值,非官方强制)。

### 违禁词(文案 / 上架描述 / 专辑名)
- **硬性流程**:任何对外文案必须先过 `multi-wordcheck`(公众号/小红书/抖音,若宿主环境已安装);未安装则降级用 `scripts/check_compliance.py` + `references/中文平台违禁词合规参考.md` 种子集做离线兜底,并向用户说明这是离线兜底、非实时。校验通过才算完成。
- 红线类别:广告法极限词、政治敏感、色情低俗、虚假医疗、私域导流(小红书)、站外引流(抖音)。

> 完整规范与源 URL 见 `references/`。**执行时以 references 中 `status = active` 且「官方核实」的条目为最终依据**;`pending-verify` 条目需提示用户复核,`deprecated` 条目一律不得使用。

## When to use
- 用户说:做表情包、生成贴纸、微信表情上架、小红书 / 抖音表情图、一套聊天表情……
- 用户说:**动态表情 / GIF 表情 / 让表情动起来** → 走路线 D。
- 用户已有图片想批量裁成平台尺寸并打包。
- 用户要检查表情包文案 / 上架描述是否踩违禁词。
- 用户说:**更新表情包规则 / 巡检表情包规范** → 走下方「规则更新与退出机制」。

## Workflow
按目标平台走不同路线(规范见 `references/中文平台表情包尺寸规范.md`):

**路线 A — 微信表情开放平台上架(主目标,有正式规范)**
1. **生成**:用宿主生图工具(WorkBuddy: `ImageGen`)产出表情图(prompt 要点:同一角色 / 统一风格;`background: transparent`;如需角色一致可先出 1 张定稿,再用图生图批量延展)。
2. **裁切 + 命名**:一键五件套——
   ```bash
   python3 scripts/resize_stickers.py ./raw --wechat --out ./wechat_pack --zip --max-kb 500
   ```
   自动输出 主图 240×240 / 聊天面板图标 50×50 / 封面 240×240 / 详情页横幅 750×400(默认浅灰底,禁纯白)/ 缩略图 120×120,全部规范命名 `01.png`…`24.png`,每类独立 ZIP。也可单独指定尺寸:`--size 240x240 --bg transparent`。
3. **上架元数据**:准备专辑名(≤4 汉字)、描述、封面、横幅。
4. **合规校验**:文案 / 描述优先调 `multi-wordcheck`(未装则用 `scripts/check_compliance.py` 离线兜底并提示局限);不通过则改写后复检。
5. **上架实操**(sticker.weixin.qq.com):
   1. 登录微信表情开放平台,进入「提交表情」;
   2. 创建专辑:填专辑名(≤4 汉字)、简介、分类、标签;
   3. 按资产表逐项上传主图 / 图标 / 封面 / 横幅 / 缩略图;
   4. 逐张填写单品名(每张 ≤4 汉字)与描述;
   5. 预览确认透明底、循环动画无闪断后提交审核(通常 3–7 个工作日);
   6. 被驳回时按驳回原因修改素材 / 文案后重新提交。

**路线 B — 小红书 / 抖音(内联图片,无正式上架平台)**
1. 宿主生图工具生成表情图。
2. 裁切到推荐尺寸:小红书 1080×1080(笔记配图)、抖音 240–1000px GIF/WebP。
3. 文案走违禁词校验(优先 `multi-wordcheck`;小红书严打私域导流与绝对化词,抖音严查站外引流;离线兜底:`check_compliance.py --platform xiaohongshu douyin`)。
4. 直接用于笔记 / 聊天,无需成套上架。

**路线 C — 已有图片批量裁切**
- 直接跑 `scripts/resize_stickers.py`,指定平台尺寸与背景,输出规范图 + 可选 ZIP;`--fit cover` 可裁切填满、`--max-kb` 可校验体积超限。

**路线 D — 动态 GIF(内容匹配型动画,零积分,优先推荐)**
- **v2 工作流(看图自动配动效)**:
  1. **画像**:agent 直接查看贴图,输出内容画像——主体类型(人物全身/大头像/动物/物件/文字)、情绪、动态倾向、置信度;
  2. **匹配**:查 `references/动效匹配规则.md` 选配方;置信度低 → `neutral` 兜底(宁可轻微也不生硬);文字型主体 → `text`;
  3. **渲染**:`scripts/animate_sticker.py cat.png --recipe happy --out cat_happy.gif`
- 9 个情绪配方:`happy`(蓄力蹲→弹跳→落地压扁→回弹呼吸+★星星)/ `angry`(高频震动+💢)/ `sad`(慢垂+💧)/ `surprised`(过冲回弹+!)/ `shy`(慢摇+💗)/ `speechless`(近静止+…💧)/ `sleepy`(呼吸+Zzz)/ `neutral`(待机呼吸)/ `text`(整体强调脉冲)。
- 引擎要点:缓动曲线(禁线性)、多段相位、挤压拉伸守恒、**不等帧时长**(关键姿势停留更久)、程序化粒子(颜色自动取主体主色)、f(0)=f(1) 无缝循环、体积超限自动降色/抽帧。
- 兼容 v1 动效名:`--anim bounce/shake/pulse/wobble` 自动映射配方;`--list` 查看全部配方。
- 进阶可选(消耗积分):更丰富动作用宿主生图工具逐帧图生图(WorkBuddy `ImageGen` 每帧 5–10 credits)再本地合成,需注意帧间一致性;不推荐视频转 GIF 路线(50–100 credits/条 + 逐帧去底闪烁问题)。

## 规则更新与退出机制(规则持续维护的核心)
触发词:**「更新表情包规则」「巡检表情包规范」**(可由定时自动化发起)。流程:

1. **巡检**:逐个 WebFetch `references/` 两个文件中记录的「源 URL」,提取现行尺寸 / 格式 / 上限 / 成套要求 / 公约版本。
2. **Diff**:与文件中 `status = active` 的条目逐项对比(数字、格式、上限、平台开关)。
3. **报告**:把差异整理成「旧值 → 新值 + 来源 URL」清单,呈给用户,**未确认前不落盘**。
4. **更新(用户确认后)**:
   - 旧条目改为 `status: deprecated`(保留原值、注明日期 / 原因 / 替代值)——**退出但不删除**,便于回溯;
   - 新条目以 `status: active` 写入,更新「抓取日期」;
   - 文件顶部 CHANGELOG 追加一行(日期 / 版本 / 变更摘要)。
5. **违禁词侧**:实时校验依赖 `multi-wordcheck` API,无需巡检;仅当平台发布公约大版本(如小红书 2.0)时,更新参考文件的「平台专属敏感点」节。

**为什么用 agent 巡检而非写死爬虫脚本**:官方规范页多为 JS 渲染、数字嵌在表格 / 文案里,LLM 提取 + 人工确认比正则爬虫稳健,也不用维护脆弱的选择器。

**条目生命周期**:`pending-verify`(待复核)→ `active`(生效,唯一可执行依据)→ `deprecated`(已退出,禁止使用,保留留痕)。

## References(持续维护,单独更新)
- `references/中文平台表情包尺寸规范.md` — 各平台尺寸 / 格式 / 上限 / 背景 / 成套要求 + status 生命周期 + 源 URL。
- `references/中文平台违禁词合规参考.md` — 违禁词类别、权威来源、平台专属敏感点、通用极限词种子集。**实际校验优先复用 `multi-wordcheck`,本文件仅兜底。**
- `references/动效匹配规则.md` — 情绪×主体 → 动效配方匹配表 + 粒子符号表 + 兜底规则。新增情绪配方先在此登记(`pending-verify`),POC 验证后转 `active`。

## Hard rules
- 微信主图 / 图标 / 封面必须**透明底**,白边会被驳回;详情页横幅**禁透明底、禁纯白底**(用脚本 `--wechat` 默认浅灰底)。
- **不要重造违禁词检测**:有 `multi-wordcheck` 就调;没有才用 `check_compliance.py` 兜底并说明局限。
- 抖音 / 小红书无正式表情商店,按「内联图片」处理,不强求成套。
- 尺寸执行依据 = references 中 `active` + 官方核实条目;`pending-verify` 需提示复核;`deprecated` 一律不用。
- 规则巡检**先报告、后确认、再落盘**,禁止未经确认直接改 references。
- 生图消耗积分/配额前先告知用户(WorkBuddy `ImageGen` 约 5–10 credits/张),批量生成前确认张数。

## Script
```bash
# 微信五件套:主图/图标/封面/横幅/缩略图一次生成 + 规范命名 + 打包 + 体积校验
python3 scripts/resize_stickers.py ./raw --wechat --out ./wechat_pack --zip --max-kb 500

# 单尺寸批量(命名 01.png…24.png)
python3 scripts/resize_stickers.py ./raw --size 240x240 --bg transparent --format png --out ./out --zip

# 静态贴纸 → 内容匹配动效 GIF(零积分;先看图判情绪,再按 references/动效匹配规则.md 选配方)
python3 scripts/animate_sticker.py cat.png --recipe happy --out cat_happy.gif
python3 scripts/animate_sticker.py --list   # 查看全部配方

# 文案离线违禁词校验(兜底;正式发布前仍优先 multi-wordcheck)
python3 scripts/check_compliance.py "全网最低价,加微信详聊" --platform xiaohongshu douyin
```
