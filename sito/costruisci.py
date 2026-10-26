"""Legge elenco.md, le schede approvate in interventi/ e richieste.md e scrive i dati in sito/dati.js (usato da tutte le pagine);
poi una pagina per report, sito/r/<id>.html (report.html con titolo, descrizione e anteprima dell'area), sitemap.xml e robots.txt.

Uso:  py sito/costruisci.py [AAAA-MM-GG]   (data dei dati; senza argomento, oggi)

Regole applicate al testo (vedi LEGGIMI.md e le richieste sul sito):
- si usano solo le schede con "Stato scheda: approvata";
- si tolgono paragrafi, punti e righe che contengono "non verificato" o che citano giornali/stampa;
- ogni punto di "Cosa non sappiamo" è "[blocca|altra|fonti] **domanda** frasi": si tiene la domanda e si tolgono
  solo le frasi non verificate, di giornali o con le bozze FOIA; un punto senza etichetta ferma la costruzione;
- ogni punto di "Divieti e avvisi" è "[in vigore|non si sa|scaduto|revocato] **atto** frasi", con le stesse regole;
- le righe "- [costo|disponibili|spesi] ..." in cima a "Soldi" sono le cifre del riquadro: ogni cifra ha chi lo dice,
  quando e la fonte, altrimenti la costruzione si ferma; la riga in grassetto prima del blocco ("**frase** [n]") è la frase
  sui soldi del riquadro e della mappa: senza fonte la costruzione si ferma, se manca in una scheda con cifre c'è un avviso;
- la riga "- [confronto] sì|no · motivo" del blocco dice se "Già spesi" e "Soldi disponibili" si possono confrontare:
  con "sì" (due cifre della stessa fonte o della stessa data) il riquadro mostra la barra, con "no" il motivo;
- le righe "- [stranezza · tipo] frase [n]" del blocco sono le stranezze dei soldi (più del previsto, usati per altro,
  più report, fonti non concordano): senza tipo o senza fonte la costruzione si ferma;
- le bozze FOIA non vanno sul sito.
Il testo non viene riscritto: viene solo convertito da Markdown a HTML.
"""
import html, json, math, re, sys
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OGGI = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today()

SITO = "https://bonifiche-ilva.vercel.app/"
FILTRO = re.compile(r"non verificat|\bgiornal[ei]\b|\bstampa\b|quotidian|noinotizie|legambiente", re.I)
ESCLUSE = re.compile(r"^(fonti|cosa non sappiamo|bozza)", re.I)


# ---------- Markdown → HTML (solo quello che usano le schede) ----------
def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", t)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', t)
    t = re.sub(r'(?<!href=")(?<!">)(https?://[^\s<)]+[^\s<).,;])', r'<a href="\1" target="_blank" rel="noopener">link</a>', t)
    return t


def blocks(lines):
    """Divide le righe di una sezione in blocchi: ('p', testo), ('ul'/'ol', [voci]), ('table', righe), ('h', titolo)."""
    out, i = [], 0
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            i += 1; continue
        if ln.startswith("### "):
            out.append(("h", ln[4:].strip())); i += 1; continue
        if ln.lstrip().startswith("|"):
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            out.append(("table", rows)); continue
        m = re.match(r"^(\s*)(-|\d+\.)\s+", ln)
        if m and len(m.group(1)) == 0:
            kind = "ol" if m.group(2)[0].isdigit() else "ul"
            items = []
            while i < len(lines):
                l2 = lines[i]
                m2 = re.match(r"^(\s*)(-|\d+\.)\s+(.*)", l2)
                if m2 and len(m2.group(1)) == 0:
                    items.append([m2.group(3)]); i += 1
                elif l2.strip() and (l2.startswith(" ") or l2.startswith("\t")) and items:
                    items[-1].append(l2); i += 1
                elif not l2.strip() and i + 1 < len(lines) and (lines[i+1].startswith("  ") or re.match(r"^(-|\d+\.)\s", lines[i+1])) and items:
                    i += 1
                else:
                    break
            out.append((kind, items)); continue
        para = [ln.strip()]; i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r"^(\s*)(-|\d+\.)\s|^\||^#", lines[i]):
            para.append(lines[i].strip()); i += 1
        out.append(("p", " ".join(para)))
    return out


def item_html(item):
    """Una voce di lista, con eventuali sotto-voci indentate e tabelle indentate (il testo dopo una tabella va in un paragrafo)."""
    head, rest = item[0], item[1:]
    if FILTRO.search(head):
        return ""
    sub, dopo, testo, i = [], "", [], 0
    while i < len(rest):
        r = rest[i]
        if r.strip().startswith("|"):
            if testo:
                dopo += f"<p>{inline(' '.join(testo))}</p>" if not FILTRO.search(" ".join(testo)) else ""; testo = []
            rows = []
            while i < len(rest) and rest[i].strip().startswith("|"):
                cells = [c.strip() for c in rest[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            dopo += table_html(rows); continue
        m = re.match(r"^\s+(-|\d+\.)\s+(.*)", r)
        if dopo:
            testo.append(r.strip())
        elif m:
            sub.append(m.group(2))
        elif sub:
            sub[-1] += " " + r.strip()
        else:
            head += " " + r.strip()
        i += 1
    if testo and not FILTRO.search(" ".join(testo)):
        dopo += f"<p>{inline(' '.join(testo))}</p>"
    sub = [s for s in sub if not FILTRO.search(s)]
    h = inline(head)
    if sub:
        h += "<ul>" + "".join(f"<li>{inline(s)}</li>" for s in sub) + "</ul>"
    return f"<li>{h}{dopo}</li>"


def table_html(rows):
    head, body = rows[0], [r for r in rows[1:] if not FILTRO.search(" ".join(r))]
    if not body:
        return ""
    th = "".join(f"<th>{inline(c)}</th>" for c in head)
    tr = "".join("<tr>" + "".join(f'<td data-l="{html.escape(re.sub(r"[*]", "", head[k]) if k < len(head) else "")}">{inline(c)}</td>' for k, c in enumerate(r)) + "</tr>" for r in body)
    return f'<div class="tbl"><table class="rt"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'


def section_html(lines):
    out = []
    for kind, val in blocks(lines):
        if kind == "h":
            out.append(f"<h5>{inline(val)}</h5>")
        elif kind == "p":
            if not FILTRO.search(val):
                out.append(f"<p>{inline(val)}</p>")
        elif kind in ("ul", "ol"):
            lis = "".join(item_html(it) for it in val)
            if lis:
                out.append(f"<{kind}>{lis}</{kind}>")
        elif kind == "table":
            out.append(table_html(val))
    return "".join(out)


def frasi(t):
    """Toglie da un testo solo le frasi non verificate, di giornali o che rimandano alle bozze FOIA."""
    parti = re.split(r"(?<=[.!?])\s+(?=[A-ZÀÈÉÌÒÙ«\"(⚠*])", t.strip())
    return " ".join(p for p in parti if not FILTRO.search(p) and not re.search(r"bozz", p, re.I))


ETICHETTE = {"Cosa non sappiamo": ("blocca", "altra", "fonti"), "Divieti e avvisi": ("in vigore", "non si sa", "scaduto", "revocato")}


def domanda(item, nome, sezione="Cosa non sappiamo"):
    """Un punto di "Cosa non sappiamo" ([blocca|altra|fonti] **domanda** frasi) o di "Divieti e avvisi"
    ([in vigore|non si sa|scaduto|revocato] **atto** frasi), con eventuali sotto-voci.
    Restituisce {t: etichetta, q: testo in grassetto, h: testo HTML}; senza etichetta la costruzione si ferma."""
    et = ETICHETTE[sezione]
    m = re.match(r"\[(" + "|".join(et) + r")\]\s+\*\*(.+?)\*\*\s*(.*)", item[0])
    if not m:
        sys.exit(f"{nome}: in \"{sezione}\" un punto non ha l'etichetta " + ", ".join(f"[{e}]" for e in et) + f" seguita dal grassetto: {item[0][:60]}")
    head, sub, coda, rientro = m.group(3), [], "", 0
    for r in item[1:]:
        s = re.match(r"^(\s+)(-|\d+\.)\s+(.*)", r)
        if s:
            sub.append(s.group(3)); rientro = len(s.group(1))
        elif sub and len(r) - len(r.lstrip()) > rientro:   # continua la sotto-voce
            sub[-1] += " " + r.strip()
        elif sub:   # testo dopo l'elenco, rientrato come i trattini
            coda += " " + r.strip()
        else:
            head += " " + r.strip()
    head, sub, coda = frasi(head), [x for x in map(frasi, sub) if x], frasi(coda)
    h = (f"<p>{inline(head)}</p>" if head else "") + ("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in sub) + "</ul>" if sub else "") + (f"<p>{inline(coda)}</p>" if coda else "")
    return {"t": m.group(1), "q": inline(m.group(2).strip()), "h": h}


TIPI_SOLDI = ("costo", "disponibili", "spesi")
MESI_BREVI = ["gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic"]


def riga_soldi(t, nome):
    """Una riga del blocco in cima a "## Soldi" (vedi LEGGIMI.md):
    "[tipo] 18.400.000 € · chi lo dice · quando [n] nota" oppure "[tipo] testo al posto della cifra · nota".
    La cifra può cominciare con "circa" o "meno di". Restituisce {k, p, v (euro o None), pre, lbl, chi, quando, qb, t, src, note}."""
    m = re.match(r"\[(" + "|".join(TIPI_SOLDI) + r")(?: · ([^\]]+))?\]\s+(.*)", t)
    if not m:
        sys.exit(f"{nome}: in \"Soldi\" una riga del blocco non ha l'etichetta [costo], [disponibili] o [spesi]: {t[:60]}")
    if FILTRO.search(t):
        sys.exit(f"{nome}: in \"Soldi\" una riga del blocco va sul sito e non può dire \"non verificato\" o citare giornali: {t[:60]}")
    r = {"k": m.group(1), "p": m.group(2) or "", "v": None, "pre": "", "lbl": "", "chi": "", "quando": "", "qb": "", "t": None, "src": "", "note": ""}
    resto = m.group(3).strip()
    c = re.match(r"(?:(circa|meno di)\s+)?(\d{1,3}(?:\.\d{3})*(?:,\d+)?)\s*€\s*(.*)", resto)
    nota = lambda x: inline(re.sub(r"\s+(?=\[\d+\])", "", x.strip()))   # le note [n] attaccate al testo, come nel resto del sito
    if not c:   # nessuna cifra: il testo da mostrare al posto del numero e, dopo " · ", la spiegazione
        lbl, _, note = resto.partition(" · ")
        r.update(lbl=lbl.strip(), note=nota(note))
        return r
    f = re.match(r"·\s*([^·\[]+?)\s*·\s*([^·\[]+?)\s*((?:\[\d+\])+)\s*(.*)", c.group(3))
    if not f:
        sys.exit(f"{nome}: in \"Soldi\" la cifra {c.group(2)} € deve avere \"· chi lo dice · quando [n]\": {t[:80]}")
    v = float(c.group(2).replace(".", "").replace(",", "."))
    quando = f.group(2)
    y = re.search(r"\b(19|20)\d{2}\b", quando)
    if not y:
        sys.exit(f"{nome}: in \"Soldi\" manca l'anno in \"{quando}\"")
    mese = next((MESI[k] for k in MESI if re.search(r"\b" + k + r"\b", quando.lower())), 0)
    r.update(v=v / 2 if c.group(1) == "meno di" else v,   # "meno di 10.000 €": nei totali conta la metà
             pre=c.group(1) or "", lbl=c.group(2), chi=f.group(1), quando=quando,
             qb=(MESI_BREVI[mese - 1] + " " if mese else "") + y.group(0), t=[int(y.group(0)), mese],
             src=f.group(3), note=nota(f.group(4)))
    return r


def confronto(righe, soldi, nome):
    """La riga "[confronto] sì · motivo" o "[confronto] no · motivo" nel blocco dei soldi (vedi LEGGIMI.md): dice se
    "Già spesi" e "Soldi disponibili" coprono la stessa cosa. Con "sì" il sito mostra la barra con la percentuale
    (calcolo nostro), con "no" il motivo. Con due righe [disponibili · chi] si scrive [confronto · chi].
    Restituisce {si, motivo, p, pct, pre, src} o None se la scheda non ha cifre da confrontare."""
    def cifre(k, p):   # le righe con una cifra di quel tipo; con [confronto · chi], quella di chi (o quella senza nome)
        rr = [r for r in soldi if r["k"] == k and r["v"] is not None]
        return [r for r in rr if r["p"] == p] or [r for r in rr if not r["p"]] if p else rr
    if len(righe) > 1:
        sys.exit(f"{nome}: in \"Soldi\" c'è più di una riga [confronto]")
    if not righe:
        if cifre("disponibili", "") and cifre("spesi", ""):
            sys.exit(f"{nome}: in \"Soldi\" ci sono \"disponibili\" e \"spesi\" ma manca la riga \"[confronto] sì|no · motivo\"")
        return None
    t = righe[0][2:].strip()
    m = re.match(r"\[confronto(?: · ([^\]]+))?\]\s+(sì|no)\s+·\s+(\S.*)", t)
    if not m:
        sys.exit(f"{nome}: in \"Soldi\" la riga deve essere \"[confronto] sì · motivo\" o \"[confronto] no · motivo\": {t[:60]}")
    if FILTRO.search(t):
        sys.exit(f"{nome}: in \"Soldi\" la riga [confronto] va sul sito e non può dire \"non verificato\" o citare giornali")
    p, si, motivo = m.group(1) or "", m.group(2) == "sì", m.group(3).strip()
    c = {"si": si, "motivo": inline(re.sub(r"\s+(?=\[\d+\])", "", motivo)), "p": p, "pct": None, "pre": "",
         "src": "".join(re.findall(r"\[\d+\]", motivo))}
    if not si:
        return c
    d, s = cifre("disponibili", p), cifre("spesi", p)
    if len(d) != 1 or len(s) != 1:
        sys.exit(f"{nome}: in \"Soldi\" [confronto] sì vuole una sola cifra di \"disponibili\" e una di \"spesi\""
                 + (" (con più righe si scrive [confronto · chi])" if len(d) > 1 or len(s) > 1 else ""))
    d, s = d[0], s[0]
    if d["chi"] != s["chi"] and d["qb"] != s["qb"]:
        sys.exit(f"{nome}: in \"Soldi\" [confronto] sì vuole due cifre della stessa fonte o della stessa data: "
                 f"{d['chi']} · {d['qb']} e {s['chi']} · {s['qb']}")
    if d["v"] <= 0:
        sys.exit(f"{nome}: in \"Soldi\" [confronto] sì vuole \"disponibili\" maggiore di 0 €")
    sv = float(s["lbl"].replace(".", "").replace(",", ".")) if s["pre"] == "meno di" else s["v"]   # "meno di 10.000 €": la percentuale si fa sulla cifra scritta
    c.update(pct=round(sv / d["v"] * 100, 3),
             pre="" if sv == 0 else "meno di" if s["pre"] == "meno di" else "circa" if s["pre"] or d["pre"] else "")
    return c


TIPI_STRANEZZA = ("più del previsto", "usati per altro", "più report", "fonti non concordano")


def stranezza(t, nome):
    """Una riga "[stranezza · tipo] frase [n]" nel blocco dei soldi (vedi LEGGIMI.md): una cosa strana nei soldi,
    detta in una frase con la sua fonte. Restituisce {t: tipo, h: frase HTML, src}."""
    m = re.match(r"\[stranezza · (" + "|".join(TIPI_STRANEZZA) + r")\]\s+(\S.*)", t)
    if not m:
        sys.exit(f"{nome}: in \"Soldi\" la riga deve essere \"[stranezza · tipo] frase [n]\" con tipo "
                 + ", ".join(f"\"{x}\"" for x in TIPI_STRANEZZA) + f": {t[:60]}")
    if FILTRO.search(t):
        sys.exit(f"{nome}: in \"Soldi\" la riga [stranezza] va sul sito e non può dire \"non verificato\" o citare giornali")
    frase = m.group(2).strip()
    if not re.search(r"\[\d+\]$", frase):
        sys.exit(f"{nome}: in \"Soldi\" la riga [stranezza] deve finire con la sua fonte: {t[:60]}")
    return {"t": m.group(1), "h": inline(re.sub(r"\s+(?=\[\d+\])", "", frase)), "src": "".join(re.findall(r"\[\d+\]", frase))}


# ---------- coordinate UTM fuso 33 Nord → gradi (WGS84) ----------
def utm33_to_ll(E, N):
    a, f, k0 = 6378137.0, 1 / 298.257223563, 0.9996
    e2 = f * (2 - f); ep2 = e2 / (1 - e2)
    x, y = E - 500000, N
    mu = y / k0 / (a * (1 - e2/4 - 3*e2**2/64 - 5*e2**3/256))
    e1 = (1 - math.sqrt(1 - e2)) / (1 + math.sqrt(1 - e2))
    p = mu + (3*e1/2 - 27*e1**3/32)*math.sin(2*mu) + (21*e1**2/16 - 55*e1**4/32)*math.sin(4*mu) + (151*e1**3/96)*math.sin(6*mu) + (1097*e1**4/512)*math.sin(8*mu)
    C1, T1 = ep2*math.cos(p)**2, math.tan(p)**2
    N1 = a / math.sqrt(1 - e2*math.sin(p)**2); R1 = a*(1 - e2) / (1 - e2*math.sin(p)**2)**1.5; D = x / (N1*k0)
    lat = p - (N1*math.tan(p)/R1)*(D**2/2 - (5 + 3*T1 + 10*C1 - 4*C1**2 - 9*ep2)*D**4/24 + (61 + 90*T1 + 298*C1 + 45*T1**2 - 252*ep2 - 3*C1**2)*D**6/720)
    lon = (D - (1 + 2*T1 + C1)*D**3/6 + (5 - 2*C1 + 28*T1 - 3*C1**2 + 8*ep2 + 24*T1**2)*D**5/120) / math.cos(p)
    return round(math.degrees(lat), 6), round(15 + math.degrees(lon), 6)


num = lambda s: float(s.replace(".", "").replace(",", ".")) if s.count(",") else float(s)


def coordinate(text):
    """Cerca la riga **Coordinate** della scheda: restituisce lat/lon, testo originale e numero della fonte."""
    tutte = coordinate_per_codice(text)
    return next(iter(tutte.values()), None)


def coordinate_per_codice(text):
    """Tutte le righe **Coordinate**: {codice: coordinata}. Se la riga nomina un codice prima dei numeri
    ("**Coordinate** di D1 (SP1): ...") vale per quel codice, altrimenti per tutta la scheda (chiave "*").
    Le righe **Posizione sulla mappa** (centro delle particelle catastali indicate da un documento, calcolato da noi)
    vengono prima delle righe **Coordinate**: "... [n] — Comune, foglio e particelle — ...: E m E – N m N ... Nota: ..."."""
    out = {}
    righe = text.splitlines()
    for chiave in ("**Posizione sulla mappa**", "**Coordinate**"):
        for ln in righe:
            if chiave not in ln or FILTRO.search(ln.split("(conversione")[0]):
                continue
            m = re.search(r"(\d{6}[,.]\d+)\s*m\s*E\s*[–-]\s*(\d{7}[,.]\d+)\s*m\s*N", ln) or re.search(r"X\s*=\s*(\d{6}[,.]\d+)\s*m\s*[–-]\s*Y\s*=\s*(\d{7}[,.]\d+)\s*m", ln)
            n = re.search(r"\[(\d+)\]", ln)
            if m and n:
                E, N = num(m.group(1)), num(m.group(2))
                lat, lon = utm33_to_ll(E, N)
                c = {"ll": [lat, lon], "e": m.group(1), "n": m.group(2), "fonte": int(n.group(1)),
                     "sistema": "RDN2008 / TM33 (EPSG 6708)" if "RDN2008" in ln else "UTM fuso 33 Nord, datum WGS84"}
                if chiave == "**Posizione sulla mappa**":
                    cat = re.search(r"—\s*(.+?)\s*—", ln)
                    nota = re.search(r"Nota:\s*(.+?)\s*$", ln)
                    c.update(metodo="catasto", sistema="UTM fuso 33 Nord, ETRS89", cat=cat.group(1) if cat else "",
                             nota=(lambda x: x[:1].upper() + x[1:])(re.sub(r"\s*\[\d+\]", "", nota.group(1))) if nota else "")
                for cod in re.findall(r"\b[ABCD]\d+\b", ln[:m.start()]) or ["*"]:
                    out.setdefault(cod, c)
    return out


# ---------- date per la cronologia ----------
MESI = {m: i for i, m in enumerate(["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"], 1)}


def data_num(s):
    s = re.sub(r"[*]", "", s).lower()
    if "anni '70" in s or "anni 70" in s:
        return 1970.0
    y = re.search(r"\b(19\d{2}|20\d{2})\b", s)
    if not y:
        return None
    t = float(y.group(1))
    if re.search(r"prima del", s):
        return t - 1
    mese = next((MESI[m] for m in MESI if m in s[: y.start()] or m in s), None)
    g = re.match(r"\s*(\d{1,2})\b", s)
    if mese:
        t += (mese - 1) / 12 + ((int(g.group(1)) - 1) / 31 / 12 if g else 0)
    elif "metà" in s:
        t += .5
    elif "fine" in s:
        t += .9
    return round(t, 4)


# ---------- elenco.md ----------
def leggi_elenco():
    txt = (ROOT / "elenco.md").read_text(encoding="utf-8")
    righe = {}
    for ln in txt.splitlines():
        m = re.match(r"^\|\s*([ABCD]\d+)\s*\|(.+)\|$", ln)
        if not m:
            continue
        c = [x.strip() for x in m.group(2).split("|")]
        name, note, pag, sch = c[0], c[1], c[2], c[3] if len(c) > 3 else ""
        link = re.search(r"interventi/([\w-]+)\.md", sch)
        warn = "⚠" in note
        clean = lambda s: re.sub(r"\s+", " ", re.sub(r"\*\*|\*|⚠|✔", "", s)).strip()
        righe[m.group(1)] = [m.group(1), clean(name), clean(note), pag, link.group(1) if link else None, warn]
    # sottogruppi dei gruppi A (aree di Ilva) e B (ricadute), nell'ordine di elenco.md: [titolo, [codici]]
    # (si saltano quelli senza righe)
    def sottogruppi(lettera):
        sez = txt.split(f"\n## {lettera}.")[1].split("\n## ")[0]
        gr = [[s.split("\n", 1)[0].strip(), re.findall(r"^\|\s*([ABCD]\d+)\s*\|", s, re.M)] for s in sez.split("\n### ")[1:]]
        return [g for g in gr if g[1]]
    return righe, sottogruppi("A"), sottogruppi("B")


# ---------- richieste.md (accesso agli atti: solo colonne pubbliche) ----------
def data_lunga(s):
    g, m, a = (int(x) for x in s.split("/"))
    return f"{g} {list(MESI)[m - 1]} {a}"


def leggi_richieste(codici):
    righe = []
    for ln in (ROOT / "richieste.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\|\s*(\d+)\s*\|(.+)\|$", ln)
        if not m:
            continue
        aree, a, cosa, inviata, entro = [x.strip() for x in m.group(2).split("|")]
        aree = [x.strip() for x in aree.split(",")]
        for k in aree:
            if k not in codici:
                sys.exit(f"richieste.md, richiesta {m.group(1)}: il codice {k} non è in elenco.md")
        righe.append({"n": m.group(1), "aree": aree, "a": a, "cosa": cosa, "inviata": data_lunga(inviata),
                      "entro": data_lunga(entro), "e": [int(x) for x in reversed(entro.split("/"))], "t": [int(x) for x in reversed(inviata.split("/"))]})
    return righe


def leggi_fonti(body):
    """Righe "[n] testo, link — copia in fonti/..." → [{n, html, url}] (la copia locale non va sul sito)."""
    joined, fon = "\n".join(body), []
    for fm in re.finditer(r"^\[(\d+)\]\s+(.+?)(?=\n\s*\n|^\[\d+\]\s|\Z)", joined, re.M | re.S):
        raw = " ".join(fm.group(2).split())
        url = re.search(r"https?://[^\s)]+", raw)
        testo = re.split(r"\s+—\s+copi[ae]", raw)[0]
        testo = re.sub(r",?\s*https?://\S+", "", testo).strip(" ,")
        fon.append({"n": int(fm.group(1)), "html": inline(testo), "url": url.group(0).rstrip(".,;") if url else None})
    return fon


def immagini_di(lines):
    """Righe "**Immagine:** file.jpg" → [nomi dei file]."""
    return [re.match(r"\*\*Immagine:\*\*\s*(\S+)", l.strip()).group(1) for l in lines if l.strip().startswith("**Immagine:**")]


def immagine(lines):
    """La prima riga "**Immagine:**" → nome del file (o None)."""
    return (immagini_di(lines) or [None])[0]


# ---------- immagini.md: registro delle foto (autore, licenza, originale) ----------
def leggi_immagini():
    out = {}
    for ln in (ROOT / "immagini.md").read_text(encoding="utf-8").splitlines():
        c = [x.strip() for x in ln.strip().strip("|").split("|")]
        if len(c) == 5 and re.search(r"\.(jpe?g|png|webp)$", c[0]):
            out[c[0]] = {"did": c[1], "autore": c[2], "licenza": c[3], "url": c[4]}
    return out


# ---------- contesto.md: testi della homepage ----------
def leggi_contesto():
    txt = (ROOT / "contesto.md").read_text(encoding="utf-8")
    secs = {}
    for s in txt.split("\n## ")[1:]:
        titolo, _, corpo = s.partition("\n")
        secs[titolo.strip().lower()] = corpo.splitlines()
    sotto = lambda lines: [(s.split("\n", 1)[0].strip(), s.split("\n", 1)[1].splitlines() if "\n" in s else [])
                           for s in "\n".join(lines).split("\n### ")[1:]]
    prima = lambda lines: "\n".join(lines).split("\n### ")[0].splitlines()   # righe prima del primo ###
    testo = lambda lines: [l for l in lines if not l.strip().startswith("**Immagine:**")]
    out = {}

    st = secs["storia"]
    eventi = []
    for kind, val in blocks(testo(st)):
        if kind == "table":
            for r in val[1:]:
                eventi.append({"t": data_num(r[0]), "quando": r[0], "cosa": inline(r[1]), "fonte": r[2] if len(r) > 2 else ""})
    out["storia"] = {"img": immagini_di(st), "intro": "".join(f"<p>{inline(v)}</p>" for k, v in blocks(testo(st)) if k == "p"), "eventi": eventi}

    ci = secs["come inquina"]
    colonne = []
    for titolo, righe in sotto(ci):
        voci = []
        for kind, val in blocks(righe):
            if kind == "ul":
                for it in val:
                    riga = " ".join(x.strip() for x in it)
                    testo_v, _, codici = riga.partition("→")
                    m = re.match(r"\*\*(.+?)\*\*:?\s*(.*)", testo_v.strip())
                    voci.append({"nome": m.group(1), "html": inline(m.group(2)), "codici": re.findall(r"[ABCD]\d+", codici)})
        colonne.append({"titolo": titolo, "voci": voci})
    out["inquina"] = {"img": immagini_di(ci), "intro": section_html(testo(prima(ci))), "colonne": colonne}

    fa = secs["la fabbrica"]
    reparti, dopo, visto = [], [], False
    for kind, val in blocks(testo(fa)):
        if kind == "ol":
            visto = True
            for it in val:
                m = re.match(r"\*\*(.+?)\*\*:?\s*(.*)", " ".join(x.strip() for x in it))
                reparti.append({"nome": m.group(1), "html": inline(m.group(2))})
        elif kind == "p":
            (dopo if visto else out.setdefault("_fa_intro", [])).append(f"<p>{inline(val)}</p>")
    out["fabbrica"] = {"img": immagini_di(fa), "intro": "".join(out.pop("_fa_intro", [])), "reparti": reparti, "chiusura": "".join(dopo)}

    gl = []
    for titolo, righe in sotto(secs["glossario"]):
        parole = next((re.match(r"\*Parole:\s*(.+?)\*", l.strip()).group(1) for l in righe if l.strip().startswith("*Parole:")), "")
        corpo = [l for l in righe if not l.strip().startswith("*Parole:")]
        gl.append({"id": "g-" + re.sub(r"[^a-z]", "", titolo.split()[0].lower()), "titolo": titolo,
                   "parole": [p.strip() for p in parole.split(",") if p.strip()], "html": section_html(corpo)})
    out["glossario"] = gl
    out["fonti"] = leggi_fonti(secs["fonti"])
    return out


# ---------- fondi.md: da dove vengono i soldi (pagina sito/soldi.html) ----------
# le voci di un fondo, nell'ordine del percorso dei soldi: dato (chi, atto, quanto, per cosa) → finito in quali report → speso
DATO = ("Chi lo dà", "Atto", "Importo", "Per cosa", "CUP", "Versati al Commissario", "Quanto resta")
ALTRE_FONDI = ("In breve", "Citati nelle schede ma non per la bonifica", "Report senza un fondo conosciuto", "Cosa non sappiamo", "Fonti")


def slug(t):
    t = t.lower().translate(str.maketrans("àèéìòù", "aeeiou"))
    s = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    return s[:50].rsplit("-", 1)[0] if len(s) > 50 else s


def euro_breve(v):
    """Come fmtSoldi in comune.js: sotto il milione euro interi, sopra milioni con due decimali, dal miliardo miliardi."""
    if v >= 1e9:
        return f"{v / 1e9:,.2f}".replace(",", " ").replace(".", ",").replace(" ", ".") + " miliardi €"
    if v >= 1e6:
        return f"{v / 1e6:,.2f}".replace(",", " ").replace(".", ",").replace(" ", ".") + " mln €"
    return f"{round(v):,}".replace(",", ".") + " €"


cifra_it = lambda s: float(s.replace(".", "").replace(",", "."))
CERTEZZA = ("certo", "probabile", "calcolo nostro")   # certo: la cifra è in una relazione; probabile: lo dicono gli indizi delle fonti
PEZZO = re.compile(r"((?:al massimo )?circa )?(\d{1,3}(?:\.\d{3})*(?:,\d+)?) milioni € · ([^·:]+?) · (" + "|".join(CERTEZZA) + r")(?: · sulla linea ([^:]+?))?: (.+)$")


def pezzi_fondo(f, k, titolo):
    """I pezzi di un fondo per le barre "come erano divisi" (**Per cosa**) e "dove sono andati" (**Usati per altro**): sotto-voci
    "cifra milioni € · nome breve · certo|probabile|calcolo nostro[ · sulla linea mese anno]: testo con le fonti". Le
    sotto-voci che non cominciano con una cifra restano solo testo; si ferma se una cifra non ha il formato o la fonte."""
    if k not in f["voci"]:
        sys.exit(f"fondi.md, {titolo}: manca la voce **{k}:**, che serve alle barre del Patrimonio Destinato")
    pezzi = []
    for r in f["voci"][k]["sub"]:
        m = PEZZO.match(r)
        if not m:
            if re.match(r"(?:(?:al massimo )?circa )?\d", r):
                sys.exit(f"fondi.md, {titolo}, **{k}**: la riga deve essere \"cifra milioni € · nome · certo|probabile|calcolo nostro: testo [n]\": {r[:60]}")
            continue
        pre, num, nome, cert, linea, txt = m.groups()
        fonti = "".join(dict.fromkeys(re.findall(r"\[\d+\]", txt)))
        if not fonti or (cert == "calcolo nostro" and "(calcolo nostro)" not in txt):
            sys.exit(f"fondi.md, {titolo}, **{k}**: la riga \"{nome}\" deve avere le fonti" + (" e \"(calcolo nostro)\"" if cert == "calcolo nostro" else ""))
        t = None
        if linea:
            mese, anno = next((MESI[x] for x in MESI if re.search(r"\b" + x + r"\b", linea.lower())), 0), re.search(r"\b20\d{2}\b", linea)
            if not mese or not anno:
                sys.exit(f"fondi.md, {titolo}, **{k}**: \"sulla linea\" vuole mese e anno: {linea}")
            t = int(anno.group(0)) + mese / 12
        pezzi.append({"v": cifra_it(num), "lbl": num, "pre": (pre or "").strip(), "nome": nome.strip(), "cert": cert, "t": t, "fonti": fonti})
    if not pezzi:
        sys.exit(f"fondi.md, {titolo}, **{k}**: nessuna riga con la cifra")
    return pezzi


def semestri_fondo(f, titolo):
    """Le sotto-voci di **Speso** "primo|secondo semestre anno · cifra alla fabbrica · cifra di Ilva [n]" (o "· relazioni non
    trovate") e la riga "In questi N semestri fanno X milioni per la fabbrica e Y milioni di Ilva (calcolo nostro)": la
    costruzione si ferma se il totale non torna (con le cifre arrotondate può cambiare di un centesimo per semestre)."""
    righe, tot = [], None
    for r in f["voci"].get("Speso", {"sub": []})["sub"]:
        m = re.match(r"((?:primo|secondo) semestre \d{4}(?: e (?:primo|secondo) semestre \d{4})?) · (.+)$", r)
        if not m:
            mt = re.match(r"In questi (\d+) semestri fanno ([\d.,]+) milioni per la fabbrica e ([\d.,]+) milioni di Ilva \(calcolo nostro\)", r)
            tot = (int(mt.group(1)), mt.group(2), mt.group(3)) if mt else tot
            continue
        if m.group(2).startswith("relazioni non trovate"):
            righe.append({"quando": m.group(1), "manca": m.group(2)}); continue
        pp = m.group(2).split(" · ")
        fonti = re.search(r"((?:\[\d+\])+)$", pp[-1])
        if len(pp) != 2 or not fonti:
            sys.exit(f"fondi.md, {titolo}, **Speso**: la riga deve essere \"semestre · cifra alla fabbrica · cifra di Ilva [n]\": {r[:60]}")
        val = lambda p: 0.0 if p.startswith("nessun") else cifra_it(re.match(r"([\d.,]+) milioni", p).group(1))
        righe.append({"quando": m.group(1), "fab": val(pp[0]), "ilva": val(pp[1]), "fonti": fonti.group(1)})
    if not righe:
        return None
    dati = [x for x in righe if "manca" not in x]
    if not tot or tot[0] != len(dati) or any(abs(sum(x[k] for x in dati) - cifra_it(s)) > .006 * len(dati) for k, s in (("fab", tot[1]), ("ilva", tot[2]))):
        sys.exit(f"fondi.md, {titolo}, **Speso**: manca la riga \"In questi N semestri fanno ...\" o le cifre non tornano con i {len(dati)} semestri")
    return {"righe": righe, "tot": tot}


def leggi_fondi(schede):
    """Una sezione "## nome" per fondo, con voci "- **Chi lo dà:** ...", "**Report:**" (sotto-voci "[scheda] cifra"),
    "**Speso:**", "**Da sapere:**"; le sezioni senza testo ("## Fondi pubblici") sono i gruppi. Restituisce
    {gruppi: [[titolo, [fondo]]], altre: {titolo: righe}, fonti, controllo}; si ferma se un fondo non ha chi, importo
    o report, se una scheda non esiste o se una fonte non è nell'elenco."""
    txt = (ROOT / "fondi.md").read_text(encoding="utf-8")
    ids = {s["id"] for s in schede}
    gruppi, altre = [], {}
    for sez in txt.split("\n## ")[1:]:
        titolo, _, corpo = sez.partition("\n")
        titolo, righe = titolo.strip(), [l for l in corpo.splitlines() if l.strip() != "---"]
        if titolo in ALTRE_FONDI:
            altre[titolo] = righe; continue
        if not any(l.strip() for l in righe):
            gruppi.append([titolo, []]); continue
        f = {"nome": titolo, "id": "f-" + slug(titolo), "voci": {}, "report": []}
        for kind, val in blocks(righe):
            for it in (val if kind == "ul" else []):
                m = re.match(r"\*\*(.+?):?\*\*:?\s*(.*)", it[0])
                if not m:
                    sys.exit(f"fondi.md, {titolo}: una voce non comincia con l'etichetta in grassetto: {it[0][:60]}")
                sub, rientro = [], None
                for r in it[1:]:   # sotto-voci "  - ..." (le righe rientrate di più continuano la sotto-voce)
                    s = re.match(r"^(\s+)-\s+(.*)", r)
                    if s and (rientro is None or len(s.group(1)) <= rientro):
                        sub.append(s.group(2)); rientro = len(s.group(1))
                    elif sub:
                        sub[-1] += " " + r.strip()
                f["voci"][m.group(1).strip()] = {"testo": m.group(2).strip(), "sub": sub}
        for k in ("Chi lo dà", "Importo", "Report"):
            if k not in f["voci"]:
                sys.exit(f"fondi.md, {titolo}: manca la voce **{k}:**")
        for r in f["voci"]["Report"]["sub"]:
            sm = re.match(r"\[([a-z0-9-]+)\]\s*(.*)", r)
            if sm:
                if sm.group(1) not in ids:
                    sys.exit(f"fondi.md, {titolo}: la scheda [{sm.group(1)}] non c'è fra le schede approvate")
                f["report"].append(sm.group(1))
        imp = re.search(r"(\d{1,3}(?:\.\d{3})*(?:,\d+)?)\s*(miliardi|milioni)?\s*€", f["voci"]["Importo"]["testo"])
        f["importo"] = float(imp.group(1).replace(".", "").replace(",", ".")) * {"miliardi": 1e9, "milioni": 1e6}.get(imp.group(2), 1) if imp else None
        if "Quanto resta" in f["voci"]:   # la linea "Quanto resta": una sotto-voce "cifra milioni € · fine mese anno [n]" per punto
            f["resta"], f["resta_note"] = [], []
            for r in f["voci"]["Quanto resta"]["sub"]:
                if r.startswith("Nota:"):   # "Nota: frase [n]": va accanto alla linea
                    if not re.search(r"\[\d+\]\.?$", r):
                        sys.exit(f"fondi.md, {titolo}: in **Quanto resta** la nota deve finire con la fonte: {r[:60]}")
                    f["resta_note"].append(r[5:].strip()); continue
                rm = re.match(r"(\d{1,3}(?:\.\d{3})*(?:,\d+)?)\s*milioni €\s*·\s*([^\[·]+?)\s*((?:\[\d+\])+)$", r)
                mese = next((MESI[k] for k in MESI if re.search(r"\b" + k + r"\b", rm.group(2).lower())), 0) if rm else 0
                anno = re.search(r"\b(?:19|20)\d{2}\b", rm.group(2)) if rm else None
                if not mese or not anno:
                    sys.exit(f"fondi.md, {titolo}: in **Quanto resta** ogni riga deve essere \"cifra milioni € · mese anno [n]\": {r[:60]}")
                f["resta"].append({"v": float(rm.group(1).replace(".", "").replace(",", ".")), "lbl": rm.group(1), "quando": rm.group(2).strip(),
                                   "t": int(anno.group(0)) + mese / 12, "anno": int(anno.group(0)), "src": rm.group(3)})
            if not f["resta"]:
                sys.exit(f"fondi.md, {titolo}: **Quanto resta** non ha righe \"cifra milioni € · mese anno [n]\"")
            f["pezzi"] = {k: pezzi_fondo(f, k, titolo) for k in ("Per cosa", "Usati per altro")}
            prev = sum(p["v"] for p in f["pezzi"]["Per cosa"])
            if not f["importo"] or abs(prev - f["importo"] / 1e6) > .5:
                sys.exit(f"fondi.md, {titolo}: i pezzi di **Per cosa** fanno {num_it(prev, 2)} milioni, non l'importo")
            f["semestri"] = semestri_fondo(f, titolo)
        if not gruppi:
            sys.exit(f"fondi.md: il fondo {titolo} non sta sotto un gruppo (## Fondi pubblici, ## I soldi di Ilva)")
        gruppi[-1][1].append(f)
    fonti = leggi_fonti(altre.get("Fonti", []))
    numeri = {x["n"] for x in fonti}
    for n in map(int, re.findall(r"\[(\d+)\]", txt.split("\n## Fonti")[0])):
        if n not in numeri:
            sys.exit(f"fondi.md: la fonte [{n}] non è nell'elenco delle fonti")
    controllo = next((l.strip() for l in altre.get("Fonti", []) if l.startswith("Ultimo controllo")), "")
    breve = []   # "## In breve": i paragrafi in cima alla pagina; ogni frase finisce con la sua fonte o con "(calcolo nostro)"
    for kind, val in blocks(altre.get("In breve", [])):
        for b in ([val] if kind == "p" else []):
            for fr in re.split(r"(?<=[.!?])\s+(?=[A-ZÀÈÉÌÒÙ«\"(⚠*])", b.strip()):   # le frasi, come in frasi()
                if FILTRO.search(fr) or not re.search(r"(?:\[\d+\]|\(calcolo nostro\))\.?$", fr):
                    sys.exit(f"fondi.md, In breve: ogni frase deve finire con la sua fonte [n] o con \"(calcolo nostro)\": {fr[:60]}")
            breve.append(b)
    return {"gruppi": [g for g in gruppi if g[1]], "altre": altre, "fonti": fonti, "controllo": controllo, "breve": breve}


def num_it(x, dec, fisso=True):
    """Un numero all'italiana arrotondato come toLocaleString("it-IT") del sito: dec decimali fissi o, con fisso=False, al massimo dec."""
    s = f"{Decimal(x).quantize(Decimal(1).scaleb(-dec), ROUND_HALF_UP):,.{dec}f}".replace(",", " ").replace(".", ",").replace(" ", ".")
    return s.rstrip("0").rstrip(",") if dec and not fisso else s


# le cifre come le scrive il sito (fmtSoldi, fmtRiga, pctSpesi e barraSpesi in comune.js): i totali e le barre di soldi.html
# si calcolano qui, così la pagina resta statica; devono coincidere con quelli della home
NOMI_SOLDI = {"disponibili": "Soldi disponibili", "spesi": "Già spesi"}   # come NOMI_SOLDI in comune.js
fmt_soldi = lambda v: (num_it(v, 0), "€") if v < 1e6 else (num_it(v / 1e6, 2), "mln €")
fmt_riga = lambda r: (r["lbl"], "€") if r["pre"] == "meno di" else fmt_soldi(r["v"])
num_js = lambda x: str(int(x)) if float(x).is_integer() else repr(float(x))   # un numero scritto come in JavaScript (5.0 → 5)


def pct_spesi(c):
    if 0 < c["pct"] < 0.1:
        return "meno di 0,1%"
    return (c["pre"] + " " if c["pre"] else "") + num_it(c["pct"], 1 if c["pct"] < 100 else 0, False) + "%"


def barra_spesi(c):
    p = c["pct"]
    return (f'<span class="bar" role="img" aria-label="Già spesi: {pct_spesi(c)} dei soldi disponibili">'
            + (f'<span style="width:{num_js(min(p, 100))}%"></span>' if p > 0 else "")
            + (f'<i style="left:{num_js(100 / p * 100)}%"></i>' if p > 100 else "") + "</span>")


def ordine_codice(c, gruppo_di):   # come codeCmp in comune.js: gruppo A prima del B, poi lettera e numero
    return (gruppo_di.get(c, "Z"), c[0], int(c[1:]))


def elenco_codici(cs, gruppo_di):
    """Come elencoCodici nella home: numeri di fila uniti ("D1–D5", "A5 e A6")."""
    cs, pezzi, i = sorted(cs, key=lambda c: ordine_codice(c, gruppo_di)), [], 0
    while i < len(cs):
        j = i
        while j + 1 < len(cs) and cs[j + 1][0] == cs[i][0] and int(cs[j + 1][1:]) == int(cs[j][1:]) + 1:
            j += 1
        pezzi += [f"{cs[i]}–{cs[j]}"] if j - i >= 2 else cs[i:j + 1]; i = j + 1
    return ", ".join(pezzi[:-1]) + " e " + pezzi[-1] if len(pezzi) > 1 else "".join(pezzi)


def grafico_resta(f, eventi=()):
    """La linea di quanto resta del Patrimonio Destinato (voce **Quanto resta** di fondi.md): un punto per anno, l'ultima cifra
    dell'anno (tutte le cifre sono nella tabella), una linea solo fra due punti a non più di un anno l'uno dall'altro; dove mancano le cifre una fascia "nessuna cifra". Statico:
    griglia, fascia e linea in un SVG che si allunga con il riquadro (su schermo grande è alto quanto la colonna accanto),
    scritte e punti in HTML posizionati in percentuale, così non si deformano. Le cifre al tocco le mostra il codice in
    fondo alla pagina."""
    pts = sorted({p["anno"]: p for p in sorted(f["resta"], key=lambda p: p["t"])}.values(), key=lambda p: p["t"])
    W, H, L, R, T, B = 360, 214, 40, 14, 30, 24
    x0, x1 = math.floor(pts[0]["t"]) - .2, math.floor(pts[-1]["t"]) + 1
    ymax = math.ceil(max(p["v"] for p in pts) / 400) * 400
    X = lambda t: round(L + (t - x0) / (x1 - x0) * (W - L - R), 1)
    Y = lambda v: round(T + (1 - v / ymax) * (H - T - B), 1)
    pos = lambda x, y: f'left:{round(x / W * 100, 2)}%;top:{round(y / H * 100, 2)}%'
    scritta = lambda x, y, t, cls="": f'<span class="lb {cls}" style="{pos(x, y)}">{t}</span>'   # cls: r (finisce lì), l (comincia lì), centrata se manca
    g, s = [], [scritta(L - 6, T - 16, "mln €", "r")]
    for v in range(0, ymax + 1, 400):   # griglia leggera, una riga ogni 400 milioni
        g.append(f'<line class="gl" x1="{L}" x2="{W - R}" y1="{Y(v)}" y2="{Y(v)}"/>')
        s.append(scritta(L - 6, Y(v), num_it(v, 0), "r"))
    for a in range(math.floor(x0) + 1, math.floor(x1) + 1):   # un'etichetta per anno, a metà dell'anno
        g.append(f'<line class="gl" x1="{X(a)}" x2="{X(a)}" y1="{Y(0)}" y2="{Y(0) + 4}"/>')
        if a < x1:
            s.append(scritta(X(a + .5), H - 9, a))
    linee, tratto = [], [pts[0]]
    for a, b in zip(pts, pts[1:]):
        if b["t"] - a["t"] > 1.01:   # più di un anno senza cifre: niente linea, una fascia
            g.append(f'<rect class="buco" x="{X(a["t"])}" y="{T}" width="{round(X(b["t"]) - X(a["t"]), 1)}" height="{round(Y(0) - T, 1)}"/>')
            s.append(scritta((X(a["t"]) + X(b["t"])) / 2, Y(ymax / 2), f'nessuna cifra<br>{math.ceil(a["t"])}–{math.ceil(b["t"]) - 2}', "buco-t"))
            linee.append(tratto); tratto = []
        tratto.append(b)
    linee.append(tratto)
    for i, (quando, nome) in enumerate(eventi):   # i soldi tolti al fondo: una riga gialla alla data, la cifra in alto a scalini
        g.append(f'<line class="ev" x1="{X(quando)}" x2="{X(quando)}" y1="{T - 4}" y2="{Y(0)}"/>')
        s.append(scritta(X(quando) - 2, T + 2 + i * 15, nome, "r ev-t"))
    g += [f'<polyline class="ln" points="{" ".join(f"{X(p["t"])},{Y(p["v"])}" for p in tr)}"/>' for tr in linee if len(tr) > 1]
    for p in pts:
        t = f'{p["quando"]}: {p["lbl"]} milioni €'
        s.append(f'<span class="pt" tabindex="0" role="img" aria-label="{t}" data-t="{t}" style="{pos(X(p["t"]), Y(p["v"]))}"><i class="dot"></i></span>')
    primo, ultimo = pts[0], pts[-1]   # etichette solo sul primo e sull'ultimo punto; le altre cifre al tocco e nella tabella
    s.append(scritta(X(primo["t"]) + 8, Y(primo["v"]) - 12, primo["lbl"], "l val")
             + scritta(X(ultimo["t"]) + 4, Y(ultimo["v"]) + 16, ultimo["lbl"], "r val"))   # sotto: sopra passa la linea
    titolo = "Quanto restava nel Patrimonio Destinato, in milioni di euro: " + "; ".join(f'{p["quando"]} {p["lbl"]}' for p in pts)
    return (f'<figure class="resta" aria-label="{titolo}"><svg viewBox="0 0 {W} {H}" preserveAspectRatio="none" aria-hidden="true">{"".join(g)}</svg>'
            f'{"".join(s)}<div class="resta-tip" hidden></div></figure>')


def tabella_resta(f, cita, note=""):   # tutte le cifre, anche quelle che non sono sulla linea; sotto, le note della voce
    pts = sorted(f["resta"], key=lambda p: p["t"])
    tab = (f'<details class="note"><summary>Tutte le cifre in una tabella ({len(pts)})</summary><table class="resta-tab"><thead><tr><th>Quando</th><th>Quanto restava</th></tr></thead><tbody>'
           + "".join(f'<tr><td>{p["quando"]}</td><td>{p["lbl"]} milioni €{cita(p["src"])}</td></tr>' for p in pts) + f"</tbody></table>{note}</details>")
    return tab


def scrivi_soldi(fondi, schede, gruppo_di, short):
    """sito/soldi.html, "I soldi della bonifica": In breve, i totali, dove i soldi sono fermi, le stranezze, quanto resta
    del Patrimonio Destinato, i fondi report per report, un riquadro per fondo con il percorso dei soldi (dato → finito
    in quali report → speso), poi i fondi non per la bonifica, i report senza fondo, cosa non sappiamo e le fonti.
    Pagina statica: si legge anche senza JavaScript (il codice in fondo apre la fonte o il fondo indicati dal link e
    mostra le cifre della linea al tocco)."""
    schede = sorted(schede, key=lambda s: ordine_codice(s["code"], gruppo_di))   # nell'ordine della home
    per_id = {s["id"]: s for s in schede}

    def cita(h, base="#fondi-f"):   # come cite() in comune.js: [3][4][5] → [3–5]; base: dove porta il numero
        def nota(m):
            ns, pezzi, i = sorted({int(x) for x in re.findall(r"\d+", m.group(0))}), [], 0
            while i < len(ns):
                j = i
                while j + 1 < len(ns) and ns[j + 1] == ns[j] + 1:
                    j += 1
                if j - i >= 2:
                    pezzi.append(f'<a href="{base}{ns[i]}-{ns[j]}" aria-label="fonti da {ns[i]} a {ns[j]}">{ns[i]}–{ns[j]}</a>'); i = j + 1
                else:
                    pezzi.append(f'<a href="{base}{ns[i]}" aria-label="fonte {ns[i]}">{ns[i]}</a>'); i += 1
            return f'<sup class="c">[{", ".join(pezzi)}]</sup>'
        return re.sub(r"(?:\[\d+\])+", nota, h)

    testo = lambda t: cita(inline(re.sub(r"\s+(?=\[\d+\])", "", frasi(t))))
    nome_breve = lambda s: short.get(s["id"]) or re.split(r" \(|:", s["title"])[0]

    def chip(sid):
        s = per_id[sid]
        return f'<a class="area g{gruppo_di.get(s["code"], "A")}" href="r/{sid}.html"><b>{elenco_codici(s["codes"], gruppo_di)}</b>{html.escape(nome_breve(s))}</a>'

    # ---- i totali (spostati dalla home): si sommano solo "Soldi disponibili" e "Già spesi"; le cifre dette da Ilva a parte
    ilva = lambda r: bool(re.match(r"Ilva\b", r["chi"]))
    righe = [(s, r) for s in schede for r in s["soldi"] if r["v"] is not None]

    def casella(k, di_ilva):
        rr = [(s, r) for s, r in righe if r["k"] == k and ilva(r) == di_ilva]
        n, u = fmt_soldi(sum(r["v"] for _, r in rr))
        return f'<div><small>{NOMI_SOLDI[k]}</small><b>{n}</b><span class="small muted">{u}</span><span class="small">in {len({s["id"] for s, _ in rr})} report</span></div>'
    for k in ("disponibili", "spesi"):   # i totali scritti in "In breve" devono essere quelli di oggi
        for di_ilva in (False, True):
            n = fmt_soldi(sum(r["v"] for s, r in righe if r["k"] == k and ilva(r) == di_ilva))[0]
            if fondi["breve"] and not any(f"**{n}" in b for b in fondi["breve"]):
                sys.exit(f"fondi.md, In breve: manca il totale {NOMI_SOLDI[k]} {'secondo Ilva' if di_ilva else 'dei fondi pubblici'}, {n} (in grassetto)")
    blocco = lambda titolo, sotto, di_ilva: f'<div><h4>{titolo}<small>{sotto}</small></h4><div class="soldi" style="--n:2">{casella("disponibili", di_ilva)}{casella("spesi", di_ilva)}</div></div>'
    SOTTO = {False: "A date diverse: ogni report dice quando e da dove vengono", True: "Tabella di Ilva in amministrazione straordinaria, febbraio 2023"}
    con_cifre = {s["id"] for s, r in righe if r["k"] != "costo"}
    senza = [s for s in schede if s["id"] not in con_cifre]
    stimati = len({s["id"] for s, r in righe if r["k"] == "costo"})
    js = (ROOT / "sito" / "comune.js").read_text(encoding="utf-8")
    info = ('<button type="button" class="info-i" aria-expanded="false" aria-controls="soldi-info" aria-label="Cosa vogliono dire le cifre">i</button>',
            re.search(r'^const soldiInfoBox = id => `(.*?)`;', js, re.M | re.S).group(1).replace("${id}", "soldi-info"))
    quanti = lambda n: "Il report" if n == 1 else f'{"Gli" if str(n).startswith("8") or n == 11 else "I"} {n} report'
    totali = (f'<section class="card chart soldi-tot sz" id="totali"><h2>I totali {info[0]}</h2>{info[1]}'
              '<p class="chart-intro">Quanti soldi sono disponibili e quanti sono già stati spesi, sommando le cifre dei report (somme fatte da noi). Le cifre di Ilva sono a parte: le ha dichiarate Ilva e nessun ente pubblico le ha controllate.</p>'
              f'<div class="tot">{blocco("Fondi pubblici", SOTTO[False], False)}{blocco("Secondo Ilva", SOTTO[True], True)}</div>'
              f'<p class="note">Le cifre ci sono in {len(con_cifre)} report su {len(schede)}. Non sommiamo quanto costerebbero i lavori: la cifra c\'è solo in {stimati} report.</p>'
              + (f'<details class="note"><summary>{quanti(len(senza))} senza cifre</summary><div class="aree">{"".join(chip(s["id"]) for s in senza)}</div></details>' if senza else "")
              + "</section>")

    # ---- dove i soldi sono fermi: per gruppo le barre "Già spesi su Soldi disponibili" dei report con [confronto] sì,
    # dalla percentuale più bassa; sotto i report con cifre del gruppo ma senza barra, con il motivo
    cifre_di = lambda s, k, di_ilva: [r for r in s["soldi"] if r["k"] == k and r["v"] is not None and ilva(r) == di_ilva]
    fra = lambda r: (r["pre"] + " " if r["pre"] else "") + " ".join(fmt_riga(r))

    def ferme(di_ilva):
        barre, altri = [], []
        for s in schede:
            d, sp, cf = cifre_di(s, "disponibili", di_ilva), cifre_di(s, "spesi", di_ilva), s["confronto"]
            if not d and not sp:
                continue
            dc = None
            if cf and cf["si"]:
                dc = (next((r for r in d if r["p"] == cf["p"]), None) or next((r for r in d if not r["p"]), None)) if cf["p"] else (d[0] if d else None)
            if dc:
                barre.append((s, cf, dc, sp[0])); continue
            altri.append((s, d[0] if d else None, sp[0] if sp else None,
                          html.unescape(re.sub(r"<[^>]+>", "", re.sub(r"\[\d+\]", "", cf["motivo"]))) if cf and not cf["si"]
                          else "nel report c'è solo la cifra dei soldi disponibili" if not sp else "nel report c'è solo la cifra dei già spesi"))
        barre.sort(key=lambda b: b[1]["pct"])
        li = lambda s, cf, d, sp: (f'<li><a href="r/{s["id"]}.html"><span class="fr-n"><b class="g{gruppo_di.get(s["code"], "A")}">{elenco_codici(s["codes"], gruppo_di)}</b>{html.escape(nome_breve(s))}</span>'
                                   f'<span class="fr-p">{pct_spesi(cf)}</span>{barra_spesi(cf)}<small>{fra(sp)} già spesi su {fra(d)} disponibili{" (la tacca segna i soldi disponibili)" if cf["pct"] > 100 else ""}</small></a></li>')
        # senza confronto: la stessa riga e la stessa barra, vuota, con "?" al posto della percentuale
        cosa = lambda d, sp: (f"{fra(sp)} già spesi · {fra(d)} disponibili" if d and sp
                              else f"{fra(d)} disponibili · già spesi: non si sa" if d else f"{fra(sp)} già spesi · disponibili: non si sa")
        nd = lambda s, d, sp, p: (f'<li><a href="r/{s["id"]}.html"><span class="fr-n"><b class="g{gruppo_di.get(s["code"], "A")}">{elenco_codici(s["codes"], gruppo_di)}</b>{html.escape(nome_breve(s))}</span>'
                                  f'<span class="fr-p">?</span><span class="bar" role="img" aria-label="Quanta parte è già stata spesa: non si sa"></span>'
                                  f'<small>{cosa(d, sp)}<br><span class="fr-m">{html.escape(p, quote=False)}</span></small></a></li>')
        return '<div class="fr-c">' + ((f'<ol class="fr">{"".join(li(*b) for b in barre)}</ol>' if barre
                 else f'<p class="fr-vuoto">Nessun report ha due cifre {"di Ilva" if di_ilva else "di fondi pubblici"} che si possono confrontare.</p>')
                + (f'<h5>Senza confronto possibile</h5><ul class="fr fr-nd">{"".join(nd(*a) for a in altri)}</ul>' if altri else "")) + "</div>"
    fermi = ('<section class="card chart soldi-tot ferme sz" id="fermi"><h2>Dove i soldi sono fermi</h2>'
             '<p class="chart-intro">Per ogni report, quanta parte dei soldi disponibili è già stata spesa (calcolo nostro), dalla percentuale più bassa. Solo dove le due cifre riguardano la stessa cosa e vengono dalla stessa fonte o dalla stessa data; gli altri report sono in fondo, con il punto di domanda e il motivo.</p>'
             f'<div class="tot"><div><h4>Fondi pubblici</h4>{ferme(False)}</div><div><h4>Secondo Ilva<small>{SOTTO[True]}</small></h4>{ferme(True)}</div></div></section>')

    # ---- le stranezze: tutte le righe [stranezza · tipo] delle schede, per tipo; il numero porta alla fonte nel report
    nomi_st = json.loads(re.search(r"^const STRANEZZA = (\{.*?\});", (ROOT / "sito" / "report.html").read_text(encoding="utf-8"), re.M | re.S).group(1))
    SPIEGA = {"più del previsto": "Pagati o impegnati più soldi di quelli previsti, o divisi più soldi di quelli che c'erano.",
              "usati per altro": "Soldi dati per una cosa e spesi per altre.",
              "più report": "Lo stesso fondo paga anche altri interventi.",
              "fonti non concordano": "Fonti diverse danno cifre diverse per la stessa cosa."}   # i quattro tipi, come in LEGGIMI.md
    strane = [(s, x) for s in schede for x in s["stranezze"]]
    n_strane = len({s["id"] for s, _ in strane})
    for b in fondi["breve"]:   # se "In breve" conta le stranezze, i numeri devono essere quelli di oggi
        m = re.search(r"stranezze sono (\d+), in (\d+) report", b)
        if m and (int(m.group(1)), int(m.group(2))) != (len(strane), n_strane):
            sys.exit(f"fondi.md, In breve: le stranezze sono {len(strane)} in {n_strane} report, non {m.group(1)} in {m.group(2)}")
    tipi_st = []
    for t in TIPI_STRANEZZA:
        xx = [(s, x) for s, x in strane if x["t"] == t]
        if xx:
            tipi_st.append(f'<div class="st-g"><h3>{nomi_st[t]}<small>{len(xx)}</small></h3><p class="note">{SPIEGA[t]}</p><ul class="strane">'
                           + "".join(f'<li>{chip(s["id"])}<p>{cita(x["h"], "r/" + s["id"] + ".html#" + s["id"] + "-f")}</p></li>' for s, x in xx) + "</ul></div>")
    stranezze = ('<section class="card chart sz" id="stranezze"><h2>Le stranezze</h2>'
                 f'<p class="chart-intro">Le cose che non tornano nei soldi, come le scrivono i report: {len(strane)} in {n_strane} report (calcolo nostro). '
                 'Il numero fra parentesi porta alla fonte, nel report.</p>' + "".join(tipi_st) + "</section>") if strane else ""

    # ---- dove sono finiti i soldi dei Riva: come erano divisi, dove sono andati, quanto resta (Patrimonio Destinato di Ilva)
    dom = [domanda(it, "fondi.md") for kind, val in blocks(fondi["altre"].get("Cosa non sappiamo", [])) if kind == "ol" for it in val]
    resta = ""
    pd = next((f for _, ff in fondi["gruppi"] for f in ff if f.get("resta")), None)
    if pd:
        cifre = "".join(p["src"] for p in pd["resta"])
        previsti, usati, ultimo = pd["pezzi"]["Per cosa"], pd["pezzi"]["Usati per altro"], pd["resta"][-1]
        tot, n_usati = pd["importo"] / 1e6, sum(p["v"] for p in usati)
        fonte_imp = "".join(re.findall(r"\[\d+\]", pd["voci"]["Importo"]["testo"].split(".")[0] + "."))
        resto = tot - n_usati - ultimo["v"]   # quello che resta dal conto: bonifiche e altre spese, al massimo (calcolo nostro)
        andati = usati + [{"v": resto, "lbl": num_it(resto, 0), "pre": "al massimo circa", "nome": "bonifiche e altre spese", "cert": "calcolo nostro", "fonti": fonte_imp + ultimo["src"], "t": None},
                          {"v": ultimo["v"], "lbl": ultimo["lbl"], "pre": "", "nome": "rimasti a " + ultimo["quando"], "cert": "certo", "fonti": ultimo["src"], "t": None, "resta": True}]
        mb = re.search(r"al massimo circa \**(\d+)", " ".join(fondi["breve"]))
        if mb and int(mb.group(1)) != round(resto):
            sys.exit(f"fondi.md, In breve: per le bonifiche restano al massimo circa {round(resto)} milioni (calcolo nostro), non {mb.group(1)}")
        bonifiche = sum(p["v"] for p in previsti if "decarbonizzazione" not in p["nome"])
        adi = {c: sum(p["v"] for p in usati if p["nome"].startswith("Acciaierie d'Italia") and p["cert"] == c) for c in CERTEZZA}
        tag = lambda c: f'<small class="cert">{c}</small>'
        grigi = [p for p in previsti if "Aree escluse" not in p["nome"]]

        def colore(p):   # giallo: usati per altro (righe se probabili); arancione: le Aree escluse di Ilva e quello che resta;
            if any(p is q for q in usati):     # tratteggiato: il resto "al massimo" (calcolo nostro); grigi: gli altri pezzi
                return "c-altro" + (" prob" if p["cert"] == "probabile" else "")
            if p["pre"].startswith("al massimo"):
                return "c-max"
            if "Aree escluse" in p["nome"] or p.get("resta"):
                return "c-ilva"
            return f"c-g{1 + next((i for i, q in enumerate(grigi) if q is p), 0)}"

        def barra(pezzi, titolo):   # una barra in pila, stessa scala per le due (il totale del fondo); la cifra dentro solo nei pezzi larghi
            somma = sum(p["v"] for p in pezzi)
            seg = "".join(f'<span class="pz {colore(p)}" style="flex-grow:{num_js(round(p["v"], 2))}" title="{html.escape(p["nome"])}: {p["pre"] + " " if p["pre"] else ""}{p["lbl"]} milioni €">'
                          f'{p["lbl"] if p["v"] / somma >= .1 else ""}</span>' for p in pezzi)
            leg = "".join(f'<li><i class="sw {colore(p)}"></i><b>{p["lbl"]}</b><span>{html.escape(p["nome"])}{", " + p["pre"] if p["pre"] else ""} {tag(p["cert"])}{cita(p["fonti"])}</span></li>' for p in pezzi)
            return (f'<div class="pzb" role="img" aria-label="{titolo}, in milioni di euro: ' + "; ".join(f'{p["nome"]} {p["lbl"]}' for p in pezzi) + f'">{seg}</div>'
                    f'<ul class="pz-leg">{leg}</ul>')

        prelievi = [p for p in usati if p["t"]]
        domande_pd = [d for d in dom if re.search(r"Patrimonio Destinato|dei Riva|Aree escluse", d["q"])]
        sem, rimborsi = pd.get("semestri"), ""
        if sem:
            riga = lambda x: (f'<tr><td>{x["quando"]}</td><td colspan="2" class="na">{x["manca"]}</td></tr>' if "manca" in x else
                              f'<tr><td>{x["quando"]}</td><td>{num_it(x["fab"], 2) if x["fab"] else "nessuno"}</td><td>{num_it(x["ilva"], 2)}{cita(x["fonti"])}</td></tr>')
            rimborsi = ('<details class="note" id="rimborsi"><summary>I soldi per la decontaminazione, semestre per semestre</summary>'
                        '<p class="note">Dalle relazioni dei commissari di Ilva al Parlamento sul conto del Patrimonio Destinato, in milioni di euro: i rimborsi ad Acciaierie d\'Italia per decontaminare la fabbrica e i pagamenti di Ilva per la decontaminazione, senza dire per quale area.</p>'
                        '<table class="resta-tab"><thead><tr><th>Semestre</th><th>Alla fabbrica</th><th>Pagati da Ilva</th></tr></thead><tbody>'
                        + "".join(map(riga, sem["righe"]))
                        + f'<tr class="tot"><td>In {sem["tot"][0]} semestri (calcolo nostro)</td><td>{sem["tot"][1]}</td><td>{sem["tot"][2]}</td></tr></tbody></table></details>')
        resta = ('<section class="card chart sz" id="resta"><h2>Dove sono finiti i soldi dei Riva</h2>'
                 f'<p class="chart-intro">Il Patrimonio Destinato è il fondo di Ilva per le bonifiche e il risanamento, nato soprattutto dall\'accordo con la famiglia Riva: <b>{num_it(tot, 0)} milioni €</b>{cita(fonte_imp)}. '
                 f'Qui come erano divisi, dove sono andati e quanto ne resta. Accanto a ogni cifra: {tag("certo")} è scritta in una relazione, {tag("probabile")} lo dicono più fonti ma nessuna relazione, {tag("calcolo nostro")} l\'abbiamo calcolata noi.</p>'
                 '<div class="pz-g">'
                 f'<div class="pz-p"><h3>1. Come erano divisi<small>milioni €, secondo Ilva, giugno 2022</small></h3>{barra(previsti, "Come erano divisi")}</div>'
                 f'<div class="pz-p"><h3>2. Dove sono andati<small>milioni €, fino a fine 2025</small></h3>{barra(andati, "Dove sono andati")}'
                 f'<p class="note">Usati per altro, in giallo: circa <b>{num_it(n_usati, 0)} milioni</b>. Ad Acciaierie d\'Italia, per far funzionare la fabbrica, ne sono andati {num_it(adi["certo"], 0)} certi, {num_it(adi["certo"] + adi["probabile"], 0)} contando i probabili. '
                 f'Il resto, al massimo circa {num_it(resto, 0)} milioni, comprende le bonifiche nella fabbrica e nelle aree di Ilva e le altre spese del fondo, contro i {num_it(bonifiche, 0)} milioni previsti per le bonifiche (calcolo nostro).</p></div></div>'
                 '<h3 class="pz-h">3. Quanto resta</h3>'
                 f'<p class="chart-intro">Quanti soldi c\'erano nel Patrimonio Destinato, secondo le relazioni di Ilva e dei suoi commissari al Parlamento{cita(cifre)}. '
                 f'Sulla linea l\'ultima cifra di ogni anno; tutte le cifre sono nella tabella. Dove manca il punto non abbiamo la cifra, e lì non c\'è la linea.</p>'
                 # su schermo grande il grafico a sinistra, note, tabella e domande a destra
                 f'<div class="resta-g">{grafico_resta(pd, [(p["t"], "−" + p["lbl"] + ("?" if p["cert"] == "probabile" else "")) for p in prelievi])}<div class="resta-dx">'
                 + (f'<p class="note"><i class="sw c-altro"></i> Le righe gialle sono i soldi andati ad Acciaierie d\'Italia: '
                    + ", ".join(f'{p["lbl"]} milioni a {p["nome"].split(", ", 1)[1]}' + (" (probabili)" if p["cert"] == "probabile" else "") for p in prelievi)
                    + cita("".join(p["fonti"] for p in prelievi)) + ".</p>" if prelievi else "")
                 + tabella_resta(pd, cita, "".join(f'<p class="note">{testo(n)}</p>' for n in pd["resta_note"]))
                 + "".join(f'<p class="aperta"><b>{cita(d["q"])}</b> <a href="#domande">Cosa non sappiamo →</a></p>' for d in domande_pd)
                 + f'<p class="note"><a href="#{pd["id"]}">Il Patrimonio Destinato, da dove viene e per cosa →</a></p></div></div>{rimborsi}</section>')

    # ---- in breve, in cima
    breve = ('<section class="card chart sz breve" id="in-breve"><h2>In breve</h2>'
             + "".join(f"<p>{testo(b)}</p>" for b in fondi["breve"]) + "</section>") if fondi["breve"] else ""

    def voce_report(r):   # "[scheda] cifra e per cosa" → il report e la sua quota; le altre righe come testo
        m = re.match(r"\[([a-z0-9-]+)\]\s*(.*)", r)
        return f'<li>{chip(m.group(1))}<span>{testo(m.group(2))}</span></li>' if m else f'<li class="altro"><span>{testo(r)}</span></li>'

    def per_report(gruppi):
        """Al contrario dei riquadri: una scheda per report con i fondi che lo pagano e la quota di ognuno (la prima cifra
        della riga "[scheda] cifra" di **Report**), dalla più grande; i report dal più pagato (somma nostra, senza i fondi
        revocati). Un fondo che paga più di 6 report (il Patrimonio Destinato di Ilva) ha una scheda sola."""
        quote, grandi = {}, []
        for _, ff in gruppi:
            for f in ff:
                rep = list(dict.fromkeys(f["report"]))
                tot, circa = 0, False
                for r in f["voci"]["Report"]["sub"]:
                    m = re.match(r"\[([a-z0-9-]+)\]\s*(?:(circa|meno di)\s+)?(?:(\d{1,3}(?:\.\d{3})*(?:,\d+)?)\s*€)?", r)
                    if not m:
                        continue
                    v = float(m.group(3).replace(".", "").replace(",", ".")) if m.group(3) else None
                    tot += v or 0; circa = circa or bool(m.group(2))
                    if len(rep) <= 6:
                        rev = "revocat" in f["nome"]
                        quote.setdefault(m.group(1), []).append({"f": f, "v": None if rev else v, "c": "revocato" if rev else (m.group(2) + " " if m.group(2) else "") + euro_breve(v) if v else "senza cifra"})
                if len(rep) > 6:
                    grandi.append((f, rep, ("circa " if circa else "") + euro_breve(tot)))
        riga = lambda f, c, na: f'<li><a href="#{f["id"]}">{html.escape(f["nome"].split(" (")[0])}</a><span class="{"na" if na else ""}">{c}</span></li>'
        somma = lambda r: sum(q["v"] or 0 for q in quote[r])
        schede_r = [f'<div class="pr">{chip(r)}<ul>{"".join(riga(q["f"], q["c"], q["v"] is None) for q in sorted(quote[r], key=lambda q: -(q["v"] or 0)))}</ul></div>'
                    for r in sorted(quote, key=lambda r: -somma(r))]
        schede_g = [f'<div class="pr largo"><a class="tutti" href="#{f["id"]}">{len(rep)} aree di Ilva</a><ul>{riga(f, c, False)}</ul>'
                    f'<div class="aree">{"".join(chip(r) for r in rep)}</div></div>' for f, rep, c in grandi]
        return f'<div class="prr">{"".join(schede_r + schede_g)}</div>'

    def voce(v, cls=""):   # testo della voce e sotto-voci; dei pezzi delle barre ("cifra · nome · certo: testo") la cifra in grassetto e il testo
        h = f"<p>{testo(v['testo'])}</p>" if frasi(v["testo"]) else ""
        pezzo = lambda m: f"**{(m.group(1) or '')}{m.group(2)} milioni €**: {m.group(6)}"
        sub = [PEZZO.sub(pezzo, x) for x in v["sub"] if frasi(x)]
        return h + (f'<ul{cls}>' + "".join(f"<li>{testo(x)}</li>" for x in sub) + "</ul>" if sub else "")

    def fondo(f):
        v = f["voci"]
        nome, _, sotto = f["nome"].partition(" (")
        sotto = sotto.rstrip(")")
        n = len(dict.fromkeys(f["report"]))
        dato = "".join(f'<div><span class="k">{k}</span>{voce(v[k])}</div>' for k in list(DATO) + [k for k in v if k not in DATO + ("Report", "Speso", "Da sapere")] if k in v)
        rep = v["Report"]
        finito = (f"<p>{testo(rep['testo'])}</p>" if rep["testo"] else "") + f'<ul class="dove">{"".join(voce_report(r) for r in rep["sub"])}</ul>'
        speso = voce(v["Speso"]) if "Speso" in v else "<p>Le fonti non lo dicono.</p>"
        sapere = f'<div class="sapere"><h4>Da sapere</h4>{voce(v["Da sapere"])}</div>' if "Da sapere" in v else ""
        som = [x for x in (html.escape(sotto), euro_breve(f["importo"]) if f["importo"] else "", f"{n} report" if n else "") if x]
        return (f'<details class="acc fondo" id="{f["id"]}"><summary><span>{html.escape(nome)}<small>{" · ".join(som)}</small></span></summary>'
                f'<div class="body"><ol class="percorso">'
                f'<li><span class="tappa">Dato</span><div class="dato">{dato}</div></li>'
                f'<li><span class="tappa">Finito in</span>{finito}</li>'
                f'<li><span class="tappa">Speso</span>{speso}</li></ol>{sapere}</div></details>')

    gruppi = "".join(f'<div class="gruppo"><h3>{html.escape(t)}<small>{len(ff)} {"fondo" if len(ff) == 1 else "fondi"}</small></h3><div class="accs">{"".join(map(fondo, ff))}</div></div>' for t, ff in fondi["gruppi"])
    altre = fondi["altre"]
    lista = lambda righe: "".join(voce_report(" ".join(x.strip() for x in it)) for kind, val in blocks(righe) if kind == "ul" for it in val)
    altro = lambda righe: "".join(f"<li><span>{testo(' '.join(x.strip() for x in it))}</span></li>" for kind, val in blocks(righe) if kind == "ul" for it in val)
    dopo = []
    if altre.get("Report senza un fondo conosciuto"):
        dopo.append(f'<details class="acc"><summary><span>Report senza un fondo conosciuto</span></summary><div class="body"><ul class="dove">{lista(altre["Report senza un fondo conosciuto"])}</ul></div></details>')
    if altre.get("Citati nelle schede ma non per la bonifica"):
        dopo.append(f'<details class="acc"><summary><span>Citati nelle schede ma non per la bonifica<small>Soldi che non pagano una bonifica del censimento</small></span></summary><div class="body"><ul class="dove">{altro(altre["Citati nelle schede ma non per la bonifica"])}</ul></div></details>')
    if dom:
        ol = lambda xs, k="": f'<ol class="unk {k}">' + "".join(f'<li><span><b>{cita(d["q"])}</b>{cita(d["h"])}</span></li>' for d in xs) + "</ol>"
        al, fo = [d for d in dom if d["t"] != "fonti"], [d for d in dom if d["t"] == "fonti"]
        dopo.append(f'<details class="acc" id="domande"><summary><span>Cosa non sappiamo<small>{len(dom)} domande sui soldi</small></span></summary><div class="body">'
                    + (f'<h4 class="unk-h">Domande aperte</h4>{ol(al, "altra")}' if al else "")
                    + (f'<div class="unk-fonti"><h4 class="unk-h">Le fonti non concordano</h4>{ol(fo)}</div>' if fo else "") + "</div></details>")
    apri_doc = lambda u: f' · <a href="{html.escape(u)}" target="_blank" rel="noopener">apri il documento</a>' if u else ""
    dopo.append(f'<details class="acc" id="fonti"><summary><span>Fonti<small>{len(fondi["fonti"])} documenti ufficiali</small></span></summary><div class="body"><ol class="fonti">'
                + "".join(f'<li id="fondi-f{x["n"]}"><span>[{x["n"]}]</span><span>{x["html"]}{apri_doc(x["url"])}</span></li>' for x in fondi["fonti"])
                + "</ol></div></details>")
    corpo = ('<header class="sd-head"><h1>I soldi della bonifica</h1>'
             '<p class="lead">Quanti soldi ci sono per la bonifica delle aree dell\'Ilva, quanti ne sono stati spesi, cosa non torna e da dove vengono. '
             'Solo cifre di documenti ufficiali; le somme e le percentuali fatte da noi sono scritte "calcolo nostro".</p>'
             f'<p class="note">{html.escape(fondi["controllo"])}</p></header>'
             + breve + totali + fermi + stranezze + resta
             + '<details class="acc" id="per-report"><summary><span>Report per report<small>I fondi che pagano ogni report, e con quanto</small></span></summary><div class="body">'
             '<p class="chart-intro">Per ogni report, i fondi che lo pagano e con quanto, dalla cifra più grande; "senza cifra" vuol dire che le fonti non dicono la quota. Tocca un fondo per il suo riquadro più sotto, un report per aprirlo.</p>'
             + per_report(fondi["gruppi"]) + '</div></details>'
             '<section class="sz-fondi" id="fondi"><h2>Fondo per fondo</h2>'
             '<p class="chart-intro">Ogni riquadro è un fondo: un atto (una delibera, un decreto, un accordo) che ha messo soldi per la bonifica. '
             'Dentro c\'è il percorso dei soldi: chi li ha dati, in quali report sono finiti e quanto è stato speso. '
             'Se lo stesso atto paga più interventi, le quote stanno nello stesso riquadro, così nessun fondo si conta due volte.</p>'
             f'{gruppi}<div class="gruppo"><h3>Altro</h3><div class="accs">{"".join(dopo)}</div></div></section>')
    tpl = (ROOT / "sito" / "report.html").read_text(encoding="utf-8")
    testa = tpl.split("<main")[0]   # stessa testata dei report (meta, caratteri, menu), con titolo e descrizione della pagina
    desc = "I soldi per la bonifica delle aree dell'Ilva: quanti ce ne sono, quanti ne sono stati spesi, cosa non torna e da dove vengono, solo con documenti ufficiali."
    testa = re.sub(r'<!-- questa pagina rimanda.*?-->\n<meta name="robots"[^>]*>\n', "", testa)
    testa = testa.replace("<title>Report · Bonifiche Ilva</title>", f'<title>I soldi della bonifica · Bonifiche Ilva</title>\n<link rel="canonical" href="{SITO}soldi.html">')
    testa = testa.replace('content="Report · Bonifiche Ilva"', 'content="I soldi della bonifica · Bonifiche Ilva"').replace(f"{SITO}report.html", f"{SITO}soldi.html")
    testa = re.sub(r'(<meta (?:name|property)="(?:og:)?description" content=")[^"]*', lambda m: m.group(1) + desc, testa)
    testa = testa.replace('<a href="soldi.html">', '<a href="soldi.html" aria-current="page">')
    piede = re.sub(r"\s*<p>Mappa:.*?</p>", "", tpl.split("</main>")[1].split("<script")[0])   # qui non c'è la mappa
    contatto = re.search(r'^const CONTATTO = "([^"]*)";', js, re.M).group(1)
    js = ("<script>\n/* Apre il fondo (#f-...) o la fonte (#fondi-f3, #fondi-f3-6) indicati dal link e li evidenzia per un attimo. */\n"
          f'document.querySelectorAll(".contatto").forEach(a => {{ const u = "{contatto}"; if (u) a.href = u; else a.hidden = true; }});\n'
          "function apri(){\n"
          "  const h = decodeURIComponent(location.hash.slice(1)), m = h.match(/^fondi-f(\\d+)(?:-(\\d+))?$/);\n"
          "  const els = m ? Array.from({length: +(m[2] || m[1]) - +m[1] + 1}, (_, k) => document.getElementById(\"fondi-f\" + (+m[1] + k))).filter(Boolean)\n"
          "    : [document.getElementById(h)].filter(x => x && x.tagName === \"DETAILS\");\n"
          "  if (!els.length) return;\n"
          "  els.forEach(el => { const d = el.closest(\"details\"); if (d) d.open = true; });\n"
          "  els[0].scrollIntoView({block: m ? \"center\" : \"start\"});\n"
          "  els.forEach(el => { el.classList.add(\"flash\"); setTimeout(() => el.classList.remove(\"flash\"), 1800); });\n"
          "}\n"
          "// su schermo grande \"Report per report\" e la tabella dei semestri sono aperti; sul telefono restano chiusi, così la pagina è corta\n"
          "if (matchMedia(\"(min-width:900px)\").matches) document.querySelectorAll(\"#per-report, #rimborsi\").forEach(d => d.open = true);\n"
          "addEventListener(\"hashchange\", apri); apri();\n"
          "// la stessa nota toccata due volte non cambia l'hash: si riapre a mano\n"
          "document.addEventListener(\"click\", e => { const a = e.target.closest('a[href^=\"#\"]'); if (a && a.getAttribute(\"href\") === location.hash) apri(); });\n"
          "// la \"i\" accanto ai totali: cosa vogliono dire le cifre\n"
          "document.addEventListener(\"click\", e => { const b = e.target.closest(\".info-i\"); if (!b) return;\n"
          "  const open = b.getAttribute(\"aria-expanded\") !== \"true\"; b.setAttribute(\"aria-expanded\", open); document.getElementById(b.getAttribute(\"aria-controls\")).hidden = !open; });\n"
          "// la linea di quanto resta: la cifra di un punto al tocco, al passaggio del mouse o con la tastiera\n"
          "document.querySelectorAll(\".resta\").forEach(fig => {\n"
          "  const tip = fig.querySelector(\".resta-tip\");\n"
          "  const mostra = g => { tip.textContent = g.dataset.t; tip.hidden = false; const f = fig.getBoundingClientRect(), r = g.querySelector(\".dot\").getBoundingClientRect();\n"
          "    tip.style.left = Math.min(Math.max(r.left + r.width / 2 - f.left - tip.offsetWidth / 2, 0), f.width - tip.offsetWidth) + \"px\"; tip.style.top = (r.top - f.top - tip.offsetHeight - 8) + \"px\";\n"
          "    fig.querySelectorAll(\".pt\").forEach(x => x.classList.toggle(\"on\", x === g)); };\n"
          "  const nascondi = () => { tip.hidden = true; fig.querySelectorAll(\".pt\").forEach(x => x.classList.remove(\"on\")); };\n"
          "  fig.querySelectorAll(\".pt\").forEach(g => { [\"pointerenter\", \"focus\", \"click\"].forEach(ev => g.addEventListener(ev, () => mostra(g))); g.addEventListener(\"blur\", nascondi); });\n"
          "  fig.addEventListener(\"pointerleave\", nascondi);\n"
          "});\n"
          "</script>\n")
    pg = ("<!doctype html>\n<!-- Scritta da sito/costruisci.py leggendo fondi.md e le schede: non modificare a mano. -->\n" + testa.replace("<!doctype html>\n", "", 1)
          + f'<main class="rp sd">\n  <div class="wrap">{corpo}</div>\n</main>' + piede + js)
    (ROOT / "sito" / "soldi.html").write_text(pg, encoding="utf-8")


# ---------- schede ----------
def leggi_scheda(path):
    txt = path.read_text(encoding="utf-8")
    lines = txt.splitlines()
    if "approvata" not in lines[1]:
        return None
    m = re.match(r"#\s+(.+?)\s+[–-]\s+(.+)", lines[0])
    codes = re.findall(r"[ABCD]\d+", m.group(1))
    title = m.group(2).strip()
    stato = lines[1].strip("* ")
    upd = re.search(r"aggiornata all?'?([^*·]+)", stato).group(1).strip()
    warn = None
    if "·" in lines[1]:
        warn = re.sub(r"^[*\s]*|[*\s]*$", "", lines[1].split("·", 1)[1]).replace("⚠", "").strip()
    # sezioni ##
    secs, cur = [], None
    for ln in lines[2:]:
        if ln.startswith("## "):
            cur = [ln[3:].strip(), []]; secs.append(cur)
        elif cur:
            cur[1].append(ln)
    out = {"id": path.stem, "codes": codes, "code": codes[0], "title": title, "updated": upd, "warnNote": warn,
           "sections": [], "nonsappiamo": [], "divieti": [], "soldi": [], "soldiFrase": "", "confronto": None, "stranezze": [], "fonti": [], "date": [], "verdict": "", "punto": [], "fatto": "", "chi": [], "posto": "", "perche": ""}
    for t, body in secs:
        tl = t.lower()
        if tl.startswith("cosa è stato fatto"):
            k = next((j for j, b in enumerate(body) if b.strip()), None)
            vm = k is not None and re.match(r"\*\*(.+?)\*\*\s*((?:\[\d+\])*)\s*(.*)", body[k].strip())
            if vm:
                out["verdict"] = vm.group(1).strip()
                body = body[:k] + ([vm.group(3)] if vm.group(3) else []) + body[k + 1:]
        if tl.startswith("fonti"):
            out["fonti"] = leggi_fonti(body)
            continue
        if tl.startswith("a che punto"):   # tre blocchi ### (finora, cosa manca, adesso) con le loro fonti
            cur = None
            for ln in body:
                if ln.startswith("### "):
                    cur = [ln[4:].strip(), []]; out["punto"].append(cur)
                elif cur:
                    cur[1].append(ln)
            out["punto"] = [{"title": t2, "html": section_html(b2)} for t2, b2 in out["punto"]]
            continue
        if tl.startswith("che posto è"):
            out["posto"] = section_html(body); continue
        if tl.startswith("perché è inquinata"):
            out["perche"] = section_html(body); continue
        if tl.startswith("divieti e avvisi"):   # solo atti ufficiali, ognuno con il suo stato (vedi LEGGIMI.md)
            for kind, val in blocks(body):
                if kind == "ul":
                    out["divieti"] += [domanda(it, path.name, "Divieti e avvisi") for it in val]
            continue
        if tl.startswith("cosa non sappiamo"):
            for kind, val in blocks(body):
                if kind == "ol":
                    for it in val:
                        out["nonsappiamo"].append(domanda(it, path.name))
                if kind == "h":
                    break
            continue
        if ESCLUSE.match(t):
            continue
        if tl.startswith("soldi"):   # la frase in grassetto e il blocco con le etichette vanno nel riquadro "Soldi"; il resto è il racconto
            k = next((j for j, b in enumerate(body) if b.strip()), None)
            if k is not None and body[k].startswith("**"):
                fm = re.match(r"\*\*(.+?)\*\*\s*((?:\[\d+\])+)\s*$", body[k].strip())
                if not fm:
                    sys.exit(f"{path.name}: in \"Soldi\" la frase in grassetto deve finire con la sua fonte: {body[k][:60]}")
                if FILTRO.search(fm.group(1)):
                    sys.exit(f"{path.name}: in \"Soldi\" la frase va sul sito e non può dire \"non verificato\" o citare giornali")
                out["soldiFrase"] = fm.group(1).strip() + fm.group(2)
                body = body[:k] + body[k + 1:]
            blocco = [ln for ln in body if re.match(r"- \[[^\]]+\](?!\()", ln)]   # non i link [testo](url)
            conf = [ln for ln in blocco if ln.startswith("- [confronto")]
            strane = [ln for ln in blocco if ln.startswith("- [stranezza")]
            out["stranezze"] = [stranezza(ln[2:].strip(), path.name) for ln in strane]
            out["soldi"] = [riga_soldi(ln[2:].strip(), path.name) for ln in blocco if ln not in conf and ln not in strane]
            out["confronto"] = confronto(conf, out["soldi"], path.name)
            body = [ln for ln in body if ln not in blocco]
        if tl.startswith("date principali"):
            for kind, val in blocks(body):
                if kind == "table":
                    for r in val[1:]:
                        if len(r) >= 2 and not FILTRO.search(" ".join(r)):
                            dn = data_num(r[0])
                            if dn:
                                quando = re.sub(r"\*\*", "", r[0])
                                out["date"].append({"t": dn, "quando": quando, "cosa": inline(re.sub(r"\*\*", "", r[1])),
                                                    "fonte": r[2] if len(r) > 2 else "", "plan": dn > OGGI.year + (OGGI.month - 1) / 12 + OGGI.day / 372})
        if tl.startswith("chi se ne occupa"):
            for kind, val in blocks(body):
                if kind in ("ul", "ol"):
                    for it in val:   # i nomi in grassetto nella prima riga di ogni punto, prima delle note [n]
                        for b in re.findall(r"\*\*(.+?)\*\*", it[0].split("[")[0]):
                            nome = b.strip(" :")
                            if nome[:1].isupper() and nome.lower() != "attenzione" and not FILTRO.search(nome) and nome not in out["chi"]:
                                out["chi"].append(nome)
        h = section_html(body)
        if not h and tl.startswith("soldi") and not out["soldi"]:
            h = "<p>Nessuna cifra verificata: i costi non si trovano nei documenti ufficiali.</p>"
        if tl.startswith("cosa è stato fatto"):
            out["fatto"] = h; continue
        if h:
            out["sections"].append({"title": t, "html": h})
    if len(out["punto"]) != 3:   # ogni scheda racconta a che punto è in tre blocchi (vedi LEGGIMI.md)
        sys.exit(f"{path.name}: manca \"## A che punto è\" con i blocchi ### Finora, ### Cosa manca, ### Adesso")
    numeri = {f["n"] for f in out["fonti"]}
    for src in [r["src"] for r in out["soldi"] + out["stranezze"]] + re.findall(r"\[\d+\]", out["soldiFrase"]) + [(out["confronto"] or {}).get("src", "")]:   # cifre, frase e stranezze rimandano a una fonte della scheda
        for n in map(int, re.findall(r"\d+", src)):
            if n not in numeri:
                sys.exit(f"{path.name}: in \"Soldi\" la fonte [{n}] non è nell'elenco delle fonti")
    if out["soldi"] and not out["soldiFrase"]:
        print(f"Avviso: {path.name} ha le cifre dei soldi ma non la frase in grassetto all'inizio di \"Soldi\"")
    out["coord"] = coordinate(txt)
    per_cod = coordinate_per_codice(txt)
    out["coords"] = {k: v for k, v in per_cod.items() if k != "*"} or None
    out["immagine"] = immagine(lines)
    return out


# ---------- una pagina per report, sitemap e robots ----------
def scrivi_pagine(schede):
    """sito/r/<id>.html per ogni scheda: lo stesso codice di report.html, con <title>, description e og: dell'area
    scritti nella pagina (per le anteprime su WhatsApp e per Google) e i percorsi relativi spostati di una cartella."""
    sito = ROOT / "sito"
    tpl = (sito / "report.html").read_text(encoding="utf-8")
    js = (sito / "comune.js").read_text(encoding="utf-8")
    short = json.loads(re.search(r"^const SHORT = (\{.*\});$", js, re.M).group(1))   # gli stessi nomi brevi del sito
    tpl = re.sub(r'<!-- questa pagina rimanda.*?-->\n<meta name="robots"[^>]*>\n', "", tpl)
    tpl = re.sub(r'((?:href|src)=")(?!https?:|#|/|data:|mailto:|\$)', r"\1../", tpl)   # non i link scritti dal codice (${…})
    a = lambda v: html.escape(v, quote=False).replace('"', "&quot;")   # valori tra virgolette doppie
    cartella = sito / "r"
    cartella.mkdir(exist_ok=True)
    for vecchia in cartella.glob("*.html"):   # report tolti o rinominati
        if vecchia.stem not in {s["id"] for s in schede}:
            vecchia.unlink()
    for s in schede:
        nome = short.get(s["id"]) or re.split(r" \(|:", s["title"])[0]
        titolo = a(f'{s["code"]} {nome} · Bonifiche Ilva')
        desc = a(s["verdict"] or s["title"])
        url = f'{SITO}r/{s["id"]}.html'
        cambi = [("<title>Report · Bonifiche Ilva</title>", f'<title>{titolo}</title>\n<link rel="canonical" href="{url}">'),
                 ('<meta property="og:type" content="website">', '<meta property="og:type" content="article">'),
                 ('<meta property="og:title" content="Report · Bonifiche Ilva">', f'<meta property="og:title" content="{titolo}">'),
                 (f'<meta property="og:url" content="{SITO}report.html">', f'<meta property="og:url" content="{url}">'),
                 ('<div class="wrap" id="rp">', f'<div class="wrap" id="rp" data-scheda="{a(s["id"])}">')]
        pg = tpl.replace("<!doctype html>\n", "<!doctype html>\n<!-- Scritta da sito/costruisci.py a partire da report.html: non modificare a mano. -->\n", 1)
        for vecchio, nuovo in cambi:
            if pg.count(vecchio) != 1:
                sys.exit(f"report.html è cambiata: non trovo {vecchio!r}")
            pg = pg.replace(vecchio, nuovo)
        pg = re.sub(r'(<meta (?:name|property)="(?:og:)?description" content=")[^"]*', lambda m: m.group(1) + desc, pg)
        (cartella / f'{s["id"]}.html').write_text(pg, encoding="utf-8")

    def iso(upd):   # "8 ottobre 2026" → 2026-10-08
        g, m, y = upd.split()
        return f"{y}-{MESI[m.lower()]:02d}-{int(g):02d}"
    urls = [(SITO, OGGI.isoformat()), (SITO + "mappa.html", OGGI.isoformat()), (SITO + "soldi.html", OGGI.isoformat())] + [(f'{SITO}r/{s["id"]}.html', iso(s["updated"])) for s in schede]
    (sito / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                      + "".join(f"  <url><loc>{u}</loc><lastmod>{d}</lastmod></url>\n" for u, d in urls) + "</urlset>\n", encoding="utf-8")
    (sito / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITO}sitemap.xml\n", encoding="utf-8")


def main():
    elenco, gruppi_a, gruppi_b = leggi_elenco()
    # solo interventi/*.md: le schede in interventi/fuori-perimetro/ non vanno sul sito
    schede = [s for s in (leggi_scheda(p) for p in sorted((ROOT / "interventi").glob("*.md"))) if s]
    # le richieste di accesso agli atti: in ogni scheda quelle sui suoi codici, dalla più vecchia; in home il totale
    richieste = leggi_richieste(elenco)
    for s in schede:
        rr = [r for r in richieste if set(r["aree"]) & set(s["codes"])]
        s["richieste"] = [{k: r[k] for k in ("n", "a", "cosa", "inviata", "entro", "e")} for r in sorted(rr, key=lambda r: (r["t"], int(r["n"])))]
    enti = {re.sub(r"^(al|alla|ad|allo|all')\s*", "", r["a"]) for r in richieste}
    immagini = leggi_immagini()
    contesto = leggi_contesto()
    usate = contesto["storia"]["img"] + contesto["inquina"]["img"] + contesto["fabbrica"]["img"] + [s["immagine"] for s in schede if s["immagine"]]
    for f in usate:   # ogni foto usata deve essere nel registro (autore e licenza) e in sito/img/
        if f not in immagini or not (ROOT / "sito" / "img" / f).exists():
            sys.exit(f"Immagine {f}: manca in immagini.md o in sito/img/")
    # da dove vengono i soldi: in ogni scheda i fondi che la pagano (per i link del riquadro "Soldi"), poi la pagina soldi.html
    fondi = leggi_fondi(schede)
    for s in schede:
        s["fondi"] = [{"id": f["id"], "nome": f["nome"] if "revocat" in f["nome"] else f["nome"].split(" (")[0]} for _, ff in fondi["gruppi"] for f in ff if s["id"] in f["report"]]
    short = json.loads(re.search(r"^const SHORT = (\{.*\});$", (ROOT / "sito" / "comune.js").read_text(encoding="utf-8"), re.M).group(1))
    gruppo_di = {c: g for g, gg in (("A", gruppi_a), ("B", gruppi_b)) for _, cc in gg for c in cc}
    scrivi_soldi(fondi, schede, gruppo_di, short)
    data = {"elenco": elenco, "gruppiA": gruppi_a, "gruppiB": gruppi_b, "schede": schede, "contesto": contesto,
            "immagini": immagini, "richieste": {"n": len({r["n"] for r in richieste}), "enti": len(enti)},
            "generato": OGGI.isoformat()}
    js = ("/* Generato da sito/costruisci.py leggendo elenco.md e le schede approvate: non modificare a mano. */\n"
          "const DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n")
    (ROOT / "sito" / "dati.js").write_text(js, encoding="utf-8")
    scrivi_pagine(schede)
    print(f"{len(schede)} schede approvate, {len(elenco)} righe dell'elenco, "
          f"{sum(1 for x in schede if x['coord'])} con coordinate, {sum(len(x['date']) for x in schede)} date, "
          f"{len(schede)} pagine in sito/r/.")


if __name__ == "__main__":
    main()
