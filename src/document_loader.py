from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = (
    PROJECT_ROOT
    / "data"
    / "demo_projects"
    / "sample_echo_field"
)

SUPPORTED_EXTENSIONS = {".md", ".txt", ".pdf"}


@dataclass(slots=True)
class Document:
    content: str
    source: str
    category: str
    file_type: str


def read_text_file(file_path: Path) -> str:
    """Read a Markdown or plain-text file as UTF-8."""
    return file_path.read_text(encoding="utf-8").strip()


def read_pdf_file(file_path: Path) -> str:
    """Extract text from every page of a PDF file."""
    reader = PdfReader(file_path)
    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""

        if page_text.strip():
            pages.append(
                f"[Page {page_number}]\n{page_text.strip()}"
            )

    return "\n\n".join(pages)


def load_file(file_path: Path) -> str:
    """Load one supported file."""
    suffix = file_path.suffix.lower()

    if suffix in {".md", ".txt"}:
        return read_text_file(file_path)

    if suffix == ".pdf":
        return read_pdf_file(file_path)

    raise ValueError(f"Unsupported file type: {suffix}")


def load_documents(root_directory: Path) -> list[Document]:
    """Recursively load all supported documents from a directory."""
    if not root_directory.exists():
        raise FileNotFoundError(
            f"Data directory does not exist: {root_directory}"
        )

    documents = []

    for file_path in sorted(root_directory.rglob("*")):
        if not file_path.is_file():
            continue

        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        try:
            content = load_file(file_path)
        except Exception as error:
            raise RuntimeError(
                f"Failed to load document: {file_path}"
            ) from error

        if not content:
            print(f"Skipped empty document: {file_path.name}")
            continue

        relative_path = file_path.relative_to(root_directory)
        path_parts = relative_path.parts

        category = (
            path_parts[0]
            if len(path_parts) > 1
            else "uncategorised"
        )

        documents.append(
            Document(
                content=content,
                source=relative_path.as_posix(),
                category=category,
                file_type=file_path.suffix.lower(),
            )
        )

    return documents


def main() -> None:
    documents = load_documents(DEFAULT_DATA_DIR)

    print(f"\nLoaded {len(documents)} document(s)\n")

    for document in documents:
        print(f"Source: {document.source}")
        print(f"Category: {document.category}")
        print(f"Type: {document.file_type}")
        print(f"Characters: {len(document.content)}")
        print("-" * 50)


if __name__ == "__main__":
    main()