import re

from embeddings import chunk_label

LANGUAGE_INSTRUCTION = """
Odpovedz vyhradne v spisovnej slovenčine, vrátane správnej diakritiky
(mäkčene, dĺžne - napr. č, š, ž, ť, ď, ľ, ň, á, é, í, ó, ú, ý, ä).
Aj ak su zdrojove pasaze v anglictine alebo inom jazyku, cely tvoj vystup
musi byt po slovensky - prelozi obsah, nepouzivaj anglicke ani ceske slova
ani ceske gramaticke tvary. Nemiesaj jazyky.
"""

FORMAT_INSTRUCTION = """
Pis plynulym suvislym textom, ako bezne vety. Nepouzivaj ziadne formatovanie
markdown (ziadne **, *, #, odrazky ani ciselne zoznamy). Do textu odpovede
nevkladaj citacie ani odkazy na zdroje v zatvorkach - zdroje sa zobrazia
samostatne, takze v samotnej odpovedi o nich nepisat.
"""


CITATION_PATTERN = re.compile(r"\s*\[[^\[\]]*\.(pdf|md|txt)[^\[\]]*\]")


def strip_markdown(text):
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"(?m)^\s*[*-]\s+", "", text)
    text = text.replace("**", "").replace("*", "")
    text = CITATION_PATTERN.sub("", text)
    return text.strip()


def summary_prompt(content):
    return f"""
Zhrň nasledujúci dokument.
Zameraj sa na hlavné myšlienky, dôležité pojmy a praktický význam.
{LANGUAGE_INSTRUCTION}
{FORMAT_INSTRUCTION}
Dokument:
{content}
"""


def qa_prompt(question, chunks):
    context = ""

    for chunk in chunks:
        context += f"Zdroj: {chunk_label(chunk)}\n"
        context += f"{chunk['text']}\n\n"

    return f"""
Odpovedz na otázku používateľa iba na základe nasledujúcich pasáží z dokumentov.
{LANGUAGE_INSTRUCTION}
{FORMAT_INSTRUCTION}
Otázka:
{question}

Pasáže:
{context}

Ak odpoveď z pasáží nevyplýva, napíš, že v dokumentoch nie je dostatok informácií.
"""
