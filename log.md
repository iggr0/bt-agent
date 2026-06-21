# Zaznamnik

## 2026-06-13

### Nadstavenie projektu

- vytvorenie github repozitara
- lokalne naklonovanie repozitara
- instalacia pythonu 3.13
- vytvorenie virtualneho prostredia (.venv)
- vytvorenie python suboru (main.py)

### Poznamky

- venv je modul, ktory vytvori izolovane python prostredie pre jeden konkretny projekt, aby sa kniznice a nastavenia jednotlivych projektov navzajom neovplyvnovali
- Path() sluzi na pracu s cestami, kde chceme nieco hladat
- file.suffix umoznuje zistit typ suboru
- enumerate() na ziskanie cisla riadku
- pouzitie kniznice pypdf
- 

### Architektura projektu

 - vytvorenie agenta, ktory bude pomahat pri tvorbe bakalarskej prace

 #### Funkcionality
 - odpovedat na otazky nad PDF dokumentmi
 - sumarizovat odborne clanky
 - vyhladavat informacie v nahranych zdrojoch - filtrovanie podla formatov
 - pomahat s tvorbou osnovy bakalarskej prace
 - navrhovat otazky na obhajobu
 - upozornovat na chybajuce citacie
 - vysvetlovat odborne pojmy

 #### Casti systemu

 - uzivatelske rozhranie
    - tu prebieha komunikacia s agentom, uzivatel zadava otazky, agent mu dava odpovede 
 - logika agenta
    - spracovanie poziadaviek od uzivatela
    - rozhodne sa, ake kroky vykona
    - komunikuje s uzivatelom
 - cerpanie informacii
    - obsahuje vlozene pdf, clanky, poznamky, zdroje z ktorych vyhladava odpovede
- AI model
    - generuje odpovede na zaklade vyhladanych informacii zo zdrojov
    - pomaha s analyzou, sumarizaciou a vysvetlovanim obsahu

#### Tok dat

- pouzivatel -> UI -> logika agenta -> zdroje agenta -> AI model -> vysledna odpoved uzivatelovi

#### Roadmap

![alt text](roadmap.png)


### Problemy a riesenia

#### Aktivacia virtualneho prostredia

Problem:
PowerShell odmietol spustit Activate.ps1.

Riesenie:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

### Dokoncene

- vytvorenie hlavneho menu
- nacitanie dokumentov z priecinka
- filtrovanie dokumentov
- vyber konkretneho dokumentu
- zobrazenie obsahu dokumentu
- podpora pdf dokumentov
- vyhladavanie vyrazu v dokumentoch
- zobrazenie cisla riadku s najdenym vyrazom

## 2026-06-21

### Refaktor

- rozdelenie `main.py` do modulov: `loader.py` (citanie suborov), `search.py`
  (presne vyhladavanie), `ai.py` (komunikacia s Ollama), `cli.py` (terminalove UI)
- `main.py` zostal len ako vstupny bod programu

### Semanticke vyhladavanie (RAG)

- nahradenie keyword matchingu (presny vyskyt slova v riadku) semantickym
  vyhladavanim cez embeddings
- stiahnuty lokalny model `nomic-embed-text` cez Ollama
- novy modul `embeddings.py`: chunkovanie dokumentov (po stranach pri pdf),
  vypocet embeddings, cosine similarity, vyber najrelevantnejsich pasazi
- odstranena povodna funkcia `find_relevant_lines` (nahradena embeddings pristupom)

### Citacie

- `loader.read_document_pages()` cita pdf po stranach, aby sa dalo citovat
  presne cislo strany
- chunky v `embeddings.py` nesu cislo strany (pri pdf) alebo poradie casti
  (pri txt/md) - `chunk_label()` z toho zostavi citaciu
- prompt pre AI explicitne ziada uviest citaciu zdroja pri kazdom tvrdeni

### Optimalizacia a osetrenie chyb

- `get_cached_index()` - embeddings sa prepocitavaju len ak sa zmenili
  subory v `data/` (podla mena, velkosti a casu upravy), nie pri kazdej otazke
- nova vynimka `OllamaError` (`errors.py`) - chyby pri komunikacii s Ollama
  (chat aj embed) sa zachytavaju a zobrazia ako zrozumitelna sprava, program
  nepadne
- `loader.py` - poskodeny/necitatelny subor sa preskoci (vrati `None`)
  namiesto padu programu
- pridany `requirements.txt` (ollama, pypdf)

### Poznamky

- ollama.embed() vrati 768-rozmerovy vektor pre kazdy text, vie spracovat aj
  list textov naraz (batch)
- cosine similarity meria, ako podobny je vyznam dvoch textov - nezavisi od
  toho, ci sa pouzivaju presne tie iste slova

### Dokoncene

- modularna architektura (loader/search/ai/cli/embeddings/errors)
- semanticke vyhladavanie nad dokumentmi s citaciami (subor + strana)
- cachovanie embeddings indexu
- zakladne osetrenie chyb (Ollama nedostupna, poskodeny subor)
- requirements.txt

