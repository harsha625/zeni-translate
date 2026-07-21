# ✨ Zeni Translate

> **Next-Generation AI Translation, Picture Scanning OCR & Conversational Assistant**

![Zeni Translate Banner](https://img.shields.io/badge/Zeni%20Translate-v2.0-06b6d4?style=for-the-badge&logo=google-translate&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.0%2B-000000?style=for-the-badge&logo=flask&logoColor=white)
![Tesseract OCR](https://img.shields.io/badge/Tesseract--OCR-Client--Side-4285F4?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

---

## 🌟 Overview

**Zeni Translate** is a feature-rich, modern web application designed for fast multilingual translation, picture text recognition (OCR), conversational AI language assistance, and voice synthesis. Built with a sleek glassmorphic UI, responsive layouts, and customizable light/dark themes.

---

## 🚀 Features

### 🌐 Multilingual Neural Translation
- Supports **25+ major global languages** (English, Telugu, Hindi, Tamil, Kannada, Malayalam, Spanish, French, German, Japanese, Chinese, Arabic, and more).
- **Tone & Style Selector**: Standard, Formal & Polite, Casual Conversation, Business Professional, and Simplified.
- Auto-language detection and phonetic transliteration guide.

###  Picture Scan (Image OCR)
- Drag-and-drop or upload images (`PNG`, `JPG`, `JPEG`, `WEBP`, `BMP`).
- Interactive laser scanner animation powered by **Tesseract.js** in browser.
- Automatically extracts text from pictures and translates it into target languages in real-time.

###  Light Mode & Dark Mode Themes
- Seamless 1-click theme switcher with curated color tokens.
- **Dark Obsidian Theme**: Deep midnight tones with cyan and indigo glowing highlights.
- **Light Porcelain Theme**: Crisp slate canvas with royal blue and emerald highlights.
- Remembers user theme preference in `localStorage`.

###  Enhanced Voiceover & Speech Input
- **Text-to-Speech (TTS)**: Web Speech Synthesis with server `gTTS` fallback.
- **Playback Speed Controller**: `0.75x`, `1.0x`, `1.25x`, and `1.5x`.
- **Animated Audio Waveform**: Soundwave bars vibrate during playback.
- **Speech-to-Text Microphone Input**: Speak directly to transcribe and translate text.

###  Zeni AI Assistant (Bot Drawer)
- Side-drawer conversational assistant (`Zeni Bot`).
- Answers grammar questions, translation tips, pronunciation advice, and usage examples.

###  Authentication & Guest Mode
- Login & Sign Up modal with profile avatar integration.
- Quick "Continue as Guest" access.

---

##  Project Structure

```text
translate language/
├── app.py                     # Main Flask Application & Web Routes
├── translate_bot.py           # Interactive CLI Translation Bot
├── requirements.txt           # Python Dependencies
├── Procfile                   # Cloud Deployment (Render / Heroku)
├── vercel.json                # Vercel Serverless Deployment Config
├── README.md                  # Project Documentation
├── run_website.bat            # 1-Click Windows Batch Launcher
├── start_zeni_translate.vbs   # Silent Background Launcher
└── create_shortcut.ps1        # Desktop Shortcut Generator Script
```

---

##  Local Setup & Installation

1. **Clone Repository**:
   ```bash
   git clone https://github.com/harsha625/zeni-translate.git
   cd zeni-translate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Application**:
   ```bash
   python app.py
   ```
   Open your browser at `http://127.0.0.1:5050`.

---

##  Cloud Deployment

### Deploy to Render
1. Create a New **Web Service** on [Render.com](https://render.com).
2. Connect your GitHub repository `harsha625/zeni-translate`.
3. Set **Build Command**: `pip install -r requirements.txt`
4. Set **Start Command**: `gunicorn app:app`
5. Click **Create Web Service**.

---

##  License
Distributed under the **MIT License**. Created by [harsha625](https://github.com/harsha625).
