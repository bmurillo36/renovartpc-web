#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera la web de renovartpc.es.

    python _web/generar.py

Por qué un generador y no nueve ficheros sueltos: la cabecera, el menú, el pie
y las fichas de datos son idénticos en todas las páginas. Escritos a mano,
tarde o temprano una queda distinta —un teléfono viejo, un enlace roto— y nadie
se entera.

DOS DECISIONES QUE CONVIENE ENTENDER ANTES DE TOCAR ESTO:

1. LA HOJA DE ESTILO VA INCRUSTADA Y MINIFICADA en cada página, y el
   JavaScript va aparte con `defer`. No es capricho: la hoja bloquea el
   pintado y el guion no. Incrustada, no hay que esperar a una segunda
   petición para ver la página; y el guion, al ir aparte, se guarda una vez y
   vale para todas. `estilo.css` SIGUE SIENDO EL ORIGINAL: se edita ahí y se
   vuelve a ejecutar esto.

2. NO HAY CONTENEDOR DE TAG MANAGER. Va vacío a propósito (ver centro.py). El
   enganche está puesto: cuando la gestora diga cuál es, se escribe en
   `GTM` y funciona sin tocar nada más.
"""

import io
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)

from centro import (SITIO, CENTRO, TEL_E164, WASAP, WASAP_TEXTO, GTM)  # noqa: E402
import paginas  # noqa: E402

HOY = "2026-09-16"


# --------------------------------------------------------------------------
# Minificadores. Conservadores a propósito: quitan lo que no pinta y ya.
# --------------------------------------------------------------------------

def _sin_comentarios(txt, linea_tambien):
    """Quita comentarios respetando lo que va entrecomillado."""
    fuera, i, n = [], 0, len(txt)
    while i < n:
        c = txt[i]
        if c == "/" and txt[i + 1:i + 2] == "*":
            fin = txt.find("*/", i + 2)
            i = n if fin == -1 else fin + 2
            fuera.append("\n")
            continue
        if linea_tambien and c == "/" and txt[i + 1:i + 2] == "/":
            fin = txt.find("\n", i)
            i = n if fin == -1 else fin
            continue
        if c in "\"'`":
            j = i + 1
            while j < n and txt[j] != c:
                j += 2 if txt[j] == "\\" else 1
            fuera.append(txt[i:j + 1])
            i = j + 1
            continue
        fuera.append(c)
        i += 1
    return "".join(fuera)


def minifica_css(css):
    css = _sin_comentarios(css, False)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};,>])\s*", lambda m: m.group(1), css)
    css = re.sub(r":\s+", ":", css)
    css = re.sub(r";}", "}", css)
    # En las media queries hace falta el espacio: `and(` no existe.
    # PERO OJO CON EL PRECEDIDO: un `replace("not(", "not (")` a secas rompe
    # `a:not(.btn)` y lo convierte en `a:not (.btn)`, que es invalido, asi que
    # el navegador TIRA la regla entera y no dice nada. Paso el 13/09/2026 con
    # el menu: los enlaces salieron subrayados y la auditoria dio verde, porque
    # al desaparecer `.nav a:not(.btn)` el contraste salia bien por accidente.
    # El lookbehind evita justo eso: solo se toca cuando empieza palabra.
    css = re.sub(r"(?<![\w:.#-])(and|or|not)\(", r"\1 (", css)
    return css.strip()


def minifica_js(js):
    """NO junta líneas: en JavaScript el punto y coma final es opcional y
    juntar dos líneas puede cambiar lo que hace el programa sin dar error."""
    js = _sin_comentarios(js, True)
    return "\n".join(l for l in (x.strip() for x in js.split("\n")) if l)


# --------------------------------------------------------------------------
# La plantilla
# --------------------------------------------------------------------------

PLANTILLA = """<!doctype html>
<html lang="es-ES"{gtm}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo}</title>
<meta name="description" content="{descripcion}">
<link rel="canonical" href="{sitio}{url}">
<meta name="robots" content="{robots}">
<meta name="theme-color" content="#1F3B35">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Renovar la TPC · Prevención Siglo 21">
<meta property="og:locale" content="es_ES">
<meta property="og:title" content="{titulo}">
<meta property="og:description" content="{descripcion}">
<meta property="og:url" content="{sitio}{url}">
<meta name="twitter:card" content="summary">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<style>{css}</style>
{extra}</head>
<body>
<a class="saltar" href="#principal">Saltar al contenido</a>

<div class="barra">
  <div class="wrap barra__in">
    <span>Centro de formación acreditado · Móstoles (Madrid)</span>
    <span class="barra__tels">{tels}</span>
  </div>
</div>

<header class="cab">
  <div class="wrap cab__in">
    <a class="logo" href="/">
      <span class="logo__marca">Renovar <b>TPC</b></span>
      <span class="logo__sub">Prevención Siglo 21</span>
    </a>
    <input type="checkbox" id="abrir-menu" class="menu-check" hidden>
    <label for="abrir-menu" class="menu-boton" aria-label="Abrir el menú"><span></span></label>
    <nav class="nav" aria-label="Principal">
      <ul>
        {menu}
        <li><a class="btn btn--cta" href="/contacto/">Contacto</a></li>
      </ul>
    </nav>
  </div>
</header>

<main id="principal">
{cuerpo}
</main>

<footer class="pie">
  <div class="wrap">
    <div class="pie__grid">
      <div>
        <p class="pie__titulo">{empresa}</p>
        <p>{direccion}<br>{cp} {ciudad} ({provincia})<br>{referencia}</p>
        <p>Acreditado por la Comunidad de Madrid: {acreditacion}<br>
        Homologado por la Fundación Laboral de la Construcción: {homologacion}</p>
      </div>
      <div>
        <p class="pie__titulo">Hablar con alguien</p>
        <ul>{tels_pie}
          <li><a href="mailto:{correo}">{correo}</a></li>
          <li><a href="https://wa.me/{wasap}?text={wasap_texto}" rel="noopener">WhatsApp</a></li>
        </ul>
      </div>
      <div>
        <p class="pie__titulo">La web</p>
        <ul>
          <li><a href="/">Inicio</a></li>
          <li><a href="/renovar-la-tpc/">Cómo renovar la TPC</a></li>
          <li><a href="/tpc-caducada/">TPC caducada</a></li>
          <li><a href="/curso-reciclaje-4-horas/">Reciclaje de 4 horas</a></li>
          <li><a href="/cursos/">Cursos</a></li>
          <li><a href="/preguntas-frecuentes/">Preguntas frecuentes</a></li>
          <li><a href="/contacto/">Contacto</a></li>
        </ul>
      </div>
    </div>
    <div class="pie__legal">
      <span>© <span id="anyo">2026</span> {empresa}</span>
      <span>
        <a href="/aviso-legal/">Aviso legal</a> ·
        <a href="/politica-de-privacidad/">Privacidad</a> ·
        <a href="/politica-de-cookies/">Cookies</a> ·
        <a href="#" data-abrir-cookies>Cambiar cookies</a>
      </span>
    </div>
  </div>
</footer>

<a class="wasap" href="https://wa.me/{wasap}?text={wasap_texto}" rel="noopener"
   aria-label="Escribir por WhatsApp">
  <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12.04 2A9.9 9.9 0 0 0 2.1 11.9c0 1.75.46 3.45 1.34 4.95L2 22l5.3-1.39a9.9 9.9 0 0 0 4.74 1.21h.01a9.9 9.9 0 0 0 9.9-9.9A9.9 9.9 0 0 0 12.04 2zm0 18.15h-.01a8.2 8.2 0 0 1-4.19-1.15l-.3-.18-3.11.82.83-3.03-.2-.31a8.22 8.22 0 1 1 6.98 3.85zm4.5-6.16c-.25-.12-1.46-.72-1.68-.8-.23-.09-.39-.13-.56.12s-.64.8-.78.97c-.15.16-.29.18-.53.06-.25-.12-1.04-.38-1.98-1.22-.73-.65-1.23-1.46-1.37-1.71-.14-.24-.02-.38.11-.5.11-.11.25-.29.37-.44.13-.15.17-.25.25-.41.09-.17.04-.31-.02-.43-.06-.12-.56-1.34-.76-1.84-.2-.48-.4-.42-.56-.43h-.48c-.16 0-.43.06-.65.31-.22.25-.85.83-.85 2.03s.87 2.35.99 2.51c.12.17 1.71 2.61 4.15 3.66.58.25 1.03.4 1.39.51.58.19 1.11.16 1.53.1.47-.07 1.46-.6 1.66-1.18.21-.58.21-1.07.14-1.18-.06-.1-.22-.16-.47-.28z"/></svg>
</a>

<script src="/web.js" defer></script>
</body>
</html>
"""


def menu_html(actual):
    li = []
    for url, texto in paginas.MENU:
        cl = ' class="activo"' if url == actual else ""
        aria = ' aria-current="page"' if url == actual else ""
        li.append('<li><a href="%s"%s%s>%s</a></li>' % (url, cl, aria, texto))
    return "\n        ".join(li)


def monta(url, titulo, descripcion, cuerpo, extra="", robots=None):
    tels = " ".join('<a href="tel:%s">%s</a>' % (TEL_E164[t], t)
                    for t in CENTRO["telefonos"][:2])
    tels_pie = "".join('\n          <li><a href="tel:%s">%s</a></li>'
                       % (TEL_E164[t], t) for t in CENTRO["telefonos"])
    return PLANTILLA.format(
        gtm=(' data-gtm="%s"' % GTM) if GTM else "",
        titulo=titulo, descripcion=descripcion, url=url, sitio=SITIO,
        robots=robots or "index, follow, max-snippet:-1, max-image-preview:large",
        css=CSS, extra=extra, menu=menu_html(url), cuerpo=cuerpo,
        tels=tels, tels_pie=tels_pie,
        empresa=CENTRO["empresa"], direccion=CENTRO["direccion"],
        cp=CENTRO["cp"], ciudad=CENTRO["ciudad"], provincia=CENTRO["provincia"],
        referencia=CENTRO["referencia"],
        acreditacion=CENTRO["acreditacion_cm"],
        homologacion=CENTRO["homologacion_flc"],
        correo=CENTRO["correo"], wasap=WASAP, wasap_texto=WASAP_TEXTO)


def escribe(url, html):
    """La URL '/algo/' se escribe como 'algo/index.html'."""
    # Los comentarios del codigo NO se publican. Las notas para nosotros se
    # escriben dentro de bloques de HTML y acabarian en el fichero que ve todo
    # el mundo: uno de ellos, una fila de guiones, desbordaba el ancho en el
    # movil (16/09/2026). Se quitan aqui, en el ultimo paso.
    html = re.sub(r"<!--(?!\[if).*?-->\s*", "", html, flags=re.S)
    destino = RAIZ if url == "/" else os.path.join(RAIZ, url.strip("/"))
    os.makedirs(destino, exist_ok=True)
    ruta = os.path.join(destino, "index.html")
    io.open(ruta, "w", encoding="utf-8", newline="\n").write(html)
    return len(html)


# --------------------------------------------------------------------------

def main():
    global CSS
    original = io.open(os.path.join(RAIZ, "estilo.css"), encoding="utf-8").read()
    CSS = minifica_css(original)
    # Minificar no puede perder ni una regla. Si las llaves no cuadran, algo se
    # ha comido por el camino y mas vale parar que publicar una web a medio
    # pintar: un selector roto no da error, simplemente deja de aplicarse.
    if original.count("{") != CSS.count("{"):
        raise SystemExit("El minificador ha perdido reglas: %d llaves antes, %d "
                         "despues. NO se genera nada."
                         % (original.count("{"), CSS.count("{")))
    js = io.open(os.path.join(RAIZ, "web.js"), encoding="utf-8").read()
    mini_js = minifica_js(js)
    io.open(os.path.join(RAIZ, "web.min.js"), "w", encoding="utf-8", newline="\n").write(mini_js)

    print("Generando renovartpc.es")
    print("  hoja de estilo incrustada: %d letras (de %d)"
          % (len(CSS), os.path.getsize(os.path.join(RAIZ, "estilo.css"))))
    print("  guion: %d letras (de %d)" % (len(mini_js), len(js)))
    print()

    total = 0
    for url, titulo, descripcion, constructor, robots in paginas.TODAS:
        cuerpo, extra = constructor()
        n = escribe(url, monta(url, titulo, descripcion, cuerpo, extra, robots))
        total += n
        print("  %-34s %7d letras" % (url, n))

    # --- sitemap, robots y el fichero para las IA ---
    urls = "".join(
        '  <url><loc>%s%s</loc><lastmod>%s</lastmod>'
        '<changefreq>monthly</changefreq><priority>%s</priority></url>\n'
        % (SITIO, u, HOY, "1.0" if u == "/" else "0.7")
        for u, _t, _d, _c, r in paginas.TODAS if "noindex" not in (r or ""))
    io.open(os.path.join(RAIZ, "sitemap.xml"), "w", encoding="utf-8", newline="\n").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + urls + '</urlset>\n')

    io.open(os.path.join(RAIZ, "robots.txt"), "w", encoding="utf-8", newline="\n").write(
        "# %s\nUser-agent: *\nAllow: /\nDisallow: /gracias/\n\n"
        "# Buscadores con IA: bienvenidos. Lo que buscan está en /llms.txt\n"
        "User-agent: GPTBot\nAllow: /\n"
        "User-agent: OAI-SearchBot\nAllow: /\n"
        "User-agent: ChatGPT-User\nAllow: /\n"
        "User-agent: ClaudeBot\nAllow: /\n"
        "User-agent: Claude-User\nAllow: /\n"
        "User-agent: PerplexityBot\nAllow: /\n"
        "User-agent: Google-Extended\nAllow: /\n"
        "User-agent: Applebot-Extended\nAllow: /\n"
        "User-agent: Bingbot\nAllow: /\n\n"
        "Sitemap: %s/sitemap.xml\n" % (SITIO, SITIO))

    io.open(os.path.join(RAIZ, "llms.txt"), "w", encoding="utf-8", newline="\n").write(
        paginas.llms())

    print("\n  sitemap.xml, robots.txt y llms.txt")
    print("\n  TOTAL: %d letras en %d páginas" % (total, len(paginas.TODAS)))
    print("  Todo en: %s" % RAIZ)


if __name__ == "__main__":
    main()
