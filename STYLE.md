# 省錢情報風格規範：「省錢」

> 給負責改這頁或新增類別的 bot（含 **X Free Credits Finder**）：**改 `index.html` 之前，先完整讀完這份文件並遵守。**
>
> 這一頁有自己的樣子，不要做成連結總站的報紙風（深色報頭、金色、暖米色紙）。優惠的新增、更新、刪除、清過期請用 `scripts/deals.py`，不要手改 `deals.json`（見 README）。

## 0. 設計方向

這是一張還沒到期的優惠單。主色是**省錢綠**，快截止用**價籤紅橘**。類別是彩色標籤加小圖示，截止日做成醒目的徽章。過期的不畫出來。

## 1. 硬性規則

1. 單檔自含：`index.html` 內含 CSS 與 JS。優惠由同目錄的 `deals.json` 載入。不載外部字型、CSS、CDN。主畫面圖示與 `site.webmanifest` 用同目錄的檔案。
2. 淺色與深色都要有（`prefers-color-scheme`），每個類別的顏色兩種模式都要定義。
3. 不准：漸層、`box-shadow`、`backdrop-filter`。圓角維持現有大小（卡片 0.85rem、標籤與截止徽章 999px、密碼框 1.35rem），不要自己放大。
4. 手機（約 390px）優先，不可橫向捲動。分類分頁列可以在自己那一列裡橫向滑，整頁不行。
5. 類別只能出現在 `scripts/deals.py` 的 `CATEGORIES` 裡；前端清單（`CATEGORIES` 陣列）與它要同步，名稱與順序都要一致。`保健／海外` 的斜線是全形 `／`。
6. 外部連結維持純 `<a href rel="noopener noreferrer">`，不加 `target`。說明裡的 `[文字](網址)` 也一樣，只允許 `http`／`https`。

## 2. 整體 token（`:root`）

| 用途 | 淺色 | 深色 |
|---|---|---|
| 背景 `--bg` | `#e6f2e8` | `#0c1410` |
| 文字 `--fg` | `#13261c` | `#e7f6ec` |
| 次要文字 `--muted` | `#4f6558` | `#b7cfc0` |
| 卡片 `--paper` | `#f7fbf8` | `#15211b` |
| 分隔線 `--line` | `#c9ddd0` | `#2c4034` |
| 報頭底 `--mast` | `#0b6a3c` | `#072818` |
| 報頭字 `--mast-fg` | `#f4fff8` | `#f3fff6` |
| 報頭說明 `--mast-muted` | `#d7f3e3` | `#c5e6d4` |
| 價籤字 `--tag` | `#ffd2c4` | `#ffb59a` |
| 緊急底 `--urgent` | `#c2410c` | `#ff7a55` |
| 緊急字 `--urgent-ink` | `#fff7f4` | `#3a120c` |
| 即將底 `--soon-fill` | `#fff4e5` | `#3a2714` |
| 即將字 `--soon-ink` | `#8a3d08` | `#ffd7b0` |
| 即將框 `--soon-line` | `#e8b48a` | `#c4894a` |
| 較遠底 `--later-fill` | `#e5f6ea` | `#143226` |
| 較遠字 `--later-ink` | `#0b6a3c` | `#7ddea6` |
| 較遠框 `--later-line` | `#0b6a3c` | `#3dce7a` |

報頭是綠色，最上緣一條價籤紅橘（`border-top`）。小標「省下來」用 `--tag`，旁邊是內嵌的價籤 SVG。標題用 `--sans`，不要改回襯線報頭。

字型只用系統字，不載外部字型。

## 3. 類別標籤

每個類別用一組六個變數，**淺色與深色各一組**，掛在 `.cat-xxx` 上：

```css
.cat-xxx{--fill:…;--ink:…;--soft:…;--mark:…;--mark-ink:…;--hairline:…}
```

- `--fill`／`--ink`：標籤底與標籤字。
- `--mark`／`--mark-ink`：標籤裡的小圖示。`--mark` 也是說明連結的顏色，以及卡片左側色條。
- `--soft`、`--hairline` 留給標籤的次要字與淡框，不要拿來畫截止徽章。

類別標籤只出現在貼頂分頁，帶同一個小圖示。圖示是 SVG sprite 裡的單色線條（`stroke="currentColor"`、`stroke-width="1.7"`、圓角線頭）。分頁下面不要再畫一次類別標題。

優惠卡本身是 `--paper`，不要整張刷成類別色。左側 4px 色條是卡片裡的直線（`::before`，上下與左側都縮進，兩端切平，不跟著 0.85rem 圓角彎）。顏色用該類 `--mark`；24 小時內要截止的改成 `--urgent`。卡片圓角維持 0.85rem。

內文對比至少 4.5:1。標籤字對標籤底、圖示字對圖示底、說明連結（`--mark`）對 `--paper` 都要夠。

| 類別 | class | 圖示 | 淺色 `--mark` |
|---|---|---|---|
| AI 免費額度 | `cat-ai` | `icon-ai` | 紫 `#5b21b6` |
| 電商檔期 | `cat-mall` | `icon-mall` | 朱紅 `#b42318` |
| 居家生活 | `cat-home` | `icon-home` | 橄欖 `#4d6216` |
| 吃喝 | `cat-eat` | `icon-eat` | 莓紅 `#be185d` |
| 軟體訂閱 | `cat-soft` | `icon-soft` | 靛藍 `#243e9c` |
| 保健／海外 | `cat-health` | `icon-health` | 綠 `#166534` |
| 刷卡回饋 | `cat-card` | `icon-card` | 銅 `#8a5a10` |

新類別要再選一個跟上面七個都拉得開的色相，並維持「淺色底深色字、深色底淺色字」。

## 4. 版面與截止徽章

- 解鎖後才畫清單。上方一行「最後更新」（台北時間，取 `deals.json` 裡最新的 `added`）和還在顯示的則數。
- 分類是貼頂分頁（`position: sticky; top: 0`，底色 `--bg`），不是往下捲的目錄。只放還有還沒到期項目的類別，順序與 `CATEGORIES` 相同，沒有「全部」。點一個類別只顯示那一類。沒有 hash 時打開第一個有優惠的類別，網址維持空白。選到的分頁寫進網址 hash（`#cat-ai` 這類），重新整理或分享連結會回到同一個分頁。`#all` 或對不上的 hash 回到第一個有優惠的類別，並把網址改成那個分頁。分頁按鈕 id 加 `tab-`、區塊 id 加 `panel-`，頁面上不要有跟 hash 同名的元素，避免瀏覽器自己捲過去。
- 每個類別一個 `<section>`，裡面直接是優惠卡，不再重複類別標題。卡片標題是連結，截止徽章在標題上面，說明在下面。說明裡若有連結，標題連結不要包住說明。
- 渲染當下已過期的項目直接不畫。同一區裡，**24 小時內要截止的排最前**（比較早的在上），其餘依截止時間由近到遠，`expires` 是 null 的放最後、維持原順序。
- 截止徽章用 `.expiry`，再加一個語氣 class。只有日期、或時間是 23:59，視為那天結束，不另外寫鐘點。`expires` 是 null 就不顯示徽章。

| 情況 | 文字 | class | 顏色 |
|---|---|---|---|
| 台北時間就是截止那天，且沒有更早的鐘點 | 今天截止 | `is-urgent` | `--urgent` |
| 就是截止那天，但有鐘點 | 今天 23:00 截止 | `is-urgent` | `--urgent` |
| 距截止日 1 到 6 天，且是整天 | 剩 2 天 | `is-soon`；若同時落在 24 小時內則改 `is-urgent` | `--soon-*` 或 `--urgent` |
| 更遠，或需要寫鐘點 | 到 12/6、到 11/26 02:00 | `is-later`；6 天內的鐘點用 `is-soon` | `--later-*` 或 `--soon-*` |

天數用台北日曆相減（截止日減今天），不是四捨五入的小時。

## 5. 新增類別的完整步驟

1. `scripts/deals.py` 的 `CATEGORIES` 加上名稱（決定區塊順序）。
2. `index.html` 的 `CATEGORIES` 陣列加一筆：`{ name, id, className: "cat-xxx", icon: "icon-xxx" }`，順序與第 1 步一致。`id` 用在分頁 hash（`#cat-ai`）。分頁按鈕 id 加 `tab-`、區塊 id 加 `panel-`。
3. 在淺色區塊加 `.cat-xxx { … }`，並在 `@media (prefers-color-scheme: dark)` 區塊加深色版。
4. 在 SVG sprite 加 `<symbol id="icon-xxx">`：單色線條、`stroke="currentColor"`、`stroke-width="1.7"`、圓角線頭。
5. README 的類別清單同步。
6. 用 `python3 -m http.server` 開頁面，淺色與深色各看一次，並確認約 390px 寬沒有橫向捲動。

## 6. 檢查清單

- [ ] 頁面仍是省錢綠加價籤紅橘，沒有改回米色報紙或金色小標。
- [ ] 類別是彩色標籤加小圖示，優惠卡不是整張色塊。
- [ ] 截止徽章分緊急、即將、較遠，24 小時內的排在該類最前。
- [ ] 淺色與深色都有定義，且文字對比足夠。
- [ ] `deals.py` 與前端的類別清單、順序一致，含 `保健／海外` 的全形斜線。
- [ ] 分類是分頁，沒有「全部」。沒有優惠的類別不出現。沒有 hash 時打開第一個有優惠的類別；`#all` 也回到那一頁。選到的分頁寫在 hash。390px 分頁列可橫滑，整頁不橫向捲動。
- [ ] 390px 寬度無橫向捲動；沒有外部字型、CSS 或 CDN。
- [ ] 外部連結是 `<a rel="noopener noreferrer">`，沒有 `target`。
- [ ] 沒有漸層、`box-shadow`、`backdrop-filter`。
- [ ] 密碼門仍用同一組 PBKDF2 常數與 `link-hub-gate`。
