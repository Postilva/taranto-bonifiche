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
    title: "Ricadute dell'Ilva",
    who: "Quartiere Tamburi, Statte, Mar Piccolo: aree per cui una fonte ufficiale dice che l'inquinamento viene (anche) dall'Ilva.",
    subs: subs(DATA.gruppiB)
  }
};
const GRUPPO = {};   // codice → "A" | "B"
for (const g of ["A","B"]) {
  ELENCO[g].items = ELENCO[g].subs.flatMap(s => s[1]);
  ELENCO[g].items.forEach(r => GRUPPO[r[0]] = g);
  ELENCO[g].count = ELENCO[g].items.length + " aree";
}
// ricadute per cui la fonte che lega l'inquinamento all'Ilva non è ancora stata trovata
const DA_VERIFICARE = new Set(ELENCO.B.subs.filter(s => s[0].startsWith("Da verificare")).flatMap(s => s[1].map(r => r[0])));

// nome breve per lista, grafici e cronologia (se manca si usa il titolo fino alla parentesi)
const SHORT = {"tamburi-risanamento-suoli":"Tamburi, risanamento dei suoli (SP1–SP4)","area-pneumatici-ua26":"Area pneumatici (UA26)","area-traversine-ua27":"Area traversine (UA27)","area-vasta-statte":"Area vasta di Statte","tamburi-falda":"Tamburi, falda","discarica-nord-ovest":"Discarica Nord-Ovest","mar-piccolo-gara-2018":"Mar Piccolo, gara 2018","pip-statte":"PIP Statte","stoccaggio-fanghi":"Stoccaggio fanghi","land-l-amastuola":"Land L (Amastuola)","gravina-leucaspide":"Gravina di Leucaspide","cimitero-san-brunone":"Cimitero San Brunone","mar-piccolo-studi":"Mar Piccolo, studi","mar-piccolo-area-170":"Mar Piccolo, Area 170 ha","scuole-tamburi-aree-verdi":"Aree verdi delle scuole Tamburi","atleti-azzurri-tamburi":"Impianto Atleti Azzurri","acciaierie-italia-suoli":"Acciaieria, suoli","acciaierie-italia-falda":"Acciaieria, falda","amianto-stabilimento":"Acciaieria, amianto"};
// note sulla posizione che la scheda stessa segnala
const COORD_NOTE = {};
// cartella del sito vista dalla pagina: "" per home e mappa, "../" per i report in r/ (si ricava da come è caricato questo file)
const RADICE = document.currentScript.getAttribute("src").replace(/comune\.js.*$/, "");
// pagina del report di una scheda (r/<id>.html, scritta da costruisci.py), con un eventuale #codice o #fonte
const reportUrl = (s, hash) => `${RADICE}r/${s.id}.html${hash ? "#" + hash : ""}`;
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
  acciaieria:{ll:[40.5091,17.2083], r:.0015, label:"Stabilimento siderurgico (circa 1.050 ettari dentro il SIN): il report riguarda tutta l'area. Il punto è il centro del corpo principale dello stabilimento, a est della ferrovia (contorno di OpenStreetMap senza il tubificio, circa 700 ettari), quindi solo indicativo"},
  plant:   {ll:[40.507,17.190], r:.019, label:"Zona generica: stabilimento ex Ilva (l'elenco non indica dove si trova l'area)"},
  statte:  {ll:[40.553,17.205], r:.004, label:"Statte (luogo citato nel nome o nelle fonti)"},
  gravina: {ll:[40.5454,17.1951], r:0, label:`Gravina di Leucaspide, tra lo stabilimento e Statte (${MAPPA22}; l'area è una striscia lunga circa 3 km lungo la gravina, il punto ne indica la parte centrale)`},
  duemari: {ll:[40.5294,17.2092], r:0, label:`Ex cava Due Mari, a est della cava Mater Gratiae (${MAPPA22})`},
  nuovevasche:{ll:[40.52807,17.20317], r:0, label:"Centro delle tre vasche (V1, V2, V3) riconosciute da noi sulle ortofoto 2006 e 2012 del Ministero dell'Ambiente (Geoportale nazionale), nella zona della cava Mater Gratiae: il recinto misura circa 3,5 ettari come la discarica descritta da Ilva. Punto messo da noi, non da un documento; errore stimato sotto i 30 m"},
  d1:      {ll:[40.5044,17.1963], r:0, label:`Appena fuori dalla fabbrica, sul lato sud-ovest, accanto a Land D2 (${MAPPA22})`},
  tamburi: {ll:[40.4905,17.2285], r:.003, label:"Quartiere Tamburi"},
  // punti presi da OpenStreetMap (non da documenti ufficiali): restano "posizione indicativa"
  amastuola:{ll:[40.5987,17.1703], r:0, label:"Cava accanto alla Masseria Amastuola, a circa 1 km dalla Strada provinciale 42 (punto preso da OpenStreetMap, dove la cava ha come gestore \"ILVA in A.S.\"; nessun documento ufficiale trovato ne indica la posizione)"},
  ospnord: {ll:[40.5443,17.2753], r:0, label:"Circa 500 m dall'Ospedale San Giuseppe Moscati (\"Ospedale Nord\"). Punto messo da noi al centro di una particella catastale di 2.092 m², cioè 0,2 ettari come l'area secondo Ilva: foglio 38, particella 6, dati trovati in una fonte non ufficiale e non ancora verificati su un documento; il Comune e il foglio non li abbiamo potuti confermare sul catasto"},
  mp1:     {ll:[40.483,17.262], r:.009, label:"Mar Piccolo, 1° seno"},
  mp170:   {ll:[40.4825,17.2540], r:0, label:"Mar Piccolo, 1° seno, nello specchio d'acqua davanti all'Arsenale della Marina Militare, dove ISPRA e ARPA collocano l'\"Area 170 ha\" (2015). Punto messo da noi con OpenStreetMap: l'area è grande circa 1,7 km², il punto indica solo la zona"},
  cementir:{ll:[40.4910,17.2065], r:0, label:"Dentro la cava del cementificio, tra la raffineria ENI e lo stabilimento (punto messo da noi: la discarica indicata nella mappa delle aree di Ilva del luglio 2022 si riconosce sulla foto satellitare; errore stimato sotto i 100 m). Il punto cade nella particella 258 del foglio 198 di Taranto indicata da ARPA, che però è tutto il cementificio (circa 25 ettari): verificato da noi sul catasto"},
};
const PLACE = {A1:"gravina",A3:"duemari",A4:"cementir",A7:"nuovevasche",A12:"d1",A14:"amastuola",A18:"ospnord",B6:"mp1",B10:"statte",B12:"mp170",B13:"mp1",C1:"acciaieria",C2:"acciaieria",C35:"acciaieria",D1:"tamburi",D2:"tamburi",D3:"tamburi",D4:"tamburi",D5:"tamburi",D6:"tamburi",D8:"statte",D16:"statte",D17:"statte"};
function pointsFor(){
  const all = ALL;
  const byZone = {};
  const pts = [];
  all.forEach(i => {
    const s = verified[i[0]], k = s && ((s.coords && s.coords[i[0]]) || s.coord);   // coordinate del codice, se la scheda ne ha più di una
    if (k) {   // coordinate da documento ufficiale
      const f = s.fonti.find(x => x.n === k.fonte);
      const gradi = `${k.ll[0].toFixed(4).replace(".",",")}° N – ${k.ll[1].toFixed(4).replace(".",",")}° E`;
      pts.push({code:i[0], name:i[1], note:i[2], ll:k.ll, official:true, catasto:k.metodo === "catasto", ok:true,
        zone: k.metodo === "catasto" ? "Centro delle particelle catastali indicate da un documento ufficiale" : "Coordinate da documento ufficiale",
        src:{sid:s.id, n:k.fonte, url:f && f.url, note:(k.nota || COORD_NOTE[s.id] || ""),
          text: k.metodo === "catasto"
            ? `centro delle particelle (${k.cat}), calcolato da noi sulla cartografia catastale dell'Agenzia delle Entrate: ${k.e} m E – ${k.n} m N (${k.sistema}), cioè ${gradi}.`
            : k.metodo === "gradi"
            ? `punto con cui il Ministero indica l'area sulla sua mappa SmartEcoGIS: ${k.gradi} (WGS84); in metri, con la nostra conversione: ${k.e} m E – ${k.n} m N (${k.sistema}).`
            : `${k.e} m E – ${k.n} m N (${k.sistema}); in gradi, con la nostra conversione: ${gradi}.`}});
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
  // un solo punto ufficiale per più codici (es. A5 e A6): pallini affiancati in orizzontale, circa 70 m l'uno dall'altro
  const stessi = {};
  pts.filter(p => p.official).forEach(p => (stessi[p.ll.join()] ||= []).push(p));
  Object.values(stessi).filter(g => g.length > 1).forEach(g => g.forEach((p,k) => {
    p.ll = [p.ll[0], p.ll[1] + (k - (g.length-1)/2) * .0008];
    p.src = {...p.src, note:`Il documento dà un solo punto per ${g.map(q => q.code).join(" e ")}: sulla mappa i pallini sono affiancati.${p.src.note ? " " + p.src.note : ""}`};
  }));
  return pts.sort((a,b)=> codeCmp(a.code, b.code));
}
const PTS = pointsFor();

const PT = Object.fromEntries(PTS.map(p => [p.code, p]));
const ORDER = [...PTS].sort((a,b) => (b.ok-a.ok) || codeCmp(a.code,b.code));   // prima i verificati
const posShort = p => p.catasto ? `Posizione dal catasto indicato da un documento ufficiale [${p.src.n}]` : p.official ? `Posizione da documento ufficiale [${p.src.n}]` : "Posizione indicativa";
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
// riquadro "fin dove è arrivata", barra delle 5 tappe e legenda: nel report
function faseHtml(steps, sid){
  if (!steps && PASSI_SUOI[sid]) return `<p class="fase"><b>Passaggi diversi</b><span>${esc(PASSI_SUOI[sid])}</span></p>`;
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
  "pozzo-25":[["done","Analisi di terreno e acqua"],["done","Approvata con il decreto n. 149 del 26/05/2026: terreno nei limiti, acqua sotterranea \"contaminata\""],["part","Previsti solo controlli e divieto di accesso; impianto a osmosi non ancora installato a fine 2025"],["todo","Non bonificata"],["todo","Non ancora"]],
  "land-i":[["todo","Nessuna analisi: Ilva dice che non servono, ma nessun ente di controllo lo conferma"],["todo","Non fatta: Ilva dice che non serve"],["todo","Non fatta: Ilva dice che non serve"],["todo","Non bonificata: Ilva dice che non serve"],["todo","Nessun atto pubblico dice che l'area è pulita"]],
  "cimitero-san-brunone":[["done","Terreno analizzato, risultati convalidati da ARPA (ma non pubblicati)"],["done","Completata ad agosto 2015, approvata dalla Regione il 12/02/2016"],["todo","Per il Commissario la messa in sicurezza d'emergenza è \"completata\" (agosto 2026), ma nessun atto la descrive: solo recinzioni e teloni sulla terra scavata"],["part","Lavori iniziati nel 2020, fermati dopo tre mesi; gara annullata nel 2021; progetto in aggiornamento"],["todo","Non ancora"]],
  "pip-statte":[["done","Caratterizzazione di terreni e falda finita il 30/11/2013"],["done","Rifatta e approvata dal Ministero con il decreto n. 313 del 1/08/2018"],["part","Solo l'intervento d'emergenza (pompaggio dell'olio); la messa in sicurezza definitiva è ferma dal 2020"],["todo","Nessun progetto approvato; non si sa se sarà bonifica o messa in sicurezza"],["todo","Non ancora"]],
  "mar-piccolo-gara-2018":[["done","Studi ufficiali ARPA e ISPRA (2005, 2010, 2014); i valori misurati non sono online"],["na","Le fonti non ne parlano"],["todo","Fondali non messi in sicurezza"],["todo","Gara del 2018 mai aggiudicata, nessun lavoro in mare; nessun piano finanziato per il 1° seno"],["todo","Non ancora"]],
  "scuole-tamburi-aree-verdi":[["done","Analisi del terreno completate, risultati approvati da ARPA"],["done","Approvata dalla Regione (determina n. 145 del 24/06/2016): rischio accettabile per chi usa le aree, non accettabile per la falda"],["todo","Non messa in sicurezza"],["todo","Solo riqualificazione delle aree; gli obiettivi di bonifica per la falda sono rimandati dal 2016"],["todo","Nessun certificato"]],
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
// link al report di un codice: per le schede divise r/<id>.html#<codice>, così il report evidenzia la parte
const reportHref = code => { const s = verified[code]; return reportUrl(s, parteDi(s, code) ? code : ""); };
// barra delle 5 tappe in piccolo, solo da guardare (per "Parte per parte")
const mini5Html = steps => `<span class="mini5" aria-label="${esc(steps.map(([k],i) => `${PASSI[i][2]}: ${STATO[k].label.toLowerCase()}`).join(", "))}">${steps.map(([k]) => `<i class="${k}" style="--c:var(${STATO[k].color})"></i>`).join("")}</span>`;
// fin dove è arrivato un codice: [id, nome, cosa vuol dire] di FASI
const faseDi = (s, code) => { const st = stepsDi(s, code); return st ? FASI.find(f => f[0] === fase(st)) : PASSI_SUOI[s.id] ? [null, "Passaggi diversi", PASSI_SUOI[s.id]] : [null, "Nessuna bonifica", NO_STEPS[s.id] || ""]; };
// la stessa fase come chiave per i colori della mappa: "nessuna" se i 5 passaggi non si applicano, "" se non c'è il report
const faseCode = code => { const s = verified[code]; return s ? faseDi(s, code)[0] || (PASSI_SUOI[s.id] ? "suoi" : "nessuna") : ""; };
// schede che non descrivono un intervento di bonifica: i 5 passaggi non si applicano
const NO_STEPS = {
  "mar-piccolo-studi":"Sono studi e analisi: nessuna bonifica, nessuna messa in sicurezza.",
};
// schede con passaggi loro, diversi dai 5 di terreni e acque: fuori dal grafico della home e dalle quattro fasi (deciso il 29/10/2026)
const PASSI_SUOI = {
  "amianto-stabilimento":"L'amianto degli impianti non segue i passaggi di terreni e acque: si toglie, si riveste o si chiude dentro una barriera, i tre metodi di bonifica previsti per l'amianto. Per questo non è nel grafico delle aree.",
};
// il percorso delle 5 tappe, lo stesso nel grafico della home, nella legenda e nei filtri della mappa e nell'anteprima di un punto
// (deciso il 30/10/2026): ogni area sta nella tappa che ha davanti, la prima non ancora fatta secondo FASI. In fondo una stazione
// sola per bonificate e non necessarie, senza distinguere la tappa 5 (certificato). I pallini della mappa restano di tre colori.
// [chiave, nome, fasi, nome corto (filtri della mappa), cosa vuol dire, segno nel cerchio]
const TAPPE = [
  ["1",     "Analisi",                     ["dafare"],                       "Analisi",                "il terreno non è ancora stato analizzato del tutto",  "1"],
  ["2",     "Analisi di rischio",          ["analisi"],                      "Rischio",                "si sa cosa c'è, non ancora se è pericoloso",           "2"],
  ["3",     "Messa in sicurezza",          ["rischio"],                      "Sicurezza",              "si sa se è pericoloso, nessun lavoro finito",          "3"],
  ["4",     "Bonifica",                    ["mis"],                          "Bonifica",               "l'inquinamento è chiuso dentro, ma resta lì",          "4"],
  ["fatto", "Bonificata o non necessaria", ["nonserve", "bonifica", "cert"], "Bonificata o non serve", "",                                                     "✓"]
];
// fuori dal percorso: le schede che non sono una bonifica (NO_STEPS) e quelle con passaggi loro (PASSI_SUOI, l'amianto)
const FUORI = ["nessuna", "suoi"];
const tappaDi = c => { const f = faseCode(c); return TAPPE.find(t => t[2].includes(f))?.[0] || (FUORI.includes(f) ? "fuori" : ""); };
// sotto "Bonificata o non necessaria" quante hanno il certificato visto da noi, perché "2" non si legga "2 bonificate"
const tappaSub = t => {
  if (t[0] !== "fatto") return t[4];
  const n = ALL.filter(i => faseCode(i[0]) === "cert").length;
  return n ? `${n} con il certificato visto da noi` : "nessuna con il certificato visto da noi";
};
// le cifre del riquadro "Soldi": il blocco con le etichette in cima a "## Soldi" della scheda (letto da costruisci.py)
// {k: costo|disponibili|spesi, p: precisazione, v: euro (null = nessuna cifra), pre: "circa"|"meno di", lbl, chi, qb: quando in breve, t: [anno, mese], src: "[n]", note}
// una cifra è "vecchia" se ha più di due anni (deciso il 24/10/2026); senza mese conta dicembre
const OGGI_M = new Date().getFullYear() * 12 + new Date().getMonth() + 1;
const vecchio = r => !!r.t && OGGI_M - (r.t[0] * 12 + (r.t[1] || 12)) > 24;
// i nomi delle tre caselle sul sito e cosa vogliono dire (la "i" accanto a "Soldi", che si apre al tocco)
const NOMI_SOLDI = {costo:"Quanto costerebbe", disponibili:"Soldi disponibili", spesi:"Già spesi"};
const nomeSoldi = r => NOMI_SOLDI[r.k] + (r.p ? " · " + r.p : "");
const soldiInfo = id => `<button type="button" class="info-i" aria-expanded="false" aria-controls="${id}" aria-label="Cosa vogliono dire le cifre">i</button>`;
const soldiInfoBox = id => `<div class="info-box" id="${id}" hidden>
  <p><b>Quanto costerebbe</b>: il costo stimato dei lavori o delle analisi, scritto in un progetto, in una gara o in un altro documento.</p>
  <p><b>Soldi disponibili</b>: i soldi messi a disposizione per l'intervento. Comprende le cifre che le fonti chiamano stanziate, assegnate, allocate o impegnate.</p>
  <p><b>Già spesi</b>: i soldi già pagati, alla data indicata dalla fonte.</p>
  <p>Sotto ogni cifra c'è chi la dice e quando; le cifre di più di due anni fa sono in grigio, con scritto "dato vecchio".</p>
  <p>Sotto il milione le cifre sono in euro; "circa" vuol dire che la fonte non dà la cifra esatta (per esempio Ilva dà solo i milioni con due decimali).</p></div>`;
document.addEventListener("click", e => {
  const b = e.target.closest(".info-i"); if (!b) return;
  const open = b.getAttribute("aria-expanded") !== "true";
  b.setAttribute("aria-expanded", open); document.getElementById(b.getAttribute("aria-controls")).hidden = !open;
});

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
  return L.tileLayer(RADICE + "tiles/{z}/{x}/{y}.png", {minZoom:11, maxZoom:16, maxNativeZoom:14, bounds:TILE_BOUNDS, attribution:'© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'}).addTo(m);
}
// zoom più lontano (tra minimo e 14, a passi di 0,25) al quale la finestra della mappa sta tutta dentro la zona coperta dai tile
function coverZoom(m, from){
  for (let z = Math.max(11, from); z < 14; z += .25) if (m.getBoundsZoom(tileBounds(z), true) <= z) return z;
  return 14;
}
const pinIcon = (p, extra="") => L.divIcon({className:"pinwrap", iconSize:[0,0], html:`<span class="pin g${GRUPPO[p.code]} f-${faseCode(p.code)} ${p.ok?"ok":""} ${p.official?"exact":""} ${extra}">${p.code}</span>`});
// cifra in euro → [numero, unità]: sotto il milione euro interi (75.751 €), sopra milioni con due decimali (18,40 mln €)
const fmtSoldi = v => v < 1e6 ? [Math.round(v).toLocaleString("it-IT"), "€"] : [(v / 1e6).toLocaleString("it-IT", {minimumFractionDigits:2, maximumFractionDigits:2}), "mln €"];
// una riga del blocco dei soldi: "meno di 10.000 €" si scrive come nella scheda (nei totali conta la metà), le altre cifre con fmtSoldi
const fmtRiga = r => r.pre === "meno di" ? [r.lbl, "€"] : fmtSoldi(r.v);
// la percentuale di [confronto] sì (calcolo nostro): sotto lo 0,1% "meno di 0,1%"; fino al 100% un decimale, oltre senza
const pctSpesi = c => c.pct > 0 && c.pct < 0.1 ? "meno di 0,1%"
  : (c.pre ? c.pre + " " : "") + c.pct.toLocaleString("it-IT", {maximumFractionDigits: c.pct < 100 ? 1 : 0}) + "%";
// la barra "Già spesi su Soldi disponibili" (report; in soldi.html la scrive costruisci.py, con le stesse regole): oltre il 100% la barra intera sono i già spesi e una tacca segna i disponibili
const barraSpesi = c => `<span class="bar" role="img" aria-label="Già spesi: ${pctSpesi(c)} dei soldi disponibili">${c.pct > 0 ? `<span style="width:${Math.min(c.pct, 100)}%"></span>` : ""}${c.pct > 100 ? `<i style="left:${100 / c.pct * 100}%"></i>` : ""}</span>`;
const STATO = Object.fromEntries(STATI.map(s => [s[0], {label:s[1], color:s[2]}]));

/* ---------- stabilimento, foto e glossario (home e report) ---------- */
// contorno dello stabilimento siderurgico: relazione OpenStreetMap 11843712 "Acciaierie d'Italia S.p.A." (© contributori OSM, licenza ODbL)
const STABILIMENTO = [[40.50586,17.17141],[40.50501,17.17138],[40.50448,17.17121],[40.50411,17.17181],[40.50358,17.17199],[40.50308,17.17185],[40.4994,17.175],[40.49865,17.17566],[40.49729,17.1776],[40.4967,17.17902],[40.49692,17.17962],[40.49707,17.17979],[40.4973,17.18004],[40.49841,17.18208],[40.49934,17.18433],[40.50019,17.18751],[40.50144,17.19212],[40.50174,17.1929],[40.50229,17.19492],[40.50269,17.19973],[40.49912,17.20314],[40.49792,17.20423],[40.49755,17.20394],[40.49583,17.20565],[40.491,17.21001],[40.49078,17.21029],[40.49074,17.2105],[40.49082,17.21065],[40.49126,17.21125],[40.49141,17.21162],[40.49133,17.21273],[40.49261,17.21524],[40.49616,17.2218],[40.49694,17.22328],[40.49808,17.22443],[40.49881,17.22471],[40.51078,17.22165],[40.5132,17.22102],[40.51493,17.22057],[40.51593,17.21997],[40.5175,17.21887],[40.51839,17.21827],[40.51913,17.2179],[40.51962,17.21597],[40.51979,17.21604],[40.51989,17.21569],[40.52117,17.21377],[40.52291,17.21004],[40.52399,17.20765],[40.52425,17.20695],[40.52511,17.20118],[40.52495,17.19967],[40.52377,17.19735],[40.52213,17.19882],[40.52044,17.19562],[40.51904,17.19285],[40.51755,17.1901],[40.51604,17.18731],[40.51451,17.189],[40.51279,17.18599],[40.5119,17.18415],[40.51287,17.1829],[40.51216,17.18013],[40.51131,17.1777],[40.51005,17.17519],[40.50956,17.1743],[40.50888,17.17311],[40.5083,17.1722],[40.50797,17.17161],[40.50749,17.17074],[40.50716,17.17012],[40.50691,17.16969],[40.50682,17.16952],[40.50668,17.16925],[40.50646,17.16987],[40.50586,17.17141]];
// foto con didascalia e credito, dal registro immagini.md (autore, licenza, link all'originale)
function fotoHtml(file, cls = "", eager = false){
  const i = DATA.immagini[file]; if (!i) return "";
  return `<figure class="photo ${cls}"><img src="${RADICE}img/${file}" alt="${esc(i.did)}" ${eager ? "" : 'loading="lazy"'}><figcaption>${esc(i.did)}. <span class="cr">Foto: ${esc(i.autore)}, <a href="${esc(i.url)}" target="_blank" rel="noopener">${esc(i.licenza)}</a></span></figcaption></figure>`;
}
// voci del glossario citate in un testo: si cercano le "parole" di ogni voce (le sigle maiuscole solo così come sono scritte)
function glossarioIn(testo){
  const t = testo.replace(/<[^>]+>/g, " ");
  return DATA.contesto.glossario.filter(g => g.parole.some(p => {
    const sigla = p === p.toUpperCase();
    return new RegExp("(^|[^\\wàèéìòù])" + p.replace(/[()]/g, "\\$&") + "($|[^\\wàèéìòù])", sigla ? "" : "i").test(t);
  }));
}
