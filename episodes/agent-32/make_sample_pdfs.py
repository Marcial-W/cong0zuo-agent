from pathlib import Path

from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject, NumberObject


def _add_text_page(writer: PdfWriter, text: str) -> None:
    page = writer.add_blank_page(width=612, height=792)
    font = DictionaryObject(
        {
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
        }
    )
    font_ref = writer._add_object(font)
    page[NameObject("/Resources")] = DictionaryObject(
        {NameObject("/Font"): DictionaryObject({NameObject("/F1"): font_ref})}
    )
    escaped = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    content = DecodedStreamObject()
    content.set_data(f"BT /F1 18 Tf 72 700 Td ({escaped}) Tj ET".encode("ascii"))
    page[NameObject("/Contents")] = writer._add_object(content)


def _add_image_only_page(writer: PdfWriter) -> None:
    page = writer.add_blank_page(width=612, height=792)
    image = DecodedStreamObject()
    image.set_data(bytes([245, 245, 245, 40, 40, 40, 245, 245, 245, 40, 40, 40]))
    image.update(
        {
            NameObject("/Type"): NameObject("/XObject"),
            NameObject("/Subtype"): NameObject("/Image"),
            NameObject("/Width"): NumberObject(2),
            NameObject("/Height"): NumberObject(2),
            NameObject("/ColorSpace"): NameObject("/DeviceRGB"),
            NameObject("/BitsPerComponent"): NumberObject(8),
        }
    )
    image_ref = writer._add_object(image)
    page[NameObject("/Resources")] = DictionaryObject(
        {NameObject("/XObject"): DictionaryObject({NameObject("/Scan"): image_ref})}
    )
    content = DecodedStreamObject()
    content.set_data(b"q 468 0 0 648 72 72 cm /Scan Do Q")
    page[NameObject("/Contents")] = writer._add_object(content)


def build_samples(output_dir: str | Path) -> dict[str, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    text_path = output / "text_pdf.pdf"
    text_writer = PdfWriter()
    _add_text_page(text_writer, "This page has an extractable text layer.")
    with text_path.open("wb") as pdf_file:
        text_writer.write(pdf_file)

    scanned_path = output / "scanned_pdf.pdf"
    scanned_writer = PdfWriter()
    _add_image_only_page(scanned_writer)
    with scanned_path.open("wb") as pdf_file:
        scanned_writer.write(pdf_file)

    mixed_path = output / "mixed_pdf.pdf"
    mixed_writer = PdfWriter()
    _add_text_page(mixed_writer, "Page one has text.")
    _add_image_only_page(mixed_writer)
    with mixed_path.open("wb") as pdf_file:
        mixed_writer.write(pdf_file)

    return {"text": text_path, "scanned": scanned_path, "mixed": mixed_path}


if __name__ == "__main__":
    for sample_type, path in build_samples(Path(__file__).with_name("samples")).items():
        print(f"{sample_type}: {path}")
