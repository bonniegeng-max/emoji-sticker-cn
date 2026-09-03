# emoji-sticker-cn · 中文表情包生成合规助手

把「一张图 / 一段描述」变成**可直接上架或发布的中文平台表情包**。

GitHub / ClawHub 上的表情包 skill 大多只管「生成」,普遍忽略两件在中国平台致命的事:

1. **平台尺寸规范**——微信表情开放平台对主图 / 图标 / 封面 / 横幅各有硬性尺寸、体积、透明底要求,不达标直接驳回;
2. **内容合规**——上架描述、专辑名踩了广告法极限词 / 平台违禁词,轻则限流重则下架。

本 skill 只做这条「合规流水线」增量:生成层复用宿主环境的生图工具(不重造模型),规则层内置可持续维护的平台硬约束。

## 特性

- **硬约束速查前置**:微信全参数表(240×240 主图 / 50×50 图标 / 750×400 横幅…)、小红书 / 抖音推荐尺寸、违禁词红线,产出前逐条对照
- **四条工作路线**:
  - A 微信表情上架(成套 8–24 张 + 素材机检 + 提交清单 + 站点实操步骤)
  - B 小红书 / 抖音内联表情(笔记配图 / 聊天表情)
  - C 已有图片批量裁切 + 规范命名 + ZIP 打包
  - D **内容匹配动效 GIF——看图判情绪,自动配动效(9 情绪配方 + 程序化粒子 + 缓动曲线),零 API 成本**,自动控体积 ≤500KB
- **一键七件套**:`--wechat` 预设一次生成主图 / 聊天图标 / 封面 / 横幅 / 缩略图 / 赞赏引导图 / 致谢图,自动建目录、规范命名、体积校验
- **素材机检 `check_assets.py`**:尺寸/格式/体积/透明底分级判定(封面/图标必须透明,主图照片型合法)、白描边检测、整套 dhash 查重(第一拒因「整套差异不足」)、含义词校验;FAIL/WARN/OK 三级,退出码 = FAIL 数
- **提交清单 `make_submit.py`**:机检通过后生成「字段→值/文件」对照的 submit.md,上架照抄不猜编号
- **内容匹配动效引擎**:`animate_sticker.py` 内置 9 个情绪配方(happy/angry/sad/surprised/shy/speechless/sleepy/neutral/text),程序化粒子(★💢💧💗Zzz!… 零素材),缓动曲线 + 不等帧时长 + 无缝循环;`references/动效匹配规则.md` 提供情绪×主体→配方的 L2 匹配表,v1 动效名自动映射
- **规则更新与退出机制**:条目生命周期 `pending-verify → active → deprecated`;说「更新表情包规则」即触发巡检(WebFetch 官方源 → diff 报告 → 确认后落盘),作废规则留痕不删除
- **违禁词校验**:优先复用 `multi-wordcheck` 类实时检测 skill(宿主环境有则用);未安装则降级用 `check_compliance.py` 离线种子集兜底

## 安装

```bash
# ClawHub (OpenClaw)
npx clawhub@latest install emoji-sticker-cn

# 或从 GitHub 克隆到你的 skills 目录
git clone https://github.com/bonniegeng-max/emoji-sticker-cn.git
```

依赖:`pip install Pillow`(裁切 / 动画脚本)。

> 外挂依赖说明:脚本层的硬依赖仅 Pillow。**实时**违禁词校验是可选外挂——宿主环境装有 `multi-wordcheck` 类 skill 时自动优先调用;未安装则自动降级为脚本内置的离线种子集兜底(非实时,会向用户提示局限)。生图复用宿主环境自带的文生图/图生图工具,本 skill 不自带。

## 使用

对宿主 agent 说:

- 「帮我做一套微信表情包」→ 路线 A
- 「把这张图裁成小红书尺寸」→ 路线 C
- 「让这张贴纸动起来」→ 路线 D
- 「更新表情包规则」→ 巡检工作流

脚本直用:

```bash
# 微信七件套:主图/图标/封面/横幅/缩略图/赞赏引导图/致谢图一次生成 + 规范命名 + 打包 + 体积校验
python3 scripts/resize_stickers.py ./raw --wechat --out ./wechat_pack --zip --max-kb 500

# 素材机检(上架前必跑,FAIL 必须清零;退出码 = FAIL 数)
python3 scripts/check_assets.py ./wechat_pack --meanings meanings.txt

# 生成提交清单(字段→值/文件对照表,上架照抄)
python3 scripts/make_submit.py ./wechat_pack --name 表情名 --intro 介绍 --copyright 作者 --meanings meanings.txt

# 单尺寸批量(命名 01.png…24.png,主图保持源图透明状态)
python3 scripts/resize_stickers.py ./raw --size 240x240 --format png --out ./out --zip

# 静态贴纸 → 内容匹配动效 GIF(零积分;先看图判情绪,再按 references/动效匹配规则.md 选配方)
python3 scripts/animate_sticker.py cat.png --recipe happy --out cat_happy.gif
python3 scripts/animate_sticker.py --list   # 查看全部配方

# 文案离线违禁词校验(兜底;正式发布前仍优先 multi-wordcheck)
python3 scripts/check_compliance.py "全网最低价,加微信详聊" --platform xiaohongshu douyin
```

## 产物样张

> 待补充：此处放 2–3 张真实贴纸产物图（历史 demo 在 WorkBuddy projects/archive/sticker demo，本机已归档于 `projects/archive/2026-08-25-09-45-19/sticker-demo`），建议含一张过审/发布截图。当前刻意不放占位图，避免冒充真实产物。

## 目录

```
├── SKILL.md                                  # 工作流 + 硬约束 + 更新/退出机制
├── references/
│   ├── 中文平台表情包尺寸规范.md              # 微信/QQ/飞书官方核实 + 内联平台标注(持续维护)
│   ├── 中文平台违禁词合规参考.md              # 类别体系 + 权威来源 + 极限词种子集(持续维护)
│   ├── 微信表情审核标准与高频拒因.md          # 高频拒因清单 / 审核红线 / IP 形象约束 / 付费表情
│   └── 动效匹配规则.md                        # 情绪×主体 → 动效配方匹配表 + 粒子符号表(路线 D)
└── scripts/
    ├── resize_stickers.py                    # 批量裁切 / 命名 / ZIP / 微信七件套
    ├── check_assets.py                       # 素材机检(尺寸/透明底/白描边/dhash 查重/含义词)
    ├── make_submit.py                        # 生成 submit.md 提交清单(字段→值/文件对照)
    ├── animate_sticker.py                    # 内容匹配动效引擎(9 情绪配方 + 程序化粒子)
    └── check_compliance.py                   # 离线违禁词 / 极限词快速校验(兜底)
```

## 数据可信度约定

`references/` 中每条规则带 `status`(active / pending-verify / deprecated)、源 URL、抓取日期。执行只认 `active` + 官方核实条目;教程 / 营销文来源的数据一律标 `pending-verify` 待复核。平台规则变动走巡检流程更新,CHANGELOG 记版本。

> 免责:平台规范随时可能调整,上架前请以官方开放平台当日页面为准。

## License

[MIT](./LICENSE)
