# Piano: sistemare il sito (dal giro del 22/10/2026)

Un task per chat. In una chat nuova basta scrivere: **"Leggi PIANO-SITO.md e fai il task N"**.

**Regole per ogni task**
- Prima di toccare il codice, leggere `LEGGIMI.md` e i file indicati nel task.
- Nessuna frase nuova senza fonte ufficiale (regole di verifica in `LEGGIMI.md`).
- Dopo le modifiche: `py sito/costruisci.py`, controllo a 390 px (Playwright con `py`, perché Chrome non si restringe) e a 1440 px, mostrare all'utente **prima** di estendere a tutte le schede.
- Commit in italiano, senza Co-Authored-By, solo quando l'utente approva. Poi segnare il task come fatto qui sotto (`[x]` e data).
- Se il task contiene **"Da decidere"**, chiederlo all'utente all'inizio, con la raccomandazione.

File principali: `sito/report.html` (pagina dell'area), `sito/mappa.html`, `sito/index.html` (home e pannelli), `sito/comune.js` (STEPS, PARTI, MONEY, FASI, `cite`, `faseHtml`, `barraHtml`), `sito/costruisci.py` (legge `elenco.md` e `interventi/*.md`, scrive `sito/dati.js`). Il riassunto di un'area (quello in rosso sotto il titolo e nella lista della mappa) è la riga in grassetto all'inizio di "Cosa è stato fatto" nella scheda.

---

## Prima parte: cose che sembrano errori (veloci)

### [x] 1. Report: bollino, fase e barra, gergo (fatto il 22/10/2026)
- **Bollino "✔ verificato"** (`report.html:107`): c'è su tutti i report, quindi non distingue niente. *Da decidere:* toglierlo (raccomandato) oppure sostituirlo con "Aggiornato al …", che è già nella pagina.
- **La fase e la barra si contraddicono.** Esempio A15: la fase dice "Analisi da fare o da finire", ma nella barra Rischio e Sicurezza sono "a metà". Quando un passaggio dopo quello della fase è "a metà", aggiungere sotto la fase una riga generata dal testo dello step (es. "Rischio: Ilva ne ha fatta una, ma nessun ente l'ha approvata"). La barra deve dire perché ogni pallino è a metà anche al tocco (oggi il motivo si vede solo passandoci sopra col mouse?): verificarlo.
- **Gergo "la scheda"**: sul sito si chiama "report". Sostituire nei testi visibili: STEPS ("La scheda non ne parla" → "Le fonti non ne parlano"), MONEY ("La scheda non dà un costo stimato" → "Nessun costo stimato nelle fonti"), il piè di pagina di tutte le pagine ("dall'elenco degli interventi, dalle schede approvate…" → una frase da lettore, es. "Ogni frase viene da un documento ufficiale, citato con il suo numero [1]").
- **Coordinate UTM** nel riquadro della mappa del report (es. Tamburi "688569,3876 m E – 4484590,303 m N…"): lasciare "Posizione da documento ufficiale [n]" e spostare i numeri dentro "Dove si trova e quanto è grande" o nella fonte.
- Verifica: A15, Tamburi suoli, C2, A16 a 390 px.

### [x] 2. Tamburi: le parti dentro il report (fatto il 22/10/2026)
- Il problema: in home D5 è "Bonificata, certificato non visto", ma il report Tamburi (D1–D5 insieme) dice in cima "Analisi da fare o da finire". Il codice lo fa apposta (il report segue la parte messa peggio, `PARTI` in `comune.js`), ma chi legge vede una contraddizione.
- Fare: nel report, quando la scheda ha `PARTI`, sotto la fase generale un elenco "Parte per parte" (SP1, SP2 pubblico, SP2 private, SP3, SP4), ognuna con nome, fase e mini-barra. Se si arriva da `report.html#…` con un codice (dalla home o dalla mappa), evidenziare la parte giusta.
- Riassunti uguali: nella mappa D1–D5 hanno la stessa frase, e per D3 (aree private) "lavori fatti… nelle aree pubbliche" è fuorviante. Dare a ogni parte il suo riassunto (una riga per parte in `PARTI` o nella scheda, con fonte), usato dalla lista della mappa e dal riquadro del punto.
- Verifica: aprire D3 e D5 dalla home e dalla mappa.

### [x] 3. Codici e numeri che non tornano (fatto il 22/10/2026)
- **Codici**: il filtro "Aree di Ilva (A)" contiene C1, C2, D16, D17, e "Ricadute (B)" contiene D1–D8. *Da decidere:* (a, raccomandato) togliere la lettera dai nomi dei filtri ("Aree di Ilva", "Ricadute") e aggiungere in "Chi è nel censimento" una riga su cosa sono i codici (vengono dal nostro elenco: A = aree di Ilva in A.S., C = stabilimento di Acciaierie d'Italia, B = ricadute del Commissario, D = altre ricadute da anagrafe regionale; controllare in `elenco.md` che sia così); (b) rinumerare tutto, sconsigliato perché i codici sono nelle FOIA già inviate.
- **Numeri**: home 22 + 14 = 36, grafico 34 blocchi, schede 31. Sotto il grafico, accanto alla nota su B6, aggiungere: "A5 e A6 hanno un solo report, i cinque sottoperimetri del Tamburi uno solo". Contare dal codice, non scrivere i numeri a mano.
- Verifica: home e mappa a 390 px con i filtri.

### [x] 4. Note delle fonti più leggere (fatto il 22/10/2026)
- Frasi con 5–6 note di fila, es. "[3][4][5][6][9][13]". In `cite` (`comune.js:47`) unire le note consecutive in un solo richiamo, es. "[3–6, 9, 13]": ogni numero resta cliccabile (o il primo clic apre la lista delle fonti di quella frase). Solo visualizzazione: il testo delle schede non cambia.
- Verifica: A15 "Che posto è" a 390 px; il clic deve ancora portare alla fonte.

---

## Seconda parte: mappa

### [x] 5. Riassunti troppo corti o diversi (fatto il 22/10/2026)
- Nella lista della mappa alcuni riassunti dicono quasi niente: B8 "Non bonificato.", A15 "Non bonificate e non messe in sicurezza in modo definitivo.", B12/B13 "Né bonificato né messo in sicurezza.". Riscrivere la riga in grassetto di quelle schede con lo stesso schema delle migliori (A2, A4, A11): stato + cosa c'è di concreto, una frase, con la fonte. Solo dati già nelle schede.
- Prima elencare tutte le 31 righe e farle approvare all'utente, poi scriverle.

### [x] 6. Tamburi illeggibile sul telefono e colori per fase (fatto il 22/10/2026)
- A 390 px B2, B8, B9 e D1–D6 sono uno sopra l'altro. Raggruppare i pallini vicini (a uno zoom basso un pallino col numero, che al tocco apre l'elenco del gruppo o fa zoom), senza librerie pesanti se si può (Leaflet.markercluster da cdnjs va bene).
- Colori: oggi i pallini sono arancione/azzurro per gruppo. Aggiungere un interruttore "Colora per: gruppo / a che punto è" con i colori di FASI (gli stessi del grafico della home). *Da decidere:* quale dei due è il default (raccomandato: "a che punto è", che risponde al titolo del sito).
- Verifica: a 390 px toccare il gruppo Tamburi e aprire D3.

---

## Terza parte: cose che mancano

### [x] 7. "Cosa non sappiamo" che si capisca (fatto il 23/10/2026: 255 punti in 31 schede, 42 che bloccano; la riga 3 con la richiesta all'ente arriva col task 8)
- Oggi `costruisci.py` tiene di ogni punto solo il titolo in grassetto, e sul sito restano etichette come "Superficie.", "Da non confondere.", "Quando partono le analisi.": non sono domande, non dicono perché contano, pesano tutte uguale e non si vede se le abbiamo chieste a qualcuno.
- **Nel sito:** ogni punto diventa tre righe:
  1. la **domanda vera**;
  2. 1–2 frasi su cosa sappiamo e **perché conta**, con fonte;
  3. se c'è, la richiesta all'ente (dal task 8).

  I punti si dividono in "Cosa blocca la bonifica" e "Altre domande". Le contraddizioni tra fonti e gli avvisi ("Da non confondere", numeri diversi per la superficie) vanno in un riquadro a parte, "Le fonti non concordano". Il sottotitolo dell'accordion diventa per esempio "3 domande che bloccano la bonifica, 5 altre".
- **Nelle schede:** il grassetto di ogni punto diventa una domanda (es. "**Chi ha controllato l'analisi di rischio del 2021?**"). Accanto al numero, un'etichetta: `[blocca]`, `[altra]` o `[fonti]` (formato da decidere nel task, deve restare leggibile nel Markdown). `costruisci.py` prende la domanda e le frasi dopo, toglie **solo le frasi** con "non verificato", giornali o "bozza FOIA" (oggi toglierebbe il punto intero) e si ferma se un punto non ha l'etichetta.
- Regola nuova per `LEGGIMI.md`: quando una risposta arriva, il punto esce da "Cosa non sappiamo" e il dato entra nel racconto con la sua fonte.
- **Ordine di lavoro:** riscrivere prima i punti di A15 e Tamburi suoli e mostrarli all'utente a 390 px; poi tutte le altre schede, in gruppi da 5–6, facendo approvare le domande.
- **Da decidere:** se nel riquadro "A che punto è" mettere anche il primo dubbio che blocca, una riga sotto "Cosa manca" (raccomandato: no, "Cosa manca" lo dice già; meglio un link "Le domande aperte ↓").

### [x] 8. Le richieste di accesso agli atti nel report (fatto il 23/10/2026: `richieste.md` con 47 richieste a 8 enti, riquadro descrittivo "Cosa abbiamo chiesto" in ogni report, niente collegamento punto per punto; gli esiti si aggiungono quando saranno arrivate tutte le risposte)
- "Come lavoriamo" promette FOIA, ma nei report si vedono solo ogni tanto nel testo. Aggiungere in ogni report un riquadro "Cosa abbiamo chiesto": ente, cosa, data, scadenza, esito in parole semplici (in attesa / risposta arrivata / rifiutata / chiesto il riesame).
- **Da decidere (privacy):** `.tmp/foia/REGISTRO.md` contiene nomi di funzionari, caselle PEC e note private, quindi **non va letto dal sito**. Raccomandato: un file nuovo tracciato `richieste.md` con solo le colonne pubbliche (codice area, ente, oggetto breve, inviata il, scadenza, esito breve), aggiornato a mano quando cambia il registro; `costruisci.py` lo legge.
- Anche in home una riga: "N richieste inviate, M risposte".

### [ ] 9. I soldi in totale
- In home, sotto il grafico, un riquadro "Soldi": totale stanziato e totale pagato da `MONEY`, con **quante aree hanno il dato** ("su 12 aree con il dato") e un link alle aree senza dato. Niente totale "stimato" se mancano troppi dati. Attenzione a non sommare due volte gli stessi fondi (es. A5+A6, parti del Tamburi): controllare le spiegazioni in `MONEY` e farle approvare all'utente prima di pubblicare il numero.

### [ ] 10. Cosa è cambiato
- In home un blocco "Ultimi aggiornamenti": le 5 schede aggiornate più di recente (data "aggiornata al" già nelle schede) con una riga su cosa è cambiato. *Da decidere:* riga scritta a mano in ogni scheda (es. `*Ultima novità: …*` sotto lo stato) oppure solo nome e data (raccomandato iniziare con nome e data, zero manutenzione).

### [ ] 11. Pagine vere per i report (condivisione e Google)
- Oggi tutti i report sono `report.html#id`: su WhatsApp ogni report mostra l'anteprima generica, Google vede una pagina sola, non c'è `sitemap.xml`.
- Fare: `costruisci.py` genera anche `sito/r/<id>.html` (stesso codice di `report.html`, ma con `<title>`, `description` e `og:` dell'area scritti nella pagina), più `sitemap.xml` e `robots.txt`. I vecchi link `report.html#id` continuano a funzionare. Link interni (home, mappa) verso le pagine nuove.
- Verifica: anteprima con un debugger di og (o leggendo l'HTML), e che `report.html#collinette-ecologiche` funzioni ancora.

---

## Quarta parte: ricerca (lunga, scheda per scheda)

### [ ] 12. Cosa vale oggi per chi ci vive
- La domanda di chi abita lì ("è pericoloso? ci sono divieti?") ha risposta sparsa nel racconto. Aggiungere al report, **solo dove esiste un atto ufficiale**, una sezione breve "Divieti e avvisi in vigore" (ordinanze del Sindaco, divieti d'uso di Statte, note ASL), con data e se è ancora valido. Dove non c'è niente, non scrivere niente (o "Nessun divieto trovato negli atti": *da decidere*).
- Partire dalle schede che già citano ordinanze: A15, B2, D8, D1–D5, B10.

### [ ] 13. Il perimetro delle aree sulla mappa
- Il pallino su una foto satellitare allo zoom 18 non fa capire quanto è grande un'area di 10–100 ettari. Disegnare il perimetro solo dove c'è una planimetria ufficiale (piani di caratterizzazione Ilva, decreti MASE, anagrafe regionale), ridisegnato a mano su OpenStreetMap e marcato "perimetro indicativo da <documento> [n]".
- Una scheda alla volta, partendo dalle più grandi o più visitate; il report si apre allo zoom che contiene il perimetro.
