#!/usr/bin/env python3
"""Render verified-listing sections in listings.html and the topic hub pages from canonical JSON data."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "verified-listings.json"
HTML_PATH = ROOT / "listings.html"
START = "<!-- VERIFIED_LISTINGS_GENERATED_START -->"
END = "<!-- VERIFIED_LISTINGS_GENERATED_END -->"

HUBS = [
    {
        "path": ROOT / "learning.html",
        "topic": "learning",
        "start": "<!-- TOPIC_LEARNING_GENERATED_START -->",
        "end": "<!-- TOPIC_LEARNING_GENERATED_END -->",
        "heading": "大阪で確認できた<br>学び・講座の情報。",
        "intro": "50PLUSが公式情報で確認できた、大阪の学び・講座に関する情報です。日時・対象・料金・申込方法は、必ずリンク先の公式ページで最新情報を確認してください。",
    },
    {
        "path": ROOT / "volunteering.html",
        "topic": "volunteering",
        "start": "<!-- TOPIC_VOLUNTEERING_GENERATED_START -->",
        "end": "<!-- TOPIC_VOLUNTEERING_GENERATED_END -->",
        "heading": "大阪で確認できた<br>ボランティア・市民活動の情報。",
        "intro": "50PLUSが公式情報で確認できた、大阪のボランティア・市民活動に関する情報です。活動内容・参加条件・申込方法は、必ずリンク先の公式ページで最新情報を確認してください。",
    },
    {
        "path": ROOT / "sports.html",
        "topic": "sports",
        "start": "<!-- TOPIC_SPORTS_GENERATED_START -->",
        "end": "<!-- TOPIC_SPORTS_GENERATED_END -->",
        "heading": "大阪で確認できた<br>スポーツの情報。",
        "intro": "50PLUSが公式情報で確認できた、大阪のスポーツに関する情報です。開催日・参加条件・申込方法は、必ずリンク先の公式ページで最新情報を確認してください。",
    },
    {
        "path": ROOT / "culture-library.html",
        "topic": "culture",
        "start": "<!-- TOPIC_CULTURE_GENERATED_START -->",
        "end": "<!-- TOPIC_CULTURE_GENERATED_END -->",
        "heading": "大阪で確認できた<br>文化・図書館の情報。",
        "intro": "50PLUSが公式情報で確認できた、大阪の文化・図書館に関する情報です。日時・対象・料金・申込方法は、必ずリンク先の公式ページで最新情報を確認してください。",
    },
]

VALID_TOPICS = {hub["topic"] for hub in HUBS}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def ja_date(value: str) -> str:
    parsed = date.fromisoformat(value)
    return f"{parsed.year}年{parsed.month}月{parsed.day}日"


def listing_attributes(item: dict) -> str:
    return (
        'data-listing-card '
        f'data-kind="{esc(item.get("kind", ""))}" '
        f'data-category="{esc(item.get("category", ""))}"'
    )


def source_buttons(item: dict, *, primary: bool) -> str:
    urls = item.get("source_urls", [])
    css = "button button-primary" if primary else "button button-ghost"
    links = []
    for index, url in enumerate(urls, start=1):
        if len(urls) == 1:
            label = "公式情報を確認する" if primary else "公式サイトを見る"
        else:
            label = f"公式情報{index}を確認する"
        links.append(
            f'<a class="{css}" href="{esc(url)}" target="_blank" rel="noopener">{label}</a>'
        )
    return '<div class="hero-actions">' + "".join(links) + "</div>"


def render_resource(item: dict, number: int) -> str:
    details = []
    if item.get("area"):
        details.append(f'<p><strong>エリア：</strong>{esc(item["area"])}</p>')
    if item.get("category"):
        details.append(f'<p><strong>カテゴリー：</strong>{esc(item["category"])}</p>')

    return (
        f'    <article class="card reveal" {listing_attributes(item)}><span class="card-number">{number:02d}</span>'
        f'<h3>{esc(item["name"])}</h3><p>{esc(item["summary"])}</p>'
        + "".join(details)
        + source_buttons(item, primary=False)
        + "</article>"
    )


def render_event(item: dict, number: int) -> str:
    details = []
    mapping = (
        ("venue", "会場"),
        ("schedule", "日時"),
        ("eligibility", "対象"),
        ("capacity", "定員"),
        ("fee", "費用"),
        ("registration_period", "申込期間"),
    )
    for key, label in mapping:
        if item.get(key):
            details.append(f'<p><strong>{label}：</strong>{esc(item[key])}</p>')

    note = ""
    if item.get("verification_note"):
        note = (
            '<div class="notice"><strong>公式情報を再確認してください。</strong><br>'
            + esc(item["verification_note"])
            + "</div>"
        )

    return (
        f'    <article class="card reveal" style="color:var(--ink)" {listing_attributes(item)}><span class="card-number">{number:02d}</span>'
        f'<h3>{esc(item["name"])}</h3><p>{esc(item["summary"])}</p>'
        + "".join(details)
        + note
        + source_buttons(item, primary=True)
        + "</article>"
    )


def render_block(data: dict) -> str:
    items = data["items"]
    resources = [item for item in items if item.get("kind") == "resource"]
    events = [item for item in items if item.get("kind") == "event"]
    verified_at = ja_date(data["verified_at"])

    number = 1
    resource_cards = []
    for item in resources:
        resource_cards.append(render_resource(item, number))
        number += 1

    event_cards = []
    for item in events:
        event_cards.append(render_event(item, number))
        number += 1

    parts = [
        f'  <section class="section-tight listings-tools" data-listing-filters aria-labelledby="listing-filter-title"><div class="container"><div class="listing-filter-panel"><div class="listing-filter-copy"><p class="eyebrow">Find verified activities</p><h2 id="listing-filter-title">確認済み情報を絞り込む。</h2><p>名前、エリア、カテゴリー、会場などをキーワードで検索できます。</p></div><div class="listing-filter-controls"><label class="listing-search-label" for="listing-search">キーワード検索</label><input class="listing-search-input" id="listing-search" type="search" placeholder="例：梅田、語学、ボランティア" autocomplete="off" data-listing-search><div class="listing-kind-filter" role="group" aria-label="情報の種類"><button class="listing-filter-button is-active" type="button" data-listing-kind="all" aria-pressed="true">すべて</button><button class="listing-filter-button" type="button" data-listing-kind="resource" aria-pressed="false">継続情報</button><button class="listing-filter-button" type="button" data-listing-kind="event" aria-pressed="false">開催イベント</button></div><p class="listing-result-count" aria-live="polite" data-listing-count>{len(items)}件を表示中</p><p class="listing-empty" hidden data-listing-empty>条件に合う確認済み情報はありません。検索語や種類を変えてください。</p></div></div></div></section>',
        f'  <section class="section-tight"><div class="narrow"><div class="notice"><strong>最終確認日：{verified_at}</strong><br>参加者の男女比、年齢層、雰囲気、人気度など、公式に確認できない情報は掲載していません。イベント情報は変更・中止の可能性があるため、申込前に必ず公式ページを確認してください。</div></div></section>',
    ]

    if resource_cards:
        parts.append(
            '  <section class="section" data-listing-section="resource"><div class="container"><div class="section-heading reveal"><div><p class="eyebrow">Ongoing resources</p><h2>まず相談・検索から<br>始められる場所。</h2></div><p>単発イベントだけでなく、継続的に活動を探せる公式の情報窓口も掲載します。</p></div><div class="card-grid">\n'
            + "\n".join(resource_cards)
            + "\n  </div></div></section>"
        )

    if event_cards:
        parts.append(
            f'  <section class="section section-dark" data-listing-section="event"><div class="container"><div class="section-heading reveal"><div><p class="eyebrow">Upcoming verified events</p><h2>開催予定を確認できた<br>学び・ものづくり。</h2></div><p>50PLUSが{verified_at}に公式情報で確認した内容です。</p></div><div class="card-grid">\n'
            + "\n".join(event_cards)
            + "\n  </div></div></section>"
        )

    return "\n\n".join(parts)


def render_topic_block(data: dict, topic: str, heading: str, intro: str) -> str:
    items = [item for item in data["items"] if topic in item.get("topics", [])]
    resources = [item for item in items if item.get("kind") == "resource"]
    events = [item for item in items if item.get("kind") == "event"]
    verified_at = ja_date(data["verified_at"])

    number = 1
    cards = []
    for item in resources:
        cards.append(render_resource(item, number))
        number += 1
    for item in events:
        cards.append(render_event(item, number))
        number += 1

    parts = [
        f'  <section class="section-tight"><div class="narrow"><div class="notice"><strong>最終確認日：{verified_at}</strong><br>参加者の男女比、年齢層、雰囲気、人気度など、公式に確認できない情報は掲載していません。イベント情報は変更・中止の可能性があるため、申込前に必ず公式ページで最新情報を確認してください。</div></div></section>',
    ]

    if cards:
        parts.append(
            f'  <section class="section" data-listing-section="topic"><div class="container"><div class="section-heading reveal"><div><p class="eyebrow">Verified in Osaka</p><h2>{heading}</h2></div><p>{intro}</p></div><div class="card-grid">\n'
            + "\n".join(cards)
            + "\n  </div></div></section>"
        )
    else:
        parts.append(
            '  <section class="section-tight"><div class="narrow"><div class="notice"><strong>現在、確認済みの掲載情報はありません。</strong><br>公式情報が確認でき次第、随時追加します。</div></div></section>'
        )

    return "\n\n".join(parts)


def substitute(current: str, start: str, end: str, block: str, *, label: str) -> str:
    if start not in current or end not in current:
        raise ValueError(f"Generated-listing markers are missing from {label}")
    generated = f"{start}\n{block}\n  {end}"
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
    return pattern.sub(generated, current, count=1)


def expected_html(current: str, data: dict) -> str:
    return substitute(current, START, END, render_block(data), label="listings.html")


def expected_hub_html(current: str, data: dict, hub: dict) -> str:
    block = render_topic_block(data, hub["topic"], hub["heading"], hub["intro"])
    return substitute(current, hub["start"], hub["end"], block, label=hub["path"].name)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail if generated HTML is not in sync with JSON")
    args = parser.parse_args()

    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))

    targets = [(HTML_PATH, lambda current: expected_html(current, data))]
    for hub in HUBS:
        targets.append((hub["path"], lambda current, hub=hub: expected_hub_html(current, data, hub)))

    in_sync = True
    for path, expected_fn in targets:
        current = path.read_text(encoding="utf-8")
        try:
            expected = expected_fn(current)
        except (KeyError, ValueError) as exc:
            print(f"render error: {exc}", file=sys.stderr)
            return 1

        if args.check:
            if current != expected:
                print(f"{path.name} is out of sync with data/verified-listings.json", file=sys.stderr)
                in_sync = False
            continue

        if current == expected:
            print(f"{path.name} is already up to date.")
        else:
            path.write_text(expected, encoding="utf-8")
            print(f"Updated {path.name} from data/verified-listings.json.")

    if args.check:
        if not in_sync:
            print("Run: python3 scripts/render_listings.py", file=sys.stderr)
            return 1
        print("Verified listings HTML is in sync with canonical JSON.")
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
