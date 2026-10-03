# Bonifiche Taranto — come lavoriamo

**Obiettivo:** fare chiarezza sulle bonifiche dell'ex Ilva e dell'area di Taranto, un intervento alla volta, con ogni dato verificato. Alla fine costruiremo una pagina web comprensibile anche a chi non sa nulla dell'Ilva.

**Regola d'oro: non complicare.** Pochi file, passi piccoli, e un riepilogo di 2–3 righe alla fine di ogni passo.

## File
- `elenco.md`: tutti gli interventi e il loro stato
- `interventi/<nome>.md`: una scheda per intervento
- `fonti/`: i PDF dei documenti usati, nominati `anno-mese_ente_titolo.pdf`

## Tre regole di verifica
1. **Ogni frase ha una fonte ufficiale**: Ministero, Commissario, ARPA, ISPRA, Regione, Provincia, tribunale. I giornali servono solo a trovare le fonti ufficiali.
2. **"Bonificato" si scrive solo se esiste il certificato ufficiale di avvenuta bonifica.** Altrimenti si dice cosa è stato fatto davvero, per esempio "messo in sicurezza".
3. **Se un dato non si trova, si scrive "non verificato".** Se il dato è importante, si prepara una bozza di richiesta di accesso civico (FOIA), che invia l'utente.

## Modello di scheda
```
# <Nome intervento>
*Stato scheda: bozza / approvata — aggiornata al <data>*

## In breve
(3 frasi semplici: cos'è, dov'è, a che punto è)

## Chi se ne occupa
## Cosa è stato fatto
(dire chiaramente se è "bonificato" o solo "messo in sicurezza")
## Soldi
(promessi / spesi, se si trovano)
## Date principali
## Fonti
[1] Ente, titolo, data, link — copia in fonti/<file>
## Cosa non sappiamo
(dubbi, dati mancanti, fonti che si contraddicono)
```
Ogni frase della scheda finisce con il numero della sua fonte, per esempio [1].

## Come lavorare con i PDF
Molti PDF ufficiali sono scansioni: `pdftotext` non estrae testo, quindi vanno letti come immagini, per gruppi di pagine.
