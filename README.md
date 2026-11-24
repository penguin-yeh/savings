# 省錢情報

還沒到期的台灣優惠，依類別整理在同一頁。過期的不顯示，也不是一天一頁的封存。

GitHub Pages 從 `main` 根目錄提供這個網站：<https://penguin-yeh.github.io/savings/>

類別順序：AI 免費額度、電商檔期、居家生活、吃喝、軟體訂閱、保健／海外、刷卡回饋。`保健／海外` 的斜線是全形 `／`。

**X Free Credits Finder** 和其他 bot 用 `scripts/deals.py` 維護清單。不要手改 `deals.json`。

**改頁面或新增類別前，請先讀 [STYLE.md](STYLE.md)（「省錢」配色，不是連結總站那套報紙風）。**

## 本機預覽

```bash
python3 -m http.server 8080
```

打開 <http://127.0.0.1:8080/>。

## 密碼

首頁會先問密碼，通過後把比對用的 hash 記在這台瀏覽器的 `localStorage`（鍵名 `link-hub-gate`，跟每日連結總站同一把），下次（包含加到 iPhone 主畫面）就不用再輸入。密碼本身不會存下來。這只擋一下隨便點進來的人，`deals.json` 仍然公開、可以直接抓。

演算法是 PBKDF2-SHA256（WebCrypto），常數與 link-hub 相同：

- `salt_b64` = `mv24FYlAQXqzWPt+kNbhdw==`
- `iterations` = `200000`
- `hash_b64` = `3xAExdNY8/ArB2V6OVaNLkCIqCfvftk81PIMvdj9sIM=`

頁面有 `noindex`。

## 給 bot：不要手改 deals.json

`deals.json` 是一個陣列。每一筆是：

| 欄位 | 說明 |
|---|---|
| `id` | 穩定的英數 id。同一網址可以有不同 id |
| `category` | 上面七個類別之一 |
| `title` | 標題 |
| `note` | 說明。可以寫 `[文字](https://網址)`，頁面會變成連結 |
| `href` | 這則優惠的網址 |
| `expires` | `YYYY-MM-DD`、帶時區的 ISO 時間，或 `null`（不知道何時結束） |
| `added` | 新增當下的台北時間，由指令寫入。更新時不改 |

頁面的「最後更新」是目前檔案裡最新的 `added`，並換算成台北時間。

只有日期的 `expires` 表示**台北時間那天整天都還算有效**，次日 00:00 起算過期。帶時間的值則以那個瞬間為準（`now >= expires` 就過期）。頁面渲染時會再藏一次已經過期的項目；`prune` 會把它們從檔案刪掉。`null` 不會被藏，也不會被 `prune` 刪掉。

同一篇報導可以掛兩筆（現在的 7-11 與全家就是同一個 `href`）。這種情況**一定要給不同的 `--id`**。沒有 `--id` 時，指令用 `href` 對到唯一的一筆來更新；若對到多筆會停下來，請你改帶 `--id`。

### 新增

```bash
python3 scripts/deals.py add \
  --id renoise-200 \
  --category "AI 免費額度" \
  --title "Renoise $200 額度抽 2 人" \
  --note "追蹤 @renoiseai 並轉推（官方帳號，AI 影片）" \
  --href "https://x.com/renoiseai/status/2125263159816827176"
```

沒寫 `--expires` 的新項目，期限是 `null`。有期限就加上，例如整天到 11/30：

```bash
python3 scripts/deals.py add \
  --id momo-bf \
  --category "電商檔期" \
  --title "momo 黑五購物節" \
  --note "至 11/30，每晚 21:00 滿額登記送 mo 點" \
  --href "https://www.momoshop.com.tw/edm/cmmedm.jsp?lpn=O7BnxyFfXGw&n=1" \
  --expires 2026-11-30
```

有鐘點就寫台北時間的 ISO，例如 `--expires 2026-11-26T02:00:00+08:00`。`--expires null` 會把期限清掉。

不寫 `--id` 也可以新增。指令會依標題和網址產生 id，並印出 `新增 <id>`。

### 更新（upsert）

同一個 `--id` 再跑一次就是更新。沒寫的欄位保持原樣，`added` 也不會改。

```bash
python3 scripts/deals.py add \
  --id momo-bf \
  --note "至 11/30，每晚 21:00 滿額登記送 mo 點" \
  --expires 2026-11-30
```

沒有 `--id`、但 `--href` 在檔案裡只出現一次時，會更新那一筆：

```bash
python3 scripts/deals.py add \
  --href "https://shopee.tw/m/shopee-mall-sale" \
  --expires 2026-11-25
```

`--href` 對到多筆時不會猜，請改用 `--id`。帶了新的 `--id`（檔案裡還沒有）則一律新增，就算網址跟別筆一樣。

### 刪除

```bash
python3 scripts/deals.py remove --id momo-bf
```

```bash
python3 scripts/deals.py remove --href "https://shopee.tw/m/shopee-mall-sale"
```

`--href` 對到多筆時不會刪，請改用 `--id`。`--id` 和 `--href` 不要同時給。

### 清掉過期

以台北現在時間為準，刪掉已經過期的項目。期限是 `null` 或解析不了的會留下。

```bash
python3 scripts/deals.py prune
```

建議更新完清單後跑一次，避免過期項目堆在檔案裡。就算還沒跑，頁面也不會把它們畫出來。
