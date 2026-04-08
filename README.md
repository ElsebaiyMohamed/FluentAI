# 🎙️ FluentAI an English Learning & Pronunciation Assessment Tool

An AI-powered system for evaluating **English pronunciation and fluency** from speech recordings of predefined text.
Built for real-world usage with fast inference and interpretable scoring.

---

## 🚀 Overview

This project provides an automated pronunciation assessment pipeline using **self-supervised speech models + forced alignment + GOP scoring**.

It enables:

* 🎯 Pronunciation accuracy evaluation
* 🗣️ Fluency assessment
* 📊 Word/phoneme-level feedback

---

## 🧠 Methodology

### 1. Speech Recognition Backbone

* Model: **Wav2Vec2**
* Fine-tuned for speech-to-text alignment

### 2. Alignment

* **CTC-based forced alignment**
* Maps audio frames → phonemes/words

### 3. Scoring (Core Innovation)

* Implemented **Goodness of Pronunciation (GOP)**
* Measures likelihood of correct phoneme production

### 4. Output

* Overall pronunciation score
* Word-level feedback
* Fluency indicators (timing, pauses)

---

## 📊 Performance

| Metric           | Value                   |
| ---------------- | ----------------------- |
| Scoring Accuracy | ~88%                    |
| Inference Time   | ~15 seconds/audio       |
| Input Type       | Predefined English text |

---

## 🏗️ System Architecture

```
Audio Input
   ↓
Preprocessing
   ↓
Wav2Vec2 Model
   ↓
CTC Alignment
   ↓
Phoneme Extraction
   ↓
GOP Scoring
   ↓
Final Evaluation Report
```

---

## 📁 Project Structure

```
FluentAI/
│
├── app/                    # API & serving layer
│   ├── flask_app.py
│   ├── routes/
│   └── schemas/
│
├── core/                   # Core ML logic
│   ├── model.py            # Wav2Vec2 loading/inference
│   ├── aligner.py          # CTC alignment
│   ├── gop.py              # GOP scoring
│   └── evaluator.py        # Final scoring pipeline
│
├── data/
│   ├── samples/
│   └── test_cases/
│
├── configs/
│   └── config.yaml
│
├── utils/
│   ├── audio.py
│   └── text.py
│
├── demo/
│   ├── gradio_app.py       # UI demo
│
├── notebooks/
│
├── tests/
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## ⚙️ Installation

```bash
git clone https://github.com/ElsebaiyMohamed/FluentAI.git
cd FluentAI

pip install -r requirements.txt
```

---

## ▶️ Usage

### Run Flask API

```bash
python app/flask_app.py
```

### API Endpoint

**POST** `/evaluate`

#### Request

```json
{
  "audio": "<base64_encoded_audio>",
  "reference_text": "The quick brown fox jumps over the lazy dog"
}
```

#### Response

```json
{
  "overall_score": 0.88,
  "fluency_score": 0.84,
  "pronunciation_score": 0.90,
  "word_scores": [
    {"word": "quick", "score": 0.92},
    {"word": "brown", "score": 0.87}
  ]
}
```

---

## 🎛️ Gradio Demo

Run locally:

```bash
python demo/gradio_app.py
```

Features:

* Upload or record audio
* Input reference text
* Visual pronunciation feedback

---

## 🌐 Example Workflow

1. User reads predefined sentence
2. Uploads recording
3. System aligns audio → text
4. Computes phoneme-level scores
5. Returns detailed feedback

---

## 📌 Use Cases

* Language learning platforms
* Pronunciation training apps
* EdTech solutions
* Automated speaking assessment

---

## 🔥 Key Highlights

* Real-world deployment-ready pipeline
* Efficient (~15s latency)
* Interpretable scoring (GOP)
* Modular design (easy to extend)

---

---

## 📜 License

 GPL-3.0 license 
