# Piano: verificare schede e pagine (dal giro del 30–31/10/2026)

Un task per chat. In una chat nuova basta scrivere: **"Leggi PIANO-VERIFICHE.md e fai il task N"**.

**Regole per ogni task**
- Prima di cominciare, leggere `LEGGIMI.md` (regole di verifica) e i file indicati nel task.
- Una frase si corregge solo con una fonte ufficiale in mano; se la fonte non basta, si scrive "non verificato" (regola 3) e, se il dato è importante, si prepara una bozza di richiesta di accesso agli atti.
- Una citazione "non trovata" in una scansione non è per forza sbagliata: l'OCR perde righe intere. Prima di correggerla, guardare la pagina come immagine.
- I lavori pesanti per il PC (OCR) vanno a priorità minima su un core, a meno che l'utente non dica che può andare al massimo.
- Dopo le modifiche: `py sito/costruisci.py`, controllo del sito (`py -P .tmp/lavoro/controlla_sito.py .`, deve dare 0 problemi), mostrare all'utente in locale.
- Commit in italiano, senza Co-Authored-By, solo con "pubblica"; prima del push alzare il `?v=` in `sito/index.html`, `sito/mappa.html` e `sito/report.html` se è cambiato `comune.js`, `stile.css` o `dati.js`. Poi segnare il task come fatto qui sotto (`[x]` e data).
- Se il task contiene **"Da decidere"**, chiederlo all'utente all'inizio, con la raccomandazione.

**Gli strumenti** sono in `.tmp/lavoro/` (cartella non versionata) e si lanciano con `py -P` (non `-I`, che non vede pymupdf, playwright e l'OCR):
- `controlla_cifre.py . [scheda ...] [contesto.md fondi.md]`: cifre e date di ogni frase cercate nelle fonti citate → `.tmp/controllo/cifre.md`; poi `dividi_cifre.py .` (la cifra è in un'altra fonte della scheda o in nessuna) → `.tmp/controllo/divisi.md`.
- `controlla_virgolette.py .`: citazioni tra virgolette cercate parola per parola → `.tmp/controllo/virgolette.md`; `vicine_virgolette.py .` dice quanto combaciano.
- `cerca_fonte.py . <scheda> <n|*> <regex>`: cercare a mano nel testo di una fonte.
- `controlla_sito.py . [larghezza]`, `controlla_link.py .`, `controlla.py . -v` (struttura delle schede).
- `ocr_uno.py`, `ocr_pagine.py`: OCR delle scansioni; il testo delle fonti sta in `.tmp/controllo/testi/`.
- `confronta_archivio.py <vecchia.html> <nuova.html>`: documenti nuovi nell'archivio del Ministero.

---

## Prima parte: controlli già fatti (30–31/10/2026)

### [x] 1. Cifre e date contro le fonti (fatto il 31/10/2026)
Tutte le cifre e le date delle 33 schede, della home (`contesto.md`) e della pagina dei soldi (`fondi.md`) cercate nelle fonti citate, con l'OCR dei 27 PDF scansionati e delle 120 pagine scansionate citate dei PDF misti. Nessun errore nei fatti. Corretti: "calcolo nostro" mancante (925 ettari della falda dello stabilimento, 375.252,04 € e 41,3 milioni di PIP Statte, 332.817 t dei fanghi, 48,57 milioni spesi da Ilva), la conversione dei PCB di Area Verde Ovest, alcune note (Pini [26] in PIP Statte, TAR 458 [22] in Due Mari, D.Lgs. 624/1996 [12] in Land L, Accordo per la Coesione accanto alla delibera CIPESS), i dati OpenCoesione del Cimitero salvati in `fonti/`. Pubblicato con il commit ffae5a3.

### [x] 2. Citazioni tra virgolette (fatto il 31/10/2026)
303 citazioni controllate parola per parola; rese esatte 11 citazioni che non lo erano (senso invariato). Le 29 che lo script non trova sono spiegate (righe perse dall'OCR, nomi di aree, titoli, rimandi "stesso documento del [n]"); viste come immagine Land D1 («in corso di ultimazione»), ASL su Collinette («non hanno evidenziato criticità di rilievo»), allegato della DGR 981/2024 (lettere spostate). Pubblicato con il commit ffae5a3.

### [x] 3. Le tappe di ogni area (fatto il 31/10/2026)
Controllate le 18 tappe segnate come fatte in `STEPS` e `PARTI` (`sito/comune.js`): reggono tutte su un atto di un ente di controllo, tranne l'analisi di Area Verde Ovest (A8, ARPA chiede un nuovo piano di indagini, gennaio 2026) e di Land D1 (A12, acqua sotterranea mai campionata), passate ad "a metà". Area Verde Nord e Land E restano "fatte" (ARPA ha validato terreno e acqua; i nuovi controlli servono all'analisi di rischio). Pubblicato con il commit c6883d3.

### [x] 4. Documenti nuovi, sito, link e foto (fatto il 31/10/2026)
- Archivio del Ministero: copia del 31/10 in `.tmp/mase-2026-10-31/sin7.html`, uguale a quella del 14/10 (732 righe; ultimo documento del 5/10/2026, su aree fuori dal censimento).
- Sito a 390 e 1280 px: nessun errore JavaScript, file mancante, pagina troppo larga o ancora rotta.
- Link esterni: tutti funzionanti nel browser (sentenze della giustizia amministrativa e Prefettura rispondono male solo agli script).
- Foto: le 6 di `sito/img/` hanno autore e licenza uguali a Wikimedia Commons e il sito li mostra.
- Numeri di pagina: provato in automatico (`controlla_pagine.py`), solo falsi allarmi (fonti con più intervalli di pagine, numerazione del documento invece che del PDF); lasciato perdere.

---

## Seconda parte: le frasi senza cifre, sulle schede più delicate

Le frasi come "ARPA ha validato", "il Ministero ha respinto", "secondo Ilva" non le controlla nessuno script. Si fanno solo dove un errore pesa di più. **Per ogni scheda:**
- elencare le frasi che dicono **chi ha fatto o deciso cosa** (validato, approvato, respinto, chiesto, dichiarato, archiviato, "secondo …", "scrive …");
- per ognuna aprire la fonte citata alla pagina giusta (testo o immagine) e controllare: **chi** lo dice (ente di controllo o chi fa i lavori, regola 4), **quando**, **per quale parte** dell'area, e che il verbo non dica di più della fonte (es. "approvato" quando la fonte dice "parere favorevole");
- controllare che "A che punto è" e la riga in grassetto di "Cosa è stato fatto" dicano le stesse cose delle tappe in `STEPS`;
- correggere e mostrare all'utente le frasi cambiate, prima e dopo.

### [x] 5. Stabilimento, terreno (C1, `interventi/acciaierie-italia-suoli.md`) (fatto il 2/11/2026)
La scheda con più fonti tecniche (ARPA, ISPRA, ADI) e più verbi "chi ha chiesto cosa" (piano delle indagini bocciato nel 2023, analisi di rischio mai esaminata, pavimentazioni come messa in sicurezza).
Fatto: il piano 2023 è "giudicato insufficiente" (ARPA, valutazione preliminare; ISPRA, non conforme alle linee guida), non "bocciato", e l'estensione a tutto lo stabilimento la chiede solo ARPA; il Ministero chiede di "adeguare", non di "rifare"; il Ministero "ha deciso di non esaminare" l'analisi di rischio 2016–17; ADI rivendica anche la rimozione di alcuni hot spot (non solo le pavimentazioni); la nota prot. 20001/2017 non dice di quale ente è; i "30 siti" del capitolato li dice un deputato; tolto "vinto da Ilva" dal contenzioso 2007–2016. Aggiunti la nota del Ministero del 4/7/2023, il parere "esaustiva" sul modello 3D (dicembre 2022, secondo ADI) e ATV022 (ADI lo dice ripulito, ARPA ancora inquinato). Tappe in `comune.js` ed `elenco.md` allineate. Il documento ADI DIR 339 del 25/7/2023 (fase separata) è da leggere nel task 6.

### [ ] 6. Stabilimento, falda (C2, `interventi/acciaierie-italia-falda.md`)
Pareri di ARPA e ISPRA sulla barriera dei Parchi minerali, prodotto in fase separata, "efficacia non valutabile" (2024).

### [ ] 7. Amianto dello stabilimento (C35, `interventi/amianto-stabilimento.md`)
Avanzamento dei programmi secondo ADI e secondo ISPRA, sentenze di Milano e Cassazione, tonnellate: verificare che ogni cifra dica di chi è (azienda, ISPRA, giudici).

### [ ] 8. Collinette ecologiche (A15, `interventi/collinette-ecologiche.md`)
Indagini per la Procura, misure precauzionali, piano approvato nel 2024, ordinanze sulle scuole: molte fonti scansionate (ASL, Comune).

### [ ] 9. Scuole e aree verdi del Tamburi (B2, `interventi/scuole-tamburi-aree-verdi.md`)
Analisi di rischio approvata dalla Regione nel 2016 con rischio per la falda, lavori di riqualificazione: verificare che "riqualificazione" non sia mai detta "bonifica".

### [ ] 10. Zona PIP di Statte (B10, `interventi/pip-statte.md`)
La scheda più lunga sui soldi pubblici (37 milioni del 2012, 89,9 dell'Accordo per la Coesione), con atti del Comune del 2013 scansionati.

---

## Terza parte: rifiniture e controlli periodici

### [ ] 11. Note che rimandano alla fonte sbagliata
`dividi_cifre.py` segnala circa 140 cifre che non stanno nella fonte citata ma in un'altra fonte della stessa scheda. Quasi tutte sono rumore. Fare:
- restringere l'elenco in automatico: togliere gli anni da soli, le date con intervalli ("16–18 aprile"), le fonti scansionate (OCR) e le cifre presenti anche nella fonte citata scritte in altro modo;
- per quelle rimaste, aprire le due fonti e aggiungere o cambiare la nota (di solito aggiungere la fonte giusta accanto a quella citata);
- *Da decidere:* correggere tutte le schede in un task solo, oppure solo quelle dei task 5–10 (raccomandato: tutte, sono correzioni piccole).

### [ ] 12. Controllo mensile (prossimo: fine novembre 2026)
- L'utente salva la ricerca dell'archivio del Ministero: https://bonifichesiticontaminati.mite.gov.it/ricerca/, SIN **Taranto**, **Cerca**, Ctrl+S ("Pagina web, solo HTML"; tutte le righe sono nel file anche se lo schermo ne mostra 10). Copiarla in una cartella nuova `.tmp/mase-AAAA-MM-GG/` e lanciare `confronta_archivio.py` contro la copia precedente.
- Per ogni documento nuovo di un'area del censimento: leggerlo e aggiornare la scheda (e le tappe, se cambia qualcosa).
- Cercare le relazioni trimestrali di Ilva del 2026 (oggi le schede usano al massimo il 4° trimestre 2025) e i nuovi rapporti ISPRA sullo stabilimento.
- Guardare le risposte alle richieste di accesso in scadenza (in `richieste.md`, molte tra il 25 e il 29 novembre 2026).
- Rilanciare i controlli 1 e 2 sulle schede cambiate.

### [ ] 13. Lettura da fuori (lo fa l'utente)
Il controllo che manca: se il sito **si capisce**. Far leggere a 2–3 persone che non sanno niente dell'Ilva, dal telefono:
- la home, un report (per esempio Land D1, `r/land-d1.html`) e la pagina dei soldi;
- poi chiedere: che cosa hai capito di quest'area? È bonificata? Chi deve farlo? Dove ti sei perso? Quale parola non conoscevi?
- portare le risposte in una chat: diventano task di `PIANO-SITO.md`.
