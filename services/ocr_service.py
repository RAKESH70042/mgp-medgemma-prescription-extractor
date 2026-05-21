import easyocr
import torch


_reader = None


def get_reader():
    """Lazy-load the EasyOCR reader so startup is fast."""
    global _reader
    if _reader is None:
        use_gpu = torch.cuda.is_available()
        _reader = easyocr.Reader(['en'], gpu=use_gpu)
    return _reader


def extract_text(image_path):

    try:
        reader = get_reader()
        results = reader.readtext(image_path)
        extracted_text = [item[1] for item in results]
        return "\n".join(extracted_text)

    except FileNotFoundError:
        return ""

    except Exception as e:
        return ""