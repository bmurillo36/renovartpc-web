# -*- coding: utf-8 -*-
"""
El contenido de renovartpc.es, página a página.

Cada función devuelve (cuerpo, extra_head). El «extra» es lo que va en la
cabecera de esa página y solo de esa: los datos estructurados, sobre todo.

=============================================================================
LA REGLA DE ORO: el curso de reciclaje de 4 horas de construcción NO EXISTE.
=============================================================================
Ni una frase de este fichero puede dar a entender lo contrario. Nada de
«próximamente», nada de fechas, nada de «ya puedes reservar». Lo que sí se
hace es contar la verdad de hoy y ofrecer una lista de aviso por si algún día
el convenio lo aprueba. Ver CLAUDE.md y `centro.py`.
=============================================================================

REGLA AL ESCRIBIR AQUÍ: ni un dato inventado. Lo que regula el convenio sale
del portal oficial de la TPC y va con su artículo; lo del centro lo dictó
Pedro. Lo que no se sabe no se pone: en `centro.py` hay `# PENDIENTE PEDRO`
donde falta su confirmación, y aquí eso se traduce en «pídenos precio», no en
un número inventado.
"""

import json

from centro import (SITIO, CENTRO, TEL_E164, TARJETA, BOE_CADUCIDAD,
                    DOCUMENTACION, DOCUMENTACION_UNO_DE, REGIMENES, PLAZOS,
                    DONDE, DERECHOS, RECICLAJE_4H, CATALOGO, REGLAS_CENTRO,
                    PREGUNTAS, HORARIO, HORARIO_NOTA, FORMULARIO,
                    WASAP, WASAP_TEXTO, MAPA)

MENU = [
    ("/", "Inicio"),
    ("/renovar-la-tpc/", "Renovar"),
    ("/tpc-caducada/", "Caducada"),
    ("/curso-reciclaje-4-horas/", "Reciclaje 4 h"),
    ("/cursos/", "Cursos"),
]

TEL1 = CENTRO["telefonos"][0]

# Las webs hermanas del centro. Se enlazan desde el texto, donde vienen a
# cuento, no en una lista de enlaces al final: así sirven de algo.
# reciclajemetal.es NO se enlaza todavía (Pedro, 16/09/2026).
HERMANAS = {
    "prevencionmadrid": '<a href="https://prevencionmadrid.es" rel="noopener">prevencionmadrid.es</a>',
    "cursotpc": '<a href="https://curso-tpc.es" rel="noopener">curso-tpc.es</a>',
    "tpc20": '<a href="https://tpc20horas.es" rel="noopener">tpc20horas.es</a>',
    "tpc60": '<a href="https://tpc60horas.es" rel="noopener">tpc60horas.es</a>',
    "metal": '<a href="https://tpcmetal.es" rel="noopener">tpcmetal.es</a>',
}


# --- Piezas que se repiten -------------------------------------------------

def _tic():
    return ('<svg width="18" height="18" viewBox="0 0 24 24" fill="none" '
            'stroke="#3F6759" stroke-width="2.6" stroke-linecap="round" '
            'stroke-linejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>')


def _botonera(principal="Preguntar sin compromiso", href="/contacto/"):
    return (
        '<div class="botonera">'
        '<a class="btn btn--cta" href="%s">%s</a>'
        '<a class="btn btn--linea" href="tel:%s">Llamar al %s</a>'
        '</div>' % (href, principal, TEL_E164[TEL1], TEL1))


# Las opciones del desplegable `Curso` del formulario. El servicio solo
# entrega SIETE campos, y `Curso` es el único libre que queda: por eso lleva
# el motivo de la consulta y no solo un nombre de curso.
OPCIONES = [
    ("Renovación de la TPC", "Tengo una duda sobre la renovación"),
    ("TPC caducada", "La tengo caducada"),
    ("Duplicado de la TPC", "Me la han robado o la he perdido"),
    ("Lista de aviso · reciclaje 4 h construcción",
     "Avisadme si sale el reciclaje de 4 horas"),
    ("Curso del catálogo de construcción", "Quiero hacer un curso"),
]

OPCIONES_AVISO = [
    ("Lista de aviso · reciclaje 4 h construcción",
     "Avisadme si sale el reciclaje de 4 horas"),
    ("Renovación de la TPC", "Tengo una duda sobre la renovación"),
    ("Curso del catálogo de construcción", "Quiero hacer un curso"),
]


def _formulario(titulo="Pregunta lo que necesites", ruta="/", opciones=None,
                lateral=None, aviso=None):
    """El formulario. Va al servicio propio de Pedro; ver centro.py.

    `ruta` es la pagina en la que se pinta, y solo sirve para el campo Origen:
    asi se sabe DESDE QUE PAGINA escribio cada persona. Esta web no tiene
    Analytics (la gestora no le ha asignado contenedor), asi que ese campo es
    hoy la unica forma de saberlo.
    """
    ops = "".join('<option value="%s">%s</option>' % (v, t)
                  for v, t in (opciones or OPCIONES))
    return """
<section class="seccion seccion--menta" id="pedir">
  <div class="wrap">
    <div class="rejilla rejilla--2">
      <div class="aparece">
        <p class="rotulo">Hablamos</p>
        <h2>%(titulo)s</h2>
        <p class="entradilla">%(lateral)s</p>
        <div class="botonera">
          <a class="btn btn--salvia" href="tel:%(tel_e)s">Llamar al %(tel)s</a>
          <a class="btn btn--linea" href="https://wa.me/%(wasap)s?text=%(wtexto)s"
             rel="noopener">WhatsApp</a>
        </div>
        <div class="aviso">
          <p>%(aviso)s</p>
        </div>
      </div>

      <div class="form-caja aparece" data-orden="1">
        <!-- ================================================================
             OJO CON LOS NOMBRES DE LOS CAMPOS: van con INICIAL MAYÚSCULA y son
             EXACTAMENTE estos siete, ni uno más:

                 Nombre · Email · Telefono · Curso · Mensaje · Acepto · Origen

             Están en `CAMPOS` de servidor.py y el servicio NO normaliza
             mayúsculas. Un campo con otro nombre —`nombre`, `correo`,
             `consentimiento`— no es que llegue mal: es que NO LLEGA. El
             servicio se queda solo con esos siete y tira el resto, y como sin
             Nombre no hay envío válido, devuelve un 400 y el cliente se pierde.

             Y el ORDEN importa igual: el lector del CRM usa `Acepto` para saber
             dónde acaba el mensaje. Ver [[circuito-formularios-crm]].

             Los campos que empiezan por guion bajo SÍ son del servicio y se
             quedan: `_honey` (trampa antispam), `_t` (sello de JavaScript),
             `_next` (a dónde se va después, y el servicio comprueba que sea de
             esta misma web).
             ================================================================ -->
        <form class="form" method="post" action="%(accion)s">
          <input type="hidden" name="_next" value="%(sitio)s/gracias/">
          <input type="hidden" name="_t" value="">
          <input type="hidden" name="Origen" value="renovartpc.es%(ruta)s">
          <p style="position:absolute;left:-9999px" aria-hidden="true">
            <label>No rellenar <input type="text" name="_honey" tabindex="-1" autocomplete="off"></label>
          </p>

          <div class="campo">
            <label for="nombre">Nombre y apellidos <span class="obl">*</span></label>
            <input id="nombre" name="Nombre" type="text" required autocomplete="name"
                   maxlength="80" placeholder="Como aparece en tu DNI">
          </div>
          <div class="campo">
            <label for="telefono">Teléfono <span class="obl">*</span></label>
            <input id="telefono" name="Telefono" type="tel" required autocomplete="tel"
                   inputmode="tel" maxlength="20" placeholder="600 00 00 00">
            <span class="pista">Es por donde te contestamos.</span>
          </div>
          <div class="campo">
            <label for="correo">Correo electrónico</label>
            <input id="correo" name="Email" type="email" autocomplete="email"
                   maxlength="90" placeholder="opcional">
          </div>
          <div class="campo">
            <label for="motivo">¿Qué necesitas?</label>
            <select id="motivo" name="Curso">%(ops)s</select>
          </div>
          <div class="campo">
            <label for="mensaje">Cuéntanos</label>
            <textarea id="mensaje" name="Mensaje" maxlength="900"
              placeholder="Si te lo pide una obra o una empresa concreta, dínoslo: así te decimos exactamente qué te están pidiendo."></textarea>
          </div>
          <label class="consentimiento">
            <input type="checkbox" name="Acepto" value="si" required>
            <span>He leído la <a href="/politica-de-privacidad/">política de
            privacidad</a> y acepto que uséis mis datos para responderme.</span>
          </label>
          <button type="submit" class="btn btn--cta">Enviar</button>
          <p class="form__aviso">Solo lo usamos para contestarte. Ni lo vendemos
          ni te apuntamos a ninguna lista de publicidad.</p>
        </form>
      </div>
    </div>
  </div>
</section>""" % {
        "titulo": titulo, "accion": FORMULARIO, "sitio": SITIO,
        "ruta": ruta, "ops": ops,
        "lateral": lateral or ("Déjanos el teléfono y te contestamos nosotros. Si "
                               "tienes prisa, llamar es más rápido: la mayoría de "
                               "las dudas de la renovación se resuelven en la misma "
                               "llamada."),
        "aviso": aviso or ("<strong>Preguntar no cuesta nada y no hay que comprar "
                           "nada.</strong> La renovación de la tarjeta se tramita en "
                           "la Fundación Laboral, no aquí. Aun así te decimos qué "
                           "papeles necesitas."),
        "tel": TEL1, "tel_e": TEL_E164[TEL1],
        "wasap": WASAP, "wtexto": WASAP_TEXTO}


def _ld(*bloques):
    return "".join('<script type="application/ld+json">%s</script>\n'
                   % json.dumps(b, ensure_ascii=False, separators=(",", ":"))
                   for b in bloques)


def _centro_ld():
    return {
        "@context": "https://schema.org",
        "@type": ["EducationalOrganization", "LocalBusiness"],
        "@id": SITIO + "/#centro",
        "name": "Prevención Siglo 21 — Centro de formación",
        "legalName": CENTRO["empresa"],
        "url": SITIO,
        "telephone": [TEL_E164[t] for t in CENTRO["telefonos"]],
        "email": CENTRO["correo"],
        "address": {
            "@type": "PostalAddress",
            "streetAddress": CENTRO["direccion"],
            "postalCode": CENTRO["cp"],
            "addressLocality": CENTRO["ciudad"],
            "addressRegion": CENTRO["provincia"],
            "addressCountry": "ES",
        },
        "areaServed": {"@type": "AdministrativeArea", "name": "Comunidad de Madrid"},
        "identifier": [
            {"@type": "PropertyValue",
             "name": "Acreditación de la Comunidad de Madrid",
             "value": CENTRO["acreditacion_cm"]},
            {"@type": "PropertyValue",
             "name": "Homologación de la Fundación Laboral de la Construcción",
             "value": CENTRO["homologacion_flc"]},
        ],
        "openingHoursSpecification": [
            {"@type": "OpeningHoursSpecification",
             "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday"],
             "opens": "08:00", "closes": "18:00"},
            {"@type": "OpeningHoursSpecification",
             "dayOfWeek": "Friday", "opens": "08:00", "closes": "15:00"},
        ],
    }


def _sin_etiquetas(txt):
    """Los datos estructurados no llevan HTML: el <strong> de un texto de la
    web, copiado tal cual a un JSON-LD, sale impreso en el resultado de Google
    como `<strong>`. Se quita aqui y no a mano, que es donde se olvida."""
    fuera, dentro = [], False
    for c in txt:
        if c == "<":
            dentro = True
        elif c == ">":
            dentro = False
        elif not dentro:
            fuera.append(c)
    return "".join(fuera)


def _howto_ld():
    """El trámite de renovación, en formato HowTo. Lo que se describe es el
    procedimiento OFICIAL de la Fundación Laboral, no un servicio del centro:
    por eso no lleva `offers` ni precio. Poner un precio aquí sería dar a
    entender que la renovación se compra, y no se compra."""
    pasos = [
        ("Comprueba la fecha de caducidad de tu tarjeta",
         "La TPC caduca a los cinco años de su emisión (artículo 161 del VII "
         "Convenio General del Sector de la Construcción). La fecha está "
         "impresa en la propia tarjeta. Si ya ha pasado, se puede renovar "
         "igualmente."),
        ("Pide el informe de vida laboral",
         "Tiene que estar emitido dentro de los 90 días anteriores a la "
         "solicitud. Si es más antiguo, no vale y te lo requerirán."),
        ("Reúne el resto de la documentación",
         "Impreso de solicitud de renovación, una foto tamaño carnet y "
         "fotocopia del DNI o NIE. Y al menos uno de estos: certificado de "
         "empresa para la Fundación Laboral (Anexo VI), certificado de empresa "
         "para el Servicio Público de Empleo, recibos de salarios o contrato "
         "de trabajo."),
        ("Entrégalo en un punto de tramitación",
         "Centros de la Fundación Laboral de la Construcción, sedes de las "
         "asociaciones de la CNC, sedes de CCOO del Hábitat o de UGT FICA."),
        ("Espera la tarjeta",
         "La entrega tarda un mes como máximo desde que la documentación está "
         "correcta. Si falta algo, tienes 10 días para subsanarlo."),
    ]
    return {
        "@context": "https://schema.org",
        "@type": "HowTo",
        "@id": SITIO + "/renovar-la-tpc/#howto",
        "name": "Cómo renovar la Tarjeta Profesional de la Construcción",
        "description": ("El procedimiento de renovación de la TPC: es el mismo "
                        "que el de la solicitud inicial excepto la formación en "
                        "prevención, que no se exige."),
        "inLanguage": "es",
        "totalTime": "P1M",
        "supply": [{"@type": "HowToSupply", "name": _sin_etiquetas(t)}
                   for t, _d in DOCUMENTACION],
        "step": [{"@type": "HowToStep", "position": i + 1, "name": t,
                  "text": d, "url": SITIO + "/renovar-la-tpc/#paso-%d" % (i + 1)}
                 for i, (t, d) in enumerate(pasos)],
    }


def _cursos_ld():
    """Un Course por cada curso del catálogo que el centro imparte de verdad.
    Los que no tienen precio confirmado por Pedro salen SIN `offers`: es mejor
    no declarar precio que declarar uno inventado, porque Google lo enseña."""
    fuera = []
    for nombre, horas, precio, _que in CATALOGO:
        c = {
            "@context": "https://schema.org",
            "@type": "Course",
            "name": "%s (%d horas) — construcción" % (nombre, horas),
            "description": _sin_etiquetas(_que),
            "url": SITIO + "/cursos/",
            "inLanguage": "es",
            "provider": {"@id": SITIO + "/#centro"},
            "hasCourseInstance": {
                "@type": "CourseInstance",
                "courseMode": "Onsite",
                "courseWorkload": "PT%dH" % horas,
                "location": {
                    "@type": "Place",
                    "name": "Prevención Siglo 21 — Móstoles",
                    "address": {
                        "@type": "PostalAddress",
                        "streetAddress": CENTRO["direccion"],
                        "postalCode": CENTRO["cp"],
                        "addressLocality": CENTRO["ciudad"],
                        "addressCountry": "ES",
                    },
                },
            },
        }
        if precio:
            c["offers"] = {"@type": "Offer", "price": str(precio),
                           "priceCurrency": "EUR", "category": "Formación",
                           "url": SITIO + "/contacto/",
                           "availability": "https://schema.org/LimitedAvailability"}
        fuera.append(c)
    return fuera


def _faq_ld(pares):
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": _sin_etiquetas(p),
             "acceptedAnswer": {"@type": "Answer", "text": _sin_etiquetas(r)}}
            for p, r in pares],
    }


def _migas(*pares):
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n,
             "item": SITIO + u} for i, (n, u) in enumerate(pares)],
    }


def _preguntas_html(pares):
    return "".join(
        '<details class="pregunta"><summary>%s</summary>'
        '<div class="pregunta__cuerpo"><p>%s</p></div></details>' % (p, r)
        for p, r in pares)


def _aviso_reciclaje(enlace=True):
    """El bloque honesto sobre el reciclaje de 4 horas. Se repite en varias
    páginas A PROPÓSITO: es el punto donde más gente llega equivocada, y donde
    más fácil sería colar una mentira rentable."""
    mas = ('  <p><a href="/curso-reciclaje-4-horas/">Te lo contamos entero '
           'aquí</a>, incluida la lista de aviso.</p>') if enlace else ""
    return """
<div class="aviso aparece" data-orden="1">
  <p><strong>¿Y el «curso de reciclaje de 4 horas»?</strong> Hoy no existe en
  construcción. El convenio no exige formación para renovar la tarjeta, y en el
  catálogo de construcción no hay ningún curso de reciclaje ni de renovación de
  4 horas. Preferimos decírtelo antes de que pagues por algo que no te van a
  pedir.</p>
%s
</div>""" % mas


# --- Las páginas -----------------------------------------------------------

def portada():
    cifras = [
        ("5 años", "dura la tarjeta"),
        ("0 horas", "de formación para renovar"),
        ("90 días", "de antigüedad máxima de la vida laboral"),
        ("1 mes", "máximo para entregártela"),
    ]
    html_cifras = "".join(
        '<div class="linterna"><span class="cifra__n">%s</span>'
        '<span class="cifra__t">%s</span></div>' % (n, t) for n, t in cifras)

    resumen = [
        ("Caduca a los cinco años",
         "Artículo 161 del VII Convenio General del Sector de la Construcción."),
        ("Se renueva con papeles, no con clase",
         "El mismo procedimiento que la solicitud inicial, excepto la formación."),
        ("Caducada también se renueva",
         "No la has perdido y el portal oficial no describe ninguna sanción."),
        ("La emite la Fundación Laboral",
         "Se entrega en sus centros y en los de CCOO del Hábitat, UGT FICA y la CNC."),
    ]
    html_resumen = "".join(
        '<li>%s<span><strong>%s.</strong> %s</span></li>' % (_tic(), t, d)
        for t, d in resumen)

    pasos = [
        ("Mira la fecha de tu tarjeta",
         "Está impresa en ella. Cinco años desde que se emitió."),
        ("Pide la vida laboral",
         "Y hazlo cerca de la fecha: solo vale si se emitió en los 90 días "
         "anteriores a la solicitud."),
        ("Junta los papeles y entrégalos",
         "Impreso de renovación, foto, DNI o NIE, vida laboral y una prueba de "
         "que trabajas en el sector."),
        ("Recoge la tarjeta",
         "Un mes como máximo desde que la documentación está correcta."),
    ]
    html_pasos = "".join(
        '<article class="tarjeta%s aparece" data-orden="%d">'
        '<span class="tarjeta__num">%d</span><h3>%s</h3><p>%s</p></article>'
        % (" tarjeta--acento" if i == 3 else "", i, i + 1, t, d)
        for i, (t, d) in enumerate(pasos))

    # Solo cuatro del catálogo en la portada: los que más se piden. El resto
    # está en /cursos/, para no convertir la portada en un folleto.
    destacados = "".join(
        '<article class="tarjeta linterna aparece" data-orden="%d">'
        '<h3>%s · %d horas</h3><p>%s</p><p><strong>%s</strong></p></article>'
        % (i, n, h, q, ("%d €" % p) if p else "Pídenos precio")
        for i, (n, h, p, q) in enumerate(
            [c for c in CATALOGO if c[1] in (8, 20, 6, 60)][:4]))

    seis = _preguntas_html(PREGUNTAS[:6])

    cuerpo = """
<section class="hero">
  <div class="wrap hero__in">
    <div class="hero__grid">
      <div>
        <span class="sello"><span class="sello__punto"></span>Tarjeta Profesional de la Construcción</span>
        <h1>Renovar la <em>TPC</em>: lo que hay que hacer de verdad</h1>
        <p class="entradilla">Tu tarjeta caduca a los cinco años. La buena
        noticia es que renovarla <strong>no exige volver a formarse</strong>:
        es un trámite de papeles ante la Fundación Laboral de la Construcción.
        Aquí está el trámite entero, sin humo y sin venderte nada.</p>
        %(botonera)s
      </div>

      <aside class="ficha ficha--luz linterna aparece" data-orden="1">
        <p class="rotulo">En cuatro líneas</p>
        <ul class="ficha__lista">%(resumen)s</ul>
      </aside>
    </div>
  </div>
</section>

<section class="cifras">
  <div class="wrap">
    <div class="cifras__grid">%(cifras)s</div>
  </div>
</section>

<section class="seccion seccion--crema">
  <div class="wrap">
    <div class="cabecera-seccion aparece">
      <p class="rotulo">Lo primero</p>
      <h2>Para renovar la TPC no hace falta ningún curso</h2>
      <p class="entradilla">El portal oficial de la tarjeta lo dice con estas
      palabras: la renovación sigue el mismo procedimiento que la solicitud
      inicial <em>«excepto la formación en prevención»</em>. Es decir, la
      formación que hiciste en su día no se repite.</p>
    </div>
    %(reciclaje)s
  </div>
</section>

<section class="seccion seccion--papel">
  <div class="wrap">
    <div class="cabecera-seccion aparece">
      <p class="rotulo">Cómo va</p>
      <h2>El trámite, en cuatro pasos</h2>
    </div>
    <div class="rejilla rejilla--4">%(pasos)s</div>
    <div class="botonera">
      <a class="btn btn--linea" href="/renovar-la-tpc/">Ver el trámite con todo el detalle</a>
    </div>
  </div>
</section>

<section class="seccion seccion--menta">
  <div class="wrap">
    <div class="rejilla rejilla--2">
      <div class="aparece">
        <h2>¿La tienes caducada?</h2>
        <p>No has perdido nada. Quien tiene la tarjeta caducada
        <strong>puede solicitar la renovación</strong>, con los mismos papeles.
        El portal oficial no describe ninguna sanción por haberla dejado
        caducar.</p>
        <p>Y si lo que ha pasado es que te la han robado, la has perdido o está
        destrozada, entonces no es una renovación: es un <strong>duplicado</strong>,
        que se pide mostrando el DNI y que <strong>conserva la fecha de
        caducidad original</strong>. No confundas una cosa con la otra.</p>
        <div class="botonera">
          <a class="btn btn--salvia" href="/tpc-caducada/">Tarjeta caducada, robada o perdida</a>
        </div>
      </div>
      <div class="aparece" data-orden="1">
        <h2>¿Y si mi tarjeta es antigua?</h2>
        <p>Hasta el BOE del %(boe)s existía una disposición transitoria que
        tenía la caducidad suspendida. Se eliminó. Desde entonces todas las
        tarjetas caducan a los cinco años de su emisión.</p>
        <p>Si la tuya es de antes y nunca te preocupó la fecha, míralo ahora:
        es el motivo número uno por el que alguien se planta en la obra con una
        tarjeta que no vale.</p>
      </div>
    </div>
  </div>
</section>

<section class="seccion seccion--papel">
  <div class="wrap">
    <div class="cabecera-seccion aparece">
      <p class="rotulo">Formación</p>
      <h2>Los cursos que sí existen, y que damos aquí</h2>
      <p class="entradilla">Para <em>sacar</em> la tarjeta por primera vez sí
      hace falta formación. Para renovarla, no. Somos centro homologado por la
      Fundación Laboral de la Construcción con el número %(flc)s y damos el
      catálogo de construcción en nuestras aulas de Móstoles.</p>
    </div>
    <div class="rejilla rejilla--4">%(destacados)s</div>
    <div class="botonera">
      <a class="btn btn--linea" href="/cursos/">Todos los cursos y sus horas</a>
    </div>
  </div>
</section>

<section class="seccion seccion--crema">
  <div class="wrap">
    <div class="cabecera-seccion aparece">
      <p class="rotulo">Dudas</p>
      <h2>Lo que más nos preguntan por teléfono</h2>
    </div>
    %(seis)s
    <div class="botonera">
      <a class="btn btn--linea" href="/preguntas-frecuentes/">Las quince preguntas</a>
    </div>
  </div>
</section>
%(formulario)s""" % {
        "botonera": _botonera(), "resumen": html_resumen, "cifras": html_cifras,
        "reciclaje": _aviso_reciclaje(), "pasos": html_pasos,
        "destacados": destacados, "seis": seis, "boe": BOE_CADUCIDAD,
        "flc": CENTRO["homologacion_flc"],
        "formulario": _formulario(ruta="/")}

    return cuerpo, _ld(_centro_ld(), _howto_ld())


def renovar():
    docs = "".join(
        '<li>%s<span><strong>%s.</strong> %s</span></li>' % (_tic(), t, d)
        for t, d in DOCUMENTACION)
    uno_de = "".join('<li>%s<span>%s</span></li>' % (_tic(), x)
                     for x in DOCUMENTACION_UNO_DE)

    regimenes = "".join(
        '<article class="tarjeta aparece" data-orden="%d"><h3>%s</h3><p>%s</p></article>'
        % (i, t, d) for i, (t, d) in enumerate(REGIMENES))

    plazos = "".join(
        '<tr><td><strong>%s</strong></td><td>%s</td><td>%s</td></tr>'
        % (q, c, p) for q, c, p in PLAZOS)

    donde = "".join("<li>%s</li>" % d for d in DONDE)
    derechos = "".join('<li>%s<span><strong>%s.</strong> %s</span></li>'
                       % (_tic(), t, d) for t, d in DERECHOS)

    cuerpo = """
<section class="seccion seccion--crema">
  <div class="wrap">
    <div class="cabecera-seccion">
      <p class="rotulo">El trámite</p>
      <h1>Cómo se renueva la TPC, paso a paso</h1>
      <p class="entradilla">La Tarjeta Profesional de la Construcción caduca a
      los cinco años de su emisión (%(art_cad)s del %(convenio)s). Para
      renovarla se repite el procedimiento de la solicitud inicial
      <strong>excepto la formación en prevención</strong>, que no se vuelve a
      exigir. Esto es todo lo que piden.</p>
      %(botonera)s
    </div>
  </div>
</section>

<section class="seccion seccion--papel">
  <div class="wrap">
    <div class="cabecera-seccion aparece">
      <p class="rotulo">Paso 1</p>
      <h2 id="paso-1">Mira cuándo caduca la tuya</h2>
    </div>
    <div class="rejilla rejilla--2">
      <div class="aparece">
        <p>La fecha está impresa en la tarjeta. Son cinco años desde que se
        emitió, no desde que hiciste el curso ni desde que entraste en la
        empresa.</p>
        <p>Si tu tarjeta es anterior al BOE del <strong>%(boe)s</strong>, puede
        que en su día te dijeran que no caducaba: hasta esa fecha existía una
        disposición transitoria que tenía la caducidad suspendida, y se
        eliminó. Hoy caducan todas.</p>
        <p>Y si ya se te ha pasado la fecha, no hay drama:
        <a href="/tpc-caducada/">se puede renovar igualmente</a>.</p>
      </div>
      <div class="ficha aparece" data-orden="1">
        <p class="rotulo">Quién puede renovar</p>
        <p style="font-size:.95rem">Depende del régimen en el que estés. Es el
        requisito que más gente da por perdido sin comprobarlo.</p>
      </div>
    </div>
  </div>
</section>

<section class="seccion seccion--menta">
  <div class="wrap">
    <div class="cabecera-seccion aparece">
      <p class="rotulo">Paso 2</p>
      <h2 id="paso-2">Comprueba que cumples el requisito de tu régimen</h2>
    </div>
    <div class="rejilla rejilla--3">%(regimenes)s</div>
    <div class="aviso aparece" data-orden="3">
      <p><strong>Lee bien lo de los 30 días.</strong> En Régimen General no hace
      falta estar trabajando hoy: vale con acreditar al menos 30 días de alta en
      los 60 meses anteriores, o sea en los últimos cinco años. Mucha gente cree
      que ha perdido el derecho y no es cierto.</p>
    </div>
  </div>
</section>

<section class="seccion seccion--papel">
  <div class="wrap">
    <div class="cabecera-seccion aparece">
      <p class="rotulo">Paso 3</p>
      <h2 id="paso-3">La documentación que piden</h2>
      <p class="entradilla">Es la del %(art_doc)s, apartados 1 y 2. Cuatro
      papeles fijos y uno a elegir entre cuatro.</p>
    </div>
    <div class="rejilla rejilla--2">
      <div class="ficha aparece">
        <p class="rotulo">Siempre</p>
        <ul class="ficha__lista">%(docs)s</ul>
      </div>
      <div class="ficha aparece" data-orden="1">
        <p class="rotulo">Y al menos uno de estos</p>
        <ul class="ficha__lista">%(uno_de)s</ul>
      </div>
    </div>
    <div class="aviso aparece" data-orden="2">
      <p><strong>El papel que más solicitudes atasca es la vida laboral.</strong>
      Tiene que estar emitida dentro de los 90 días anteriores a la solicitud.
      Si la pediste hace cuatro meses para otra cosa, no te sirve: pide una
      nueva, que es gratis y se saca por internet en un minuto.</p>
    </div>
  </div>
</section>

<section class="seccion seccion--crema">
  <div class="wrap">
    <div class="cabecera-seccion aparece">
      <p class="rotulo">Paso 4</p>
      <h2 id="paso-4">Dónde se entrega</h2>
    </div>
    <div class="rejilla rejilla--2">
      <div class="aparece">
        <p>La tarjeta la emite la <strong>%(emisor)s</strong>. La solicitud se
        entrega en cualquiera de estos sitios:</p>
        <ul>%(donde)s</ul>
        <p>El portal oficial tiene un teléfono gratuito de información:
        <strong>%(tel_portal)s</strong>.</p>
      </div>
      <div class="aparece" data-orden="1">
        <h3>Nosotros no tramitamos la tarjeta</h3>
        <p>Y conviene decirlo claro. Somos un centro de formación homologado por
        la Fundación Laboral (número %(flc)s): damos los cursos del catálogo de
        construcción. El trámite de la tarjeta se hace en los puntos de arriba.</p>
        <p>Si tu duda es de papeles, llámanos igual. Te la resolvemos en dos
        minutos aunque no nos compres nada.</p>
      </div>
    </div>
  </div>
</section>

<section class="seccion seccion--papel">
  <div class="wrap">
    <div class="cabecera-seccion aparece">
      <p class="rotulo">Paso 5</p>
      <h2 id="paso-5">Los plazos</h2>
    </div>
    <div class="tabla-envoltorio aparece">
      <table>
        <thead><tr><th>Qué</th><th>Cuánto</th><th>Detalle</th></tr></thead>
        <tbody>%(plazos)s</tbody>
      </table>
    </div>
    <div class="aviso aparece" data-orden="1">
      <p><strong>El plazo que se lleva por delante los expedientes es el del
      mes.</strong> Si te requieren documentación y lo dejas pasar un mes, el
      expediente se archiva y la solicitud se entiende denegada. Hay que volver
      a empezar de cero.</p>
    </div>
  </div>
</section>

<section class="seccion seccion--menta">
  <div class="wrap">
    <div class="rejilla rejilla--2">
      <div class="aparece">
        <h2>Para qué sirve tenerla en vigor</h2>
        <ul class="ficha__lista">%(derechos)s</ul>
      </div>
      <div class="aparece" data-orden="1">
        <h2>Y si lo que quieres es formación</h2>
        <p>Para renovar, ya lo hemos dicho, no hace falta. Pero hay cursos que
        te van a pedir en obra por otros motivos: el nivel básico de 60 horas
        para ser recurso preventivo, las 20 horas de un oficio nuevo o la
        polivalente de 6 horas si ya tienes las 20 de otro.</p>
        <p>Los damos todos en Móstoles: <a href="/cursos/">mira el catálogo</a>.
        Si tu curso es el de 20 horas, también lo tienes en %(tpc20)s; si es el
        nivel básico de 60, en %(tpc60)s.</p>
      </div>
    </div>
    %(reciclaje)s
  </div>
</section>
%(formulario)s""" % {
        "botonera": _botonera("Preguntar por mi caso"),
        "art_cad": TARJETA["articulo_caducidad"], "convenio": TARJETA["convenio"],
        "art_doc": TARJETA["articulo_documentacion"], "boe": BOE_CADUCIDAD,
        "regimenes": regimenes, "docs": docs, "uno_de": uno_de,
        "donde": donde, "tel_portal": TARJETA["telefono_portal"],
        "emisor": TARJETA["emisor"], "flc": CENTRO["homologacion_flc"],
        "plazos": plazos, "derechos": derechos,
        "tpc20": HERMANAS["tpc20"], "tpc60": HERMANAS["tpc60"],
        "reciclaje": _aviso_reciclaje(),
        "formulario": _formulario("Dinos tu caso y te decimos qué te falta",
                                  ruta="/renovar-la-tpc/")}

    return cuerpo, _ld(_howto_ld(), _migas(("Inicio", "/"),
                                           ("Renovar la TPC", "/renovar-la-tpc/")))


def caducada():
    """Dos cosas que la gente mezcla: renovar (la tarjeta venció) y duplicar
    (la tarjeta desapareció). Van juntas porque se buscan juntas, pero la
    página deja clarísimo que el duplicado NO alarga la validez."""
    mias = [PREGUNTAS[3], PREGUNTAS[7], PREGUNTAS[13]]

    cuerpo = """
<section class="seccion seccion--crema">
  <div class="wrap">
    <div class="cabecera-seccion">
      <p class="rotulo">Tarjeta caducada</p>
      <h1>Se te ha caducado la TPC: qué pasa ahora</h1>
      <p class="entradilla">Nada grave. Quien tiene la tarjeta caducada
      <strong>puede solicitar la renovación</strong>, y el portal oficial de la
      tarjeta no describe ninguna sanción por haberla dejado pasar. Lo que sí
      pasa es que, hasta que la renueves, no tienes tarjeta en vigor que
      enseñar en la obra.</p>
      %(botonera)s
    </div>
  </div>
</section>

<section class="seccion seccion--papel">
  <div class="wrap">
    <div class="rejilla rejilla--2">
      <div class="aparece">
        <h2>Caducada: se renueva y ya está</h2>
        <p>Se pide con los mismos papeles que cualquier renovación: impreso de
        solicitud de renovación, foto, DNI o NIE, informe de vida laboral de los
        últimos 90 días y una prueba de que trabajas en el sector.</p>
        <p>No hay que repetir la formación en prevención. No hay recargo
        descrito. No hay que empezar de cero.</p>
        <div class="botonera">
          <a class="btn btn--salvia" href="/renovar-la-tpc/">El trámite completo</a>
        </div>
      </div>
      <div class="aparece" data-orden="1">
        <h2>Robada, perdida o destrozada: eso es un duplicado</h2>
        <p>Si la tarjeta sigue en vigor pero no la tienes —te la han robado, la
        has perdido o está deteriorada—, lo que se pide es un
        <strong>duplicado</strong>. Se hace mostrando el DNI en un punto de
        tramitación.</p>
        <p>Y aquí está la trampa que pilla a todo el mundo: el duplicado
        <strong>conserva la fecha de caducidad original</strong>. No te regala
        cinco años nuevos. Si a tu tarjeta le quedaban dos meses, al duplicado
        le quedan dos meses.</p>
      </div>
    </div>
  </div>
</section>

<section class="seccion seccion--menta">
  <div class="wrap">
    <div class="cabecera-seccion aparece">
      <p class="rotulo">De un vistazo</p>
      <h2>Renovación y duplicado no son lo mismo</h2>
    </div>
    <div class="tabla-envoltorio aparece">
      <table>
        <thead><tr><th></th><th>Renovación</th><th>Duplicado</th></tr></thead>
        <tbody>
          <tr><td><strong>Cuándo</strong></td>
              <td>La tarjeta ha caducado o está a punto</td>
              <td>Deterioro, robo o extravío</td></tr>
          <tr><td><strong>Qué se lleva</strong></td>
              <td>Impreso, foto, DNI o NIE, vida laboral de 90 días y una prueba de empleo</td>
              <td>El DNI</td></tr>
          <tr><td><strong>Fecha de caducidad</strong></td>
              <td>Cinco años nuevos</td>
              <td><strong>La misma de antes</strong></td></tr>
          <tr><td><strong>Formación</strong></td>
              <td>No se exige</td>
              <td>No se exige</td></tr>
        </tbody>
      </table>
    </div>
    <div class="aviso aparece" data-orden="1">
      <p><strong>Si se te ha perdido una tarjeta que además está caducada</strong>,
      no pidas el duplicado: pide directamente la renovación. El duplicado te
      devolvería una tarjeta caducada, que no te sirve para entrar.</p>
    </div>
  </div>
</section>

<section class="seccion seccion--papel">
  <div class="wrap">
    <div class="cabecera-seccion aparece">
      <p class="rotulo">Antes de que te lo vendan</p>
      <h2>Que no te cobren un curso por renovar</h2>
    </div>
    %(reciclaje)s
    <div class="rejilla rejilla--2">
      <div class="aparece" data-orden="2">
        <p>Si alguien te dice que para recuperar una TPC caducada tienes que
        hacer un curso de reciclaje, pídele que te enseñe dónde lo dice el
        convenio. El procedimiento de renovación es el mismo que el de la
        solicitud inicial <em>excepto la formación en prevención</em>: son las
        palabras del portal oficial.</p>
      </div>
      <div class="aparece" data-orden="3">
        <p>Otra cosa distinta es que te pidan formación <strong>nueva</strong>:
        un oficio que no tenías, el nivel básico de 60 horas o los cursos de
        mandos. Eso sí existe, sí se hace y te lo damos nosotros.
        <a href="/cursos/">Está aquí</a>.</p>
      </div>
    </div>
  </div>
</section>

<section class="seccion seccion--crema">
  <div class="wrap">
    <div class="cabecera-seccion aparece">
      <p class="rotulo">Dudas</p>
      <h2>Las tres que más nos hacen con la tarjeta caducada</h2>
    </div>
    %(preg)s
  </div>
</section>
%(formulario)s""" % {
        "botonera": _botonera("Contarnos mi caso"),
        "reciclaje": _aviso_reciclaje(),
        "preg": _preguntas_html(mias),
        "formulario": _formulario("Te decimos si te toca renovar o duplicar",
                                  ruta="/tpc-caducada/")}

    return cuerpo, _ld(_faq_ld(mias), _migas(("Inicio", "/"),
                                             ("TPC caducada", "/tpc-caducada/")))


def reciclaje():
    """LA PÁGINA DELICADA. Su trabajo es posicionar para «curso de reciclaje
    TPC 4 horas» diciendo la verdad: hoy no existe. El gancho es la lista de
    aviso, no una promesa.

    Si alguna vez hay que cambiar esta página porque el curso salga de verdad,
    la señal es `RECICLAJE_4H['existe']` en centro.py, y la fuente tiene que
    ser el convenio o el portal oficial. Un correo de un comercial no vale."""
    assert not RECICLAJE_4H["existe"], (
        "RECICLAJE_4H['existe'] esta a True: esta pagina dice lo contrario y "
        "hay que reescribirla ANTES de generar nada. Ver CLAUDE.md.")

    mias = [PREGUNTAS[1], PREGUNTAS[0], PREGUNTAS[11]]

    cuatro_h = [c for c in CATALOGO if c[1] == 4][0]

    cuerpo = """
<section class="seccion seccion--crema">
  <div class="wrap">
    <div class="cabecera-seccion">
      <p class="rotulo">La pregunta del millón</p>
      <h1>El curso de reciclaje de 4 horas de construcción</h1>
      <p class="entradilla">Se busca muchísimo, así que vamos al grano:
      <strong>hoy no existe</strong>. En el catálogo de formación de
      construcción no hay ningún curso de reciclaje ni de renovación de 4
      horas, y para renovar la TPC el convenio no exige volver a formarse.</p>
    </div>
  </div>
</section>

<section class="seccion seccion--papel">
  <div class="wrap">
    <div class="rejilla rejilla--2">
      <div class="aparece">
        <h2>Lo que hemos comprobado</h2>
        <p>Fuimos al %(fuente)s el %(cuando)s y miramos dos cosas:</p>
        <ul>
          <li>En el catálogo de formación de construcción <strong>no aparece
          ningún curso de reciclaje ni de renovación de 4 horas</strong>.</li>
          <li>El procedimiento de renovación es el mismo que el de la solicitud
          inicial <em>«excepto la formación en prevención»</em>. Literal.</li>
        </ul>
        <p>Así que, a día de hoy, nadie puede venderte un reciclaje de 4 horas
        de construcción para renovar la tarjeta. Si te lo ofrecen, pregunta qué
        curso es exactamente y con qué amparo.</p>
      </div>
      <div class="ficha ficha--luz linterna aparece" data-orden="1">
        <p class="rotulo">De dónde viene la confusión</p>
        <p><strong>Del metal.</strong> En el sector del metal sí hay formación
        de reciclaje, y mucha gente que trabaja en los dos sectores da por hecho
        que en construcción funciona igual. No funciona igual. Si lo tuyo es el
        metal, tu web es %(metal)s.</p>
        <p><strong>Y del único curso de 4 horas que sí existe:</strong>
        %(cuatro)s de %(cuatro_h)d horas, amparado por el %(convenio)s. Es
        formación de emergencias y <strong>no renueva la tarjeta</strong>.</p>
      </div>
    </div>
  </div>
</section>

<section class="seccion seccion--menta">
  <div class="wrap">
    <div class="cabecera-seccion aparece">
      <p class="rotulo">Si algún día sale</p>
      <h2>Te avisamos, y ya está</h2>
      <p class="entradilla">Se habla de que el convenio pueda aprobar en algún
      momento una formación de reciclaje para construcción. Nosotros no sabemos
      si saldrá, ni cuándo, ni con cuántas horas, y no vamos a decirte que sí
      para que nos dejes el teléfono.</p>
    </div>
    <div class="rejilla rejilla--3">
      <article class="tarjeta aparece"><span class="icono">%(ic)s</span>
        <h3>Lo que sí sabemos</h3><p>Que si se aprueba, lo daremos: somos centro
        homologado por la Fundación Laboral de la Construcción con el número
        %(flc)s y acreditados por la Comunidad de Madrid (%(cm)s).</p></article>
      <article class="tarjeta aparece" data-orden="1"><span class="icono">%(ic)s</span>
        <h3>Lo que no sabemos</h3><p>Si saldrá, en qué fecha, cuántas horas
        tendrá, qué contenido ni cuánto costará. Cuando lo sepamos de fuente
        oficial, lo pondremos aquí y lo diremos con esa fuente.</p></article>
      <article class="tarjeta tarjeta--acento aparece" data-orden="2"><span class="icono">%(ic)s</span>
        <h3>Lo que puedes hacer</h3><p>Dejarnos tus datos abajo. Si el reciclaje
        de construcción se aprueba, te llamamos. Si no se aprueba, no te llama
        nadie y no pasa nada.</p></article>
    </div>
    <div class="aviso aparece" data-orden="3">
      <p><strong>Esto no es una reserva ni una preinscripción.</strong> No hay
      nada que reservar. Es una lista para avisarte, y puedes pedirnos que te
      borremos de ella cuando quieras escribiendo a
      <a href="mailto:%(correo)s">%(correo)s</a>.</p>
    </div>
  </div>
</section>

<section class="seccion seccion--papel">
  <div class="wrap">
    <div class="cabecera-seccion aparece">
      <p class="rotulo">Mientras tanto</p>
      <h2>Lo que de verdad te toca hacer hoy</h2>
    </div>
    <div class="rejilla rejilla--2">
      <div class="aparece">
        <h3>Si tu tarjeta caduca o ha caducado</h3>
        <p>Renovarla con papeles. Está explicado entero, con la documentación
        del artículo 159 y los plazos, en
        <a href="/renovar-la-tpc/">cómo renovar la TPC</a>. Y si ya se te pasó
        la fecha, en <a href="/tpc-caducada/">TPC caducada</a>.</p>
      </div>
      <div class="aparece" data-orden="1">
        <h3>Si lo que te piden es un curso</h3>
        <p>Entonces no es un reciclaje: será un oficio nuevo de 20 horas, la
        polivalente de 6, el nivel básico de 60 o alguno de los de mandos.
        <a href="/cursos/">Todos están aquí</a> y los damos en Móstoles.</p>
      </div>
    </div>
  </div>
</section>

<section class="seccion seccion--crema">
  <div class="wrap">
    <div class="cabecera-seccion aparece">
      <p class="rotulo">Dudas</p>
      <h2>Las tres preguntas que llegan con esto</h2>
    </div>
    %(preg)s
  </div>
</section>
%(formulario)s""" % {
        "fuente": RECICLAJE_4H["fuente"], "cuando": RECICLAJE_4H["comprobado"],
        "metal": HERMANAS["metal"], "cuatro": cuatro_h[0].lower(),
        "cuatro_h": cuatro_h[1], "convenio": TARJETA["convenio"],
        "ic": _tic(), "flc": CENTRO["homologacion_flc"],
        "cm": CENTRO["acreditacion_cm"], "correo": CENTRO["correo"],
        "preg": _preguntas_html(mias),
        "formulario": _formulario(
            "Apúntate a la lista de aviso",
            ruta="/curso-reciclaje-4-horas/", opciones=OPCIONES_AVISO,
            lateral=("Si el reciclaje de construcción llega a aprobarse, te "
                     "llamamos. No hay que pagar nada, no hay que reservar "
                     "nada y no te vamos a mandar publicidad."),
            aviso=("<strong>Somos honestos con esto:</strong> puede que esa "
                   "llamada no se produzca nunca, porque el curso puede no "
                   "aprobarse. Si mientras tanto te corre prisa renovar la "
                   "tarjeta, llámanos y te decimos qué papeles necesitas."))}

    return cuerpo, _ld(_faq_ld(mias),
                       _migas(("Inicio", "/"),
                              ("Curso de reciclaje de 4 horas",
                               "/curso-reciclaje-4-horas/")))


def cursos():
    filas = "".join(
        '<article class="bloque aparece" data-orden="%d">'
        '<div class="bloque__cab"><span class="bloque__n">%d h</span><h3>%s</h3></div>'
        '<ul><li>%s</li><li><strong>%s</strong></li></ul></article>'
        % (i, h, n, q, ("%d €" % p) if p else
           "Pídenos precio: no publicamos un número que no esté confirmado")
        for i, (n, h, p, q) in enumerate(CATALOGO))

    reglas = "".join(
        '<li>%s<span><strong>%s.</strong> %s</span></li>' % (_tic(), t, d)
        for t, d in REGLAS_CENTRO)

    cuerpo = """
<section class="seccion seccion--crema">
  <div class="wrap">
    <div class="cabecera-seccion">
      <p class="rotulo">Formación de construcción</p>
      <h1>Los cursos que sí existen y que damos en Móstoles</h1>
      <p class="entradilla">El catálogo de formación de construcción del
      %(convenio)s, impartido en nuestras aulas. Somos centro homologado por la
      %(emisor)s con el número %(flc)s y acreditados por la Comunidad de Madrid
      con el %(cm)s.</p>
      %(botonera)s
    </div>
  </div>
</section>

<section class="seccion seccion--papel">
  <div class="wrap">
    <div class="aviso aparece">
      <p><strong>Ninguno de estos cursos renueva la tarjeta.</strong> La
      renovación va por papeles: <a href="/renovar-la-tpc/">aquí está el
      trámite</a>. Estos cursos son para sacar la tarjeta por primera vez, para
      añadir un oficio o para lo que te pida la obra por otro motivo.</p>
    </div>
    <div class="temario-2">%(filas)s</div>
  </div>
</section>

<section class="seccion seccion--menta">
  <div class="wrap">
    <div class="rejilla rejilla--2">
      <div class="aparece">
        <h2>Cuál te toca a ti</h2>
        <p><strong>Nunca has trabajado en construcción.</strong> El nivel
        inicial de 8 horas y después las 20 horas de tu oficio. Con eso se pide
        la tarjeta por primera vez. Las 20 horas también las tienes explicadas
        en %(tpc20)s y en %(cursotpc)s.</p>
        <p><strong>Ya tienes las 20 horas de un oficio y te piden otro.</strong>
        La polivalente de 6 horas. No se repite lo hecho.</p>
        <p><strong>Te piden ser recurso preventivo.</strong> El nivel básico de
        60 horas del artículo 145, que está entero en %(tpc60)s.</p>
        <p><strong>Trabajas en el metal.</strong> Ese es otro convenio y otra
        tarjeta: %(metal)s.</p>
      </div>
      <div class="ficha aparece" data-orden="1">
        <p class="rotulo">Cómo trabajamos</p>
        <ul class="ficha__lista">%(reglas)s</ul>
      </div>
    </div>
  </div>
</section>

<section class="seccion seccion--papel">
  <div class="wrap">
    <div class="cabecera-seccion aparece">
      <p class="rotulo">Por qué faltan precios</p>
      <h2>Preferimos que nos llames a inventarnos un número</h2>
      <p class="entradilla">Los precios que ves publicados son los que están
      confirmados. Los demás cursos tienen precio, claro, pero no lo publicamos
      hasta tenerlo revisado: un precio mal puesto en una web es una discusión
      en el mostrador. Llama al %(tel)s y te lo decimos en el momento.</p>
    </div>
    %(reciclaje)s
  </div>
</section>
%(formulario)s""" % {
        "convenio": TARJETA["convenio"], "emisor": TARJETA["emisor"],
        "flc": CENTRO["homologacion_flc"], "cm": CENTRO["acreditacion_cm"],
        "botonera": _botonera("Preguntar por un curso"), "filas": filas,
        "reglas": reglas, "tel": TEL1,
        "tpc20": HERMANAS["tpc20"], "tpc60": HERMANAS["tpc60"],
        "cursotpc": HERMANAS["cursotpc"], "metal": HERMANAS["metal"],
        "reciclaje": _aviso_reciclaje(),
        "formulario": _formulario("Dinos qué te piden y te decimos qué curso es",
                                  ruta="/cursos/")}

    return cuerpo, _ld(*(_cursos_ld() + [_migas(("Inicio", "/"),
                                                ("Cursos", "/cursos/"))]))


def preguntas():
    cuerpo = """
<section class="seccion seccion--crema">
  <div class="wrap">
    <div class="cabecera-seccion">
      <p class="rotulo">Preguntas frecuentes</p>
      <h1>Todo lo que nos preguntáis sobre renovar la TPC</h1>
      <p class="entradilla">Las respuestas salen del portal oficial de la
      tarjeta y del %(convenio)s. Si tu duda no está aquí, llámanos al %(tel)s:
      no hay que registrarse en nada para preguntar.</p>
    </div>
  </div>
</section>

<section class="seccion seccion--papel">
  <div class="wrap">%(todas)s%(botonera)s</div>
</section>
%(formulario)s""" % {
        "convenio": TARJETA["convenio"], "tel": TEL1,
        "todas": _preguntas_html(PREGUNTAS), "botonera": _botonera(),
        "formulario": _formulario(ruta="/preguntas-frecuentes/")}

    return cuerpo, _ld(_faq_ld(PREGUNTAS),
                       _migas(("Inicio", "/"),
                              ("Preguntas frecuentes", "/preguntas-frecuentes/")))


def contacto():
    tels = "".join('<li><a href="tel:%s">%s</a></li>' % (TEL_E164[t], t)
                   for t in CENTRO["telefonos"])
    horario = "".join('<tr><td>%s</td><td>%s</td></tr>' % (d, h) for d, h in HORARIO)

    cuerpo = """
<section class="seccion seccion--crema">
  <div class="wrap">
    <div class="cabecera-seccion">
      <p class="rotulo">Contacto</p>
      <h1>Hablemos</h1>
      <p class="entradilla">Lo más rápido es llamar. Te decimos qué papeles
      necesitas para renovar aunque no nos compres nada: no tramitamos la
      tarjeta, así que no tenemos nada que venderte en esa llamada.</p>
    </div>
  </div>
</section>

<section class="seccion seccion--papel">
  <div class="wrap">
    <div class="rejilla rejilla--3">
      <article class="tarjeta aparece">
        <span class="icono">%(ic)s</span>
        <h3 style="text-align:center">Teléfonos</h3>
        <ul class="tels">%(tels)s</ul>
      </article>
      <article class="tarjeta aparece" data-orden="1">
        <span class="icono">%(ic)s</span>
        <h3>Dónde estamos</h3>
        <p><a class="direccion" href="%(mapa)s" rel="noopener">%(dir)s<br>
        %(cp)s %(ciudad)s (%(prov)s)</a><br><em>%(ref)s</em></p>
        <p style="font-size:.9rem;color:var(--tenue)">Hay aparcamiento gratuito al lado.</p>
      </article>
      <article class="tarjeta aparece" data-orden="2">
        <span class="icono">%(ic)s</span>
        <h3>Horario de oficina</h3>
        <table style="font-size:.92rem"><tbody>%(horario)s</tbody></table>
        <p style="font-size:.86rem;color:var(--tenue);margin-top:10px">%(nota)s</p>
      </article>
    </div>
    <div class="aviso aparece" data-orden="3">
      <p><strong>Para el trámite de la tarjeta, el teléfono oficial es el
      %(tel_portal)s</strong>, gratuito, del portal de la TPC. La solicitud se
      entrega en los centros de la %(emisor)s, en las asociaciones de la CNC y
      en las sedes de CCOO del Hábitat y UGT FICA. Nosotros somos el centro de
      formación; el resto de las webs del centro están en %(prevencionmadrid)s.</p>
    </div>
  </div>
</section>
%(formulario)s""" % {
        "ic": _tic(), "tels": tels, "dir": CENTRO["direccion"], "cp": CENTRO["cp"],
        "ciudad": CENTRO["ciudad"], "prov": CENTRO["provincia"],
        "ref": CENTRO["referencia"], "mapa": MAPA, "horario": horario,
        "nota": HORARIO_NOTA, "tel_portal": TARJETA["telefono_portal"],
        "emisor": TARJETA["emisor"],
        "prevencionmadrid": HERMANAS["prevencionmadrid"],
        "formulario": _formulario("Déjanos tus datos y te llamamos",
                                  ruta="/contacto/")}

    return cuerpo, _ld(_centro_ld(), _migas(("Inicio", "/"), ("Contacto", "/contacto/")))


def gracias():
    """Va en noindex: si alguien llegara por Google dispararía una conversión
    falsa y ensuciaría la medición."""
    cuerpo = """
<section class="seccion seccion--crema">
  <div class="wrap" style="max-width:660px;text-align:center">
    <span class="sello" style="margin-bottom:1em"><span class="sello__punto"></span>Recibido</span>
    <h1>Gracias, ya lo tenemos</h1>
    <p class="entradilla" style="margin:0 auto 1.4em">Te contestamos nosotros.
    Si tienes prisa, llamar es lo más rápido: la mayoría de las dudas de la
    renovación se resuelven en la misma llamada.</p>
    <div class="botonera" style="justify-content:center">
      <a class="btn btn--cta" href="tel:%(tel_e)s">Llamar al %(tel)s</a>
      <a class="btn btn--linea" href="/renovar-la-tpc/">Ver el trámite de renovación</a>
    </div>
  </div>
</section>""" % {"tel": TEL1, "tel_e": TEL_E164[TEL1]}
    return cuerpo, ""


# --- Legales ---------------------------------------------------------------

def _legal(titulo, html):
    cuerpo = """
<section class="seccion seccion--crema">
  <div class="wrap" style="max-width:820px">
    <h1>%s</h1>
  </div>
</section>
<section class="seccion seccion--papel">
  <div class="wrap" style="max-width:820px">%s</div>
</section>""" % (titulo, html)
    return cuerpo, ""


def aviso_legal():
    return _legal("Aviso legal", """
<h2>Titular</h2>
<p><strong>%(empresa)s</strong><br>%(dir)s<br>%(cp)s %(ciudad)s (%(prov)s)<br>
Correo: <a href="mailto:%(correo)s">%(correo)s</a><br>
Teléfono: %(tel)s<br>
Acreditado por la Comunidad de Madrid: %(cm)s<br>
Homologado por la Fundación Laboral de la Construcción: %(flc)s</p>

<h2>Objeto</h2>
<p>Esta web informa sobre la renovación de la Tarjeta Profesional de la
Construcción y sobre los cursos de formación de construcción que imparte el
centro. No es una plataforma de venta: no se cobra nada a través de ella.</p>

<h2>El centro no tramita la tarjeta</h2>
<p>La Tarjeta Profesional de la Construcción la emite la Fundación Laboral de
la Construcción y su solicitud se presenta en los puntos de tramitación
oficiales. El titular de esta web es un centro de formación homologado: imparte
cursos, no tramita tarjetas ni interviene en el procedimiento.</p>

<h2>Información sobre el convenio</h2>
<p>Los datos sobre plazos, documentación y requisitos proceden del portal
oficial de la Tarjeta Profesional de la Construcción y del VII Convenio General
del Sector de la Construcción. Se publican a título informativo. Lo que vale
siempre es el texto vigente del convenio y lo que indique la Fundación Laboral
de la Construcción.</p>

<h2>Condiciones de uso</h2>
<p>El acceso a la web es libre y gratuito. Quien la usa se compromete a
hacerlo conforme a la ley y a no realizar actividades que puedan dañar o
sobrecargar los sistemas del titular.</p>

<h2>Contenidos</h2>
<p>Los precios, la duración y las condiciones de los cursos son los vigentes en
la fecha de publicación y pueden cambiar. Ante cualquier duda, lo que vale es
lo que se confirme por teléfono o por escrito al matricularse.</p>

<h2>Propiedad intelectual</h2>
<p>Los textos y el diseño de esta web pertenecen al titular.</p>

<h2>Responsabilidad</h2>
<p>El titular no se hace responsable de los daños derivados del uso de la web
ni de la indisponibilidad temporal por causas técnicas.</p>

<h2>Legislación y fuero</h2>
<p>Esta web se rige por la legislación española. Para cualquier controversia
serán competentes los juzgados y tribunales que correspondan conforme a
derecho.</p>""" % {
        "empresa": CENTRO["empresa"], "dir": CENTRO["direccion"],
        "cp": CENTRO["cp"], "ciudad": CENTRO["ciudad"], "prov": CENTRO["provincia"],
        "correo": CENTRO["correo"], "tel": TEL1,
        "cm": CENTRO["acreditacion_cm"], "flc": CENTRO["homologacion_flc"]})


def privacidad():
    return _legal("Política de privacidad", """
<h2>Quién trata tus datos</h2>
<p><strong>%(empresa)s</strong>, %(dir)s, %(cp)s %(ciudad)s (%(prov)s).
Correo de contacto: <a href="mailto:%(correo)s">%(correo)s</a>.</p>

<h2>Qué datos y para qué</h2>
<p>Solo los que nos das en el formulario o por teléfono: nombre, teléfono, y
si quieres, correo electrónico y lo que nos cuentes. Los usamos para
<strong>responderte y gestionar tu matrícula</strong>, y para nada más.</p>

<h2>La lista de aviso</h2>
<p>Si nos pides que te avisemos por si algún día se aprueba una formación de
reciclaje para construcción, guardamos tus datos con ese único fin: llamarte si
eso llega a ocurrir. No es una reserva ni una preinscripción, no implica ningún
pago y puede que esa llamada no se produzca nunca. Puedes pedirnos que te
borremos de la lista cuando quieras escribiendo a
<a href="mailto:%(correo)s">%(correo)s</a>.</p>

<h2>Base legal</h2>
<p>Tu consentimiento, que das al marcar la casilla del formulario, y la
ejecución de la relación que se inicia si te matriculas.</p>

<h2>Cuánto tiempo</h2>
<p>Mientras dure la relación y, después, el tiempo que exijan las obligaciones
legales del centro. Si solo pediste información y no llegas a matricularte,
los datos se eliminan cuando dejan de ser necesarios.</p>

<h2>A quién se los damos</h2>
<p>A nadie, salvo obligación legal. No vendemos ni cedemos datos, ni te
apuntamos a ninguna lista de publicidad. Los formularios de esta web los recoge
un servicio propio del centro alojado en su propio servidor.</p>

<h2>Tus derechos</h2>
<p>Puedes pedirnos acceso a tus datos, su rectificación o su supresión, y
oponerte o limitar su tratamiento, escribiendo a
<a href="mailto:%(correo)s">%(correo)s</a>. También puedes reclamar ante la
Agencia Española de Protección de Datos (<a href="https://www.aepd.es"
rel="noopener">aepd.es</a>).</p>""" % {
        "empresa": CENTRO["empresa"], "dir": CENTRO["direccion"],
        "cp": CENTRO["cp"], "ciudad": CENTRO["ciudad"], "prov": CENTRO["provincia"],
        "correo": CENTRO["correo"]})


def cookies():
    return _legal("Política de cookies", """
<h2>Qué usamos</h2>
<p>Esta web no necesita cookies para funcionar. No hay carrito, ni cuenta de
usuario, ni nada que recordar entre páginas.</p>

<h2>Lo único que se guarda por defecto</h2>
<p>Cuando respondes al aviso de cookies, guardamos <em>tu respuesta</em> en el
propio navegador (no es una cookie, es almacenamiento local, y no viaja a
ningún sitio). Sirve para no volver a preguntarte en cada página. Caduca a los
24 meses.</p>

<h2>Cookies de medición</h2>
<p>Si las aceptas, cargamos las herramientas de medición de Google para saber
qué páginas sirven de algo y cuáles no. <strong>No se cargan si no las
aceptas</strong>, y hasta ese momento el consentimiento se declara denegado.</p>
<p>Rechazarlas no limita nada: la web funciona exactamente igual.</p>

<h2>Cambiar de opinión</h2>
<p>Cuando quieras, desde el enlace <strong>«Cambiar cookies»</strong> del pie
de esta página.</p>

<h2>Cómo borrarlas desde el navegador</h2>
<p>Todos los navegadores permiten ver y borrar las cookies y el almacenamiento
de un sitio desde sus ajustes de privacidad.</p>""")


# --- El índice de páginas --------------------------------------------------
# (url, título, descripción, función, robots)

TODAS = [
    ("/",
     "Renovar la TPC: cómo se renueva la tarjeta de construcción",
     "Cómo renovar la Tarjeta Profesional de la Construcción: caduca a los "
     "cinco años y se renueva con papeles, no con un curso. Centro en "
     "Móstoles, Madrid.",
     portada, None),

    ("/renovar-la-tpc/",
     "Cómo renovar la TPC paso a paso | Documentación y plazos",
     "El trámite de renovación de la Tarjeta Profesional de la Construcción: "
     "quién puede, qué documentación pide el artículo 159, dónde se entrega y "
     "en cuánto te la dan.",
     renovar, None),

    ("/tpc-caducada/",
     "TPC caducada: qué hacer para renovarla | Duplicados",
     "Si tu Tarjeta Profesional de la Construcción ha caducado, puedes "
     "renovarla igual. Y si te la han robado o la has perdido, lo que toca es "
     "un duplicado.",
     caducada, None),

    ("/curso-reciclaje-4-horas/",
     "Curso de reciclaje TPC de 4 horas: qué hay de verdad hoy",
     "Hoy no existe ningún curso de reciclaje de 4 horas en construcción y "
     "para renovar la TPC no hace falta formación. Te avisamos si algún día se "
     "aprueba uno.",
     reciclaje, None),

    ("/cursos/",
     "Cursos de construcción en Móstoles: 8, 20, 6, 60 y 70 horas",
     "La formación de construcción que sí existe y que damos en Móstoles: "
     "nivel inicial de 8 horas, 20 por oficio, polivalente de 6, nivel básico "
     "de 60 y la de mandos.",
     cursos, None),

    ("/preguntas-frecuentes/",
     "Preguntas frecuentes sobre renovar la TPC",
     "Cada cuánto caduca la TPC, qué papeles piden para renovarla, qué pasa si "
     "está caducada, si hace falta curso y qué hay del reciclaje de 4 horas.",
     preguntas, None),

    ("/contacto/",
     "Contacto | Renovar la TPC en Móstoles (Madrid)",
     "Teléfonos, dirección y horario del centro en Móstoles. Te resolvemos la "
     "duda de la renovación de la TPC por teléfono, aunque no nos compres "
     "nada.",
     contacto, None),

    ("/gracias/",
     "Gracias | renovartpc.es",
     "Hemos recibido tus datos y te contestamos nosotros. Mientras tanto, "
     "puedes ver el trámite completo de la renovación de la Tarjeta "
     "Profesional de la Construcción.",
     gracias, "noindex, nofollow"),

    ("/aviso-legal/",
     "Aviso legal | renovartpc.es",
     "Titular de la web, condiciones de uso y responsabilidad. El centro "
     "imparte formación de construcción y no tramita la Tarjeta Profesional "
     "de la Construcción.",
     aviso_legal, None),

    ("/politica-de-privacidad/",
     "Política de privacidad | renovartpc.es",
     "Qué datos tratamos, para qué los usamos, cómo funciona la lista de aviso "
     "del reciclaje de 4 horas y cómo ejercer tus derechos de protección de "
     "datos.",
     privacidad, None),

    ("/politica-de-cookies/",
     "Política de cookies | renovartpc.es",
     "Qué cookies usa esta web, por qué la medición no se carga hasta que la "
     "aceptas y cómo rechazarlas o cambiar de opinión cuando quieras.",
     cookies, None),
]


# --- El fichero para los buscadores con IA ---------------------------------

def llms():
    """llms.txt: lo que una IA necesita saber de esta web, en llano y sin
    tener que interpretar el HTML.

    Lo importante de este fichero en ESTA web: que un modelo al que le
    pregunten «¿existe el curso de reciclaje de 4 horas de construcción?»
    conteste que no. Por eso va arriba del todo y con esas palabras."""
    preg = "\n".join("- **%s** %s" % (_sin_etiquetas(p), _sin_etiquetas(r))
                     for p, r in PREGUNTAS)
    cursos_txt = "\n".join(
        "- **%s, %d horas:** %s%s" % (n, h, _sin_etiquetas(q),
                                      (" Precio: %d €." % p) if p else
                                      " Precio no publicado; se pide al centro.")
        for n, h, p, q in CATALOGO)
    docs_txt = "\n".join("- %s %s" % (_sin_etiquetas(t), _sin_etiquetas(d))
                         for t, d in DOCUMENTACION)
    uno_txt = "\n".join("- %s" % _sin_etiquetas(x) for x in DOCUMENTACION_UNO_DE)
    plazos_txt = "\n".join("- **%s:** %s. %s" % (q, c, p) for q, c, p in PLAZOS)
    reg_txt = "\n".join("- **%s:** %s" % (t, _sin_etiquetas(d)) for t, d in REGIMENES)

    return """# renovartpc.es

> Cómo **renovar la Tarjeta Profesional de la Construcción (TPC)**, explicado
> por Prevención Siglo 21 (Centro Médico Siglo XXI Prevención de Riesgos
> Laborales, S.L.), centro de formación en Móstoles, Madrid.

## Lo primero, porque es lo que más se pregunta

**El «curso de reciclaje de 4 horas de construcción» NO EXISTE hoy**
(comprobado el %(comprobado)s en el %(fuente)s). En el catálogo de formación de
construcción no hay ningún curso de reciclaje ni de renovación de 4 horas.

**Para renovar la TPC no hay que volver a formarse.** El portal oficial dice
que la renovación sigue el mismo procedimiento que la solicitud inicial
*«excepto la formación en prevención»*.

El único curso de 4 horas del catálogo de construcción es **primeros auxilios
en equipos de emergencia**, amparado por el %(convenio)s, y no renueva la
tarjeta.

Si algún día se aprueba una formación de reciclaje para construcción, este
centro la impartirá y avisará a quien se haya apuntado a su lista de aviso en
%(sitio)s/curso-reciclaje-4-horas/. No hay fecha, no hay precio y no hay
reserva posible.

## La tarjeta

- **Quién la emite:** %(emisor)s.
- **Qué la regula:** %(convenio)s.
- **Validez:** caduca a los **cinco años** de su emisión (%(art_cad)s).
- **Antecedente:** en el BOE del %(boe)s se eliminó la disposición transitoria
  tercera, que tenía la caducidad suspendida. Desde entonces caducan todas.
- **Tarjeta caducada:** quien la tiene caducada **puede solicitar la
  renovación**. El portal oficial no describe ninguna sanción.
- **Deterioro, robo o extravío:** se pide un **duplicado** mostrando el DNI en
  un punto de tramitación. El duplicado **conserva la fecha de caducidad
  original**: no alarga la validez.
- **Derechos del titular:** exención del periodo de prueba para los trabajos de
  su categoría, y validez del reconocimiento de vigilancia de la salud con el
  límite de un año para el mismo puesto.

## Documentación de renovación (%(art_doc)s, apartados 1 y 2)

Siempre:

%(docs)s

Y al menos uno de estos:

%(uno)s

## Requisitos por régimen

%(regimenes)s

## Plazos

%(plazos)s

## Dónde se tramita

%(donde)s

Teléfono gratuito de información del portal oficial: **%(tel_portal)s**.

**Este centro NO tramita la tarjeta.** Es un centro de formación homologado por
la %(emisor)s con el número %(flc)s y acreditado por la Comunidad de Madrid con
el %(cm)s. Imparte cursos; la tarjeta se solicita en los puntos de arriba.

## Cursos de construcción que sí existen y que imparte el centro

%(cursos)s

Condiciones del centro: presencial en Móstoles, solo hay que traer DNI o NIE,
18 años cumplidos, 30 minutos de margen de puntualidad, duplicado del título
del curso 10 €, bonificable por FUNDAE pero **la gestión la hace una entidad
organizadora externa** (los autónomos no tienen crédito de formación), y los
grupos se abren **según la demanda**, sin calendario fijo publicado.

## El centro

- **Dirección:** %(dir)s, %(cp)s %(ciudad)s (%(prov)s). %(ref)s. Aparcamiento
  gratuito al lado.
- **Teléfonos:** %(tels)s
- **Correo:** %(correo)s
- **Horario de oficina:**
%(horario)s

## Preguntas y respuestas

%(preguntas)s

## Páginas

- [Inicio](%(sitio)s/): resumen de la renovación.
- [Cómo renovar la TPC](%(sitio)s/renovar-la-tpc/): el trámite paso a paso.
- [TPC caducada](%(sitio)s/tpc-caducada/): caducada, robada o perdida.
- [Curso de reciclaje de 4 horas](%(sitio)s/curso-reciclaje-4-horas/): qué hay
  de verdad y lista de aviso.
- [Cursos](%(sitio)s/cursos/): el catálogo de construcción.
- [Preguntas frecuentes](%(sitio)s/preguntas-frecuentes/)
- [Contacto](%(sitio)s/contacto/)
""" % {
        "comprobado": RECICLAJE_4H["comprobado"], "fuente": RECICLAJE_4H["fuente"],
        "emisor": TARJETA["emisor"], "convenio": TARJETA["convenio"],
        "art_cad": TARJETA["articulo_caducidad"],
        "art_doc": TARJETA["articulo_documentacion"],
        "tel_portal": TARJETA["telefono_portal"], "boe": BOE_CADUCIDAD,
        "docs": docs_txt, "uno": uno_txt, "regimenes": reg_txt,
        "plazos": plazos_txt,
        "donde": "\n".join("- %s" % d for d in DONDE),
        "cursos": cursos_txt,
        "dir": CENTRO["direccion"], "cp": CENTRO["cp"],
        "ciudad": CENTRO["ciudad"], "prov": CENTRO["provincia"],
        "ref": CENTRO["referencia"], "correo": CENTRO["correo"],
        "cm": CENTRO["acreditacion_cm"], "flc": CENTRO["homologacion_flc"],
        "tels": ", ".join(CENTRO["telefonos"]),
        "horario": "\n".join("  - %s: %s" % (d, h) for d, h in HORARIO),
        "preguntas": preg, "sitio": SITIO}
