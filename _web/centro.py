# -*- coding: utf-8 -*-
"""
Datos del centro y de la RENOVACION de la Tarjeta Profesional de la
Construccion (TPC).

QUE ES ESTA WEB: renovartpc.es, la web para quien busca renovar su Tarjeta
Profesional de la Construccion. La hermana es reciclajemetal.es, para el metal.
Son DOS webs distintas a proposito y NO comparten textos: ver la regla de
no-duplicar-contenido-entre-webs en la memoria de Claude.

============================================================================
LA REGLA DE ORO DE ESTA WEB
============================================================================
EL «CURSO DE RECICLAJE DE 4 HORAS DE CONSTRUCCION» NO EXISTE HOY.

Comprobado en el portal oficial de la TPC (trabajoenconstruccion.com): en el
catalogo de construccion NO hay ningun curso de reciclaje ni de renovacion de
4 horas, y **para renovar la TPC no hay que volver a formarse**. El unico curso
de 4 horas del catalogo de construccion es «primeros auxilios en equipos de
emergencia», que no renueva nada.

Pedro quiere posicionarse para ese curso por si sale en unos meses. Se puede
posicionar SIN MENTIR: se cuenta la verdad de hoy y se ofrece una lista de
aviso. NUNCA se afirma que exista, ni se pone fecha, ni «proximamente».

Antes de escribir una linea sobre el reciclaje de 4 horas, leer CLAUDE.md.
============================================================================

NI UN DATO INVENTADO. Lo que dicta Pedro va aqui; lo que regula el convenio va
marcado con su fuente. Si algo no se sabe, no se publica: se pregunta. Lo que
esta a la espera de que Pedro lo confirme lleva `# PENDIENTE PEDRO`.

Si un dato cambia, se cambia AQUI y se vuelve a ejecutar generar.py.
"""

SITIO = "https://renovartpc.es"

# --- El centro (identico en todas sus webs; revisado por Pedro el 11/09/2026)
CENTRO = {
    "empresa": "Centro Médico Siglo XXI Prevención de Riesgos Laborales, S.L.",
    "marca": "Prevención Siglo 21",
    "homologacion_flc": "0505101086",   # Fundación Laboral de la Construcción
    "acreditacion_cm": "CM 87/2006",    # Comunidad de Madrid
    "direccion": "Calle La Fragua 1, Portal 2, 1ª planta (oficinas 2101, 2102 y 2104)",
    "cp": "28933",
    "ciudad": "Móstoles",
    "provincia": "Madrid",
    "referencia": "Junto a la Plaza de Toros",
    "telefonos": ["91 617 04 23", "630 29 25 16", "691 10 10 10"],
    "correo": "info@renovartpc.es",   # buzon propio del dominio (Pedro, 16/09/2026)
}

TEL_E164 = {"91 617 04 23": "+34916170423",
            "630 29 25 16": "+34630292516",
            "691 10 10 10": "+34691101010"}

WASAP = "34630292516"
# OJO: el texto del WhatsApp NO puede dar por hecho que exista el curso de
# reciclaje de 4 horas. Antes ponia «con el curso de reciclaje de 4 horas» y
# eso ya era afirmar que existe, desde el primer mensaje.
WASAP_TEXTO = "Hola,%20tengo%20una%20duda%20sobre%20la%20renovaci%C3%B3n%20de%20mi%20TPC"

MAPA = ("https://www.google.com/maps/search/?api=1&amp;"
        "query=Calle+La+Fragua+1+Portal+2+28933+M%C3%B3stoles+Madrid")

# --- El formulario ---------------------------------------------------------
# Servicio propio de Pedro. PENDIENTE: dar de alta la clave "renovartpc" en
# /etc/formularios/config.json del VPS (paso de root, ver despliegue/).
# Los campos que el servicio lee son SIETE y con inicial mayuscula: Nombre,
# Email, Telefono, Curso, Mensaje, Acepto, Origen. Con otros nombres el aviso
# llega vacio.
FORMULARIO = "https://formularios.tpcmetal.es/enviar/renovartpc"

# --- La medicion -----------------------------------------------------------
# VACIO A PROPOSITO: renovartpc.es no esta en la tabla de contenedores de la
# gestora (Dlega). El contenedor lo da Ana, no se inventa. Cuando lo de, se
# escribe aqui y web.js hace el resto (consentimiento denegado por defecto).
GTM = ""

# --- La TPC, segun el portal oficial ---------------------------------------
# Fuente: portal oficial de la Tarjeta Profesional de la Construccion
# (trabajoenconstruccion.com), consultado el 16/09/2026. La emite la Fundacion
# Laboral de la Construccion (FLC) y la regula el VII Convenio General del
# Sector de la Construccion. El VI Convenio es historico: no citarlo como
# vigente.
TARJETA = {
    "emisor": "Fundación Laboral de la Construcción",
    "convenio": "VII Convenio General del Sector de la Construcción",
    "validez_anyos": 5,
    "articulo_caducidad": "artículo 161",
    "articulo_documentacion": "artículo 159",
    "telefono_portal": "900 11 21 21",
}

# El antecedente que explica por que hoy caduca y antes no. En el BOE del 23 de
# febrero de 2016 se elimino la disposicion transitoria tercera, que tenia la
# caducidad suspendida. No es un dato de relleno: mucha gente tiene tarjetas
# emitidas antes de esa fecha y cree que le valen para siempre.
BOE_CADUCIDAD = "23 de febrero de 2016"

# Documentacion de RENOVACION (articulo 159, apartados 1 y 2).
# El impreso, la foto, el DNI y la vida laboral son los cuatro obligatorios;
# de la quinta lista hace falta AL MENOS UNO.
DOCUMENTACION = [
    ("Impreso de solicitud de renovación",
     "El de renovación, que no es el mismo que el de la solicitud inicial."),
    ("Una foto tamaño carnet",
     "La de siempre, como la del DNI."),
    ("Fotocopia del DNI o del NIE",
     "En vigor."),
    ("Informe de vida laboral",
     "Emitido <strong>dentro de los 90 días anteriores</strong> a la solicitud. "
     "Es el papel que más solicitudes atasca: si lo pediste hace cuatro meses, "
     "ya no vale."),
]

DOCUMENTACION_UNO_DE = [
    "Certificado de empresa para la Fundación Laboral de la Construcción "
    "(modelo <strong>Anexo VI</strong>)",
    "Certificado de empresa para el Servicio Público de Empleo",
    "Recibos de salarios (las nóminas)",
    "Contrato de trabajo",
]

# Requisitos por regimen (portal oficial).
REGIMENES = [
    ("Régimen General",
     "Estar de alta —o en incapacidad temporal— en una empresa del ámbito del "
     "convenio. También vale acreditar <strong>al menos 30 días de alta en los "
     "60 meses anteriores</strong>."),
    ("Autónomos (RETA)",
     "Realizar actividades encuadradas en el ámbito del convenio."),
    ("Profesionales colegiados",
     "Estar afiliados a una mutualidad de previsión social y realizar "
     "actividades del ámbito del convenio."),
]

# Plazos del procedimiento (portal oficial).
PLAZOS = [
    ("Subsanar la documentación", "10 días",
     "Si falta algo, te lo requieren y tienes 10 días para arreglarlo."),
    ("Si no atiendes el requerimiento", "1 mes",
     "Pasado un mes sin contestar, el expediente se archiva y la solicitud se "
     "entiende denegada. Hay que volver a empezar."),
    ("Entrega de la tarjeta", "máximo 1 mes",
     "Desde que la documentación está correcta y completa."),
    ("Reclamar", "15 días",
     "Desde la notificación, si no estás de acuerdo con la resolución."),
]

# Donde se tramita (portal oficial).
DONDE = [
    "Centros de la Fundación Laboral de la Construcción",
    "Sedes de las asociaciones de la Confederación Nacional de la Construcción (CNC)",
    "Sedes de CCOO del Hábitat",
    "Sedes de UGT FICA",
]

# Derechos del titular de la TPC (portal oficial).
DERECHOS = [
    ("Exención del periodo de prueba",
     "Para los trabajos de la categoría que figura en la tarjeta."),
    ("El reconocimiento médico vale",
     "El reconocimiento de vigilancia de la salud se da por válido, con el "
     "límite de un año, para el mismo puesto de trabajo."),
]

# --- El curso de reciclaje de 4 horas: HOY NO EXISTE -----------------------
# No es una ficha de curso: es la ficha de UNA COSA QUE NO EXISTE, y esta aqui
# para que nadie la confunda con un curso del catalogo. Si algun dia el
# convenio aprueba uno, se rellena y se avisa a la lista.
RECICLAJE_4H = {
    "existe": False,          # <-- lo que manda. NO cambiar sin fuente oficial.
    "comprobado": "16/09/2026",
    "fuente": "portal oficial de la TPC (trabajoenconstruccion.com)",
    "precio": None,           # PENDIENTE PEDRO: no hay precio de algo que no existe.
    # PENDIENTE PEDRO: los 70 € que figuraban aquí son los del curso
    # POLIVALENTE de 6 horas, que sí existe. Estaban puestos en el andamiaje
    # inicial sobre el curso de 4 h; se han movido a CATALOGO, donde les toca.
}

# --- La formacion de construccion que SI existe y SI damos -----------------
# Catalogo del VII Convenio. Precios: solo los que ha dictado Pedro y estan
# verificados en sus otras webs (20 h = 120 €, 60 h = 180 €, polivalente 6 h =
# 70 €). Los demas van a None y en la web NO se pone precio: se dice «pídenos
# precio». Inventarse uno es peor que no ponerlo.
# (nombre, horas, precio, para quien / que es)
CATALOGO = [
    ("Primeros auxilios en equipos de emergencia", 4, None,   # PENDIENTE PEDRO
     "El <strong>único</strong> curso de 4 horas del catálogo de construcción, "
     "amparado por el VII Convenio. No renueva la tarjeta ni la sustituye: es "
     "formación de emergencias."),
    ("Formación polivalente", 6, 70,
     "Las 6 horas para quien ya hizo las 20 horas de otro oficio, tiene el "
     "nivel básico del artículo 145 o la convalidación de la parte común de "
     "14 horas del anexo XIII. No se repite lo que ya está hecho."),
    ("Personal directivo", 10, 90,   # precio dictado por Pedro el 16/09/2026
     "Para gerencia y dirección de empresa."),
    ("Formación por oficio", 20, 120,
     "Las 20 horas del oficio concreto: albañilería, ferralla, encofrados, "
     "fontanería… Hay 31 oficios en el catálogo."),
    ("Responsables de obra y técnicos de ejecución", 20, None,  # PENDIENTE PEDRO
     "Para quien dirige la ejecución de la obra."),
    ("Administrativos", 20, None,                         # PENDIENTE PEDRO: precio
     "Personal de oficina de empresas del sector."),
    ("Nivel básico de prevención", 60, 180,
     "El nivel básico del artículo 145. Es lo que se pide para ejercer de "
     "recurso preventivo en obra."),
]

# Reglas del centro (verificadas, de las otras webs de Pedro).
REGLAS_CENTRO = [
    ("Presencial en Móstoles",
     "Las clases son presenciales, en nuestras aulas de la Calle La Fragua 1."),
    ("Solo hay que traer el DNI o el NIE",
     "El material lo pone el centro. No hay que comprar nada."),
    ("18 años cumplidos",
     "Con 16 o 17 llámanos: en construcción los menores solo pueden estar en "
     "obra con contrato de formación en alternancia."),
    ("30 minutos de margen",
     "Hay media hora de cortesía para llegar. Aun así, lo que se pierde no se "
     "recupera."),
    ("Duplicado del título del curso: 10 €",
     "Si pierdes el título que te damos nosotros. El duplicado de la TARJETA "
     "es otra cosa distinta y se pide en la Fundación Laboral."),
    ("FUNDAE, con claridad",
     "Los cursos son bonificables, pero <em>la gestión no la hacemos "
     "nosotros</em>: la tramita una entidad organizadora externa. Y si eres "
     "autónomo, no tienes crédito de formación."),
    ("Grupos según la demanda",
     "No publicamos calendario fijo a propósito. Apuntamos lo que necesitas y "
     "te avisamos cuando sale grupo."),
]

# El horario de oficina, con las palabras que quiere Pedro: «de 8 horas a 18
# horas», no «08:00 a 18:00». Viernes hasta las 15 (Pedro, 15/09/2026).
HORARIO = [
    ("Lunes a jueves", "de 8 horas a 18 horas"),
    ("Viernes", "de 8 horas a 15 horas"),
    ("Sábados y domingos", "cerrado"),
]
HORARIO_NOTA = ("Los días que hay formación por la tarde —de 14 a 21 o de 15 "
                "a 22 horas— las aulas se quedan abiertas hasta esa hora.")

# --- Las preguntas ---------------------------------------------------------
# Las respuestas salen de: el portal oficial de la TPC (lo que regula el
# convenio) y las reglas del centro que dicto Pedro. Ni una inventada.
PREGUNTAS = [
    ("¿Hay que hacer un curso para renovar la TPC?",
     "No. El portal oficial lo dice literalmente: la renovación sigue el mismo "
     "procedimiento que la solicitud inicial <em>«excepto la formación en "
     "prevención»</em>. Se renueva con papeles —vida laboral y acreditación de "
     "que trabajas en el sector—, no volviendo a clase."),

    ("¿Existe el curso de reciclaje de 4 horas de construcción?",
     "Hoy no. En el catálogo de formación de construcción no hay ningún curso "
     "de reciclaje ni de renovación de 4 horas. El único curso de 4 horas que "
     "existe en construcción es el de primeros auxilios en equipos de "
     "emergencia, y ese no renueva la tarjeta. Si algún día el convenio aprueba "
     "uno, lo daremos: puedes dejarnos tus datos y te avisamos."),

    ("¿Cada cuánto caduca la Tarjeta Profesional de la Construcción?",
     "A los cinco años de su emisión, según el artículo 161 del VII Convenio "
     "General del Sector de la Construcción. La fecha exacta está impresa en la "
     "propia tarjeta."),

    ("Se me ha caducado. ¿La he perdido?",
     "No. Quien tiene la tarjeta caducada puede solicitar la renovación. El "
     "portal oficial no describe ninguna sanción por haberla dejado caducar. "
     "Se pide con los mismos papeles."),

    ("¿Qué documentación piden para renovar?",
     "Cuatro papeles siempre: impreso de solicitud de renovación, foto tamaño "
     "carnet, fotocopia del DNI o NIE e informe de vida laboral emitido dentro "
     "de los 90 días anteriores. Y además al menos uno de estos: certificado de "
     "empresa para la Fundación Laboral (Anexo VI), certificado de empresa para "
     "el Servicio Público de Empleo, recibos de salarios o contrato de trabajo. "
     "Es el artículo 159, apartados 1 y 2."),

    ("Llevo un tiempo sin trabajar en construcción, ¿puedo renovar?",
     "En Régimen General se puede acreditar <strong>al menos 30 días de alta en "
     "los 60 meses anteriores</strong>, es decir, en los últimos cinco años. No "
     "hace falta estar trabajando hoy mismo si cumples eso."),

    ("Soy autónomo. ¿Puedo tener y renovar la TPC?",
     "Sí. Los autónomos del RETA pueden renovarla si realizan actividades "
     "encuadradas en el ámbito del convenio de la construcción."),

    ("Me han robado la tarjeta. ¿Eso es una renovación?",
     "No, eso es un <strong>duplicado</strong>. Por deterioro, robo o extravío "
     "se pide mostrando el DNI en un punto de tramitación. Ojo con esto: el "
     "duplicado <strong>conserva la fecha de caducidad original</strong>. Si la "
     "tarjeta estaba a punto de caducar, el duplicado también."),

    ("¿Cuánto tarda en llegar la tarjeta renovada?",
     "Un mes como máximo desde que la documentación está correcta y completa. "
     "Si falta algo, te requieren y tienes 10 días para subsanarlo; si pasa un "
     "mes sin atender el requerimiento, el expediente se archiva y la solicitud "
     "se entiende denegada."),

    ("¿Dónde se entrega la solicitud?",
     "En los centros de la Fundación Laboral de la Construcción, en las sedes "
     "de las asociaciones de la CNC y en las de CCOO del Hábitat y UGT FICA. El "
     "portal oficial tiene un teléfono gratuito de información: 900 11 21 21."),

    ("¿Vosotros me tramitáis la renovación?",
     "No. La tarjeta la emite la Fundación Laboral de la Construcción y la "
     "solicitud se entrega en sus puntos de tramitación. Nosotros somos un "
     "centro de formación homologado por la Fundación (número 0505101086): "
     "damos los cursos del catálogo. Si tu duda es de papeles, te la "
     "resolvemos por teléfono igual, aunque no nos compres nada."),

    ("Entonces, ¿para qué necesito un curso?",
     "Para <em>sacar</em> la tarjeta por primera vez sí hace falta formación en "
     "prevención: el nivel inicial de 8 horas y las 20 horas del oficio. Para "
     "<em>renovarla</em>, no. Y hay cursos que no van de la tarjeta, sino de lo "
     "que te pide la obra: el nivel básico de 60 horas para ser recurso "
     "preventivo, los 10 de directivos o los 70 de delegados de prevención."),

    ("Ya hice las 20 horas de un oficio y ahora me piden otro",
     "Para eso está la formación polivalente de 6 horas: vale para quien ya "
     "tiene las 20 horas de otro oficio, el nivel básico del artículo 145 o la "
     "convalidación de la parte común de 14 horas del anexo XIII. Son 70 € y no "
     "se repite lo que ya está hecho."),

    ("Mi tarjeta es antigua y no ponía nada de caducar",
     "Hasta el BOE del 23 de febrero de 2016 había una disposición transitoria "
     "que tenía la caducidad suspendida. Se eliminó. Desde entonces la tarjeta "
     "caduca a los cinco años de su emisión, sin excepciones."),

    ("¿Para qué sirve tener la TPC, aparte de para entrar en obra?",
     "El titular queda exento del periodo de prueba en los trabajos de su "
     "categoría, y el reconocimiento médico de vigilancia de la salud se da por "
     "válido —con el límite de un año— para el mismo puesto de trabajo."),
]
