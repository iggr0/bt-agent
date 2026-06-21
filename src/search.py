from loader import read_document


def search_term_in_files(files, term):
    term = term.lower()
    matches = []

    for file in files:
        content = read_document(file)

        if content is None:
            continue

        for line_number, line in enumerate(content.splitlines(), start=1):
            if term in line.lower():
                matches.append({
                    "file": file.name,
                    "line_number": line_number,
                    "text": line.strip()
                })

    return matches
