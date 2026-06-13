from pathlib import Path

def list_documents():
    data_path = Path("data")

    files = list(data_path.iterdir())

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
   
    if file.suffix not in [".txt", ".md"]:
        print("Tento typ suboru zatial nevieme zobrazit.")
        return

    print(f"\nObsah dokumentu: {file.name}\n")

    content = file.read_text(encoding="utf-8")
    print(content)

def show_menu(): # vytvorenie funkcie na zobrazenie menu
    print("\nBP Agent")
    print("1. Zobrazit dokumenty")
    print("2. Ukoncit")


def main(): # hlavna funkcia programu
    while True: # nekonecny cyklus
        show_menu()

        choice = input("Vyber moznost: ")

        if choice == "1":
            list_documents()
        elif choice == "2":
            print("Ukoncenie programu")
            break
        else:
            print("Neplatna moznost!")


if __name__ == "__main__":
    main()
