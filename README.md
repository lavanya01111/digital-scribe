# Digital Scribe 

**Digital Scribe** is a specialized, production-ready web application designed to assist students with Specific Learning Disabilities (especially dyslexia) by acting as a digital scribe during exams. It provides a secure, accessible environment to convert handwriting to text, support speech-to-text (STT) dictate functionality, read back text using text-to-speech (TTS), and perform spelling/grammar corrections.

---

## 🚀 Features

- **Handwriting Recognition**: Converts uploaded or live-captured handwriting into digital text.
- **Speech-to-Text (STT)**: Allows students to dictate their answers using their voice.
- **Text-to-Speech (TTS)**: Reads out text and questions to assist with comprehension.
- **Spelling & Grammar Correction**: Automatically corrects spelling mistakes and grammar dynamically.
- **Multi-Language Support**: Capable of detecting and processing various languages.
- **Secure Exam Environment**: Purpose-built to be reliable and secure during high-stakes exam condition.

---

## 🛠️ Technology Stack

### Frontend
- **Framework:** React 18, Vite
- **Styling:** Tailwind CSS, PostCSS
- **Icons:** Lucide React
- **Auth/Backend Client:** `@supabase/supabase-js`

### AI Service (Backend)
- **Framework:** FastAPI, Uvicorn (Python)
- **Deep Learning / AI:** PyTorch, Transformers (Hugging Face)
- **Speech Models:** OpenAI Whisper
- **Text Processing:** `symspellpy`, `langdetect`
- **Image Processing:** Pillow (`PIL`)

### Database & Authentication
- **Provider:** Supabase (PostgreSQL, GoTrue for Auth)

---

## 📂 Project Structure

```bash
digital-scribe/
├── ai_service/             # FastAPI backend for ML models
│   ├── app/
│   │   ├── routers/        # API endpoints (handwriting, stt, tts, correction)
│   │   ├── models/         # ML model loading & inference code
│   │   ├── utils/          # Helper utilities
│   │   └── main.py         # FastAPI application entry point
│   ├── Dockerfile          # Container specification
│   ├── requirements.txt    # Python dependencies
│   └── training/           # Scripts & modules for training custom AI models
├── frontend/               # React web application
│   ├── src/                # UI components, pages, and Supabase integration
│   ├── public/             # Static assets
│   ├── package.json        # Node.js dependencies
│   ├── tailwind.config.js  # Styling configuration
│   └── vite.config.js      # Bundler settings
├── supabase/               # Supabase database configurations/migrations
└── docs/                   # Additional documentation
```

---

## ⚙️ Prerequisites

Before you begin, ensure you have the following installed:
- **Node.js** (v18 or higher)
- **Python** (v3.9 or higher)
- **Git**
- **Supabase CLI** (optional, but recommended for local database management)

---

## 💻 Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/your-username/digital-scribe.git
cd digital-scribe
```

### 2. Set up the Frontend
```bash
cd frontend
npm install
```
*Create a `.env.local` file in the frontend directory with your Supabase credentials:*
```env
VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### 3. Set up the AI Service (Backend)
```bash
cd ../ai_service
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## ▶️ Running the Application Locally

You will need two terminal windows to run both the frontend and the backend simultaneously.

**Terminal 1: Start the AI Service Backend**
```bash
cd ai_service
# Make sure your virtual environment is activated
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
*The FastAPI backend will run at `http://localhost:8000` and the interactive API documentation can be found at `http://localhost:8000/docs`.*

**Terminal 2: Start the React Frontend**
```bash
cd frontend
npm run dev
```
*The React app will typically run at `http://localhost:5173`.*

---

## 📡 API Endpoints Overview

The `ai_service` exposes the following main routers (accessible under `/` or specific api prefixes):

- `POST /handwriting/recognize` - Uploads a canvas image or scanned image to convert handwriting into text.
- `POST /stt/transcribe` - Accepts audio input and uses Whisper to transcribe speech to text.
- `POST /tts/synthesize` - Converts text to audio format.
- `POST /correction/correct` - Accepts text input and returns grammatically correct and spell-checked text.

You can interact with all APIs directly via the Swagger UI spawned by FastAPI at `http://localhost:8000/docs`.

---

## 🤝 Contributing

We welcome contributions to make Digital Scribe better!
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

---

> **Note:** Digital Scribe is an open-source initiative dedicated to supporting accessible education. If you are integrating this tool into official exam bodies, ensure compliance with local educational and disability accommodation regulations.
