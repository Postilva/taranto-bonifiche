/* Codice comune a home, mappa e report. Richiede dati.js (generato da costruisci.py) caricato prima. */

/* ---------- elenco.md: gruppo A (aree di Ilva) e gruppo B (ricadute fuori dalla fabbrica) ---------- */
// il gruppo di un intervento è la sezione di elenco.md in cui sta, non la lettera del codice (C1, C2, D16, D17 sono aree di Ilva)
const subs = gs => gs.map(g => [g[0], g[1].map(c => DATA.elenco[c])]);
const ELENCO = {
  A: {
    title: "Aree di Ilva",
    who: "Terreni, discariche e falde dell'Ilva: le vecchie aree affidate a Ilva in amministrazione straordinaria e lo stabilimento in funzione, gestito da Acciaierie d'Italia.",
    subs: subs(DATA.gruppiA)
  },
  B: {
    title: "Ricadute fuori dalla fabbrica",
    who: "Quartiere Tamburi, Statte, Mar Piccolo: aree per cui una fonte ufficiale dice che l'inquinamento viene (anche) dall'Ilva.",
    subs: subs(DATA.gruppiB)
  }
};
const GRUPPO = {};   // codice → "A" | "B"
for (const g of ["A","B"]) {
  ELENCO[g].items = ELENCO[g].subs.flatMap(s => s[1]);
  ELENCO[g].items.forEach(r => GRUPPO[r[0]] = g);
  ELENCO[g].count = ELENCO[g].items.length + " interventi";
}
// ricadute per cui la fonte che lega l'inquinamento all'Ilva non è ancora stata trovata
const DA_VERIFICARE = new Set(ELENCO.B.subs.filter(s => s[0].startsWith("Da verificare")).flatMap(s => s[1].map(r => r[0])));

// nome breve per lista, grafici e cronologia (se manca si usa il titolo fino alla parentesi)
const SHORT = {"tamburi-risanamento-suoli":"Tamburi, risanamento dei suoli (SP1–SP4)","area-pneumatici-ua26":"Area pneumatici (UA26)","area-traversine-ua27":"Area traversine (UA27)","area-vasta-statte":"Area vasta di Statte","tamburi-falda":"Tamburi, falda","discarica-nord-ovest":"Discarica Nord-Ovest","mar-piccolo-gara-2018":"Mar Piccolo, gara 2018","pip-statte":"PIP Statte","stoccaggio-fanghi":"Stoccaggio fanghi","land-l-amastuola":"Land L (Amastuola)","gravina-leucaspide":"Gravina di Leucaspide","cimitero-san-brunone":"Cimitero San Brunone","mar-piccolo-studi":"Mar Piccolo, studi","mar-piccolo-area-170":"Mar Piccolo, Area 170 ha","scuole-tamburi-aree-verdi":"Aree verdi delle scuole Tamburi","atleti-azzurri-tamburi":"Impianto Atleti Azzurri","acciaierie-italia-suoli":"Acciaieria, suoli","acciaierie-italia-falda":"Acciaieria, falda"};
// note sulla posizione che la scheda stessa segnala
const COORD_NOTE = {"pozzo-25":"Attenzione: le fonti danno coordinate diverse tra loro (il piano del 2021 indica un punto circa 2,8 km più a nord)."};
const SCHEDE = DATA.schede.map(s => ({...s, short: SHORT[s.id] || s.title.split(/ \(|:/)[0]}));

/* ---------- contatto ---------- */
// link del modulo Google per scriverci; vuoto = i link "Scrivici" restano nascosti
const CONTATTO = "https://forms.gle/fLbgTRdhU5ES3kXw5";
document.querySelectorAll(".contatto").forEach(a => { if (CONTATTO) a.href = CONTATTO; else a.hidden = true; });

/* ---------- utilità ---------- */
const $ = s => document.querySelector(s);
const esc = s => String(s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
// ordine: gruppo A prima del gruppo B, poi lettera del codice e numero
const codeCmp = (a,b) => (GRUPPO[a]||"Z") !== (GRUPPO[b]||"Z") ? ((GRUPPO[a]||"Z") < (GRUPPO[b]||"Z") ? -1 : 1) : a[0]===b[0] ? (+a.slice(1))-(+b.slice(1)) : (a<b?-1:1);
SCHEDE.sort((a,b)=> codeCmp(a.code, b.code));
const verified = Object.fromEntries(SCHEDE.flatMap(s => s.codes.map(c => [c, s])));
document.querySelectorAll(".n-ok").forEach(el => el.textContent = Object.keys(verified).filter(c => GRUPPO[c]).length);
document.querySelectorAll(".n-sch").forEach(el => el.textContent = SCHEDE.length);
// note di fila unite in un richiamo solo: [3][4][5][6][9][13] → [3–6, 9, 13]; "3–6" porta a #<sid>-f3-6 (si evidenziano tutte e quattro)
function cite(html, sid){
  return html.replace(/(?:\[\d+\])+/g, m => {
    const ns = [...new Set(m.match(/\d+/g).map(Number))].sort((a,b) => a-b), pezzi = [];
    for (let i = 0; i < ns.length;) {
      let j = i; while (j + 1 < ns.length && ns[j+1] === ns[j] + 1) j++;
      if (j - i >= 2) { pezzi.push(`<a href="#${sid}-f${ns[i]}-${ns[j]}" aria-label="fonti da ${ns[i]} a ${ns[j]}">${ns[i]}–${ns[j]}</a>`); i = j + 1; }
      else { pezzi.push(`<a href="#${sid}-f${ns[i]}" aria-label="fonte ${ns[i]}">${ns[i]}</a>`); i++; }
    }
    return `<sup class="c">[${pezzi.join(", ")}]</sup>`;
  });
}
// le voci della lista fonti indicate da un richiamo: "<sid>-f3" → [f3], "<sid>-f3-6" → [f3, f4, f5, f6]
function fontiLi(root, id){
  const m = id.match(/^(.*-f)(\d+)(?:-(\d+))?$/); if (!m) return [];
  const lis = [];
  for (let n = +m[2]; n <= +(m[3] || m[2]); n++) { const li = root.querySelector("#" + CSS.escape(m[1] + n)); if (li) lis.push(li); }
  return lis;
}
/* ---------- interventi: dati comuni a lista, mappa e report ---------- */
// sulla mappa: tutti gli interventi dei gruppi A e B
const ALL = [...ELENCO.A.items, ...ELENCO.B.items];   // [codice, nome, nota, pagina, id scheda, avviso]
const ROW = Object.fromEntries(ALL.map(i => [i[0], i]));
const TOTAL = ALL.length;   // interventi sulla mappa
const CENSITI = TOTAL;      // tutti gli interventi dell'elenco
document.querySelectorAll(".n-cens").forEach(el => el.textContent = CENSITI);
document.querySelectorAll(".n-a").forEach(el => el.textContent = ELENCO.A.count);
document.querySelectorAll(".n-b").forEach(el => el.textContent = ELENCO.B.count);
document.querySelectorAll(".n-dv").forEach(el => el.textContent = DA_VERIFICARE.size);
// etichetta del gruppo: "Area di Ilva" / "Ricaduta dell'Ilva" (+ chi se ne occupa, dalla lettera del codice)
const GRP_CHI = {A:"Ilva in amministrazione straordinaria", B:"Commissario per la bonifica", C:"Acciaierie d'Italia", D:"anagrafe della Regione"};
const grpLabel = (code, short) => {
  const t = GRUPPO[code] === "A" ? "Area di Ilva" : DA_VERIFICARE.has(code) ? "Ricaduta da verificare" : "Ricaduta dell'Ilva";
  return short ? t : `${t} · ${GRP_CHI[code[0]]}`;
};

/* Posizioni "da documento ufficiale": solo se la scheda riporta le coordinate di un documento (riga **Coordinate**,
   lette da costruisci.py e convertite in gradi). Tutte le altre sono INDICATIVE: messe a mano nella zona
   nominata dall'elenco o dalla scheda. */
// aree di Ilva senza coordinate ufficiali: punto ricavato dalla mappa delle 18 aree (Ilva per l'Osservatorio, luglio 2022, pag. 1),
// riportata sulla carta con le coordinate ufficiali di 7 aree (A8–A11, A13, A16, A17) e di due discariche riconoscibili sulla foto satellitare
const MAPPA22 = "punto ricavato da noi dalla mappa delle aree di Ilva del luglio 2022, riportata sulla carta con le coordinate ufficiali di 7 aree: errore stimato 100–200 m";
const ZONES = {
  acciaieria:{ll:[40.513,17.196], r:.006, label:"Stabilimento siderurgico (circa 1.050 ettari dentro il SIN): il report riguarda tutta l'area, il punto è solo indicativo"},
  plant:   {ll:[40.507,17.190], r:.019, label:"Zona generica: stabilimento ex Ilva (l'elenco non indica dove si trova l'area)"},
  statte:  {ll:[40.553,17.205], r:.004, label:"Statte (luogo citato nel nome o nelle fonti)"},
  gravina: {ll:[40.5454,17.1951], r:0, label:`Gravina di Leucaspide, tra lo stabilimento e Statte (${MAPPA22}; l'area è una striscia lunga circa 3 km lungo la gravina, il punto ne indica la parte centrale)`},
  nordovest:{ll:[40.5502,17.1954], r:0, label:`Confine nord della fabbrica, a Statte, accanto alla Gravina di Leucaspide (${MAPPA22})`},
  duemari: {ll:[40.5294,17.2092], r:0, label:`Ex cava Due Mari, a est della cava Mater Gratiae (${MAPPA22})`},
  fanghi:  {ll:[40.5264,17.2050], r:0, label:`Comune di Statte, vicino alla Strada provinciale 48 Taranto–Statte, a sud della cava Mater Gratiae (${MAPPA22})`},
  limitrofe:{ll:[40.5265,17.2011], r:0, label:`Accanto allo stoccaggio fanghi, a sud della cava Mater Gratiae (${MAPPA22})`},
  nuovevasche:{ll:[40.5290,17.2030], r:0, label:"Zona della cava Mater Gratiae, a sud-est della cava (punto messo da noi: la discarica indicata nella mappa delle aree di Ilva del luglio 2022 si riconosce sulla foto satellitare; errore stimato sotto i 100 m)"},
  d1:      {ll:[40.5044,17.1963], r:0, label:`Appena fuori dalla fabbrica, sul lato sud-ovest, accanto a Land D2 (${MAPPA22})`},
  tamburi: {ll:[40.4905,17.2285], r:.003, label:"Quartiere Tamburi"},
  // punti presi da OpenStreetMap (non da documenti ufficiali): restano "posizione indicativa"
  collinette:{ll:[40.4988,17.2280], r:0, label:"A nord del quartiere Tamburi, accanto alla scuola Deledda (secondo le fonti la Collinetta 3 è attaccata alla scuola); punto messo da noi con OpenStreetMap"},
  deledda: {ll:[40.4971,17.2292], r:0, label:"Scuola Deledda, quartiere Tamburi (punto preso da OpenStreetMap)"},
  cimitero:{ll:[40.4918,17.2202], r:0, label:"Cimitero San Brunone, quartiere Tamburi (punto preso da OpenStreetMap)"},
  amastuola:{ll:[40.5987,17.1703], r:0, label:"Cava accanto alla Masseria Amastuola, a circa 1 km dalla Strada provinciale 42 (punto preso da OpenStreetMap, dove la cava ha come gestore \"ILVA in A.S.\"; nessun documento ufficiale trovato ne indica la posizione)"},
  ospnord: {ll:[40.5396,17.2771], r:0, label:"Ospedale San Giuseppe Moscati, a Statte, chiamato in zona \"Ospedale Nord\" (punto preso da OpenStreetMap sull'ospedale: l'area di Ilva è lì vicino, ma non sappiamo esattamente dove)"},
  mp1:     {ll:[40.483,17.262], r:.009, label:"Mar Piccolo, 1° seno"},
  cementir:{ll:[40.4910,17.2065], r:0, label:"Dentro la cava del cementificio, tra la raffineria ENI e lo stabilimento (punto messo da noi: la discarica indicata nella mappa delle aree di Ilva del luglio 2022 si riconosce sulla foto satellitare; errore stimato sotto i 100 m)"},
};
const PLACE = {A1:"gravina",A2:"nordovest",A3:"duemari",A4:"cementir",A5:"fanghi",A6:"limitrofe",A7:"nuovevasche",A12:"d1",A14:"amastuola",A15:"collinette",A18:"ospnord",B2:"deledda",B6:"mp1",B8:"cimitero",B9:"tamburi",B10:"statte",B12:"mp1",B13:"mp1",C1:"acciaieria",C2:"acciaieria",D1:"tamburi",D2:"tamburi",D3:"tamburi",D4:"tamburi",D5:"tamburi",D6:"tamburi",D8:"statte",D16:"statte",D17:"statte"};
function pointsFor(){
  const all = ALL;
  const byZone = {};
  const pts = [];
  all.forEach(i => {
    const s = verified[i[0]], k = s && ((s.coords && s.coords[i[0]]) || s.coord);   // coordinate del codice, se la scheda ne ha più di una
    if (k) {   // coordinate da documento ufficiale
      const f = s.fonti.find(x => x.n === k.fonte);
      pts.push({code:i[0], name:i[1], note:i[2], ll:k.ll, official:true, zone:"Coordinate da documento ufficiale", ok:true,
        src:{sid:s.id, n:k.fonte, url:f && f.url, note:COORD_NOTE[s.id] || "", text:`${k.e} m E – ${k.n} m N (${k.sistema}); in gradi, con la nostra conversione: ${k.ll[0].toFixed(4).replace(".",",")}° N – ${k.ll[1].toFixed(4).replace(".",",")}° E.`}});
      return;
    }
    const z = PLACE[i[0]] || "plant"; (byZone[z] ||= []).push(i);
  });
  Object.entries(byZone).forEach(([z,items]) => {
    const Z = ZONES[z];
    items.forEach((i,k) => {
      const a = k * 2.399963, rr = Z.r * Math.sqrt((k+.5)/items.length);   // spirale regolare, non casuale
      const ll = items.length===1 && !Z.r ? Z.ll : [Z.ll[0] + rr*Math.sin(a)*.8, Z.ll[1] + rr*Math.cos(a)];
      pts.push({code:i[0], name:i[1], note:i[2], ll, zone:Z.label, official:!!Z.official, src:Z.src, ok:!!verified[i[0]]});
    });
  });
  return pts.sort((a,b)=> codeCmp(a.code, b.code));
}
const PTS = pointsFor();

const PT = Object.fromEntries(PTS.map(p => [p.code, p]));
const ORDER = [...PTS].sort((a,b) => (b.ok-a.ok) || codeCmp(a.code,b.code));   // prima i verificati
const posShort = p => p.official ? `Posizione da documento ufficiale [${p.src.n}]` : "Posizione indicativa";
const isNarrow = () => matchMedia("(max-width:899px)").matches;
/* ---------- passaggi e soldi ---------- */
// passaggi: per ogni scheda, lo stato dei 5 passaggi (lettura delle schede, fatta a mano)
// scenario peggiore: "done" solo se lo conferma un ente di controllo (Ministero, Regione, Provincia, ARPA, ISPRA)
// e vale per tutta l'area; se lo dice solo chi fa i lavori (Ilva, Comune, Commissario) o se una parte
// (per esempio l'acqua sotterranea) resta aperta, il passaggio è "part"
const STATI = [
  ["done","Fatto","--s-done"],["part","A metà","--s-part"],["todo","Non ancora","--s-todo"],["no","Non previsto","--s-no"],["na","Non si sa","--s-na"]
];
// [nome tecnico, cosa vuol dire, nome breve per la barra della scheda]
const PASSI = [["Caratterizzazione","si analizzano terreno e acqua per sapere cosa c'è","Analisi"],["Analisi di rischio","si calcola se l'inquinamento è pericoloso per le persone","Rischio"],["Messa in sicurezza","si chiude l'inquinamento perché non si sposti","Sicurezza"],["Bonifica","si toglie l'inquinamento","Bonifica"],["Certificazione","un ente di controllo dichiara l'area bonificata","Certificato"]];
// fin dove è arrivata un'area: conta solo "done", che vale già lo scenario peggiore ("part" non porta avanti)
const FASI = [
  ["dafare",  "Analisi da fare o da finire", "il terreno non è ancora stato analizzato del tutto"],
  ["analisi", "Analisi fatte", "si sa cosa c'è, non ancora se è pericoloso"],
  ["rischio", "Analisi di rischio fatta", "si sa se è pericoloso, nessun lavoro finito"],
  ["mis",     "Messa in sicurezza", "l'inquinamento è chiuso dentro, ma resta lì"],
  ["nonserve","Bonifica non necessaria", "secondo le analisi il rischio è accettabile"],
  ["bonifica","Bonificata, certificato non visto", "un ente di controllo la dice bonificata, ma il certificato non l'abbiamo visto"],
  ["cert",    "Bonificata, con certificato", "il certificato ufficiale esiste e l'abbiamo visto"]
];
function fase(steps){
  const s = steps.map(x => x[0]);
  if (s[4] === "done") return "cert";
  if (s[3] === "done") return "bonifica";
  if (s[2] === "done") return "mis";
  if (s[3] === "no" && s[1] === "done") return "nonserve";
  if (s[1] === "done") return "rischio";
  if (s[0] === "done") return "analisi";
  return "dafare";
}
// riquadro "fin dove è arrivata", barra delle 5 tappe e legenda: nel report e nell'anteprima della mappa
function faseHtml(steps, sid){
  if (!steps) return `<p class="fase"><b>Nessuna bonifica</b><span>${esc(NO_STEPS[sid] || "Le fonti non permettono di dire a che punto sono i 5 passaggi.")}</span></p>`;
  const [, nome, sub] = FASI.find(f => f[0] === fase(steps));
  // tappe "a metà" dopo l'ultima fatta: senza questa riga la fase sembra smentita dalla barra
  const da = Math.max(0, steps.map(x => x[0]).lastIndexOf("done"));
  const meta = steps.map((x,i) => [x,i]).filter(([x,i]) => i > da && x[0] === "part");
  return `<p class="fase"><b>${esc(nome)}</b><span>${esc(sub)}</span>${meta.map(([x,i]) => `<span class="fp" style="--c:var(${STATO.part.color})"><i></i><span><b>${PASSI[i][2]}, a metà:</b> ${esc(x[1])}</span></span>`).join("")}</p>`;
}
// ogni pallino si tocca (o si clicca): sotto la barra compare il perché, dal testo della tappa
const barraHtml = steps => `<ol class="barra5">${steps.map(([k,t],i) => `<li class="${k}" style="--c:var(${STATO[k].color})" tabindex="0" role="button" aria-label="${esc(PASSI[i][0])}: ${esc(STATO[k].label)}" data-i="${i}" data-why="${esc(t)}"><i></i><span>${PASSI[i][2]}</span></li>`).join("")}</ol><p class="barra-why" hidden></p>`;
const leg5Html = () => `<p class="leg5">${["done","part","todo","no"].map(k => `<span class="${k}" style="--c:var(${STATO[k].color})"><i></i>${STATO[k].label.toLowerCase()}</span>`).join("")}<span class="hint">Tocca un pallino per il motivo</span></p>`;
function barraWhy(e){
  const li = e.target.closest(".barra5 li"); if (!li) return;
  if (e.type === "keydown" && e.key !== "Enter" && e.key !== " ") return;
  e.preventDefault();
  const ol = li.parentElement, p = ol.nextElementSibling, era = li.classList.contains("sel");
  ol.querySelectorAll(".sel").forEach(x => x.classList.remove("sel"));
  p.hidden = era;
  if (era) return;
  const i = +li.dataset.i, k = li.className.split(" ")[0];
  li.classList.add("sel");
  p.innerHTML = `<b>${esc(PASSI[i][0])}, ${esc(STATO[k].label.toLowerCase())}.</b> ${esc(li.dataset.why)} <small>(${esc(PASSI[i][1])})</small>`;
}
document.addEventListener("click", barraWhy);
document.addEventListener("keydown", barraWhy);
const STEPS = {
  "gravina-leucaspide":[["part","Indagini, sondaggi e controlli; il piano delle analisi approvato nel 2022 a fine 2025 non era partito"],["na","Le fonti non ne parlano"],["todo","Messa in sicurezza delle colline ancora da progettare"],["todo","Non bonificata"],["todo","Non ancora"]],
  "discarica-nord-ovest":[["part","Indagini su rifiuti e terreno 2020–2023; le analisi di tutta la zona sono nella procedura della Gravina (A1)"],["na","Le fonti non ne parlano"],["part","Solo il progetto, approvato il 16/12/2025; nessuna fonte dice che i lavori siano partiti"],["no","Non prevista: i rifiuti restano sotto una copertura"],["todo","Non ancora: a fine lavori la Provincia dovrà certificare la messa in sicurezza"]],
  "discarica-due-mari":[["na","Le fonti non riportano analisi dei rifiuti"],["na","Le fonti non ne parlano"],["part","Copertura di terra e teli secondo Ilva, non verificata"],["no","Non prevista: i rifiuti restano nella discarica"],["todo","Nessun certificato: la Provincia non lo rilascia senza garanzie adeguate"]],
  "discarica-cementir":[["na","Le fonti non riportano i risultati delle analisi"],["na","Le fonti non ne parlano"],["part","Barriera e copertura finite nel 2023 secondo Ilva, non verificate; falda superficiale inquinata, pompaggio d'emergenza"],["no","Non prevista: i rifiuti restano nella discarica"],["todo","Nessun certificato di fine lavori"]],
  "stoccaggio-fanghi":[["todo","Il terreno non è ancora stato analizzato: le analisi si faranno dopo la rimozione di tutti i fanghi"],["todo","Non ancora"],["todo","Non messo in sicurezza"],["todo","Non bonificato; i fanghi sono stati in gran parte portati via"],["todo","Non ancora"]],
  "discarica-nuove-vasche":[["na","Le fonti non dicono quali rifiuti contenga"],["na","Le fonti non ne parlano"],["part","Chiusa e coperta, in post-gestione fino al 2048 secondo Ilva; l'atto della Provincia sulla chiusura non l'abbiamo trovato"],["no","Non prevista: i rifiuti restano dove sono"],["no","Discarica in post-gestione, non una bonifica da certificare"]],
  "area-verde-ovest":[["done","Analisi del 2021; nel 2025 trovati materiali di riporto fino a 21 m"],["part","Analisi di rischio del 2023 respinta, da rifare"],["todo","Non messa in sicurezza"],["todo","Non bonificata"],["todo","Non ancora"]],
  "area-verde-nord":[["done","Analisi 2021–2022"],["part","Analisi di rischio di Ilva respinta; pratica archiviata dal Ministero a febbraio 2024"],["todo","Non messa in sicurezza"],["todo","Non bonificata"],["todo","Non ancora"]],
  "land-a":[["done","Analisi del 2023, validate da ARPA nel 2024"],["todo","A fine 2025 non ancora presentata"],["todo","Non messa in sicurezza; rifiuti di superficie tolti"],["todo","Non bonificata"],["todo","Non ancora"]],
  "land-c":[["done","Analisi di terreno e acqua sotterranea"],["part","Decreto n. 250/2023: terreno \"non contaminato\"; per l'acqua sotterranea, inquinata, la pratica è aperta"],["todo","Per il terreno non serve; per l'acqua sotterranea non ancora"],["todo","Per il terreno non serve; l'acqua sotterranea resta da trattare"],["todo","Nessun certificato: l'acqua sotterranea resta da trattare"]],
  "land-d1":[["done","Analisi validate da ARPA nel novembre 2023"],["todo","A fine 2025 non ancora presentata"],["todo","Non messa in sicurezza"],["todo","Non bonificata; rimozione dei rifiuti sepolti \"in corso di ultimazione\" secondo Ilva"],["todo","Non ancora"]],
  "land-e":[["done","Analisi del 2022"],["part","Respinta così com'era dal Ministero (gennaio 2024); nuovi controlli sull'acqua in corso"],["todo","Non messa in sicurezza dal punto di vista ambientale"],["todo","Non bonificata"],["todo","Non ancora"]],
  "land-l-amastuola":[["todo","Piano delle analisi non approvato (2023); l'indagine preliminare a fine 2025 non era partita"],["todo","Non ancora"],["todo","Non messa in sicurezza"],["todo","Non bonificata"],["todo","Non ancora"]],
  "collinette-ecologiche":[["part","Indagini per la Procura 2019–2020; piano completo approvato a dicembre 2024, a fine 2025 non ancora iniziato"],["part","Analisi di Ilva del 2021, consegnata in Procura: non pubblica e non approvata da enti pubblici"],["part","Solo misure precauzionali: rete in cocco su parte della Collinetta 3 (2019)"],["todo","Non bonificate"],["todo","Non ancora"]],
  "land-d2":[["done","Analisi sul posto giugno–luglio 2021, validate da ARPA nel 2022"],["done","Approvata con il decreto n. 185 del 4/12/2024"],["no","Non serve: il decreto n. 185 dichiara l'area non contaminata"],["no","Non serve: il rischio calcolato è accettabile, gli inquinanti restano lì"],["no","Nessuna bonifica da certificare: il decreto n. 185 chiude la procedura"]],
  "pozzo-25":[["done","Analisi di terreno e acqua"],["part","Decreto n. 149/2026: terreno nei limiti, ma acqua sotterranea \"contaminata\""],["part","Previsti solo controlli e divieto di accesso; impianto a osmosi non ancora installato a fine 2025"],["todo","Non bonificata"],["todo","Non ancora"]],
  "land-i":[["no","Nessuna analisi: Ilva dice che non servono"],["no","Ilva dice che non serve"],["no","Ilva dice che non serve"],["no","Ilva dice che non serve"],["no","Nessun atto pubblico dice che l'area è pulita"]],
  "cimitero-san-brunone":[["done","Terreno analizzato, risultati convalidati da ARPA (ma non pubblicati)"],["done","Completata ad agosto 2015, approvata dalla Regione il 12/02/2016"],["todo","Per il Commissario la messa in sicurezza d'emergenza è \"completata\" (agosto 2026), ma nessun atto la descrive: solo recinzioni e teloni sulla terra scavata"],["part","Lavori iniziati nel 2020, fermati dopo tre mesi; gara annullata nel 2021; progetto in aggiornamento"],["todo","Non ancora"]],
  "pip-statte":[["done","Caratterizzazione di terreni e falda finita il 30/11/2013"],["done","Rifatta e approvata dal Ministero con il decreto n. 313 del 1/08/2018"],["part","Solo l'intervento d'emergenza (pompaggio dell'olio); la messa in sicurezza definitiva è ferma dal 2020"],["todo","Nessun progetto approvato; non si sa se sarà bonifica o messa in sicurezza"],["todo","Non ancora"]],
  "mar-piccolo-gara-2018":[["done","Studi ufficiali ARPA e ISPRA (2005, 2010, 2014); i valori misurati non sono online"],["na","Le fonti non ne parlano"],["todo","Fondali non messi in sicurezza"],["todo","Gara del 2018 mai aggiudicata, nessun lavoro in mare; nessun piano finanziato per il 1° seno"],["todo","Non ancora"]],
  "scuole-tamburi-aree-verdi":[["done","Analisi del terreno completate, risultati approvati da ARPA"],["done","Completata ad agosto 2015, approvata dalla Regione (determina n. 145 del 24/06/2016): nessun rischio per la salute dai suoli"],["no","Non serve secondo l'analisi di rischio"],["no","Non serve secondo l'analisi di rischio: solo riqualificazione delle aree"],["no","Nessun certificato: secondo l'analisi di rischio non serviva una bonifica"]],
  "atleti-azzurri-tamburi":[["part","Piano delle analisi approvato dalla Regione (7/07/2025) e finanziato (3/10/2025); prelievi dal 20/10/2025, a giugno 2026 ancora \"in via di completamento\" secondo il Commissario"],["todo","Non ancora approvata"],["todo","Non messo in sicurezza"],["todo","Non bonificato"],["todo","Non ancora"]],
  "mar-piccolo-area-170":[["done","Analisi del 2005 e studi ARPA e ISPRA: inquinamento esteso da PCB e metalli; i valori misurati non sono pubblici"],["na","Le fonti non ne parlano"],["todo","Sedimenti non messi in sicurezza"],["todo","Nessun lavoro in mare; circa 33,5 mln € solo proposti dalla Regione (dicembre 2025)"],["todo","Non ancora"]],
  "acciaierie-italia-suoli":[["part","Analisi dal 2004 al 2021 (oltre 2.000 sondaggi), ma nessun test di cessione sui materiali di riporto; il piano delle nuove analisi è stato bocciato da ARPA e ISPRA nel 2023"],["part","Analisi di rischio del 2016–2017 mai esaminata: prima vanno verificati i riporti"],["part","Solo pavimentazioni, che l'azienda considera una messa in sicurezza; ISPRA e ARPA no"],["todo","Non bonificati, nessun progetto"],["todo","Non ancora"]],
  "acciaierie-italia-falda":[["part","Controlli annuali dell'azienda e controlli aggiuntivi dal 2021; per ISPRA e ARPA non bastano"],["todo","Non ancora: prima serve il quadro completo del sito"],["part","Misure provvisorie: barriera di 11 pozzi ai Parchi minerali (dal 2018) e raccolta degli idrocarburi; efficacia non valutabile secondo ARPA e ISPRA (2024)"],["todo","Nessun progetto di bonifica della falda"],["todo","Non ancora"]],
  "area-pneumatici-ua26":[["part", "Secondo Ilva fatte entro il 2018; risultati non pubblici"], ["na", "Le fonti non ne parlano"], ["part", "Solo rimozione dei pneumatici (dal 2016)"], ["todo", "Non bonificata"], ["todo", "Nessun certificato: per la Regione (2020) ancora \"potenzialmente contaminata\""]],
  "area-traversine-ua27":[["part", "Piano del 2017 (34 sondaggi); secondo Ilva fatte entro il 2018, risultati non pubblici"], ["na", "Le fonti non ne parlano"], ["part", "Solo rimozione di 7.823 t di traversine (2016–2017)"], ["todo", "Non bonificata"], ["todo", "Nessun certificato: per la Regione (2020) ancora \"potenzialmente contaminata\""]],
  "area-vasta-statte":[["done", "Analisi di tutto il territorio comunale fuori dal SIN (2014–2015)"], ["done", "Approvata nel 2017 (determinazione regionale n. 124): rischio \"inaccettabile\" in alcune zone"], ["part", "Solo divieti d'uso (ordinanza n. 62/2017, valida fino a fine 2018)"], ["todo", "Non bonificata"], ["todo", "Non ancora"]],
  "tamburi-falda":[["done", "Risultati delle analisi approvati"], ["done", "Approvata (prima di aprile 2020)"], ["todo", "Nessun intervento ad aprile 2020"], ["todo", "Non bonificata"], ["todo", "Non ancora"]],
  "tamburi-risanamento-suoli":[["part", "Fatta nelle aree pubbliche (per la Regione \"siti contaminati\"); aree private di SP2 ancora in accertamento"], ["na", "Le fonti non la descrivono; il progetto parla di \"annullare il rischio sanitario\""], ["na", "Le fonti non ne parlano"], ["part", "Lavori fatti secondo il Comune in SP1–SP3 e, secondo la Regione, in SP4; nelle aree private di SP2 niente"], ["part", "Solo SP4 per la Regione (2020), certificato non visto; SP1–SP3 chiesta, non rilasciata"]]
};
// schede con più parti: nel grafico della home ogni parte conta da sola, con i suoi passaggi
// (in cima al report resta lo stato della scheda intera, che segue la parte peggiore; sotto, "Parte per parte")
// [codice, nome, passaggi, riassunto con le note della scheda: nella lista della mappa, nel riquadro del punto e nel report]
const PARTI = {
  "tamburi-risanamento-suoli": [
    ["D5", "Tamburi SP4, suolo", [["na","Le fonti non le descrivono"],["na","Le fonti non la descrivono"],["na","Le fonti non ne parlano"],["done","Per la Regione (aprile 2020) \"sito bonificato\""],["part","Certificazione di avvenuta bonifica secondo la Regione; il certificato non l'abbiamo visto"]], "Per la Regione (aprile 2020) «sito bonificato», con la certificazione di avvenuta bonifica: il certificato non l'abbiamo visto. [1]"],
    ["D1", "Tamburi SP1, suolo", [["done","Per la Regione (aprile 2020) \"sito contaminato\": le analisi ci sono"],["na","Le fonti non la descrivono"],["na","Le fonti non ne parlano"],["part","Lavori finiti secondo il Comune, che li ha fatti; nessun ente di controllo lo conferma"],["part","Certificazione chiesta dal Comune, non rilasciata ad aprile 2020"]], "Lavori fatti secondo il Comune, che ha chiesto la certificazione; ad aprile 2020 non era stata rilasciata e per la Regione era ancora «sito contaminato». [1]"],
    ["D2", "Tamburi SP2, suolo pubblico", [["done","Per la Regione (aprile 2020) \"sito contaminato\": le analisi ci sono"],["na","Le fonti non la descrivono"],["na","Le fonti non ne parlano"],["part","Lavori finiti secondo il Comune, che li ha fatti; nessun ente di controllo lo conferma"],["part","Certificazione chiesta dal Comune, non rilasciata ad aprile 2020"]], "Lavori fatti secondo il Comune, che ha chiesto la certificazione; ad aprile 2020 non era stata rilasciata e per la Regione era ancora «sito contaminato». [1]"],
    ["D4", "Tamburi SP3, suolo", [["done","Per la Regione (aprile 2020) \"sito contaminato\": le analisi ci sono"],["na","Le fonti non la descrivono"],["na","Le fonti non ne parlano"],["part","Lavori finiti secondo il Comune, che li ha fatti; nessun ente di controllo lo conferma"],["part","Certificazione chiesta dal Comune, non rilasciata ad aprile 2020"]], "Lavori fatti secondo il Comune, che ha chiesto la certificazione; ad aprile 2020 non era stata rilasciata e per la Regione era ancora «sito contaminato». [1]"],
    ["D3", "Tamburi SP2, aree private", [["part","\"In fase di accertamento\" ad aprile 2020: solo una comunicazione di potenziale contaminazione (2005)"],["todo","Non ancora"],["todo","Non messe in sicurezza"],["todo","Non bonificate"],["todo","Non ancora"]], "Mai analizzate, per quanto sappiamo: ad aprile 2020 erano «in fase di accertamento», con solo una comunicazione di potenziale contaminazione del 2005. [1]"]
  ]
};
// parte di una scheda divisa (PARTI) per un codice, se c'è
const parteDi = (s, code) => PARTI[s.id]?.find(x => x[0] === code);
// passaggi di un codice: quelli della sua parte se la scheda è divisa (PARTI), altrimenti quelli della scheda
const stepsDi = (s, code) => parteDi(s, code)?.[2] || STEPS[s.id];
// riassunto di un codice (con le note [n]): quello della sua parte, altrimenti la riga in grassetto della scheda
const verdictDi = (s, code) => parteDi(s, code)?.[3] || s.verdict;
const senzaNote = t => t.replace(/\s*\[\d+\]/g, "");
// link al report di un codice: per le schede divise report.html#<codice>, così il report evidenzia la parte
const reportHref = code => { const s = verified[code]; return "report.html#" + (parteDi(s, code) ? code : s.id); };
// barra delle 5 tappe in piccolo, solo da guardare (per "Parte per parte")
const mini5Html = steps => `<span class="mini5" aria-label="${esc(steps.map(([k],i) => `${PASSI[i][2]}: ${STATO[k].label.toLowerCase()}`).join(", "))}">${steps.map(([k]) => `<i class="${k}" style="--c:var(${STATO[k].color})"></i>`).join("")}</span>`;
// fin dove è arrivato un codice: [id, nome, cosa vuol dire] di FASI
const faseDi = (s, code) => { const st = stepsDi(s, code); return st ? FASI.find(f => f[0] === fase(st)) : [null, "Nessuna bonifica", NO_STEPS[s.id] || ""]; };
// la stessa fase come chiave per i colori della mappa: "nessuna" se i 5 passaggi non si applicano, "" se non c'è il report
const faseCode = code => { const s = verified[code]; return s ? faseDi(s, code)[0] || "nessuna" : ""; };
// schede che non descrivono un intervento di bonifica: i 5 passaggi non si applicano
const NO_STEPS = {
  "mar-piccolo-studi":"Sono studi e analisi: nessuna bonifica, nessuna messa in sicurezza.",
};
// soldi (milioni di euro). null = dato assente o "non verificato" nella scheda: non si disegna.
// [tipo, valore, spiegazione, etichetta se assente o testo al posto del numero]
const MONEY = {
  "gravina-leucaspide":[["Stimato",null,"Nessun costo stimato: non c'è ancora un progetto dei lavori","non c'è"],["Stanziato",0.3,"0,30 mln €: finanziamento della progettazione del Comune di Statte (fondi di coesione)"],["Pagato",null,"Per i lavori: nessuna cifra","—"]],
  "discarica-nord-ovest":[["Stimato",29.8124,"29,81 mln € (costo stimato del progetto approvato)"],["Stanziato",null,"Non indicato: le fonti non dicono da dove vengono i soldi","non indicato"],["Pagato",null,"Non si sa: le relazioni di Ilva dopo il 2018 non danno cifre","non si sa"]],
  "stoccaggio-fanghi":[["Stimato",null,"Nessun costo stimato nelle fonti","—"],["Stanziato",75.03,"75,03 mln € stanziati per i fanghi secondo Ilva (luglio 2022); per le aree vicine altri 12,90 mln €"],["Pagato",7.89,"7,89 mln € pagati secondo Ilva (luglio 2022)"]],
  "discarica-nuove-vasche":[["Stimato",null,"Nessun costo stimato nelle fonti","—"],["Stanziato",3.0,"3,00 mln € per la post-gestione e i controlli per 30 anni, secondo Ilva (luglio 2022)"],["Pagato",0.87,"0,87 mln € pagati secondo Ilva (luglio 2022)"]],
  "area-verde-ovest":[["Stimato",null,"Nessun costo stimato nelle fonti","—"],["Stanziato",4.88,"4,88 mln € \"allocati\" secondo Ilva (luglio 2022)"],["Pagato",0.09,"0,09 mln € pagati secondo Ilva (luglio 2022)","0,09"]],
  "area-verde-nord":[["Stimato",null,"Nessun costo stimato nelle fonti","—"],["Stanziato",18.4,"18,40 mln € \"allocati\" secondo Ilva (luglio 2022)"],["Pagato",0.29,"0,29 mln € pagati secondo Ilva (luglio 2022)"]],
  "land-c":[["Stimato",null,"Nessun costo stimato nelle fonti","—"],["Stanziato",1.29,"1,29 mln € destinati a Land C secondo Ilva (luglio 2022)"],["Pagato",0.04,"0,04 mln € pagati secondo Ilva (luglio 2022)","0,04"]],
  "land-e":[["Stimato",null,"Nessun costo stimato nelle fonti","—"],["Stanziato",3.65,"3,65 mln € destinati a Land E secondo Ilva (luglio 2022)"],["Pagato",null,"Nessuna cifra indicata","nessuna cifra"]],
  "land-l-amastuola":[["Stimato",null,"Nessun costo stimato nelle fonti","—"],["Stanziato",3.35,"3,35 mln € assegnati secondo Ilva (luglio 2022)"],["Pagato",0.005,"Meno di 0,01 mln € pagati secondo Ilva (luglio 2022)","< 0,01"]],
  "collinette-ecologiche":[["Stimato",null,"Nessun costo stimato nelle fonti","—"],["Stanziato",37.5,"37,5 mln € \"allocati\" da Ilva per caratterizzazione e messa in sicurezza"],["Pagato",0.79,"0,79 mln € pagati a luglio 2022; dopo il 2022 non si sa"]],
  "pozzo-25":[["Stimato",null,"Nessun costo stimato nelle fonti","—"],["Stanziato",0.39,"0,39 mln € assegnati secondo Ilva (luglio 2022)"],["Pagato",0.005,"Meno di 0,01 mln € pagati secondo Ilva (luglio 2022)","< 0,01"]],
  "land-i":[["Stimato",null,"Nessun intervento previsto","—"],["Stanziato",0.01,"0,01 mln € (10.000 €) per la gestione generale, secondo Ilva (luglio 2022)","0,01"],["Pagato",0,"Nessuna spesa impegnata o pagata, secondo Ilva (luglio 2022)","0"]],
  "cimitero-san-brunone":[["Stimato",17.5,"17,5 mln € (\"attualmente stimato\", opuscolo maggio 2026)"],["Stanziato",9.3771,"9,38 mln € disponibili ad aprile 2026"],["Pagato",null,"Quanto è stato speso in tutto non si sa","non si sa"]],
  "pip-statte":[["Stimato",124.074,"124,07 mln €: costo del nuovo intervento nell'Accordo per la Coesione (novembre 2025)"],["Stanziato",89.9,"89,9 mln € assegnati dal Fondo sviluppo e coesione 2021-2027 (delibera CIPESS 51/2025)"],["Pagato",null,"Quanto è stato speso in tutto non si sa (sul nuovo intervento 0 € al 30/06/2026)","non si sa"]],
  "scuole-tamburi-aree-verdi":[["Stimato",0.165,"165.000 €: costo di analisi e analisi di rischio per le tre scuole","0,17"],["Stanziato",null,"Il fondo di 8 mln € del Ministero copre tutti i suoli del quartiere Tamburi, non solo queste scuole","vedi nota"],["Pagato",0.0497,"49.709,97 € pagati a dicembre 2018; costo finale non si sa","0,05"]],
  "atleti-azzurri-tamburi":[["Stimato",null,"Il costo di una bonifica non esiste ancora: prima servono analisi e analisi di rischio","non c'è"],["Stanziato",0.0869,"86.876,20 € dal Commissario per le analisi (3/10/2025)","0,09"],["Pagato",null,"Non si sa se anticipo o saldo siano stati pagati","non si sa"]],
  "mar-piccolo-area-170":[["Stimato",33.5,"Circa 33,5 mln € nel documento di proposta della Regione (dicembre 2025)"],["Stanziato",null,"Nessun finanziamento approvato trovato","nessuno"],["Pagato",null,"Speso per l'Area 170 ha: non si sa","non si sa"]],
  "land-a":[["Stimato",null,"Nessun costo stimato nelle fonti","—"],["Stanziato",2.16,"2,16 mln € stanziati secondo Ilva (luglio 2022)"],["Pagato",0.02,"0,02 mln € pagati secondo Ilva (luglio 2022); dopo il 2022 non si sa","0,02"]],
  "land-d1":[["Stimato",null,"Nessun costo stimato nelle fonti","—"],["Stanziato",2.30,"2,30 mln € stanziati secondo Ilva (luglio 2022)"],["Pagato",0.09,"0,09 mln € pagati secondo Ilva (luglio 2022)","0,09"]],
  "discarica-due-mari":[["Stimato",null,"Nessun costo stimato nelle fonti","—"],["Stanziato",5.05,"5,05 mln € di fondi previsti secondo Ilva (luglio 2022)"],["Pagato",5.39,"5,39 mln € pagati secondo Ilva (luglio 2022)"]],
  "discarica-cementir":[["Stimato",null,"Nessun costo stimato nelle fonti","—"],["Stanziato",16.75,"16,75 mln € di fondi previsti secondo Ilva (luglio 2022)"],["Pagato",5.40,"5,40 mln € pagati secondo Ilva (luglio 2022)"]],
  "mar-piccolo-gara-2018":[["Stimato",32.276,"32,28 mln € IVA esclusa: valore della gara del 2018"],["Stanziato",55,"55 mln €: fondi di tutto il programma \"sedimenti del Mar Piccolo\", non solo della gara"],["Pagato",5.586,"5,59 mln € pagati per altre attività nel Mar Piccolo, non per la gara (OpenCoesione)"]],
  "area-vasta-statte":[["Stimato", null, "Nessun costo stimato per la bonifica", "—"], ["Stanziato", 0.75, "0,75 mln € dalla Regione al Comune di Statte per nuove analisi delle aree agricole (avviso DD 202/2017)"], ["Pagato", null, "Quanto è stato speso non si sa", "non si sa"]],
  "tamburi-risanamento-suoli":[["Stimato", null, "Nessun costo stimato nelle fonti", "—"], ["Stanziato", null, "Nessuna cifra oltre al contributo del Ministero delle Infrastrutture", "—"], ["Pagato", 1.504, "1,50 mln € versati dal Ministero delle Infrastrutture al Comune il 28/09/2018 per la bonifica dei suoli dei sottoprogetti 1–3"]]
};

/* ---------- mappa: tile locali (sito/tiles) e segnaposti ---------- */
// tile scaricati per ogni zoom: [x min, x max, y min, y max]. Agli zoom lontani la zona è più ampia, così la vista d'insieme riempie lo schermo.
const TILES = {11:[1119,1124,769,773], 12:[2239,2249,1538,1547], 13:[4481,4495,3081,3091], 14:[8969,8984,6166,6177]};
function tileBounds(z){
  const zz = Math.max(11, Math.min(14, Math.round(z))), [x0,x1,y0,y1] = TILES[zz], n = 2 ** zz;
  const lon = x => x / n * 360 - 180, lat = y => Math.atan(Math.sinh(Math.PI * (1 - 2 * y / n))) * 180 / Math.PI;
  return L.latLngBounds([lat(y1 + 1), lon(x0)], [lat(y0), lon(x1 + 1)]);
}
const TILE_BOUNDS = window.L ? tileBounds(11) : null;   // zona più ampia (zoom 11)
// aggiunge i tile alla mappa e, a ogni zoom, limita lo spostamento alla zona coperta a quello zoom
function addTiles(m){
  const lock = () => m.setMaxBounds(tileBounds(m.getZoom()));
  m.options.maxBoundsViscosity = 1;
  m.on("zoomend", lock);
  m.whenReady(lock);
  // oltre lo zoom 14 (solo la mappa grande) Leaflet ingrandisce i tile del 14: un po' sfocati, ma i pallini vicini si separano
  return L.tileLayer("tiles/{z}/{x}/{y}.png", {minZoom:11, maxZoom:16, maxNativeZoom:14, bounds:TILE_BOUNDS, attribution:'© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'}).addTo(m);
}
// zoom più lontano (tra minimo e 14, a passi di 0,25) al quale la finestra della mappa sta tutta dentro la zona coperta dai tile
function coverZoom(m, from){
  for (let z = Math.max(11, from); z < 14; z += .25) if (m.getBoundsZoom(tileBounds(z), true) <= z) return z;
  return 14;
}
const pinIcon = (p, extra="") => L.divIcon({className:"pinwrap", iconSize:[0,0], html:`<span class="pin g${GRUPPO[p.code]} f-${faseCode(p.code)} ${p.ok?"ok":""} ${p.official?"exact":""} ${extra}">${p.code}</span>`});
const fmtMln = v => v.toLocaleString("it-IT",{minimumFractionDigits:1,maximumFractionDigits:2});
const STATO = Object.fromEntries(STATI.map(s => [s[0], {label:s[1], color:s[2]}]));

/* ---------- stabilimento, foto e glossario (home e report) ---------- */
// contorno dello stabilimento siderurgico: relazione OpenStreetMap 11843712 "Acciaierie d'Italia S.p.A." (© contributori OSM, licenza ODbL)
const STABILIMENTO = [[40.50586,17.17141],[40.50501,17.17138],[40.50448,17.17121],[40.50411,17.17181],[40.50358,17.17199],[40.50308,17.17185],[40.4994,17.175],[40.49865,17.17566],[40.49729,17.1776],[40.4967,17.17902],[40.49692,17.17962],[40.49707,17.17979],[40.4973,17.18004],[40.49841,17.18208],[40.49934,17.18433],[40.50019,17.18751],[40.50144,17.19212],[40.50174,17.1929],[40.50229,17.19492],[40.50269,17.19973],[40.49912,17.20314],[40.49792,17.20423],[40.49755,17.20394],[40.49583,17.20565],[40.491,17.21001],[40.49078,17.21029],[40.49074,17.2105],[40.49082,17.21065],[40.49126,17.21125],[40.49141,17.21162],[40.49133,17.21273],[40.49261,17.21524],[40.49616,17.2218],[40.49694,17.22328],[40.49808,17.22443],[40.49881,17.22471],[40.51078,17.22165],[40.5132,17.22102],[40.51493,17.22057],[40.51593,17.21997],[40.5175,17.21887],[40.51839,17.21827],[40.51913,17.2179],[40.51962,17.21597],[40.51979,17.21604],[40.51989,17.21569],[40.52117,17.21377],[40.52291,17.21004],[40.52399,17.20765],[40.52425,17.20695],[40.52511,17.20118],[40.52495,17.19967],[40.52377,17.19735],[40.52213,17.19882],[40.52044,17.19562],[40.51904,17.19285],[40.51755,17.1901],[40.51604,17.18731],[40.51451,17.189],[40.51279,17.18599],[40.5119,17.18415],[40.51287,17.1829],[40.51216,17.18013],[40.51131,17.1777],[40.51005,17.17519],[40.50956,17.1743],[40.50888,17.17311],[40.5083,17.1722],[40.50797,17.17161],[40.50749,17.17074],[40.50716,17.17012],[40.50691,17.16969],[40.50682,17.16952],[40.50668,17.16925],[40.50646,17.16987],[40.50586,17.17141]];
// foto con didascalia e credito, dal registro immagini.md (autore, licenza, link all'originale)
function fotoHtml(file, cls = "", eager = false){
  const i = DATA.immagini[file]; if (!i) return "";
  return `<figure class="photo ${cls}"><img src="img/${file}" alt="${esc(i.did)}" ${eager ? "" : 'loading="lazy"'}><figcaption>${esc(i.did)}. <span class="cr">Foto: ${esc(i.autore)}, <a href="${esc(i.url)}" target="_blank" rel="noopener">${esc(i.licenza)}</a></span></figcaption></figure>`;
}
// voci del glossario citate in un testo: si cercano le "parole" di ogni voce (le sigle maiuscole solo così come sono scritte)
function glossarioIn(testo){
  const t = testo.replace(/<[^>]+>/g, " ");
  return DATA.contesto.glossario.filter(g => g.parole.some(p => {
    const sigla = p === p.toUpperCase();
    return new RegExp("(^|[^\\wàèéìòù])" + p.replace(/[()]/g, "\\$&") + "($|[^\\wàèéìòù])", sigla ? "" : "i").test(t);
  }));
}
