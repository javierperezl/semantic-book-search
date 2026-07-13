import re
from typing import Optional

# Tags administrativos/ruidosos que Open Library agrega y que no aportan
# señal semántica (ni para el embedding ni para mostrarle al usuario).
NOISE_SUBJECT_PATTERNS = [
    r"^accessible book$",
    r"^protected daisy$",
    r"^in library$",
    r"^overdrive$",
    r"^large type books?$",
    r"^lending library$",
    r"^internet archive",
    r"^open library staff picks$",
    r"^new york times bestseller",
]

_NOISE_RE = re.compile("|".join(NOISE_SUBJECT_PATTERNS), re.IGNORECASE)


def clean(text: Optional[str]) -> str:
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def clean_subjects(subjects: list[str], max_subjects: int = 8) -> list[str]:
    """
    Deduplica (case-insensitive) y filtra tags de baja señal. Corta a
    max_subjects para no inflar el prompt ni el embedding con ruido.
    """
    seen = set()
    cleaned = []

    for subject in subjects:
        subject = clean(subject)
        if not subject or _NOISE_RE.match(subject):
            continue
        key = subject.lower()
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(subject)

        if len(cleaned) >= max_subjects:
            break

    return cleaned


def build_book_profile(book: dict) -> str:
    """
    Perfil en prosa (no solo campos concatenados) para que el embedding del
    candidato tenga un estilo de texto más parecido al del query_profile,
    que también es prosa libre. Reduce la asimetría estructurada-vs-libre
    entre lo que se compara en el reranker.
    """
    subjects = clean_subjects(book.get("subjects", []))

    pieces = []

    title = clean(book.get("title"))
    author = clean(book.get("author"))

    if title:
        header = f'"{title}"'
        if author:
            header += f" by {author}"
        pieces.append(header)

    if book.get("year"):
        pieces.append(f"published in {book['year']}")

    if subjects:
        pieces.append("covering topics such as " + ", ".join(subjects))

    description = clean(book.get("description"))
    if description:
        # Recortamos para no dejar que una descripción larga domine el embedding
        pieces.append(description[:600])

    return ". ".join(pieces)


def build_query_profile(reference_book: Optional[dict], semantic_description: str) -> str:
    """
    Ancla el perfil de búsqueda en datos REALES del libro de referencia
    (cuando existe) en vez de depender únicamente de lo que el LLM
    "imaginó" en semantic_description. Si no hay libro de referencia
    (o no se encontró en Open Library), cae de vuelta a semantic_description sola.
    """
    pieces = []

    if reference_book:
        title = clean(reference_book.get("title"))
        author = clean(reference_book.get("author"))
        subjects = clean_subjects(reference_book.get("subjects", []))

        if title:
            ref = f'Similar in spirit to "{title}"'
            if author:
                ref += f" by {author}"
            pieces.append(ref)

        if subjects:
            pieces.append("which covers " + ", ".join(subjects))

    if semantic_description:
        pieces.append(clean(semantic_description))

    return ". ".join(pieces) if pieces else semantic_description
