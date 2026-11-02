#!/usr/bin/env python3
"""Собирает статический сайт docs/ из Markdown-файлов репозитория.

Запуск:  python build.py
Требования: pip install -r requirements.txt
"""
import html
import os
import posixpath
import re
import shutil

import markdown

ROOT = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(ROOT, "docs")

ANALYSIS = "analysis"
RESULT = "result"

PAGES = [
    {
        "src": "artifacts/01a-analiz-sales.md",
        "group": ANALYSIS,
        "nav": "01. Продажи",
        "lead": "Воронка по месяцам, конверсии переходов, тренд первого и второго полугодия.",
    },
    {
        "src": "artifacts/02a-analiz-non-clients.md",
        "group": ANALYSIS,
        "nav": "02. Отказы",
        "lead": "16 анкет клиентов, которые не начали пользоваться продуктом: причины и крючки.",
    },
    {
        "src": "artifacts/03a-analiz-retention.md",
        "group": ANALYSIS,
        "nav": "03. Удержание",
        "lead": "Когортное удержание девяти зрелых когорт, отток к 12-му месяцу, провалы.",
    },
    {
        "src": "artifacts/04a-analiz-features.md",
        "group": ANALYSIS,
        "nav": "04. Функции",
        "lead": "Adoption ключевых функций: запуски в середине года, рост и обрывы.",
    },
    {
        "src": "artifacts/05a-analiz-user-flow.md",
        "group": ANALYSIS,
        "nav": "05. Сценарий",
        "lead": "Успешность шагов ключевого сценария с учётом SLA и сквозная конверсия.",
    },
    {
        "src": "artifacts/06a-analiz-support.md",
        "group": ANALYSIS,
        "nav": "06. Поддержка",
        "lead": "30 обращений: темы, роли, типы учреждений, повторяющиеся проблемы.",
    },
    {
        "src": "artifacts/07a-analiz-loyal-feedback.md",
        "group": ANALYSIS,
        "nav": "07. Лояльные",
        "lead": "16 интервью: что ценно, почему остаются, что пробовали и забросили.",
    },
    {
        "src": "analysis/kachestvennaya-klasterizaciya.md",
        "group": ANALYSIS,
        "nav": "Кластеризация",
        "lead": "Темы из трёх качественных источников, частоты, роли и закономерности.",
    },
    {
        "src": "analysis/08a-svyazka-metrik.md",
        "group": ANALYSIS,
        "nav": "Связка метрик",
        "lead": "Каждая проблема связана с метрикой и количественным подтверждением.",
    },
    {
        "src": "artifacts/spisok-idej.md",
        "group": RESULT,
        "nav": "Идеи",
        "lead": "15 сырых идей, отсев по данным, приоритетные и отклонённые.",
    },
    {
        "src": "artifacts/prioritizirovannye-iniciativy.md",
        "group": RESULT,
        "nav": "Приоритизация",
        "lead": "Рейтинг семи инициатив по ICE, волны дорожной карты, чувствительность.",
    },
    {
        "src": "artifacts/ocenka-biznes-effekta.md",
        "group": RESULT,
        "nav": "Бизнес-эффект",
        "lead": "Монетизационные события, три сценария, разрыв цели и исследовательский трек.",
    },
]

GROUP_TITLES = {
    ANALYSIS: "Анализ данных",
    RESULT: "Результат: инициативы и эффект",
}

DATA_FILES = [
    ("sales.csv", "Воронка по месяцам 2025: вход → квалификация → демонстрация → триал → оплата → активные."),
    ("retention.csv", "Когортное удержание платных клиентов по месяцам жизни (1–12)."),
    ("features.csv", "Adoption ключевых функций по месяцам."),
    ("user_flow.csv", "Успешность шагов ключевого сценария с учётом SLA."),
    ("support.txt", "30 обращений в поддержку: клиент, роль, учреждение, проблема."),
    ("non_clients.txt", "16 анкет клиентов, не начавших пользоваться продуктом."),
    ("loyal_feedback.txt", "16 интервью лояльных клиентов."),
    ("case-description.md", "Условие кейса: цель, вводные данные, ограничения."),
]

KEY_FACTS = [
    ("244", "первых оплат за 2025 год"),
    ("1 458", "продлений к 12-му месяцу"),
    ("1 702", "монетизационных события в базе"),
    ("+340", "событий — цель +20%"),
    ("7", "приоритезированных инициатив"),
    ("49,0%", "цели закрывает базовый сценарий"),
]


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def page_title(md_text, fallback):
    for line in md_text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def md_to_html(md_text):
    return markdown.markdown(
        md_text,
        extensions=["tables", "sane_lists", "toc", "fenced_code"],
        output_format="html5",
    )


def wrap_tables(fragment):
    fragment = fragment.replace("<table>", '<div class="table-wrap"><table>')
    fragment = fragment.replace("</table>", "</table></div>")
    return fragment


def rewrite_md_links(fragment):
    return re.sub(r'href="([^"]+)\.md(#[^"]*)?"', r'href="\1.html\2"', fragment)


def prefix_for(out_rel):
    depth = out_rel.count("/")
    return "../" * depth


def breadcrumbs(prefix, group, nav):
    return (
        '<nav class="crumbs" aria-label="Хлебные крошки">'
        f'<a href="{prefix}index.html">Главная</a>'
        f'<span>/</span><a href="{prefix}index.html#{group}">{GROUP_TITLES[group]}</a>'
        f'<span>/</span><span>{html.escape(nav)}</span>'
        "</nav>"
    )


def pager(prefix, index):
    parts = ['<nav class="pager" aria-label="Навигация по страницам">']
    if index > 0:
        prev = PAGES[index - 1]
        parts.append(
            f'<a class="pager-prev" href="{prefix}{prev["@out"]}">'
            f'<span>Назад</span>{html.escape(prev["nav"])}</a>'
        )
    else:
        parts.append('<span class="pager-empty"></span>')
    if index < len(PAGES) - 1:
        nxt = PAGES[index + 1]
        parts.append(
            f'<a class="pager-next" href="{prefix}{nxt["@out"]}">'
            f'<span>Далее</span>{html.escape(nxt["nav"])}</a>'
        )
    parts.append("</nav>")
    return "".join(parts)


def layout(title, body, prefix, group=None, nav=None, description=""):
    nav_links = (
        f'<a href="{prefix}index.html#analysis">Анализ</a>'
        f'<a href="{prefix}index.html#result">Результат</a>'
        f'<a href="{prefix}index.html#data">Данные</a>'
    )
    crumbs = breadcrumbs(prefix, group, nav) if group else ""
    return f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} · Карта проекта</title>
<meta name="description" content="{html.escape(description)}">
<link rel="stylesheet" href="{prefix}assets/style.css">
</head>
<body>
<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="{prefix}index.html">
      <span class="brand-mark"></span>
      <span class="brand-text">Карта проекта<small>Закупки · медицинские учреждения</small></span>
    </a>
    <nav class="top-nav" aria-label="Разделы">{nav_links}</nav>
  </div>
</header>
<main class="wrap">
{crumbs}
<article class="prose">
{body}
</article>
</main>
<footer class="site-footer">
  <div class="wrap">
    <p>Учебный кейс 4 · анализ продукта «Закупки» за 2025 год · данные обезличены.</p>
    <p>Собрано статически из Markdown: <code>python build.py</code>.</p>
  </div>
</footer>
</body>
</html>
"""


def build_pages():
    for i, page in enumerate(PAGES):
        src = os.path.join(ROOT, page["src"])
        out_rel = page["src"].rsplit(".", 1)[0] + ".html"
        page["@out"] = out_rel

    for i, page in enumerate(PAGES):
        src = os.path.join(ROOT, page["src"])
        text = read(src)
        title = page_title(text, page["nav"])
        body = wrap_tables(rewrite_md_links(md_to_html(text)))
        prefix = prefix_for(page["@out"])
        doc = layout(
            title,
            body,
            prefix,
            group=page["group"],
            nav=page["nav"],
            description=page["lead"],
        )
        doc = doc.replace("</article>", pager(prefix, i) + "</article>")
        out_path = os.path.join(DOCS, page["@out"])
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(doc)


def card(page):
    return f"""<a class="card" href="{page["@out"]}">
  <span class="card-kicker">{html.escape(page["nav"])}</span>
  <span class="card-title">{html.escape(page["@title"])}</span>
  <span class="card-lead">{html.escape(page["lead"])}</span>
</a>"""


def build_index():
    for page in PAGES:
        page["@title"] = page_title(read(os.path.join(ROOT, page["src"])), page["nav"])

    groups = {ANALYSIS: [], RESULT: []}
    for page in PAGES:
        groups[page["group"]].append(page)

    facts = "".join(
        f'<div class="fact"><b>{html.escape(value)}</b><span>{html.escape(label)}</span></div>'
        for value, label in KEY_FACTS
    )
    analysis_cards = "".join(card(p) for p in groups[ANALYSIS])
    result_cards = "".join(card(p) for p in groups[RESULT])

    data_rows = "".join(
        f'<tr><td><a href="data/{name}">{name}</a></td><td>{html.escape(desc)}</td></tr>'
        for name, desc in DATA_FILES
    )

    body = f"""
<section class="hero">
  <p class="eyebrow">Кейс 4 · продуктовый анализ 2025</p>
  <h1>Карта проекта: развитие «Закупок» для медицинских учреждений</h1>
  <p class="hero-lead">Цель — увеличить потенциально монетизируемую ценность продукта на 20%.
  Здесь собраны исходные данные, аналитика по каждому источнику, кластеризация обратной связи,
  приоритизированные инициативы и оценка бизнес-эффекта.</p>
  <div class="chips">
    <span class="chip">44-ФЗ и 223-ФЗ</span>
    <span class="chip">7 источников данных</span>
    <span class="chip">12 артефактов</span>
    <span class="chip">метод ICE</span>
  </div>
</section>

<section class="facts" aria-label="Ключевые цифры">{facts}</section>

<section id="analysis" class="section">
  <div class="section-head">
    <h2>Анализ данных</h2>
    <p>От сырых файлов к подтверждённым потерям: сначала каждый источник отдельно,
    затем кластеризация качественной обратной связи и связка проблем с метриками.</p>
  </div>
  <div class="cards">{analysis_cards}</div>
</section>

<section id="result" class="section">
  <div class="section-head">
    <h2>Результат: инициативы и эффект</h2>
    <p>Сырые идеи, отсев по данным, рейтинг ICE, волны дорожной карты и расчёт
    влияния на монетизацию.</p>
  </div>
  <div class="cards">{result_cards}</div>
</section>

<section class="section pipeline">
  <h2>Как читать</h2>
  <ol>
    <li><b>Данные</b> — сырые выгрузки продаж, удержания, функций, сценария и обратной связи.</li>
    <li><b>Анализ</b> — по каждому файлу: факты, закономерности, отклонения.</li>
    <li><b>Кластеризация и связка</b> — темы обратной связи, подтверждённые цифрами.</li>
    <li><b>Инициативы</b> — 15 идей, отсев, 7 приоритетных по ICE.</li>
    <li><b>Эффект</b> — монетизационные события, сценарии и разрыв до цели.</li>
  </ol>
</section>

<section id="data" class="section">
  <div class="section-head">
    <h2>Исходные данные</h2>
    <p>Файлы кейса в исходном виде. Цены и выручка в данных отсутствуют:
    единица измерения — монетизационное событие.</p>
  </div>
  <div class="table-wrap">
    <table>
      <thead><tr><th>Файл</th><th>Содержание</th></tr></thead>
      <tbody>{data_rows}</tbody>
    </table>
  </div>
</section>

<section class="section note">
  <h2>Ограничения</h2>
  <p>В файлах нет цен и маржи, поэтому эффект выражен в событиях и процентных пунктах,
  а не в рублях. В <code>retention.csv</code> нет причин оттока, в <code>features.csv</code> —
  разреза по тарифам: связи «причина → отток» и «тариф → использование» остаются гипотезами.
  Оценки трудоёмкости — допущения.</p>
</section>
"""

    doc = f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Карта проекта · Закупки для медицинских учреждений</title>
<meta name="description" content="Анализ продукта «Закупки» за 2025 год: данные, аналитика, приоритизированные инициативы и оценка бизнес-эффекта для цели +20%.">
<link rel="stylesheet" href="assets/style.css">
</head>
<body class="home">
<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="index.html">
      <span class="brand-mark"></span>
      <span class="brand-text">Карта проекта<small>Закупки · медицинские учреждения</small></span>
    </a>
    <nav class="top-nav" aria-label="Разделы">
      <a href="#analysis">Анализ</a>
      <a href="#result">Результат</a>
      <a href="#data">Данные</a>
    </nav>
  </div>
</header>
<main class="wrap">
{body}
</main>
<footer class="site-footer">
  <div class="wrap">
    <p>Учебный кейс 4 · анализ продукта «Закупки» за 2025 год · данные обезличены.</p>
    <p>Собрано статически из Markdown: <code>python build.py</code>.</p>
  </div>
</footer>
</body>
</html>
"""
    with open(os.path.join(DOCS, "index.html"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(doc)


def copy_assets():
    shutil.copytree(
        os.path.join(ROOT, "assets"),
        os.path.join(DOCS, "assets"),
    )
    os.makedirs(os.path.join(DOCS, "data"), exist_ok=True)
    for name, _ in DATA_FILES:
        shutil.copyfile(
            os.path.join(ROOT, "data", name),
            os.path.join(DOCS, "data", name),
        )
    open(os.path.join(DOCS, ".nojekyll"), "w", encoding="utf-8").close()


def main():
    if os.path.isdir(DOCS):
        shutil.rmtree(DOCS)
    os.makedirs(DOCS)
    build_pages()
    build_index()
    copy_assets()
    print("docs/ собраны: %d страниц" % len(PAGES))


if __name__ == "__main__":
    main()
