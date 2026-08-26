---
name: emoji-sticker-cn
description: This skill should be used when the user wants to create Chinese-platform compliant emoji/sticker packs (微信表情开放平台 / 小红书 / 抖音), covering image generation, platform-specific resizing and cropping, sequential naming, upload metadata, and sensitive-word compliance checks. It fills the gap that most emoji skills ignore Chinese platform specs and content compliance. Also triggers on 更新表情包规则 / 巡检表情包规范 to run the rule-inspection workflow.
version: 1.1.0
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
| 缩略图 | 120×120(专辑) | PNG,≤200KB | 透明底 |
- 成套:**8–24 张**(单品可 1 张);动态须无缝循环;单品名 ≤ 4 汉字。

### 小红书 / 抖音(内联,无正式商店)
- 小红书:1080×1080(笔记配图);GIF 常被转静态,优先静态图。
- 抖音:240–1000px,GIF/WebP ≤5MB(经验值,非官方强制)。

### 违禁词(文案 / 上架描述 / 专辑名)
- **硬性流程**:任何对外文案必须先过 `multi-wordcheck`(公众号/小红书/抖音,若宿主环境已安装);未安装则降级用 `references/中文平台违禁词合规参考.md` 种子集校验,并向用户说明这是离线兜底、非实时。校验通过才算完成。
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
2. **裁切 + 命名**:用 `scripts/resize_stickers.py` 批量处理——
   - 主图 240×240 透明底 PNG,命名 `01.png`…`24.png`(一套 8–24 张)
   - 聊天面板图标 50×50;封面 240×240;详情横幅 750×400(非透明底)
3. **上架元数据**:准备专辑名(≤4 汉字)、描述、封面、横幅。
4. **合规校验**:文案 / 描述优先调 `multi-wordcheck`(未装则用参考文件兜底);不通过则改写后复检。
5. **打包**:`scripts/resize_stickers.py --zip` 输出 ZIP 供上架。

**路线 B — 小红书 / 抖音(内联图片,无正式上架平台)**
1. 宿主生图工具生成表情图。
2. 裁切到推荐尺寸:小红书 1080×1080(笔记配图)、抖音 240–1000px GIF/WebP。
3. 文案走违禁词校验(优先 `multi-wordcheck`;小红书严打私域导流与绝对化词,抖音严查站外引流)。
4. 直接用于笔记 / 聊天,无需成套上架。

**路线 C — 已有图片批量裁切**
- 直接跑 `scripts/resize_stickers.py`,指定平台尺寸与背景,输出规范图 + 可选 ZIP。

**路线 D — 动态 GIF(程序化动画,零积分,优先推荐)**
- 适用:弹跳 / 摇摆 / 缩放类简单动效——微信「沙雕动态表情」的主流做法,零 API 成本、透明底天然保留。
- 用 `scripts/animate_sticker.py`:输入**一张透明底静态贴图** → 输出循环透明底 GIF,默认 240×240、≤500KB(微信规范),超限自动降色 / 抽帧。
- 内置动效:`bounce`(弹跳 + 挤压拉伸)/ `shake`(左右晃)/ `pulse`(呼吸缩放)/ `wobble`(摇摆)。
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

## Hard rules
- 微信主图 / 图标 / 封面必须**透明底**,白边会被驳回。
- **不要重造违禁词检测**:有 `multi-wordcheck` 就调;没有才用参考文件兜底并说明局限。
- 抖音 / 小红书无正式表情商店,按「内联图片」处理,不强求成套。
- 尺寸执行依据 = references 中 `active` + 官方核实条目;`pending-verify` 需提示复核;`deprecated` 一律不用。
- 规则巡检**先报告、后确认、再落盘**,禁止未经确认直接改 references。
- 生图消耗积分/配额前先告知用户(WorkBuddy `ImageGen` 约 5–10 credits/张),批量生成前确认张数。

## Script
```bash
# 批量裁切 + 规范命名 + 打包
python3 scripts/resize_stickers.py ./raw --size 240x240 --bg transparent --format png --prefix emoji --out ./wechat --zip

# 静态贴纸 → 动画 GIF(零积分)
python3 scripts/animate_sticker.py cat.png --anim bounce --out cat_bounce.gif
```
