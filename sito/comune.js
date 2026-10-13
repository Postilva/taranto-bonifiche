/* Codice comune a home, mappa e report. Richiede dati.js (generato da costruisci.py) caricato prima. */

/* ---------- elenco.md: gruppi A, B, C ---------- */
const byCode = (a,b) => a[0]===b[0] ? (+a.slice(1))-(+b.slice(1)) : (a<b?-1:1);
const ROWS = Object.values(DATA.elenco);
const GRUPPI_B = DATA.gruppiB;   // [titolo, [codici]] nell'ordine di elenco.md
const FUORI_G = GRUPPI_B.filter(g => /^(Nel programma|Contesto)/.test(g[0]));
const FUORI = new Set(FUORI_G.flatMap(g => g[1]));
const NON_AMB = new Set((FUORI_G.find(g => g[0].startsWith("Nel programma")) || ["",[]])[1]);
const ELENCO = {
  A: {
    title: "Aree di Ilva", count: "18 aree",
    who: "Le vecchie aree della fabbrica non passate ai nuovi gestori. Se ne occupano i commissari di Ilva in amministrazione straordinaria. Fonte: relazione trimestrale di Ilva in AS, 4° trimestre 2025.",
    items: ROWS.filter(r => r[0][0]==="A").sort((a,b)=>byCode(a[0],b[0]))
  },
  B: {
    title: "Aree fuori dalla fabbrica", count: "",
    who: "Mare, quartiere Tamburi, Statte. Se ne occupa il Commissario straordinario per la bonifica di Taranto. Fonte: opuscolo del Commissario, maggio 2026.",
    subs: GRUPPI_B.filter(g => !FUORI_G.includes(g)).map(g => [g[0].replace(/^Interventi c/,"C").replace(/^Interventi i/,"I"), g[1].map(c => DATA.elenco[c])])
  },
  // voci del programma del Commissario che non sono opere ambientali, e il contesto (B14): fuori da conteggi e mappa
  X: FUORI_G.map(g => [g[0], g[1].map(c => DATA.elenco[c])]),
  C: {
    title: "Altri responsabili", count: "da esplorare",
    who: "Soggetti elencati dal Ministero nella pagina del SIN di Taranto. Qui non abbiamo ancora cercato.",
    items: ["Acciaierie d'Italia (l'acciaieria in funzione)","Raffineria Eni","Cementir","Italcave","Marina Militare / Arsenale","Autorità portuale"]
  }
};
ELENCO.B.count = ELENCO.B.subs.reduce((n,s) => n + s[1].length, 0) + " interventi";

// nome breve per lista, grafici e cronologia (se manca si usa il titolo fino alla parentesi)
const SHORT = {"discarica-nord-ovest":"Discarica Nord-Ovest","mar-piccolo-gara-2018":"Mar Piccolo, gara 2018","pip-statte":"PIP Statte","stoccaggio-fanghi":"Stoccaggio fanghi","land-l-amastuola":"Land L (Amastuola)","gravina-leucaspide":"Gravina di Leucaspide","cimitero-san-brunone":"Cimitero San Brunone","mar-piccolo-mercato-ittico":"Mar Piccolo, mercato ittico","mar-piccolo-rifiuti-lotto1":"Mar Piccolo, rifiuti 1° lotto","mar-piccolo-rifiuti-lotto2":"Mar Piccolo, rifiuti 2° lotto","mar-piccolo-studi":"Mar Piccolo, studi","mar-piccolo-area-170":"Mar Piccolo, Area 170 ha","scuole-tamburi-aree-verdi":"Aree verdi delle scuole Tamburi","scuole-tamburi-riqualificazione":"Scuole Tamburi, lavori","atleti-azzurri-tamburi":"Impianto Atleti Azzurri","deperimetrazione-sin":"Riduzione del SIN","molo-polisettoriale":"Molo polisettoriale","mitili-mitica":"Cozze e MITICA","sea-hub":"Sea Hub, Arco Nord","filiere-verdi":"Filiere verdi"};
// note sulla posizione che la scheda stessa segnala
const COORD_NOTE = {"pozzo-25":"Attenzione: la scheda segnala che le fonti danno coordinate diverse tra loro (il piano del 2021 indica un punto circa 2,8 km più a nord)."};
const SCHEDE = DATA.schede.map(s => ({...s, short: SHORT[s.id] || s.title.split(/ \(|:/)[0]}));

/* ---------- utilità ---------- */
const $ = s => document.querySelector(s);
const esc = s => String(s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
// schede in ordine di codice: A prima di B, poi per numero
SCHEDE.sort((a,b)=> a.code[0]===b.code[0] ? (+a.code.slice(1))-(+b.code.slice(1)) : a.code<b.code?-1:1);
const verified = Object.fromEntries(SCHEDE.flatMap(s => s.codes.map(c => [c, s])));
document.querySelectorAll(".n-ok").forEach(el => el.textContent = Object.keys(verified).filter(c => !FUORI.has(c)).length);
document.querySelectorAll(".n-sch").forEach(el => el.textContent = SCHEDE.length);
function cite(html, sid){ return html.replace(/\[(\d+)\]/g, (m,n) => `<sup class="c"><a href="#${sid}-f${n}" aria-label="fonte ${n}">[${n}]</a></sup>`); }
/* ---------- interventi A e B: dati comuni a lista, mappa e report ---------- */
const ALL = [...ELENCO.A.items, ...ELENCO.B.subs.flatMap(s=>s[1])];   // [codice, nome, nota, pagina, id scheda, avviso]
const ROW = Object.fromEntries(ALL.map(i => [i[0], i]));
const TOTAL = ALL.length;   // interventi ambientali (gruppi A e B, senza le voci FUORI)
document.querySelectorAll(".n-b").forEach(el => el.textContent = ELENCO.B.count);
document.querySelectorAll(".n-x").forEach(el => el.textContent = NON_AMB.size);
const codeCmp = (a,b) => a[0]===b[0] ? (+a.slice(1))-(+b.slice(1)) : (a<b?-1:1);
const GRP = {A:"Gruppo A · Ilva in amministrazione straordinaria", B:"Gruppo B · Commissario per la bonifica", B14:"Ministero dell'Ambiente"};   // B14: i decreti di riduzione del SIN sono del Ministero
const GRP_SHORT = {A:"Gruppo A · Ilva", B:"Gruppo B · Commissario"};

/* Posizioni "da documento ufficiale": solo se la scheda riporta le coordinate di un documento (riga **Coordinate**,
   lette da costruisci.py e convertite in gradi). Tutte le altre sono INDICATIVE: messe a mano nella zona
   nominata dall'elenco o dalla scheda. */
const ZONES = {
  plant:   {ll:[40.507,17.190], r:.019, label:"Zona generica: stabilimento ex Ilva (l'elenco non indica dove si trova l'area)"},
  statte:  {ll:[40.553,17.205], r:.004, label:"Statte (luogo citato nel nome o nella scheda)"},
  gravina: {ll:[40.538,17.188], r:.003, label:"Gravina di Leucaspide, tra lo stabilimento e Statte"},
  nordovest:{ll:[40.527,17.180], r:0, label:"Confine nord della fabbrica, a Statte, vicino alla Gravina di Leucaspide (dalla scheda)"},
  cemerad: {ll:[40.558,17.215], r:0, label:"Statte, località Vocchiaro (dalla scheda); punto non preciso"},
  tamburi: {ll:[40.4905,17.2285], r:.003, label:"Quartiere Tamburi"},
  // punti presi da OpenStreetMap (non da documenti ufficiali): restano "posizione indicativa"
  collinette:{ll:[40.4988,17.2280], r:0, label:"A nord del quartiere Tamburi, accanto alla scuola Deledda (la scheda dice che la Collinetta 3 è attaccata alla scuola); punto messo da noi con OpenStreetMap"},
  deledda: {ll:[40.4971,17.2292], r:0, label:"Scuola Deledda, quartiere Tamburi (punto preso da OpenStreetMap)"},
  cimitero:{ll:[40.4918,17.2202], r:0, label:"Cimitero San Brunone, quartiere Tamburi (punto preso da OpenStreetMap)"},
  mp1:     {ll:[40.483,17.262], r:.009, label:"Mar Piccolo, 1° seno"},
  cementir:{ll:[40.4895,17.1875], r:0, label:"Vicino alla raffineria ENI (dalla scheda); punto non preciso"},
  sp48:    {ll:[40.536,17.203], r:.002, label:"Comune di Statte, vicino alla Strada provinciale 48 Taranto–Statte (dalla scheda); punto non preciso"},
  mp2:     {ll:[40.490,17.305], r:.004, label:"Mar Piccolo, 2° seno"},
  porto:   {ll:[40.465,17.180], r:.003, label:"Porto di Taranto"},
  margrande:{ll:[40.452,17.205], r:0, label:"Mar Grande"},
  generic: {ll:[40.515,17.245], r:.004, label:"Zona generica: area di Taranto (l'elenco non indica un luogo)"}
};
const PLACE = {A1:"gravina",A2:"nordovest",A4:"cementir",A5:"sp48",A6:"sp48",A15:"collinette",B1:"cemerad",B2:"deledda",B3:"tamburi",B4:"mp1",B5:"mp1",B6:"mp1",B7:"porto",B8:"cimitero",B9:"tamburi",B10:"statte",B11:"mp1",B12:"mp1",B13:"mp1",B14:"margrande",B15:"generic",B16:"mp1",B17:"mp2"};
function pointsFor(){
  const all = [...ELENCO.A.items, ...ELENCO.B.subs.flatMap(s=>s[1])];
  const byZone = {};
  const pts = [];
  all.forEach(i => {
    const s = verified[i[0]], k = s && s.coord;
    if (k) {   // coordinate da documento ufficiale
      const f = s.fonti.find(x => x.n === k.fonte);
      pts.push({code:i[0], name:i[1], note:i[2], ll:k.ll, official:true, zone:"Coordinate da documento ufficiale", ok:true,
        src:{sid:s.id, n:k.fonte, url:f && f.url, text:`${k.e} m E – ${k.n} m N (${k.sistema}), indicate nella fonte [${k.fonte}] della scheda. Conversione in gradi nostra: ${k.ll[0].toFixed(4).replace(".",",")}° N – ${k.ll[1].toFixed(4).replace(".",",")}° E.${COORD_NOTE[s.id] ? " " + COORD_NOTE[s.id] : ""}`}});
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
  return pts.sort((a,b)=> a.code[0]===b.code[0] ? (+a.code.slice(1))-(+b.code.slice(1)) : a.code<b.code?-1:1);
}
const PTS = pointsFor();

const PT = Object.fromEntries(PTS.map(p => [p.code, p]));
const ORDER = [...PTS].sort((a,b) => (b.ok-a.ok) || codeCmp(a.code,b.code));   // prima i verificati
const posShort = p => p.official ? `Posizione da documento ufficiale [${p.src.n}]` : "Posizione indicativa";
const isNarrow = () => matchMedia("(max-width:899px)").matches;
/* ---------- passaggi e soldi ---------- */
// passaggi: per ogni scheda, lo stato dei 5 passaggi (lettura delle schede, fatta a mano)
const STATI = [
  ["done","Fatto","--s-done"],["part","Iniziato, solo progettato o respinto","--s-part"],["todo","Non ancora fatto","--s-todo"],["no","Non previsto","--s-no"],["na","Non indicato nella scheda","--s-na"]
];
const PASSI = [["Caratterizzazione","analisi"],["Analisi di rischio","pericolo per le persone"],["Messa in sicurezza","chiudere il problema"],["Bonifica","eliminare l'inquinamento"],["Certificazione","\"bonificato\""]];
const STEPS = {
  "gravina-leucaspide":[["part","Indagini, sondaggi e controlli; il piano delle analisi approvato nel 2022 a fine 2025 non era partito"],["na","La scheda non ne parla"],["todo","Messa in sicurezza delle colline ancora da progettare"],["todo","Non bonificata"],["todo","Non ancora"]],
  "discarica-nord-ovest":[["part","Indagini su rifiuti e terreno 2020–2023; le analisi di tutta la zona sono nella procedura della Gravina (A1)"],["na","La scheda non ne parla"],["part","Solo il progetto, approvato il 16/12/2025; nessuna fonte dice che i lavori siano partiti"],["no","Non prevista: i rifiuti restano sotto una copertura"],["todo","Non ancora: a fine lavori la Provincia dovrà certificare la messa in sicurezza"]],
  "discarica-due-mari":[["na","La scheda non riporta analisi dei rifiuti"],["na","La scheda non ne parla"],["done","Copertura di terra e teli, secondo Ilva"],["no","Non prevista: i rifiuti restano nella discarica"],["todo","Nessun certificato: la Provincia non lo rilascia senza garanzie adeguate"]],
  "discarica-cementir":[["na","La scheda non riporta i risultati delle analisi"],["na","La scheda non ne parla"],["done","Barriera e copertura, lavori finiti nel 2023 secondo Ilva; falda superficiale inquinata, pompaggio d'emergenza"],["no","Non prevista: i rifiuti restano nella discarica"],["todo","Nessun certificato di fine lavori"]],
  "stoccaggio-fanghi":[["todo","Il terreno non è ancora stato analizzato: le analisi si faranno dopo la rimozione di tutti i fanghi"],["todo","Non ancora"],["todo","Non messo in sicurezza"],["todo","Non bonificato; i fanghi sono stati in gran parte portati via"],["todo","Non ancora"]],
  "discarica-nuove-vasche":[["na","La scheda non dice quali rifiuti contenga"],["na","La scheda non ne parla"],["done","Discarica chiusa e coperta, in post-gestione (controlli per 30 anni, fino al 2048)"],["no","Non prevista: i rifiuti restano dove sono"],["no","Discarica in post-gestione, non una bonifica da certificare"]],
  "area-verde-ovest":[["done","Analisi del 2021; nel 2025 trovati materiali di riporto fino a 21 m"],["part","Analisi di rischio del 2023 respinta, da rifare"],["todo","Non messa in sicurezza"],["todo","Non bonificata"],["todo","Non ancora"]],
  "area-verde-nord":[["done","Analisi 2021–2022"],["part","Analisi di rischio di Ilva respinta; pratica archiviata dal Ministero a febbraio 2024"],["todo","Non messa in sicurezza"],["todo","Non bonificata"],["todo","Non ancora"]],
  "land-a":[["done","Analisi del 2023, validate da ARPA nel 2024"],["todo","A fine 2025 non ancora presentata"],["todo","Non messa in sicurezza; rifiuti di superficie tolti"],["todo","Non bonificata"],["todo","Non ancora"]],
  "land-c":[["done","Analisi di terreno e acqua sotterranea"],["done","Decreto n. 250/2023: terreno \"non contaminato\"; acqua sotterranea inquinata, pratica aperta"],["no","Per il terreno non serve"],["no","Per il terreno non serve; l'acqua sotterranea resta da trattare"],["no","Nessuna bonifica da certificare per il terreno"]],
  "land-d1":[["done","Analisi validate da ARPA nel novembre 2023"],["todo","A fine 2025 non ancora presentata"],["todo","Non messa in sicurezza"],["todo","Non bonificata; rimozione dei rifiuti sepolti \"in corso di ultimazione\" secondo Ilva"],["todo","Non ancora"]],
  "land-e":[["done","Analisi del 2022"],["part","Respinta così com'era dal Ministero (gennaio 2024); nuovi controlli sull'acqua in corso"],["todo","Non messa in sicurezza dal punto di vista ambientale"],["todo","Non bonificata"],["todo","Non ancora"]],
  "land-l-amastuola":[["todo","Piano delle analisi non approvato (2023); l'indagine preliminare a fine 2025 non era partita"],["todo","Non ancora"],["todo","Non messa in sicurezza"],["todo","Non bonificata"],["todo","Non ancora"]],
  "collinette-ecologiche":[["part","Indagini per la Procura 2019–2020; piano completo approvato a dicembre 2024, a fine 2025 non ancora iniziato"],["part","Analisi di Ilva del 2021, consegnata in Procura: non pubblica e non approvata da enti pubblici"],["part","Solo misure precauzionali: rete in cocco su parte della Collinetta 3 (2019)"],["todo","Non bonificate"],["todo","Non ancora"]],
  "land-d2":[["done","Analisi sul posto giugno–luglio 2021, validate da ARPA nel 2022"],["done","Approvata con il decreto n. 185 del 4/12/2024"],["no","Non serve: il decreto n. 185 dichiara l'area non contaminata"],["no","Non serve: il rischio calcolato è accettabile, gli inquinanti restano lì"],["no","Nessuna bonifica da certificare: il decreto n. 185 chiude la procedura"]],
  "pozzo-25":[["done","Analisi di terreno e acqua"],["done","Decreto n. 149/2026: terreno nei limiti, acqua sotterranea \"contaminata\""],["part","Previsti solo controlli e divieto di accesso; impianto a osmosi non ancora installato a fine 2025"],["todo","Non bonificata"],["todo","Non ancora"]],
  "land-i":[["no","Nessuna analisi: Ilva dice che non servono"],["no","Ilva dice che non serve"],["no","Ilva dice che non serve"],["no","Ilva dice che non serve"],["no","Nessun atto pubblico dice che l'area è pulita"]],
  "ex-cemerad":[["part","Una prima analisi nel 2005, risultati non pubblicati; la nuova analisi del sito è da avviare"],["na","La scheda non ne parla"],["done","Deposito messo in sicurezza e svuotato: 16.640 fusti tolti entro il 29/01/2025"],["todo","Da avviare, dopo analisi e demolizione del capannone"],["todo","Non ancora"]],
  "cimitero-san-brunone":[["done","Terreno analizzato, risultati convalidati da ARPA (ma non pubblicati)"],["done","Completata ad agosto 2015, approvata dalla Regione il 12/02/2016"],["todo","Per il Commissario la messa in sicurezza d'emergenza è \"completata\" (agosto 2026), ma nessun atto la descrive: solo recinzioni e teloni sulla terra scavata"],["part","Lavori iniziati nel 2020, fermati dopo tre mesi; gara annullata nel 2021; progetto in aggiornamento"],["todo","Non ancora"]],
  "pip-statte":[["done","Caratterizzazione di terreni e falda finita il 30/11/2013"],["done","Rifatta e approvata dal Ministero con il decreto n. 313 del 1/08/2018"],["part","Solo l'intervento d'emergenza (pompaggio dell'olio); la messa in sicurezza definitiva è ferma dal 2020"],["todo","Nessun progetto approvato; non si sa se sarà bonifica o messa in sicurezza"],["todo","Non ancora"]],
  "mar-piccolo-gara-2018":[["done","Studi ufficiali ARPA e ISPRA (2005, 2010, 2014); i valori misurati non sono online"],["na","La scheda non ne parla"],["todo","Fondali non messi in sicurezza"],["todo","Gara del 2018 mai aggiudicata, nessun lavoro in mare; nessun piano finanziato per il 1° seno"],["todo","Non ancora"]],
  "scuole-tamburi-aree-verdi":[["done","Analisi del terreno completate, risultati approvati da ARPA"],["done","Completata ad agosto 2015, approvata dalla Regione (determina n. 145 del 24/06/2016): nessun rischio per la salute dai suoli"],["no","Non serve secondo l'analisi di rischio"],["no","Non serve secondo l'analisi di rischio: solo riqualificazione delle aree"],["no","Nessun certificato: secondo l'analisi di rischio non serviva una bonifica"]],
  "atleti-azzurri-tamburi":[["part","Piano delle analisi approvato dalla Regione (7/07/2025) e finanziato (3/10/2025); a maggio 2026 i prelievi erano iniziati, secondo il Commissario"],["todo","Non ancora"],["todo","Non messo in sicurezza"],["todo","Non bonificato"],["todo","Non ancora"]],
  "mar-piccolo-mercato-ittico":[["na","La scheda non ne parla"],["na","La scheda non ne parla"],["todo","Fondali non messi in sicurezza"],["todo","Relitto rimosso e smaltito (lavori finiti il 17/12/2021); i fanghi del fondale non sono stati bonificati"],["todo","Solo il certificato di regolare esecuzione del contratto (16/03/2022), non di bonifica"]],
  "mar-piccolo-rifiuti-lotto1":[["na","La scheda non ne parla"],["na","La scheda non ne parla"],["todo","Sedimenti non messi in sicurezza"],["todo","Rifiuti e relitti tolti dal fondale (circa 500 tonnellate nella prima tranche); nessuna bonifica dei sedimenti"],["todo","Nessun certificato di bonifica"]],
  "mar-piccolo-rifiuti-lotto2":[["na","La scheda non ne parla"],["na","La scheda non ne parla"],["todo","Non messo in sicurezza"],["todo","Non c'è progetto, gara o cantiere"],["todo","Non ancora"]],
  "mar-piccolo-area-170":[["done","Analisi del 2005 e studi ARPA e ISPRA: inquinamento esteso da PCB e metalli; i valori misurati non sono pubblici"],["na","La scheda non ne parla"],["todo","Sedimenti non messi in sicurezza"],["todo","Nessun lavoro in mare; circa 33,5 mln € solo proposti dalla Regione (dicembre 2025)"],["todo","Non ancora"]],
  "filiere-verdi":[["na","La scheda non ne parla: non si sa ancora dove siano i 90 ettari"],["na","La scheda non ne parla"],["todo","Non messo in sicurezza"],["part","Pulizia del suolo con le piante su circa 90 ettari: parte a terra ammessa a finanziamento (marzo 2026), non ancora partita sul campo"],["todo","Non ancora"]],
};
// schede che non descrivono un intervento di bonifica: i 5 passaggi non si applicano
const NO_STEPS = {
  "deperimetrazione-sin":"È un atto del Ministero che riduce il perimetro del SIN, non un intervento sul terreno. Nessuna area è stata dichiarata \"bonificata\" con questi decreti.",
  "mar-piccolo-studi":"Sono studi e analisi: nessuna bonifica, nessuna messa in sicurezza.",
  "mitili-mitica":"Sono studi sulle cozze: nessuno dei due progetti interviene su fanghi o acqua del Mar Piccolo.",
  "scuole-tamburi-riqualificazione":"Sono lavori su edifici, aria delle aule e cortili: non è un'opera ambientale.",
  "molo-polisettoriale":"È un'opera portuale (banchina e dragaggio per le navi): non è un'opera ambientale.",
  "sea-hub":"È una riqualificazione della costa (demolizione di pontili e strutture): non è un'opera ambientale."
};
// soldi (milioni di euro). null = dato assente o "non verificato" nella scheda: non si disegna.
// [tipo, valore, spiegazione, etichetta se assente o testo al posto del numero]
const MONEY = {
  "gravina-leucaspide":[["Stimato",null,"Nessun costo stimato: non c'è ancora un progetto dei lavori","non c'è"],["Stanziato",0.3,"0,30 mln €: finanziamento della progettazione del Comune di Statte (fondi di coesione)"],["Pagato",null,"Per i lavori: nessuna cifra","—"]],
  "discarica-nord-ovest":[["Stimato",29.8124,"29,81 mln € (costo stimato del progetto approvato)"],["Stanziato",null,"Non indicato: le fonti non dicono da dove vengono i soldi","non indicato"],["Pagato",null,"Non si sa: le relazioni di Ilva dopo il 2018 non danno cifre","non si sa"]],
  "stoccaggio-fanghi":[["Stimato",null,"La scheda non dà un costo stimato","—"],["Stanziato",75.03,"75,03 mln € stanziati per i fanghi secondo Ilva (luglio 2022); per le aree vicine altri 12,90 mln €"],["Pagato",7.89,"7,89 mln € pagati secondo Ilva (luglio 2022)"]],
  "discarica-nuove-vasche":[["Stimato",null,"La scheda non dà un costo stimato","—"],["Stanziato",3.0,"3,00 mln € per la post-gestione e i controlli per 30 anni, secondo Ilva (luglio 2022)"],["Pagato",0.87,"0,87 mln € pagati secondo Ilva (luglio 2022)"]],
  "area-verde-ovest":[["Stimato",null,"La scheda non dà un costo stimato","—"],["Stanziato",4.88,"4,88 mln € \"allocati\" secondo Ilva (luglio 2022)"],["Pagato",0.09,"0,09 mln € pagati secondo Ilva (luglio 2022)","0,09"]],
  "area-verde-nord":[["Stimato",null,"La scheda non dà un costo stimato","—"],["Stanziato",18.4,"18,40 mln € \"allocati\" secondo Ilva (luglio 2022)"],["Pagato",0.29,"0,29 mln € pagati secondo Ilva (luglio 2022)"]],
  "land-c":[["Stimato",null,"La scheda non dà un costo stimato","—"],["Stanziato",1.29,"1,29 mln € destinati a Land C secondo Ilva (luglio 2022)"],["Pagato",0.04,"0,04 mln € pagati secondo Ilva (luglio 2022)","0,04"]],
  "land-e":[["Stimato",null,"La scheda non dà un costo stimato","—"],["Stanziato",3.65,"3,65 mln € destinati a Land E secondo Ilva (luglio 2022)"],["Pagato",null,"Nessuna cifra indicata","nessuna cifra"]],
  "land-l-amastuola":[["Stimato",null,"La scheda non dà un costo stimato","—"],["Stanziato",3.35,"3,35 mln € assegnati secondo Ilva (luglio 2022)"],["Pagato",0.005,"Meno di 0,01 mln € pagati secondo Ilva (luglio 2022)","< 0,01"]],
  "collinette-ecologiche":[["Stimato",null,"La scheda non dà un costo stimato","—"],["Stanziato",37.5,"37,5 mln € \"allocati\" da Ilva per caratterizzazione e messa in sicurezza"],["Pagato",0.79,"0,79 mln € pagati a luglio 2022; dopo il 2022 non si sa"]],
  "pozzo-25":[["Stimato",null,"La scheda non dà un costo stimato","—"],["Stanziato",0.39,"0,39 mln € assegnati secondo Ilva (luglio 2022)"],["Pagato",0.005,"Meno di 0,01 mln € pagati secondo Ilva (luglio 2022)","< 0,01"]],
  "land-i":[["Stimato",null,"Nessun intervento previsto","—"],["Stanziato",0.01,"0,01 mln € (10.000 €) per la gestione generale, secondo Ilva (luglio 2022)","0,01"],["Pagato",0,"Nessuna spesa impegnata o pagata, secondo Ilva (luglio 2022)","0"]],
  "ex-cemerad":[["Stimato",16.4285,"16,43 mln € (costo previsto, accordo con Sogin 2023)"],["Stanziato",18.8,"18,8 mln € (10 mln legge 2015 + 8,8 mln legge di bilancio 2022)"],["Pagato",16.86,"16,86 mln € (due progetti dello svuotamento, OpenCoesione al 30/06/2026)"]],
  "cimitero-san-brunone":[["Stimato",17.5,"17,5 mln € (\"attualmente stimato\", opuscolo maggio 2026)"],["Stanziato",9.3771,"9,38 mln € disponibili ad aprile 2026"],["Pagato",null,"Quanto è stato speso in tutto non si sa","non si sa"]],
  "pip-statte":[["Stimato",124.074,"124,07 mln €: costo del nuovo intervento nell'Accordo per la Coesione (novembre 2025)"],["Stanziato",89.9,"89,9 mln € assegnati dal Fondo sviluppo e coesione 2021-2027 (delibera CIPESS 51/2025)"],["Pagato",null,"Quanto è stato speso in tutto non si sa (sul nuovo intervento 0 € al 30/06/2026)","non si sa"]],
  "scuole-tamburi-aree-verdi":[["Stimato",0.165,"165.000 €: costo di analisi e analisi di rischio per le tre scuole","0,17"],["Stanziato",null,"Il fondo di 8 mln € del Ministero copre tutti i suoli del quartiere Tamburi, non solo queste scuole","vedi nota"],["Pagato",0.0497,"49.709,97 € pagati a dicembre 2018; costo finale non si sa","0,05"]],
  "atleti-azzurri-tamburi":[["Stimato",null,"Il costo di una bonifica non esiste ancora: prima servono analisi e analisi di rischio","non c'è"],["Stanziato",0.0869,"86.876,20 € dal Commissario per le analisi (3/10/2025)","0,09"],["Pagato",null,"Non si sa se anticipo o saldo siano stati pagati","non si sa"]],
  "mar-piccolo-mercato-ittico":[["Stimato",2.5123,"2,51 mln €: base d'asta della gara (2019)"],["Stanziato",null,"Pagato con i fondi del programma \"sedimenti del Mar Piccolo\" da 55 mln €, non solo per questo lavoro","vedi nota"],["Pagato",2.4288,"2,43 mln € IVA esclusa, saldo pagato il 12/09/2022; l'impresa chiede altri 0,96 mln € in tribunale"]],
  "mar-piccolo-rifiuti-lotto2":[["Stimato",4.7,"4,7 mln € stimati nella lista della Regione (2024), dentro i 429,7 mln € del Mar Piccolo 1° seno"],["Stanziato",null,"Soldi disponibili e certi: non si sa","non si sa"],["Pagato",0,"Nulla risulta speso","0"]],
  "mar-piccolo-area-170":[["Stimato",33.5,"Circa 33,5 mln € nel documento di proposta della Regione (dicembre 2025)"],["Stanziato",null,"Nessun finanziamento approvato trovato","nessuno"],["Pagato",null,"Speso per l'Area 170 ha: non si sa","non si sa"]],
  "filiere-verdi":[["Stimato",null,"La scheda non dà un costo stimato diverso dai fondi","—"],["Stanziato",22.976,"22,98 mln € ammessi per la parte a terra (marzo 2026); la parte a mare è scesa a 3,06 mln € (giugno 2026)"],["Pagato",null,"La scheda non indica pagamenti","—"]],
  "sea-hub":[["Stimato",13.2036,"13,20 mln €: fabbisogno stimato dal Commissario per l'Arco Nord"],["Stanziato",null,"Solo fabbisogni stimati, non un contributo già ammesso","non ancora"],["Pagato",null,"Nessun lavoro fatto sull'Arco Nord","—"]],
  "land-a":[["Stimato",null,"La scheda non dà un costo stimato","—"],["Stanziato",2.16,"2,16 mln € stanziati secondo Ilva (luglio 2022)"],["Pagato",0.02,"0,02 mln € pagati secondo Ilva (luglio 2022); dopo il 2022 non si sa","0,02"]],
  "land-d1":[["Stimato",null,"La scheda non dà un costo stimato","—"],["Stanziato",2.30,"2,30 mln € stanziati secondo Ilva (luglio 2022)"],["Pagato",0.09,"0,09 mln € pagati secondo Ilva (luglio 2022)","0,09"]],
  "discarica-due-mari":[["Stimato",null,"La scheda non dà un costo stimato","—"],["Stanziato",5.05,"5,05 mln € di fondi previsti secondo Ilva (luglio 2022)"],["Pagato",5.39,"5,39 mln € pagati secondo Ilva (luglio 2022)"]],
  "discarica-cementir":[["Stimato",null,"La scheda non dà un costo stimato","—"],["Stanziato",16.75,"16,75 mln € di fondi previsti secondo Ilva (luglio 2022)"],["Pagato",5.40,"5,40 mln € pagati secondo Ilva (luglio 2022)"]],
  "mar-piccolo-gara-2018":[["Stimato",32.276,"32,28 mln € IVA esclusa: valore della gara del 2018"],["Stanziato",55,"55 mln €: fondi di tutto il programma \"sedimenti del Mar Piccolo\", non solo della gara"],["Pagato",5.586,"5,59 mln € pagati per altre attività nel Mar Piccolo, non per la gara (OpenCoesione)"]]
};

/* ---------- mappa: tile locali (sito/tiles) e segnaposti ---------- */
// tile scaricati per ogni zoom: [x min, x max, y min, y max]. Agli zoom lontani la zona è più ampia, così la vista d'insieme riempie lo schermo.
const TILES = {11:[1119,1124,769,773], 12:[2239,2249,1538,1547], 13:[4481,4495,3081,3091], 14:[8969,8984,6166,6177]};
function tileBounds(z){
  const [x0,x1,y0,y1] = TILES[Math.max(11, Math.min(14, Math.round(z)))], n = 2 ** Math.round(z);
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
  return L.tileLayer("tiles/{z}/{x}/{y}.png", {minZoom:11, maxZoom:14, bounds:TILE_BOUNDS, attribution:'© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'}).addTo(m);
}
// zoom più lontano (tra minimo e 14) al quale la finestra della mappa sta tutta dentro la zona coperta dai tile
function coverZoom(m, from){
  for (let z = Math.max(11, from); z < 14; z++) if (m.getBoundsZoom(tileBounds(z), true) <= z) return z;
  return 14;
}
const pinIcon = (p, extra="") => L.divIcon({className:"pinwrap", iconSize:[0,0], html:`<span class="pin ${p.ok?"ok":""} ${p.official?"exact":""} ${extra}">${p.code}</span>`});
const fmtMln = v => v.toLocaleString("it-IT",{minimumFractionDigits:1,maximumFractionDigits:2});
const STATO = Object.fromEntries(STATI.map(s => [s[0], {label:s[1], color:s[2]}]));
