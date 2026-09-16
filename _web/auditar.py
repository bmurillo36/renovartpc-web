#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audita la web generada. Se ejecuta, no se lee.

    python _web/auditar.py

Dos partes:

  A. LO QUE SE PUEDE MIRAR EN EL FICHERO: que cada página tenga título,
     descripción, canónica y datos estructurados; que no haya enlaces rotos
     dentro de la web; que solo /gracias/ vaya en noindex; que el formulario
     apunte a donde debe; que no se cuele un contenedor de medición sin
     consentimiento. Y LA REGLA DE ORO DE ESTA WEB: que ninguna página dé a
     entender que el curso de reciclaje de 4 horas de construcción existe.
     Ver CLAUDE.md.

  B. LO QUE SOLO SE VE EJECUTÁNDOLO, en Chrome de verdad: el contraste real
     de cada texto sobre su fondo real, que la página no se desborde a lo
     ancho en un móvil, que el aviso de cookies salga y que sus dos botones
     funcionen, y que no haya ni un error en la consola.

Sale con código 1 si algo falla, para poder engancharlo a un despliegue.
"""

import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)

from centro import SITIO, FORMULARIO, GTM  # noqa: E402
import paginas  # noqa: E402

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

fallos = []
avisos = []


def mal(que, detalle=""):
    fallos.append("%s%s" % (que, ("  — " + detalle) if detalle else ""))


def ojo(que, detalle=""):
    avisos.append("%s%s" % (que, ("  — " + detalle) if detalle else ""))


def leer(url):
    p = RAIZ if url == "/" else os.path.join(RAIZ, url.strip("/"))
    ruta = os.path.join(p, "index.html")
    if not os.path.exists(ruta):
        return None
    return io.open(ruta, encoding="utf-8").read()


# ==========================================================================
# A. En el fichero
# ==========================================================================

def parte_a():
    print("=== A. Lo que se ve en el fichero ===")
    urls = [u for u, _t, _d, _c, _r in paginas.TODAS]
    paginas_html = {}

    for url, titulo, descr, _c, robots in paginas.TODAS:
        h = leer(url)
        if h is None:
            mal("falta la página", url)
            continue
        paginas_html[url] = h

        if "<title>%s</title>" % titulo not in h:
            mal("título distinto del declarado", url)
        if len(titulo) > 70:
            ojo("título largo (%d letras, Google corta ~60)" % len(titulo), url)
        if 'name="description" content="%s"' % descr not in h:
            mal("descripción distinta de la declarada", url)
        if not (110 <= len(descr) <= 165):
            ojo("descripción de %d letras (lo cómodo son 120-160)" % len(descr), url)
        if 'rel="canonical" href="%s%s"' % (SITIO, url) not in h:
            mal("canónica ausente o distinta", url)
        if 'property="og:title"' not in h:
            mal("sin Open Graph", url)
        if h.count("<h1") != 1:
            mal("tiene %d <h1> (debe haber exactamente uno)" % h.count("<h1"), url)
        if 'lang="es-ES"' not in h:
            mal("sin idioma declarado", url)

        # noindex: solo /gracias/
        tiene_noindex = "noindex" in h
        if url == "/gracias/" and not tiene_noindex:
            mal("/gracias/ TIENE que ir en noindex: si no, Google la indexa y "
                "cada visita cuenta como una conversión falsa")
        if url != "/gracias/" and tiene_noindex:
            mal("noindex donde no toca", url)

        # Enlaces internos rotos
        for destino in set(re.findall(r'href="(/[^"#?]*)"', h)):
            if destino in urls:
                continue
            if os.path.exists(os.path.join(RAIZ, destino.strip("/"))):
                continue
            if os.path.exists(os.path.join(RAIZ, destino.lstrip("/"))):
                continue
            mal("enlace interno roto: %s" % destino, url)

    # Datos estructurados: que sean JSON válido
    for url, h in paginas_html.items():
        for bloque in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S):
            try:
                json.loads(bloque)
            except Exception as e:
                mal("datos estructurados rotos: %s" % e, url)

    # Que cada página declare lo suyo. La portada NO lleva Course: esta web va
    # de un trámite, no de un curso, y declarar un Course en la portada sería
    # decirle a Google que aquí se vende formación para renovar.
    p = paginas_html.get("/", "")
    for tipo in ('"EducationalOrganization"', '"HowTo"'):
        if tipo not in p:
            mal("la portada no declara %s en los datos estructurados" % tipo)
    if '"HowTo"' not in paginas_html.get("/renovar-la-tpc/", ""):
        mal("la página del trámite no declara HowTo")
    if '"Course"' not in paginas_html.get("/cursos/", ""):
        mal("la página de cursos no declara Course")
    if '"FAQPage"' not in paginas_html.get("/preguntas-frecuentes/", ""):
        mal("la página de preguntas no declara FAQPage")

    # ---- LA REGLA DE ORO DE ESTA WEB ------------------------------------
    # El curso de reciclaje de 4 horas de construccion NO EXISTE hoy. Esta
    # comprobacion existe porque la tentacion de escribir «proximamente» o
    # «ya disponible» es enorme y se cuela en una frase suelta, no en un
    # rediseno. Ver CLAUDE.md y RECICLAJE_4H en centro.py.
    prohibido = [
        "próximamente", "proximamente",
        "ya disponible", "ya está disponible", "ya esta disponible",
        "reserva tu plaza para el reciclaje", "preinscríbete", "preinscribete",
        "nuevo curso de reciclaje", "curso de reciclaje de 4 horas ya",
    ]
    for url, h in paginas_html.items():
        bajo = h.lower()
        for frase in prohibido:
            if frase in bajo:
                mal("dice «%s»: el reciclaje de 4 horas de construcción NO "
                    "existe y esta web no puede insinuar que sí" % frase, url)
    rec = paginas_html.get("/curso-reciclaje-4-horas/", "")
    if "no existe" not in rec.lower():
        mal("la página del reciclaje de 4 horas no dice claramente que hoy no "
            "existe: es lo único que esa página tiene que dejar claro")
    if "no existe" not in io.open(os.path.join(RAIZ, "llms.txt"),
                                  encoding="utf-8").read().lower():
        mal("llms.txt no dice que el reciclaje de 4 horas no existe")

    # El formulario
    for url in ("/", "/contacto/", "/curso-reciclaje-4-horas/"):
        h = paginas_html.get(url, "")
        if FORMULARIO not in h:
            mal("el formulario no apunta al servicio propio", url)
        if 'name="_honey"' not in h:
            mal("falta la trampa antispam (_honey)", url)
        if 'name="_t"' not in h:
            mal("falta el sello antispam (_t)", url)

        # LOS NOMBRES DE LOS CAMPOS. Esta comprobacion existe porque el
        # 13/09/2026 la web se publico con los campos en minuscula (nombre,
        # correo, telefono, consentimiento) y el servicio solo entiende estos
        # siete, con inicial mayuscula. Resultado: el formulario se veia
        # perfecto, el visitante lo rellenaba, y no llegaba NADA.
        # Y esta misma auditoria daba VERDE, porque comprobaba
        # `name="consentimiento"`, que era justo el nombre equivocado. Una
        # prueba escrita a partir del codigo, en vez de a partir de lo que el
        # servicio espera, solo sirve para confirmar el error.
        for campo in ("Nombre", "Telefono", "Email", "Curso", "Mensaje",
                      "Acepto", "Origen"):
            if 'name="%s"' % campo not in h:
                mal("al formulario le falta el campo %s (el servicio solo "
                    "entiende Nombre, Email, Telefono, Curso, Mensaje, Acepto "
                    "y Origen, con inicial mayuscula)" % campo, url)
        for viejo in ("nombre", "correo", "telefono", "mensaje", "consentimiento"):
            if 'name="%s"' % viejo in h:
                mal("el formulario manda «%s» en minuscula: el servicio lo tira "
                    "y el aviso llega vacio" % viejo, url)

        # Que el envio acabe en la pagina de gracias de ESTA web.
        if 'name="_next" value="%s/gracias/"' % SITIO not in h:
            mal("el formulario no lleva a la pagina de gracias de esta web", url)
        # Y que nadie vuelva a interceptar el envio: con _json el servicio
        # contesta JSON en vez de redirigir, y no se llega a /gracias/.
        if 'name="_json"' in h:
            mal("el formulario pide respuesta JSON: asi no redirige a /gracias/",
                url)

    # Medición: nada de contenedores en el HTML
    for url, h in paginas_html.items():
        if "googletagmanager.com" in h:
            mal("carga la medición desde el HTML: tiene que ir después del "
                "consentimiento, en web.js", url)
        if re.search(r"GTM-[A-Z0-9]{6,}", h) and not GTM:
            mal("hay un contenedor escrito a mano y centro.py dice que no hay "
                "ninguno asignado", url)

    # Ficheros sueltos
    for f in ("robots.txt", "sitemap.xml", "llms.txt", "estilo.css", "web.js",
              "favicon.svg"):
        if not os.path.exists(os.path.join(RAIZ, f)):
            mal("falta el fichero", f)

    sm = io.open(os.path.join(RAIZ, "sitemap.xml"), encoding="utf-8").read()
    if "/gracias/" in sm:
        mal("/gracias/ está en el sitemap y no debería")
    for url in urls:
        if url == "/gracias/":
            continue
        if SITIO + url not in sm:
            mal("falta en el sitemap", url)

    print("   %d páginas revisadas" % len(paginas_html))


# ==========================================================================
# B. En Chrome de verdad
# ==========================================================================

MEDIDA = """
<script>
(function(){
  var r = {contrastes: [], desborde: null, errores: [], cookies: null, h1: null};

  function lum(c){
    var m = (c.match(/[\\d.]+/g)||[0,0,0]).slice(0,3).map(Number).map(function(x){
      x = x/255; return x <= 0.03928 ? x/12.92 : Math.pow((x+0.055)/1.055, 2.4); });
    return 0.2126*m[0] + 0.7152*m[1] + 0.0722*m[2];
  }
  /* El fondo real de un elemento. Ojo con los degradados: van en
     background-image, no en backgroundColor, y si solo se mira el segundo
     un boton con degradado parece transparente y se acaba comparando el
     texto contra el fondo de la seccion. Eso daba 1.00 y era mentira.
     Con degradado se sacan TODOS sus colores y se devuelve el peor para
     ese texto, que es el que manda. */
  function fondosDe(e, colorTexto){
    var lt = lum(colorTexto);
    while (e && e !== document.documentElement) {
      var cs = getComputedStyle(e);
      var img = cs.backgroundImage || '';
      // Un degradado RECORTADO AL TEXTO (background-clip: text) no es un
      // fondo: es la propia letra pintada. Compararlo con el color del texto
      // da 1.00 y es mentira. Se salta y se sigue subiendo a buscar el fondo
      // de verdad. Lo cazo el efecto laser de las cifras el 13/09/2026.
      var recorte = cs.backgroundClip || cs.webkitBackgroundClip || '';
      if (recorte === 'text') img = '';
      if (img.indexOf('gradient') !== -1) {
        var paradas = img.match(/rgba?\\([^)]+\\)/g) || [];
        paradas = paradas.filter(function(c){
          var a = (c.match(/[\\d.]+/g)||[])[3];
          return a === undefined || Number(a) > 0.5; });
        if (paradas.length) {
          // el peor = el que menos se distingue del texto
          return paradas.sort(function(x, y){
            return Math.abs(lum(x)-lt) - Math.abs(lum(y)-lt); })[0];
        }
      }
      var c = cs.backgroundColor;
      if (c && c !== 'rgba(0, 0, 0, 0)' && c !== 'transparent') {
        var a = (c.match(/[\\d.]+/g)||[])[3];
        if (a === undefined || Number(a) > 0.5) return c;
      }
      e = e.parentElement;
    }
    return 'rgb(255, 255, 255)';
  }
  function ratio(fg, bg){
    var a = lum(fg), b = lum(bg), hi = Math.max(a,b), lo = Math.min(a,b);
    return Math.round(((hi+0.05)/(lo+0.05))*100)/100;
  }

  // Contraste de TODO el texto visible
  var vistos = {};
  [].slice.call(document.querySelectorAll('body *')).forEach(function(e){
    if (!e.firstChild) return;
    var suyo = [].slice.call(e.childNodes).some(function(n){
      return n.nodeType === 3 && n.textContent.trim().length > 1; });
    if (!suyo) return;
    var cs = getComputedStyle(e);
    if (cs.display === 'none' || cs.visibility === 'hidden' || +cs.opacity === 0) return;
    if (e.closest('[aria-hidden="true"]')) return;
    var fondo = fondosDe(e, cs.color);
    var tam = parseFloat(cs.fontSize);
    var grande = tam >= 24 || (tam >= 18.66 && +cs.fontWeight >= 700);
    var pide = grande ? 3 : 4.5;
    var v = ratio(cs.color, fondo);
    var clave = cs.color + '|' + fondo + '|' + pide;
    if (vistos[clave]) return;
    vistos[clave] = 1;
    r.contrastes.push({
      etiqueta: e.tagName.toLowerCase() + (e.className && typeof e.className === 'string'
                 ? '.' + e.className.split(' ')[0] : ''),
      texto: (e.textContent||'').trim().slice(0,34),
      color: cs.color, fondo: fondo, tam: Math.round(tam*10)/10,
      pide: pide, ratio: v, ok: v >= pide
    });
  });

  // ¿Se desborda a lo ancho?
  r.desborde = {
    documento: document.documentElement.scrollWidth,
    ventana: window.innerWidth,
    se_desborda: document.documentElement.scrollWidth > window.innerWidth + 1
  };

  r.h1 = document.querySelectorAll('h1').length;

  // El aviso de cookies
  var caja = document.getElementById('cookies');
  r.cookies = {
    sale: !!caja,
    botones: caja ? [].slice.call(caja.querySelectorAll('[data-cookies]'))
                      .map(function(b){ return b.textContent.trim(); }) : [],
    consentDenegado: (window.dataLayer||[]).some(function(x){
      return x && x[0] === 'consent' && x[1] === 'default' && x[2] &&
             x[2].analytics_storage === 'denied'; }),
    medicionCargada: !!document.querySelector('script[src*="googletagmanager"]')
  };

  // Pulsar Rechazar y comprobar que se va y NO carga medicion
  if (caja) {
    var no = caja.querySelector('[data-cookies="no"]');
    if (no) no.click();
  }
  setTimeout(function(){
    r.cookies.tras_rechazar = {
      sigue: !!document.getElementById('cookies'),
      medicion: !!document.querySelector('script[src*="googletagmanager"]')
    };
    var pre = document.createElement('pre');
    pre.id = 'RESULTADOS';
    pre.textContent = JSON.stringify(r);
    document.body.appendChild(pre);
  }, 500);
})();
</script>
"""


_COPIA = {"dir": None}


def _preparar():
    """Copia la web a un temporal UNA sola vez y le empalma la medida a cada
    pagina. Antes se copiaba por cada pagina y cada tamano —18 veces— y con la
    maquina ocupada uno de los Chrome se pasaba de los 150 s y se llevaba por
    delante la auditoria entera."""
    if _COPIA["dir"]:
        return _COPIA["dir"]
    tmp = tempfile.mkdtemp(prefix="aud-")
    destino = os.path.join(tmp, "web")
    shutil.copytree(RAIZ, destino, ignore=shutil.ignore_patterns(
        "_web", ".git", "despliegue", "*.md"))
    for url, _t, _d, _c, _r in paginas.TODAS:
        rel = "index.html" if url == "/" else os.path.join(url.strip("/"), "index.html")
        p = os.path.join(destino, rel)
        h = io.open(p, encoding="utf-8").read()
        h = h.replace('<script src="/web.js" defer></script>',
                      '<script src="%s/web.js"></script>' % destino.replace("\\", "/"))
        io.open(p, "w", encoding="utf-8", newline="\n").write(h + MEDIDA)
    _COPIA["dir"] = destino
    return destino


def en_chrome(url, ancho, alto, intento=1):
    destino = _preparar()
    rel = "index.html" if url == "/" else os.path.join(url.strip("/"), "index.html")
    p = os.path.join(destino, rel)
    perfil = tempfile.mkdtemp(prefix="perf-")
    try:
        out = subprocess.run(
            [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
             "--hide-scrollbars", "--user-data-dir=" + perfil,
             "--window-size=%d,%d" % (ancho, alto),
             "--virtual-time-budget=15000", "--dump-dom",
             "file:///" + p.replace("\\", "/")],
            capture_output=True, timeout=180)
    except subprocess.TimeoutExpired:
        shutil.rmtree(perfil, ignore_errors=True)
        if intento < 3:
            # La maquina puede estar cargada: se reintenta antes de acusar a
            # la web de algo que no ha hecho.
            print("      (Chrome se atasco en %s, reintento %d)" % (url, intento + 1))
            return en_chrome(url, ancho, alto, intento + 1)
        mal("Chrome no responde despues de 3 intentos", url)
        return None
    shutil.rmtree(perfil, ignore_errors=True)
    dom = out.stdout.decode("utf-8", "replace")
    m = re.search(r'<pre id="RESULTADOS">(.*?)</pre>', dom, re.S)
    if not m:
        return None
    return json.loads(m.group(1).replace("&quot;", '"').replace("&lt;", "<")
                      .replace("&gt;", ">").replace("&amp;", "&"))


def parte_b():
    print("\n=== B. Lo que solo se ve ejecutándolo (Chrome) ===")
    if not os.path.exists(CHROME):
        ojo("no encuentro Chrome: la parte B no se ha ejecutado", CHROME)
        return

    for url, _t, _d, _c, _r in paginas.TODAS:
        for nombre, ancho, alto in (("móvil", 390, 850), ("escritorio", 1280, 900)):
            r = en_chrome(url, ancho, alto)
            if r is None:
                mal("el arnés no dejó resultados (¿falla el guion?)",
                    "%s en %s" % (url, nombre))
                continue

            malos = [c for c in r["contrastes"] if not c["ok"]]
            for c in malos:
                mal("contraste %.2f (hace falta %.1f) en %s «%s»"
                    % (c["ratio"], c["pide"], c["etiqueta"], c["texto"]),
                    "%s · %s" % (url, nombre))

            if r["desborde"]["se_desborda"]:
                mal("la página se desborda a lo ancho: %d px de contenido en "
                    "%d px de pantalla" % (r["desborde"]["documento"],
                                           r["desborde"]["ventana"]),
                    "%s · %s" % (url, nombre))

            if r["h1"] != 1:
                mal("%d <h1> al pintarla" % r["h1"], url)

            ck = r["cookies"]
            if not ck["sale"]:
                mal("el aviso de cookies no sale", "%s · %s" % (url, nombre))
            elif len(ck["botones"]) != 2:
                mal("el aviso no tiene dos botones: %s" % ck["botones"], url)
            if not ck["consentDenegado"]:
                mal("no se declara el consentimiento como denegado antes de nada", url)
            if ck["medicionCargada"]:
                mal("la medición se carga SIN consentimiento", url)
            tras = ck.get("tras_rechazar") or {}
            if tras.get("sigue"):
                mal("el aviso no se va al pulsar Rechazar", url)
            if tras.get("medicion"):
                mal("carga la medición DESPUÉS DE RECHAZAR", url)

        print("   %-34s móvil y escritorio" % url)


# ==========================================================================

def main():
    parte_a()
    parte_b()

    if _COPIA["dir"]:
        shutil.rmtree(os.path.dirname(_COPIA["dir"]), ignore_errors=True)

    print("\n" + "=" * 66)
    if avisos:
        print("AVISOS (no rompen nada, pero conviene mirarlos):")
        for a in avisos:
            print("  - " + a)
        print()
    if fallos:
        print("FALLOS: %d" % len(fallos))
        for f in fallos:
            print("  MAL " + f)
        return 1
    print("FALLOS: 0 — la web pasa la auditoría")
    return 0


if __name__ == "__main__":
    sys.exit(main())
