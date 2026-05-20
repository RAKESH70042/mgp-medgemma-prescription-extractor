import gradio as gr
import json
from services.llm_service import extract_prescription


def process_image(image):

    if image is None:
        return {}

    result = extract_prescription(image)

    return result


custom_css = """
body {
    background: #f5f7fb;
}

.gradio-container {
    max-width: 1500px !important;
    margin: auto !important;
    padding-top: 10px !important;
}

.main-title {
    text-align: center;
    font-size: 42px;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 10px;
}

.sub-title {
    text-align: center;
    color: #64748b;
    font-size: 17px;
    margin-bottom: 25px;
}

.card {
    border-radius: 18px !important;
    border: 1px solid #e2e8f0 !important;
    box-shadow: 0 4px 14px rgba(0,0,0,0.05);
    background: white;
}

.json-box {
    min-height: 700px;
}

footer {
    visibility: hidden;
}

@media (max-width: 900px) {

    .main-title {
        font-size: 30px;
    }

    .sub-title {
        font-size: 14px;
    }
}
"""


with gr.Blocks(
    css=custom_css,
    theme=gr.themes.Soft(
        primary_hue="orange",
        secondary_hue="slate"
    )
) as demo:


    gr.HTML(
        """
        <div class='main-title'>
            Medical Prescription Extractor
        </div>

        <div class='sub-title'>
            Upload a prescription image to extract structured medication information.
        </div>
        """
    )


    with gr.Row(equal_height=True):


        with gr.Column(scale=1):

            with gr.Group(elem_classes="card"):

                image_input = gr.Image(
                    type="filepath",
                    label="Prescription Image",
                    height=700
                )

                with gr.Row():

                    clear_btn = gr.ClearButton(
                        value="Clear",
                        components=[image_input]
                    )

                    submit_btn = gr.Button(
                        "Extract Information",
                        variant="primary"
                    )


        with gr.Column(scale=1):

            with gr.Group(elem_classes="card"):

                json_output = gr.JSON(
                    label="Extracted Prescription (JSON)",
                    elem_classes="json-box"
                )


    submit_btn.click(
        fn=process_image,
        inputs=image_input,
        outputs=json_output
    )


if __name__ == "__main__":
    demo.launch()