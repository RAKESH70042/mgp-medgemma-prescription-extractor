from services.llm_service import extract_prescription
from services.parser import parse_json
import json
import sys


IMAGE_PATH = "fixtures/test.png"


def main():

    path = sys.argv[1] if len(sys.argv) > 1 else IMAGE_PATH

    print(f"\n📄 Processing: {path}")
    print("─" * 50)

    print("🔍 Sending to MedGemma API...")
    raw = extract_prescription(path)

    print("🧩 Parsing response...")
    parsed = parse_json(raw)

    print("\n✅ FINAL OUTPUT:\n")
    print(json.dumps(parsed, indent=2))


if __name__ == "__main__":
    main()