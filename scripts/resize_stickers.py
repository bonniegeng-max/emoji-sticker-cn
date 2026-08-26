#!/usr/bin/env python3
"""批量将表情原图裁切/缩放为指定平台尺寸并规范命名、可选打包 ZIP。

依赖: Pillow  (缺失时: pip install Pillow)
设计: 本脚本只做机械的「缩放 + 居中贴合 + 顺序命名 + 打包」,
      平台尺寸规范以 emoji-sticker-cn/references/中文平台表情包尺寸规范.md 为准(单一事实源)。

用法:
  python3 resize_stickers.py ./raw --size 240x240 --bg transparent --format png --prefix emoji --out ./out --zip
  python3 resize_stickers.py ./raw --size 750x400 --bg white --format png --prefix banner --out ./out
"""
import argparse
import os
import sys
import zipfile

try:
    from PIL import Image
except ImportError:
    sys.stderr.write("缺少依赖 Pillow,请先运行: pip install Pillow\n")
    sys.exit(2)


def parse_size(s: str):
    w, h = s.lower().split("x")
    return int(w), int(h)


def make_bg(w, h, bg):
    if bg == "transparent":
        return Image.new("RGBA", (w, h), (0, 0, 0, 0))
    elif bg == "white":
        return Image.new("RGB", (w, h), (255, 255, 255))
    else:  # black
        return Image.new("RGB", (w, h), (0, 0, 0))


def process_one(src_path, size, bg, fmt, out_path):
    img = Image.open(src_path).convert("RGBA" if bg == "transparent" else "RGBA")
    # 先缩放到「贴合」目标框(保持比例,不裁切重要内容)
    img.thumbnail(size, Image.LANCZOS)
    canvas = make_bg(*size, bg)
    # 居中粘贴
    off_x = (size[0] - img.width) // 2
    off_y = (size[1] - img.height) // 2
    if bg == "transparent":
        canvas.paste(img, (off_x, off_y), img)
    else:
        canvas.paste(img.convert("RGB"), (off_x, off_y))
    save_args = {}
    if fmt == "jpg":
        canvas = canvas.convert("RGB")
    elif fmt == "png" and bg == "transparent":
        save_args["optimize"] = True
    canvas.save(out_path, format=fmt.upper(), **save_args)
    return out_path


def main():
    ap = argparse.ArgumentParser(description="表情包批量裁切/缩放/命名/打包")
    ap.add_argument("input", help="原图文件或目录")
    ap.add_argument("--size", required=True, help="目标尺寸,如 240x240")
    ap.add_argument("--bg", choices=["transparent", "white", "black"], default="transparent")
    ap.add_argument("--format", choices=["png", "jpg", "gif", "webp"], default="png")
    ap.add_argument("--prefix", default="sticker", help="输出文件名前缀")
    ap.add_argument("--out", default="./out", help="输出目录")
    ap.add_argument("--zip", action="store_true", help="额外打包成 ZIP")
    args = ap.parse_args()

    size = parse_size(args.size)
    os.makedirs(args.out, exist_ok=True)

    # 收集输入文件
    if os.path.isdir(args.input):
        files = sorted(
            f for f in os.listdir(args.input)
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"))
        )
        files = [os.path.join(args.input, f) for f in files]
    else:
        files = [args.input]

    if not files:
        sys.stderr.write("未找到输入图片\n")
        sys.exit(1)

    ext = args.format
    out_paths = []
    for i, fp in enumerate(files, 1):
        out_name = f"{args.prefix}_{i:02d}.{ext}"
        out_path = os.path.join(args.out, out_name)
        process_one(fp, size, args.bg, args.format, out_path)
        out_paths.append(out_path)
        print(f"[{i:02d}] {os.path.basename(fp)} -> {out_name}")

    if args.zip:
        zip_name = os.path.join(args.out, f"{args.prefix}_{args.size.replace('x','x')}.zip")
        with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as z:
            for p in out_paths:
                z.write(p, os.path.basename(p))
        print(f"已打包: {zip_name}")

    print(f"完成,共 {len(out_paths)} 张,输出目录: {args.out}")


if __name__ == "__main__":
    main()
