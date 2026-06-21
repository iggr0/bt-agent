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


def find_relevant_lines(files, question):
    keywords = question.lower().split()
    relevant_lines = []

    for file in files:
        content = read_document(file)

        if content is None:
            continue

        for line_number, line in enumerate(content.splitlines(), start=1):
            line_lower = line.lower()

            for keyword in keywords:
                if keyword in line_lower:
                    relevant_lines.append({
                        "file": file.name,
                        "line_number": line_number,
                        "text": line.strip()
                    })
                    break

    return relevant_lines
