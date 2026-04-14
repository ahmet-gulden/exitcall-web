// Replace native <select> lang-switch with custom button+dropdown (avoids browser-native arrows)
(function() {
  function initLangDropdown() {
    var select = document.querySelector('select.lang-switch');
    if (!select) return;
    var wrap = select.parentElement;
    var selected = select.options[select.selectedIndex];

    var btn = document.createElement('button');
    btn.className = 'lang-switch-btn';
    btn.type = 'button';
    btn.setAttribute('aria-haspopup', 'listbox');
    btn.setAttribute('aria-expanded', 'false');
    btn.innerHTML =
      '<span>' + (selected ? selected.text : '') + '</span>' +
      '<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 16 16" fill="currentColor"><path d="M8 11L3 6h10z"/></svg>';

    var menu = document.createElement('ul');
    menu.className = 'lang-switch-menu';
    menu.setAttribute('role', 'listbox');
    for (var i = 0; i < select.options.length; i++) {
      var opt = select.options[i];
      var li = document.createElement('li');
      var a = document.createElement('a');
      a.href = opt.value;
      a.textContent = opt.text;
      if (opt.selected) { li.setAttribute('aria-selected', 'true'); a.className = 'active'; }
      li.appendChild(a);
      menu.appendChild(li);
    }

    wrap.replaceChild(btn, select);
    wrap.appendChild(menu);

    btn.addEventListener('click', function(e) {
      e.stopPropagation();
      var open = menu.classList.toggle('open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    document.addEventListener('click', function() {
      menu.classList.remove('open');
      btn.setAttribute('aria-expanded', 'false');
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initLangDropdown);
  } else {
    initLangDropdown();
  }
})();

// Handle ?lang=XX&from=app parameters from in-app browser
(function() {
  var params = new URLSearchParams(window.location.search);
  var fromApp = params.get('from') === 'app';
  var lang = params.get('lang');

  // Hide language picker + app install prompts when opened from app
  if (fromApp) {
    document.body.classList.add('from-app');
    // Remove Safari Smart App Banner
    var smartBanner = document.querySelector('meta[name="apple-itunes-app"]');
    if (smartBanner) smartBanner.remove();
  }

  // Redirect to correct locale if needed
  if (lang) {
    var locales = ['ar','de','es','fr','hi','it','ja','ko','pt-BR','ru','tr','zh-Hans'];
    var path = window.location.pathname;
    // Determine current locale from path
    var currentLocale = 'en';
    for (var i = 0; i < locales.length; i++) {
      if (path.indexOf('/' + locales[i] + '/') === 0) {
        currentLocale = locales[i];
        break;
      }
    }

    if (lang !== currentLocale && (lang === 'en' || locales.indexOf(lang) !== -1)) {
      // Build target path — ensure .html extension for GitHub Pages
      var pageName = path.split('/').pop() || 'index.html';
      if (pageName === '' || pageName === currentLocale) pageName = 'index.html';
      if (pageName.indexOf('.') === -1) pageName += '.html';
      var targetPath = lang === 'en' ? '/' + pageName : '/' + lang + '/' + pageName;
      // Preserve query params (keep from=app, remove lang)
      var newParams = new URLSearchParams(params);
      newParams.delete('lang');
      var qs = newParams.toString();
      window.location.replace(targetPath + (qs ? '?' + qs : ''));
    }
  }
})();
