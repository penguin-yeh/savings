#!/usr/bin/env python3
"""維護省錢情報的 deals.json。

給 X Free Credits Finder 與其他 bot：不要手改 deals.json。
新增、更新、刪除、清掉過期項目都用這個指令。用法見 README.md。
"""

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

CATEGORIES = (
    "AI 免費額度",
    "電商檔期",
    "居家生活",
    "吃喝",
    "軟體訂閱",
    "保健／海外",
    "刷卡回饋",
)

TZ = ZoneInfo("Asia/Taipei")
ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "deals.json"
KEYS = ("id", "category", "title", "note", "href", "expires", "added")
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class _Unset:
    def __repr__(self):
        return "UNSET"


UNSET = _Unset()


def taipei_now():
    return datetime.now(TZ)


def format_added(now):
    if now.tzinfo is None:
        now = now.replace(tzinfo=TZ)
    else:
        now = now.astimezone(TZ)
    return now.isoformat(timespec="seconds")


def parse_expires(value):
    """回傳 YYYY-MM-DD、台北時間的 ISO 字串，或 None。"""
    if value is None:
        return None
    text = str(value).strip()
    if text.lower() in {"", "null", "none"}:
        return None
    if DATE_RE.fullmatch(text):
        datetime.strptime(text, "%Y-%m-%d")
        return text
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("expires 須為 YYYY-MM-DD、ISO 時間，或 null") from exc
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=TZ)
    else:
        dt = dt.astimezone(TZ)
    return dt.isoformat(timespec="seconds")


def expires_arg(value):
    try:
        return parse_expires(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def expiry_instant(value):
    """期限的截止瞬間（不含）。日期視為台北時間該日結束、次日 00:00。"""
    if value is None or value == "":
        return None
    text = str(value).strip()
    if DATE_RE.fullmatch(text):
        year, month, day = (int(part) for part in text.split("-"))
        start = datetime(year, month, day, tzinfo=TZ)
        return start + timedelta(days=1)
    dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=TZ)
    return dt


def is_expired(value, now):
    if value is None or value == "":
        return False
    instant = expiry_instant(value)
    if now.tzinfo is None:
        now = now.replace(tzinfo=TZ)
    return now >= instant


def validate_id(value):
    if not value or not ID_RE.fullmatch(value):
        raise SystemExit("id 只能用英數、點、底線、連字號，且須以英數開頭")


def clean_href(value):
    href = str(value or "").strip()
    if not href.startswith(("http://", "https://")):
        raise SystemExit("href 必須是 http 或 https 網址")
    if any(char.isspace() for char in href):
        raise SystemExit("href 不可含空白")
    return href


def normalize(item):
    if not isinstance(item, dict):
        raise SystemExit("deals.json 含有不是物件的項目")
    expires = item.get("expires", None)
    if expires is not None:
        expires = str(expires).strip() or None
    deal = {
        "id": str(item.get("id") or "").strip(),
        "category": str(item.get("category") or "").strip(),
        "title": str(item.get("title") or "").strip(),
        "note": "" if item.get("note") is None else str(item.get("note")),
        "href": str(item.get("href") or "").strip(),
        "expires": expires,
        "added": str(item.get("added") or "").strip(),
    }
    for key, extra in item.items():
        if key not in deal:
            deal[key] = extra
    return deal


def order_deals(deals):
    indexed = list(enumerate(deals))

    def sort_key(pair):
        index, deal = pair
        try:
            category_index = CATEGORIES.index(deal.get("category"))
        except ValueError:
            category_index = len(CATEGORIES)
        return (category_index, index)

    indexed.sort(key=sort_key)
    return [deal for _, deal in indexed]


def load_deals(path=DATA_PATH):
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return []
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"deals.json 不是合法的 JSON：{exc}") from exc
    if not isinstance(data, list):
        raise SystemExit("deals.json 必須是陣列")
    return [normalize(item) for item in data]


def save_deals(deals, path=DATA_PATH):
    payload = []
    for deal in order_deals(deals):
        ordered = {key: deal.get(key) for key in KEYS}
        for key, value in deal.items():
            if key not in ordered:
                ordered[key] = value
        payload.append(ordered)
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def index_by_id(deals, deal_id):
    for index, deal in enumerate(deals):
        if deal.get("id") == deal_id:
            return index
    return None


def indexes_by_href(deals, href):
    return [index for index, deal in enumerate(deals) if deal.get("href") == href]


def make_id(title, href, deals):
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    slug = slug[:32] if slug else "deal"
    digest = hashlib.sha1(href.encode("utf-8")).hexdigest()[:8]
    candidate = f"{slug}-{digest}"
    taken = {deal.get("id") for deal in deals}
    number = 2
    while candidate in taken:
        candidate = f"{slug}-{digest}-{number}"
        number += 1
    return candidate


def apply_add(deals, *, deal_id, category, title, note, href, expires, now):
    """依 id 更新；沒有 id 時依唯一的 href 更新；否則新增。

    有帶 id 但找不到時一律新增，就算 href 已經被別筆使用。
    這樣同一篇報導可以同時掛兩筆（例如 7-11 與全家）。
    """
    if deal_id:
        deal_id = deal_id.strip()
        validate_id(deal_id)
    if category is not None:
        category = category.strip()
        if category not in CATEGORIES:
            names = "、".join(CATEGORIES)
            raise SystemExit(f"未知的類別：{category}。只能是：{names}")
    if title is not None:
        title = title.strip()
        if not title:
            raise SystemExit("title 不可為空白")
    if href is not None:
        href = clean_href(href)
    if note is not None:
        note = str(note)

    index = index_by_id(deals, deal_id) if deal_id else None
    if index is None and not deal_id:
        if not href:
            raise SystemExit("請提供 --id，或提供 --href")
        hits = indexes_by_href(deals, href)
        if len(hits) > 1:
            names = ", ".join(deals[hit]["id"] for hit in hits)
            raise SystemExit(f"這個網址對到多筆，請指定 --id：{names}")
        if len(hits) == 1:
            index = hits[0]

    if index is None:
        if not category or not title or not href:
            raise SystemExit("新增時 --category、--title、--href 都要有")
        new_id = deal_id or make_id(title, href, deals)
        deals.append(
            {
                "id": new_id,
                "category": category,
                "title": title,
                "note": "" if note is None else note,
                "href": href,
                "expires": None if expires is UNSET else expires,
                "added": format_added(now),
            }
        )
        return "added", new_id

    deal = deals[index]
    if category:
        deal["category"] = category
    if title:
        deal["title"] = title
    if note is not None:
        deal["note"] = note
    if href:
        deal["href"] = href
    if expires is not UNSET:
        deal["expires"] = expires
    return "updated", deal["id"]


def apply_remove(deals, *, deal_id, href):
    if bool(deal_id) == bool(href):
        raise SystemExit("remove 請只給 --id 或 --href 其中一個")
    if deal_id:
        deal_id = deal_id.strip()
        index = index_by_id(deals, deal_id)
        if index is None:
            raise SystemExit(f"找不到 id：{deal_id}")
        removed = deals.pop(index)
        return [removed["id"]]
    href = clean_href(href)
    hits = indexes_by_href(deals, href)
    if not hits:
        raise SystemExit("找不到這個網址")
    if len(hits) > 1:
        names = ", ".join(deals[hit]["id"] for hit in hits)
        raise SystemExit(f"這個網址對到多筆，請指定 --id：{names}")
    removed = deals.pop(hits[0])
    return [removed["id"]]


def apply_prune(deals, now):
    kept = []
    removed = []
    for deal in deals:
        try:
            expired = is_expired(deal.get("expires"), now)
        except ValueError:
            print(f"略過無法解析的期限：{deal.get('id')}", file=sys.stderr)
            expired = False
        if expired:
            removed.append(deal.get("id"))
        else:
            kept.append(deal)
    return kept, removed


def build_parser():
    parser = argparse.ArgumentParser(
        prog="deals.py",
        description="維護省錢情報 deals.json。不要手改 JSON。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="類別順序與名稱見 README.md。日期 YYYY-MM-DD 表示台北時間該日整天都還有效。",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="新增，或依 id／唯一 href 更新")
    add.add_argument("--id", help="穩定 id。已存在就更新；不存在就新增")
    add.add_argument("--category", choices=CATEGORIES, help="類別，必須是固定的七個之一")
    add.add_argument("--title", help="標題")
    add.add_argument("--note", default=None, help="說明。可含 [文字](https://...) 連結")
    add.add_argument("--href", help="優惠網址")
    add.add_argument(
        "--expires",
        default=UNSET,
        type=expires_arg,
        help="YYYY-MM-DD、ISO 時間（建議 +08:00），或 null。省略表示新增時沒有期限、更新時不改",
    )

    remove = sub.add_parser("remove", help="依 id 或唯一 href 刪除一筆")
    remove.add_argument("--id")
    remove.add_argument("--href")

    sub.add_parser("prune", help="刪除已過期的項目（以台北現在時間判斷）。期限不明的留下")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    now = taipei_now()
    deals = load_deals()

    if args.command == "add":
        action, deal_id = apply_add(
            deals,
            deal_id=args.id,
            category=args.category,
            title=args.title,
            note=args.note,
            href=args.href,
            expires=args.expires,
            now=now,
        )
        save_deals(deals)
        print(f"{'新增' if action == 'added' else '更新'} {deal_id}")
        current = next(deal for deal in deals if deal["id"] == deal_id)
        try:
            expired = is_expired(current.get("expires"), now)
        except ValueError:
            expired = False
        if expired:
            print("這筆已經過期：頁面不會顯示，prune 會刪除它")
        return 0

    if args.command == "remove":
        removed = apply_remove(deals, deal_id=args.id, href=args.href)
        save_deals(deals)
        for deal_id in removed:
            print(f"刪除 {deal_id}")
        return 0

    if args.command == "prune":
        kept, removed = apply_prune(deals, now)
        save_deals(kept)
        print(f"刪除 {len(removed)} 筆")
        for deal_id in removed:
            print(deal_id)
        return 0

    parser.error("未知的指令")
    return 2


if __name__ == "__main__":
    sys.exit(main())
