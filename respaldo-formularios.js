/* =============================================================================
   PLAN B DE LOS FORMULARIOS — Prevención Siglo 21 (18/10/2026, 3 caminos el 19/10/2026)

   El 18/10/2026 formularios.tpcmetal.es estuvo más de 3 h sin llegar desde
   España (bloqueo de LaLiga a Cloudflare) y se perdieron los formularios.
   Este fichero es el MISMO para todas las webs: nginx lo añade al final de cada
   página (snippets/respaldo-formularios.conf). Hay tres caminos, por orden:
     1. el servicio principal (formularios.tpcmetal.es, en el VPS);
     2. el receptor de respaldo del hosting de IONOS (www.prevencion.cc);
     3. la reserva de Cloudflare (Worker formularios-reserva, *.workers.dev),
        que no depende ni del VPS ni de IONOS.
   Los tres acaban en el buzón del CRM.

   - Webs que envían con fetch (la mayoría): si un camino falla (red/DNS,
     8 s sin respuesta, HTTP >= 500 o JSON sin «ok») se prueba el siguiente con
     el MISMO cuerpo y _json=1; la web recibe {ok:true}: su «gracias» y la
     conversión salen igual. Si un camino contesta ok:false (rechazo a
     propósito), se respeta: nada se duplica.
   - Webs con el envío normal del formulario: antes de enviar se mira qué camino
     está al alcance (4 s cada uno) y el formulario se envía a ese.
   - Si NINGUNO llega: el envío se guarda en este navegador (7 días), se avisa al
     visitante con los teléfonos y se reintenta solo, por los caminos 2 y 3, la
     próxima vez que abra cualquier página de la misma web. Sin conversión: el
     reintento no toca la web.
   Prueba sin crear clientes: añadir al formulario un campo _prueba=1 y bloquear
   los caminos: el 2 y el 3 lo mandan a pedro@, no al CRM.
   ========================================================================== */
(function () {
  'use strict';
  var PRINCIPAL = /^https:\/\/(formularios\.(?:tpcmetal\.es|prevencion\.cc))\/enviar\/([A-Za-z0-9._-]+)/;
  var RESPALDO = 'https://www.prevencion.cc/formularios-respaldo/enviar/';
  var RESERVA = 'https://formularios-reserva.pedro-105.workers.dev/enviar/';
  var GUARDADOS = 'respaldoFormularios.pendientes', SIETE_DIAS = 7 * 864e5;
  if (!window.fetch || window.__respaldoFormularios) return;
  window.__respaldoFormularios = '2026-10-19';
  var fetchOriginal = window.fetch.bind(window);

  function conTiempo(url, op, ms) {
    var o = {}, k;
    for (k in op) o[k] = op[k];
    if (!window.AbortController) return fetchOriginal(url, o);
    var c = new AbortController(), t = setTimeout(function () { c.abort(); }, ms);
    o.signal = c.signal;
    return fetchOriginal(url, o).then(function (r) { clearTimeout(t); return r; },
      function (e) { clearTimeout(t); throw e; });
  }

  /* Un camino «contesta» si da HTTP < 500 con un JSON que lleva «ok». Con soloOk, «ok:false» también cuenta como
     fallo (IONOS: así se prueba el Worker); sin él, «ok:false» es un rechazo que se respeta (el último camino). */
  function contesta(r, soloOk) {
    if (r.status >= 500) throw new Error('formulario: HTTP ' + r.status);
    return r.clone().json().then(function (d) {
      if (d && typeof d === 'object' && 'ok' in d && (d.ok || !soloOk)) return r;
      throw new Error('formulario: respuesta sin ok');
    });
  }

  /* El mismo cuerpo, urlencoded y con _json=1 (el receptor de IONOS es PHP y no entiende JSON; los ficheros se
     quedan fuera: los formularios son solo texto). Así también se puede guardar como texto. */
  function cuerpoRespaldo(b) {
    var u = new URLSearchParams(), k;
    if (typeof URLSearchParams !== 'undefined' && b instanceof URLSearchParams) { u = new URLSearchParams(b); }
    else if (typeof FormData !== 'undefined' && b instanceof FormData) {
      b.forEach(function (v, k2) { if (typeof v === 'string') u.append(k2, v); });
    } else if (typeof b === 'string' && /^\s*\{/.test(b)) {
      try { var o = JSON.parse(b); for (k in o) u.append(k, o[k]); } catch (e) { return null; }
    } else if (typeof b === 'string') { u = new URLSearchParams(b); }
    else return null;
    u.set('_json', '1');
    return u;
  }

  /* Caminos 2 y 3 en orden; si los dos fallan, se guarda en el navegador y se avisa. */
  function aLasReservas(sitio, cuerpo, guardarSiFalla) {
    function por(base, soloOk) {
      return conTiempo(base + sitio, { method: 'POST', body: new URLSearchParams(cuerpo) }, 8000)
        .then(function (r) { return contesta(r, soloOk); });
    }
    return por(RESPALDO, true).catch(function () { return por(RESERVA, false); }).catch(function (e) {
      if (guardarSiFalla) { guardar(sitio, cuerpo); avisar(); }
      throw e;
    });
  }

  /* ---------- Guardado en el navegador y reintento (7 días) ---------- */
  function leer() {
    try {
      var l = JSON.parse(localStorage.getItem(GUARDADOS) || '[]'), ahora = Date.now();
      return Array.isArray(l) ? l.filter(function (x) { return x && x.s && x.c && ahora - x.t < SIETE_DIAS; }) : [];
    } catch (e) { return []; }
  }
  function escribir(l) {
    try { if (l.length) localStorage.setItem(GUARDADOS, JSON.stringify(l)); else localStorage.removeItem(GUARDADOS); } catch (e) { }
  }
  function guardar(sitio, cuerpo) {
    var l = leer();
    l.push({ s: sitio, c: cuerpo.toString(), t: Date.now() });
    escribir(l.slice(-5));
  }
  /* ponytail: dos pestañas abiertas a la vez podrían reintentar el mismo envío (se «reserva» la lista al empezar,
     pero no hay cerrojo entre pestañas). Como mucho llega dos veces al CRM, que deduplica por teléfono/email. */
  function reintentar() {
    var l = leer();
    if (!l.length) return;
    escribir([]);
    var quedan = [];
    l.reduce(function (p, x) {
      return p.then(function () {
        return aLasReservas(x.s, new URLSearchParams(x.c), false).catch(function () { quedan.push(x); });
      });
    }, Promise.resolve()).then(function () { escribir(leer().concat(quedan)); });
  }

  /* Aviso al visitante, con los teléfonos de la propia página (o el del centro si no hay). */
  function avisar() {
    if (document.getElementById('respaldo-formularios-aviso')) return;
    var tels = [], vistos = {}, a = document.querySelectorAll('a[href^="tel:"]'), i;
    for (i = 0; i < a.length && tels.length < 3; i++) {
      var num = a[i].getAttribute('href').replace(/[^0-9+]/g, '');
      if (num && !vistos[num]) { vistos[num] = 1; tels.push(num); }
    }
    if (!tels.length) tels.push('+34916170423');
    var d = document.createElement('div'), p = document.createElement('p'), b = document.createElement('button');
    d.id = 'respaldo-formularios-aviso';
    d.setAttribute('role', 'alert');
    d.style.cssText = 'position:fixed;left:12px;right:12px;bottom:12px;z-index:2147483647;max-width:560px;margin:0 auto;' +
      'background:#fff;color:#111;border:2px solid #b3261e;border-radius:10px;padding:14px 16px;font:16px/1.45 system-ui,sans-serif;' +
      'box-shadow:0 6px 24px rgba(0,0,0,.25)';
    p.style.margin = '0 0 8px';
    p.textContent = 'No hemos podido enviar tu solicitud ahora mismo. La hemos guardado en este navegador e ' +
      'intentaremos enviarla de nuevo automáticamente la próxima vez que entres en esta web (durante 7 días). ' +
      'Si es urgente, llámanos: ';
    tels.forEach(function (t, j) {
      var l = document.createElement('a');
      l.href = 'tel:' + t;
      l.textContent = t.replace(/^\+34/, '').replace(/(\d{3})(\d{2})(\d{2})(\d{2})/, '$1 $2 $3 $4');
      l.style.cssText = 'color:#0b57d0;font-weight:700;white-space:nowrap';
      p.appendChild(l);
      p.appendChild(document.createTextNode(j < tels.length - 1 ? ' · ' : '.'));
    });
    b.type = 'button';
    b.textContent = 'Cerrar';
    b.style.cssText = 'font:inherit;padding:6px 14px;border:1px solid #555;border-radius:6px;background:#f3f3f3;color:#111;cursor:pointer';
    b.onclick = function () { d.parentNode.removeChild(d); };
    d.appendChild(p);
    d.appendChild(b);
    (document.body || document.documentElement).appendChild(d);
  }

  /* Unas 10 webs miran ANTES de enviar si el principal está vivo (fetch a /salud) y, si no, enseñan «Ahora mismo no
     podemos recibir el formulario» y NO envían. Si /salud falla, se les dice que sí (así envían) y el envío va directo
     a las reservas; si tampoco llegan, queda guardado en el navegador (mejor que perderlo). */
  var SALUD = /^https:\/\/formularios\.(?:tpcmetal\.es|prevencion\.cc)\/salud/;

  window.fetch = function (url, op) {
    var u0 = typeof url === 'string' ? url : (url && url.url) || '';
    if (SALUD.test(u0)) {
      var o = {}, k;
      for (k in op) if (k !== 'signal') o[k] = op[k];   /* sin su temporizador: el de aquí es de 6 s */
      return conTiempo(url, o, 6000).catch(function () {
        window.__formulariosAlRespaldo = true;
        return new Response('ok (respaldo)', { status: 200 });
      });
    }
    var m = PRINCIPAL.exec(u0);
    if (!m || !op || String(op.method || '').toUpperCase() !== 'POST') return fetchOriginal(url, op);
    var cuerpo = cuerpoRespaldo(op.body);
    function alRespaldo(motivo) {
      if (cuerpo === null) throw motivo instanceof Error ? motivo : new Error('formulario: sin respaldo posible');
      return aLasReservas(m[2], cuerpo, true);
    }
    if (window.__formulariosAlRespaldo && cuerpo !== null) return alRespaldo();
    return conTiempo(url, op, 8000).then(function (r) {
      if (r.status >= 500) return alRespaldo();
      return r.clone().json().then(function (d) {
        return d && typeof d === 'object' && 'ok' in d ? r : alRespaldo();
      }, function () { return r; });   /* no es JSON (p. ej. la web no pidió _json): lo trata la web */
    }, alRespaldo);
  };

  /* ¿Llega algo a esa dirección? (HEAD no-cors: cualquier respuesta vale, aunque sea un 501 o un 503). */
  function alcanza(url) {
    return conTiempo(url, { method: 'HEAD', mode: 'no-cors', cache: 'no-store' }, 4000).then(function () { return true; }, function () { return false; });
  }

  /* Envío normal del formulario (sin fetch): se escucha en window, que va DESPUÉS de los manejadores de la web;
     si alguno ya lo paró (porque lo envía él con fetch), no se hace nada. */
  window.addEventListener('submit', function (e) {
    var f = e.target, m = f && f.action && PRINCIPAL.exec(f.action);
    if (!m || e.defaultPrevented || f.__respaldoMirado) return;
    e.preventDefault();
    function enviar(destino) {
      f.__respaldoMirado = true;
      if (destino) f.action = destino;
      HTMLFormElement.prototype.submit.call(f);
    }
    (window.__formulariosAlRespaldo ? Promise.resolve(false) : alcanza('https://' + m[1] + '/widget/seo.js'))
      .then(function (ok) {
        if (ok) return enviar();
        return alcanza(RESPALDO + 'salud').then(function (ok2) {
          if (ok2) return enviar(RESPALDO + m[2]);
          return alcanza(RESERVA.replace('/enviar/', '/salud')).then(function (ok3) {
            if (ok3) return enviar(RESERVA + m[2]);
            var u = new URLSearchParams();
            new FormData(f).forEach(function (v, k) { if (typeof v === 'string') u.append(k, v); });
            u.set('_json', '1');
            guardar(m[2], u);
            avisar();
          });
        });
      });
  });

  if (document.readyState === 'complete') setTimeout(reintentar, 3000);
  else window.addEventListener('load', function () { setTimeout(reintentar, 3000); });
}());
