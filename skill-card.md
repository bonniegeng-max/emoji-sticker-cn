## Description:

This skill helps agents create Chinese-platform compliant emoji and sticker packs for WeChat Sticker Open Platform, Xiaohongshu, and Douyin by guiding image generation, platform-specific resizing and cropping, sequential naming, asset machine-checking (size/format/size-limit/alpha/white-fringe/similarity), submission checklist generation, and sensitive-word compliance checks.

This skill is ready for commercial/non-commercial use.

## Publisher:

[bonniegeng-max](https://clawhub.ai/user/bonniegeng-max)

### License/Terms of Use:

MIT

## Use Case:

External creators, designers, and developers use this skill to prepare sticker packs and sticker-related copy for Chinese social platforms, especially WeChat sticker submissions and Xiaohongshu or Douyin inline images. It also supports local resizing, animated GIF creation, metadata preparation, and rule-inspection workflows.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Rule-inspection requests may fetch current platform pages and propose edits to the skill's reference files.

Mitigation: Review fetched-source summaries and file diffs before approving any reference updates.

Risk: Sticker generation or sensitive-word checks may send prompts, images, or text to host-provided external tools when the user chooses those workflows.

Mitigation: Confirm paid ImageGen usage and external sensitive-word checking before sending user content to those tools.

Risk: Offline prohibited-word references are a fallback and may not reflect fast-changing platform enforcement.

Mitigation: Prefer the host's real-time multi-wordcheck workflow when available and treat offline checks as limited pre-screening.

## Reference(s):

- [Chinese Platform Sticker Size Reference](references/中文平台表情包尺寸规范.md)
- [Chinese Platform Prohibited Words Compliance Reference](references/中文平台违禁词合规参考.md)
- [WeChat Sticker Open Platform Guide](https://sticker.weixin.qq.com/cgi-bin/mmemoticon-bin/readtemplate?t=guide/index.html)
- [QQ Original Gallery Design Rules](https://yuanchuang.qq.com/html/design_rule.html) (domain deregistered 2026-09-16, platform likely defunct — QQ specs deprecated)
- [Feishu Sticker Help Center](https://feishu.cn/hc/zh-CN/articles/360049068046)
- [WeChat Public Platform Operations Specification](https://fuwu.weixin.qq.com/community/develop/article/doc/000a46f78684f8b21d903690460013)
- [Douyin Community Rules](https://www.douyin.com/rule/policy)

## Skill Output:

**Output Type(s):** [Guidance, Markdown, Code, Shell commands, Configuration, Files]

**Output Format:** [Markdown guidance with inline bash commands and generated image or ZIP file outputs]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May produce resized PNG, JPG, GIF, or WebP sticker assets, animated GIFs, upload metadata, compliance review notes, and optional ZIP packages.]

## Skill Version(s):

1.3.0 (source: frontmatter and server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
