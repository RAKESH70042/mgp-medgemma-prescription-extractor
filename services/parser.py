def parse_json(response_text):

    result = {
        "patient_name": "",
        "doctor_name": "",
        "medications": "",
        "dosage": "",
        "frequency": "",
        "duration": ""
    }

    lines = response_text.splitlines()

    for line in lines:

        if ":" in line:

            key, value = line.split(":", 1)

            key = key.strip().lower()
            value = value.strip()

            if key in result:
                result[key] = value

    return result