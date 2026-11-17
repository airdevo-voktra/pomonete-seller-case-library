from argparse import ArgumentParser
from collections import Counter
from dataclasses import dataclass
from html import escape
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring

from models import MODELS
from scenarios import SUPPLEMENTS


ROOT = Path(__file__).resolve().parent
CATEGORIES = {
    "01": ("Юнит-экономика и цены", "https://yandex.ru/support/marketplace/ru/introduction/rates/placement"),
    "02": ("Окупаемость складских изменений", "https://yandex.ru/support/marketplace/ru/analytics/key-metrics"),
    "03": ("Ошибки сборки и приёмки", "https://yandex.ru/support/marketplace/ru/quality/score/"),
    "04": ("Деньги и график платежей", "https://yandex.ru/support/marketplace/ru/accounting/financial-summary"),
    "05": ("Запасы и закупки", "https://yandex.ru/support/marketplace/ru/storage/shipment/application"),
    "06": ("Комплекты и общий запас", "https://yandex.ru/support/marketplace/ru/assortment/create/main-fields/general"),
    "07": ("Контроль выгрузок и расходов", "https://yandex.ru/support/marketplace/ru/accounting/financial-summary"),
    "08": ("Расходы отгрузки и перевозки", "https://yandex.ru/support/marketplace/ru/tutorials/delivery"),
    "09": ("Осмотр и экономика возвратов", "https://yandex.ru/support/marketplace/ru/orders/returns/realization"),
    "10": ("Тесты карточек и отклик покупателей", "https://yandex.ru/support/marketplace/ru/analytics/shows-sales"),
}

CSS = """
:root{color-scheme:light;--paper:#faf8f3;--white:#fffefa;--ink:#17231d;--muted:#43564c;--green:#285e4c;--line:#d8e0d8;--soft:#edf3ee;font-family:"Source Sans 3",system-ui,sans-serif;background:var(--paper);color:var(--ink)}
*{box-sizing:border-box}body{margin:0}a{color:var(--green);text-underline-offset:.18em}a:focus-visible{outline:3px solid var(--green);outline-offset:3px}
.top,.foot{width:min(100% - 36px,1100px);margin:auto;padding:18px 0;display:flex;justify-content:space-between;align-items:center;gap:16px;border-bottom:1px solid var(--line);font-size:.95rem}
.brand{font-weight:800;letter-spacing:-.025em;text-decoration:none}.top span,.foot{color:var(--muted)}.foot{border-top:1px solid var(--line);border-bottom:0}
.content{width:min(100% - 36px,740px);margin:40px auto 60px}.directory{width:min(100% - 36px,1040px);margin:52px auto}
h1,h2{font-family:"Instrument Serif",Georgia,serif;font-weight:600;line-height:1.1;letter-spacing:-.026em;margin-block:0 .45em}
h1{font-size:clamp(2.25rem,5vw,4rem)}h2{font-size:clamp(1.60rem,3vw,2.10rem);margin-top:1.15em}
p{line-height:1.62;margin:0 0 1.15em}.lead{font-size:1.2rem}.cred{font-size:.95rem;color:var(--muted)}
figure{margin:24px 0;text-align:left}figure img{display:block;width:100%;height:auto;border:1px solid var(--line);border-radius:10px;background:var(--white)}
figcaption{font-size:.88rem;color:var(--muted);margin-top:8px}.method{overflow-x:auto;border:1px solid var(--line);border-radius:10px}
table{width:100%;border-collapse:collapse;line-height:1.35;background:var(--white)}th,td{text-align:left;padding:11px 14px;border-bottom:1px solid var(--line);vertical-align:top}thead th{background:var(--soft)}tbody tr:last-child td,tbody tr:last-child th{border-bottom:0}td:not(:first-child){font-variant-numeric:tabular-nums}
.browse{border-top:1px solid var(--line);margin-top:35px;padding-top:14px}.browse ul,.links{padding-left:22px;line-height:1.5}.browse li,.links li{margin:.42em 0}
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}.group{background:var(--white);border:1px solid var(--line);border-radius:12px;padding:9px 19px 16px}.group h2{font-size:1.5rem}.group li{padding-right:8px}
.sources{text-wrap:pretty}.illustration{background:var(--white);padding:24px;color:var(--ink)}.illustration small{color:var(--muted)}.illustration h1{font-size:28px;margin-top:8px}.illustration th,.illustration td{font-size:16px}
@media(max-width:640px){.grid{grid-template-columns:1fr}.top{align-items:flex-start}.top span{font-size:.83rem;text-align:right}.content,.directory{margin-top:28px}th,td{padding:8px;font-size:.92rem}}
""".strip()


@dataclass
class Article:
    category: str
    slug: str
    title: str
    opener: str
    audit: str
    decision: str
    model: object
    scenarios: tuple


def read_articles():
    for source in sorted((ROOT / "cases").glob("*.tsv")):
        category = source.name[:2]
        for line in source.read_text().splitlines():
            slug, title, *fields = line.split("|")
            opener, audit, decision = fields[-3:]
            raw = fields[:-3]
            if category == "01":
                detail = raw.pop(5)
            else:
                detail = raw.pop()
            values = tuple(map(int, raw))
            model = MODELS[category](values, detail)
            scenarios = SUPPLEMENTS[category](values, detail)
            yield Article(category, slug, title, opener, audit, decision, model, scenarios)


def make_table(model):
    header = "".join(f'<th scope="col">{escape(label)}</th>' for label in model.columns)
    rows = []
    for label, first, second in model.rows:
        rows.append(f'<tr><th scope="row">{escape(label)}</th><td>{escape(str(first))}</td><td>{escape(str(second))}</td></tr>')
    return f"<table><thead><tr>{header}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def shell(title, description, body, canonical=""):
    canon = f'<link rel="canonical" href="{escape(canonical)}">' if canonical else ""
    return f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(description)}">
{canon}
<link rel="stylesheet" href="/styles.css">
</head>
<body>
<header class="top"><a class="brand" href="/">Pomonete</a><span>Аналитика для селлеров Яндекс Маркета</span></header>
{body}
<footer class="foot"><a href="/">Все разборы</a><span>Редакция Pomonete</span></footer>
</body>
</html>
"""


def link_list(entries):
    return '<ul class="links">' + "".join(
        f'<li><a href="/{article.slug}.html">{escape(article.title)}</a></li>' for article in entries
    ) + '</ul>'


def closing_checks(article):
    chosen = article.title.rstrip("?")
    return (
        f"Соберите для задачи «{chosen}» одну проверяемую рабочую строку. Рядом с исходными суммами запишите дату первой выгрузки, статус завершения и событие, которое переводит оценку в факт. Если по документу видно лишь итог, приложите небольшую выборку операций с подтверждённой причиной. Такой способ помогает вернуться к решению после смены периода или после нового начисления и заметить, где на исход повлияла именно гипотеза статьи.",
        f"У владельца и исполнителя должны совпадать единица расчёта и момент проверки. Прочитайте вывод по «{article.model.headline.lower()}» вслух рядом с данными. Если в первом сценарии речь о выполненной работе, а во втором только об обещанной, исправьте основу сравнения до расчёта. В следующей версии оставьте первоначальные значения рядом с фактом. Тогда расхождение объяснит, какое действие меняет экономику и насколько надёжно считать эффект повторяемым."
    )


def render_article(article, same_category, host, images):
    title, opener, audit, decision, model = article.title, article.opener, article.audit, article.decision, article.model
    checks = closing_checks(article)
    core = [opener, model.arithmetic, model.boundary, model.stress, model.scope, audit, model.evidence,
            decision, model.followup, *article.scenarios, *checks]
    actual = sum(not char.isspace() for char in "".join(core))
    table = make_table(model)
    article_title, source = CATEGORIES[article.category]
    nearby = [other for other in same_category if other.slug != article.slug]
    offset = sum(map(ord, article.slug)) % len(nearby)
    related = (nearby + nearby)[offset:offset + 2]
    if images:
        exhibit = (f'<figure><img src="/figures/{article.slug}.png" width="960" height="{images[article.slug]}" '
                   f'alt="{escape(model.headline)}"><figcaption>Таблица расчёта на условных данных.</figcaption></figure>')
    else:
        exhibit = ""
    desc = opener.split(". ", 1)[0].strip().rstrip(".") + "."
    body = f"""<main class="content">
<article>
<header>
<p class="cred"><a href="/#{article.category}">{escape(article_title)}</a></p>
<h1>{escape(title)}</h1>
<p class="cred">Разбор команды Pomonete. Данные учебного примера условные.</p>
<p class="lead">{escape(opener)}</p>
</header>
<h2>{escape(model.headline)}</h2>
<p>{escape(model.arithmetic)}</p>
<div class="method">{table}</div>
{exhibit}
<h2>Где меняется решение</h2>
<p>{escape(model.boundary)}</p>
<p>{escape(model.stress)}</p>
<h2>Что проверить в данных своего магазина</h2>
<p>{escape(model.scope)}</p>
<p>{escape(audit)}</p>
<p>{escape(model.evidence)}</p>
<h2>Сценарии для рабочего расчёта</h2>
<p>{escape(article.scenarios[0])}</p>
<p>{escape(article.scenarios[1])}</p>
<p>{escape(article.scenarios[2])}</p>
<h2>Как подтвердить результат</h2>
<p>{escape(decision)}</p>
<p>{escape(model.followup)}</p>
<p>{escape(checks[0])}</p>
<p>{escape(checks[1])}</p>
<p class="sources"><a href="{source}">Справка Яндекс Маркета</a> · <a href="https://pomonete.ru/">Финансовая аналитика Pomonete</a></p>
</article>
<aside class="browse" aria-label="Похожие разборы"><h2>По теме</h2>{link_list(related)}</aside>
</main>"""
    return shell(title, desc, body, f"{host}/{article.slug}.html" if host else ""), actual


def render_catalog(entries, host, title):
    categories = {}
    for entry in entries:
        categories.setdefault(entry.category, []).append(entry)
    groups = "".join(
        f'<section class="group" id="{category}"><h2>{escape(CATEGORIES[category][0])}</h2>{link_list(articles)}</section>'
        for category, articles in categories.items()
    )
    lead = "Практические расчёты и проверки для продавцов Яндекс Маркета. Каждый разбор отвечает на один вопрос и показывает, какие данные подставить из своего магазина."
    body = f'<main class="directory"><h1>{escape(title)}</h1><p class="lead">{lead}</p><div class="grid">{groups}</div></main>'
    return shell(f"{title} | Pomonete", lead, body, f"{host}/" if host else "")


def screenshot_figures(entries, output):
    from playwright.sync_api import sync_playwright

    folder = output / "figures"
    folder.mkdir(exist_ok=True)
    heights = {}
    with sync_playwright() as playwright:
        browser = playwright.webkit.launch(headless=True)
        page = browser.new_page(viewport={"width":960,"height":700})
        for article in entries:
            model = article.model
            page.set_content(
                f'<meta charset="utf-8"><style>{CSS}</style>'
                f'<main class="illustration"><small>Pomonete · Условный пример</small>'
                f'<h1>{escape(model.headline)}</h1><div class="method">{make_table(model)}</div></main>'
            )
            exhibit = page.locator(".illustration")
            assert page.locator("table").evaluate("(el) => el.scrollWidth <= el.parentElement.clientWidth + 2")
            path = folder / f"{article.slug}.png"
            exhibit.screenshot(path=str(path),animations="disabled")
            heights[article.slug] = round(exhibit.bounding_box()["height"])
        browser.close()
    return heights


def sitemap(output, selected, host):
    addresses = [host + "/"] + [f"{host}/{article.slug}.html" for article in selected]
    urls = Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for address in addresses:
        SubElement(SubElement(urls, "url"), "loc").text = address
    (output / "sitemap.xml").write_bytes(tostring(urls, encoding="utf-8", xml_declaration=True))
    (output / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {host}/sitemap.xml\n")


def main():
    parser = ArgumentParser()
    parser.add_argument("--categories", default=",".join(CATEGORIES))
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--host", default="")
    parser.add_argument("--title", default="Считаем деньги на Яндекс Маркете")
    parser.add_argument("--images", action="store_true")
    args = parser.parse_args()
    selected = [article for article in read_articles() if article.category in args.categories.split(",")]
    assert selected and len({a.slug for a in selected}) == len(selected)
    output = args.out
    output.mkdir(exist_ok=True, parents=True)
    host = args.host.rstrip("/")
    heights = screenshot_figures(selected, output) if args.images else {}
    output.joinpath("styles.css").write_text(CSS)
    output.joinpath("index.html").write_text(render_catalog(selected, host, args.title))
    count = {}
    for article in selected:
        related = [item for item in selected if item.category == article.category]
        html, length = render_article(article, related, host, heights)
        assert "—" not in html
        assert length >= 5000, (article.slug, length)
        output.joinpath(f"{article.slug}.html").write_text(html)
        count[article.slug] = length
    if host:
        sitemap(output, selected, host)
    else:
        output.joinpath("robots.txt").write_text("User-agent: *\nAllow: /\n")
    print(f"{len(count)} статей, {min(count.values())}–{max(count.values())} знаков без пробелов")
    print(Counter(a.category for a in selected))


if __name__ == "__main__":
    main()
