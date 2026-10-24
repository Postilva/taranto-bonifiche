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

### [ ] 6. Home: dove i soldi sono fermi
- Sotto i due totali un grafico a barre per report: soldi disponibili e già spesi, ordinato dalla percentuale spesa più bassa. Fondi pubblici e "secondo Ilva" in due gruppi separati, come i totali.
- Solo i report che hanno la barra del task 4; gli altri in un elenco sotto ("senza confronto possibile").
- Leggere la skill `dataviz` prima di scrivere il grafico. Sul telefono barre orizzontali con il nome sopra, niente assi illeggibili.

## Terza parte: da dove vengono i soldi

### [ ] 7. L'elenco dei fondi (`fondi.md`)
- Un file nuovo con una sezione per ogni fondo: nome semplice, chi l'ha dato, atto (delibera, decreto, accordo), importo, per cosa doveva servire, CUP, in quali report è finito e con quanto, quanto è stato speso (con data), fonti.
- Partire da quello che c'è già nelle schede, cominciando dal Mar Piccolo, che è il caso più ingarbugliato: FSC 2007-2013 della Regione (21 mln, CIPE 87/2012), FSC 2014-2020 del Ministero (34 mln, CIPE 55/2016), poi la delibera CIPE 87/2012 intera (75,17 mln con PIP Statte e molo), il fondo di 8 mln per i suoli del Tamburi, la CIPESS 51/2025 (89,9 mln, PIP Statte), il contributo del Ministero delle Infrastrutture al Comune (1,50 mln).
- **I soldi di Ilva:** da dove vengono le cifre "secondo Ilva" (fondi di Ilva in AS, somme recuperate dai Riva, altro)? Cercarlo in una fonte ufficiale (decreti, relazioni al Parlamento, archivio MASE). Finché non c'è, sul sito resta "secondo Ilva" e la domanda va in "Cosa non sappiamo".
- Prima l'elenco dei fondi trovati, da approvare con l'utente; poi le sezioni.
- *Da decidere:* includere anche i fondi sotto una soglia (es. 100.000 €)? Raccomandato sì, se sono gli unici di un report.

### [ ] 8. La pagina "Da dove vengono i soldi"
- `costruisci.py` legge `fondi.md` e scrive `sito/soldi.html` (più le voci in `sitemap.xml`): un riquadro per fondo con il percorso dei soldi (dato → finito in quali report → speso).
- Un disegno fondi → interventi: su schermo grande un diagramma a flussi, sul telefono un elenco a fisarmonica. Mostrare la versione 390 px prima di fare l'altra.
- Nel riquadro "Soldi" di ogni report il nome del fondo diventa un link alla pagina.
- I totali in home si controllano anche per fondo: nessun fondo contato due volte. Se il risultato cambia, farlo approvare all'utente prima di pubblicare.
- Link alla pagina dal menu e dal riquadro "Soldi" della home.

## Quarta parte: dati nuovi (ricerca)

### [ ] 9. Le cifre di Ilva dopo luglio 2022
- Il blocco A ha quasi solo la tabella di Ilva di luglio 2022. Cercare un resoconto più recente: online e nell'archivio MASE (relazioni dei commissari di Ilva in AS, rendiconti al Ministero, relazioni al Parlamento, Corte dei conti), come da regola delle ricerche prima delle FOIA.
- Se non c'è: una FOIA al MASE (ed eventualmente a Ilva in AS, se è tenuta a rispondere: verificarlo) per lo stato della spesa per intervento, via PEC, pacchetto in `.tmp/foia/invio/`. Mai accettare costi di ricerca.
- Le cifre nuove entrano nelle schede con data e fonte; quelle del 2022 restano come storia.

### [ ] 10. I fondi pubblici aggiornati (OpenCoesione e OpenCUP)
- Per ogni CUP dei fondi del task 7: costo pubblico e pagamenti a oggi su OpenCoesione e OpenCUP, atti del Comune sul portale trasparenza. Aggiornare "Già spesi" con data.
- Dove i pagamenti sono fermi da anni o a 0 €, scriverlo con la data dell'ultimo pagamento.
- Ripetibile: annotare in fondo a `fondi.md` la data dell'ultimo controllo.
