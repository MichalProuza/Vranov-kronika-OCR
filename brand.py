"""Vizuální styl webu s přepisem kroniky: barvy, písma, značka a logomanuál.

Styl vychází ze znaku obce Vranov (červené pole se zlatou korunou, zlaté pole
s modrým mariánským monogramem). Značka webu je jeho zjednodušená kresba –
není to úřední znak obce. Úřední znak je v `data/znak_obce.png` a v logomanuálu
se ukazuje jen jako předloha.
"""

import base64
import html
import math
from pathlib import Path
from urllib.parse import quote

CREST_FILE = Path(__file__).parent / "data" / "znak_obce.png"

FONT_DISPLAY = "Grenze Gotisch"
FONT_BODY = "Literata"
FONT_UI = "Source Sans 3"
FONTS_URL = ("https://fonts.googleapis.com/css2?family=Grenze+Gotisch:wght@400;600;800"
             "&family=Literata:ital,opsz,wght@0,7..72,400;0,7..72,700;1,7..72,400"
             "&family=Source+Sans+3:wght@400;600&display=swap")

# klíč: (název, hex, k čemu slouží)
COLORS = {
    "red": ("Červeň znaku", "#D8232A", "Horní pole štítu ve značce. Na webu jen jako výrazný detail."),
    "carmine": ("Karmín", "#8C1A1F", "Základní barva webu: záhlaví, nadpisy, odkazy, tlačítka."),
    "gold": ("Zlato znaku", "#F2C12E", "Dolní pole štítu, koruna, linky a ozdoby. Nikdy jako barva textu na světlém."),
    "ochre": ("Okr", "#B98A14", "Tmavší zlato pro tenké linky a rámečky na papíru."),
    "blue": ("Modř znaku", "#1FA3C8", "Barva monogramu ve znaku obce. Na webu tenké linky a drobné zvýraznění."),
    "petrol": ("Petrolej", "#16607A", "Tmavší modř: monogram ve značce, odkazy na skeny, ovládací prvky."),
    "ink": ("Inkoust", "#241A12", "Text přepisu."),
    "paper": ("Papír", "#FFFDF8", "Podklad stran s přepisem."),
    "parchment": ("Pergamen", "#F6F0E1", "Pozadí webu."),
}
HEX = {key: value[1] for key, value in COLORS.items()}

SHIELD_BASE = "M4 50H96V62C96 95 75 112 50 116C25 112 4 95 4 62Z"
SHIELD_OUTLINE = "M4 4H96V62C96 95 75 112 50 116C25 112 4 95 4 62Z"
ROSETTES = [(18.5, 24, -28), (33, 16, -12), (50, 12.5, 0), (67, 16, 12), (81.5, 24, 28)]

# barvy variant značky: horní pole, dolní pole, koruna, perly, monogram, obrys
MARK_VARIANTS = {
    "color": (HEX["red"], HEX["gold"], HEX["gold"], "#FFFFFF", HEX["petrol"], None),
    "ink": (HEX["ink"], "none", HEX["paper"], HEX["ink"], HEX["ink"], HEX["ink"]),
    "light": ("#FFFDF8", "none", HEX["carmine"], "#FFFDF8", "#FFFDF8", "#FFFDF8"),
}


def _rosette(cx: float, cy: float, turn: float, fill: str, pearl: str, r: float = 2.7) -> str:
    """Pětilistá růžice z koruny: pět okvětních lístků kolem perly."""
    petals = []
    for i in range(5):
        angle = math.radians(turn - 90 + i * 72)
        petals.append(f'<circle cx="{cx + r * 1.05 * math.cos(angle):.2f}" cy="{cy + r * 1.05 * math.sin(angle):.2f}" r="{r}"/>')
    return f'<g fill="{fill}">{"".join(petals)}</g><circle cx="{cx}" cy="{cy}" r="{r * 0.62:.2f}" fill="{pearl}"/>'


def mark_svg(variant: str = "color", size: int | None = None, title: str = "Značka Kroniky obce Vranov",
             standalone: bool = False) -> str:
    """Značka webu (štít s korunou a monogramem) jako SVG. `size` je výška v px."""
    chief, base, crown, pearl, mono, outline = MARK_VARIANTS[variant]
    rosettes = "".join(_rosette(x, y, turn, crown, pearl) for x, y, turn in ROSETTES)
    pearls = "".join(f'<circle cx="{32 + i * 6}" cy="{40.4 + 1.6 * (1 - ((i - 3) / 3) ** 2):.2f}" r="1.35"/>' for i in range(7))
    stroke = f'<path d="{SHIELD_OUTLINE}" fill="none" stroke="{outline}" stroke-width="3" stroke-linejoin="round"/>' if outline else ""
    attrs = f' height="{size}" width="{size * 100 / 120:.0f}"' if size else ""
    if standalone:
        attrs += ' xmlns="http://www.w3.org/2000/svg"'
    return (
        f'<svg class="brand-mark" viewBox="0 0 100 120"{attrs} role="img" aria-label="{html.escape(title)}">'
        f'<path d="M4 4H96V50H4Z" fill="{chief}"/><path d="{SHIELD_BASE}" fill="{base}"/>'
        # koruna: obruč s perlami, pět hrotů s růžicemi
        f'<path d="M20.5 27.5Q27 33 32.5 21Q41 33 50 17.5Q59 33 67.500 21Q73 33 79.500 27.500L74 37Q50 42 26 37Z" fill="{crown}"/>'
        f'<path d="M27 38.800Q50 43.800 73 38.800L71.500 45.500Q50 49.500 28.500 45.500Z" fill="{crown}"/>'
        f'<g fill="{pearl}">{pearls}</g>{rosettes}'
        # monogram: M a A přes sebe, středem žezlo s lilií
        f'<g fill="none" stroke="{mono}" stroke-width="2.9" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M50 62V106"/>'
        '<path d="M39.500 95V74.500L50 89L60.500 74.500V95"/>'
        '<path d="M26.500 93.500Q26 99.500 31.500 99Q36 98 38.500 90L47 69.500Q50 65 53 69.500L61.500 90Q64 98 68.500 99Q74 99.500 73.500 93.500"/>'
        '<path d="M33.500 72Q50 66.500 66.500 72"/>'
        '</g>'
        f'<g fill="{mono}"><path d="M50 55.500Q53.200 58.500 50 62.500Q46.800 58.500 50 55.500Z"/>'
        '<circle cx="46" cy="61.500" r="1.9"/><circle cx="54" cy="61.500" r="1.9"/>'
        '<path d="M50 103L53.500 107.500L50 112L46.500 107.500Z"/></g>'
        f'{stroke}</svg>'
    )


def svg_data_uri(svg: str) -> str:
    return "data:image/svg+xml," + quote(svg, safe="/:=' ")


def rosette_svg(fill: str, pearl: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 12 12">'
            f'{_rosette(6, 6, 0, fill, pearl)}</svg>')


def favicon_uri() -> str:
    return svg_data_uri(mark_svg("color", standalone=True))


def lockup_html(variant: str = "color", stacked: bool = False, size: int = 56) -> str:
    """Logotyp: značka s nápisem."""
    cls = "lockup lockup-stacked" if stacked else "lockup"
    return (f'<span class="{cls} lockup-{variant}">{mark_svg(variant, size)}'
            '<span class="lockup-text"><span class="lockup-name">Kronika obce Vranov</span>'
            '<span class="lockup-sub">Přepis obecní kroniky</span></span></span>')


def _luminance(hex_color: str) -> float:
    channels = [int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    r, g, b = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: str, b: str) -> float:
    """Kontrastní poměr dvou barev podle WCAG."""
    la, lb = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def _swatch(key: str) -> str:
    name, hex_color, use = COLORS[key]
    rgb = ", ".join(str(int(hex_color[i:i + 2], 16)) for i in (1, 3, 5))
    on = HEX["ink"] if contrast(hex_color, HEX["ink"]) > contrast(hex_color, "#FFFFFF") else "#FFFFFF"
    ratio = f"{contrast(hex_color, HEX['paper']):.1f}".replace(".", ",")
    return (f'<li class="lm-swatch"><span class="lm-chip" style="background:{hex_color};color:{on}">{hex_color}</span>'
            f'<span class="lm-swatch-text"><b>{name}</b><span class="lm-meta">RGB {rgb} · kontrast k papíru {ratio} : 1</span>'
            f'<span>{use}</span></span></li>')


def crest_data_uri(path: Path = CREST_FILE) -> str:
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


PANGRAM = "Příliš žluťoučký kůň úpěl ďábelské ódy"


def build_logomanual_html() -> str:
    """Oddíl „Logomanuál“: znak obce, značka webu, barvy, písma a pravidla užití."""
    crest = ""
    if CREST_FILE.exists():
        crest = f'<img src="{crest_data_uri()}" alt="Znak obce Vranov" width="128" height="150">'
    download = svg_data_uri(mark_svg("color", standalone=True))
    download_ink = svg_data_uri(mark_svg("ink", standalone=True))
    palette = "".join(_swatch(key) for key in COLORS)
    rosette = rosette_svg(HEX["ochre"], HEX["paper"])
    return f'''
        <section id="logomanual" class="chronicle-section logomanual">
            <h2>Logomanuál</h2>
            <p class="ni-intro">Jak vypadá web s přepisem kroniky a proč. Barvy, značka i ozdoby vycházejí ze znaku obce Vranov;
            pravidla níže drží vzhled pohromadě, až se bude web dál rozšiřovat.</p>

            <h3>1. Předloha: znak obce</h3>
            <div class="lm-row">
                <figure class="lm-tile lm-tile-paper">{crest}<figcaption>Znak obce Vranov</figcaption></figure>
                <div class="lm-text">
                    <p>Štít je dělený. V horním červeném poli je zlatá koruna s pěti růžicemi a perlami, v dolním zlatém poli
                    modrý mariánský monogram – připomínka poutního kostela Narození Panny Marie.</p>
                    <p>Ze znaku si web bere tři věci: <b>trojici barev</b> (červená, zlatá, modrá), <b>dělení</b> na červenou
                    plochu nad zlatou linkou a <b>růžici z koruny</b> jako drobnou ozdobu.</p>
                    <p class="lm-note">Znak patří obci. Kdo jej chce použít jinde, potřebuje její souhlas
                    (zákon č. 128/2000 Sb., o obcích, § 34a). Tento web proto znak neužívá jako své logo, ale jen jako předlohu.</p>
                </div>
            </div>

            <h3>2. Značka webu</h3>
            <p>Značka je zjednodušená kresba znaku: štít, koruna a monogram v plochých barvách bez obrysů, aby byla čitelná
            i jako ikona v záložce prohlížeče. Není to úřední symbol obce a nenahrazuje jej.</p>
            <div class="lm-grid">
                <figure class="lm-tile lm-tile-paper">{mark_svg("color", 120)}<figcaption>Barevná – základní</figcaption></figure>
                <figure class="lm-tile lm-tile-carmine">{mark_svg("color", 120)}<figcaption>Barevná na karmínu</figcaption></figure>
                <figure class="lm-tile lm-tile-paper">{mark_svg("ink", 120)}<figcaption>Jednobarevná</figcaption></figure>
                <figure class="lm-tile lm-tile-carmine">{mark_svg("light", 120)}<figcaption>Negativní</figcaption></figure>
            </div>
            <p class="lm-downloads">Ke stažení:
                <a href="{download}" download="kronika-vranov-znacka.svg">barevná značka (SVG)</a> ·
                <a href="{download_ink}" download="kronika-vranov-znacka-jednobarevna.svg">jednobarevná značka (SVG)</a></p>

            <h3>3. Logotyp</h3>
            <p>Značka s nápisem. Název je sázen písmem {FONT_DISPLAY}, podtitul verzálkami písma {FONT_UI}.
            Vodorovná podoba je základní, svislá se hodí na úzká místa a titulní strany.</p>
            <div class="lm-grid lm-grid-wide">
                <figure class="lm-tile lm-tile-paper">{lockup_html("color")}<figcaption>Vodorovný</figcaption></figure>
                <figure class="lm-tile lm-tile-carmine">{lockup_html("light")}<figcaption>Vodorovný, negativní</figcaption></figure>
                <figure class="lm-tile lm-tile-paper">{lockup_html("color", stacked=True, size=84)}<figcaption>Svislý</figcaption></figure>
                <figure class="lm-tile lm-tile-paper">{lockup_html("ink", stacked=True, size=84)}<figcaption>Svislý, jednobarevný</figcaption></figure>
            </div>

            <h3>4. Ochranná zóna a nejmenší velikost</h3>
            <div class="lm-row">
                <figure class="lm-tile lm-tile-paper"><span class="lm-zone">{mark_svg("color", 110)}</span>
                    <figcaption>Volné místo kolem značky = čtvrtina šířky štítu</figcaption></figure>
                <div class="lm-text">
                    <p>Do ochranné zóny nezasahuje text, obrázek ani okraj plochy.</p>
                    <p>Nejmenší velikost barevné značky je <b>24 px</b> na výšku (8 mm v tisku), logotypu <b>32 px</b>.
                    Pod 24 px se používá jen jednobarevná podoba; ikona v záložce prohlížeče je výjimka.</p>
                    <p class="lm-sizes">{mark_svg("color", 64)}{mark_svg("color", 40)}{mark_svg("color", 24)}{mark_svg("ink", 16)}
                    <span class="lm-meta">64 · 40 · 24 · 16 px</span></p>
                </div>
            </div>

            <h3>5. Barvy</h3>
            <p>Tři barvy znaku doplňují jejich tmavší odstíny, které unesou text, a tři neutrální tóny papíru a inkoustu.
            Heraldika odstíny nepředepisuje (zlatá se běžně kreslí žlutou); hodnoty níže platí pro tento web.</p>
            <ul class="lm-palette">{palette}</ul>
            <p>Text a odkazy se sázejí jen inkoustem, karmínem a petrolejem – ty mají na papíru kontrast aspoň 4,5 : 1.
            Červeň, zlato a modř znaku jsou barvy ploch a ozdob.</p>

            <h3>6. Písmo</h3>
            <div class="lm-fonts">
                <div class="lm-font"><span class="lm-meta">{FONT_DISPLAY} · nadpisy a název</span>
                    <p class="lm-sample-display">Kronika obce Vranov</p>
                    <p class="lm-sample-display lm-sample-small">{PANGRAM} · 1920–1929</p>
                    <p>Lomené písmo s moderní stavbou: připomíná titulní listy starých kronik, ale čte se bez potíží.
                    Jen pro krátké texty – název, nadpisy oddílů, letopočty.</p></div>
                <div class="lm-font"><span class="lm-meta">{FONT_BODY} · text přepisu</span>
                    <p class="lm-sample-body">{PANGRAM}. <i>Léta Páně 1924 byla úroda dobrá.</i></p>
                    <p>Knižní antikva navržená pro dlouhé čtení na obrazovce.</p></div>
                <div class="lm-font"><span class="lm-meta">{FONT_UI} · navigace a popisky</span>
                    <p class="lm-sample-ui">{PANGRAM} · Strana 123 · sken</p>
                    <p>Bezpatkové písmo pro vše, co není text kroniky: nabídku, rejstříky, hledání, poznámky.</p></div>
            </div>

            <h3>7. Ozdoby</h3>
            <div class="lm-row">
                <figure class="lm-tile lm-tile-paper"><span class="lm-rosette">{rosette}</span><figcaption>Růžice z koruny</figcaption></figure>
                <div class="lm-text">
                    <p>Růžice odděluje nadpis oddílu od textu a tvoří jemný vzor v záhlaví. Používá se střídmě:
                    jedna na nadpis, nikdy jako odrážka v textu přepisu.</p>
                    <p>Záhlaví opakuje dělení štítu – karmínová plocha, pod ní zlatá linka a tenká modrá.</p>
                </div>
            </div>

            <h3>8. Čemu se vyhnout</h3>
            <div class="lm-grid lm-donts">
                <figure class="lm-tile lm-tile-paper"><span class="lm-bad" style="transform:scaleX(1.5)">{mark_svg("color", 80)}</span><figcaption>Nedeformovat</figcaption></figure>
                <figure class="lm-tile lm-tile-paper"><span class="lm-bad" style="transform:rotate(-18deg)">{mark_svg("color", 80)}</span><figcaption>Nenatáčet</figcaption></figure>
                <figure class="lm-tile lm-tile-paper"><span class="lm-bad" style="filter:hue-rotate(140deg)">{mark_svg("color", 80)}</span><figcaption>Neměnit barvy</figcaption></figure>
                <figure class="lm-tile lm-tile-gold"><span class="lm-bad">{mark_svg("color", 80)}</span><figcaption>Nedávat na zlatou ani červenou plochu</figcaption></figure>
            </div>
        </section>'''


BRAND_CSS = '''
        /* --- Značka a logotyp --- */
        .brand-mark { display: block; flex-shrink: 0; }
        .header-inner { position: relative; }
        .header .brand-mark { margin: 0 auto 1rem; filter: drop-shadow(0 3px 6px rgba(0, 0, 0, 0.35)); }
        .header a { color: inherit; }
        .lockup { display: inline-flex; align-items: center; gap: 0.9rem; text-align: left; }
        .lockup-stacked { flex-direction: column; text-align: center; gap: 0.6rem; }
        .lockup-text { display: flex; flex-direction: column; }
        .lockup-name {
            font-family: var(--font-display);
            font-weight: 600;
            font-size: 1.75rem;
            line-height: 1.05;
            color: var(--color-accent);
        }
        .lockup-sub {
            font-family: var(--font-ui);
            font-size: 0.68rem;
            font-weight: 600;
            letter-spacing: 0.16em;
            text-transform: uppercase;
            color: var(--color-text-light);
            margin-top: 0.3rem;
        }
        .lockup-ink .lockup-name { color: var(--color-text); }
        .lockup-light .lockup-name { color: #fffdf8; }
        .lockup-light .lockup-sub { color: #f3d98a; }
        .sidebar-brand { display: block; padding: 0 1.5rem 1.2rem; text-decoration: none; }
        .sidebar-brand .lockup-name { font-size: 1.35rem; }
        .sidebar-brand .lockup { gap: 0.7rem; }
        .footer .brand-mark { margin: 0 auto 0.8rem; opacity: 0.75; }
        .footer a { color: var(--color-accent); }

        /* --- Logomanuál --- */
        .logomanual { font-family: var(--font-ui); line-height: 1.6; }
        .logomanual h3 {
            font-family: var(--font-display);
            font-weight: 600;
            font-size: 1.5rem;
            color: var(--color-accent);
            margin: 2.6rem 0 0.8rem;
        }
        .logomanual p { margin-bottom: 0.8rem; }
        .logomanual a { color: var(--color-blue); }
        .lm-row { display: flex; gap: 1.5rem; align-items: flex-start; }
        .lm-row .lm-tile { flex: 0 0 13rem; }
        .lm-text { flex: 1; min-width: 0; }
        .lm-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(9.5rem, 1fr)); gap: 1rem; margin: 1rem 0; }
        .lm-grid-wide { grid-template-columns: repeat(auto-fit, minmax(17rem, 1fr)); }
        .lm-tile {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            padding: 1.5rem 1rem 0.8rem;
            border: 1px solid var(--color-border);
            border-radius: 6px;
            overflow: hidden;
        }
        .lm-tile-paper { background: var(--color-paper); }
        .lm-tile-carmine { background: var(--color-accent); border-color: var(--color-accent); }
        .lm-tile-gold { background: var(--color-gold); border-color: var(--color-gold); }
        .lm-tile figcaption { font-size: 0.78rem; color: var(--color-text-light); text-align: center; }
        .lm-tile-carmine figcaption { color: #f1d9c9; }
        .lm-tile-gold figcaption { color: var(--color-text); }
        .lm-note, .lm-meta { font-size: 0.85rem; color: var(--color-text-light); }
        .lm-note { border-left: 3px solid var(--color-gold); padding-left: 0.8rem; }
        .lm-meta { display: block; }
        .lm-downloads { font-size: 0.9rem; }
        .lm-zone { display: block; padding: 23px; border: 1px dashed var(--color-blue); background:
            linear-gradient(var(--color-bg), var(--color-bg)) padding-box, transparent; }
        .lm-zone .brand-mark { background: var(--color-paper); outline: 23px solid rgba(31, 163, 200, 0.14); }
        .lm-sizes { display: flex; align-items: flex-end; gap: 1rem; flex-wrap: wrap; }
        .lm-palette { list-style: none; display: grid; gap: 0.6rem; margin: 1rem 0; }
        .lm-swatch { display: flex; gap: 1rem; align-items: stretch; background: var(--color-paper);
            border: 1px solid var(--color-border); border-radius: 6px; overflow: hidden; }
        .lm-chip { flex: 0 0 7.5rem; display: flex; align-items: flex-end; padding: 0.6rem 0.7rem;
            font-size: 0.85rem; font-weight: 600; font-variant-numeric: tabular-nums;
            box-shadow: inset -1px 0 0 var(--color-border); }
        .lm-swatch-text { padding: 0.6rem 0.8rem 0.6rem 0; font-size: 0.9rem; min-width: 0; }
        .lm-swatch-text b { display: block; }
        .lm-font { background: var(--color-paper); border: 1px solid var(--color-border); border-radius: 6px;
            padding: 1.1rem 1.3rem 0.5rem; margin-bottom: 1rem; }
        .lm-font .lm-meta { text-transform: uppercase; letter-spacing: 0.08em; font-size: 0.72rem; font-weight: 600; }
        .lm-sample-display { font-family: var(--font-display); font-weight: 600; font-size: 2.6rem; line-height: 1.15;
            color: var(--color-accent); overflow-wrap: anywhere; }
        .lm-sample-display.lm-sample-small { font-size: 1.35rem; font-weight: 400; color: var(--color-text); }
        .lm-sample-body { font-family: var(--font-body); font-size: 1.15rem; }
        .lm-sample-ui { font-size: 1.15rem; }
        .lm-rosette svg { display: block; width: 72px; height: 72px; }
        .lm-bad { display: block; position: relative; }
        .lm-donts .lm-tile { position: relative; }
        .lm-donts .lm-tile::after {
            content: "";
            position: absolute;
            top: 0.6rem;
            right: 0.6rem;
            width: 1.4rem;
            height: 1.4rem;
            border-radius: 50%;
            background: linear-gradient(45deg, transparent 44%, #fff 44%, #fff 56%, transparent 56%),
                        linear-gradient(-45deg, transparent 44%, #fff 44%, #fff 56%, transparent 56%), #b3261e;
        }
        @media (max-width: 768px) {
            .lm-row { flex-direction: column; }
            .lm-row .lm-tile { flex: none; align-self: stretch; }
            .lm-chip { flex-basis: 5.5rem; }
            .lm-sample-display { font-size: 2rem; }
        }
        @media print {
            .sidebar-brand { display: none; }
        }
'''
