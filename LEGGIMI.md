# Bonifiche Taranto — come lavoriamo

**Obiettivo:** censire le aree inquinate dall'Ilva e fare chiarezza sulla loro bonifica, un intervento alla volta, con ogni dato verificato, in una pagina web comprensibile anche a chi non sa nulla dell'Ilva.

**Cosa rientra nel censimento** (deciso il 20/10/2026):
- **aree di Ilva**: aree di Ilva in A.S. e dello stabilimento di Acciaierie d'Italia, anche fuori dal SIN;
- **ricadute fuori dalla fabbrica**: di regola solo se una fonte ufficiale dice che l'inquinamento viene (anche) dall'Ilva. Il 20/10/2026 l'utente ha messo dentro anche le 9 aree che erano "da verificare" (Tamburi B9 e D1–D6, Statte B10 e D8): dove la fonte è generale o manca, lo dice il paragrafo "Perché sono qui" in `elenco.md` e la scheda.

Tutto il resto (aree inquinate da altri, voci del Commissario che non riguardano l'inquinamento dell'Ilva) sta in `fuori-perimetro.md` e le sue schede in `interventi/fuori-perimetro/`: il sito non le legge. Prima di aprire una scheda nuova, controllare che l'area sia nel censimento.

**Regola d'oro: non complicare.** Pochi file, passi piccoli, e un riepilogo di 2–3 righe alla fine di ogni passo.

## File
- `elenco.md`: le aree inquinate dall'Ilva e il loro stato
- `fuori-perimetro.md`: le voci censite prima e uscite dal censimento
- `interventi/<nome>.md`: una scheda per intervento
- `contesto.md`: i testi della homepage (storia, come inquina, la fabbrica, glossario), con le loro fonti
- `immagini.md`: il registro delle foto in `sito/img/` (autore, licenza, link): una foto senza riga qui non va sul sito
- `fonti/`: i PDF dei documenti usati, nominati `anno-mese_ente_titolo.pdf`

## Tre regole di verifica
1. **Ogni frase ha una fonte ufficiale**: Ministero, Commissario, ARPA, ISPRA, Regione, Provincia, tribunale. I giornali servono solo a trovare le fonti ufficiali.
2. **"Bonificato" si scrive solo se esiste il certificato ufficiale di avvenuta bonifica.** Altrimenti si dice cosa è stato fatto davvero, per esempio "messo in sicurezza".
3. **Se un dato non si trova, si scrive "non verificato".** Se il dato è importante, si prepara una bozza di richiesta di accesso civico (FOIA), che invia l'utente.

## Modello di scheda
```
# <Nome intervento>
*Stato scheda: bozza / approvata — aggiornata al <data>*

**Immagine:** <file in sito/img/, facoltativa>

## In breve
(3 frasi semplici: cos'è, dov'è, a che punto è)
## Che posto è
(1–2 frasi: dov'è, quanto è grande, cosa c'è intorno)
## Perché è inquinata
(1–3 frasi: da dove viene l'inquinamento e cosa è stato trovato)

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
