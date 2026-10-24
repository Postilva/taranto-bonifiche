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
    urls = [(SITO, OGGI.isoformat()), (SITO + "mappa.html", OGGI.isoformat())] + [(f'{SITO}r/{s["id"]}.html', iso(s["updated"])) for s in schede]
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
