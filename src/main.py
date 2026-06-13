from pathlib import Path
from pypdf import PdfReader
from ollama import chat

def ask_ai(question):
    response = chat(
        model="qwen3:8b",
        messages=[
            {
                "role": "user",
                "content": question
            }
        ]
    )

    return response["message"]["content"]

def test_ai():
    answer = ask_ai(
        "V jednej vete vysvetli, co je umela inteligencia."
    )

    print(answer)

def read_pdf(file):
    reader = PdfReader(file)

    text = ""

    for page in reader.pages:
        text += page.extract_text()

    return text

def read_document(file):
    if file.suffix == ".pdf":
        return read_pdf(file)

    elif file.suffix in [".txt", ".md"]:
        return file.read_text(encoding="utf-8")

    else:
        return None

def search_in_documents():
    data_path = Path("data")
    files = list(data_path.iterdir()) # ziskanie zoznamu suborov v priecinku data

    search_term = input("Zadaj hladany vyraz: ").lower().strip()

    found = False

    for file in files:
        if file.suffix not in [".txt", ".md", ".pdf"]: # kontrola typu suboru
            continue

        if file.suffix == ".pdf":
            content = read_pdf(file)
        else:
            content = file.read_text(encoding="utf-8") # nacitanie obsahu suboru

        for line_number, line in enumerate(content.splitlines(), start=1): # enumerate ziska cislo riadku a obsah riadku
            if search_term in line.lower(): # kontrola, ci sa hladany vyraz nachadza v riadku
                print(f"\nNajdene v subore: {file.name}")
                print(f"Riadok {line_number}")
                print(f"-> {line.strip()}")
                found = True

    if not found:
        print("Vyraz sa nenasiel v ziadnom dokumente!")

def list_documents():
    data_path = Path("data")

    files = list(data_path.iterdir()) # 

    if not files:
        print("Priecinok data je prazdny!")
        return

    files = filter_documents(files) # nadstavenie filtra pre dokumenty pouzitim funkcie filter_documents

    if not files:
        print("Nenasli sa ziadne dokumenty pre vybrany filter.")
        return

    print("\nDostupne dokumenty:")

    for file in files:
        print(f"- {file.name}")

    selected_file = select_document(files) # vyber dokumentu pouzitim funkcie select_document

    if selected_file is None:
        return

    show_document_content(selected_file) # 

def filter_documents(files):
    print("\nFiltrovanie dokumentov:")
    print("1. Vsetky")
    print("2. PDF")

    choice = input("Vyber moznost: ")

    if choice == "1":
        return files

    elif choice == "2":
        pdf_files = []

        for file in files:
            if file.suffix == ".pdf":
                pdf_files.append(file)

        return pdf_files

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

def summarize_document():
    data_path = Path("data")
    files = list(data_path.iterdir())

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

def show_menu():
    print("\nBP Agent")
    print("1. Zobrazit dokumenty")
    print("2. Vyhladat vyraz")
    print("3. Test AI")
    print("4. Zhrnut dokument")
    print("5. Ukoncit")


def main(): # hlavna funkcia programu
    while True: # nekonecny cyklus
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
            print("Ukoncenie programu")
            break
        else:
            print("Neplatna moznost!")

if __name__ == "__main__":
    main()
