"""Legge elenco.md e le schede approvate in interventi/ e scrive i dati in sito/dati.js (usato da tutte le pagine).

Uso:  py sito/costruisci.py [AAAA-MM-GG]   (data dei dati; senza argomento, oggi)

Regole applicate al testo (vedi LEGGIMI.md e le richieste sul sito):
- si usano solo le schede con "Stato scheda: approvata";
- si tolgono paragrafi, punti e righe che contengono "non verificato" o che citano giornali/stampa;
- di "Cosa non sappiamo" si tiene solo la frase in grassetto iniziale di ogni punto (la domanda aperta, senza dati);
- le bozze FOIA non vanno sul sito.
Il testo non viene riscritto: viene solo convertito da Markdown a HTML.
"""
import html, json, math, re, sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OGGI = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today()

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
    """Una voce di lista, con eventuali sotto-voci indentate."""
    head, rest = item[0], item[1:]
    if FILTRO.search(head):
        return ""
    sub = []
    for r in rest:
        m = re.match(r"^\s+(-|\d+\.)\s+(.*)", r)
        if m:
            sub.append(m.group(2))
        elif sub:
            sub[-1] += " " + r.strip()
        else:
            head += " " + r.strip()
    sub = [s for s in sub if not FILTRO.search(s)]
    h = inline(head)
    if sub:
        h += "<ul>" + "".join(f"<li>{inline(s)}</li>" for s in sub) + "</ul>"
    return f"<li>{h}</li>"


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
    for ln in text.splitlines():
        if "**Coordinate**" not in ln or FILTRO.search(ln.split("(conversione")[0]):
            continue
        m = re.search(r"(\d{6}[,.]\d+)\s*m\s*E\s*[–-]\s*(\d{7}[,.]\d+)\s*m\s*N", ln) or re.search(r"X\s*=\s*(\d{6}[,.]\d+)\s*m\s*[–-]\s*Y\s*=\s*(\d{7}[,.]\d+)\s*m", ln)
        n = re.search(r"\[(\d+)\]", ln)
        if m and n:
            E, N = num(m.group(1)), num(m.group(2))
            lat, lon = utm33_to_ll(E, N)
            return {"ll": [lat, lon], "e": m.group(1), "n": m.group(2), "fonte": int(n.group(1)),
                    "sistema": "RDN2008 / TM33 (EPSG 6708)" if "RDN2008" in ln else "UTM fuso 33 Nord, datum WGS84"}
    return None


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
        m = re.match(r"^\|\s*([AB]\d+)\s*\|(.+)\|$", ln)
        if not m:
            continue
        c = [x.strip() for x in m.group(2).split("|")]
        name, note, pag, sch = c[0], c[1], c[2], c[3] if len(c) > 3 else ""
        link = re.search(r"interventi/([\w-]+)\.md", sch)
        warn = "⚠" in note
        clean = lambda s: re.sub(r"\s+", " ", re.sub(r"\*\*|\*|⚠|✔", "", s)).strip()
        righe[m.group(1)] = [m.group(1), clean(name), clean(note), pag, link.group(1) if link else None, warn]
    # sottogruppi del gruppo B
    conclusi, b = [], txt.split("## B.")[1].split("## C.")[0]
    parte = b.split("### Interventi in corso")[0]
    conclusi = re.findall(r"^\|\s*(B\d+)\s*\|", parte, re.M)
    return righe, conclusi


# ---------- schede ----------
def leggi_scheda(path):
    txt = path.read_text(encoding="utf-8")
    lines = txt.splitlines()
    if "approvata" not in lines[1]:
        return None
    m = re.match(r"#\s+(.+?)\s+[–-]\s+(.+)", lines[0])
    codes = re.findall(r"[AB]\d+", m.group(1))
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
           "sections": [], "nonsappiamo": [], "fonti": [], "date": [], "verdict": "", "breve": "", "fatto": "", "chi": []}
    for t, body in secs:
        tl = t.lower()
        if tl.startswith("cosa è stato fatto"):
            k = next((j for j, b in enumerate(body) if b.strip()), None)
            vm = k is not None and re.match(r"\*\*(.+?)\*\*\s*((?:\[\d+\])*)\s*(.*)", body[k].strip())
            if vm:
                out["verdict"] = vm.group(1).strip()
                body = body[:k] + ([vm.group(3)] if vm.group(3) else []) + body[k + 1:]
        if tl.startswith("fonti"):
            joined, fon = "\n".join(body), []
            for fm in re.finditer(r"^\[(\d+)\]\s+(.+?)(?=^\[\d+\]\s|\Z)", joined, re.M | re.S):
                raw = " ".join(fm.group(2).split())
                url = re.search(r"https?://[^\s)]+", raw)
                testo = re.split(r"\s+—\s+copi[ae]", raw)[0]
                testo = re.sub(r",?\s*https?://\S+", "", testo).strip(" ,")
                fon.append({"n": int(fm.group(1)), "html": inline(testo), "url": url.group(0).rstrip(".,;") if url else None})
            out["fonti"] = fon
            continue
        if tl.startswith("cosa non sappiamo"):
            for kind, val in blocks(body):
                if kind == "ol":
                    for it in val:
                        b = re.match(r"\*\*(.+?)\*\*", it[0])
                        if b and not FILTRO.search(b.group(1)):
                            out["nonsappiamo"].append(inline(b.group(1).strip()))
                if kind == "h":
                    break
            continue
        if ESCLUSE.match(t):
            continue
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
        if not h and tl.startswith("soldi"):
            h = "<p>Nessuna cifra verificata: i costi non si trovano nei documenti ufficiali.</p>"
        if tl.startswith("in breve"):
            out["breve"] = h; continue
        if tl.startswith("cosa è stato fatto"):
            out["fatto"] = h; continue
        if h:
            out["sections"].append({"title": t, "html": h})
    if not out["verdict"]:   # "Cosa è stato fatto" non inizia con una frase in grassetto: si usa quella di "In breve"
        b = re.search(r"<strong>(.+?)</strong>", out["breve"])
        if b:
            out["verdict"] = re.sub(r"<[^>]+>", "", b.group(1)).strip(" :.") + "."
    out["coord"] = coordinate(txt)
    return out


def main():
    elenco, conclusi = leggi_elenco()
    schede = [s for s in (leggi_scheda(p) for p in sorted((ROOT / "interventi").glob("*.md"))) if s]
    data = {"elenco": elenco, "conclusiB": conclusi, "schede": schede, "generato": OGGI.isoformat()}
    js = ("/* Generato da sito/costruisci.py leggendo elenco.md e le schede approvate: non modificare a mano. */\n"
          "const DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n")
    (ROOT / "sito" / "dati.js").write_text(js, encoding="utf-8")
    print(f"{len(schede)} schede approvate, {len(elenco)} righe dell'elenco, "
          f"{sum(1 for x in schede if x['coord'])} con coordinate, {sum(len(x['date']) for x in schede)} date.")


if __name__ == "__main__":
    main()
