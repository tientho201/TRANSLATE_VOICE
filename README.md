# 🌐 Voice Translator

Ứng dụng dịch giọng nói sử dụng **Groq API** (Whisper Large v3 + LLaMA 3.3 70B).

## 📁 Cấu trúc dự án

```
TRANSLATE_VOICE/
├── backend/
│   ├── main.py                  # FastAPI app
│   ├── routers/
│   │   └── translate.py         # API endpoints
│   ├── services/
│   │   └── groq_service.py      # Groq STT + LLM
│   ├── .env                     # API key (không commit!)
│   └── requirements.txt
├── frontend/
│   ├── app.py                   # Streamlit UI
│   └── requirements.txt
├── start.ps1                    # Script khởi động (Windows)
└── README.md
```

## ⚙️ Cài đặt

### 1. Clone & cài dependencies

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../frontend
pip install -r requirements.txt
```

### 2. Cấu hình API Key

Mở file `backend/.env` và điền Groq API key:

```env
GROQ_API_KEY=your_groq_api_key_here
```

> Lấy API key miễn phí tại: https://console.groq.com

## 🚀 Khởi động

### Option A — Dùng script PowerShell (khuyến nghị)

```powershell
.\start.ps1
```

### Option B — Chạy thủ công (2 terminal)

**Terminal 1 — Backend:**
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 — Frontend:**
```bash
cd frontend
streamlit run app.py
```

Sau đó mở trình duyệt: **http://localhost:8501**

## 🔌 API Endpoints

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| `GET` | `/health` | Kiểm tra trạng thái server |
| `GET` | `/api/v1/languages` | Danh sách ngôn ngữ hỗ trợ |
| `POST` | `/api/v1/translate` | Upload audio và dịch |

### POST `/api/v1/translate`

**Form-data:**
- `audio_file` — file âm thanh (mp3, wav, m4a, webm, ogg, flac...)
- `source_language` — mã ngôn ngữ nguồn (vd: `vi`)
- `target_language` — mã ngôn ngữ đích (vd: `en`)

**Response:**
```json
{
  "success": true,
  "source_language": "Vietnamese",
  "target_language": "English",
  "transcribed_text": "Xin chào thế giới",
  "translated_text": "Hello world"
}
```

## 🌍 Ngôn ngữ hỗ trợ

| Code | Ngôn ngữ |
|------|----------|
| `vi` | Tiếng Việt |
| `en` | English |
| `zh` | Chinese |
| `ja` | Japanese |
| `ko` | Korean |
| `fr` | French |
| `de` | German |
| `es` | Spanish |
| `th` | Thai |
| `ru` | Russian |
| `ar` | Arabic |
| `pt` | Portuguese |
| `it` | Italian |
| `hi` | Hindi |

## 🤖 Models sử dụng

- **STT**: `whisper-large-v3` (Groq) — transcribe audio
- **LLM**: `llama-3.3-70b-versatile` (Groq) — dịch văn bản
