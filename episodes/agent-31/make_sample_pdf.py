from pathlib import Path

from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject


SAMPLE_PAGES = [
    "A knowledge-base Agent should retrieve evidence before answering.",
    "Keep the page number so every answer can point back to its source.",
]


def build_sample_pdf(output_path: str | Path) -> Path:
    output = Path(output_path)
    writer = PdfWriter()

    font = DictionaryObject(
        {
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
        }
    )
    font_ref = writer._add_object(font)

    for text in SAMPLE_PAGES:
        page = writer.add_blank_page(width=612, height=792)
        page[NameObject("/Resources")] = DictionaryObject(
            {
                NameObject("/Font"): DictionaryObject(
                    {NameObject("/F1"): font_ref}
                )
            }
        )
        stream = DecodedStreamObject()
        escaped = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        stream.set_data(f"BT /F1 18 Tf 72 700 Td ({escaped}) Tj ET".encode("ascii"))
        page[NameObject("/Contents")] = writer._add_object(stream)

    with output.open("wb") as pdf_file:
        writer.write(pdf_file)
    return output


if __name__ == "__main__":
    print(build_sample_pdf(Path(__file__).with_name("sample_agent_notes.pdf")))
