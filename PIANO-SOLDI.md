# Piano: rendere chiari i soldi (dal 24/10/2026)

Un task per chat. In una chat nuova basta scrivere: **"Leggi PIANO-SOLDI.md e fai il task N"**.

**Regole per ogni task**
- Prima di toccare il codice, leggere `LEGGIMI.md` e i file indicati nel task.
- Nessuna cifra e nessuna frase nuova senza fonte ufficiale (regole di verifica in `LEGGIMI.md`). Le somme e le percentuali fatte da noi si dicono tali ("calcolo nostro").
- Dopo le modifiche: `py sito/costruisci.py`, controllo a 390 px (Playwright con `py`) e a 1440 px, mostrare all'utente **prima** di estendere a tutte le schede.
- Commit in italiano, senza Co-Authored-By, solo quando l'utente approva. Poi segnare il task come fatto qui sotto (`[x]` e data).
- Se il task contiene **"Da decidere"**, chiederlo all'utente all'inizio, con la raccomandazione.

File principali: `sito/comune.js` (`MONEY`, `fmtMln`), `sito/report.html` (riquadro "Soldi", righe 114–120), `sito/index.html` (riquadro `#soldi-tot`, righe 301–320), `sito/costruisci.py`, la sezione `## Soldi` di `interventi/*.md`.

**Perché i soldi oggi non si capiscono** (giro del 24/10/2026)
1. Parole da addetti: "stanziato" nelle fonti diventa allocati, assegnati, impegnati, fondi previsti, versati al Commissario.
2. Le tre caselle sembrano confrontabili ma spesso coprono cose diverse (gara 2018: 55 mln sono di tutto il programma, il pagato è per altre attività; scuole Tamburi: "vedi nota").
3. Numeri che sembrano errori: Due Mari, 5,05 mln previsti e 5,39 pagati, senza spiegazione.
4. Non si capisce di chi sono i soldi: "secondo Ilva" dice chi dà il numero, non da dove vengono i soldi.
5. Dati vecchi che non si vedono: quasi tutto il blocco A è fermo a luglio 2022.
6. Gli stessi soldi passano per più report (CUP J56J14000460001 in B13, B5, gara 2018, B11; delibera CIPE 87/2012 per Mar Piccolo, PIP Statte e molo).
7. "mln €" illeggibile per le cifre piccole ("< 0,01", "0,08").

---

## Prima parte: come si leggono le cifre (veloce)

### [x] 1. Parole da lettore e cifre in euro (fatto il 24/10/2026: le cifre di Ilva, date solo in milioni con due decimali, si scrivono "circa 90.000 €" e "meno di 10.000 €")
- Le tre caselle diventano **"Quanto costerebbe"** (oggi Stimato), **"Soldi disponibili"** (Stanziato), **"Già spesi"** (Pagato), nel report e in home.
- Una "i" accanto al titolo "Soldi" che al tocco (non solo al passaggio del mouse) spiega le tre parole in una frase ciascuna, e che "disponibili" comprende stanziati, assegnati, allocati e impegnati.
- Cifre sotto il milione in euro interi (75.751 €), sopra in milioni con due decimali (18,40 mln €). Niente più "< 0,01".
- *Da decidere:* i tre nomi (raccomandati quelli sopra; in alternativa "Costo previsto / Soldi messi a disposizione / Soldi spesi").
- Verifica: Scuole Tamburi, Land L, Gravina, gara 2018 a 390 px.

### [x] 2. Le cifre dentro la scheda, con chi le dice e quando (fatto il 24/10/2026: "dato vecchio" dopo 2 anni, "impegnati" scritti nella nota di [disponibili]; Mar Piccolo studi senza riquadro, da rivedere con i task 7–8)
- Oggi le cifre del riquadro stanno in `MONEY` dentro `comune.js`, scritte a mano e separate dalla scheda: possono non coincidere con `## Soldi`. Spostarle nella scheda: all'inizio di `## Soldi` un blocco con etichette, letto da `costruisci.py` (come "Cosa non sappiamo" e "Divieti e avvisi"), che si ferma se manca l'etichetta o la fonte. Bozza:
  ```
  - [costo] 29.812.400 € · progetto approvato · 2019 [3]
  - [disponibili] 18.400.000 € · Ilva · luglio 2022 [8] allocati per la messa in sicurezza
  - [spesi] 290.000 € · Ilva · luglio 2022 [8]
  - [spesi] non si sa · le relazioni di Ilva dopo il 2018 non danno cifre
  ```
- Sotto ogni cifra sul sito: **chi lo dice e quando** ("Ilva · lug 2022", "OpenCoesione · giu 2026", "Decreto del Commissario · ott 2026").
- Le cifre di più di due anni fa in grigio con scritto "dato vecchio".
- Aggiornare il modello in `LEGGIMI.md` e togliere `MONEY` da `comune.js`. In home i totali si fanno dalle cifre delle schede, con lo stesso risultato di oggi (controllarlo prima e dopo).
- *Da decidere:* soglia per "dato vecchio" (raccomandati 2 anni); se distinguere "impegnati" da "disponibili" con un'etichetta a parte (raccomandato di no per ora: si scrive nel testo della riga).
- Prima una scheda (Area verde nord), mostrarla, poi tutte e 25 quelle che hanno `MONEY`; per le altre 6 si vede se `## Soldi` ha cifre.

### [x] 3. Una frase sui soldi per ogni report (fatto il 24/10/2026: frase in tutte le 25 schede con cifre; caselle del riquadro allineate riga per riga)
- La riga in grassetto all'inizio di `## Soldi` (come il riassunto di "Cosa è stato fatto") dice in parole semplici quanto c'è, quanto è stato speso, cosa non si sa. Esempio: *"Ilva ha messo da parte 18,4 milioni; fino al 2022 ne aveva spesi 0,29, meno del 2% (calcolo nostro). Dopo il 2022 non si sa."* [8]
- Sul sito: in cima al riquadro "Soldi" del report e nella scheda rapida della mappa.
- Ogni frase si controlla sulle fonti della scheda, non su `MONEY`. `costruisci.py` avvisa se una scheda con cifre non ha la frase.
- Prima tre schede diverse (Area verde nord, gara 2018, Cimitero), mostrarle, poi tutte.

## Seconda parte: confronti e stranezze

### [x] 4. La barra "quanto è stato speso" (fatto il 24/10/2026: riga `[confronto] sì|no · motivo`, con `[confronto · chi]` se ci sono due righe di disponibili; barra in 15 schede, tutte con la tabella di Ilva del luglio 2022, "no" nella gara 2018)
- Nel riquadro del report una barra **Già spesi su Soldi disponibili** con la percentuale (calcolo nostro), **solo se le due cifre coprono la stessa cosa e vengono dalla stessa fonte o dallo stesso periodo**. Altrimenti niente barra e una riga col motivo ("le due cifre riguardano cose diverse", "date diverse").
- Nella scheda serve un modo per dirlo: *da decidere* fra un segno sulla riga `[spesi]` (es. `[spesi, stessa voce]`) e una riga `[confronto] sì/no: motivo` (raccomandata, perché obbliga a scrivere il motivo).
- Verifica: Area verde nord (barra bassissima), Due Mari (oltre il 100%), gara 2018 (niente barra), Cimitero.

### [x] 5. Le stranezze dette chiaramente (fatto il 24/10/2026: righe `[stranezza · tipo]` nel blocco Soldi, tipo "più del previsto" invece di "speso più del previsto" perché vale anche per impegni e divisioni; 10 righe in 6 schede: Due Mari, Cementir, gara 2018, PIP Statte, Cimitero, Scuole Tamburi; in PIP Statte nuova fonte [27], decreto n. 1/2025)
- Etichette nel riquadro "Soldi", con una frase e la fonte:
  - **speso più del previsto** (Due Mari: 5,39 pagati su 5,05 previsti, ma 5,95 impegnati);
  - **soldi usati per altro** (Mar Piccolo: i 21 milioni della Regione per togliere i fanghi con PCB, nessuna voce toglie fanghi, decreto n. 56/2026);
  - **cifre che coprono più report** (fondo di 8 mln per i suoli del Tamburi, 55 mln del programma Mar Piccolo);
  - **le fonti non concordano** (21,24 milioni contro 21; 75 milioni della delibera CIPE 87/2012).
- Nella scheda: righe `[stranezza]` nel blocco del task 2, oppure riuso dei punti `[fonti]` di "Cosa non sappiamo" che parlano di soldi. *Da decidere* (raccomandato `[stranezza]` nel blocco Soldi, perché i punti `[fonti]` hanno già il loro riquadro).
- Prima cercare nelle schede tutti i casi (grep di "impegnati", "non concord", "per altro", "tutto il programma"), elencarli all'utente, poi farli.

### [x] 6. Home: dove i soldi sono fermi (fatto il 25/10/2026: le 15 barre sono tutte "secondo Ilva", luglio 2022; nessun report di fondi pubblici ha un confronto possibile, gli 8 report sono nell'elenco con il motivo)
- Sotto i due totali un grafico a barre per report: soldi disponibili e già spesi, ordinato dalla percentuale spesa più bassa. Fondi pubblici e "secondo Ilva" in due gruppi separati, come i totali.
- Solo i report che hanno la barra del task 4; gli altri in un elenco sotto ("senza confronto possibile").
- Leggere la skill `dataviz` prima di scrivere il grafico. Sul telefono barre orizzontali con il nome sopra, niente assi illeggibili.

## Terza parte: da dove vengono i soldi

### [x] 7. L'elenco dei fondi (`fondi.md`) (fatto il 25/10/2026: 13 fondi pubblici e il Patrimonio Destinato di Ilva, 1.157 mln dall'accordo con i Riva secondo la Commissione parlamentare; delibera CIPE 87/2012 in una sezione con le quote; fondi non per la bonifica in una riga in fondo; nessuna soglia; la quota dell'1,5% del Commissario spiega, per calcolo nostro, le differenze di Cimitero, PIP e decreto n. 56)
- Un file nuovo con una sezione per ogni fondo: nome semplice, chi l'ha dato, atto (delibera, decreto, accordo), importo, per cosa doveva servire, CUP, in quali report è finito e con quanto, quanto è stato speso (con data), fonti.
- Partire da quello che c'è già nelle schede, cominciando dal Mar Piccolo, che è il caso più ingarbugliato: FSC 2007-2013 della Regione (21 mln, CIPE 87/2012), FSC 2014-2020 del Ministero (34 mln, CIPE 55/2016), poi la delibera CIPE 87/2012 intera (75,17 mln con PIP Statte e molo), il fondo di 8 mln per i suoli del Tamburi, la CIPESS 51/2025 (89,9 mln, PIP Statte), il contributo del Ministero delle Infrastrutture al Comune (1,50 mln).
- **I soldi di Ilva:** da dove vengono le cifre "secondo Ilva" (fondi di Ilva in AS, somme recuperate dai Riva, altro)? Cercarlo in una fonte ufficiale (decreti, relazioni al Parlamento, archivio MASE). Finché non c'è, sul sito resta "secondo Ilva" e la domanda va in "Cosa non sappiamo".
- Prima l'elenco dei fondi trovati, da approvare con l'utente; poi le sezioni.
- *Da decidere:* includere anche i fondi sotto una soglia (es. 100.000 €)? Raccomandato sì, se sono gli unici di un report.

### [x] 8. La pagina "Da dove vengono i soldi" (fatto il 25/10/2026: sul telefono un riquadro a fisarmonica per fondo con il percorso dato → finito in → speso; su schermo grande, al posto del diagramma a flussi e delle barre, scartati perché troppo complicati, i fondi report per report; totali in home invariati, nessun fondo contato due volte)
- `costruisci.py` legge `fondi.md` e scrive `sito/soldi.html` (più le voci in `sitemap.xml`): un riquadro per fondo con il percorso dei soldi (dato → finito in quali report → speso).
- Un disegno fondi → interventi: su schermo grande un diagramma a flussi, sul telefono un elenco a fisarmonica. Mostrare la versione 390 px prima di fare l'altra.
- Nel riquadro "Soldi" di ogni report il nome del fondo diventa un link alla pagina.
- I totali in home si controllano anche per fondo: nessun fondo contato due volte. Se il risultato cambia, farlo approvare all'utente prima di pubblicare.
- Link alla pagina dal menu e dal riquadro "Soldi" della home.

## Quarta parte: dati nuovi (ricerca)

### [x] 9. Le cifre di Ilva dopo luglio 2022 (fatto il 25/10/2026: le cifre per area più recenti sono quelle di Ilva al 28 febbraio 2023, nell'aggiornamento per l'Osservatorio del 29 marzo 2023, ora in 17 schede con Nord-Ovest, 12 mln; dopo non c'è nulla. Le relazioni semestrali dei commissari al Parlamento sul conto 6055 (Doc. XXVII) danno i pagamenti di Ilva "per attività di Decontaminazione" in tutto, non per area, i 250 mln ad Acciaierie d'Italia del 2025 (DL 3/2025) e quanto resta del Patrimonio Destinato: 133,4 mln a giugno 2025, 80,6 a dicembre 2025; tolto il punto "387,5 a marzo 2025", superato. Le relazioni del secondo semestre 2023 e del primo semestre 2024 non sono pubblicate. Le pagine "OMISSIS" delle relazioni trimestrali hanno ancora il testo nascosto: non usato. Nessuna FOIA per ora, scelta dell'utente)
- Il blocco A ha quasi solo la tabella di Ilva di luglio 2022. Cercare un resoconto più recente: online e nell'archivio MASE (relazioni dei commissari di Ilva in AS, rendiconti al Ministero, relazioni al Parlamento, Corte dei conti), come da regola delle ricerche prima delle FOIA.
- Se non c'è: una FOIA al MASE (ed eventualmente a Ilva in AS, se è tenuta a rispondere: verificarlo) per lo stato della spesa per intervento, via PEC, pacchetto in `.tmp/foia/invio/`. Mai accettare costi di ricerca.
- Le cifre nuove entrano nelle schede con data e fonte; quelle del 2022 restano come storia.

### [x] 10. I fondi pubblici aggiornati (OpenCoesione e OpenCUP) (fatto il 25/10/2026: OpenCoesione è ancora ai dati del 30 giugno 2026; nuovi il CUP J76J17000370002 dei 750.000 € dell'area vasta di Statte, impegnati nel 2021 e senza pagamenti, che dà la prima barra dei fondi pubblici (0%), le analisi del 2014–2015 dell'area vasta, 1,14 mln tutti pagati, la delibera CIPE 93/2017 e i tre pagamenti della Gravina, il costo OpenCUP di 275.192 € della Gravina e il CUP dell'intervento d'emergenza del PIP; date dell'ultimo pagamento in fondi.md; script in `.tmp/lavoro/controllo-opencoesione.py` e `controllo-opencup.py`)
- Per ogni CUP dei fondi del task 7: costo pubblico e pagamenti a oggi su OpenCoesione e OpenCUP, atti del Comune sul portale trasparenza. Aggiornare "Già spesi" con data.
- Dove i pagamenti sono fermi da anni o a 0 €, scriverlo con la data dell'ultimo pagamento.
- Ripetibile: annotare in fondo a `fondi.md` la data dell'ultimo controllo.

## Quinta parte: la pagina come analisi dei soldi (decisa il 25/10/2026)

`sito/soldi.html` diventa l'analisi dei soldi: prima quanti ce ne sono, quanti ne sono stati spesi e cosa non torna, poi da dove vengono. Deciso con l'utente: titolo **"I soldi della bonifica"** (nel menu resta "Soldi"); in home restano solo i due totali con un link; si fanno le stranezze tutte insieme e la linea del Patrimonio Destinato, "In breve" per ultimo. Ordine della pagina, uguale su telefono e computer:
1. In breve (task 14) · 2. I totali · 3. Dove i soldi sono fermi · 4. Le stranezze · 5. Quanto resta ai soldi di Ilva · 6. Report per report · 7. Fondo per fondo · 8. Cosa non sappiamo e Fonti.
Sul telefono le sezioni 1–5 sono aperte; 6, 7 e 8 a fisarmonica, così la pagina resta corta (scelta lasciata a Claude dall'utente).

### [x] 11. Titolo, totali e "Dove i soldi sono fermi" nella pagina (fatto il 25/10/2026: calcoli in `costruisci.py`, totali e barre identici a quelli che c'erano in home; pagina larga come la home; "Report per report" a fisarmonica, aperto su schermo grande)
- Titolo "I soldi della bonifica" in `<title>`, `h1`, anteprime (og) e descrizione; frase iniziale riscritta: la pagina dice quanti soldi ci sono, quanti ne sono stati spesi, cosa non torna e da dove vengono.
- Spostare dalla home a `soldi.html` i due totali (Fondi pubblici e Secondo Ilva, disponibili e già spesi, con "in N report"), la nota "Le cifre ci sono in N report", l'elenco dei report senza cifre e tutto "Dove i soldi sono fermi" (barre e "Senza confronto possibile").
- In home resta il riquadro "Soldi" con i due totali e il link "Analisi dei soldi →" (al posto di "Da dove vengono i soldi, fondo per fondo →").
- "Report per report" anche sul telefono, a fisarmonica; "Fondo per fondo" con un titolo di sezione.
- *Da decidere:* dove si fanno i calcoli. Raccomandato: in `costruisci.py`, così `soldi.html` resta statica e non carica `dati.js` (860 KB); i totali della pagina e quelli della home devono coincidere (controllarlo prima e dopo). In alternativa la pagina carica `dati.js` e `comune.js` e riusa il codice della home.
- Verifica a 390 e 1440 px.

### [x] 12. Le stranezze tutte insieme (fatto il 25/10/2026: sono 11 in 6 report, non 10; su schermo grande su due colonne)
- Una sezione con tutte le righe `[stranezza · tipo]` delle schede (oggi 10 in 6 schede: Due Mari, Cementir, gara 2018, PIP Statte, Cimitero, Scuole Tamburi), divise per i quattro tipi (più del previsto, usati per altro, più report, fonti non concordano), con il numero per tipo.
- Ogni stranezza con il report (codice e nome, link) e la frase con la sua fonte: la fonte è della scheda, quindi il numero porta alla fonte nel report (`r/<id>.html#<id>-f<n>`).
- Nessuna frase nuova: il testo è quello delle schede.

### [x] 13. Quanto resta ai soldi di Ilva (fatto il 25/10/2026: cifre ricontrollate sulle relazioni di Ilva; la riga del DL 21/2022 all'inizio del 2022 perché la data del decreto non è nelle fonti; su schermo grande il grafico è alto quanto la colonna con nota, tabella e domanda. Per il task 9: le relazioni trimestrali hanno una sezione "5. Aree Escluse di competenza Ilva" da leggere, e il punto 3 di Cosa non sappiamo in `fondi.md` va ricontrollato)
- Una linea con quanto resta del Patrimonio Destinato, dalla voce **Quanto resta** di `fondi.md`: 1.064 milioni a fine 2018 [28], 818,3 a marzo 2022 [29], 726,8 a dicembre 2022 [30], 624,2 a dicembre 2023 [31], 387,5 a dicembre 2024 [32] e a marzo 2025 [33].
- `costruisci.py` legge le cifre con data e fonte e si ferma se una cifra non ha la data o la fonte. Fra il 2019 e il 2021 non ci sono dati: il disegno deve mostrarlo (punti solo dove c'è la cifra, niente linea inventata in mezzo).
- Sul disegno: i 150 milioni spostati alla decarbonizzazione dal decreto-legge 21/2022 [2]; sotto, la domanda aperta "quanto di questo calo è andato alle bonifiche?" (Cosa non sappiamo, punto 3).
- Leggere la skill `dataviz` prima di scrivere il disegno: etichette dirette, cifre al tocco, tabella con le stesse cifre.

### [x] 14. In breve (fatto il 25/10/2026: 4 frasi approvate dall'utente; la costruzione controlla anche che "Le stranezze sono N, in M report" sia giusto)
- 3–4 frasi in cima alla pagina, scritte in una sezione nuova `## In breve` di `fondi.md`, ognuna con la sua fonte o con "calcolo nostro" (per esempio: le cifre di Ilva sono quasi tutte ferme a luglio 2022; nessun report di fondi pubblici permette il confronto fra disponibili e spesi; stranezze in N report).
- `costruisci.py` si ferma se una frase non finisce con la fonte o se la fonte non è nell'elenco. Ogni frase si controlla sulle fonti prima di mostrarla.
- Prima le frasi all'utente, poi sul sito.

## Sesta parte: appunti dell'utente sulla pagina (26/10/2026)

### [x] 15. In breve, più chiaro (fatto il 26/10/2026: per scelta dell'utente un testo discorsivo in 4 paragrafi invece delle frasi a elenco: fondi pubblici, spese di Ilva per area, Patrimonio Destinato, stranezze; cifre principali in grassetto; la costruzione controlla ogni frase e i quattro totali)
Oggi le 4 frasi sono lunghe e piene di punti e virgola: la prima comincia da quello che non sappiamo, la seconda mette insieme tre cose (un report confrontabile, uno che non torna, 6 a cui manca una cifra), nessuna dice i totali (fondi pubblici 155,41 mln disponibili e 7,17 spesi; secondo Ilva 412,46 e 48,57), "Patrimonio Destinato" non è spiegato.
- Riscrivere `## In breve` in `fondi.md`: frasi corte, una cosa per frase, prima quello che si sa (la cifra) e poi quello che manca; ogni frase con la sua fonte o con "calcolo nostro", come nel task 14.
- *Da decidere:* quali frasi. Raccomandato, nell'ordine: (1) quanti soldi ci sono e quanti ne sono stati spesi, fondi pubblici e Ilva separati; (2) dove i soldi sono più fermi (i report a 0% o quasi); (3) le stranezze, quante e in quanti report; (4) quanto resta del Patrimonio Destinato di Ilva, detto come "i soldi lasciati dai Riva per le bonifiche"; (5) le cifre di Ilva ferme a febbraio 2023. Al massimo 5 frasi.
- *Da decidere:* la cifra principale di ogni frase in grassetto? Raccomandato sì, così sul telefono si legge anche solo scorrendo.
- Le cifre dei totali in "In breve" devono essere quelle della sezione "I totali": `costruisci.py` si ferma se non coincidono (come già fa per le stranezze).
- Prima le frasi all'utente, poi sul sito. Verifica a 390 e 1440 px.

### [x] 16. "Dove i soldi sono fermi": una barra per ogni report (fatto il 26/10/2026: per scelta dell'utente le stesse barre, vuote, con "?" al posto della percentuale, in fondo al gruppo sotto "Senza confronto possibile"; su schermo grande i titoli delle due colonne su una riga comune, così il sottotitolo di destra non sfasa più le righe)
Oggi la barra c'è solo dove le due cifre si possono confrontare (D8 e i 17 report di Ilva); i 7 report di fondi pubblici in "Senza confronto possibile" (A1 Gravina, B2 Scuole Tamburi, B8 Cimitero, B9 Atleti Azzurri, B10 PIP Statte, B13 gara 2018, D1–D5 suoli Tamburi) hanno solo la frase.
- Una riga con la barra per ogni report, anche dove manca una cifra, senza inventare la percentuale: la regola del task 4 resta (percentuale solo se le due cifre riguardano la stessa cosa).
- *Da decidere:* come si disegna la barra senza confronto. Raccomandato: stessa riga degli altri, barra grigia tratteggiata con scritto "non si sa" al posto della percentuale; sotto la cifra che c'è ("750.000 € disponibili, spesi: non si sa") e il motivo di oggi in piccolo. Per la gara 2018 le due cifre, con il motivo per cui non si confrontano.
- *Da decidere:* dove vanno. Raccomandato: in fondo a ogni gruppo (Fondi pubblici, Secondo Ilva), dopo quelle con la percentuale, così l'ordine dalla più bassa resta.
- *Da decidere:* anche i report senza nessuna cifra (quelli elencati sotto "I totali")? Raccomandato no: lì non c'è niente da disegnare, restano nell'elenco.
- Leggere la skill `dataviz` prima del disegno. Mostrare 2–3 righe a 390 px prima di estenderle a tutti; poi 1440 px.

## Settima parte: dove sono finiti i soldi dei Riva (26/10/2026)

Ragionando con l'utente sul Patrimonio Destinato è venuto fuori che più della metà è stata usata per altro (calcolo nostro): dati e fonti già in `fondi.md` (voci **Per cosa**, **Usati per altro**, **Speso**, **Quanto resta**, **Da sapere**, punti 3 e 8–11 di Cosa non sappiamo, fonti [46]–[62]). Il sito non è stato ricostruito: alla prossima costruzione `soldi.html` prende i dati nuovi, quindi questo task va fatto prima di pubblicare altro.

### [x] 17. "Dove sono finiti i soldi dei Riva" (fatto il 26/10/2026: due barre in pila con la stessa scala, "come erano divisi" e "dove sono andati", giallo per gli usati per altro, a righe i 150 probabili, tratteggiato il resto al massimo di circa 444 calcolato dalla costruzione; ogni pezzo con certo/probabile/calcolo nostro e fonti, in un formato nuovo delle sotto-voci di **Per cosa** e **Usati per altro** (regola in LEGGIMI.md); per scelta dell'utente la linea ha un punto per anno, l'ultima cifra dell'anno, con i prelievi in giallo, e tutte le 17 cifre sono nella tabella; tolta dalla linea la riga del DL 21/2022; tabella dei semestri a fisarmonica, il totale 167,37 ricontrollato sulle cifre intere; In breve, terzo paragrafo a frasi corte)
L'utente vuole che il sito spieghi bene la situazione. Oggi la pagina dice solo "1.157 milioni, 150 spostati alla decarbonizzazione, 250 ad Acciaierie d'Italia, restano 80,6".
- La sezione "Quanto resta ai soldi di Ilva" di `sito/soldi.html` diventa "Dove sono finiti i soldi dei Riva", in tre parti: (1) **come erano divisi** i 1.157 milioni (467 Aree escluse di Ilva, 503 decontaminazione della fabbrica, 37 sottosuolo della fabbrica, 150 decarbonizzazione) [2]; (2) **dove sono andati** (circa 550 ad Acciaierie d'Italia per far funzionare la fabbrica, di cui 150 probabili; 23,6 per la garanzia dell'AIA; 58,8 di anticipo alla gestione ordinaria non restituito; al massimo circa 444 per bonifiche e decontaminazione; 80,6 rimasti); (3) la linea **quanto resta**, ora con 17 punti, con i prelievi segnati sopra (marzo 2024, primavera 2024, gennaio–febbraio 2025).
- Ogni pezzo deve dire se è **certo** (cifra in una relazione), **probabile** (i 150 del DL 63/2024) o **calcolo nostro**; `costruisci.py` legge le cifre da `fondi.md` e si ferma se manca la fonte.
- "In breve": riscrivere il terzo paragrafo, quello del Patrimonio Destinato. Proposta: "Dei 1.157 milioni lasciati dai Riva per le bonifiche, almeno 400 sono andati ad Acciaierie d'Italia per far funzionare la fabbrica [53][40]; a fine 2025 ne restavano 80,6 [41], mentre per le Aree escluse Ilva ne aveva previsti 467 e spesi 48,57 a febbraio 2023 [39]."
- *Da decidere:* barra in pila (raccomandato: due barre una sopra l'altra, "previsti" e "dove sono andati", stessa scala) o tabella; il colore dei pezzi "usati per altro".
- *Da decidere:* dove mettere i rimborsi semestre per semestre (raccomandato: tabella a fisarmonica sotto la linea).
- Leggere la skill `dataviz` prima del disegno. Mostrare a 390 px, poi 1440 px; pubblicare solo con "pubblica".
- Quando arriva la risposta alla richiesta 72 (MIMIT), aggiornare `fondi.md` (punti 8–11 di Cosa non sappiamo) prima o dopo questo task.

## Ottava parte: una pagina in cui non perdersi (27/10/2026)

Ragionando con l'utente: la pagina è ricca ma ci si perde. Sul telefono era alta 11.338 px (circa 13 schermate), la storia più forte (i soldi dei Riva) cominciava alla nona, ogni sezione saltava fra fondi pubblici e Ilva, e tre quarti delle parole erano consultazione. Decise insieme le idee D (ordine per storia), A (titoli come domande con la risposta sotto) ed E (la consultazione in fondo, separata); fatte nella stessa chat, per scelta dell'utente.

### [x] 18. Ordine per storia, titoli come domande, consultazione in fondo (fatto il 27/10/2026: sezioni in ordine "Dove sono finiti i soldi dei Riva?", "Quanto ha speso Ilva nelle sue aree?", "Quanto è stato speso dei fondi pubblici?", "Cosa non torna?", poi "Per controllare" con report per report e fondo per fondo nella stessa pagina, perché i report puntano a `soldi.html#<fondo>`; "I totali" e "Dove i soldi sono fermi" divisi in una sezione per Ilva e una per i fondi pubblici, ognuna con i suoi due totali e le sue barre, su due colonne su schermo grande; sotto ogni titolo una risposta in evidenza calcolata dalla costruzione; sul telefono chiusi i report senza confronto e i tipi di stranezze, aperti su schermo grande; In breve riordinato come la pagina, con la prima frase del Patrimonio Destinato riscritta. Sul telefono da 11.338 a circa 9.300 px, i Riva dalla nona alla seconda schermata)

### [x] 19. Indice, cifre grandi, la tua zona, parole spiegate (fatto il 27/10/2026, nella stessa chat per scelta dell'utente: B, l'indice in alto che resta sotto la barra del sito e segna la parte in cui si è; C, In breve con le cifre grandi e il testo sotto "Leggi tutto" (le cifre grandi poi sono entrate nei riquadri del task 20); G, "Cerca la tua zona", fatto e poi tolto perché all'utente non piaceva; F, la sezione `## Parole` in `fondi.md` (5 parole con fonte: Patrimonio Destinato, Aree escluse, Acciaierie d'Italia, decontaminazione, amministrazione straordinaria), spiegate al tocco e nel riquadro "Le parole"; "impegnati" non c'è perché sta già nella "i" accanto al titolo di Ilva; barre di Ilva dopo le prime 6 a fisarmonica sul telefono. Sul telefono la pagina passa da circa 9.300 a 7.363 px)

### [x] 20. Prima di tutto, i due tipi di soldi (fatto il 27/10/2026, su richiesta dell'utente: "si deve spiegare in primis la distinzione fra Patrimonio Destinato Ilva e soldi pubblici")
- In breve si apre con una frase ("due tipi di soldi… due conti separati: sul sito li teniamo divisi e non li sommiamo mai") e due riquadri affiancati su schermo grande: i soldi dei Riva (Patrimonio Destinato di Ilva) in arancione e i fondi pubblici in blu. In ognuno: l'importo (1.157 milioni [2]; 155,41 milioni sommando i report, calcolo nostro), da dove vengono, chi li spende, chi dà le cifre, quanti report (17, tutti con le cifre; 10, di cui 8 con le cifre) e le cifre principali che portano alla loro parte. Sotto i riquadri c'erano il report con tutti e due i tipi (Gravina) e le 12 stranezze: tolti per scelta dell'utente.
- Il testo dei riquadri è in `fondi.md`, sezione `## Due tipi di soldi`, ogni riga con la fonte; "a cui lo stabilimento era stato ceduto nel 1995" ricontrollato nella relazione della Commissione parlamentare [2].
- Tolto "Cerca la tua zona" (non piaceva all'utente).
- Tolti anche "Leggi tutto" e il testo `## In breve` di `fondi.md` (con i controlli della costruzione che lo riguardavano): per l'utente non servivano più.
- Tolta dalla sezione dei Riva la tabella "I soldi per la decontaminazione, semestre per semestre" (scelta dell'utente): le cifre restano in `fondi.md` (voce **Speso** del Patrimonio Destinato, con il controllo del totale) e nel riquadro del fondo in "Per controllare".
- Spese di Ilva: al posto della fisarmonica "Le altre aree" una sola lista con una freccia sotto, che sul telefono mostra le altre 11 aree nella stessa lista (scelta dell'utente); senza JavaScript e su schermo grande la lista è tutta aperta.

### [x] 21. "Dove sono finiti i fondi pubblici?", in parallelo ai soldi dei Riva (fatto il 27/10/2026, brainstorming con l'utente, che ha scelto le tre parti consigliate)
- In `fondi.md` la voce **A che punto:** per ognuno dei 14 fondi pubblici: chi li dà e la quota di ogni report divisa per stato, ogni pezzo con la fonte; 3 fondi "non contati" con il motivo (Fondo di rotazione del Cimitero, solo su OpenCoesione; Accordo del 2004 per l'Area 170 ha, nessun atto che abbia poi dato i soldi; Piattaforma per l'area vasta, nessuna cifra per i nostri report). Scelte prudenti: i 34 milioni del Ministero per il Mar Piccolo sono "non si sa", perché OpenCoesione non dice se i 5,59 milioni pagati vengono da questi o dai 21 della Regione; i 21 della Regione sono "usati per altro" (15,78) e "senza impegni" (5,22) come dice il decreto n. 56 del 2026.
- La sezione, dopo "Quanto ha speso Ilva", ha la risposta in evidenza (circa 199 milioni, pagati 4,46, circa il 2%; circa 16 usati per altro, 42 non ancora pagati, 43 non si sa, 90 da arrivare, tutto calcolo nostro), 1. la barra per chi li dà (Ministero dell'Ambiente 133,52, Regione Puglia 63,81, Ministero delle Infrastrutture 1,50, CIS 0,30), 2. la barra per stato con i pezzi a fisarmonica, 3. una riga per quota dall'anno dei soldi a oggi (tratteggiata se ancora aperta, ✓ se spesi tutti) con una barretta dello stato. Note: perché il totale è più dei 155,41 dei report e perché i pagati sono meno dei 7,17; i fondi non contati.
- In breve, riquadro dei fondi pubblici: la cifra grande ora è la somma delle quote (circa 199 milioni) e c'è il link "Ne risultano pagati 4,46 milioni". Indice: "Fondi pubblici" porta alla sezione nuova, "Spese pubbliche" alle barre per report.
- Poi, su richiesta dell'utente: nella parte 1 ogni voce (chi dà i soldi) si apre con la freccia sui suoi fondi, con la cifra, il nome intero e i report; la parte 3 è una tabella (Quota, Dal, Anni con ✓ se spesi tutti, A che punto con la barretta e "pagati N%") al posto delle righe con la linea del tempo.
- La tabella prende tutta la larghezza della sezione e non ha più la barretta: in "A che punto" "pagati N%" e sotto, a parole, il resto della quota.

### [x] 22. Via le sezioni doppie (fatto il 27/10/2026, scelta dell'utente)
- Tolte "Quanto è stato speso dei fondi pubblici?" (le barre per report, superate da "Dove sono finiti i fondi pubblici?"), "Cosa non torna?" (le stranezze sono già nel riquadro Soldi di ogni scheda) e "Report per report" in "Per controllare" (i fondi di ogni report sono già nella scheda, riga "Da dove vengono i soldi"). Tolti anche il loro codice e il loro CSS, il link "solo in 1 degli 8 report" in In breve, le voci dell'indice e le due note che rimandavano "più sotto"; la nota sui pagati ora parla delle schede dei report.
- La pagina ora ha In breve, i soldi dei Riva, le spese di Ilva, i fondi pubblici e "Per controllare". Sul telefono circa 10.000 px.

### [x] 23. Le spese di Ilva nel riquadro dei Riva (fatto il 27/10/2026, scelta dell'utente)
- Nel riquadro "Dove sono finiti i soldi dei Riva?" la parte 3 non è più "Quanto resta" (la linea, la tabella delle 17 cifre e le note accanto): è "Quanto ha speso Ilva nelle sue aree", una tabella come quella dei fondi pubblici (Area, Disponibili, Già spesi, Spesi), dalla percentuale più bassa, con la riga del totale (17 aree, 412,46 e 48,57 milioni, circa 12%, calcolo nostro), il testo che era la risposta della sezione e la "i" con il significato delle cifre. Le domande aperte e il link al fondo restano in fondo al riquadro.
- Tolta la sezione "Quanto ha speso Ilva nelle sue aree?" (totali, barre e freccetta) e la sua voce nell'indice; il link di In breve porta alla tabella. Le cifre di "Quanto resta" restano in `fondi.md` e nel riquadro del fondo in "Per controllare"; i 80,6 milioni rimasti sono nella barra "dove sono andati".
- Tolti il codice e il CSS rimasti senza uso (linea "quanto resta", barre report per report, freccetta). La pagina ora ha In breve, i soldi dei Riva, i fondi pubblici e "Per controllare": sul telefono circa 9.900 px, a 1440 px circa 5.900.

### [x] 24. Home e pagina dei soldi con le stesse cifre (fatto il 27/10/2026, segnalato dall'utente)
- La home sommava le cifre delle schede (fondi pubblici 155,41 disponibili e 7,17 spesi; secondo Ilva 412,46 e 48,57), la pagina dei soldi ora usa le quote dei fondi: le cifre non coincidevano.
- Ora il riquadro "Soldi" della home ha i due tipi di soldi come In breve: i soldi dei Riva (1.157 milioni nel fondo, circa 632 usati per altro) e i fondi pubblici (circa 199 milioni dati per i report, 4,46 pagati, circa il 2%), con la frase "due tipi di soldi, in conti separati: non li sommiamo mai". Le cifre le scrive `costruisci.py` in `DATA.soldi`, già formattate, così non possono più essere diverse.
- Sul telefono le due tabelle (spese di Ilva per area e fondi pubblici) mostrano le prime 6 righe, più la riga del totale; una freccia sotto le apre tutte e le richiude (scelta dell'utente). Su schermo grande e senza JavaScript sono intere. Sul telefono la pagina scende a circa 8.600 px.
