import math
from ollama import embed

EMBED_MODEL = "nomic-embed-text"
CHUNK_SIZE = 200
CHUNK_OVERLAP = 40


def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    words = text.split()
    chunks = []

    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])

        if chunk.strip():
            chunks.append(chunk)

        if end >= len(words):
            break

        start = end - overlap

    return chunks


def embed_texts(texts):
    response = embed(model=EMBED_MODEL, input=texts)
    return response["embeddings"]


def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)


def build_chunks(files, read_document_pages):
    chunks = []

    for file in files:
        pages = read_document_pages(file)

        if not pages:
            continue

        for page_number, page_text in pages:
            if not page_text:
                continue

            for chunk_index, text in enumerate(chunk_text(page_text)):
                chunks.append({
                    "file": file.name,
                    "page": page_number,
                    "chunk_index": chunk_index,
                    "text": text
                })

    return chunks


def chunk_label(chunk):
    if chunk["page"] is not None:
        return f"{chunk['file']}, strana {chunk['page']}"

    return f"{chunk['file']}, cast {chunk['chunk_index']}"


def build_index(files, read_document_pages):
    chunks = build_chunks(files, read_document_pages)

    if not chunks:
        return []

    vectors = embed_texts([chunk["text"] for chunk in chunks])

    for chunk, vector in zip(chunks, vectors):
        chunk["embedding"] = vector

    return chunks


def find_relevant_chunks(index, question, top_k=5):
    if not index:
        return []

    question_vector = embed_texts([question])[0]

    scored = [
        {**chunk, "score": cosine_similarity(chunk["embedding"], question_vector)}
        for chunk in index
    ]

    scored.sort(key=lambda chunk: chunk["score"], reverse=True)

    return scored[:top_k]
