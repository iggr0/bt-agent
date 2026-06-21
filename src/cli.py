from ai import ask_ai
from loader import list_files, filter_by_suffix, read_document
from search import search_term_in_files, find_relevant_lines


def test_ai():
    answer = ask_ai(
        "V jednej vete vysvetli, co je umela inteligencia."
    )

    print(answer)


def filter_documents(files):
    print("\nFiltrovanie dokumentov:")
    print("1. Vsetky")
    print("2. PDF")

    choice = input("Vyber moznost: ")

    if choice == "1":
        return files

    elif choice == "2":
        return filter_by_suffix(files, [".pdf"])

    else:
        print("Neplatna moznost!")
        return files


def select_document(files):
    print("\nVyber dokument:")

    for index, file in enumerate(files, start=1):
        print(f"{index}. {file.name}")

    choice = input("Zadaj cislo dokumentu: ")

    if not choice.isdigit():
        print("Musis zadat cislo.")
        return None

    choice = int(choice)

    if choice < 1 or choice > len(files):
        print("Neplatne cislo dokumentu.")
        return None

    return files[choice - 1]


def show_document_content(file):
    content = read_document(file)

    if content is None:
        print("Tento typ suboru zatial nevieme zobrazit.")
        return

    print(f"\nObsah dokumentu: {file.name}\n")
    print(content)


def list_documents():
    files = filter_by_suffix(list_files())

    if not files:
        print("Priecinok data je prazdny!")
        return

    files = filter_documents(files)

    if not files:
        print("Nenasli sa ziadne dokumenty pre vybrany filter.")
        return

    print("\nDostupne dokumenty:")

    for file in files:
        print(f"- {file.name}")

    selected_file = select_document(files)

    if selected_file is None:
        return

    show_document_content(selected_file)


def search_in_documents():
    files = filter_by_suffix(list_files())
    search_term = input("Zadaj hladany vyraz: ").strip()

    matches = search_term_in_files(files, search_term)

    if not matches:
        print("Vyraz sa nenasiel v ziadnom dokumente!")
        return

    for match in matches:
        print(f"\nNajdene v subore: {match['file']}")
        print(f"Riadok {match['line_number']}")
        print(f"-> {match['text']}")


def summarize_document():
    files = filter_by_suffix(list_files())

    if not files:
        print("Priecinok data je prazdny!")
        return

    selected_file = select_document(files)

    if selected_file is None:
        return

    content = read_document(selected_file)

    if content is None:
        print("Tento typ suboru zatial nevieme zhrnut.")
        return

    if not content.strip():
        print("Dokument je prazdny alebo sa nepodarilo nacitat text.")
        return

    prompt = f"""
Zhrn nasledujuci dokument po slovensky.
Zameraj sa na hlavne myslienky, dolezite pojmy a prakticky vyznam.

Dokument:
{content}
"""

    print("\nGenerujem zhrnutie...\n")
    summary = ask_ai(prompt)
    print(summary)


def ask_about_documents():
    question = input("Zadaj otazku k dokumentom: ").strip()

    if not question:
        print("Otazka nemoze byt prazdna.")
        return

    files = filter_by_suffix(list_files())
    relevant_lines = find_relevant_lines(files, question)

    if not relevant_lines:
        print("Nenasli sa ziadne relevantne pasaze v dokumentoch.")
        return

    print("\nPouzite zdroje:")

    for item in relevant_lines[:5]:
        print(f"\n[{item['file']}, riadok {item['line_number']}]")
        print(item['text'])

    context = ""

    for item in relevant_lines[:10]:
        context += f"Subor: {item['file']}, riadok {item['line_number']}\n"
        context += f"{item['text']}\n\n"

    prompt = f"""
Odpovedz na otazku pouzivatela iba na zaklade nasledujucich pasazi z dokumentov.

Otazka:
{question}

Pasaze:
{context}

Odpovedz po slovensky. Ak odpoved z pasazi nevyplyva, napis, ze v dokumentoch nie je dostatok informacii.
"""

    print("\nGenerujem odpoved...\n")

    answer = ask_ai(prompt)
    print(answer)


def show_menu():
    print("\nBP Agent")
    print("1. Zobrazit dokumenty")
    print("2. Vyhladat vyraz")
    print("3. Test AI")
    print("4. Zhrnut dokument")
    print("5. Opytat sa na dokumenty")
    print("6. Ukoncit")


def main():
    while True:
        show_menu()

        choice = input("Vyber moznost: ")

        if choice == "1":
            list_documents()
        elif choice == "2":
            search_in_documents()
        elif choice == "3":
            test_ai()
        elif choice == "4":
            summarize_document()
        elif choice == "5":
            ask_about_documents()
        elif choice == "6":
            print("Ukoncenie programu")
            break
        else:
            print("Neplatna moznost!")
