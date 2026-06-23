# Japan Bank & Branch Code API

日本の銀行コード(4桁)・支店コード(3桁)を引く/検索する小さなREST API。
データ = zengin-code(全銀協 銀行・支店コード, 公開情報, MIT)。銀行1,146・支店31,219。

## エンドポイント
- `GET /v1/bank?code=0001` — 銀行コード → 銀行情報
- `GET /v1/banks?q=みずほ` — 銀行名で検索
- `GET /v1/branch?bank=0001&branch=001` — 支店情報
- `GET /v1/branches?bank=0001&q=新宿` — 支店一覧/検索

## ローカル実行
```bash
pip install -r requirements.txt
uvicorn app:app --reload --port 8007   # http://127.0.0.1:8007/docs
```

## データ更新
```bash
python refresh_data.py   # zengin-code のzipを再取得し data/{banks,branches}.json を更新
```
`.github/workflows/refresh.yml` が毎月自動で再取得→commit。

## デプロイ / 出品
- `render.yaml`(Render free)。データ~3.5MB。
- `openapi_rapidapi.json` を RapidAPI に / `DOCS_TAB.md` を Docs に / `bankcode_logo.png` をロゴに。
