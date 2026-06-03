# 🌍 Multilingual Document Parser

> An AI pipeline that reads documents in any language — extracts text, detects figures, translates content, and lets you ask questions about it using LLMs.

---

## 💡 What It Does

Most document parsers break on non-English text, and all of them ignore embedded images and figures. This pipeline handles both — it combines OCR, object detection, language detection, neural translation, and LLM-powered Q&A into one end-to-end system.

**Extraction accuracy: 80% across 9 languages tested.**

---

## ✨ Features

- 📝 **Text Extraction** — PaddleOCR detects and extracts text with layout preservation
- 🖼 **Figure & Image Detection** — YOLOv8 identifies charts, diagrams, and embedded images
- 🌐 **Language Detection** — fastText identifies the document language automatically
- 🔄 **Neural Translation** — NLLB-200 (Meta's 200-language model) translates to English
- 🤖 **LLM Q&A** — Gemini and Claude APIs for summarization, entity recognition, and contextual Q&A
- 📊 **Multi-format Support** — PDFs, scanned documents, and image-based files

---

## 🛠 Tech Stack

| Component | Tool |
|---|---|
| Layout & text OCR | PaddleOCR |
| Image/figure detection | YOLOv8 (PyTorch) |
| Language identification | fastText |
| Translation | NLLB-200 (Meta) |
| Summarization & Q&A | Google Gemini, Anthropic Claude |
| Deployment | React.js, Firebase |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- CUDA-enabled GPU recommended (for YOLOv8 and PaddleOCR)
- Gemini API key and/or Claude API key

### Installation

```bash
# Clone the repo
git clone https://github.com/prakritipatkar/multilingual-document-parser.git
cd multilingual-document-parser

# Install dependencies
pip install paddlepaddle paddleocr ultralytics fasttext transformers torch

# Set up environment variables
cp .env.example .env
# Add your GEMINI_API_KEY and/or ANTHROPIC_API_KEY
```

### Run the Pipeline

```python
from parser import DocumentParser

parser = DocumentParser()
result = parser.parse("document.pdf")

print(result["language"])       # Detected language
print(result["translated_text"]) # English translation
print(result["entities"])        # Extracted entities
```

---

## 🔄 Pipeline Overview

```
Input Document (PDF / Image)
        │
        ▼
  PaddleOCR (text + layout extraction)
        │
        ▼
  YOLOv8 (figure & image detection)
        │
        ▼
  fastText (language identification)
        │
        ▼
  NLLB-200 (translation → English)
        │
        ▼
  Gemini / Claude (summarization, NER, Q&A)
        │
        ▼
  Structured Output (JSON)
```

---

## 📊 Performance

| Metric | Value |
|---|---|
| Extraction accuracy | 80% |
| Languages supported | 9 tested (200 via NLLB-200) |
| Figure detection mAP | _(add your value)_ |

---

## 🔮 Future Improvements

- [ ] Table structure extraction
- [ ] Handwriting recognition
- [ ] Real-time streaming output
- [ ] Web UI for non-technical users

---

## 👩‍💻 Author

**Prakriti Patkar** — [LinkedIn](https://www.linkedin.com/in/prakriti-patkar-33125b228) · [GitHub](https://github.com/prakritipatkar)
