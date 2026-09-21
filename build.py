"""
Gera a landing page a partir de _src/.

  _src/layout.html        -> estrutura base (head, header, footer)
  _src/partials/*.html    -> blocos reutilizáveis: {{include:nome}}
  _src/pages/*.html       -> conteúdo de cada página (com metadados no topo)
  _src/icons.py           -> ícones SVG: {{icon:nome}} ou {{icon:nome:classe-extra}}
  _src/google-reviews.json -> avaliações do Google: {{google-reviews:N}} e {{google-badge}}
  _src/pacientes.json     -> galeria de fotos de pacientes: {{patient-gallery}}

Uso:  python build.py
"""
import html
import io
import json
import os
import re
import sys
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "_src")

sys.path.insert(0, SRC)
from icons import ICONS  # noqa: E402


def read(path):
    with io.open(path, encoding="utf-8") as f:
        return f.read()


def icon(match):
    name, _, extra = match.group(1).partition(":")
    return svg_icon(name, extra)


def svg_icon(name, extra=""):
    if name not in ICONS:
        raise KeyError("Ícone não encontrado: " + name)
    cls = ("icon " + extra).strip()
    fill = "currentColor" if name in ("whatsapp", "play", "quote") else "none"
    stroke = "none" if fill == "currentColor" else "currentColor"
    return (
        f'<svg class="{cls}" viewBox="0 0 24 24" fill="{fill}" stroke="{stroke}" stroke-width="1.8" '
        f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>'
    )


# --- Avaliações do Google (dados em _src/google-reviews.json) -----------------
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro"]
STAR = "M12 2.5l2.9 6 6.6.8-4.9 4.5 1.3 6.5L12 17.1l-5.9 3.2 1.3-6.5L2.5 9.3l6.6-.8Z"
G_LOGO = ('<svg class="{cls}" viewBox="0 0 48 48" aria-hidden="true">'
          '<path fill="#FFC107" d="M43.6 20.1H42V20H24v8h11.3C33.7 32.7 29.2 36 24 36c-6.6 0-12-5.4-12-12s5.4-12 12-12c3.1 0 5.8 1.2 7.9 3.1l5.7-5.7C34 6.1 29.3 4 24 4 13 4 4 13 4 24s9 20 20 20 20-9 20-20c0-1.3-.1-2.6-.4-3.9Z"/>'
          '<path fill="#FF3D00" d="m6.3 14.7 6.6 4.8C14.7 15.1 19 12 24 12c3.1 0 5.8 1.2 7.9 3.1l5.7-5.7C34 6.1 29.3 4 24 4 16.3 4 9.7 8.3 6.3 14.7Z"/>'
          '<path fill="#4CAF50" d="M24 44c5.2 0 9.9-2 13.4-5.2l-6.2-5.2C29.2 35.1 26.7 36 24 36c-5.2 0-9.6-3.3-11.3-7.9l-6.5 5C9.5 39.6 16.2 44 24 44Z"/>'
          '<path fill="#1976D2" d="M43.6 20.1H42V20H24v8h11.3c-.8 2.2-2.2 4.2-4.1 5.6l6.2 5.2C37 39.2 44 34 44 24c0-1.3-.1-2.6-.4-3.9Z"/></svg>')


def load_reviews():
    with io.open(os.path.join(SRC, "google-reviews.json"), encoding="utf-8") as f:
        return json.load(f)


def stars(rating):
    out = [f'<span class="stars" role="img" aria-label="Nota {rating:g} de 5">']
    for i in range(1, 6):
        off = ' class="is-off"' if i > round(rating) else ""
        out.append(f'<svg viewBox="0 0 24 24" fill="currentColor"{off}><path d="{STAR}"/></svg>')
    out.append("</span>")
    return "".join(out)


def rating_br(value):
    return f"{value:.1f}".replace(".", ",")


def review_card(r):
    year, month = r["date"].split("-")
    when = f"{MESES[int(month) - 1]} de {year}"
    text = "<br><br>".join(html.escape(p.strip()) for p in r["text"].split("\n\n"))
    long = len(r["text"]) > 260
    more = '<button class="gcard__more" type="button">Ler mais</button>' if long else ""
    initial = html.escape(r["author"].strip()[0].upper())
    return (
        f'<article class="gcard{" gcard--long" if long else ""}">'
        f'<div class="gcard__head"><span class="avatar">{initial}</span>'
        f'<div><span class="gcard__author">{html.escape(r["author"])}</span>'
        f'<span class="gcard__when">{when}</span></div>{G_LOGO.format(cls="gcard__g")}</div>'
        f'{stars(r["rating"])}<p class="gcard__text">{text}</p>{more}</article>'
    )


def google_reviews(match):
    data = load_reviews()
    limit = int(match.group(1))
    reviews = data["reviews"][:limit]
    cols = " greviews--2col" if len(reviews) in (2, 4) else ""
    url = html.escape(data["placeUrl"])
    return (
        f'<div class="greviews{cols}">'
        '<div class="greviews__summary reveal"><div class="greviews__brand">'
        f'{G_LOGO.format(cls="greviews__g")}<div>'
        '<span class="greviews__label">Avaliações no Google</span>'
        f'<div class="greviews__score"><strong>{rating_br(data["rating"])}</strong>{stars(data["rating"])}</div>'
        f'<span class="greviews__total">{data["total"]} avaliações</span></div></div>'
        '<div class="greviews__actions">'
        f'<a class="btn btn--ghost btn--sm" href="{url}" target="_blank" rel="noopener">Ver todas no Google</a>'
        f'<a class="btn btn--sm" href="{url}" target="_blank" rel="noopener">Avaliar a MultiSorrisos</a>'
        '</div></div>'
        f'<div class="greviews__list">{"".join(review_card(r) for r in reviews)}</div></div>'
    )


def google_badge(_match):
    data = load_reviews()
    return (
        f'<li class="gbadge">{G_LOGO.format(cls="gbadge__g")}'
        f'<span><strong>{rating_br(data["rating"])}</strong> {stars(data["rating"])}'
        f'<small>{data["total"]} avaliações no Google</small></span></li>'
    )


# --- Galeria de pacientes (dados em _src/pacientes.json) ---------------------
TAMANHOS = {"alta": "tall", "larga": "wide"}


def patient_gallery(_match):
    with io.open(os.path.join(SRC, "pacientes.json"), encoding="utf-8") as f:
        fotos = json.load(f)["fotos"]
    items = []
    for p in fotos:
        size = TAMANHOS.get(p.get("tamanho", ""), "")
        cls = "pgallery__item" + (f" pgallery__item--{size}" if size else "")
        nome = html.escape(p.get("nome", ""))
        legenda = html.escape(p.get("legenda", ""))
        caption = f'<figcaption><strong>{nome}</strong><span>{legenda}</span></figcaption>' if nome or legenda else ""
        if p.get("foto"):
            alt = html.escape(p.get("alt") or p.get("nome") or "Paciente da MultiSorrisos")
            style = f' style="object-position: {html.escape(p["foco"])}"' if p.get("foco") else ""
            items.append(f'<figure class="{cls}"><img src="{html.escape(p["foto"])}" alt="{alt}" loading="lazy"{style}>{caption}</figure>')
        else:
            items.append(f'<figure class="{cls} pgallery__item--empty" aria-hidden="true">{svg_icon("smile")}<span>Foto do paciente</span></figure>')
    return '<div class="pgallery reveal">' + "".join(items) + "</div>"

def parse_page(text):
    m = re.match(r"\s*<!--(.*?)-->\s*", text, re.S)
    meta = {}
    if m:
        for line in m.group(1).strip().splitlines():
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip()
        text = text[m.end():]
    return meta, text


def render(template, ctx):
    for _ in range(3):  # permite includes que usam ícones/includes
        template = re.sub(r"\{\{include:([\w-]+)\}\}", lambda m: read(os.path.join(SRC, "partials", m.group(1) + ".html")), template)
    template = re.sub(r"\{\{google-reviews:(\d+)\}\}", google_reviews, template)
    template = re.sub(r"\{\{google-badge\}\}", google_badge, template)
    template = re.sub(r"\{\{patient-gallery\}\}", patient_gallery, template)
    template = re.sub(r"\{\{icon:([\w:-]+)\}\}", icon, template)
    for key, value in ctx.items():
        template = template.replace("{{" + key + "}}", value)
    return template


def main():
    layout = read(os.path.join(SRC, "layout.html"))
    pages_dir = os.path.join(SRC, "pages")
    for filename in sorted(os.listdir(pages_dir)):
        if not filename.endswith(".html"):
            continue
        meta, body = parse_page(read(os.path.join(pages_dir, filename)))
        out = filename
        nav = meta.get("nav", "")
        html = render(layout.replace("{{content}}", body), {
            "title": meta.get("title", "Multisorrisos Caruaru"),
            "description": meta.get("description", ""),
            "og_image": meta.get("image", "https://multisorrisoscaruaru.com.br/wp-content/uploads/2025/12/Multisorrisos025-1536x1024.jpg"),
            "og_type": meta.get("type", "website"),
            "year": str(date.today().year),
        })
        # marca o item ativo do menu
        if nav:
            html = html.replace(f'data-nav="{nav}"', f'data-nav="{nav}" class="is-active" aria-current="page"')
        with io.open(os.path.join(ROOT, out), "w", encoding="utf-8", newline="\n") as f:
            f.write(html)
        print("ok ", out)



if __name__ == "__main__":
    main()
