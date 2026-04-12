// Handle ?lang=XX&from=app parameters from in-app browser
(function() {
  var params = new URLSearchParams(window.location.search);
  var fromApp = params.get('from') === 'app';
  var lang = params.get('lang');

  // Hide language picker when opened from app
  if (fromApp) {
    document.body.classList.add('from-app');
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
