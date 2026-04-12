#!/usr/bin/env python3
"""Generate localized HTML pages for exitcall.app from translations.json."""

import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
TRANSLATIONS_FILE = os.path.join(SCRIPT_DIR, "translations.json")

# Locale metadata
LOCALE_META = {
    "en":      {"html_lang": "en",    "dir": "ltr", "name": "English",    "hreflang": "en"},
    "ar":      {"html_lang": "ar",    "dir": "rtl", "name": "العربية",    "hreflang": "ar"},
    "de":      {"html_lang": "de",    "dir": "ltr", "name": "Deutsch",    "hreflang": "de"},
    "es":      {"html_lang": "es",    "dir": "ltr", "name": "Español",    "hreflang": "es"},
    "fr":      {"html_lang": "fr",    "dir": "ltr", "name": "Français",   "hreflang": "fr"},
    "hi":      {"html_lang": "hi",    "dir": "ltr", "name": "हिन्दी",       "hreflang": "hi"},
    "it":      {"html_lang": "it",    "dir": "ltr", "name": "Italiano",   "hreflang": "it"},
    "ja":      {"html_lang": "ja",    "dir": "ltr", "name": "日本語",      "hreflang": "ja"},
    "ko":      {"html_lang": "ko",    "dir": "ltr", "name": "한국어",       "hreflang": "ko"},
    "pt-BR":   {"html_lang": "pt-BR", "dir": "ltr", "name": "Português",  "hreflang": "pt-BR"},
    "ru":      {"html_lang": "ru",    "dir": "ltr", "name": "Русский",    "hreflang": "ru"},
    "tr":      {"html_lang": "tr",    "dir": "ltr", "name": "Türkçe",     "hreflang": "tr"},
    "zh-Hans": {"html_lang": "zh-Hans","dir": "ltr","name": "简体中文",    "hreflang": "zh-Hans"},
}

# Map locale to directory name (en = root, others = /{locale}/)
def locale_dir(locale):
    if locale == "en":
        return ""
    return locale + "/"

def locale_prefix(locale):
    """URL prefix for a locale."""
    if locale == "en":
        return "/"
    return f"/{locale}/"

def t(strings, key, locale):
    """Get translated string."""
    return strings.get(key, {}).get(locale, strings.get(key, {}).get("en", f"[{key}]"))

def build_hreflang_tags(page_name, all_locales):
    """Build hreflang link tags for a page."""
    tags = []
    for loc in all_locales:
        href = f"https://exitcall.app/{locale_dir(loc)}{page_name}"
        hl = LOCALE_META[loc]["hreflang"]
        tags.append(f'  <link rel="alternate" hreflang="{hl}" href="{href}">')
    # x-default points to English
    tags.append(f'  <link rel="alternate" hreflang="x-default" href="https://exitcall.app/{page_name}">')
    return "\n".join(tags)

def build_lang_switcher(current_locale, page_name, strings):
    """Build language switcher HTML."""
    options = []
    for loc in ["en"] + sorted([l for l in LOCALE_META if l != "en"]):
        meta = LOCALE_META[loc]
        href = f"/{locale_dir(loc)}{page_name}"
        selected = ' class="active"' if loc == current_locale else ''
        options.append(f'<option value="{href}"{" selected" if loc == current_locale else ""}>{meta["name"]}</option>')
    return f'''<select class="lang-switch" onchange="window.location.href=this.value" aria-label="{t(strings, 'lang_switch_label', current_locale)}">
        {"".join(options)}
      </select>'''

def asset_prefix(locale):
    """Prefix for static assets (images, css) — localized pages are in subdirs."""
    if locale == "en":
        return ""
    return "../"

def build_header(locale, page_name, strings, is_index=False):
    """Build the common header/nav."""
    ap = asset_prefix(locale)
    features_href = f"{locale_prefix(locale)}#features" if is_index else f"{locale_prefix(locale)}index.html#features"
    if is_index:
        features_href = "#features"

    faq_href = f"{locale_prefix(locale)}faq.html"
    support_href = f"{locale_prefix(locale)}support.html"
    home_href = locale_prefix(locale)

    lang_switch = build_lang_switcher(locale, page_name, strings)

    return f'''  <header class="site-header">
    <div class="container">
      <a href="{home_href}" class="site-logo"><img src="{ap}app-icon-64.png" alt="ExitCall icon" width="32" height="32">ExitCall</a>
      <nav class="site-nav">
        <a href="{features_href if is_index else locale_prefix(locale) + 'index.html#features'}">{t(strings, "nav_features", locale)}</a>
        <a href="{faq_href}">{t(strings, "nav_faq", locale)}</a>
        <a href="{support_href}">{t(strings, "nav_support", locale)}</a>
        {lang_switch}
      </nav>
    </div>
  </header>'''

def build_footer(locale, strings):
    """Build the common footer."""
    lp = locale_prefix(locale)
    return f'''  <footer class="site-footer">
    <div class="container">
      <div class="footer-links">
        <a href="{lp}privacy.html">{t(strings, "footer_privacy", locale)}</a>
        <a href="{lp}terms.html">{t(strings, "footer_terms", locale)}</a>
        <a href="{lp}eula.html">{t(strings, "footer_eula", locale)}</a>
        <a href="{lp}faq.html">{t(strings, "nav_faq", locale)}</a>
        <a href="{lp}support.html">{t(strings, "nav_support", locale)}</a>
      </div>
      <p>{t(strings, "footer_copyright", locale)}</p>
    </div>
  </footer>'''

def build_head(locale, page_name, strings, title, description, all_locales, extra_head=""):
    """Build <head> section."""
    ap = asset_prefix(locale)
    meta = LOCALE_META[locale]
    canonical = f"https://exitcall.app/{locale_dir(locale)}{page_name}"
    hreflang = build_hreflang_tags(page_name, all_locales)

    return f'''<!DOCTYPE html>
<html lang="{meta['html_lang']}"{' dir="rtl"' if meta['dir'] == 'rtl' else ''}>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <link rel="canonical" href="{canonical}">
{hreflang}
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="{meta['html_lang'].replace('-', '_')}">
  <meta property="og:image" content="https://exitcall.app/app-icon-180.png">
  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{description}">
  <meta name="apple-itunes-app" content="app-id=0000000000">
  <meta name="robots" content="index, follow">
  <link rel="icon" type="image/png" href="{ap}favicon.png">
  <link rel="apple-touch-icon" href="{ap}app-icon-180.png">
  <link rel="stylesheet" href="{ap}style.css">
{extra_head}</head>'''


# ── Page generators ──

def gen_index(locale, strings, all_locales):
    ap = asset_prefix(locale)
    title = t(strings, "page_title_index", locale)
    desc = t(strings, "meta_desc_index", locale)

    extra = ""
    if locale == "en":
        extra = """  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "MobileApplication",
    "name": "ExitCall",
    "operatingSystem": "iOS",
    "applicationCategory": "UtilitiesApplication",
    "description": "ExitCall simulates realistic incoming phone calls so you can leave awkward situations gracefully.",
    "url": "https://exitcall.app",
    "offers": { "@type": "Offer", "price": "0", "priceCurrency": "USD" }
  }
  </script>
"""

    head = build_head(locale, "index.html", strings, title, desc, all_locales, extra)
    header = build_header(locale, "index.html", strings, is_index=True)
    footer = build_footer(locale, strings)

    how_href = "#how-it-works" if locale == "en" else "#how-it-works"

    body = f'''<body>

{header}

  <section class="hero">
    <img src="{ap}app-icon-180.png" alt="ExitCall app icon" class="hero-icon" width="120" height="120">
    <h1>{t(strings, "hero_title", locale)}</h1>
    <p class="subtitle">{t(strings, "hero_subtitle", locale)}</p>
    <a href="https://apps.apple.com/app/exitcall/id0000000000" class="app-store-badge" aria-label="{t(strings, "download_badge_alt", locale)}">
      <img src="https://developer.apple.com/assets/elements/badges/download-on-the-app-store.svg" alt="{t(strings, "download_badge_alt", locale)}" width="180" height="60">
    </a>
  </section>

  <section id="features" class="features container">
    <h2 class="section-title">{t(strings, "section_features", locale)}</h2>
    <div class="features-grid">
      <div class="feature-card">
        <div class="feature-icon" aria-hidden="true">&#128222;</div>
        <h3>{t(strings, "feature1_title", locale)}</h3>
        <p>{t(strings, "feature1_desc", locale)}</p>
      </div>
      <div class="feature-card">
        <div class="feature-icon" aria-hidden="true">&#127917;</div>
        <h3>{t(strings, "feature2_title", locale)}</h3>
        <p>{t(strings, "feature2_desc", locale)}</p>
      </div>
      <div class="feature-card">
        <div class="feature-icon" aria-hidden="true">&#9201;</div>
        <h3>{t(strings, "feature3_title", locale)}</h3>
        <p>{t(strings, "feature3_desc", locale)}</p>
      </div>
      <div class="feature-card">
        <div class="feature-icon" aria-hidden="true">&#128241;</div>
        <h3>{t(strings, "feature4_title", locale)}</h3>
        <p>{t(strings, "feature4_desc", locale)}</p>
      </div>
      <div class="feature-card">
        <div class="feature-icon" aria-hidden="true">&#128483;</div>
        <h3>{t(strings, "feature5_title", locale)}</h3>
        <p>{t(strings, "feature5_desc", locale)}</p>
      </div>
      <div class="feature-card">
        <div class="feature-icon" aria-hidden="true">&#128274;</div>
        <h3>{t(strings, "feature6_title", locale)}</h3>
        <p>{t(strings, "feature6_desc", locale)}</p>
      </div>
    </div>
  </section>

  <section id="how-it-works" class="how-it-works">
    <h2 class="section-title">{t(strings, "how_title", locale)}</h2>
    <div class="steps">
      <div class="step">
        <div class="step-number" aria-hidden="true">1</div>
        <h3>{t(strings, "step1_title", locale)}</h3>
        <p>{t(strings, "step1_desc", locale)}</p>
      </div>
      <div class="step">
        <div class="step-number" aria-hidden="true">2</div>
        <h3>{t(strings, "step2_title", locale)}</h3>
        <p>{t(strings, "step2_desc", locale)}</p>
      </div>
      <div class="step">
        <div class="step-number" aria-hidden="true">3</div>
        <h3>{t(strings, "step3_title", locale)}</h3>
        <p>{t(strings, "step3_desc", locale)}</p>
      </div>
    </div>
  </section>

  <section class="cta-section">
    <h2>{t(strings, "cta_title", locale)}</h2>
    <p>{t(strings, "cta_subtitle", locale)}</p>
    <a href="https://apps.apple.com/app/exitcall/id0000000000" class="app-store-badge" aria-label="{t(strings, "download_badge_alt", locale)}">
      <img src="https://developer.apple.com/assets/elements/badges/download-on-the-app-store.svg" alt="{t(strings, "download_badge_alt", locale)}" width="180" height="60">
    </a>
  </section>

{footer}

</body>
</html>
'''
    return head + "\n" + body


def gen_faq(locale, strings, all_locales):
    ap = asset_prefix(locale)
    title = f"{t(strings, 'faq_title', locale)} — ExitCall"
    desc = t(strings, "meta_desc_index", locale)

    # Build FAQ schema only for English (Google prefers single-language schema)
    extra = ""
    head = build_head(locale, "faq.html", strings, title, desc, all_locales, extra)
    header = build_header(locale, "faq.html", strings)
    footer = build_footer(locale, strings)

    body = f'''<body>

{header}

  <div class="page-content">
    <h1>{t(strings, "faq_title", locale)}</h1>

    <h2>{t(strings, "faq_q1", locale)}</h2>
    <p>{t(strings, "faq_a1", locale)}</p>

    <h2>{t(strings, "faq_q2", locale)}</h2>
    <p>{t(strings, "faq_a2", locale)}</p>

    <h2>{t(strings, "faq_q3", locale)}</h2>
    <p>{t(strings, "faq_a3", locale)}</p>

    <h2>{t(strings, "faq_q4", locale)}</h2>
    <p>{t(strings, "faq_a4", locale)}</p>

    <h2>{t(strings, "faq_q5", locale)}</h2>
    <p>{t(strings, "faq_a5", locale)}</p>

    <h2>{t(strings, "faq_q6", locale)}</h2>
    <p>{t(strings, "faq_a6", locale)}</p>

    <h2>{t(strings, "faq_q7", locale)}</h2>
    <p>{t(strings, "faq_a7", locale)}</p>
  </div>

{footer}

</body>
</html>
'''
    return head + "\n" + body


def gen_support(locale, strings, all_locales):
    title = f"{t(strings, 'support_title', locale)} — ExitCall"
    desc = t(strings, "support_intro", locale)

    head = build_head(locale, "support.html", strings, title, desc, all_locales)
    header = build_header(locale, "support.html", strings)
    footer = build_footer(locale, strings)

    body = f'''<body>

{header}

  <div class="page-content">
    <h1>{t(strings, "support_title", locale)}</h1>
    <p>{t(strings, "support_intro", locale)}</p>

    <h2>{t(strings, "support_contact_title", locale)}</h2>
    <p>{t(strings, "support_contact_email", locale)}</p>
    <p>{t(strings, "support_response_time", locale)}</p>

    <h2>{t(strings, "support_q_schedule", locale)}</h2>
    <p>{t(strings, "support_a_schedule", locale)}</p>

    <h2>{t(strings, "support_q_pro", locale)}</h2>
    <p>{t(strings, "support_a_pro", locale)}</p>

    <h2>{t(strings, "support_q_cancel", locale)}</h2>
    <p>{t(strings, "support_a_cancel", locale)}</p>

    <h2>{t(strings, "support_q_noarrive", locale)}</h2>
    <p>{t(strings, "support_a_noarrive", locale)}</p>

    <h2>{t(strings, "support_q_more", locale)}</h2>
    <p>{t(strings, "support_a_more", locale)}</p>
  </div>

{footer}

</body>
</html>
'''
    return head + "\n" + body


# Legal pages: privacy, terms, eula — keep English content, just translate chrome
def gen_legal_page(locale, strings, all_locales, page_name, page_title_en, content_html):
    """Legal pages keep English content body but get localized chrome (header/footer/nav)."""
    title = f"{page_title_en} — ExitCall"
    desc = f"{page_title_en} for ExitCall."

    head = build_head(locale, page_name, strings, title, desc, all_locales)
    header = build_header(locale, page_name, strings)
    footer = build_footer(locale, strings)

    body = f'''<body>

{header}

  <div class="page-content">
{content_html}
  </div>

{footer}

</body>
</html>
'''
    return head + "\n" + body


# Legal page content (English, reused across all locales — legal docs stay in English)
PRIVACY_CONTENT = """    <h1>Privacy Policy</h1>
    <p class="meta">Last updated: April 9, 2026</p>

    <p>ExitCall ("we", "our", or "us") is committed to protecting your privacy. This policy explains what data we collect and how we use it.</p>

    <h2>Data We Collect</h2>
    <p>ExitCall does not collect or store any personally identifiable information on our servers. All data (call history, character settings, scheduled calls) is stored locally on your device.</p>

    <h2>Analytics</h2>
    <p>We use Firebase Analytics to collect anonymous, aggregated usage data (e.g. feature usage, crash reports). This data cannot be used to identify you personally.</p>

    <h2>Purchases</h2>
    <p>In-app purchases are processed by Apple via the App Store. We do not have access to your payment information.</p>

    <h2>Third-Party Services</h2>
    <ul>
      <li><a href="https://firebase.google.com/support/privacy" target="_blank" rel="noopener">Firebase (Google)</a> — analytics and remote configuration</li>
    </ul>

    <h2>Children's Privacy</h2>
    <p>ExitCall is not directed at children under 13. We do not knowingly collect data from children.</p>

    <h2>Changes to This Policy</h2>
    <p>We may update this policy from time to time. The latest version will always be available at this URL.</p>

    <h2>Contact</h2>
    <p>Questions? Email us at <a href="mailto:support@exitcall.app">support@exitcall.app</a></p>"""

TERMS_CONTENT = """    <h1>Terms of Service</h1>
    <p class="meta">Last updated: April 12, 2026</p>

    <p>By using ExitCall ("the App"), you agree to these terms. If you do not agree, do not use the App.</p>

    <h2>Description of Service</h2>
    <p>ExitCall is a mobile application that simulates incoming phone calls to help you leave uncomfortable situations. The App uses text-to-speech to generate voice content during simulated calls.</p>

    <h2>Subscriptions</h2>
    <p>ExitCall offers optional in-app subscriptions (monthly and annual) that unlock additional features. Subscriptions are billed through your Apple ID and automatically renew unless cancelled at least 24 hours before the end of the current period. You can manage or cancel subscriptions in your device's Settings.</p>

    <h2>Free Trial</h2>
    <p>New users receive a free trial period with full access. After the trial expires, some features require a paid subscription.</p>

    <h2>Acceptable Use</h2>
    <p>You agree not to use ExitCall for any unlawful purpose or in any way that could harm, disable, or impair the service.</p>

    <h2>Intellectual Property</h2>
    <p>All content, design, and code in ExitCall are owned by us and protected by applicable intellectual property laws.</p>

    <h2>Disclaimer</h2>
    <p>ExitCall is provided "as is" without warranties of any kind. We are not responsible for any consequences arising from the use of simulated calls.</p>

    <h2>Limitation of Liability</h2>
    <p>To the maximum extent permitted by law, we shall not be liable for any indirect, incidental, or consequential damages arising from your use of the App.</p>

    <h2>Changes</h2>
    <p>We may update these terms at any time. Continued use of the App after changes constitutes acceptance of the new terms.</p>

    <h2>Contact</h2>
    <p>Questions? Email us at <a href="mailto:support@exitcall.app">support@exitcall.app</a></p>"""

EULA_CONTENT = """    <h1>End User License Agreement</h1>
    <p class="meta">Last updated: April 12, 2026</p>

    <p>This End User License Agreement ("EULA") governs your use of the ExitCall application ("the App"). By downloading or using the App, you agree to be bound by this agreement.</p>

    <h2>License Grant</h2>
    <p>We grant you a limited, non-exclusive, non-transferable, revocable license to use the App on any Apple device that you own or control, subject to Apple's Usage Rules.</p>

    <h2>Restrictions</h2>
    <p>You may not: (a) copy, modify, or distribute the App; (b) reverse engineer, decompile, or disassemble the App; (c) rent, lease, or lend the App to third parties; (d) use the App for any unlawful purpose.</p>

    <h2>Ownership</h2>
    <p>The App and all intellectual property rights therein are owned by us. This EULA does not grant you any ownership rights.</p>

    <h2>Termination</h2>
    <p>This license is effective until terminated. It will terminate automatically if you fail to comply with any term. Upon termination, you must delete all copies of the App.</p>

    <h2>Disclaimer of Warranties</h2>
    <p>The App is provided "as is" without warranty of any kind, express or implied.</p>

    <h2>Limitation of Liability</h2>
    <p>In no event shall we be liable for any damages arising from the use or inability to use the App.</p>

    <h2>Apple Terms</h2>
    <p>This EULA is between you and us, not Apple. Apple has no obligation to furnish maintenance or support for the App. In the event of any failure to conform to applicable warranties, you may notify Apple for a refund of the purchase price (if any). Apple has no other warranty obligation.</p>

    <h2>Contact</h2>
    <p>Questions? Email us at <a href="mailto:support@exitcall.app">support@exitcall.app</a></p>"""


def main():
    with open(TRANSLATIONS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    strings = data["strings"]
    locales = ["en"] + data["locales"]
    all_locales = locales

    pages_generated = 0

    for locale in locales:
        # Create directory
        dir_path = os.path.join(ROOT_DIR, locale) if locale != "en" else ROOT_DIR
        if locale != "en":
            os.makedirs(dir_path, exist_ok=True)

        # Generate pages
        pages = {
            "index.html": gen_index(locale, strings, all_locales),
            "faq.html": gen_faq(locale, strings, all_locales),
            "support.html": gen_support(locale, strings, all_locales),
            "privacy.html": gen_legal_page(locale, strings, all_locales, "privacy.html", "Privacy Policy", PRIVACY_CONTENT),
            "terms.html": gen_legal_page(locale, strings, all_locales, "terms.html", "Terms of Service", TERMS_CONTENT),
            "eula.html": gen_legal_page(locale, strings, all_locales, "eula.html", "End User License Agreement", EULA_CONTENT),
        }

        for page_name, html in pages.items():
            file_path = os.path.join(dir_path, page_name)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html)
            pages_generated += 1

    print(f"Generated {pages_generated} pages for {len(locales)} locales.")

    # Generate sitemap
    gen_sitemap(all_locales)
    print("Updated sitemap.xml")


def gen_sitemap(all_locales):
    """Generate sitemap.xml with all localized pages."""
    pages = ["index.html", "faq.html", "support.html", "privacy.html", "terms.html", "eula.html"]

    urls = []
    for page in pages:
        # Each page has alternate links for all locales
        xhtml_links = []
        for loc in all_locales:
            href = f"https://exitcall.app/{locale_dir(loc)}{page}"
            hl = LOCALE_META[loc]["hreflang"]
            xhtml_links.append(f'    <xhtml:link rel="alternate" hreflang="{hl}" href="{href}"/>')
        xhtml_links.append(f'    <xhtml:link rel="alternate" hreflang="x-default" href="https://exitcall.app/{page}"/>')

        for loc in all_locales:
            href = f"https://exitcall.app/{locale_dir(loc)}{page}"
            priority = "1.0" if page == "index.html" else "0.8"
            urls.append(f"""  <url>
    <loc>{href}</loc>
    <priority>{priority}</priority>
{"".join(l + chr(10) for l in xhtml_links)}  </url>""")

    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">
{"".join(u + chr(10) for u in urls)}</urlset>
"""
    with open(os.path.join(ROOT_DIR, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sitemap)


if __name__ == "__main__":
    main()
