"""Render the original repository text without rewriting the research content.

Optional regeneration: pip install markdown beautifulsoup4
Then: python tools/build_page.py
Publishing the generated HTML does not require Python or a build step.
"""
from pathlib import Path
from html import escape
import re
import markdown
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "content"
REPOSITORY = "https://github.com/SIAT-INVS/OpenMAMS"
NAV_ITEMS = [
    ("overview", "Overview"),
    ("architecture", "Architecture"),
    ("carla-simulation", "CARLA Simulation"),
    ("real-world-experiments", "Real-World Experiments"),
    ("memory-native-non-terrestrial-networks", "MemNTN"),
    ("results", "Results"),
    ("demos", "Demos"),
    ("citation", "Citation"),
]
ANIMATIONS = {
    "pmas-semantic-map.webp": "pmas-semantic-map",
    "town05_10uavs.webp": "town05_10uavs",
}


def read_markdown(path):
    text = path.read_text(encoding="utf-8")
    # GitHub renders Markdown inside these blocks; enable the same behavior here.
    text = text.replace('<div align="center">', '', 1).replace('</div>', '', 1)
    text = text.replace('<details>', '<details markdown="1">')
    return BeautifulSoup(markdown.markdown(text, extensions=["extra", "toc"]), "html.parser")


def content_text(soup):
    copy = BeautifulSoup(str(soup), "html.parser")
    for element in copy.select("button, video"):
        element.decompose()
    return re.sub(r"\s+", " ", copy.get_text(" ", strip=True)).strip()


def wrap(tag, name, **attrs):
    wrapper = document.new_tag(name, attrs=attrs)
    tag.wrap(wrapper)
    return wrapper


document = read_markdown(SOURCE / "project.md")
# Installation/module details stay in the code repository. Keep the following
# demonstrations as their own section without modifying the source snapshot.
code_heading = document.find("h2", id="code")
demos_heading = document.find("h3", id="demos")
if code_heading is None or demos_heading is None:
    raise RuntimeError("Expected Code and Demos headings in the source README.")
for node in list(code_heading.next_siblings):
    if node is demos_heading:
        break
    node.extract()
code_heading.decompose()
demos_heading.name = "h2"
for node in demos_heading.next_siblings:
    if getattr(node, "name", None) == "h2":
        break
    if getattr(node, "name", None) == "h4":
        node.name = "h3"
# Requested page heading; the archived repository wording stays untouched.
results_heading = document.find("h2", id="selected-results")
results_heading.string = "Results"
results_heading["id"] = "results"
# Requested evaluation label, scoped to the Results table.
results_table = results_heading.find_next_sibling("table")
for row in results_table.find_all("tr"):
    label = row.find("td")
    if label and label.get_text(strip=True) == "PMAS":
        label.string = "Real PMAS"
original_text = content_text(document)

for image in list(document.find_all("img")):
    name = Path(image["src"]).name
    if name in ANIMATIONS:
        stem = ANIMATIONS[name]
        video = document.new_tag("video", attrs={
            "autoplay": "", "muted": "", "loop": "", "playsinline": "", "controls": "",
            "preload": "none", "data-autoplay": "", "poster": f"assets/{stem}-poster.jpg",
            "aria-label": image.get("alt", stem),
        })
        video.append(document.new_tag("source", attrs={"src": f"assets/{stem}.mp4", "type": "video/mp4"}))
        video.append("Your browser does not support HTML video. ")
        fallback = document.new_tag("a", href=f"assets/{stem}.mp4")
        fallback.string = "Download"
        video.append(fallback)
        if stem == "pmas-semantic-map":
            video["id"] = "map-video"
        # A native player must not be nested inside a link to another media file.
        if image.parent.name == "a":
            image.parent.replace_with(video)
        else:
            image.replace_with(video)
        wrap(video, "div", **{"class": "video-frame"})
    else:
        image["src"] = f"assets/{Path(name).stem}.webp"
        image["loading"] = "lazy"
        image["decoding"] = "async"
        image.attrs.pop("width", None)
        if image.parent.name != "a":
            wrap(image, "a", href=f"assets/{Path(name).stem}.webp", target="_blank", rel="noopener")

for link in document.find_all("a", href=True):
    href = link["href"]
    if href == "assets/README.md":
        link["href"] = "assets.html"
    elif href.startswith("assets/") and (
        href.endswith(".pdf") or (href.endswith(".png") and (ROOT / href).is_file())
    ):
        link["target"] = "_blank"
        link["rel"] = "noopener"
    elif href.startswith("assets/") and not href.endswith(".mp4"):
        link["href"] = f"assets/{Path(href).stem}.webp"
        link["target"] = "_blank"
        link["rel"] = "noopener"
    elif href.startswith(("ntn/", "uav_data_recorder/")):
        link["href"] = f"{REPOSITORY}/blob/main/{href}"

# Preserve every heading, paragraph, list item, table cell, and BibTeX entry.
# Only presentation wrappers and functional copy controls are added.
main = document.new_tag("main", id="main")
hero = document.new_tag("section", attrs={"class": "paper-intro", "id": "paper"})
main.append(hero)
current = hero
section_number = 0
for node in list(document.contents):
    if getattr(node, "name", None) == "h2":
        section_number += 1
        section_id = node.attrs.pop("id", None)
        section = document.new_tag("section", attrs={
            "class": "section" + (" tinted" if section_number % 2 else ""),
            "id": section_id,
        })
        current = document.new_tag("div", attrs={"class": "container"})
        section.append(current)
        main.append(section)
    current.append(node.extract())

title = hero.find("h1")
title.name = "h1"
title["class"] = "project-label"
paper = hero.find("h3")
paper.name = "h2"
paper["class"] = "paper-title"

for paragraph in hero.find_all("p", recursive=False):
    text = paragraph.get_text(" ", strip=True)
    if text.startswith("Chengyang Li"):
        paragraph["class"] = "authors"
        # Keep each name and affiliation marker together without changing wording.
        for marker in list(paragraph.find_all("sup")):
            name_text = marker.previous_sibling
            if not isinstance(name_text, str):
                continue
            match = re.match(r"^(\s*(?:,\s*(?:and\s+)?)?)(.*)$", str(name_text))
            prefix, name = match.groups()
            author = document.new_tag("span", attrs={"class": "author"})
            author.append(name)
            name_text.replace_with(prefix)
            marker.insert_before(author)
            author.append(marker.extract())
    elif "The University of Hong Kong" in text:
        paragraph["class"] = "affiliations"
    elif paragraph.find("a", href="#overview"):
        paragraph["class"] = "project-nav"
    elif paragraph.find("a", href="https://arxiv.org/abs/2609.35431"):
        paragraph["class"] = "paper-links"

# Convert invalid paragraph-around-block markup into a semantic media figure.
for frame in main.select(".video-frame"):
    if frame.parent.name == "p":
        frame.parent.name = "figure"
        frame.parent.attrs = {"class": "demo-figure"}

for table in main.find_all("table"):
    if table.find("img"):
        table["class"] = "figure-table"
        for cell in table.find_all("td"):
            cell.attrs.pop("width", None)
    else:
        table["class"] = "data-table"
        wrapper = document.new_tag("div", attrs={"class": "table-scroll", "tabindex": "0", "role": "region", "aria-label": "Table"})
        table.wrap(wrapper)

for index, pre in enumerate(main.find_all("pre")):
    code = pre.find("code")
    if code:
        code["id"] = f"bibtex-{index}"
        box = document.new_tag("div", attrs={"class": "citation-block"})
        pre.wrap(box)
        button = document.new_tag("button", attrs={"class": "copy-button", "data-copy": code["id"], "aria-label": f"Copy citation {index + 1} BibTeX"})
        button.string = "Copy BibTeX"
        box.insert(0, button)

if content_text(main) != original_text:
    raise RuntimeError("Rendered main content no longer matches the source README text.")

# The user-requested cover sits above the unchanged research content.
# Move the existing header video into it instead of loading a second copy.
header_video = main.find("video", id="map-video")
old_figure = header_video.find_parent("figure")
header_video.extract()
old_figure.decompose()
header_video["preload"] = "metadata"
header_video.attrs.pop("controls", None)
cover = document.new_tag("section", attrs={
    "class": "header-video", "id": "top", "aria-label": "Panoramic multi-agent system demonstration",
})
cover.append(header_video)
main.insert(0, cover)
research_copy = BeautifulSoup(str(main), "html.parser")
research_copy.select_one(".header-video").decompose()
assert content_text(research_copy) == original_text

# The user keeps navigation in the sticky header and omits both intro link rows.
for link_row in main.select(".project-nav, .paper-links"):
    link_row.decompose()

# Additional demonstration supplied by the user after the repository snapshot.
robot_demo = BeautifulSoup('''
<h3 id="robot-dog">Robot Dog · UAV-to-ground memory reuse</h3>
<figure class="demo-figure"><div class="video-frame">
  <video autoplay muted loop playsinline controls preload="none" data-autoplay
      poster="assets/robot-dog-poster.jpg"
      aria-label="Robot dog navigating to a basketball court using aerial memory">
    <source src="assets/robot-dog.mp4" type="video/mp4">
    Your browser does not support HTML video. <a href="assets/robot-dog.mp4">Download</a>
  </video>
</div></figure>
<p>A robot dog reuses aerial memory to answer environmental questions and navigate to a queried location. The video shows the robot navigating to a basketball court, alongside first-person, third-person, and point-cloud views.</p>
''', "html.parser")
demos = main.select_one("#demos .container")
for node in list(robot_demo.contents):
    demos.append(node.extract())

description = main.find("blockquote").get_text(" ", strip=True)
favicon = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='8' fill='%234c52cc'/%3E%3Cpath d='M7 23V10l9 7 9-7v13M7 10l9-4 9 4' fill='none' stroke='white' stroke-width='2.5' stroke-linejoin='round'/%3E%3C/svg%3E"


def page_html(title, body, navigation):
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{escape(description, quote=True)}">
  <meta name="theme-color" content="#ffffff">
  <meta property="og:title" content="{escape(title, quote=True)}">
  <meta property="og:description" content="{escape(description, quote=True)}">
  <meta property="og:type" content="website">
  <title>{escape(title)}</title>
  <link rel="icon" type="image/svg+xml" href="{favicon}">
  <link rel="stylesheet" href="project.css">
  <script src="project.js" defer></script>
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>
  <header class="site-header"><nav class="navigation container" aria-label="Main navigation">
    <a class="wordmark" href="index.html#top" aria-label="OpenMAMS home"><span class="brand-symbol" aria-hidden="true">INVS</span>OpenMAMS</a>
    <div class="nav-links">{navigation}</div>
    <a class="nav-code" href="{REPOSITORY}">GitHub <span aria-hidden="true">↗</span></a>
  </nav></header>
  {body}
  <p class="container copy-status" id="copy-status" role="status" aria-live="polite"></p>
  <footer class="site-footer"><div class="container"><a class="wordmark" href="index.html#top">OpenMAMS</a><a href="{REPOSITORY}">GitHub ↗</a></div></footer>
</body>
</html>
'''


navigation = "".join(f'<a href="#{anchor}">{label}</a>' for anchor, label in NAV_ITEMS)
(ROOT / "index.html").write_text(page_html("OpenMAMS: Open-Sourced Multi-Agent Memory System", str(main), navigation), encoding="utf-8")

asset_document = read_markdown(SOURCE / "assets.md")
asset_original = content_text(asset_document)
for link in asset_document.find_all("a", href=True):
    if not link["href"].startswith(("https:", "http:", "#")):
        link["href"] = "assets/" + link["href"]
for table in asset_document.find_all("table"):
    table["class"] = "data-table"
    wrapper = asset_document.new_tag("div", attrs={"class": "table-scroll", "tabindex": "0", "role": "region", "aria-label": "Asset table"})
    table.wrap(wrapper)
assert content_text(asset_document) == asset_original
asset_body = f'<main id="main" class="asset-page container">{asset_document}</main>'
(ROOT / "assets.html").write_text(page_html("OpenMAMS · Assets", asset_body, '<a href="index.html">OpenMAMS</a>'), encoding="utf-8")
print("Generated page with Code details omitted and Demos retained. Remaining research text matches the source Markdown (whitespace normalized).")
