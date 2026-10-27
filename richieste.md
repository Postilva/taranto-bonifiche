# Richieste di accesso agli atti (FOIA)

Le richieste che abbiamo inviato agli enti per le aree del censimento, con solo i dati che possono andare sul sito: `sito/costruisci.py` legge questo file e le mostra nel report di ogni area ("Cosa abbiamo chiesto") e in home.

**Regole**
- Niente nomi di funzionari, indirizzi email o PEC, note interne: quelli stanno solo in `.tmp/foia/REGISTRO.md`, che il sito non legge.
- Si aggiorna a mano quando cambia il registro (richiesta nuova o inviata di nuovo).
- **Aree**: i codici di `elenco.md`, separati da virgole. Una richiesta che parla di più aree con domande diverse ha una riga per ogni gruppo di aree, con lo stesso numero.
- **A chi**: l'ente con la preposizione ("alla Regione Puglia"), perché sul sito la frase è "Il … abbiamo chiesto <a chi> <cosa>".
- **Cosa abbiamo chiesto**: in parole semplici, minuscolo all'inizio, senza punto finale.
- **Inviata il**: il giorno da cui l'ente ha 30 giorni per rispondere (per le richieste mandate di nuovo via PEC, il giorno della consegna della PEC). **Risposta entro**: la scadenza del registro.
- Le risposte non vanno ancora sul sito (deciso il 23/10/2026): si aggiungeranno quando saranno arrivate tutte. Intanto, quando un documento arriva, il dato entra nella scheda con la sua fonte.

| N. | Aree | A chi | Cosa abbiamo chiesto | Inviata il | Risposta entro |
|---|---|---|---|---|---|
| 01 | B10 | al Commissario straordinario per la bonifica di Taranto | quanto è stato speso per i primi interventi, se la messa in sicurezza d'emergenza è finita, chi attua il nuovo intervento, da dove vengono i fondi e con quali tempi, e chi ha inquinato | 15/10/2026 | 14/11/2026 |
| 02 | B10 | al Comune di Statte | se la messa in sicurezza d'emergenza è finita, il programma dei lavori, la nuova progettazione e le misure dell'aria e dei gas del sottosuolo dopo il 2020 | 15/10/2026 | 14/11/2026 |
| 03 | A15 | alla Regione Puglia | il piano delle analisi approvato e i documenti che lo accompagnano, quando partono le indagini, i controlli della falda dal 2024 e la richiesta di far entrare le collinette nel SIN | 15/10/2026 | 14/11/2026 |
| 04 | A15 | ad ARPA Puglia | le analisi del 2018–2019, il suo parere sull'analisi di rischio del 2021, i controlli della falda, l'inizio delle analisi complete e le misure dell'aria nelle scuole vicine e dopo l'incendio del 2024 | 08/10/2026 | 07/11/2026 |
| 05 | B2 | al Commissario straordinario per la bonifica di Taranto | i risultati delle analisi, l'analisi di rischio e i pagamenti e la chiusura dei lavori | 15/10/2026 | 14/11/2026 |
| 06 | B2 | alla Regione Puglia | la determinazione n. 145 del 2016, i dati delle analisi e lo stato della pratica | 15/10/2026 | 14/11/2026 |
| 58 | B2 | ad ARPA Puglia | la validazione e i risultati delle analisi dei terreni, il suo parere sull'analisi di rischio e i controlli dopo il 2016 | 20/10/2026 | 19/11/2026 |
| 07 | B9 | al Comune di Taranto | le prime analisi, le analisi complete, l'atto che ha chiuso l'impianto e il progetto dei lavori | 15/10/2026 | 14/11/2026 |
| 08 | B9 | al Commissario straordinario per la bonifica di Taranto | i pagamenti, l'inizio e i risultati dei lavori e gli atti che li hanno preparati | 15/10/2026 | 14/11/2026 |
| 09 | B8 | al Commissario straordinario per la bonifica di Taranto | quanto è inquinato il terreno, la messa in sicurezza d'emergenza, dove è finita la terra scavata, le spese, il progetto aggiornato e i fondi | 15/10/2026 | 14/11/2026 |
| 10 | B8 | al Comune di Taranto | i divieti di accesso, le analisi, le analisi complete del 2013 e le misure per proteggere chi lavora nel cimitero e chi lo visita | 15/10/2026 | 14/11/2026 |
| 11 | A8 | al Comune di Statte | l'ordinanza sui rifiuti, i rifiuti ancora presenti, di chi è il terreno vicino, la recinzione e i controlli | 15/10/2026 | 14/11/2026 |
| 12 | A8 | ad ARPA Puglia | la validazione delle analisi del 2022, i nuovi pozzi di controllo, l'acqua sotterranea, le nuove indagini, i rifiuti e gli accessi | 08/10/2026 | 07/11/2026 |
| 13 | A9 | ad ARPA Puglia | il piano dei controlli, i nuovi pozzi di controllo, l'acqua sotterranea, fin dove arriva l'inquinamento, i rifiuti e gli accessi | 09/10/2026 | 08/11/2026 |
| 14 | A9 | al Comune di Statte | a cosa è destinata l'area, i rifiuti abbandonati, la recinzione e i pozzi di controllo | 15/10/2026 | 14/11/2026 |
| 15 | A2 | alla Regione Puglia | la garanzia che Ilva deve dare per i lavori, l'autorizzazione per il bosco e l'inizio dei lavori | 15/10/2026 | 14/11/2026 |
| 16 | A2 | ad ARPA Puglia | l'inizio dei lavori, l'acqua dentro i rifiuti, l'acqua sotterranea e la classificazione dei rifiuti | 09/10/2026 | 08/11/2026 |
| 59 | A2 | al Ministero dell'Ambiente (MASE) | la garanzia che Ilva deve dare per i lavori, l'inizio dei lavori e gli atti dopo il 19 giugno 2026 | 20/10/2026 | 19/11/2026 |
| 17 | A5, A6 | alla Provincia di Taranto | lo svuotamento del deposito, le proroghe, la garanzia e le spedizioni di fanghi all'estero | 09/10/2026 | 08/11/2026 |
| 18 | A5, A6 | ad ARPA Puglia | lo svuotamento del deposito, le analisi dei fanghi, i materiali con radioattività anomala, i campioni del 2024 e i controlli | 09/10/2026 | 08/11/2026 |
| 19 | A3, A4 | alla Provincia di Taranto | le garanzie per i controlli dopo la chiusura delle discariche, la certificazione dei lavori, gli importi e cosa cambia con il decreto-legge n. 154 del 2026 | 09/10/2026 | 08/11/2026 |
| 20 | A4 | ad ARPA Puglia | i superamenti dei limiti nella falda, la messa in sicurezza d'emergenza della falda, il piano dei controlli e i rifiuti fuori dalla nuova barriera | 09/10/2026 | 08/11/2026 |
| 34 | A3 | alla Provincia di Taranto | l'autorizzazione, i rifiuti portati in discarica, il progetto e la fine dei lavori e i controlli dopo la chiusura | 12/10/2026 | 11/11/2026 |
| 35 | A7 | alla Provincia di Taranto | i rifiuti smaltiti, la chiusura, i controlli, la garanzia e le acque piovane | 12/10/2026 | 11/11/2026 |
| 32 | A1 | al Comune di Statte | a cosa è destinata l'area, il progetto del tratto sud, l'invio al Ministero e il tratto nord | 15/10/2026 | 14/11/2026 |
| 33 | A1 | ad ARPA Puglia | l'inizio delle analisi, i risultati controllati da ARPA, la stabilità dei terrapieni e la falda profonda | 12/10/2026 | 11/11/2026 |
| 36 | A10 | ad ARPA Puglia | i rifiuti e l'amianto, l'acqua sotterranea, a cosa è destinata l'area e l'analisi di rischio | 12/10/2026 | 11/11/2026 |
| 37 | A11 | ad ARPA Puglia | i nuovi pozzi di controllo, l'acqua sotterranea nel 2025–2026 e da dove viene l'inquinamento | 12/10/2026 | 11/11/2026 |
| 38 | A12 | ad ARPA Puglia | l'acqua sotterranea, i rifiuti sepolti, l'analisi di rischio e a cosa è destinata l'area | 13/10/2026 | 12/11/2026 |
| 39 | A13 | ad ARPA Puglia | la validazione delle analisi, i nuovi pozzi di controllo e la falda, l'analisi di rischio e l'amianto | 13/10/2026 | 12/11/2026 |
| 40 | A14 | alla Regione Puglia | il piano delle analisi, il piano delle indagini preliminari, lo stato della pratica e l'autorizzazione della cava | 15/10/2026 | 14/11/2026 |
| 41 | A14 | ad ARPA Puglia | il piano delle analisi, il piano delle indagini preliminari e i sopralluoghi | 13/10/2026 | 12/11/2026 |
| 42 | A16 | al Comune di Taranto | come il Comune ha recepito l'analisi di rischio nelle regole urbanistiche, a cosa è destinata l'area e i progetti per la chiesa | 15/10/2026 | 14/11/2026 |
| 43 | A17 | alla Provincia di Taranto | la concessione del pozzo, quanta acqua si preleva e com'è, e l'impianto che dovrebbe depurarla | 13/10/2026 | 12/11/2026 |
| 44 | A17 | ad ARPA Puglia | i controlli dopo il decreto del Ministero, la validazione del 2023 e gli accessi | 13/10/2026 | 12/11/2026 |
| 45 | A18 | al Ministero delle Imprese (MIMIT) | dove si trova l'area, le verifiche ambientali, la cessione e perché è stata esclusa dalle aree date al gestore della fabbrica | 13/10/2026 | 12/11/2026 |
| 21 | B13 | al Commissario straordinario per la bonifica di Taranto | a che punto è la gara, le imprese ammesse, le spese, i fondi e i sedimenti | 15/10/2026 | 14/11/2026 |
| 22 | B13 | alla Regione Puglia | quanto è stato speso e se i fondi sono ancora validi, e i controlli | 15/10/2026 | 14/11/2026 |
| 23 | B12 | al Commissario straordinario per la bonifica di Taranto | gli accordi con la Marina Militare, il nulla osta di ISPRA, la bonifica dagli ordigni bellici, le indagini e il progetto, i soldi e i tempi, e i sedimenti | 15/10/2026 | 14/11/2026 |
| 27 | B6 | al Commissario straordinario per la bonifica di Taranto | gli accordi di collaborazione, le indagini sui sedimenti del primo seno, i risultati, la convenzione con Sogesid del 2016 e dove sono conservati i dati | 15/10/2026 | 14/11/2026 |
| 53 | D1, D2, D3, D4, D5, D6 | ad ARPA Puglia | a che punto sono, nell'anagrafe regionale dei siti da bonificare, i terreni e la falda del quartiere Tamburi | 14/10/2026 | 13/11/2026 |
| 53 | D8, D16, D17 | ad ARPA Puglia | a che punto sono, nell'anagrafe regionale dei siti da bonificare, l'area vasta di Statte e le aree di deposito UA26 e UA27 | 14/10/2026 | 13/11/2026 |
| 55 | C1, C2 | al Ministero dell'Ambiente (MASE) | le analisi dei suoli, dei materiali di riporto e della falda, la barriera che pompa l'acqua dei Parchi primari, i documenti citati ma non pubblicati, le cause in tribunale e chi deve fare la bonifica | 17/10/2026 | 16/11/2026 |
| 56 | C1, C2 | ad ARPA Puglia | i campioni di ottobre 2022, i controlli successivi, i pareri dopo febbraio 2024, i materiali di riporto e le aree fuori dal SIN | 17/10/2026 | 16/11/2026 |
| 57 | C1 | alla Provincia di Taranto | la garanzia finanziaria chiesta al gestore dal Piano ambientale del 2017, il suo importo e la situazione di oggi | 17/10/2026 | 16/11/2026 |
| 63 | D16, D17 | alla Regione Puglia | le analisi fatte sulle due aree di deposito, i pareri di ARPA e gli atti che chiudono la pratica | 21/10/2026 | 20/11/2026 |
| 63 | D3 | alla Regione Puglia | da dove nasce l'iscrizione delle aree private di SP2 nell'anagrafe dei siti da bonificare e gli atti successivi | 21/10/2026 | 20/11/2026 |
| 63 | D6 | alla Regione Puglia | l'approvazione delle analisi e dell'analisi di rischio della falda del Tamburi | 21/10/2026 | 20/11/2026 |
| 64 | D8 | alla Provincia di Taranto | l'atto del 2018 che ha chiuso la ricerca di chi ha inquinato l'area vasta di Statte e i verbali delle riunioni tecniche | 21/10/2026 | 20/11/2026 |
| 64 | D1, D2, D3, D4, D5 | alla Provincia di Taranto | i certificati di avvenuta bonifica dei sottoperimetri SP1, SP2, SP3 e SP4 | 21/10/2026 | 20/11/2026 |
| 65 | D8 | al Comune di Statte | l'analisi di rischio approvata nel 2017, le ordinanze successive e le indagini integrative da 750.000 € sulle aree agricole | 21/10/2026 | 20/11/2026 |
| 68 | B13 | alla Regione Puglia | gli atti con cui sono stati versati, usati o spostati i 21 milioni della delibera CIPE 87/2012 per il Mar Piccolo e i resoconti del Commissario | 23/10/2026 | 22/11/2026 |
| 69 | B10 | al Ministero dell'Ambiente (MASE) | da dove vengono i 34,17 milioni di "altre risorse" previsti per il nuovo intervento | 26/10/2026 | 25/11/2026 |
| 69 | B12 | al Ministero dell'Ambiente (MASE) | l'accordo del 2004 per l'Area 170 ha, l'ultimo rapporto sul suo stato e gli atti che hanno spostato o tolto i suoi 37,2 milioni | 26/10/2026 | 25/11/2026 |
| 70 | D1, D2, D3, D4, D5 | al Ministero delle Infrastrutture | la convenzione con il Comune di Taranto per la bonifica dei suoli dei sottoprogetti 1, 2 e 3 e le spese presentate dal Comune per avere il rimborso di 1,50 milioni | 26/10/2026 | 25/11/2026 |
| 71 | A1 | al Comune di Statte | la domanda di pagamento finale del progetto della bonifica della gravina, con il dettaglio dei 191.575,16 € spesi, e i conti finali del progetto | 26/10/2026 | 25/11/2026 |
| 72 | A1, A2, A3, A4, A5, A6, A7, A8, A9, A10, A11, A12, A13, A14, A15, A16, A17, A18 | al Ministero delle Imprese (MIMIT) | come sono stati usati i soldi lasciati dai Riva per le bonifiche (il Patrimonio Destinato di Ilva): i trasferimenti ad Acciaierie d'Italia, i rimborsi per la fabbrica, l'anticipo del 2019 e con quali soldi si finiranno le bonifiche delle aree di Ilva | 26/10/2026 | 25/11/2026 |
