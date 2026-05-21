import gradio as gr
import json
from services.llm_service import extract_prescription
from services.parser import parse_json
from services.voice_service import transcribe_audio
from dotenv import load_dotenv
load_dotenv()

# ── helpers ───────────────────────────────────────────────────────────────────

def process_image(image):
    """Send image to MedGemma API and return structured result."""
    if image is None:
        return None, gr.update(visible=False), gr.update(visible=False)

    raw = extract_prescription(image)
    parsed = parse_json(raw)

    if isinstance(parsed, dict) and parsed.get("error"):
        return parsed, gr.update(visible=True), gr.update(visible=False)

    return parsed, gr.update(visible=False), gr.update(visible=True)


def format_medications(data):
    """Render medications list as clean HTML cards."""
    if not isinstance(data, dict):
        return ""

    meds = data.get("medications", [])
    if not meds:
        return "<p style='color:#94a3b8;font-style:italic;'>No medications extracted.</p>"

    cards = []
    for i, med in enumerate(meds):
        name = med.get("medication_name", "Unknown")
        dosage = med.get("dosage", "")
        unit = med.get("unit", "")
        freq = med.get("frequency", "")
        route = med.get("route", "")
        duration = med.get("duration", "")
        instructions = med.get("special_instructions", "")
        notes = med.get("uncertainty_notes", "")

        rows = ""
        for label, val in [
            ("Dosage", f"{dosage} {unit}".strip()),
            ("Frequency", freq),
            ("Route", route),
            ("Duration", duration),
            ("Instructions", instructions),
            ("Notes", notes),
        ]:
            if val:
                rows += f"""
                <div style="display:flex;gap:8px;padding:4px 0;border-bottom:1px solid #f1f5f9;">
                  <span style="min-width:110px;font-size:11px;font-weight:600;color:#94a3b8;text-transform:uppercase;letter-spacing:.5px;">{label}</span>
                  <span style="font-size:13px;color:#1e293b;">{val}</span>
                </div>"""

        cards.append(f"""
        <div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:16px;margin-bottom:12px;box-shadow:0 1px 4px rgba(0,0,0,.04);">
          <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
            <span style="background:#f97316;color:#fff;border-radius:50%;width:24px;height:24px;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;flex-shrink:0;">{i+1}</span>
            <span style="font-weight:700;font-size:15px;color:#0f172a;">{name}</span>
          </div>
          {rows}
        </div>""")

    return "".join(cards)


# ── CSS ───────────────────────────────────────────────────────────────────────

CSS = """
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

* { box-sizing: border-box; }

body, .gradio-container {
    font-family: 'DM Sans', sans-serif !important;
    background: #f8fafc !important;
}

.gradio-container {
    max-width: 1400px !important;
    margin: 0 auto !important;
    padding: 24px 20px !important;
}

/* header */
.rx-header {
    text-align: center;
    margin-bottom: 32px;
}
.rx-header .badge {
    display: inline-block;
    background: #fff7ed;
    color: #ea580c;
    border: 1px solid #fed7aa;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
    padding: 4px 14px;
    margin-bottom: 14px;
    letter-spacing: .5px;
}
.rx-header h1 {
    font-size: 36px;
    font-weight: 700;
    color: #0f172a;
    margin: 0 0 8px;
    line-height: 1.2;
}
.rx-header p {
    color: #64748b;
    font-size: 15px;
    margin: 0;
}

/* cards */
.panel {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,.04);
}

.panel-title {
    font-size: 13px;
    font-weight: 600;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: .8px;
    margin-bottom: 14px;
}

/* upload zone */
.upload-zone { border-radius: 12px; overflow: hidden; }

/* buttons */
.btn-extract {
    background: linear-gradient(135deg, #f97316, #ea580c) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 12px 0 !important;
    width: 100% !important;
    cursor: pointer !important;
    transition: opacity .2s !important;
    margin-top: 10px !important;
}
.btn-extract:hover { opacity: .88 !important; }

.btn-clear {
    background: #f1f5f9 !important;
    color: #475569 !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    padding: 10px 0 !important;
    margin-top: 8px !important;
    width: 100% !important;
}

/* meta row */
.meta-row {
    display: flex;
    gap: 10px;
    margin-bottom: 16px;
    flex-wrap: wrap;
}
.meta-chip {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 8px 14px;
    flex: 1;
    min-width: 120px;
}
.meta-chip .label {
    font-size: 10px;
    font-weight: 600;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: .5px;
    margin-bottom: 2px;
}
.meta-chip .value {
    font-size: 14px;
    font-weight: 600;
    color: #0f172a;
}

/* error banner */
.error-banner {
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 10px;
    padding: 14px 16px;
    color: #dc2626;
    font-size: 13px;
    line-height: 1.6;
}
.error-banner strong { display: block; margin-bottom: 4px; }

/* results section */
.results-wrapper {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

/* status dot */
.status-dot {
    display: inline-block;
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #22c55e;
    margin-right: 6px;
}

/* voice section */
.voice-badge {
    display: inline-block;
    background: #eff6ff;
    color: #2563eb;
    border: 1px solid #bfdbfe;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
    padding: 4px 14px;
    margin-bottom: 14px;
    letter-spacing: .5px;
}

footer { display: none !important; }
"""

# ── UI ────────────────────────────────────────────────────────────────────────

with gr.Blocks( title="Prescription Extractor") as demo:

    # ── Header ────────────────────────────────────────────────────────────────
    gr.HTML("""
    <div class="rx-header">
      <div class="badge">✦ Powered by MedGemma 4B</div>
      <h1>Medical Prescription Extractor</h1>
      <p>Upload a prescription image — get structured medication data in seconds.</p>
    </div>
    """)

    # ── Section 1: Prescription Image ─────────────────────────────────────────
    with gr.Row(equal_height=False):

        # LEFT: Upload
        with gr.Column(scale=1):
            gr.HTML('<div class="panel-title">Upload Prescription</div>')

            image_input = gr.Image(
                type="filepath",
                label="",
                height=420,
                elem_classes="upload-zone",
                show_label=False
            )

            extract_btn = gr.Button(
                "⬡  Extract Prescription",
                elem_classes="btn-extract"
            )

            clear_btn = gr.ClearButton(
                value="✕  Clear",
                components=[image_input],
                elem_classes="btn-clear"
            )

            gr.HTML("""
            <div style="margin-top:16px;padding:12px 14px;background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;">
              <div style="font-size:11px;font-weight:600;color:#166534;text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px;">Supported formats</div>
              <div style="font-size:13px;color:#15803d;line-height:1.6;">PNG · JPG · JPEG · WEBP · PDF screenshots</div>
            </div>
            """)

        # RIGHT: Results
        with gr.Column(scale=1):
            gr.HTML('<div class="panel-title">Extracted Data</div>')

            error_box = gr.HTML(value="", visible=False)

            with gr.Column(visible=False) as results_col:
                meta_html = gr.HTML("")
                gr.HTML('<div style="font-size:12px;font-weight:600;color:#94a3b8;text-transform:uppercase;letter-spacing:.6px;margin:4px 0 10px;">Medications</div>')
                meds_html = gr.HTML("")
                with gr.Accordion("Raw JSON output", open=False):
                    raw_json = gr.JSON(label="")

            placeholder = gr.HTML("""
            <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
                        min-height:420px;color:#cbd5e1;text-align:center;gap:12px;">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2">
                <path d="M9 12h6m-3-3v6M3 12a9 9 0 1 0 18 0 9 9 0 0 0-18 0z"/>
              </svg>
              <div style="font-size:15px;font-weight:500;">Upload an image to get started</div>
              <div style="font-size:13px;">Results will appear here</div>
            </div>
            """)

    # ── Divider ───────────────────────────────────────────────────────────────
    gr.HTML('<hr style="margin:40px 0;border:none;border-top:1px solid #e2e8f0;">')

    # ── Section 2: Voice Transcription ────────────────────────────────────────
    gr.HTML("""
    <div class="rx-header">
      <div class="voice-badge">🎙 NEW · Groq Whisper</div>
      <h1 style="font-size:28px;">Doctor–Patient Conversation</h1>
      <p>Record the conversation and get a full transcript instantly.</p>
    </div>
    """)

    with gr.Row(equal_height=False):

        # LEFT: Record
        with gr.Column(scale=1):
            gr.HTML('<div class="panel-title">Record Conversation</div>')

            audio_input = gr.Audio(
                sources=["microphone"],
                type="filepath",
                label="",
                show_label=False,
            )

            transcribe_btn = gr.Button(
                "🎙  Transcribe Conversation",
                elem_classes="btn-extract"
            )

            clear_audio_btn = gr.ClearButton(
                value="✕  Clear",
                components=[],
                elem_classes="btn-clear"
            )

            gr.HTML("""
            <div style="margin-top:16px;padding:12px 14px;background:#eff6ff;border:1px solid #bfdbfe;border-radius:10px;">
              <div style="font-size:11px;font-weight:600;color:#1e40af;text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px;">Supported audio</div>
              <div style="font-size:13px;color:#1d4ed8;line-height:1.6;">MP3 · MP4 · WAV · M4A · WEBM · OGG</div>
            </div>
            """)

        # RIGHT: Transcript
        with gr.Column(scale=1):
            gr.HTML('<div class="panel-title">Transcript</div>')

            transcript_output = gr.Textbox(
                label="",
                placeholder="Transcript will appear here after recording...",
                lines=15,
                show_label=False,
                
            )

    # ── State & Event Handlers ────────────────────────────────────────────────
    state = gr.State(None)

    def on_extract(image):
        if image is None:
            return (
                gr.update(value='<div class="error-banner"><strong>No image uploaded.</strong> Please upload a prescription image first.</div>', visible=True),
                gr.update(visible=False),
                gr.update(visible=True),
                "", "", None,
                gr.update(visible=False)
            )

        raw = extract_prescription(image)
        data = parse_json(raw)

        if isinstance(data, dict) and data.get("error"):
            msg = data.get("message", "Unknown error occurred.")
            hint = data.get("hint", "")
            html = f'<div class="error-banner"><strong>⚠ Error</strong> {msg}'
            if hint:
                html += f'<br><span style="opacity:.75">{hint}</span>'
            html += "</div>"
            return (
                gr.update(value=html, visible=True),
                gr.update(visible=False),
                gr.update(visible=False),
                "", "", None,
                gr.update(visible=False)
            )

        patient = data.get("patient_name") or "—"
        doctor = data.get("prescriber_name") or "—"
        date = data.get("prescription_date") or "—"
        model = data.get("run_metadata", {}).get("model_name", "MedGemma 4B")
        latency = data.get("run_metadata", {}).get("latency_ms", "")
        latency_str = f"{latency} ms" if latency else "—"

        meta = f"""
        <div class="meta-row">
          <div class="meta-chip"><div class="label">Patient</div><div class="value">{patient}</div></div>
          <div class="meta-chip"><div class="label">Prescriber</div><div class="value">{doctor}</div></div>
          <div class="meta-chip"><div class="label">Date</div><div class="value">{date}</div></div>
          <div class="meta-chip"><div class="label">Latency</div><div class="value">{latency_str}</div></div>
        </div>
        <div style="font-size:11px;color:#94a3b8;margin-bottom:12px;">
          <span class="status-dot"></span>Extracted via {model}
        </div>
        """

        meds = format_medications(data)

        return (
            gr.update(visible=False),
            gr.update(visible=True),
            gr.update(visible=False),
            meta, meds, data,
            gr.update(visible=False)
        )

    def on_clear():
        return (
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=True),
            "", "", None,
            gr.update(value="", visible=False)
        )

    outputs = [error_box, results_col, placeholder, meta_html, meds_html, raw_json, error_box]

    extract_btn.click(fn=on_extract, inputs=image_input, outputs=outputs)
    clear_btn.click(fn=on_clear, inputs=None, outputs=outputs)

    # Voice events
    transcribe_btn.click(fn=transcribe_audio, inputs=audio_input, outputs=transcript_output)
    clear_audio_btn.click(fn=lambda: "", inputs=None, outputs=transcript_output)


if __name__ == "__main__":
    demo.launch(css=CSS)