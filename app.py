#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Japan Bank & Branch Code API  --  flip_bankcodeapi/app.py
================================================================================
日本の銀行コード(4桁)・支店コード(3桁)を引く/検索するAPI。金融連携・口座入力の定番ニーズ。
データ = zengin-code(全銀協の銀行・支店コードを公開・MIT)。銀行コード自体は公開情報。

  - GET /v1/bank?code=0001            銀行コード → 銀行情報
  - GET /v1/banks?q=みずほ            銀行名で検索
  - GET /v1/branch?bank=0001&branch=001   支店コード → 支店情報
  - GET /v1/branches?bank=0001        その銀行の支店一覧/検索

  pip install -r requirements.txt
  uvicorn app:app --reload --port 8007   → http://127.0.0.1:8007/docs
"""
import json
import os
import re
from typing import Optional

from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.responses import HTMLResponse, PlainTextResponse

_HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(_HERE, "data", "banks.json"), encoding="utf-8") as _f:
    BANKS = json.load(_f)                                   # "0001" -> {code,name,kana,hira,roma}
with open(os.path.join(_HERE, "data", "branches.json"), encoding="utf-8") as _f:
    BRANCHES = json.load(_f)                                # "0001" -> {"001": {...}}

RAPIDAPI_SECRET = os.environ.get("RAPIDAPI_PROXY_SECRET")
PRO_KEYS = set(k.strip() for k in os.environ.get("BANKCODE_KEYS", "").split(",") if k.strip())
ATTRIBUTION = ("出典: zengin-code(全銀協 銀行・支店コード, 公開情報)を加工。"
               "Source: zengin-code (Japanese bank/branch codes), processed.")

app = FastAPI(
    title="Japan Bank & Branch Code API",
    version="1.0.0",
    description="Look up Japanese bank codes (4-digit) and branch codes (3-digit), or search banks by "
                "name. Name, katakana, hiragana and romaji for every bank and branch. zengin-code data.",
)


def auth(x_api_key: Optional[str], rapid_secret: Optional[str]) -> None:
    if RAPIDAPI_SECRET:
        if rapid_secret == RAPIDAPI_SECRET:
            return
        if x_api_key and x_api_key in PRO_KEYS:
            return
        raise HTTPException(status_code=403, detail="Requests must go through the RapidAPI marketplace.")


def _bank_code(code: str) -> str:
    c = re.sub(r"\D", "", code or "")
    if not 1 <= len(c) <= 4:
        raise HTTPException(status_code=422, detail="bank code must be up to 4 digits")
    return c.zfill(4)


def _branch_code(code: str) -> str:
    c = re.sub(r"\D", "", code or "")
    if not 1 <= len(c) <= 3:
        raise HTTPException(status_code=422, detail="branch code must be up to 3 digits")
    return c.zfill(3)


def _match(rec: dict, q: str) -> bool:
    ql = q.lower()
    return (q in rec.get("name", "") or q in rec.get("kana", "") or q in rec.get("hira", "")
            or ql in rec.get("roma", "").lower())


# --------------------------------------------------------------------------- #
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def root():
    return ('<h2>Japan Bank &amp; Branch Code API</h2>'
            '<p>Japanese bank / branch code lookup &amp; search.</p>'
            '<p>→ <a href="/docs">/docs</a>. <code>/v1/bank?code=0001</code> '
            '<code>/v1/branch?bank=0001&amp;branch=001</code></p>')


@app.get("/ping", include_in_schema=False)
def ping():
    return {"status": "ok"}


@app.get("/llms.txt", response_class=PlainTextResponse, include_in_schema=False)
def llms_txt():
    return """# Japan Bank & Branch Code API
> Japanese bank (4-digit) and branch (3-digit) code lookup & search. 1,100+ banks, 31,000+ branches.

Base URL: https://japan-bankcode-api.onrender.com
Docs: https://japan-bankcode-api.onrender.com/docs
OpenAPI: https://japan-bankcode-api.onrender.com/openapi.json

## Endpoints
- GET /v1/bank?code=0001 - bank code -> bank (name + katakana/hiragana/romaji)
- GET /v1/banks?q=みずほ - search banks by name
- GET /v1/branch?bank=0001&branch=001 - branch code -> branch
- GET /v1/branches?bank=0001 - list/search a bank's branches
- Access: via the RapidAPI marketplace (subscribe for a key)
"""


@app.get("/v1/bank")
def bank(code: str = Query(..., description="銀行コード(4桁)。例: 0001"),
         x_api_key: Optional[str] = Header(None),
         x_rapidapi_proxy_secret: Optional[str] = Header(None)):
    """銀行コード → 銀行情報。"""
    auth(x_api_key, x_rapidapi_proxy_secret)
    c = _bank_code(code)
    b = BANKS.get(c)
    if not b:
        raise HTTPException(status_code=404, detail=f"bank not found: {c}")
    return {"data": b, "branch_count": len(BRANCHES.get(c, {})), "attribution": ATTRIBUTION}


@app.get("/v1/banks")
def banks(q: str = Query(..., description="銀行名/カナ/ローマ字(部分一致)。例: みずほ"),
          limit: int = Query(30, ge=1, le=100),
          x_api_key: Optional[str] = Header(None),
          x_rapidapi_proxy_secret: Optional[str] = Header(None)):
    """銀行名で検索。"""
    auth(x_api_key, x_rapidapi_proxy_secret)
    out = []
    for b in BANKS.values():
        if _match(b, q):
            out.append(b)
            if len(out) >= limit:
                break
    return {"count": len(out), "limit": limit, "data": out, "attribution": ATTRIBUTION}


@app.get("/v1/branch")
def branch(bank: str = Query(..., description="銀行コード(4桁)"),
           branch: str = Query(..., description="支店コード(3桁)"),
           x_api_key: Optional[str] = Header(None),
           x_rapidapi_proxy_secret: Optional[str] = Header(None)):
    """銀行コード+支店コード → 支店情報。"""
    auth(x_api_key, x_rapidapi_proxy_secret)
    bc, brc = _bank_code(bank), _branch_code(branch)
    if bc not in BANKS:
        raise HTTPException(status_code=404, detail=f"bank not found: {bc}")
    br = BRANCHES.get(bc, {}).get(brc)
    if not br:
        raise HTTPException(status_code=404, detail=f"branch not found: {bc}-{brc}")
    return {"bank": BANKS[bc], "data": br, "attribution": ATTRIBUTION}


@app.get("/v1/branches")
def branches(bank: str = Query(..., description="銀行コード(4桁)"),
             q: Optional[str] = Query(None, description="支店名で絞り込み(部分一致)"),
             limit: int = Query(50, ge=1, le=500),
             x_api_key: Optional[str] = Header(None),
             x_rapidapi_proxy_secret: Optional[str] = Header(None)):
    """その銀行の支店一覧(q で名前絞り込み)。"""
    auth(x_api_key, x_rapidapi_proxy_secret)
    bc = _bank_code(bank)
    if bc not in BANKS:
        raise HTTPException(status_code=404, detail=f"bank not found: {bc}")
    items = list(BRANCHES.get(bc, {}).values())
    if q:
        items = [b for b in items if _match(b, q)]
    total = len(items)
    items = items[:limit]
    return {"bank": BANKS[bc], "count": len(items), "total": total, "limit": limit,
            "data": items, "attribution": ATTRIBUTION}
