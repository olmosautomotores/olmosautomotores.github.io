#!/usr/bin/env python3
"""Olmos Automotores — genera la página a partir de autos.json.

Uso (desde la carpeta OLMOSWEB):
  .venv/bin/python tools/build.py build              # procesa fotos nuevas + genera páginas
  .venv/bin/python tools/build.py fotos <id> --reemplazar   # vuelve a procesar las fotos de un auto
  .venv/bin/python tools/build.py publicar "mensaje"  # build + git commit + push
"""
import html, json, os, shutil, subprocess, sys, urllib.parse
from datetime import date
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOTOS = os.path.join(ROOT, "fotos")
SIZES = {"": 1080, "m": 720, "t": 220}  # carpeta -> ancho
VER = "6"

e = html.escape


def load():
    with open(os.path.join(ROOT, "autos.json"), encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------- fotos
def procesar_fotos(auto, reemplazar=False):
    dst = os.path.join(FOTOS, auto["id"])
    if os.path.isdir(dst) and not reemplazar:
        return
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    for sub in SIZES:
        os.makedirs(os.path.join(dst, sub), exist_ok=True)
    for n, src in enumerate(auto.get("fotos_origen", []), 1):
        p = src if os.path.isabs(src) else os.path.join(ROOT, src)
        im = ImageOps.exif_transpose(Image.open(p)).convert("RGB")
        for sub, w in SIZES.items():
            r = im if im.width <= w else im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
            r.save(os.path.join(dst, sub, f"{n}.jpg"), "JPEG", quality=80 if sub != "t" else 72, optimize=True, progressive=True)
    print(f"  fotos {auto['id']}: {len(auto.get('fotos_origen', []))}")


def lista_fotos(auto):
    d = os.path.join(FOTOS, auto["id"])
    if not os.path.isdir(d):
        return []
    return sorted([f for f in os.listdir(d) if f.endswith(".jpg")], key=lambda f: int(f.split(".")[0]))


# ---------------------------------------------------------------- formato
def miles(n):
    return f"{int(n):,}".replace(",", ".")


def precio_html(a):
    if not a.get("precio"):
        return '<span class="price">Consultar</span>'
    sym = "US$" if a.get("moneda") == "USD" else "$"
    return f'<span class="price"><small>{sym}</small>{miles(a["precio"])}</span>'


def precio_txt(a):
    if not a.get("precio"):
        return "Consultar precio"
    return ("US$ " if a.get("moneda") == "USD" else "$ ") + miles(a["precio"])


def titulo(a):
    return f'{a["marca"]} {a["modelo"]}'


def nombre_largo(a):
    return " ".join(x for x in [a["marca"], a["modelo"], a.get("version", ""), str(a.get("anio", ""))] if x)


def wa_link(neg, texto):
    return f'https://wa.me/{neg["whatsapp"]}?text={urllib.parse.quote(texto)}'


# ---------------------------------------------------------------- íconos
def ic(name):
    P = {
        "wa": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.47 14.38c-.3-.15-1.75-.86-2.02-.96-.27-.1-.47-.15-.67.15-.2.3-.77.96-.94 1.16-.17.2-.35.22-.64.07-.3-.15-1.25-.46-2.38-1.47-.88-.79-1.47-1.76-1.65-2.06-.17-.3-.02-.46.13-.6.13-.14.3-.35.45-.52.15-.18.2-.3.3-.5.1-.2.05-.37-.03-.52-.07-.15-.67-1.6-.92-2.2-.24-.58-.49-.5-.67-.5h-.57c-.2 0-.52.07-.8.37-.27.3-1.04 1.02-1.04 2.48s1.07 2.88 1.21 3.08c.15.2 2.1 3.2 5.08 4.49.71.3 1.26.49 1.7.63.71.22 1.36.19 1.87.12.57-.09 1.75-.72 2-1.41.25-.7.25-1.29.17-1.41-.07-.13-.27-.2-.57-.35M12.05 21.5h-.01a9.4 9.4 0 0 1-4.8-1.31l-.34-.2-3.57.93.95-3.48-.22-.36a9.4 9.4 0 0 1-1.44-5.02c0-5.2 4.23-9.43 9.44-9.43 2.52 0 4.89.98 6.67 2.77a9.37 9.37 0 0 1 2.76 6.67c0 5.2-4.23 9.43-9.44 9.43M20.08 3.9A11.3 11.3 0 0 0 12.05.58C5.79.58.7 5.67.7 11.92c0 2 .52 3.95 1.52 5.67L.6 23.42l5.96-1.56a11.3 11.3 0 0 0 5.48 1.4h.01c6.25 0 11.34-5.1 11.34-11.35 0-3.03-1.18-5.88-3.32-8.02"/></svg>',
        "arrow": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
        "back": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M19 12H5M11 18l-6-6 6-6"/></svg>',
        "l": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m15 18-6-6 6-6"/></svg>',
        "r": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m9 18 6-6-6-6"/></svg>',
        "x": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12"/></svg>',
        "check": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9.5" opacity=".35"/><path d="m8 12.5 2.6 2.5L16 9.5"/></svg>',
        "cam": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="6" width="18" height="14" rx="2.5"/><circle cx="12" cy="13" r="3.5"/><path d="M8.5 6 10 3.5h4L15.5 6"/></svg>',
        "search": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>',
        "money": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2.5" y="6" width="19" height="12" rx="2.5"/><circle cx="12" cy="12" r="2.6"/><path d="M6 9.5v5M18 9.5v5"/></svg>',
        "swap": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 8h13l-3.5-3.5M20 16H7l3.5 3.5"/></svg>',
        "key": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="8" cy="15" r="4.5"/><path d="m11.2 11.8 8.3-8.3M16.5 6.5l2.5 2.5M14 9l2 2"/></svg>',
        "doc": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M9 13h6M9 17h4"/></svg>',
        "pin": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 21s-7-6.1-7-11.5a7 7 0 0 1 14 0C19 14.9 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/></svg>',
        "ig": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4.2"/><circle cx="17.4" cy="6.6" r="1.1" fill="currentColor" stroke="none"/></svg>',
        "phone": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 1.1 4.2 2 2 0 0 1 3.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L7 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/></svg>',
        "share": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="m8.6 13.5 6.8 4M15.4 6.5l-6.8 4"/></svg>',
        "shield": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg>',
    }
    return P[name]


# ---------------------------------------------------------------- layout
FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Archivo:ital,wdth,wght@0,62..125,600..800;1,62..125,600..800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">'


def head(neg, title, desc, url, img, base):
    return f"""<!DOCTYPE html>
<html lang="es-AR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="theme-color" content="#0a0a0b">
<link rel="canonical" href="{e(url)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{e(neg['nombre'])}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{e(url)}">
<meta property="og:image" content="{e(img)}">
<meta property="og:locale" content="es_AR">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" href="{base}assets/icono.png">
<link rel="apple-touch-icon" href="{base}assets/apple-touch-icon.png">
{FONTS}
<link rel="stylesheet" href="{base}assets/style.css?v={VER}">
</head>
<body>
"""


def header(neg, base, home=False):
    pre = "" if home else f"{base}"
    wa = wa_link(neg, "Hola! Quería hacer una consulta.")
    return f"""<header class="top"><div class="wrap">
  <a class="brand" href="{base or './'}" aria-label="{e(neg['nombre'])} — inicio"><img src="{base}assets/logo-blanco.png" alt="{e(neg['nombre'])}" width="774" height="119"></a>
  <nav class="nav" aria-label="Principal"><a href="{pre}#stock">Stock</a><a href="{pre}#servicios">Servicios</a><a href="{pre}#vender">Vendé tu auto</a><a href="{pre}#contacto">Contacto</a></nav>
  <a class="btn btn-wa btn-sm" href="{e(wa)}" target="_blank" rel="noopener" aria-label="WhatsApp">{ic('wa')}<span>WhatsApp</span></a>
</div></header>
"""


def footer(neg, base, wa_text):
    wa = wa_link(neg, wa_text)
    return f"""<footer class="foot"><div class="wrap">
  <img src="{base}assets/logo-blanco.png" alt="{e(neg['nombre'])}" width="774" height="119" loading="lazy">
  <div>{e(neg['ciudad'])} · <a href="tel:+{neg['whatsapp']}">{e(neg['telefono'])}</a> · <a href="https://instagram.com/{neg['instagram']}" target="_blank" rel="noopener">@{e(neg['instagram'])}</a></div>
  <div>© {date.today().year} {e(neg['nombre'])}</div>
</div></footer>
<a class="fab" href="{e(wa)}" target="_blank" rel="noopener" aria-label="Escribinos por WhatsApp">{ic('wa')}</a>
<script src="{base}assets/app.js?v={VER}" defer></script>
</body>
</html>
"""


def specs_chips(a):
    out = []
    if a.get("anio"): out.append(str(a["anio"]))
    if a.get("km") is not None: out.append(f'{miles(a["km"])} km')
    if a.get("caja"): out.append(a["caja"])
    if a.get("combustible"): out.append(a["combustible"])
    return "".join(f"<span>{e(x)}</span>" for x in out)


def badge(a):
    if a.get("estado") == "reservado":
        return '<span class="badge res">Reservado</span>'
    if a.get("estado") == "vendido":
        return '<span class="badge">Vendido</span>'
    return ""


def card(a, base):
    fotos = lista_fotos(a)
    cover = f'{base}fotos/{a["id"]}/m/{fotos[0]}' if fotos else f"{base}assets/og-olmos.jpg"
    txt = " ".join(str(a.get(k, "")) for k in ["marca", "modelo", "version", "anio", "combustible", "caja", "carroceria", "traccion"])
    from unicodedata import normalize
    txt = normalize("NFD", txt.lower()).encode("ascii", "ignore").decode()
    fecha = a.get("fecha", "2000-01-01").replace("-", "")
    return f"""<a class="card" href="{base}a/{a['id']}/" data-tipo="{e((a.get('carroceria') or 'otro').lower())}" data-txt="{e(txt)}" data-anio="{a.get('anio', 0)}" data-km="{a.get('km') or 0}" data-fecha="{fecha}">
  <div class="ph"><img src="{cover}" alt="{e(nombre_largo(a))}" loading="lazy" width="720" height="900">{badge(a)}<span class="nph">{ic('cam')}{len(fotos)}</span></div>
  <div class="bd">
    <div><h3>{e(titulo(a))}</h3><div class="ver">{e(a.get('version', ''))}</div></div>
    <div class="specs">{specs_chips(a)}</div>
    <div class="ft">{precio_html(a)}<span class="go">Ver auto {ic('arrow')}</span></div>
  </div>
</a>"""


# ---------------------------------------------------------------- páginas
def pagina_inicio(data):
    neg, autos = data["negocio"], data["autos"]
    visibles = [a for a in autos if a.get("estado") != "vendido"]
    visibles.sort(key=lambda a: a.get("fecha", ""), reverse=True)
    tipos = sorted({(a.get("carroceria") or "otro") for a in visibles})
    chips = '<button class="chip" data-tipo="todos" aria-pressed="true">Todos</button>' + "".join(
        f'<button class="chip" data-tipo="{e(t.lower())}" aria-pressed="false">{e(t)}</button>' for t in tipos) if len(tipos) > 1 else ""
    cards = "\n".join(card(a, "") for a in visibles)
    desc = f"Autos usados seleccionados en {neg['ciudad']}. Financiación, permutas, consignaciones y gestoría. Consultá por WhatsApp al {neg['telefono']}."
    title = f"{neg['nombre']} · Autos en venta en Mendoza"
    wa_hola = wa_link(neg, "Hola! Vi la página y quería consultar por un vehículo.")
    wa_vender = wa_link(neg, "Hola! Quiero vender mi auto / dejarlo en consignación. ¿Cómo es el proceso?")
    wa_fin = wa_link(neg, "Hola! Quería consultar por financiación.")
    out = head(neg, title, desc, neg["url"], neg["url"] + "assets/og-olmos.jpg", "")
    out += header(neg, "", home=True)
    out += f"""<main>
<section class="hero"><div class="stripes" aria-hidden="true"><i></i><i></i><i></i></div><div class="wrap">
  <span class="eyebrow">Compra · Venta · {e(neg['ciudad'].split(',')[0])}</span>
  <h1>Tu próximo vehículo <span>empieza acá.</span></h1>
  <p class="lead">Autos usados seleccionados, con fotos reales y precio a la vista. Te acompañamos en todo: papeles, turnos y transferencia.</p>
  <div class="ctas">
    <a class="btn btn-accent" href="#stock">Ver autos disponibles {ic('arrow')}</a>
    <a class="btn btn-ghost" href="{e(wa_hola)}" target="_blank" rel="noopener">{ic('wa')} Consultar por WhatsApp</a>
  </div>
  <ul class="perks">
    <li>{ic('money')} Financiación</li><li>{ic('swap')} Permutas</li><li>{ic('key')} Consignaciones</li><li>{ic('doc')} Gestoría</li>
  </ul>
</div></section>

<section class="sec" id="stock"><div class="wrap">
  <div class="sec-head"><div><span class="eyebrow">Stock</span><h2>Autos disponibles</h2></div><span class="count" id="count"></span></div>
  <div class="toolbar">
    <label class="search"><span class="sr">Buscar</span>{ic('search')}<input id="q" type="search" placeholder="Buscar marca, modelo o año" autocomplete="off"></label>
    <div class="chips">{chips}</div>
    <select class="sort" id="sort" aria-label="Ordenar"><option value="recientes">Más recientes</option><option value="anio">Año: más nuevo</option><option value="km">Menor kilometraje</option></select>
  </div>
  <div class="grid" id="grid">
{cards}
    <div class="empty" id="empty" hidden>No encontramos autos con esa búsqueda.<br>Escribinos y te avisamos cuando entre uno.</div>
  </div>
</div></section>

<section class="sec svc" id="servicios"><div class="wrap">
  <div class="sec-head"><div><span class="eyebrow">Servicios</span><h2>Comprar sin vueltas</h2><p class="sec-sub">Nos ocupamos de los trámites, turnos y papeleos para que te lleves el tuyo tranquilo.</p></div></div>
  <div class="svc-grid">
    <div class="svc-card"><div class="ic">{ic('money')}</div><h3>Financiación</h3><p>Consultanos las opciones para pagar tu próximo auto en cuotas.</p></div>
    <div class="svc-card"><div class="ic">{ic('swap')}</div><h3>Permutas</h3><p>Entregá tu usado como parte de pago y llevate el que buscás.</p></div>
    <div class="svc-card"><div class="ic">{ic('key')}</div><h3>Consignaciones</h3><p>Dejá tu auto con nosotros y nos encargamos de venderlo, de principio a fin.</p></div>
    <div class="svc-card"><div class="ic">{ic('doc')}</div><h3>Gestoría</h3><p>Transferencias, informes y papeles. Simple, ágil y seguro.</p></div>
  </div>
  <div class="sell" id="vender"><div><h3>¿Querés vender tu auto?</h3><p>Vos confiás, nosotros nos encargamos. Mandanos fotos y datos por WhatsApp.</p></div>
    <a class="btn btn-accent" href="{e(wa_vender)}" target="_blank" rel="noopener">{ic('wa')} Quiero vender mi auto</a></div>
</div></section>

<section class="sec" id="contacto"><div class="wrap contact-grid">
  <div class="contact-main"><span class="eyebrow">Contacto</span><h2>Hablemos</h2>
    <p class="sec-sub">¿Viste un auto que te gusta o querés que te busquemos uno? Escribinos y te respondemos a la brevedad.</p>
    <div class="ctas"><a class="btn btn-wa" href="{e(wa_hola)}" target="_blank" rel="noopener">{ic('wa')} Escribir por WhatsApp</a><a class="btn btn-ghost" href="{e(wa_fin)}" target="_blank" rel="noopener">Consultar financiación</a></div>
  </div>
  <div class="contact-list">
    <a class="ci" href="{e(wa_hola)}" target="_blank" rel="noopener"><span class="ic">{ic('wa')}</span><span><small>WhatsApp</small><b>{e(neg['telefono'])}</b></span></a>
    <a class="ci" href="tel:+{neg['whatsapp']}"><span class="ic">{ic('phone')}</span><span><small>Llamanos</small><b>{e(neg['telefono'])}</b></span></a>
    <a class="ci" href="https://instagram.com/{neg['instagram']}" target="_blank" rel="noopener"><span class="ic">{ic('ig')}</span><span><small>Instagram</small><b>@{e(neg['instagram'])}</b></span></a>
    <div class="ci"><span class="ic">{ic('pin')}</span><span><small>Ubicación</small><b>{e(neg['ciudad'])}</b></span></div>
  </div>
</div></section>
</main>
"""
    out += footer(neg, "", "Hola! Vi la página y quería consultar por un vehículo.")
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
        f.write(out)


def pagina_auto(data, a):
    neg = data["negocio"]
    base = "../../"
    fotos = lista_fotos(a)
    url = f'{neg["url"]}a/{a["id"]}/'
    nombre = nombre_largo(a)
    vendido = a.get("estado") == "vendido"
    km = f'{miles(a["km"])} km' if a.get("km") is not None else ""
    desc = f'{nombre} · {km} · {precio_txt(a)}. {a.get("descripcion", "")}'.strip()
    img = f'{neg["url"]}fotos/{a["id"]}/m/{fotos[0]}' if fotos else neg["url"] + "assets/og-olmos.jpg"
    wa_txt = f"Hola! Vi el {nombre} en la página de {neg['nombre']} ({precio_txt(a)}). ¿Sigue disponible?\n{url}"
    wa = wa_link(neg, wa_txt)

    slides = "".join(
        f'<img src="{base}fotos/{a["id"]}/{f}" data-full="{base}fotos/{a["id"]}/{f}" alt="{e(nombre)} — foto {i}" width="1080" height="1350" {"" if i == 1 else "loading=\"lazy\""} draggable="false">'
        for i, f in enumerate(fotos, 1))
    thumbs = "".join(
        f'<button type="button" aria-label="Foto {i}"><img src="{base}fotos/{a["id"]}/t/{f}" alt="" loading="lazy" width="220" height="275"></button>'
        for i, f in enumerate(fotos, 1)) if len(fotos) > 1 else ""

    filas = [("Año", a.get("anio")), ("Kilómetros", km), ("Motor", a.get("motor")), ("Combustible", a.get("combustible")),
             ("Caja", a.get("caja")), ("Tracción", a.get("traccion")), ("Carrocería", a.get("carroceria")), ("Color", a.get("color"))]
    filas = [(k, v) for k, v in filas if v]
    if len(filas) % 2: filas.append(("Ubicación", "Mendoza"))
    sheet = "".join(f"<div><small>{e(k)}</small><b>{e(str(v))}</b></div>" for k, v in filas)

    dest = a.get("destacados") or []
    bloque_dest = ""
    if dest:
        bloque_dest = '<div class="block"><h2>Destacados</h2><ul class="checks">' + "".join(
            f"<li>{ic('check')}<span>{e(x)}</span></li>" for x in dest) + "</ul></div>"
    bloque_desc = f'<div class="block"><h2>Descripción</h2><p class="desc">{e(a["descripcion"])}</p></div>' if a.get("descripcion") else ""
    aviso = '<div class="sold"><b>Este vehículo ya se vendió.</b> Mirá los otros autos disponibles o escribinos y te buscamos uno parecido.</div>' if vendido else ""

    otros = [o for o in data["autos"] if o["id"] != a["id"] and o.get("estado") != "vendido"]
    otros.sort(key=lambda o: o.get("fecha", ""), reverse=True)
    bloque_otros = ""
    if otros:
        bloque_otros = f'<section class="sec" style="padding-top:0"><div class="wrap"><div class="sec-head"><div><span class="eyebrow">Stock</span><h2>Otros autos disponibles</h2></div><a class="go" href="{base}#stock">Ver todos {ic("arrow")}</a></div><div class="grid">' + \
            "".join(card(o, base) for o in otros[:3]) + "</div></div></section>"

    out = head(neg, f"{nombre} · {neg['nombre']}", desc, url, img, base)
    out += header(neg, base)
    out += f"""<main>
<div class="wrap"><div class="crumb"><a href="{base}#stock">{ic('back')} Volver al stock</a></div>
<div class="detail">
  <div class="gallery">
    <div class="stage">{badge(a)}<div class="track">{slides}</div>
      <button class="arrow prev" type="button" aria-label="Foto anterior">{ic('l')}</button><button class="arrow next" type="button" aria-label="Foto siguiente">{ic('r')}</button>
      <span class="counter"></span></div>
    <div class="thumbs">{thumbs}</div>
  </div>
  <div class="info">
    <div class="mk">{e(a['marca'])}</div>
    <h1>{e(a['modelo'])}</h1>
    <p class="ver">{e(a.get('version', ''))} · {e(str(a.get('anio', '')))}</p>
    {precio_html(a)}
    <p class="note">Aceptamos permutas · Consultá financiación</p>
    {aviso}
    <div class="sheet">{sheet}</div>
    <div class="actions">
      <a class="btn btn-wa" href="{e(wa)}" target="_blank" rel="noopener">{ic('wa')} Consultar por WhatsApp</a>
      <div class="row"><a class="btn btn-ghost" href="tel:+{neg['whatsapp']}">{ic('phone')} Llamar</a><button class="btn btn-ghost" type="button" data-share>{ic('share')} Compartir</button></div>
    </div>
    <div class="trust">
      <div>{ic('doc')}<span><b>Gestoría</b>Te ayudamos con la transferencia</span></div>
      <div>{ic('swap')}<span><b>Permutas</b>Tomamos tu usado</span></div>
      <div>{ic('shield')}<span><b>Vení a verlo</b>Coordinamos una visita</span></div>
    </div>
    {bloque_dest}
    {bloque_desc}
  </div>
</div></div>
{bloque_otros}
</main>
<div class="lb" role="dialog" aria-label="Fotos"><img alt=""><button class="x" type="button" aria-label="Cerrar">{ic('x')}</button><button class="arrow prev" type="button" aria-label="Anterior">{ic('l')}</button><button class="arrow next" type="button" aria-label="Siguiente">{ic('r')}</button><span class="counter"></span></div>
"""
    out += footer(neg, base, wa_txt)
    d = os.path.join(ROOT, "a", a["id"])
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
        f.write(out)


def sitemap(data):
    u = data["negocio"]["url"]
    urls = [u] + [f'{u}a/{a["id"]}/' for a in data["autos"] if a.get("estado") != "vendido"]
    with open(os.path.join(ROOT, "sitemap.xml"), "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
                "".join(f"  <url><loc>{x}</loc></url>\n" for x in urls) + "</urlset>\n")


def build():
    data = load()
    for a in data["autos"]:
        procesar_fotos(a)
    # limpiar páginas de autos borrados del json
    ids = {a["id"] for a in data["autos"]}
    adir = os.path.join(ROOT, "a")
    if os.path.isdir(adir):
        for d in os.listdir(adir):
            if d not in ids and os.path.isdir(os.path.join(adir, d)):
                shutil.rmtree(os.path.join(adir, d))
    pagina_inicio(data)
    for a in data["autos"]:
        pagina_auto(data, a)
    sitemap(data)
    disp = sum(1 for a in data["autos"] if a.get("estado") == "disponible")
    print(f"OK: {len(data['autos'])} autos ({disp} disponibles)")


def main():
    args = sys.argv[1:]
    if not args or args[0] == "build":
        build()
    elif args[0] == "fotos":
        data = load()
        a = next(x for x in data["autos"] if x["id"] == args[1])
        procesar_fotos(a, reemplazar=True)
        build()
    elif args[0] == "publicar":
        build()
        msg = args[1] if len(args) > 1 else "Actualizar stock"
        subprocess.run(["git", "add", "-A"], cwd=ROOT, check=True)
        subprocess.run(["git", "commit", "-m", msg], cwd=ROOT)
        subprocess.run(["git", "push"], cwd=ROOT, check=True)
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
