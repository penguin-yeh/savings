# 省錢情報風格規範：「報社總編桌」

> 給負責改這頁或新增類別的 bot（含 **X Free Credits Finder**）：**改 `index.html` 之前，先完整讀完這份文件並遵守。**
>
> 視覺沿用 [link-hub 的報社總編桌](https://github.com/penguin-yeh/link-hub/blob/main/STYLE.md)：深色報頭、襯線標題、暖米色紙、類別靠顏色與圖示分辨。這份文件把**這個網站**的樣子固定下來。優惠的新增、更新、刪除、清過期請用 `scripts/deals.py`，不要手改 `deals.json`（見 README）。

## 0. 設計方向

這一頁是還沒到期的台灣優惠。不是每日封存。過期的項目不畫出來。類別是固定的七塊，每塊一種顏色。

## 1. 硬性規則

1. 單檔自含：`index.html` 內含 CSS 與 JS。優惠由同目錄的 `deals.json` 載入。不載外部字型、CSS、CDN。主畫面圖示與 `site.webmanifest` 用同目錄的檔案，跟 link-hub 一樣。
2. 淺色與深色都要有（`prefers-color-scheme`），每個類別的顏色兩種模式都要定義。
3. 不准：漸層、`box-shadow`、`backdrop-filter`。圓角維持現有大小（報頭卡片 1.35rem、優惠卡 1rem、芯片 999px），不要自己放大。
4. 手機（約 390px）優先，不可橫向捲動。分類分頁列可以在自己那一列裡橫向滑，整頁不行。
5. 類別只能出現在 `scripts/deals.py` 的 `CATEGORIES` 裡；前端清單（`CATEGORIES` 陣列）與它要同步，名稱與順序都要一致。`保健／海外` 的斜線是全形 `／`。
6. 外部連結維持純 `<a href rel="noopener noreferrer">`，不加 `target`。說明裡的 `[文字](網址)` 也一樣，只允許 `http`／`https`。

## 2. 整體 token（`:root`）

| 用途 | 淺色 | 深色 |
|---|---|---|
| 背景 `--bg` | `#efe6d8` | `#100f0d` |
| 文字 `--fg` | `#1c1915` | `#f4efe6` |
| 次要文字 `--muted` | `#6f655b` | `#b7ab9c` |
| 紙張 `--paper` | `#fbf7f1` | `#1b1a17` |
| 分隔線 `--line` | `#e3d5c2` | `#34302a` |
| 報頭底 `--mast` | `#1a1815` | `#070706` |
| 報頭字 `--mast-fg` | `#f8f2e8` | `#f7f2ea` |
| 金色 `--gold` | `#e2b15a` | `#e2b15a` |

字型：標題用 `--serif`（Iowan Old Style / Palatino / Songti TC / Noto Serif TC），內文用 `--sans`（系統字型）。

## 3. 類別色

每個類別用一組六個變數，**淺色與深色各一組**，掛在 `.cat-xxx` 上：

```css
.cat-xxx{--fill:…;--ink:…;--soft:…;--mark:…;--mark-ink:…;--hairline:…}
```

- `--fill`：卡片底色；`--ink`：標題文字；`--soft`：說明與截止標籤；
- `--mark`：圖示底色，以及說明裡的連結；`--mark-ink`：圖示上的顏色；`--hairline`：截止標籤的框線。

內文對比至少 4.5:1（`--ink`／`--soft` 對 `--fill`，`--mark-ink` 對 `--mark`，`--mark` 當連結色時也要對 `--fill`）。

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

## 4. 版面

- 報頭：金色小標 `DEAL DESK`、襯線標題「省錢情報」、一行說明。
- 解鎖後才畫清單。上方一行「最後更新」（台北時間，取 `deals.json` 裡最新的 `added`）和還在顯示的則數。
- 分類是貼頂分頁（`position: sticky; top: 0`），不是往下捲的目錄。第一個是「全部」，後面只放還有還沒到期項目的類別，順序與 `CATEGORIES` 相同。點一個類別只顯示那一類；「全部」則依序顯示每一類，每類仍有自己的標題。選到的分頁寫進網址 hash（`#all`、`#cat-ai` 這類），重新整理或分享連結會回到同一個分頁。沒有對上的 hash 回到「全部」。
- 每個類別一個 `<section>`：圖示加標題（類別標籤），下面每則是色塊卡片。單一類別的分頁也留著這個標題。標題是連結，截止是醒目的小標籤，說明在下面。說明裡若有連結，標題連結不要包住說明（不能巢狀 `<a>`）。
- 截止標籤：當天且沒有更早的鐘點寫「今天截止」；當天有鐘點寫「今天 23:00 截止」；其他日子寫「到 11/30」或「到 11/26 02:00」。只有日期、或時間是 23:59，視為那天結束，不另外寫鐘點。`expires` 是 null 就不顯示標籤。
- 渲染當下已過期的項目直接不畫，就算檔案裡還在。

## 5. 新增類別的完整步驟

缺任何一步都會讓頁面壞掉或顏色不一致：

1. `scripts/deals.py` 的 `CATEGORIES` 加上名稱（決定區塊順序）。
2. `index.html` 的 `CATEGORIES` 陣列加一筆：`{ name, id, className: "cat-xxx", icon: "icon-xxx" }`，順序與第 1 步一致。`id` 用在分頁 hash（`#cat-ai`）。分頁按鈕 id 加 `tab-`、區塊 id 加 `panel-`，頁面上不要有跟 hash 同名的元素，避免瀏覽器自己捲過去。
3. 在淺色區塊加 `.cat-xxx { … }`，並在 `@media (prefers-color-scheme: dark)` 區塊加深色版。
4. 在 SVG sprite 加 `<symbol id="icon-xxx">`：單色線條、`stroke="currentColor"`、`stroke-width="1.7"`、圓角線頭，與現有圖示一致。
5. README 的類別清單同步。
6. 用 `python3 -m http.server` 開頁面，淺色與深色各看一次，並確認約 390px 寬沒有橫向捲動。

## 6. 檢查清單

- [ ] 新增或修改的顏色都用 `.cat-*` 的六個變數，沒有直接寫死在元件裡。
- [ ] 淺色與深色都有定義，且文字對比足夠。
- [ ] 圖示是單色線條，風格與其他圖示一致。
- [ ] `deals.py` 與前端的類別清單、順序一致，含 `保健／海外` 的全形斜線。
- [ ] 分類是分頁（含「全部」）。沒有優惠的類別不出現。選到的分頁寫在 hash。390px 分頁列可橫滑，整頁不橫向捲動。
- [ ] 390px 寬度無橫向捲動；頁面沒有載入任何外部字型、CSS 或 CDN。
- [ ] 外部連結是 `<a rel="noopener noreferrer">`，沒有 `target`。
- [ ] 沒有漸層、`box-shadow`、`backdrop-filter`。
