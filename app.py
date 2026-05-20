from services.ocr_service import extract_text
from services.llm_service import extract_prescription
from services.parser import parse_json


IMAGE_PATH = "fixtures/test.png"


def main():

    print("Running OCR...")

    ocr_text = extract_text(IMAGE_PATH)

    print("\nOCR TEXT:\n")
    print(ocr_text)

    print("\nRunning LLM Extraction...\n")

    response = extract_prescription(ocr_text)

    parsed = parse_json(response)

    print("\nFINAL JSON:\n")
    print(parsed)


if __name__ == "__main__":
    main()