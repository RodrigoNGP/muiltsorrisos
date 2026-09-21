(function () {
  var WA_NUMBER = '5581996855675';

  function waLink(text) {
    return 'https://wa.me/' + WA_NUMBER + '?text=' + encodeURIComponent(text);
  }

  // Eventos de conversão: GTM/GA4 (dataLayer), Google Ads (gtag) e Meta (fbq)
  function track(event, params) {
    params = params || {};
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push(Object.assign({ event: event }, params));
    if (typeof window.gtag === 'function') window.gtag('event', event, params);
    if (typeof window.fbq === 'function') {
      window.fbq('track', event === 'generate_lead' ? 'Lead' : 'Contact', params);
    }
  }

  function sectionOf(el) {
    var section = el.closest('section[id], header, footer, .mobile-bar, .wa-float');
    if (!section) return 'pagina';
    return section.id || section.className.split(' ')[0] || section.tagName.toLowerCase();
  }

  // Botões com data-wa abrem o WhatsApp com a mensagem pré-preenchida
  document.querySelectorAll('[data-wa]').forEach(function (el) {
    el.href = waLink(el.getAttribute('data-wa'));
    el.target = '_blank';
    el.rel = 'noopener';
    el.addEventListener('click', function () { track('whatsapp_click', { location: sectionOf(el) }); });
  });

  document.querySelectorAll('[data-track="phone_click"]').forEach(function (el) {
    el.addEventListener('click', function () { track('phone_click', { location: sectionOf(el) }); });
  });

  // Header com sombra ao rolar
  var header = document.querySelector('.header');
  function onScroll() { header.classList.toggle('is-scrolled', window.scrollY > 10); }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // Antes e depois
  document.querySelectorAll('[data-ba]').forEach(function (ba) {
    var range = ba.querySelector('input');
    function update() { ba.style.setProperty('--pos', range.value + '%'); }
    range.addEventListener('input', update);
    update();
  });

  // Carrossel (equipe)
  document.querySelectorAll('[data-carousel]').forEach(function (carousel) {
    var track = carousel.querySelector('[data-carousel-track]');
    var prev = carousel.querySelector('[data-carousel-prev]');
    var next = carousel.querySelector('[data-carousel-next]');
    var dotsBox = carousel.querySelector('[data-carousel-dots]');
    var items = track.children;
    var step = 0;
    var positions = 0;

    function measure() {
      var gap = parseFloat(getComputedStyle(track).columnGap) || 0;
      step = items[0].getBoundingClientRect().width + gap;
      var max = track.scrollWidth - track.clientWidth;
      positions = max > 1 ? Math.round(max / step) + 1 : 1;

      dotsBox.textContent = '';
      for (var i = 0; i < positions; i++) {
        var dot = document.createElement('button');
        dot.type = 'button';
        dot.className = 'carousel__dot';
        dot.setAttribute('aria-label', 'Ir para a posição ' + (i + 1));
        dot.addEventListener('click', goTo.bind(null, i));
        dotsBox.appendChild(dot);
      }
      dotsBox.hidden = positions < 2;
      update();
    }

    function current() { return Math.min(positions - 1, Math.round(track.scrollLeft / step)); }

    function goTo(i) {
      i = Math.max(0, Math.min(positions - 1, i));
      track.scrollTo({ left: i * step, behavior: 'smooth' });
    }

    function update() {
      var i = current();
      var max = track.scrollWidth - track.clientWidth;
      prev.disabled = track.scrollLeft <= 4;
      next.disabled = track.scrollLeft >= max - 4;
      Array.prototype.forEach.call(dotsBox.children, function (dot, n) {
        dot.classList.toggle('is-active', n === i);
        dot.setAttribute('aria-current', n === i ? 'true' : 'false');
      });
    }

    prev.addEventListener('click', function () { goTo(current() - 1); });
    next.addEventListener('click', function () { goTo(current() + 1); });
    track.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') { e.preventDefault(); goTo(current() + 1); }
      if (e.key === 'ArrowLeft') { e.preventDefault(); goTo(current() - 1); }
    });

    track.addEventListener('scroll', update, { passive: true });

    var resizeTimer;
    window.addEventListener('resize', function () {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(measure, 150);
    });
    measure();
  });

  // Avaliações do Google: "Ler mais" nos textos longos
  document.querySelectorAll('.gcard__more').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var open = btn.closest('.gcard').classList.toggle('is-expanded');
      btn.textContent = open ? 'Ler menos' : 'Ler mais';
    });
  });

  // Animação de entrada
  var items = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('is-visible'); io.unobserve(e.target); }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });
    items.forEach(function (el) { io.observe(el); });
  } else {
    items.forEach(function (el) { el.classList.add('is-visible'); });
  }

  // Formulários -> WhatsApp
  document.querySelectorAll('[data-lead-form]').forEach(function (form) {
    var tel = form.querySelector('input[name="telefone"]');
    var error = form.querySelector('.form__error');

    tel.addEventListener('input', function () {
      var d = tel.value.replace(/\D/g, '').slice(0, 11);
      var out = d;
      if (d.length > 2) out = '(' + d.slice(0, 2) + ') ' + d.slice(2);
      if (d.length > 7) out = '(' + d.slice(0, 2) + ') ' + d.slice(2, 7) + '-' + d.slice(7);
      tel.value = out;
    });

    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var nome = form.nome.value.trim();
      var fone = tel.value.replace(/\D/g, '');
      if (!nome || fone.length < 10) { error.hidden = false; return; }
      error.hidden = true;
      var msg = 'Olá! Vim através do site e gostaria de agendar uma avaliação.\n\n' +
        'Nome: ' + nome + '\n' +
        'WhatsApp: ' + tel.value + '\n' +
        'Especialidade: ' + form.interesse.value + '\n' +
        'Melhor período: ' + form.periodo.value;
      track('generate_lead', { location: 'formulario', interesse: form.interesse.value });
      window.open(waLink(msg), '_blank', 'noopener');
    });
  });
})();
