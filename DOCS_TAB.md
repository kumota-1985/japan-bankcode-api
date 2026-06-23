# Docs タブに貼る内容(英語・Markdown)— Japan Bank & Branch Code API

RapidAPIの **Docs**(About)タブに、下の `---` 内の英語Markdownをそのまま貼ってください。
ロゴは `bankcode_logo.png`(500x500)を General の Upload Logo に。

---

# Japan Bank & Branch Code — Documentation

Look up Japanese **bank codes** (4-digit 全銀協 codes) and **branch codes** (3-digit), or **search banks by name**. Every bank and branch comes with name plus **katakana / hiragana / romaji**. 1,100+ banks, 31,000+ branches. Ideal for bank-account input forms and financial integrations.

## Authentication
You don't manage any keys yourself. **Subscribe to a plan** (BASIC is free) and use the auto-generated snippets on the **Endpoints** tab — RapidAPI injects your `X-RapidAPI-Key` / `X-RapidAPI-Host` headers automatically.

---

## GET /v1/bank
Bank code → bank.

| Param | Required | Example |
|---|---|---|
| `code` | **yes** | `0001` (also accepts `1`) |

**Example:** `GET /v1/bank?code=0001`
```json
{
  "data": { "code": "0001", "name": "みずほ", "kana": "ミズホ", "hira": "みずほ", "roma": "mizuho" },
  "branch_count": 494
}
```

## GET /v1/banks
Search banks by name / katakana / hiragana / romaji (partial-match).

| Param | Required | Notes |
|---|---|---|
| `q` | **yes** | e.g. `みずほ` or `mizuho` |
| `limit` | no | default 30, max 100 |

**Example:** `GET /v1/banks?q=三菱` → `{ "count": 3, "data": [ { "code": "0005", "name": "三菱ＵＦＪ", … } ] }`

## GET /v1/branch
Branch code → branch (also returns the bank).

| Param | Required | Example |
|---|---|---|
| `bank` | **yes** | `0001` |
| `branch` | **yes** | `001` |

**Example:** `GET /v1/branch?bank=0001&branch=001`
```json
{ "bank": { "code": "0001", "name": "みずほ" },
  "data": { "code": "001", "name": "東京営業部", "kana": "トウキヨウ", "hira": "とうきよう", "roma": "toukiyou" } }
```

## GET /v1/branches
List (and optionally filter by name) a bank's branches.

| Param | Required | Notes |
|---|---|---|
| `bank` | **yes** | bank code |
| `q` | no | filter branches by name |
| `limit` | no | default 50, max 500 |

**Example:** `GET /v1/branches?bank=0001&q=新宿`

---

## Notes
- Bank codes are 4 digits, branch codes 3 digits (zero-padded; the API also accepts un-padded numbers).
- Data is refreshed monthly.

## Data source & attribution
Bank/branch code data is from the open-source **zengin-code** project (Japanese bank & branch codes; the codes themselves are public information). Independent service. Each response includes an `attribution` field — please display it.
