import easyocr


reader = easyocr.Reader(['en'], gpu=False)


def extract_text(image_path):

    results = reader.readtext(image_path)

    extracted_text = []

    for item in results:

        text = item[1]

        extracted_text.append(text)

    return "\n".join(extracted_text)