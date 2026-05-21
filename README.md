# 🏥 Medical Prescription Extractor

> An AI-powered web application that extracts structured medication data from handwritten or printed prescription images, and transcribes doctor–patient conversations using voice input — built for speed, accuracy, and future scalability.

---

## 📌 Table of Contents

1. [Project Overview](#-project-overview)
2. [Problems It Solves](#-problems-it-solves)
3. [Architecture Overview](#-architecture-overview)
4. [Tech Stack & Dependencies](#-tech-stack--dependencies)
5. [Environment Setup](#-environment-setup)
6. [Hardware Compatibility & Performance](#-hardware-compatibility--performance)
7. [Installation Guide](#-installation-guide)
8. [How to Run](#-how-to-run)
9. [Expected Output](#-expected-output)
10. [Project Structure](#-project-structure)
11. [Scaling Roadmap](#-scaling-roadmap)
12. [Design Notes](#-design-notes)
13. [Alternative Stack Options](#-alternative-stack-options)
14. [Safety & Privacy Notes](#-safety--privacy-notes)

---

## 🧠 Project Overview

The **Medical Prescription Extractor** is a full-stack AI prototype that solves a real-world healthcare digitization problem. It has two core modules:

### Module 1 — Prescription Image Extractor
Upload a photo of a handwritten or printed medical prescription. The system sends it to a **MedGemma 4B** vision-language model (running on a remote GPU via Google Colab + Ngrok tunnel) and returns fully structured JSON data containing:
- Patient and prescriber details
- Each medication with dosage, unit, frequency, route, duration.

### Module 2 — Doctor–Patient Voice Transcription
Record a live doctor–patient conversation directly in the browser. The audio is sent to **Groq's Whisper Large V3 Turbo** model and returned with med-gemme output as a clean, full transcript in seconds.

Both modules are wrapped in a polished **Gradio** web UI with real-time feedback, error handling.

---

## 🚨 Problems It Solves

| Problem | How This Project Solves It |
|---------|----------------------------|
| Handwritten prescriptions are hard to read | MedGemma 4B vision model reads and interprets handwriting with medical context |
| Manual prescription data entry is error-prone | Automated structured JSON extraction eliminates human transcription errors |
| Pharmacists misread dosage or frequency | Explicit fields for dosage, unit, frequency, route reduce ambiguity |
| No record of doctor–patient conversations | Groq Whisper transcription creates an instant, accurate written record |

---

## 🏗 Architecture Overview

```
User Browser (Gradio UI)
        │
        ├── [Image Upload] ──► llm_service.py ──► Ngrok Tunnel ──► Google Colab
        │                                                               │
        │                                                        MedGemma 4B (GPU)
        │                                                               │
        │                        parser.py ◄── JSON Response ◄─────────┘
        │
        ├── [Audio Record] ──► voice_service.py ──► Groq API (Whisper Large V3 Turbo)
        │                                               │           
                                              MedGemma 4B (GPU)
        │                        Transcript ◄───────────┘
        │
        └── [OCR Fallback] ──► ocr_service.py ──► EasyOCR (local CPU/GPU)
```

**Data Flow Summary:**
1. User uploads prescription image via Gradio
2. `llm_service.py` sends it as a multipart POST to the MedGemma API endpoint
3. MedGemma processes the image and returns JSON
4. `parser.py` normalizes the response (handles multiple formats)
5. `ui.py` renders the structured result as JSON medication cards
6. For voice: audio goes to Groq API → Whisper transcribes -> MedGemma 4B (GPU)→ text shown in UI

---

## 🛠 Tech Stack & Dependencies

### Core AI / ML
| Component | Technology | Purpose |
|---|---|---|
| Prescription Extraction | **MedGemma 4B** (Google) | Vision-language model trained on medical data |
| Voice Transcription | **Groq Whisper Large V3 Turbo** | Fast, accurate speech-to-text |
| OCR Fallback | **EasyOCR** | Local text extraction without a GPU API |
| OCR Alternative | **Pytesseract** | Tesseract-based OCR (included in requirements) |

### Backend
| Component | Technology | Version |
|---|---|---|
| Web Framework | **Gradio** | 6.14.0 |
| HTTP Requests | **Requests** | 2.34.2 |
| Async HTTP | **HTTPX** | 0.28.1 |
| API Server | **FastAPI** | 0.136.1 |
| ASGI Server | **Uvicorn** | 0.47.0 |
| Data Validation | **Pydantic** | 2.13.4 |
| ORM (future DB) | **SQLAlchemy** | 2.0.49 |
| Groq SDK | **groq** | 0.28.0 |

### ML / Compute
| Component | Technology | Version |
|---|---|---|
| Deep Learning | **PyTorch** | 2.12.0 |
| Vision Models | **Torchvision** | 0.27.0 |
| Image Processing | **Pillow** | 12.2.0 |
| Computer Vision | **OpenCV (headless)** | 4.13.0.92 |
| Scientific Compute | **NumPy / SciPy** | 2.4.6 / 1.17.1 |
| Image I/O | **ImageIO / scikit-image** | latest |

### Frontend / UI
| Component | Technology |
|---|---|
| UI Framework | Gradio Blocks |
| Styling | Custom CSS 
| Layout | Responsive two-column Gradio Row/Column |

### Infrastructure
| Component | Technology | Purpose |
|---|---|---|
| GPU Hosting | **Google Colab** | Runs MedGemma 4B on free/pro GPU tier |
| Tunnel | **Ngrok** | Exposes Colab server as a public HTTPS endpoint |
| Env Management | **python-dotenv** | Loads `.env` variables at runtime |

---

## ⚙ Environment Setup

### Required Environment Variables

```env
# Your active Ngrok URL from the Colab notebook output

MEDGEMMA_API_URL=https://your-ngrok-url.ngrok-free.app/extract

# Your Groq API key — get it from https://console.groq.com
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx

> **Important:** The `MEDGEMMA_API_URL` is temporary. Ngrok free tier generates a new URL on every Colab restart. Update `.env` each time, or upgrade to Ngrok paid plan with a reserved domain.

### Getting Your API Keys

**Groq API Key:**
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up or log in
3. Navigate to API Keys → Create New Key
4. Copy and paste into `.env`

**MedGemma via Colab:**
1. Open the companion Colab notebook
2. Run all cells — the last cell starts the FastAPI server and the Ngrok tunnel
3. Copy the printed Ngrok URL (e.g. `https://xxxx.ngrok-free.app`)
4. Append `/extract` and paste into `MEDGEMMA_API_URL` in `.env`

---

## 💻 Hardware Compatibility & Performance

This project is designed to work across a range of hardware. Here is a full breakdown:

### Local Machine — CPU Only
| Attribute | Detail |
|---|---|
| Suitable for | Development, testing, UI work |
| MedGemma | Not run locally — offloaded to Colab GPU |
| EasyOCR | Runs on CPU (slower: ~5–15s per image) |
| Whisper | Via Groq API — no local compute needed |
| Minimum RAM | 8 GB |
| Recommended RAM | 16 GB |
| Storage needed | ~4 GB (PyTorch + EasyOCR model cache) |

### Local Machine — NVIDIA GPU
| Attribute | Detail |
|---|---|
| Suitable for | Running EasyOCR fast locally |
| CUDA Version | 11.8+ recommended (PyTorch 2.12.0 compatible) |
| EasyOCR | GPU-accelerated (~0.5–2s per image) |
| MedGemma locally | Needs 16 GB+ VRAM (e.g. RTX 3090, A100) |
| Minimum VRAM for EasyOCR | 4 GB |
| Minimum VRAM for MedGemma | 16 GB |

### Google Colab — Recommended for MedGemma
| Tier | GPU | MedGemma Performance |
|---|---|---|
| Free | T4 (16 GB VRAM) | ~8–20s per prescription |
| Colab Pro | A100 (40 GB VRAM) | ~2–5s per prescription |
| Colab Pro+ | A100 (80 GB VRAM) | ~1–3s per prescription |

### Cloud Deployment — Production
| Provider | Recommended Instance | Notes |
|---|---|---|
| AWS | `g4dn.xlarge` (T4 GPU) | Good cost/performance balance |
| GCP | `n1-standard-4` + T4 | Native support for Colab-style workloads |
| Azure | `NC6s_v3` | V100 GPU, suitable for MedGemma |
| RunPod / Lambda Labs | A10G or A100 | Cheapest GPU rental option |
| Hugging Face Spaces | ZeroGPU / A10G | Free for public spaces, easy MedGemma deploy |

---

## 📦 Installation Guide

### Prerequisites
- Python 3.10 or 3.11 (recommended)
- pip
- Git
- A valid Groq API key
- A running Colab + Ngrok session for MedGemma


### Step 2 — Create a Virtual Environment

python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate

### Step 3 — Install Dependencies

pip install -r requirements.txt


> If you have an NVIDIA GPU, install the CUDA-enabled PyTorch first for faster local inference:
>
> pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
> 

### Step 4 — Configure Environment

.env
# Open .env and fill in MEDGEMMA_API_URL and GROQ_API_KEY


### Step 5 — Verify Setup

python app.py fixtures/test.png


## ▶ How to Run

### Launch the Web UI
```bash
python ui.py
```
Open your browser at: `http://localhost:7860`

### Run via CLI (headless / scripting)
```bash
# Use default test image (fixtures/test.png)
python app.py

# Use a custom image
python app.py path/to/prescription.png
```

### CLI Output Example
```
📄 Processing: fixtures/test.png
──────────────────────────────────────────────────
🔍 Sending to MedGemma API...
🧩 Parsing response...

✅ FINAL OUTPUT:

{
  "patient_name": "John Doe",
  "prescriber_name": "Dr. Smith",
  "prescription_date": "2026-05-20",
  "medications": [...]
}
```

---

## 📤 Expected Output

### Structured JSON Response from MedGemma
```json
{
  "patient_name": "John Doe",
  "prescriber_name": "Dr. A. Sharma",
  "prescription_date": "2026-05-20",
  "medications": [
    {
      "medication_name": "Amoxicillin",
      "dosage": "500",
      "unit": "mg",
      "frequency": "3 times a day",
      "route": "oral",
      "duration": "7 days",
      "special_instructions": "Take after meals",
      "uncertainty_notes": ""
    },
    {
      "medication_name": "Paracetamol",
      "dosage": "650",
      "unit": "mg",
      "frequency": "as needed",
      "route": "oral",
      "duration": "3 days",
      "special_instructions": "Do not exceed 4 doses per day",
      "uncertainty_notes": "Dosage partially unclear from handwriting"
    }
  ],
  "run_metadata": {
    "model_name": "MedGemma 4B",
    "latency_ms": 4320
  }
}
```

### UI Output Breakdown
- **Meta chips** — Patient name, Prescriber name, Date, and Latency displayed at the top
- **Medication cards** — one styled card per drug with all fields displayed in rows
- **Raw JSON accordion** — collapsible developer view showing the full API response
- **Error banner** — shown in red if connection fails or parsing errors occur
- **Voice transcript** — plain text output in a scrollable textbox

### Error Response Structure
```json
{
  "error": true,
  "message": "Cannot connect to the MedGemma API. Make sure your Colab notebook is running and the Ngrok tunnel is active.",
  "hint": "Set the MEDGEMMA_API_URL environment variable with your current Ngrok URL."
}
```

---

## 📁 Project Structure

```
prescription-extractor/
│
├── app.py                  # CLI entrypoint — run extraction from terminal
├── ui.py                   # Gradio web UI — main application interface
├── requirements.txt        # All Python dependencies with pinned versions
├── _env                    # Environment variable template (copy to .env)
├── .gitignore              # Ignores venv, .env, caches, databases
│
├── services/
│   ├── llm_service.py      # Sends image to MedGemma API, handles all HTTP errors
│   ├── parser.py           # Normalizes and parses API response into clean JSON
│   ├── ocr_service.py      # Local EasyOCR fallback for text extraction
│   └── voice_service.py    # Groq Whisper audio transcription service
│
├── prompts/
│   └── extract_prompt.txt  # (Placeholder) System prompt for MedGemma customization
│
├── database/
│   └── db.py               # (Placeholder) SQLAlchemy DB setup for future persistence
│
└── fixtures/
    └── test.png            # Sample prescription image for local testing
```

---

## 📈 Scaling Roadmap

### Stage 1 — Current Prototype (Now)
- Single-user Gradio app running locally
- MedGemma hosted on Colab free tier via Ngrok
- No persistence, no auth, no queue management

### Stage 2 — Stable Dev Deployment
- Replace Ngrok with a dedicated cloud GPU server (RunPod / AWS g4dn)
- Add a reserved Ngrok domain or self-hosted domain with SSL
- Activate `database/db.py` with SQLite or PostgreSQL to persist extraction history
- Add basic authentication using Gradio's built-in `auth=` parameter

### Stage 3 — Multi-User Production
- Containerize with **Docker** (`Dockerfile` + `docker-compose.yml`)
- Deploy Gradio behind an **NGINX** reverse proxy
- Add **Redis + Celery** task queue for async prescription processing
- Use **Hugging Face Inference Endpoints** or **AWS SageMaker** for MedGemma hosting
- Horizontal scaling with multiple workers behind a load balancer

### Stage 4 — Enterprise / EHR Integration
- Expose a **REST API** via FastAPI (already in the stack) with `/extract` and `/transcribe` endpoints
- Add **OAuth2 / JWT** authentication
- Integrate with **HL7 FHIR** standard for EHR/EMR compatibility
- Add **audit logging** for every prescription access (compliance requirement)
- Multi-language OCR support via additional EasyOCR language packs
- Fine-tune MedGemma on institution-specific prescription templates and handwriting

### Performance Scaling by Hardware

| Scale Level | Setup | Expected Throughput |
|---|---|---|
| Prototype | Colab T4 + 1 worker | ~3–5 prescriptions / min |
| Small Clinic | Dedicated A10G + Uvicorn 4 workers | ~20–30 prescriptions / min |
| Hospital | 2x A100 + load balancer + Celery queue | ~100–200 prescriptions / min |
| Enterprise | Multi-region GPU cluster | 1000+ prescriptions / min |

---



Depending on your environment or constraints, here are drop-in alternatives for each component:

| Component | Current Choice | Alternative 1 | Alternative 2 | When to Switch |
|---|---|---|---|---|
| Vision LLM | MedGemma 4B (Colab) | GPT-4o Vision (OpenAI API) | LLaVA 1.6 (local) | If Colab is unavailable or higher accuracy is needed |
| Voice STT | Groq Whisper Large V3 | OpenAI Whisper API | Local Whisper (CPU/GPU) | For offline use or if Groq latency is too high |
| UI Framework | Gradio | Streamlit | FastAPI + React | If you need a custom branded or embedded frontend |
| OCR Fallback | EasyOCR | Pytesseract | Google Cloud Vision API | If EasyOCR accuracy is insufficient for your use case |
| Tunnel | Ngrok | Cloudflare Tunnel | Localtunnel | If Ngrok URL rotation is a blocker in your workflow |
| GPU Hosting | Google Colab | RunPod | AWS g4dn / Hugging Face Spaces | For stable production deployments with uptime requirements |
| Database | None (prototype) | SQLite via SQLAlchemy | PostgreSQL | SQLite for single-user; Postgres for multi-user production |
| Authentication | None (prototype) | Gradio `auth=` param | FastAPI + OAuth2 / JWT | The moment any patient data is stored or accessed |

---

## 🔒 Safety & Privacy Notes

> ⚠️ **This is a research prototype. Do not use with real patient data without a full compliance and security review.**

### Current Data Handling Risks
- Prescription images are transmitted over the internet to a Google Colab server via Ngrok — this is **not HIPAA or GDPR compliant** in its current form
- Audio recordings are sent to Groq's external API servers — review [Groq's privacy policy](https://groq.com/privacy-policy/) before any real patient data use
- No data is stored persistently in the current version — nothing is written to disk or a database
- Ngrok tunnels expose your Colab server publicly — always use authentication tokens and shut down sessions when not in use

### Recommended Safeguards Before Clinical Use
1. **Deploy MedGemma on a private, HIPAA-compliant server** (AWS or Azure with a signed BAA) — remove Ngrok entirely
2. **Use HTTPS for all communication** — verify end-to-end TLS when self-hosting
3. **Encrypt data at rest** if prescription images or results are stored in a database
4. **Implement full audit logging** — every prescription viewed, extracted, or modified must be logged with timestamp and user identity
5. **Enforce user authentication** before any PHI (Protected Health Information) is accessible to any user
6. **Never log raw prescription images or audio transcripts** to console or flat files in production environments
7. **Add patient consent flows** — patients should be explicitly informed that their data is being processed by an AI system
8. **Treat model output as a draft, not ground truth** — a licensed pharmacist or clinician must review all AI-extracted prescription data before any clinical action
9. **Rate limit API endpoints** to prevent abuse if the FastAPI server is externally exposed
10. **Use a private Whisper deployment** (local `whisper` Python library) instead of the Groq API for maximum audio privacy

### Model Limitations to Be Aware Of
- MedGemma 4B may misread low-quality or unclear handwriting — image quality directly impacts accuracy
- The model may hallucinate field values not present in the image, especially for partially visible text
- `uncertainty_notes` flags some issues but does not catch all errors — do not rely on it as a complete confidence indicator
- Dosage units (mg, ml, units, IU) can be confused for ambiguous handwriting styles
- Not validated for prescription formats outside of English or standard Western medical notation

---

## 📄 License

This project is a research prototype. Add your license here before public distribution.

---

## 🙏 Acknowledgements

- [MedGemma](https://ai.google.dev/gemma/docs/medgemma) by Google DeepMind
- [Groq](https://groq.com) for ultra-fast Whisper inference
- [Gradio](https://gradio.app) by Hugging Face
- [EasyOCR](https://github.com/JaidedAI/EasyOCR) by Jaided AI