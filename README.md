# 🎙️ FluentAI

FluentAI is a FastAPI-based pronunciation assessment service for English speech recordings. It evaluates uploaded audio against expected text and returns pronunciation, fluency, and content scores.

---

## 🚀 What this project does

* Loads a pretrained pronunciation model using Wav2Vec2
* Accepts audio file uploads via REST
* Supports optional expected text as a string or uploaded text file
* Returns pronunciation and fluency scoring results in JSON

---

## 📁 Project structure

```
FluentAI/
├── README.md
├── requirements.txt
└── src/
    ├── app.py
    ├── controllers/
    │   ├── BaseController.py
    │   ├── DataController.py
    │   └── LessonContraller.py
    ├── core/
    │   ├── __init__.py
    │   ├── model.py
    │   └── pronunciation.py
    ├── helpers/
    │   ├── __init__.py
    │   └── config.py
    ├── models/
    │   ├── __init__.py
    │   └── enums/
    │       └── ResponseEnums.py
    ├── routes/
    │   ├── __init__.py
    │   ├── base.py
    │   └── data.py
    └── assets/
        ├── files/
        └── sounds/
```

---

## ⚙️ Requirements

Install dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

## ▶️ Run the app

Start the FastAPI server with uvicorn:

```bash
uvicorn src.app:app --reload --host 0.0.0.0 --port 8000
```

The service will be available at `http://127.0.0.1:8000`.

---

## 🧪 API Endpoints

### Health check

`GET /fluentai/v1/health`

Response example:

```json
{
  "status": "ok",
  "model_loaded": true,
  "processor_loaded": true
}
```

### App info

`GET /fluentai/v1/info`

Response example:

```json
{
  "data_endpoint": "This endpoint provides information about the data used in the application.",
  "app_name": "FluentAI",
  "app_version": "0.1",
  "author": "your name"
}
```

### Upload audio

`POST /fluentai/v1/data/upload/{lesson_id}`

Request parameters:
* `lesson_id` — path parameter
* `file` — audio file upload as form-data

Example response:

```json
{
  "status": "success",
  "lesson_id": "lesson1",
  "file_id": "..."
}
```

### Assess pronunciation

`POST /fluentai/v1/data/assess/{lesson_id}`

Request form-data fields:
* `audio` — audio file upload
* `expected_text` — optional expected text string
* `text` — optional text file upload containing expected text

Example response:

```json
{
  "status": "success",
  "lesson_id": "lesson1",
  "file_id": "...",
  "scores": {
    "pronunciation_accuracy": 92,
    "content_scores": 89,
    "total_score": 90,
    "fluency_score": 88
  },
  "expected_text": "The quick brown fox jumps over the lazy dog"
}
```

---

## 🔧 How it works

* `src/app.py` initializes FastAPI and registers routes
* `src/core/pronunciation.py` loads the model and processes audio
* `src/routes/base.py` provides health and info endpoints
* `src/routes/data.py` handles upload and assessment requests
* `src/controllers/DataController.py` validates and saves uploaded files
* `src/helpers/config.py` defines settings and allowed extensions

---

## 💡 Notes

* The pretrained model is `seba3y/wav2vec-base-en-pronunciation-assesment`.
* Supported audio extensions are WAV, MP3, and M4A.
* The app automatically uses GPU if available, otherwise it uses CPU.
* Environment settings can be loaded from `src/.env`.

---

## 📌 Tips

* Use Postman or curl to send multipart/form-data requests.
* Ensure `uvicorn` is installed and run from the project root.
* If model download fails, check network access and Hugging Face availability.

---

## 📜 License

This project is licensed under GPL-3.0.
