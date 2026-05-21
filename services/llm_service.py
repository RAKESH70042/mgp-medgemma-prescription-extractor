import requests
import os


API_URL = os.getenv("MEDGEMMA_API_URL", "https://slacks-huntsman-despite.ngrok-free.dev/extract")


def extract_prescription(image_path):

    try:

        with open(image_path, "rb") as image_file:

            files = {
                "file": (os.path.basename(image_path), image_file, "image/png")
            }

            response = requests.post(
                API_URL,
                files=files,
                timeout=120
            )

            response.raise_for_status()

        data = response.json()

        return data

    except requests.exceptions.ConnectionError:
        return {
            "error": True,
            "message": "Cannot connect to the MedGemma API. Make sure your Colab notebook is running and the Ngrok tunnel is active.",
            "hint": "Set the MEDGEMMA_API_URL environment variable with your current Ngrok URL."
        }

    except requests.exceptions.Timeout:
        return {
            "error": True,
            "message": "Request timed out after 120 seconds. The model may still be loading."
        }

    except requests.exceptions.HTTPError as e:
        return {
            "error": True,
            "message": f"API returned an error: {e.response.status_code}",
            "detail": e.response.text[:300]
        }

    except Exception as e:
        return {
            "error": True,
            "message": f"Unexpected error: {str(e)}"
        }