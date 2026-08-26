# emoji-sticker-cn · 中文表情包生成合规助手

把「一张图 / 一段描述」变成**可直接上架或发布的中文平台表情包**。

GitHub / ClawHub 上的表情包 skill 大多只管「生成」,普遍忽略两件在中国平台致命的事:

1. **平台尺寸规范**——微信表情开放平台对主图 / 图标 / 封面 / 横幅各有硬性尺寸、体积、透明底要求,不达标直接驳回;
2. **内容合规**——上架描述、专辑名踩了广告法极限词 / 平台违禁词,轻则限流重则下架。

本 skill 只做这条「合规流水线」增量:生成层复用宿主环境的生图工具(不重造模型),规则层内置可持续维护的平台硬约束。

## 特性

- **硬约束速查前置**:微信全参数表(240×240 主图 / 50×50 图标 / 750×400 横幅…)、小红书 / 抖音推荐尺寸、违禁词红线,产出前逐条对照
- **四条工作路线**:
  - A 微信表情上架(成套 8–24 张 + 上架元数据)
  - B 小红书 / 抖音内联表情(笔记配图 / 聊天表情)
  - C 已有图片批量裁切 + 规范命名 + ZIP 打包
  - D **动态 GIF——单张静态贴图程序化动画(bounce / shake / pulse / wobble),零 API 成本**,自动控体积 ≤500KB
- **规则更新与退出机制**:条目生命周期 `pending-verify → active → deprecated`;说「更新表情包规则」即触发巡检(WebFetch 官方源 → diff 报告 → 确认后落盘),作废规则留痕不删除
- **违禁词校验**:优先复用 `multi-wordcheck` 类实时检测 skill(宿主环境有则用);未安装则降级用内置离线种子集(法定极限词)兜底

## 安装

```bash
# ClawHub (OpenClaw)
npx clawhub@latest install emoji-sticker-cn

# 或从 GitHub 克隆到你的 skills 目录
git clone https://github.com/bonniegeng-max/emoji-sticker-cn.git
```

依赖:`pip install Pillow`(裁切 / 动画脚本)。

## 使用

对宿主 agent 说:

- 「帮我做一套微信表情包」→ 路线 A
- 「把这张图裁成小红书尺寸」→ 路线 C
- 「让这张贴纸动起来」→ 路线 D
- 「更新表情包规则」→ 巡检工作流

脚本直用:

```bash
# 批量裁切 + 规范命名 + 打包
python3 scripts/resize_stickers.py ./raw --size 240x240 --bg transparent --format png --prefix emoji --out ./wechat --zip

# 静态贴纸 → 动画 GIF(零积分)
python3 scripts/animate_sticker.py cat.png --anim bounce --out cat_bounce.gif
```

## 目录

```
├── SKILL.md                                  # 工作流 + 硬约束 + 更新/退出机制
├── references/
│   ├── 中文平台表情包尺寸规范.md              # 微信/QQ/飞书官方核实 + 内联平台标注(持续维护)
│   └── 中文平台违禁词合规参考.md              # 类别体系 + 权威来源 + 极限词种子集(持续维护)
└── scripts/
    ├── resize_stickers.py                    # 批量裁切 / 命名 / ZIP
    └── animate_sticker.py                    # 静态贴纸 → 程序化动画 GIF
```

## 数据可信度约定

`references/` 中每条规则带 `status`(active / pending-verify / deprecated)、源 URL、抓取日期。执行只认 `active` + 官方核实条目;教程 / 营销文来源的数据一律标 `pending-verify` 待复核。平台规则变动走巡检流程更新,CHANGELOG 记版本。

> 免责:平台规范随时可能调整,上架前请以官方开放平台当日页面为准。

## License

[MIT](./LICENSE)
