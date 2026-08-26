#!/usr/bin/env python3
"""单张静态贴纸 → 程序化动画 GIF(零 API 成本)。

源图需透明底(PNG RGBA)。输出循环播放的透明底 GIF,默认按微信表情规范
240×240、≤500KB 校验。适合弹跳/摇摆/缩放类简单动效——微信「沙雕动态表情」
的主流做法,比逐帧生成/视频转 GIF 便宜得多。

用法:
  python3 animate_sticker.py cat.png --anim bounce --out cat_bounce.gif
  python3 animate_sticker.py cat.png --anim wobble --size 240x240 --frames 12 --out w.gif
"""
import argparse
import math
import os
import sys

try:
    from PIL import Image
except ImportError:
    sys.stderr.write("缺少依赖 Pillow,请先运行: pip install Pillow\n")
    sys.exit(2)


def load_subject(path):
    """载入并裁掉透明边,拿到紧凑主体。"""
    im = Image.open(path).convert("RGBA")
    bbox = im.getbbox()
    return im.crop(bbox) if bbox else im


def make_frame(subject, size, sx, sy, dx, dy, rot):
    w = max(1, int(subject.width * sx))
    h = max(1, int(subject.height * sy))
    s = subject.resize((w, h), Image.LANCZOS)
    if rot:
        s = s.rotate(rot, resample=Image.BICUBIC, expand=True)
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    x = (size[0] - s.width) // 2 + dx
    y = (size[1] - s.height) // 2 + dy
    canvas.paste(s, (x, y), s)
    return canvas


def build_frames(subject, size, anim, n):
    # 主体基础高度:留出弹跳/摇摆空间
    base = int(size[1] * 0.72)
    k = base / subject.height
    frames = []
    for i in range(n):
        t = i / n  # 0→1 一个循环
        sx, sy, dx, dy, rot = k, k, 0, 0, 0
        if anim == "bounce":
            # 一次落地弹跳:腾空高度 |sin|,落地时压扁(squash & stretch)
            ph = abs(math.sin(math.pi * t))
            dy = -int(size[1] * 0.14 * ph)
            sy = k * (1 - 0.10 * (1 - ph))
            sx = k * (1 + 0.07 * (1 - ph))
        elif anim == "shake":
            dx = int(size[0] * 0.05 * math.sin(2 * math.pi * t))
            rot = 3 * math.sin(2 * math.pi * t)
            sx = sy = k * 0.8
        elif anim == "pulse":
            s = 1 + 0.08 * math.sin(2 * math.pi * t)
            sx = sy = k * 0.8 * s
        elif anim == "wobble":
            rot = 6 * math.sin(2 * math.pi * t)
            dy = int(size[1] * 0.02 * math.sin(4 * math.pi * t))
            sx = sy = k * 0.8
        frames.append(make_frame(subject, size, sx, sy, dx, dy, rot))
    return frames


def to_p(frame, colors=255):
    """RGBA → 带透明索引的 P 模式帧(GIF 1-bit 透明经典配方)。"""
    alpha = frame.getchannel("A")
    p = frame.convert("RGB").quantize(colors=colors, method=2)
    mask = alpha.point(lambda a: 255 if a < 128 else 0)
    p.paste(255, mask)
    p.info["transparency"] = 255
    return p


def save_gif(frames_rgba, out, duration, colors):
    ps = [to_p(f, colors) for f in frames_rgba]
    ps[0].save(
        out,
        save_all=True,
        append_images=ps[1:],
        duration=duration,
        loop=0,
        transparency=255,
        disposal=2,
    )


def main():
    ap = argparse.ArgumentParser(description="静态贴纸 → 程序化动画 GIF")
    ap.add_argument("input", help="透明底 PNG 源图")
    ap.add_argument("--anim", choices=["bounce", "shake", "pulse", "wobble"], default="bounce")
    ap.add_argument("--size", default="240x240", help="输出尺寸,默认 240x240(微信规范)")
    ap.add_argument("--frames", type=int, default=16, help="帧数,默认 16")
    ap.add_argument("--duration", type=int, default=80, help="每帧毫秒,默认 80")
    ap.add_argument("--out", required=True, help="输出 GIF 路径")
    ap.add_argument("--max-kb", type=int, default=500, help="体积上限 KB,默认 500(微信)")
    args = ap.parse_args()

    w, h = (int(x) for x in args.size.lower().split("x"))
    subject = load_subject(args.input)
    frames = build_frames(subject, (w, h), args.anim, args.frames)

    # 体积控制:先 255 色,超限降色,再超限抽帧
    for colors in (255, 127, 63):
        save_gif(frames, args.out, args.duration, colors)
        kb = os.path.getsize(args.out) / 1024
        if kb <= args.max_kb:
            print(f"完成: {args.out} | {w}x{h} | {args.anim} | {args.frames}帧×{args.duration}ms | {colors}色 | {kb:.1f}KB ≤ {args.max_kb}KB PASS")
            return
        if colors == 63 and kb > args.max_kb and args.frames > 8:  # 最后手段:抽帧
            thin = frames[::2]
            save_gif(thin, args.out, args.duration * 2, 63)
            kb = os.path.getsize(args.out) / 1024
            if kb <= args.max_kb:
                print(f"完成(已抽帧至 {len(thin)} 帧): {args.out} | {kb:.1f}KB PASS")
                return
    print(f"警告: 仍超限 {kb:.1f}KB > {args.max_kb}KB,请减帧或缩小主体占比")


if __name__ == "__main__":
    main()
