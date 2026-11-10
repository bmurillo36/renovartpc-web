# Añade a cada <url> del sitemap.xml las imágenes de su página (<image:image>), para Google Imágenes.
# Repetible: quita las que hubiera y las vuelve a poner. Mete la og:image y las <img> con alt (sin
# logos ni iconos), máx. 10 por URL, solo del propio dominio y que EXISTEN en disco.
# La dirección de la web la saca del primer <loc>.
#   python3 sitemap_imagenes.py [raiz_de_la_web]      (raíz por defecto: la carpeta actual)
# o desde un generador:  import sitemap_imagenes; sitemap_imagenes.poner(RAIZ)
# Modelo: prevencionmadrid-web/_blog/sitemap-imagenes.py (19/10/2026). Este, 10/11/2026.
import os, re, sys, urllib.parse

NS = 'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"'
EXT = re.compile(r'\.(?:webp|jpe?g|png|gif|avif|svg)$', re.I)  # los formatos que indexa Google Imágenes


def _pagina(raiz, ruta):
    ruta = ruta.strip('/')
    for f in ([os.path.join(raiz, ruta, 'index.html'), os.path.join(raiz, ruta + '.html'), os.path.join(raiz, ruta)]
              if ruta else [os.path.join(raiz, 'index.html')]):
        if os.path.isfile(f) and (f.endswith('.html') or f.endswith('.htm')):
            return f


def _imagenes(raiz, loc, web):
    url = urllib.parse.urlparse(loc)
    f = _pagina(raiz, urllib.parse.unquote(url.path))
    if not f:
        return []
    host = url.netloc.lower().removeprefix('www.')
    vistas = []
    html = open(f, encoding='utf-8', errors='replace').read()
    # La imagen de compartir (og:image) y las <img> con alt (las de alt="" son adorno).
    fuentes = [re.search(r'\scontent\s*=\s*["\']([^"\']+)', m).group(1)
               for m in re.findall(r'<meta\b[^>]*>', html, re.I)
               if re.search(r'property\s*=\s*["\']og:image["\']', m, re.I) and re.search(r'\scontent\s*=', m)]
    for img in re.findall(r'<img\b[^>]*>', html, re.I):
        src = re.search(r'\ssrc\s*=\s*["\']([^"\'>]+)["\']', img, re.I)
        alt = re.search(r'\salt\s*=\s*["\']([^"\']*)["\']', img, re.I)
        if src and alt and alt.group(1).strip():
            fuentes.append(src.group(1))
    for src in fuentes:
        src = src.strip()
        if src.startswith('data:'):
            continue
        u = urllib.parse.urlparse(urllib.parse.urljoin(loc, src))
        if u.netloc.lower().removeprefix('www.') != host:
            continue
        ruta = urllib.parse.unquote(u.path)
        if not EXT.search(ruta) or re.search(r'logo|favicon|icon', ruta, re.I) or ruta in vistas:
            continue
        if os.path.isfile(os.path.join(raiz, ruta.lstrip('/'))):
            vistas.append(ruta)
    return [web + urllib.parse.quote(r, safe='/') for r in vistas[:10]]


def poner(raiz='.', sitemap='sitemap.xml'):
    p = os.path.join(raiz, sitemap)
    sm = open(p, encoding='utf-8', newline='').read()
    sm = re.sub(r'\s*<image:image>.*?</image:image>', '', sm, flags=re.S)
    if NS not in sm:
        sm = re.sub(r'<urlset\b', '<urlset ' + NS, sm, count=1)
    primero = re.search(r'<loc>\s*([^<\s]+)', sm)
    if not primero:
        return 0
    u = urllib.parse.urlparse(primero.group(1))
    web = '%s://%s' % (u.scheme, u.netloc)
    n = 0

    def una(m):
        nonlocal n
        imgs = _imagenes(raiz, m.group(2).strip(), web)
        n += len(imgs)
        return m.group(1) + ''.join('<image:image><image:loc>%s</image:loc></image:image>' % i
                                    for i in imgs) + m.group(3)

    sm = re.sub(r'(<url>\s*<loc>([^<]+)</loc>.*?)(\s*</url>)', una, sm, flags=re.S)
    open(p, 'w', encoding='utf-8', newline='').write(sm)
    print('imágenes en el sitemap:', n)
    return n


if __name__ == '__main__':
    poner(sys.argv[1] if len(sys.argv) > 1 else '.')
