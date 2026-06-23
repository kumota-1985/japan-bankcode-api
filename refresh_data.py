#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全銀協の銀行・支店コードデータ(zengin-code/source-data)を取得し、
data/banks.json と data/branches.json に統合保存する。
出典: zengin-code プロジェクト(MITライセンスで公開・銀行コード自体は公開情報)。
リポジトリのzipを1回でDLして展開する(支店ファイルを1つずつ取らない)。"""
import io
import json
import os
import re
import urllib.request
import zipfile

URL = "https://codeload.github.com/zengin-code/source-data/zip/refs/heads/master"
HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    raw = urllib.request.urlopen(req, timeout=180).read()
    zf = zipfile.ZipFile(io.BytesIO(raw))
    banks, branches = {}, {}
    for n in zf.namelist():
        if n.endswith("/data/banks.json"):
            banks = json.loads(zf.read(n).decode("utf-8"))
        m = re.search(r"/data/branches/(\d+)\.json$", n)
        if m:
            branches[m.group(1)] = json.loads(zf.read(n).decode("utf-8"))

    os.makedirs(os.path.join(HERE, "data"), exist_ok=True)
    bp = os.path.join(HERE, "data", "banks.json")
    rp = os.path.join(HERE, "data", "branches.json")
    with open(bp, "w", encoding="utf-8") as f:
        json.dump(banks, f, ensure_ascii=False, separators=(",", ":"))
    with open(rp, "w", encoding="utf-8") as f:
        json.dump(branches, f, ensure_ascii=False, separators=(",", ":"))
    n_branch = sum(len(v) for v in branches.values())
    print(f"banks: {len(banks)} ({os.path.getsize(bp)/1e6:.2f} MB)")
    print(f"branches: {n_branch} across {len(branches)} banks ({os.path.getsize(rp)/1e6:.2f} MB)")


if __name__ == "__main__":
    main()
