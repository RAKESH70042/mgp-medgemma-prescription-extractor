import requests


API_URL = "https://slacks-huntsman-despite.ngrok-free.dev/extract"


def extract_prescription(image_path):

    with open(image_path, "rb") as image_file:

        files = {
            "file": image_file
        }

        response = requests.post(
            API_URL,
            files=files
        )

    data = response.json()

    return data