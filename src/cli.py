from ai import ask_ai
from loader import list_files, filter_by_suffix, read_document, read_document_pages
from search import search_term_in_files
from embeddings import get_cached_index, find_relevant_chunks, chunk_label
from prompts import summary_prompt, qa_prompt, strip_markdown
from errors import OllamaError


def test_ai():
    answer = ask_ai(
        "V jednej vete vysvetli, čo je umelá inteligencia."
    )

    print(answer)


def filter_documents(files):
    print("\nFiltrovanie dokumentov:")
    print("1. Všetky")
    print("2. PDF")

    choice = input("Vyber možnosť: ")

    if choice == "1":
        return files

    elif choice == "2":
        return filter_by_suffix(files, [".pdf"])

    else:
        print("Neplatná možnosť!")
        return files


def select_document(files):
    print("\nVyber dokument:")

    for index, file in enumerate(files, start=1):
        print(f"{index}. {file.name}")

    choice = input("Zadaj číslo dokumentu: ")

    if not choice.isdigit():
        print("Musíš zadať číslo.")
        return None

    choice = int(choice)

    if choice < 1 or choice > len(files):
        print("Neplatné číslo dokumentu.")
        return None

    return files[choice - 1]


def show_document_content(file):
    content = read_document(file)

    if content is None:
        print("Tento typ súboru zatiaľ nevieme zobraziť.")
        return

    print(f"\nObsah dokumentu: {file.name}\n")
    print(content)


def list_documents():
    files = filter_by_suffix(list_files())

    if not files:
        print("Priečinok data je prázdny!")
        return

    files = filter_documents(files)

    if not files:
        print("Nenašli sa žiadne dokumenty pre vybraný filter.")
        return

    print("\nDostupné dokumenty:")

    for file in files:
        print(f"- {file.name}")

    selected_file = select_document(files)

    if selected_file is None:
        return

    show_document_content(selected_file)


def search_in_documents():
    files = filter_by_suffix(list_files())
    search_term = input("Zadaj hľadaný výraz: ").strip()

    matches = search_term_in_files(files, search_term)

    if not matches:
        print("Výraz sa nenašiel v žiadnom dokumente!")
        return

    for match in matches:
        print(f"\nNájdené v súbore: {match['file']}")
        print(f"Riadok {match['line_number']}")
        print(f"-> {match['text']}")


def summarize_document():
    files = filter_by_suffix(list_files())

    if not files:
        print("Priečinok data je prázdny!")
        return

    selected_file = select_document(files)

    if selected_file is None:
        return

    content = read_document(selected_file)

    if content is None:
        print("Tento typ súboru zatiaľ nevieme zhrnúť.")
        return

    if not content.strip():
        print("Dokument je prázdny alebo sa nepodarilo načítať text.")
        return

    print("\nGenerujem zhrnutie...\n")
    summary = strip_markdown(ask_ai(summary_prompt(content)))
    print(summary)


def ask_about_documents():
    question = input("Zadaj otázku k dokumentom: ").strip()

    if not question:
        print("Otázka nemôže byť prázdna.")
        return

    files = filter_by_suffix(list_files())

    index, was_rebuilt = get_cached_index(files, read_document_pages)

    if was_rebuilt:
        print("\nDokumenty zaindexované.")

    if not index:
        print("Priečinok data je prázdny alebo dokumenty sa nepodarilo načítať.")
        return

    relevant_chunks = find_relevant_chunks(index, question)

    if not relevant_chunks:
        print("Nenašli sa žiadne relevantné pasáže v dokumentoch.")
        return

    print("\nPoužité zdroje:")

    for chunk in relevant_chunks:
        print(f"\n[{chunk_label(chunk)}, skóre {chunk['score']:.2f}]")
        print(chunk['text'])

    print("\nGenerujem odpoveď...\n")

    answer = ask_ai(qa_prompt(question, relevant_chunks))
    print(answer)


def show_menu():
    print("\nBP Agent")
    print("1. Zobraziť dokumenty")
    print("2. Vyhľadať výraz")
    print("3. Test AI")
    print("4. Zhrnúť dokument")
    print("5. Opýtať sa na dokumenty")
    print("6. Ukončiť")


def main():
    while True:
        show_menu()

        choice = input("Vyber možnosť: ")

        try:
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
                print("Ukončenie programu")
                break
            else:
                print("Neplatná možnosť!")
        except OllamaError as error:
            print(f"\n{error}")
