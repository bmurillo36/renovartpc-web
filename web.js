/* ==========================================================================
   renovartpc.es — cookies, medición, formulario y entradas suaves.

   Sin librerías y sin nada que se pueda caer desde fuera: son doscientas
   líneas y una petición menos es una cosa menos que puede fallar.

   LO IMPORTANTE, EN ORDEN:

   1. EL CONSENTIMIENTO SE DECLARA ANTES QUE NADA. Se le dice a Google
      «denegado» en cuanto arranca la página. Así, si algún día se pone un
      contenedor, los pings que salgan de quien no ha aceptado van sin
      cookies. Cargar Analytics o Ads antes de que el visitante diga que sí
      es exactamente lo que sanciona la AEPD.

   2. NO HAY CONTENEDOR TODAVÍA, Y ES A PROPÓSITO. La regla de Pedro del
      09/09/2026 dice que la tabla de la gestora (dlega) manda y que no se
      inventa un contenedor. renovartpc.es NO está en esa tabla. Cuando le
      den uno, se escribe en centro.py y esto ya funciona: no hay que tocar
      nada más.

   3. EL AVISO DE COOKIES ES DE ESTA WEB, no el compartido del servidor.
      Igual que en tpc20horas.es, la hermana más reciente: así no hay ni una
      petición a otro dominio y el aviso va con los colores de la casa. El
      precio de esto es que el texto legal vive aquí: si cambia, cambia aquí.

   4. RECHAZAR ES TAN FÁCIL COMO ACEPTAR. Los dos botones se ven igual de
      bien, como exige la guía de cookies de la AEPD. Y se puede cambiar de
      opinión desde el pie, en cualquier momento.
   ========================================================================== */

(function () {
  'use strict';

  var CLAVE = 'renovartpc.cookies';
  var MESES = 24;                 // el consentimiento caduca a los 24 meses
  var quieto = window.matchMedia &&
               matchMedia('(prefers-reduced-motion: reduce)').matches;

  document.documentElement.classList.add('js');

  /* ---------- 1. Modo de consentimiento, lo primero de todo ---------- */

  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }

  gtag('consent', 'default', {
    ad_storage: 'denied',
    ad_user_data: 'denied',
    ad_personalization: 'denied',
    analytics_storage: 'denied',
    functionality_storage: 'granted',
    security_storage: 'granted',
    wait_for_update: 500
  });

  function decision() {
    try {
      var g = JSON.parse(localStorage.getItem(CLAVE) || 'null');
      if (!g || !g.ts) return null;
      if (Date.now() - g.ts > MESES * 30 * 24 * 3600 * 1000) return null;
      return g;
    } catch (e) { return null; }
  }

  function guardar(acepta) {
    try { localStorage.setItem(CLAVE, JSON.stringify({ ts: Date.now(), medicion: !!acepta })); }
    catch (e) { /* navegación privada: se respeta la decisión solo esta visita */ }
    if (acepta) {
      gtag('consent', 'update', {
        ad_storage: 'granted', ad_user_data: 'granted',
        ad_personalization: 'granted', analytics_storage: 'granted'
      });
      cargarMedicion();
    }
  }

  /* El contenedor se mete aquí y SOLO aquí. Con GTM vacío no hace nada, que
     es lo que toca hasta que la gestora diga cuál es el de esta web. */
  var medicionPuesta = false;
  function cargarMedicion() {
    var GTM = document.documentElement.getAttribute('data-gtm') || '';
    if (!GTM || medicionPuesta) return;
    medicionPuesta = true;
    window.dataLayer.push({ 'gtm.start': Date.now(), event: 'gtm.js' });
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtm.js?id=' + GTM;
    document.head.appendChild(s);
  }

  /* ---------- 2. El aviso ---------- */

  function pintarAviso() {
    if (document.getElementById('cookies')) return;

    var caja = document.createElement('div');
    caja.id = 'cookies';
    caja.className = 'cookies';
    caja.setAttribute('role', 'dialog');
    caja.setAttribute('aria-live', 'polite');
    caja.setAttribute('aria-label', 'Aviso de cookies');
    caja.innerHTML =
      '<div class="cookies__in">' +
        '<div class="cookies__texto">' +
          '<strong>Cookies</strong>' +
          '<p>Usamos cookies propias para que la web funcione y, si nos dejas, ' +
          'de medición para saber qué páginas sirven de algo. Puedes rechazarlas ' +
          'y la web funciona igual. Tienes el detalle en la ' +
          '<a href="/politica-de-cookies/">política de cookies</a>.</p>' +
        '</div>' +
        '<div class="cookies__botones">' +
          '<button type="button" class="btn btn--linea" data-cookies="no">Rechazar</button>' +
          '<button type="button" class="btn btn--salvia" data-cookies="si">Aceptar</button>' +
        '</div>' +
      '</div>';
    document.body.appendChild(caja);
    requestAnimationFrame(function () { caja.classList.add('visible'); });

    caja.addEventListener('click', function (e) {
      var b = e.target.closest('[data-cookies]');
      if (!b) return;
      guardar(b.getAttribute('data-cookies') === 'si');
      caja.classList.remove('visible');
      setTimeout(function () { caja.remove(); }, 260);
    });
  }

  var ya = decision();
  if (!ya) pintarAviso();
  else if (ya.medicion) {
    gtag('consent', 'update', {
      ad_storage: 'granted', ad_user_data: 'granted',
      ad_personalization: 'granted', analytics_storage: 'granted'
    });
    cargarMedicion();
  }

  /* Cambiar de opinión desde el pie */
  document.addEventListener('click', function (e) {
    if (!e.target.closest('[data-abrir-cookies]')) return;
    e.preventDefault();
    try { localStorage.removeItem(CLAVE); } catch (err) {}
    pintarAviso();
  });

  /* ---------- 3. Aparecer al bajar ---------- */

  var flojos = [].slice.call(document.querySelectorAll('.aparece'));
  if (flojos.length) {
    if (quieto || !('IntersectionObserver' in window)) {
      flojos.forEach(function (e) { e.classList.add('visible'); });
    } else {
      var ojo = new IntersectionObserver(function (entradas) {
        entradas.forEach(function (x) {
          if (!x.isIntersecting) return;
          // Un pelín de retraso entre hermanos: entran en cascada, no de golpe.
          var i = +(x.target.getAttribute('data-orden') || 0);
          setTimeout(function () { x.target.classList.add('visible'); }, i * 70);
          ojo.unobserve(x.target);
        });
      }, { rootMargin: '0px 0px -60px 0px' });
      flojos.forEach(function (e) { ojo.observe(e); });
    }
  }

  /* ---------- 4. El menú del móvil ---------- */

  var check = document.getElementById('abrir-menu');
  if (check) {
    // Al pulsar un enlace, que se cierre solo: si no, tapa la página entera.
    document.querySelectorAll('.nav a').forEach(function (a) {
      a.addEventListener('click', function () { check.checked = false; });
    });
  }

  /* ---------- 5. El formulario ----------
     El envío NO se intercepta: es un POST normal del navegador, y el servicio
     contesta con una redirección a /gracias/.

     Antes se mandaba por fetch y se enseñaba un mensaje en la misma página. Se
     quitó el 13/09/2026, por decisión de Pedro, y por tres razones:

       1. Nunca se llegaba a /gracias/, que es la página que le confirma al
          cliente que lo suyo ha entrado. Las demás webs del centro sí van ahí.
       2. Sin visita a /gracias/ no hay forma de contar conversiones el día que
          esta web tenga medición.
       3. Un POST normal funciona AUNQUE ESTE FICHERO NO LLEGUE A CARGAR. Con el
          fetch, si fallaba el JavaScript, el formulario no enviaba nada y nadie
          se enteraba. Un formulario es lo último que puede depender de un
          guion: cada envío perdido es un cliente perdido.

     Lo único que se sigue haciendo aquí es poner el sello antispam. */

  var form = document.querySelector('form.form');
  if (form) {
    // El sello que puede pedir el servicio: la hora en que se cargó la página,
    // en base 36. Solo se comprueba si el sitio está dado de alta con
    // "requiere_js": true; hoy NO lo está, a propósito, para que quien entre
    // sin JavaScript pueda escribir igual. Se deja puesto para poder encenderlo
    // el día que el spam lo pida, sin tocar la web.
    var sello = form.querySelector('input[name=_t]');
    if (sello) sello.value = Date.now().toString(36);
  }

  /* ---------- 6. La linterna ----------
     El circulo de luz que sigue al cursor. La posicion se pasa al CSS en
     --mx/--my; si este guion no llega a cargar, el CSS deja la luz centrada
     y se sigue viendo bien, solo que quieta. */

  var conLuz = [].slice.call(document.querySelectorAll('.linterna'));
  if (conLuz.length && !quieto) {
    conLuz.forEach(function (e) {
      e.addEventListener('pointermove', function (ev) {
        // getBoundingClientRect en cada movimiento seria caro; se apunta el
        // sitio y se pinta en el siguiente fotograma.
        if (e._pedido) return;
        e._pedido = true;
        requestAnimationFrame(function () {
          var c = e.getBoundingClientRect();
          e.style.setProperty('--mx', (ev.clientX - c.left) + 'px');
          e.style.setProperty('--my', (ev.clientY - c.top) + 'px');
          e._pedido = false;
        });
      }, { passive: true });
    });
  }

  /* ---------- 6. El año del pie ---------- */

  var a = document.getElementById('anyo');
  if (a) a.textContent = new Date().getFullYear();
})();
