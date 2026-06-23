#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Japan Bank & Branch Code API のロゴ(500x500 PNG)を生成。
コンセプト: 銀行の建物アイコン(切妻屋根+柱)= 誰でも銀行だと分かる。"""
import os
from PIL import Image, ImageDraw

W = 500
GREEN = (4, 120, 87, 255)       # #047857 背景
WHITE = (255, 255, 255, 255)

img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
d.rounded_rectangle([0, 0, W - 1, W - 1], radius=112, fill=GREEN)

# 切妻屋根(三角のペディメント)
d.polygon([(250, 132), (126, 214), (374, 214)], fill=WHITE)
# 屋根下の梁
d.rounded_rectangle([126, 222, 374, 250], radius=8, fill=WHITE)
# 4本の柱
for x in (150, 208, 266, 324):
    d.rounded_rectangle([x, 262, x + 26, 352], radius=7, fill=WHITE)
# 土台
d.rounded_rectangle([116, 360, 384, 392], radius=9, fill=WHITE)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bankcode_logo.png")
img.save(out)
print("saved:", out, img.size)
