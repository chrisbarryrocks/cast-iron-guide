#!/usr/bin/env python3
"""Static site builder. Usage: python build.py [--site-url URL] [--out DIR]
SITE_URL must end with '/'. Paths are derived from it (supports GitHub project pages)."""
import argparse, datetime, html, os, re, shutil, json
from urllib.parse import urlparse
import markdown

ap = argparse.ArgumentParser()
ap.add_argument("--site-url", default="https://chrisbarryrocks.github.io/cast-iron-guide/")
ap.add_argument("--out", default="_site")
a = ap.parse_args()
SITE = a.site_url if a.site_url.endswith("/") else a.site_url + "/"
BASE = urlparse(SITE).path or "/"
OUT = a.out
NAME = "Well Seasoned Iron"
TAG = "Practical, tested guides to cast iron and carbon steel care"
TODAY = datetime.date.today().isoformat()
ORDER = ["how-to-season-cast-iron","how-to-clean-cast-iron","how-to-remove-rust-from-cast-iron",
 "why-food-sticks-to-cast-iron","best-oil-for-seasoning-cast-iron","sticky-or-flaking-cast-iron-seasoning",
 "how-to-restore-vintage-cast-iron","identify-vintage-cast-iron","cast-iron-vs-carbon-steel","how-to-season-carbon-steel-pan"]

CSS = """:root{--bg:#faf8f5;--fg:#1f1d1a;--mut:#6b645b;--acc:#9a3b12;--card:#fff;--line:#e7e1d8}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;font:18px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Georgia,serif;color:var(--fg);background:var(--bg)}
a{color:var(--acc)}header,footer{background:#1f1d1a;color:#f3eee7}
header .w,footer .w{display:flex;flex-wrap:wrap;gap:.5rem 1.25rem;align-items:center;justify-content:space-between}
header a,footer a{color:#f3eee7;text-decoration:none}.logo{font-weight:700;font-size:1.15rem}
nav a{margin-left:1rem;font-size:.95rem}.w{max-width:760px;margin:0 auto;padding:1rem 1.15rem}
main .w{padding-top:1.5rem;padding-bottom:3rem}h1{font-size:2rem;line-height:1.2;margin:.3rem 0 1rem}
h2{margin-top:2.2rem;line-height:1.25}h3{margin-top:1.6rem}
table{border-collapse:collapse;width:100%;font-size:.92rem;display:block;overflow-x:auto}
th,td{border:1px solid var(--line);padding:.45rem .6rem;text-align:left;vertical-align:top}th{background:#f1ebe2}
.meta{color:var(--mut);font-size:.9rem}.cards{list-style:none;padding:0;display:grid;gap:1rem}
.cards li{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:1rem 1.1rem}
.cards a{font-weight:650;text-decoration:none;font-size:1.08rem}.cards p{margin:.35rem 0 0;color:var(--mut);font-size:.95rem}
.crumb{font-size:.88rem;color:var(--mut)}footer{font-size:.88rem}footer .w{padding:1.5rem 1.15rem}
@media(max-width:520px){body{font-size:17px}h1{font-size:1.6rem}nav a{margin-left:0;margin-right:.9rem}}"""

def page(title, desc, path, body, kind="website", extra=""):
    url = SITE + path
    full = title if title == NAME else f"{title} | {NAME}"
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(full)}</title><meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{url}"><meta name="robots" content="index,follow">
<meta property="og:type" content="{kind}"><meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}"><meta property="og:url" content="{url}">
<meta property="og:site_name" content="{NAME}"><meta name="twitter:card" content="summary">
<link rel="icon" href="{BASE}favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="{BASE}style.css">{extra}
</head><body><header><div class="w"><a class="logo" href="{BASE}">{NAME}</a>
<nav><a href="{BASE}">Guides</a><a href="{BASE}about/">About</a><a href="{BASE}contact/">Contact</a></nav></div></header>
<main><div class="w">{body}</div></main>
<footer><div class="w"><span>&copy; {datetime.date.today().year} {NAME}</span>
<span><a href="{BASE}about/">About</a> · <a href="{BASE}privacy/">Privacy</a> · <a href="{BASE}contact/">Contact</a> · <a href="{BASE}sitemap.xml">Sitemap</a></span></div></footer>
</body></html>"""

def write(path, s):
    p = os.path.join(OUT, path); os.makedirs(os.path.dirname(p) or OUT, exist_ok=True)
    open(p, "w").write(s)

def fixlinks(h): return re.sub(r'href="/(?!/)', f'href="{BASE}', h)

shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
arts = []
for slug in ORDER:
    raw = open(f"content/{slug}.md").read()
    head, body = raw.split("\n\n", 1)
    meta = dict(l.split(": ", 1) for l in head.splitlines())
    h = fixlinks(markdown.markdown(body, extensions=["tables"]))
    words = len(re.findall(r"\w+", body))
    arts.append((slug, meta["title"], meta["description"], words))
    ld = json.dumps({"@context":"https://schema.org","@type":"Article","headline":meta["title"],
        "description":meta["description"],"datePublished":TODAY,"dateModified":TODAY,
        "author":{"@type":"Organization","name":NAME},"mainEntityOfPage":SITE+slug+"/"})
    b = (f'<p class="crumb"><a href="{BASE}">Guides</a> › Article</p><article><h1>{html.escape(meta["title"])}</h1>'
         f'<p class="meta">Updated {TODAY} · {max(1,words//230)} min read</p>{h}</article>')
    write(f"{slug}/index.html", page(meta["title"], meta["description"], slug+"/", b, "article",
          f'<script type="application/ld+json">{ld}</script>'))

items = "".join(f'<li><a href="{BASE}{s}/">{html.escape(t)}</a><p>{html.escape(d)}</p></li>' for s,t,d,_ in arts)
write("index.html", page(NAME, TAG + ": seasoning, cleaning, rust removal, restoration, and more.", "",
  f"<h1>{NAME}</h1><p>{TAG}. No fluff, no fake stats: just clear steps that work, and honest explanations of why.</p>"
  f"<h2>All guides</h2><ul class='cards'>{items}</ul>"))

statics = {
 "about": ("About", "What Well Seasoned Iron is and how our guides are written.",
  "<h1>About</h1><p>Well Seasoned Iron is an independent site about one thing: caring for cast iron and carbon steel cookware. Our goal is to answer the questions people actually have, such as why a pan is sticky, how to get rust off, or whether soap is really off-limits, with clear steps and plain explanations.</p><h2>How we write</h2><ul><li>We explain the reasoning behind every step so you can troubleshoot on your own.</li><li>We don't invent statistics or test results. Where manufacturer guidance exists, we point to it, and where practices vary, we say so.</li><li>We are not affiliated with any cookware brand.</li><li>Guides are reviewed and updated as we learn more.</li></ul><h2>Safety</h2><p>Some restoration methods involve caustic chemicals or electricity. Always follow product labels and manufacturer instructions; our guides are general information.</p>"),
 "privacy": ("Privacy Policy", "How Well Seasoned Iron handles visitor data, cookies, and third-party advertising.",
  f"<h1>Privacy Policy</h1><p class='meta'>Last updated {TODAY}</p><p>This policy explains what information is collected when you visit this site.</p><h2>Information we collect</h2><p>We do not ask you to create an account or submit personal information. The site is hosted on GitHub Pages, which may log technical data such as IP addresses for security and operations; see GitHub's privacy statement.</p><h2>Cookies and advertising</h2><p>This site may display ads served by Google and its partners. Third-party vendors, including Google, use cookies to serve ads based on a user's prior visits to this website or other websites. Google's use of advertising cookies enables it and its partners to serve ads to you based on your visit to this site and/or other sites on the Internet.</p><p>You may opt out of personalized advertising by visiting <a href='https://www.google.com/settings/ads'>Google Ads Settings</a>, or opt out of some third-party vendors' use of cookies for personalized advertising at <a href='https://www.aboutads.info/choices/'>www.aboutads.info</a>. See also <a href='https://policies.google.com/technologies/partner-sites'>how Google uses information from sites that use its services</a>.</p><h2>Analytics</h2><p>If we add analytics, this policy will be updated to describe it.</p><h2>Children</h2><p>This site is not directed to children under 13 and we do not knowingly collect their information.</p><h2>Changes</h2><p>We may update this policy; the date above shows the latest revision.</p><h2>Contact</h2><p>Questions? See our <a href='{BASE}contact/'>contact page</a>.</p>"),
 "contact": ("Contact", "How to get in touch with Well Seasoned Iron.",
  "<h1>Contact</h1><p>Have a question about a pan, found a mistake in a guide, or have a topic you'd like covered? We'd like to hear from you.</p><p>Email: <strong>[contact address coming soon]</strong></p><p>We read every message, but we can't offer personalized advice about specific products or safety situations. For questions about a specific product, the manufacturer is the best source.</p>"),
}
for slug,(t,d,b) in statics.items(): write(f"{slug}/index.html", page(t, d, slug+"/", b))
write("404.html", page("Page not found", "Page not found.", "404.html", f"<h1>Page not found</h1><p><a href='{BASE}'>Browse all guides</a></p>"))
write("style.css", CSS)
write("favicon.svg", '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><circle cx="14" cy="16" r="11" fill="#1f1d1a"/><rect x="24" y="14" width="8" height="4" rx="2" fill="#1f1d1a"/></svg>')
urls = [""] + [s+"/" for s,*_ in arts] + ["about/","privacy/","contact/"]
write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
      "".join(f"  <url><loc>{SITE}{u}</loc><lastmod>{TODAY}</lastmod></url>\n" for u in urls) + "</urlset>\n")
write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE}sitemap.xml\n")
write(".nojekyll", "")
for s,t,_,w in arts: print(f"{w:5d}  {s}")
print("built", OUT, "base", BASE)
