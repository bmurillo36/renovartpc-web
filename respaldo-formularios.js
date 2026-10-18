/* =============================================================================
   PLAN B DE LOS FORMULARIOS — Prevención Siglo 21 (18/10/2026)

   El 18/10/2026 formularios.tpcmetal.es estuvo más de 3 h sin llegar desde
   España (bloqueo de LaLiga a Cloudflare) y se perdieron los formularios.
   Este fichero es el MISMO para todas las webs: nginx lo añade al final de cada
   página (snippets/respaldo-formularios.conf). Si el servicio principal no
   responde, el envío va al receptor de respaldo del hosting de IONOS (otro
   proveedor), que lo manda al buzón del CRM.

   - Webs que envían con fetch (la mayoría): si el principal falla (red/DNS,
     8 s sin respuesta, HTTP >= 500 o JSON sin «ok»), el MISMO cuerpo se manda
     al respaldo con _json=1 y la web recibe {ok:true}: su «gracias» y la
     conversión salen igual. Si el principal contesta ok (o ok:false, que es un
     rechazo suyo a propósito), no se toca: nada se duplica.
   - Webs con el envío normal del formulario: antes de enviar se mira si el
     principal está al alcance (4 s); si no, el formulario se envía al respaldo.
   Prueba sin crear clientes: añadir al formulario un campo _prueba=1 y bloquear
   formularios.tpcmetal.es: el respaldo lo manda a pedro@, no al CRM.
   ========================================================================== */
(function () {
  'use strict';
  var PRINCIPAL = /^https:\/\/(formularios\.(?:tpcmetal\.es|prevencion\.cc))\/enviar\/([A-Za-z0-9._-]+)/;
  var RESPALDO = 'https://www.prevencion.cc/formularios-respaldo/enviar/';
  if (!window.fetch || window.__respaldoFormularios) return;
  window.__respaldoFormularios = '2026-10-18';
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

  /* El mismo cuerpo, con _json=1. El receptor de respaldo es PHP: entiende urlencoded y multipart, no JSON. */
  function cuerpoRespaldo(b) {
    var u, k;
    if (typeof URLSearchParams !== 'undefined' && b instanceof URLSearchParams) { u = new URLSearchParams(b); }
    else if (typeof FormData !== 'undefined' && b instanceof FormData) {
      var f = new FormData();
      b.forEach(function (v, k2) { f.append(k2, v); });
      f.set('_json', '1');
      return f;
    } else if (typeof b === 'string' && /^\s*\{/.test(b)) {
      try { var o = JSON.parse(b); u = new URLSearchParams(); for (k in o) u.append(k, o[k]); } catch (e) { return null; }
    } else if (typeof b === 'string') { u = new URLSearchParams(b); }
    else return null;
    u.set('_json', '1');
    return u;
  }

  /* Unas 10 webs miran ANTES de enviar si el principal está vivo (fetch a /salud) y, si no, enseñan «Ahora mismo no
     podemos recibir el formulario» y NO envían. Si /salud falla pero el respaldo responde, se les dice que sí (así
     envían) y se marca que el envío tiene que ir al respaldo. Si el respaldo tampoco responde, la web decide como antes. */
  var SALUD = /^https:\/\/formularios\.(?:tpcmetal\.es|prevencion\.cc)\/salud/;
  function respaldoVivo(e) {
    return fetchOriginal(RESPALDO + 'salud', { mode: 'no-cors', cache: 'no-store' })
      .then(function (r) { window.__formulariosAlRespaldo = true; return r; }, function () { throw e; });
  }

  window.fetch = function (url, op) {
    var u0 = typeof url === 'string' ? url : (url && url.url) || '';
    if (SALUD.test(u0)) {
      var o = {}, k;
      for (k in op) if (k !== 'signal') o[k] = op[k];   /* sin su temporizador: el de aquí es de 6 s */
      return conTiempo(url, o, 6000).catch(respaldoVivo);
    }
    var m = PRINCIPAL.exec(u0);
    if (!m || !op || String(op.method || '').toUpperCase() !== 'POST') return fetchOriginal(url, op);
    var cuerpo = cuerpoRespaldo(op.body);
    function alRespaldo(motivo) {
      if (cuerpo === null) throw motivo instanceof Error ? motivo : new Error('formulario: sin respaldo posible');
      return fetchOriginal(RESPALDO + m[2], { method: 'POST', body: cuerpo });
    }
    if (window.__formulariosAlRespaldo && cuerpo !== null) return alRespaldo();
    return conTiempo(url, op, 8000).then(function (r) {
      if (r.status >= 500) return alRespaldo();
      return r.clone().json().then(function (d) {
        return d && typeof d === 'object' && 'ok' in d ? r : alRespaldo();
      }, function () { return r; });   /* no es JSON (p. ej. la web no pidió _json): lo trata la web */
    }, alRespaldo);
  };

  /* Envío normal del formulario (sin fetch): se escucha en window, que va DESPUÉS de los manejadores de la web;
     si alguno ya lo paró (porque lo envía él con fetch), no se hace nada. */
  window.addEventListener('submit', function (e) {
    var f = e.target, m = f && f.action && PRINCIPAL.exec(f.action);
    if (!m || e.defaultPrevented || f.__respaldoMirado) return;
    if (window.__formulariosAlRespaldo) { f.action = RESPALDO + m[2]; return; }   /* ya se sabe: directo al respaldo */
    e.preventDefault();
    var hecho = false;
    function enviar(llega) {
      if (hecho) return;
      hecho = true;
      f.__respaldoMirado = true;
      if (!llega) f.action = RESPALDO + m[2];
      HTMLFormElement.prototype.submit.call(f);
    }
    setTimeout(function () { enviar(false); }, 4000);
    fetchOriginal('https://' + m[1] + '/widget/seo.js', { method: 'HEAD', mode: 'no-cors', cache: 'no-store' })
      .then(function () { enviar(true); }, function () { enviar(false); });
  });
}());
