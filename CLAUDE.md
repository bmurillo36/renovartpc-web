# CLAUDE.md — renovartpc.es

Web del centro de Pedro sobre cómo **renovar la Tarjeta Profesional de la
Construcción (TPC)**. Estática, sin dependencias, generada con Python.

    python _web/generar.py     # construye las 11 páginas
    python _web/auditar.py     # las audita en Chrome de verdad; sale 1 si falla

## LA REGLA DE ORO

**Esta web NO PUEDE AFIRMAR QUE EXISTA el curso de reciclaje de 4 horas de
construcción. Hoy no existe.**

Comprobado el 16/09/2026 en el portal oficial de la TPC
(`trabajoenconstruccion.com`): en el catálogo de construcción no hay ningún
curso de reciclaje ni de renovación de 4 horas, y **para renovar la tarjeta no
hay que volver a formarse** — la renovación sigue el mismo procedimiento que la
solicitud inicial *«excepto la formación en prevención»*, palabras del portal.

Pedro quiere posicionarse por si ese curso sale en unos meses. Se puede, y sin
mentir: se cuenta la verdad de hoy y se ofrece una **lista de aviso**. Eso es
`/curso-reciclaje-4-horas/`, y el gancho de captación de la web.

Prohibido, aunque venda más:

- «próximamente», «ya disponible», «reserva tu plaza», «preinscríbete»
- poner fecha de salida, precio, horas o temario de ese curso
- insinuar que renovar la TPC exige formación

Lo que sí se dice: **si se aprueba, lo daremos** (el centro está homologado por
la Fundación Laboral con el 0505101086) **y te avisamos**.

Esto no depende de la buena memoria de nadie:

- `centro.py › RECICLAJE_4H["existe"] = False` es la bandera. Cambiarla exige
  fuente oficial —el convenio o el portal—, no el correo de un comercial.
- `paginas.py › reciclaje()` tiene un `assert` que se niega a generar la página
  si esa bandera está a `True` sin haber reescrito el texto.
- `auditar.py` se pone rojo si alguna página cuela una de las frases prohibidas,
  si `/curso-reciclaje-4-horas/` deja de decir «no existe» o si `llms.txt` lo
  deja de decir.

**El único curso de 4 horas que sí existe en construcción** es *primeros
auxilios en equipos de emergencia*, amparado por el VII Convenio. Está en
`/cursos/` y ahí se deja claro que no renueva nada. En el **metal** sí hay
reciclaje: de ahí viene media confusión, y por eso esa página enlaza a
tpcmetal.es. A **reciclajemetal.es no se enlaza todavía** (Pedro, 16/09/2026).

## De dónde sale cada dato

| | |
|---|---|
| Convenio | **VII** Convenio General del Sector de la Construcción. El VI es histórico: no citarlo como vigente |
| Caducidad | **5 años** desde la emisión, **artículo 161** |
| Antecedente | BOE del **23/02/2016**: se eliminó la disposición transitoria tercera que suspendía la caducidad |
| Documentación | **Artículo 159**, apartados 1 y 2. La vida laboral, emitida **dentro de los 90 días anteriores** |
| Caducada | **Se puede renovar.** El portal no describe ninguna sanción. No inventarse una |
| Duplicado | Robo, pérdida o deterioro. **Conserva la fecha de caducidad original**: no alarga nada |
| Plazos | Subsanar 10 días · archivo al mes · entrega máximo 1 mes · reclamar 15 días |
| Teléfono del portal | 900 11 21 21, gratuito. **No es el del centro** |
| Precios que se pueden citar | 20 h = **120 €**, 60 h = **180 €**, polivalente 6 h = **70 €**, duplicado del título 10 € |

Todo eso vive en `_web/centro.py`. Si un dato cambia, se cambia ahí y se vuelve
a generar. **Un precio que Pedro no ha confirmado va a `None`** y la web escribe
«pídenos precio»: inventarse un número es peor que no ponerlo.

## PENDIENTES DE PEDRO

Están marcados en el código con `# PENDIENTE PEDRO`:

- **Precio del reciclaje de 4 h:** ninguno, porque el curso no existe. Los 70 €
  que venían en el andamiaje inicial son los del **polivalente de 6 horas** y se
  han movido ahí, que es donde Pedro los tiene verificados.
- **Precios sin confirmar** (hoy salen como «pídenos precio»): nivel inicial de
  8 h, 10 h de directivos, 20 h de mandos intermedios, 20 h de responsables de
  obra, 20 h de administrativos, 70 h de delegados de prevención y 4 h de
  primeros auxilios.
- **Dar de alta `renovartpc` en el servicio de formularios** del VPS
  (`/etc/formularios/config.json` y reiniciar). **Sin eso el formulario no
  entrega nada.** Es un paso de root.
- **Contenedor de medición:** `centro.py › GTM` está vacío a propósito.
  renovartpc.es no está en la tabla de la gestora (Dlega) y el contenedor lo da
  Ana, no se inventa. El enganche ya está escrito y probado en `web.js`.

## Trampas heredadas de tpc60horas-web

Esta web es copia de aquel andamiaje. Las trampas siguen siendo las mismas:

- **El minificador de CSS y el `:not()`.** Un `replace("not(", "not (")` a secas
  rompe `a:not(.btn)` y el navegador **tira la regla sin decir nada**. Por eso
  `generar.py` cuenta las llaves antes y después y se niega a generar si no
  cuadran.
- **Los degradados no se ven con `backgroundColor`.** Van en `background-image`.
  `auditar.py` saca los colores del degradado y se queda con el peor.
- **Los botones no pueden ser pastel:** letra blanca a 17 px, hacen falta 4,5:1.
- **Chrome headless en este PC no baja de ~500 px de ancho.** El corte de 420 px
  no se está probando; hay que mirarlo a mano.
- **Los siete campos del formulario van con inicial mayúscula** —Nombre, Email,
  Telefono, Curso, Mensaje, Acepto, Origen— y el servicio tira todo lo demás.
  `auditar.py` lo comprueba.

## Estructura

    _web/centro.py     datos del centro y de la TPC (aquí se cambia todo)
    _web/paginas.py    el contenido, página a página
    _web/generar.py    plantilla, minificado y montaje
    _web/auditar.py    la auditoría (fichero + Chrome), incluida la regla de oro
    estilo.css         la hoja ORIGINAL; se edita aquí y se regenera
    web.js             cookies, consentimiento, formulario y entradas

La hoja va **incrustada y minificada** en cada página (bloquea el pintado) y el
guion va **aparte con `defer`** (no lo bloquea y se guarda una vez).

## Las páginas

    /                          resumen de la renovación
    /renovar-la-tpc/           el trámite paso a paso (HowTo)
    /tpc-caducada/             caducada, robada o perdida; renovación vs duplicado
    /curso-reciclaje-4-horas/  la verdad de hoy + lista de aviso  ← la delicada
    /cursos/                   el catálogo de construcción que sí damos (Course)
    /preguntas-frecuentes/     15 preguntas (FAQPage)
    /contacto/
    /gracias/                  noindex
    /aviso-legal/ /politica-de-privacidad/ /politica-de-cookies/
