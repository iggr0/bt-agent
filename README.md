# bt-agent

AI agent, ktory pomaha pri tvorbe bakalarskej prace. Analyzuje vlozene dokumenty
(.pdf, .txt, .md), umoznuje sa na ne pytat, sumarizovat ich obsah a vyhladavat
v nich vyrazy. Odpovede na otazky su podlozene citaciami zdroja (subor + strana).

Bezi lokalne - na generovanie odpovedi a embeddings pouziva lokalne modely cez
[Ollama](https://ollama.com), ziadne data sa neodosielaju do externych sluzieb.

## Funkcionalita

- zobrazenie a filtrovanie dokumentov v priecinku `data/`
- vyhladavanie presneho vyrazu v dokumentoch
- sumarizacia jednotlivych dokumentov
- odpovedanie na otazky nad obsahom dokumentov (RAG - semanticke vyhladavanie
  cez embeddings + citacia zdroja pri kazdom tvrdeni)

## Pozadovane nastroje

- Python 3.13+
- [Ollama](https://ollama.com) bezuca lokalne, s nainstalovanymi modelmi:
  - `qwen3:8b` - generovanie odpovedi
  - `nomic-embed-text` - embeddings pre semanticke vyhladavanie

```
ollama pull qwen3:8b
ollama pull nomic-embed-text
```

## Instalacia

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Pouzitie

Dokumenty (`.pdf`, `.txt`, `.md`) vloz do priecinka `data/`, potom spusti
program z korenoveho priecinka projektu:

```
python src/main.py
```

Program zobrazi menu s dostupnymi akciami (zobrazenie dokumentov, vyhladavanie,
sumarizacia, otazky nad dokumentmi).

## Struktura projektu

```
src/
  loader.py      - citanie suborov z data/ (.pdf, .txt, .md)
  search.py      - presne vyhladavanie vyrazu v dokumentoch
  embeddings.py  - chunkovanie, embeddings, semanticke vyhladavanie (RAG)
  ai.py          - komunikacia s lokalnym LLM (Ollama)
  errors.py      - vlastne vynimky
  cli.py         - terminalove uzivatelske rozhranie
  main.py        - vstupny bod programu
data/            - vlozene dokumenty
```
