from __future__ import annotations
import io
import os
import sys
import json
from flask import Flask, request, jsonify, render_template_string, Response

translator = None
try:
    from googletrans import Translator
    translator = Translator()
except Exception as err:
    print(f"googletrans import warning: {err}", file=sys.stderr)

try:
    from deep_translator import GoogleTranslator
except Exception as err:
    GoogleTranslator = None

try:
    from gtts import gTTS
except ImportError:
    gTTS = None

app = Flask(__name__)

LANGUAGES = {
    "en": "English 🇬🇧",
    "te": "Telugu (తెలుగు) 🇮🇳",
    "hi": "Hindi (हिंदी) 🇮🇳",
    "ta": "Tamil (தமிழ்) 🇮🇳",
    "kn": "Kannada (కన్నడ) 🇮🇳",
    "ml": "Malayalam (മലയാളം) 🇮🇳",
    "bn": "Bengali (বাংলা) 🇮🇳",
    "mr": "Marathi (మరాठी) 🇮🇳",
    "gu": "Gujarati (ગુજરાતી) 🇮🇳",
    "pa": "Punjabi (ਪੰਜਾਬੀ) 🇮🇳",
    "ur": "Urdu (اردو) 🇵🇰",
    "es": "Spanish (Español) 🇪🇸",
    "fr": "French (Français) 🇫🇷",
    "de": "German (Deutsch) 🇩🇪",
    "it": "Italian (Italiano) 🇮🇹",
    "pt": "Portuguese (Português) 🇵🇹",
    "ru": "Russian (Русский) 🇷🇺",
    "ja": "Japanese (日本語) 🇯🇵",
    "ko": "Korean (한국어) 🇰🇷",
    "zh-cn": "Chinese (中文) 🇨🇳",
    "ar": "Arabic (العربية) 🇸🇦",
    "tr": "Turkish (Türkçe) 🇹🇷",
    "vi": "Vietnamese (Tiếng Việt) 🇻🇳",
    "th": "Thai (ไทย) 🇹🇭",
    "nl": "Dutch (Nederlands) 🇳🇱",
}

HTML_TEMPLATE = """<!doctype html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no" />
  <title>Zeni Translate | Next-Gen AI Translation Studio</title>
  
  <meta name="description" content="Zeni Translate - Futuristic AI text translation, picture camera OCR scan, voiceover synthesis, and Zeni AI assistant." />
  <meta name="theme-color" content="#030712" />
  
  <!-- Google Fonts & Font Awesome Icons -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&family=Outfit:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" />
  
  <!-- Tesseract OCR -->
  <script src="https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/tesseract.min.js"></script>

  <style>
    /* HIGH-AESTHETIC FUTURISTIC DESIGN SYSTEM */
    :root[data-theme="dark"] {
      --bg-body: #030712;
      --bg-glass: rgba(15, 23, 42, 0.78);
      --bg-card: rgba(30, 41, 59, 0.65);
      --bg-input: rgba(11, 17, 32, 0.92);
      --border-line: rgba(255, 255, 255, 0.12);
      --border-glow: rgba(6, 182, 212, 0.5);
      --border-focus: #06b6d4;
      
      --text-bright: #ffffff;
      --text-sub: #94a3b8;
      --text-muted: #64748b;
      
      --cyan: #06b6d4;
      --indigo: #6366f1;
      --violet: #8b5cf6;
      --emerald: #10b981;
      --pink: #ec4899;
      --amber: #f59e0b;
      
      --grad-primary: linear-gradient(135deg, #06b6d4 0%, #3b82f6 35%, #8b5cf6 70%, #ec4899 100%);
      --grad-button: linear-gradient(135deg, #06b6d4 0%, #3b82f6 50%, #6366f1 100%);
      --grad-button-hover: linear-gradient(135deg, #0891b2 0%, #2563eb 50%, #4f46e5 100%);
      --grad-speaker: linear-gradient(135deg, #10b981 0%, #06b6d4 100%);
      --grad-mic: linear-gradient(135deg, #ef4444 0%, #ec4899 100%);
      
      --shadow-card: 0 30px 100px rgba(0, 0, 0, 0.85), 0 0 60px rgba(6, 182, 212, 0.18);
      --orb-glow1: rgba(6, 182, 212, 0.22);
      --orb-glow2: rgba(139, 92, 246, 0.22);
      --nav-bg: rgba(3, 7, 18, 0.88);
      --mobile-nav-bg: rgba(11, 17, 32, 0.96);
    }

    :root[data-theme="light"] {
      --bg-body: #f8fafc;
      --bg-glass: rgba(255, 255, 255, 0.94);
      --bg-card: rgba(241, 245, 249, 0.9);
      --bg-input: #ffffff;
      --border-line: rgba(0, 0, 0, 0.09);
      --border-glow: rgba(37, 99, 235, 0.45);
      --border-focus: #2563eb;
      
      --text-bright: #0f172a;
      --text-sub: #334155;
      --text-muted: #64748b;
      
      --cyan: #0284c7;
      --indigo: #2563eb;
      --violet: #7c3aed;
      --emerald: #059669;
      --pink: #db2777;
      --amber: #d97706;
      
      --grad-primary: linear-gradient(135deg, #2563eb 0%, #0d9488 40%, #7c3aed 80%, #db2777 100%);
      --grad-button: linear-gradient(135deg, #2563eb 0%, #0d9488 50%, #7c3aed 100%);
      --grad-button-hover: linear-gradient(135deg, #1d4ed8 0%, #0f766e 50%, #6d28d9 100%);
      --grad-speaker: linear-gradient(135deg, #059669 0%, #0284c7 100%);
      --grad-mic: linear-gradient(135deg, #dc2626 0%, #db2777 100%);
      
      --shadow-card: 0 25px 70px rgba(15, 23, 42, 0.1), 0 0 45px rgba(37, 99, 235, 0.12);
      --orb-glow1: rgba(37, 99, 235, 0.14);
      --orb-glow2: rgba(13, 148, 136, 0.14);
      --nav-bg: rgba(255, 255, 255, 0.92);
      --mobile-nav-bg: rgba(255, 255, 255, 0.96);
    }

    * { box-sizing: border-box; margin: 0; padding: 0; transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease; -webkit-tap-highlight-color: transparent; }

    body {
      font-family: 'Plus Jakarta Sans', sans-serif;
      min-height: 100vh;
      background-color: var(--bg-body);
      color: var(--text-bright);
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 0 0.8rem 6rem 0.8rem;
      overflow-x: hidden;
      position: relative;
    }

    /* Ambient Motion Particle Orbs */
    .bg-orb {
      position: fixed;
      border-radius: 50%;
      filter: blur(140px);
      pointer-events: none;
      z-index: 0;
      animation: orbFloat 22s ease-in-out infinite alternate;
    }
    .orb-1 { width: 600px; height: 600px; background: var(--orb-glow1); top: -150px; left: -150px; }
    .orb-2 { width: 550px; height: 550px; background: var(--orb-glow2); bottom: -150px; right: -150px; animation-delay: -9s; }

    @keyframes orbFloat {
      0% { transform: translate(0, 0) scale(1); }
      50% { transform: translate(50px, 40px) scale(1.08); }
      100% { transform: translate(-40px, 60px) scale(0.92); }
    }

    /* TOP NAVBAR */
    .navbar {
      width: 100%;
      max-width: 1280px;
      margin: 1rem auto 1.4rem auto;
      padding: 0.75rem 1.6rem;
      background: var(--nav-bg);
      backdrop-filter: blur(25px);
      border: 1px solid var(--border-line);
      border-radius: 999px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
      z-index: 50;
      box-shadow: 0 10px 30px rgba(0,0,0,0.12);
    }

    .brand-logo {
      display: flex;
      align-items: center;
      gap: 0.85rem;
      text-decoration: none;
      cursor: pointer;
    }

    .brand-icon {
      width: 46px;
      height: 46px;
      border-radius: 16px;
      background: var(--grad-button);
      display: flex;
      align-items: center;
      justify-content: center;
      color: #ffffff;
      font-size: 1.4rem;
      box-shadow: 0 8px 24px var(--cyan);
    }

    .brand-title {
      font-family: 'Outfit', sans-serif;
      font-weight: 900;
      font-size: 1.55rem;
      letter-spacing: -0.5px;
      background: var(--grad-primary);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .nav-actions {
      display: flex;
      align-items: center;
      gap: 0.65rem;
    }

    .nav-btn {
      padding: 0.6rem 1.25rem;
      border-radius: 999px;
      border: 1px solid var(--border-line);
      background: var(--bg-card);
      color: var(--text-bright);
      font-weight: 700;
      font-size: 0.88rem;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.55rem;
      min-height: 42px;
    }

    .nav-btn:hover {
      border-color: var(--border-glow);
      color: var(--cyan);
      transform: translateY(-2px);
    }

    .nav-btn.primary-btn {
      background: var(--grad-button);
      color: #ffffff;
      border: none;
      box-shadow: 0 8px 24px var(--cyan);
    }

    .nav-btn.primary-btn:hover {
      background: var(--grad-button-hover);
      transform: translateY(-2px) scale(1.02);
    }

    /* HERO & CONTAINER */
    .container {
      width: min(100%, 1280px);
      z-index: 1;
    }

    .hero-header {
      text-align: center;
      margin: 0.5rem 0 1.8rem 0;
    }

    .hero-badge {
      display: inline-flex;
      align-items: center;
      gap: 0.55rem;
      padding: 0.4rem 1.2rem;
      border-radius: 999px;
      background: rgba(6, 182, 212, 0.1);
      border: 1px solid rgba(6, 182, 212, 0.25);
      color: var(--cyan);
      font-size: 0.82rem;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.8px;
      margin-bottom: 0.6rem;
      box-shadow: 0 0 20px rgba(6, 182, 212, 0.2);
    }

    .hero-title {
      font-family: 'Outfit', sans-serif;
      font-size: clamp(2.2rem, 5.5vw, 3.8rem);
      font-weight: 900;
      line-height: 1.15;
      margin-bottom: 0.5rem;
      background: var(--grad-primary);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      letter-spacing: -1px;
    }

    .hero-sub {
      font-size: 1.08rem;
      color: var(--text-sub);
      max-width: 720px;
      margin: 0 auto;
    }

    /* WORKBENCH TABS */
    .tabs-wrapper {
      display: flex;
      justify-content: center;
      margin-bottom: 1.5rem;
    }

    .tabs-header {
      display: flex;
      gap: 0.6rem;
      background: var(--bg-glass);
      backdrop-filter: blur(25px);
      padding: 0.4rem;
      border-radius: 22px;
      border: 1px solid var(--border-line);
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
    }

    .tab-trigger {
      padding: 0.75rem 1.8rem;
      border-radius: 18px;
      border: none;
      background: transparent;
      color: var(--text-sub);
      font-family: 'Outfit', sans-serif;
      font-weight: 800;
      font-size: 1rem;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.65rem;
    }

    .tab-trigger.active {
      background: var(--grad-button);
      color: #ffffff;
      box-shadow: 0 8px 24px var(--cyan);
      transform: scale(1.02);
    }

    /* MAIN APP CARD */
    .app-card {
      background: var(--bg-glass);
      backdrop-filter: blur(40px);
      border-radius: 36px;
      box-shadow: var(--shadow-card);
      border: 1px solid var(--border-line);
      padding: 2.2rem;
      min-height: 520px;
    }

    @media (max-width: 640px) {
      .app-card {
        padding: 1.2rem;
        border-radius: 26px;
      }
    }

    /* TOOLBAR & PRESET CHIPS */
    .toolbar-bar {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
      padding-bottom: 1.3rem;
      margin-bottom: 1.6rem;
      border-bottom: 1px solid var(--border-line);
    }

    .tone-selector {
      display: flex;
      align-items: center;
      gap: 0.6rem;
      background: var(--bg-card);
      padding: 0.45rem 1rem;
      border-radius: 16px;
      border: 1px solid var(--border-line);
      font-size: 0.88rem;
      color: var(--text-sub);
    }

    .tone-select {
      background: transparent;
      border: none;
      color: var(--text-bright);
      font-weight: 700;
      font-size: 0.92rem;
      cursor: pointer;
      outline: none;
    }

    .tone-select option {
      background-color: var(--bg-body);
      color: var(--text-bright);
    }

    .preset-chips {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
    }

    .chip {
      padding: 0.4rem 0.9rem;
      border-radius: 999px;
      background: var(--bg-card);
      border: 1px solid var(--border-line);
      color: var(--text-sub);
      font-size: 0.82rem;
      font-weight: 600;
      cursor: pointer;
    }

    .chip:hover {
      border-color: var(--cyan);
      color: var(--cyan);
      transform: translateY(-1px);
    }

    /* TRANSLATION GRID */
    .translator-grid {
      display: grid;
      grid-template-columns: 1fr 56px 1fr;
      gap: 1.4rem;
      align-items: stretch;
    }

    @media (max-width: 880px) {
      .translator-grid {
        grid-template-columns: 1fr;
        gap: 1rem;
      }
      .swap-col {
        display: flex;
        justify-content: center;
        margin: 0.2rem 0;
      }
    }

    .lang-card {
      background: var(--bg-card);
      border: 1px solid var(--border-line);
      border-radius: 28px;
      padding: 1.4rem;
      display: flex;
      flex-direction: column;
      gap: 1.1rem;
      position: relative;
    }

    .lang-card:focus-within {
      border-color: var(--border-focus);
      box-shadow: 0 0 30px rgba(6, 182, 212, 0.25);
    }

    .lang-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 0.6rem;
    }

    .lang-title-badge {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      font-size: 0.82rem;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.6px;
      color: var(--cyan);
    }

    .status-pill {
      display: none;
      align-items: center;
      gap: 0.4rem;
      padding: 0.25rem 0.65rem;
      border-radius: 999px;
      font-size: 0.75rem;
      font-weight: 700;
    }

    .status-pill.recording {
      display: inline-flex;
      background: rgba(239, 68, 68, 0.15);
      border: 1px solid rgba(239, 68, 68, 0.4);
      color: #ef4444;
      animation: pulseText 1.5s infinite;
    }

    .status-pill.speaking {
      display: inline-flex;
      background: rgba(16, 185, 129, 0.15);
      border: 1px solid rgba(16, 185, 129, 0.4);
      color: #10b981;
    }

    @keyframes pulseText {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.5; }
    }

    .lang-select-wrapper {
      position: relative;
      width: 100%;
    }

    .lang-select {
      width: 100%;
      padding: 0.75rem 1.1rem;
      background: var(--bg-input);
      border: 1px solid var(--border-line);
      border-radius: 16px;
      color: var(--text-bright);
      font-weight: 700;
      font-size: 1rem;
      outline: none;
      cursor: pointer;
      appearance: none;
    }

    .swap-btn {
      width: 52px;
      height: 52px;
      border-radius: 50%;
      background: var(--bg-card);
      border: 1px solid var(--border-line);
      color: var(--text-bright);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.2rem;
      cursor: pointer;
      margin: auto;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
    }

    .swap-btn:hover {
      transform: rotate(180deg) scale(1.1);
      border-color: var(--cyan);
      color: var(--cyan);
      box-shadow: 0 0 25px rgba(6, 182, 212, 0.35);
    }

    .text-area {
      width: 100%;
      min-height: 220px;
      background: var(--bg-input);
      border: 1px solid var(--border-line);
      border-radius: 20px;
      padding: 1.2rem;
      color: var(--text-bright);
      font-family: inherit;
      font-size: 1.08rem;
      line-height: 1.65;
      resize: vertical;
      outline: none;
    }

    .text-area:focus {
      border-color: var(--border-focus);
    }

    .panel-footer {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 0.8rem;
      margin-top: auto;
      padding-top: 0.4rem;
      flex-wrap: wrap;
    }

    .action-btn-group {
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .icon-btn {
      width: 42px;
      height: 42px;
      border-radius: 14px;
      border: 1px solid var(--border-line);
      background: var(--bg-input);
      color: var(--text-sub);
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      font-size: 1.05rem;
      position: relative;
    }

    .icon-btn:hover {
      color: var(--cyan);
      border-color: var(--cyan);
      transform: translateY(-2px);
    }

    .icon-btn.mic-btn:hover {
      color: #ef4444;
      border-color: #ef4444;
    }

    .icon-btn.speaker-btn:hover {
      color: #10b981;
      border-color: #10b981;
    }

    .icon-btn.recording {
      background: #ef4444;
      color: #ffffff !important;
      border-color: #ef4444;
      animation: pulseMic 1.4s infinite;
    }

    @keyframes pulseMic {
      0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.6); }
      70% { box-shadow: 0 0 0 14px rgba(239, 68, 68, 0); }
      100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
    }

    /* TTS AUDIO CONTROLS & EQUALIZER */
    .audio-controls {
      display: flex;
      align-items: center;
      gap: 0.65rem;
    }

    .speed-select {
      padding: 0.4rem 0.75rem;
      background: var(--bg-input);
      border: 1px solid var(--border-line);
      border-radius: 10px;
      color: var(--text-sub);
      font-size: 0.82rem;
      font-weight: 700;
      outline: none;
    }

    .soundwave {
      display: none;
      align-items: center;
      gap: 4px;
      height: 20px;
    }

    .soundwave.playing {
      display: flex;
    }

    .wave-bar {
      width: 3.5px;
      height: 100%;
      background: var(--grad-speaker);
      border-radius: 4px;
      animation: waveDance 0.8s ease-in-out infinite alternate;
    }
    .wave-bar:nth-child(2) { animation-delay: 0.15s; }
    .wave-bar:nth-child(3) { animation-delay: 0.35s; }
    .wave-bar:nth-child(4) { animation-delay: 0.5s; }

    @keyframes waveDance {
      0% { height: 4px; }
      100% { height: 20px; }
    }

    /* PICTURE SCAN SECTION */
    .picture-scan-section {
      display: none;
    }

    .picture-scan-section.active {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1.6rem;
    }

    @media (max-width: 880px) {
      .picture-scan-section.active {
        grid-template-columns: 1fr;
      }
    }

    .upload-box {
      border: 2px dashed var(--border-line);
      border-radius: 28px;
      padding: 3rem 1.8rem;
      text-align: center;
      background: var(--bg-card);
      cursor: pointer;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 320px;
      position: relative;
      overflow: hidden;
    }

    .upload-box:hover {
      border-color: var(--cyan);
      background: rgba(6, 182, 212, 0.05);
    }

    .upload-icon {
      font-size: 3.6rem;
      background: var(--grad-primary);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 1rem;
    }

    .mobile-cam-btn {
      margin-top: 1.2rem;
      padding: 0.75rem 1.6rem;
      border-radius: 999px;
      background: var(--grad-button);
      color: #ffffff;
      font-weight: 800;
      font-size: 0.95rem;
      border: none;
      display: inline-flex;
      align-items: center;
      gap: 0.6rem;
      box-shadow: 0 6px 20px var(--cyan);
    }

    .image-preview-container {
      width: 100%;
      height: 100%;
      max-height: 380px;
      position: relative;
      display: none;
    }

    .image-preview-container img {
      width: 100%;
      height: 100%;
      object-fit: contain;
      border-radius: 20px;
    }

    .scan-line {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 4px;
      background: var(--grad-primary);
      box-shadow: 0 0 20px var(--cyan);
      display: none;
      animation: scanLaser 2s ease-in-out infinite alternate;
    }

    @keyframes scanLaser {
      0% { top: 5%; }
      100% { top: 92%; }
    }

    .scan-progress {
      margin-top: 1.2rem;
      width: 100%;
      display: none;
    }

    .progress-bar-bg {
      width: 100%;
      height: 10px;
      background: var(--bg-input);
      border-radius: 999px;
      overflow: hidden;
    }

    .progress-bar-fill {
      height: 100%;
      width: 0%;
      background: var(--grad-button);
      transition: width 0.3s ease;
    }

    /* ZENI AI BOT DRAWER */
    .bot-drawer {
      position: fixed;
      top: 0;
      right: -450px;
      width: 100%;
      max-width: 420px;
      height: 100vh;
      background: var(--bg-glass);
      backdrop-filter: blur(40px);
      border-left: 1px solid var(--border-line);
      z-index: 100;
      box-shadow: -25px 0 70px rgba(0, 0, 0, 0.5);
      display: flex;
      flex-direction: column;
      transition: right 0.35s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .bot-drawer.open {
      right: 0;
    }

    .bot-header {
      padding: 1.3rem 1.6rem;
      border-bottom: 1px solid var(--border-line);
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: var(--bg-card);
    }

    .bot-badge {
      display: flex;
      align-items: center;
      gap: 0.8rem;
    }

    .bot-avatar {
      width: 42px;
      height: 42px;
      border-radius: 14px;
      background: var(--grad-button);
      display: flex;
      align-items: center;
      justify-content: center;
      color: #fff;
      font-size: 1.2rem;
    }

    .bot-chat-body {
      flex: 1;
      padding: 1.3rem;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 1.1rem;
    }

    .chat-bubble {
      max-width: 88%;
      padding: 0.95rem 1.2rem;
      border-radius: 20px;
      font-size: 0.94rem;
      line-height: 1.55;
    }

    .chat-bubble.bot {
      background: var(--bg-card);
      border: 1px solid var(--border-line);
      color: var(--text-bright);
      align-self: flex-start;
      border-top-left-radius: 4px;
    }

    .chat-bubble.user {
      background: var(--grad-button);
      color: #ffffff;
      align-self: flex-end;
      border-top-right-radius: 4px;
    }

    .bot-input-area {
      padding: 1.2rem;
      border-top: 1px solid var(--border-line);
      display: flex;
      gap: 0.7rem;
      background: var(--bg-card);
    }

    .bot-input {
      flex: 1;
      padding: 0.85rem 1.1rem;
      background: var(--bg-input);
      border: 1px solid var(--border-line);
      border-radius: 16px;
      color: var(--text-bright);
      outline: none;
    }

    /* OPTIONAL AUTH & PROFILE STYLES */
    .google-auth-btn {
      width: 100%;
      padding: 0.95rem 1.2rem;
      border-radius: 16px;
      border: 1px solid var(--border-line);
      background: rgba(255, 255, 255, 0.08);
      color: var(--text-bright);
      font-weight: 700;
      font-size: 0.98rem;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.75rem;
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .google-auth-btn:hover {
      background: rgba(66, 133, 244, 0.15);
      border-color: #4285f4;
      transform: translateY(-2px);
      box-shadow: 0 8px 25px rgba(66, 133, 244, 0.3);
    }

    /* FORM & BUTTON CSS FIXES */
    .auth-tabs {
      display: flex;
      gap: 0.5rem;
      margin-bottom: 0.5rem;
      background: var(--bg-card);
      padding: 0.35rem;
      border-radius: 16px;
      border: 1px solid var(--border-line);
    }

    .auth-tab-btn {
      flex: 1;
      padding: 0.75rem;
      border: none;
      background: transparent;
      color: var(--text-sub);
      font-weight: 700;
      font-size: 0.92rem;
      border-radius: 12px;
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .auth-tab-btn.active {
      background: var(--grad-button);
      color: #ffffff;
      box-shadow: 0 4px 15px rgba(6, 182, 212, 0.3);
    }

    .form-group {
      margin-bottom: 1.1rem;
      text-align: left;
    }

    .form-label {
      display: block;
      font-size: 0.88rem;
      font-weight: 700;
      color: var(--text-sub);
      margin-bottom: 0.45rem;
    }

    .form-input {
      width: 100%;
      padding: 0.9rem 1.1rem;
      background: var(--bg-input);
      border: 1px solid var(--border-line);
      border-radius: 16px;
      color: var(--text-bright);
      font-size: 0.95rem;
      outline: none;
      transition: border-color 0.2s ease;
    }

    .form-input:focus {
      border-color: var(--cyan);
      box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.15);
    }

    .auth-submit-btn {
      width: 100%;
      padding: 0.95rem;
      border-radius: 16px;
      border: none;
      background: var(--grad-button);
      color: #ffffff;
      font-weight: 800;
      font-size: 1.05rem;
      cursor: pointer;
      transition: all 0.2s ease;
      box-shadow: 0 6px 20px rgba(6, 182, 212, 0.3);
    }

    .auth-submit-btn:hover {
      transform: translateY(-2px);
      box-shadow: 0 10px 28px rgba(6, 182, 212, 0.45);
    }

    /* GOOGLE ACCOUNT SELECTOR MODAL */
    .google-modal-overlay {
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.82);
      backdrop-filter: blur(24px);
      z-index: 1100;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 1.2rem;
    }

    .google-modal-overlay.active {
      display: flex;
    }

    .google-modal-card {
      width: min(100%, 440px);
      background: var(--bg-glass);
      backdrop-filter: blur(30px);
      border: 1px solid var(--border-line);
      border-radius: 28px;
      padding: 2.2rem;
      position: relative;
      box-shadow: 0 25px 60px rgba(0, 0, 0, 0.7);
      animation: popIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }

    @keyframes popIn {
      from { transform: scale(0.9) translateY(10px); opacity: 0; }
      to { transform: scale(1) translateY(0); opacity: 1; }
    }

    .google-account-list {
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
      margin-top: 0.5rem;
    }

    .google-account-card {
      display: flex;
      align-items: center;
      gap: 0.9rem;
      padding: 0.85rem 1rem;
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid var(--border-line);
      border-radius: 16px;
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .google-account-card:hover {
      background: rgba(66, 133, 244, 0.14);
      border-color: #4285f4;
      transform: translateY(-2px);
    }

    .google-avatar-badge {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      background: linear-gradient(135deg, #4285f4, #8b5cf6);
      color: white;
      font-weight: 800;
      font-size: 1.1rem;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .app-blur-lock {
      filter: blur(16px);
      pointer-events: none !important;
      user-select: none !important;
      transition: filter 0.4s ease;
    }

    /* INSIGHT CARD */
    .insight-card {
      margin-top: 1.6rem;
      background: var(--bg-card);
      border: 1px dashed var(--border-line);
      border-radius: 22px;
      padding: 1.1rem 1.5rem;
      font-size: 0.95rem;
      color: var(--text-sub);
      display: flex;
      align-items: center;
      gap: 0.9rem;
    }

    /* TOAST NOTIFICATIONS */
    .toast-container {
      position: fixed;
      bottom: 85px;
      right: 24px;
      z-index: 300;
      display: flex;
      flex-direction: column;
      gap: 10px;
      pointer-events: none;
    }

    .toast {
      padding: 0.8rem 1.3rem;
      border-radius: 16px;
      background: var(--bg-glass);
      backdrop-filter: blur(25px);
      border: 1px solid var(--border-glow);
      color: var(--text-bright);
      font-size: 0.88rem;
      font-weight: 700;
      box-shadow: 0 12px 35px rgba(0,0,0,0.4);
      display: flex;
      align-items: center;
      gap: 0.75rem;
      animation: toastIn 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
      pointer-events: auto;
    }

    @keyframes toastIn {
      from { opacity: 0; transform: translateY(20px) scale(0.95); }
      to { opacity: 1; transform: translateY(0) scale(1); }
    }

    /* TRANSLATION HISTORY & DRAWER STYLES */
    .badge-count {
      background: linear-gradient(135deg, var(--cyan), var(--indigo));
      color: white;
      font-size: 0.7rem;
      font-weight: 700;
      padding: 0.15rem 0.45rem;
      border-radius: 9999px;
      margin-left: 0.25rem;
    }

    .history-drawer {
      position: fixed;
      top: 0;
      right: -440px;
      width: 400px;
      max-width: 100vw;
      height: 100vh;
      background: var(--card-bg);
      backdrop-filter: blur(24px);
      border-left: 1px solid var(--border-line);
      z-index: 100;
      display: flex;
      flex-direction: column;
      transition: right 0.35s cubic-bezier(0.16, 1, 0.3, 1);
      box-shadow: -10px 0 40px rgba(0, 0, 0, 0.4);
    }

    .history-drawer.open {
      right: 0;
    }

    .history-body {
      flex: 1;
      overflow-y: auto;
      padding: 1.25rem;
      display: flex;
      flex-direction: column;
      gap: 0.9rem;
    }

    .history-card {
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid var(--border-line);
      border-radius: 14px;
      padding: 0.9rem;
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
      transition: all 0.2s ease;
    }

    .history-card:hover {
      border-color: var(--cyan);
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
    }

    .history-card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 0.78rem;
      color: var(--text-muted);
    }

    .history-lang-tag {
      font-weight: 600;
      color: var(--cyan);
      background: rgba(6, 182, 212, 0.12);
      padding: 0.2rem 0.55rem;
      border-radius: 6px;
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      font-size: 0.75rem;
    }

    .history-source-text {
      font-size: 0.88rem;
      color: var(--text-main);
      font-weight: 500;
      white-space: pre-wrap;
      line-height: 1.4;
    }

    .history-target-text {
      font-size: 0.92rem;
      color: var(--violet);
      font-weight: 600;
      white-space: pre-wrap;
      background: rgba(139, 92, 246, 0.08);
      padding: 0.5rem;
      border-radius: 8px;
      line-height: 1.4;
    }

    .history-actions {
      display: flex;
      justify-content: flex-end;
      gap: 0.4rem;
      margin-top: 0.2rem;
    }

    .history-empty {
      text-align: center;
      padding: 3.5rem 1rem;
      color: var(--text-muted);
    }

    /* MOBILE BOTTOM NAVBAR */
    .mobile-nav-bar {
      display: none;
      position: fixed;
      bottom: 0;
      left: 0;
      right: 0;
      height: 66px;
      background: var(--mobile-nav-bg);
      backdrop-filter: blur(24px);
      border-top: 1px solid var(--border-line);
      z-index: 90;
      align-items: center;
      justify-content: space-around;
      padding: 0 0.5rem;
    }

    @media (max-width: 768px) {
      .mobile-nav-bar { display: flex; }
      .tabs-header { display: none; }
      .desktop-only { display: none; }
      .toast-container { bottom: 80px; right: 12px; left: 12px; }
      .history-drawer { width: 100vw; right: -100vw; }
    }

    .mobile-nav-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 3px;
      background: none;
      border: none;
      color: var(--text-sub);
      font-size: 0.72rem;
      font-weight: 700;
      cursor: pointer;
      flex: 1;
    }

    .mobile-nav-item i { font-size: 1.3rem; }
    .mobile-nav-item.active { color: var(--cyan); }
  </style>
</head>
<body>
  <!-- Ambient Orbs -->
  <div class="bg-orb orb-1"></div>
  <div class="bg-orb orb-2"></div>

  <!-- TOAST NOTIFICATION CONTAINER -->
  <div class="toast-container" id="toastContainer"></div>

  <!-- TOP NAVBAR -->
  <nav class="navbar">
    <a class="brand-logo" onclick="switchTab('translate')">
      <div class="brand-icon">
        <i class="fa-solid fa-language"></i>
      </div>
      <span class="brand-title">Zeni Translate</span>
    </a>

    <div class="nav-actions">
      <!-- Theme Switcher -->
      <button class="nav-btn" id="themeToggleBtn" onclick="toggleTheme()" title="Toggle Theme">
        <i class="fa-solid fa-moon" id="themeIcon"></i>
        <span id="themeLabel" class="desktop-only">Dark</span>
      </button>

      <!-- Zeni Bot Trigger -->
      <button class="nav-btn" onclick="toggleBotDrawer()" title="Open Zeni AI Assistant">
        <i class="fa-solid fa-robot"></i>
        <span class="desktop-only">Zeni Bot</span>
      </button>

      <!-- History Trigger -->
      <button class="nav-btn" onclick="toggleHistoryDrawer()" title="View Translation History">
        <i class="fa-solid fa-clock-rotate-left"></i>
        <span class="desktop-only">History</span>
        <span class="badge-count" id="historyBadge">0</span>
      </button>

      <!-- Account / Login -->
      <button class="nav-btn primary-btn" id="userAuthBtn" onclick="openAuthModal()">
        <i class="fa-solid fa-user"></i>
        <span id="userAuthLabel" class="desktop-only">Sign In</span>
      </button>
    </div>
  </nav>

  <!-- MAIN CONTAINER -->
  <main class="container">
    <!-- HERO HEADER -->
    <div class="hero-header">
      <div class="hero-badge">
        <i class="fa-solid fa-wand-magic-sparkles"></i> AI Voice, Text & OCR Translation Studio
      </div>
      <h1 class="hero-title">Translate, Speak & Listen Instantly</h1>
      <p class="hero-sub">Dual-sided speech listening, natural voiceover synthesis, picture OCR scanner, and AI language assistant.</p>
    </div>

    <!-- TABS HEADER -->
    <div class="tabs-wrapper">
      <div class="tabs-header">
        <button class="tab-trigger active" id="tabBtnTranslate" onclick="switchTab('translate')">
          <i class="fa-solid fa-font"></i> Text & Voice Studio
        </button>
        <button class="tab-trigger" id="tabBtnScan" onclick="switchTab('scan')">
          <i class="fa-solid fa-camera"></i> Picture Scan OCR
        </button>
      </div>
    </div>

    <!-- MAIN APP CARD -->
    <div class="app-card">
      
      <!-- TOOLBAR & PRESETS -->
      <div class="toolbar-bar">
        <div class="tone-selector">
          <i class="fa-solid fa-sliders"></i>
          <span>Tone:</span>
          <select class="tone-select" id="toneSelect" onchange="triggerTranslation()">
            <option value="standard">Standard / Natural</option>
            <option value="formal">Formal & Polite</option>
            <option value="casual">Casual Conversation</option>
            <option value="business">Professional Business</option>
            <option value="simplified">Simplified</option>
          </select>
        </div>

        <div class="preset-chips">
          <button class="chip" onclick="setPreset('Hello, how are you today?')">👋 Greetings</button>
          <button class="chip" onclick="setPreset('Thank you very much for your assistance.')">🙏 Thanks</button>
          <button class="chip" onclick="setPreset('Could you please help me with this?')">💼 Request</button>
          <button class="chip" onclick="setPreset('Where is the nearest train station?')">🗺️ Travel</button>
          <button class="chip" onclick="setPreset('I need medical assistance.')">🚨 Emergency</button>
        </div>
      </div>

      <!-- TEXT TRANSLATOR SECTION -->
      <div id="sectionTranslate">
        <div class="translator-grid">
          
          <!-- SOURCE PANEL (INPUT / LISTEN / SPEAK) -->
          <div class="lang-card">
            <div class="lang-header">
              <div class="lang-title-badge">
                <i class="fa-solid fa-globe"></i> Source Language
              </div>
              <div class="status-pill" id="sourceRecBadge">
                <i class="fa-solid fa-microphone"></i> Listening...
              </div>
              <div class="status-pill" id="sourceSpeakBadge">
                <i class="fa-solid fa-volume-high"></i> Speaking...
              </div>
            </div>

            <div class="lang-select-wrapper">
              <select class="lang-select" id="sourceLang" onchange="triggerTranslation()">
                {% for code, name in languages.items() %}
                <option value="{{ code }}" {% if code == 'en' %}selected{% endif %}>{{ name }}</option>
                {% endfor %}
              </select>
            </div>

            <textarea class="text-area" id="sourceText" placeholder="Type, paste, or tap mic to speak in Source language..." oninput="onSourceInput()"></textarea>

            <div class="panel-footer">
              <div class="action-btn-group">
                <!-- Source Mic Listening Button -->
                <button class="icon-btn mic-btn" id="sourceMicBtn" onclick="toggleSpeechRecognition('source')" title="Listen / Voice Input (Source)">
                  <i class="fa-solid fa-microphone"></i>
                </button>

                <!-- Source Speaker TTS Button -->
                <button class="icon-btn speaker-btn" id="sourceTtsBtn" onclick="playVoiceover('source')" title="Speak / Read Source Text">
                  <i class="fa-solid fa-volume-high"></i>
                </button>

                <!-- Copy & Paste & Clear -->
                <button class="icon-btn" onclick="pasteText('sourceText')" title="Paste text from clipboard">
                  <i class="fa-solid fa-paste"></i>
                </button>
                <button class="icon-btn" onclick="clearText('source')" title="Clear Source Text">
                  <i class="fa-solid fa-xmark"></i>
                </button>
              </div>

              <!-- Audio Speed & Waveform Equalizer -->
              <div class="audio-controls">
                <div class="soundwave" id="sourceSoundwave">
                  <div class="wave-bar"></div>
                  <div class="wave-bar"></div>
                  <div class="wave-bar"></div>
                  <div class="wave-bar"></div>
                </div>
                <select class="speed-select" id="sourceAudioSpeed" title="Source Voiceover Speed">
                  <option value="0.75">0.75x</option>
                  <option value="1.0" selected>1.0x</option>
                  <option value="1.25">1.25x</option>
                  <option value="1.5">1.5x</option>
                </select>
                <span style="font-size: 0.8rem; color: var(--text-muted);" id="sourceCharCount">0 chars</span>
              </div>
            </div>
          </div>

          <!-- SWAP BUTTON -->
          <div class="swap-col">
            <button class="swap-btn" onclick="swapLanguages()" title="Swap Languages & Text">
              <i class="fa-solid fa-right-left"></i>
            </button>
          </div>

          <!-- TARGET PANEL (OUTPUT / LISTEN / SPEAK) -->
          <div class="lang-card">
            <div class="lang-header">
              <div class="lang-title-badge" style="color: var(--violet);">
                <i class="fa-solid fa-language"></i> Target Translation
              </div>
              <div class="status-pill" id="targetRecBadge">
                <i class="fa-solid fa-microphone"></i> Target Listening...
              </div>
              <div class="status-pill" id="targetSpeakBadge">
                <i class="fa-solid fa-volume-high"></i> Speaking...
              </div>
            </div>

            <div class="lang-select-wrapper">
              <select class="lang-select" id="targetLang" onchange="triggerTranslation()">
                {% for code, name in languages.items() %}
                <option value="{{ code }}" {% if code == 'te' %}selected{% endif %}>{{ name }}</option>
                {% endfor %}
              </select>
            </div>

            <textarea class="text-area" id="targetText" placeholder="Translation will appear here, or tap mic to speak in Target language..." oninput="onTargetInput()"></textarea>

            <div class="panel-footer">
              <div class="action-btn-group">
                <!-- Target Mic Listening Button -->
                <button class="icon-btn mic-btn" id="targetMicBtn" onclick="toggleSpeechRecognition('target')" title="Listen / Voice Input (Target)">
                  <i class="fa-solid fa-microphone"></i>
                </button>

                <!-- Target Speaker TTS Button -->
                <button class="icon-btn speaker-btn" id="targetTtsBtn" onclick="playVoiceover('target')" title="Speak / Read Target Translation">
                  <i class="fa-solid fa-volume-high"></i>
                </button>

                <!-- Reverse Translate & Copy -->
                <button class="icon-btn" onclick="reverseTranslation()" title="Translate Target back to Source">
                  <i class="fa-solid fa-arrow-rotate-left"></i>
                </button>
                <button class="icon-btn" onclick="copyText('targetText', 'Target translation')" title="Copy Translation">
                  <i class="fa-solid fa-copy"></i>
                </button>
              </div>

              <!-- Audio Speed & Waveform Equalizer -->
              <div class="audio-controls">
                <div class="soundwave" id="targetSoundwave">
                  <div class="wave-bar"></div>
                  <div class="wave-bar"></div>
                  <div class="wave-bar"></div>
                  <div class="wave-bar"></div>
                </div>
                <select class="speed-select" id="targetAudioSpeed" title="Target Voiceover Speed">
                  <option value="0.75">0.75x</option>
                  <option value="1.0" selected>1.0x</option>
                  <option value="1.25">1.25x</option>
                  <option value="1.5">1.5x</option>
                </select>
                <span style="font-size: 0.8rem; color: var(--text-muted);" id="targetCharCount">0 chars</span>
              </div>
            </div>
          </div>

        </div>

        <!-- INSIGHT CARD -->
        <div class="insight-card" id="insightCard">
          <i class="fa-solid fa-wand-magic-sparkles" style="color: var(--cyan); font-size: 1.25rem;"></i>
          <span id="insightText">Select source & target languages to translate automatically. Mic listening & voice playback active on both sides!</span>
        </div>
      </div>

      <!-- PICTURE SCAN SECTION (OCR) -->
      <div id="sectionScan" class="picture-scan-section">
        
        <!-- UPLOAD / PREVIEW BOX -->
        <div class="upload-box" id="dropZone" onclick="document.getElementById('imageFileInput').click()">
          <input type="file" id="imageFileInput" accept="image/*" style="display: none;" onchange="handleImageUpload(event)" />
          
          <div id="uploadPlaceholder">
            <i class="fa-solid fa-camera-retro upload-icon"></i>
            <h3 style="font-family: 'Outfit', sans-serif; font-size: 1.4rem; margin-bottom: 0.4rem;">Tap to Scan Picture</h3>
            <p style="color: var(--text-sub); font-size: 0.95rem;">Upload from Gallery or Take Photo with Camera</p>
            <div class="mobile-cam-btn">
              <i class="fa-solid fa-camera"></i> Open Camera / Gallery
            </div>
          </div>

          <div class="image-preview-container" id="imagePreviewContainer">
            <img id="imagePreview" src="" alt="Picture preview" />
            <div class="scan-line" id="scanLine"></div>
          </div>

          <div class="scan-progress" id="scanProgress">
            <div class="progress-bar-bg">
              <div class="progress-bar-fill" id="scanProgressFill"></div>
            </div>
            <p style="font-size: 0.88rem; color: var(--text-sub); margin-top: 0.6rem;" id="scanStatusText">Scanning image text...</p>
          </div>
        </div>

        <!-- EXTRACTED & TRANSLATED OCR TEXT -->
        <div class="lang-card">
          <div style="font-family: 'Outfit', sans-serif; font-weight: 800; font-size: 1.15rem; color: var(--cyan); display: flex; align-items: center; gap: 0.6rem;">
            <i class="fa-solid fa-file-lines"></i> Scanned OCR Result
          </div>

          <div style="display: flex; flex-direction: column; gap: 0.9rem; height: 100%;">
            <label class="form-label">Extracted Text from Image:</label>
            <textarea class="text-area" id="extractedOcrText" style="min-height: 110px;" placeholder="Extracted text will appear here..." readonly></textarea>

            <label class="form-label">Translation:</label>
            <textarea class="text-area" id="translatedOcrText" style="min-height: 110px;" placeholder="Translated text will appear here..." readonly></textarea>
          </div>

          <div class="panel-footer">
            <button class="nav-btn primary-btn" style="width: 100%; justify-content: center;" onclick="translateScannedText()">
              <i class="fa-solid fa-rotate"></i> Translate Extracted Text
            </button>
          </div>
        </div>

      </div>

    </div>
  </main>

  <!-- MOBILE BOTTOM NAVBAR -->
  <div class="mobile-nav-bar">
    <button class="mobile-nav-item active" id="mobNavTranslate" onclick="switchTab('translate')">
      <i class="fa-solid fa-language"></i>
      <span>Translate</span>
    </button>
    <button class="mobile-nav-item" id="mobNavScan" onclick="switchTab('scan')">
      <i class="fa-solid fa-camera"></i>
      <span>Scan Pic</span>
    </button>
    <button class="mobile-nav-item" onclick="toggleBotDrawer()">
      <i class="fa-solid fa-robot"></i>
      <span>AI Bot</span>
    </button>
    <button class="mobile-nav-item" id="mobNavHistory" onclick="toggleHistoryDrawer()">
      <i class="fa-solid fa-clock-rotate-left"></i>
      <span>History</span>
    </button>
    <button class="mobile-nav-item" onclick="toggleTheme()">
      <i class="fa-solid fa-moon" id="mobThemeIcon"></i>
      <span>Theme</span>
    </button>
  </div>

  <!-- ZENI AI BOT DRAWER -->
  <aside class="bot-drawer" id="botDrawer">
    <div class="bot-header">
      <div class="bot-badge">
        <div class="bot-avatar">
          <i class="fa-solid fa-robot"></i>
        </div>
        <div>
          <h4 style="font-family: 'Outfit', sans-serif; font-size: 1.1rem;">Zeni Assistant</h4>
          <span style="font-size: 0.78rem; color: var(--emerald);">● Online & Ready</span>
        </div>
      </div>
      <button class="icon-btn" onclick="toggleBotDrawer()"><i class="fa-solid fa-xmark"></i></button>
    </div>

    <div class="bot-chat-body" id="botChatBody">
      <div class="chat-bubble bot">
        👋 Hi! I am <strong>Zeni Bot</strong>, your AI translation assistant. Ask me questions about words, grammar, rephrasing, or voice speech tips!
      </div>
    </div>

    <div class="bot-input-area">
      <input type="text" class="bot-input" id="botInput" placeholder="Ask Zeni Bot..." onkeydown="if(event.key === 'Enter') sendBotMessage()" />
      <button class="nav-btn primary-btn" onclick="sendBotMessage()"><i class="fa-solid fa-paper-plane"></i></button>
    </div>
  </aside>

  <!-- TRANSLATION HISTORY DRAWER -->
  <aside class="history-drawer" id="historyDrawer">
    <div class="bot-header">
      <div class="bot-badge">
        <div class="bot-avatar" style="background: linear-gradient(135deg, #ec4899, #8b5cf6);">
          <i class="fa-solid fa-clock-rotate-left"></i>
        </div>
        <div>
          <h4 style="font-family: 'Outfit', sans-serif; font-size: 1.1rem;">Translation History</h4>
          <span style="font-size: 0.78rem; color: var(--text-muted);" id="historyCountSub">0 items saved</span>
        </div>
      </div>
      <div style="display: flex; gap: 0.5rem; align-items: center;">
        <button class="icon-btn" onclick="clearAllHistory()" title="Clear All History" style="color: #ef4444;"><i class="fa-solid fa-trash-can"></i></button>
        <button class="icon-btn" onclick="toggleHistoryDrawer()"><i class="fa-solid fa-xmark"></i></button>
      </div>
    </div>

    <div class="history-body" id="historyBody">
      <!-- History items rendered dynamically -->
    </div>
  </aside>



  <!-- GOOGLE ACCOUNT SELECTOR MODAL -->
  <div class="google-modal-overlay" id="googleAccountModal">
    <div class="google-modal-card">
      <button class="icon-btn" style="position: absolute; top: 1.2rem; right: 1.2rem;" onclick="closeGoogleModal()">
        <i class="fa-solid fa-xmark"></i>
      </button>

      <div style="text-align: center; margin-bottom: 1.2rem;">
        <svg width="36" height="36" viewBox="0 0 24 24" style="margin-bottom: 0.5rem;">
          <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
          <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
          <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
          <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
        </svg>
        <h3 style="font-family: 'Outfit', sans-serif; font-size: 1.4rem; margin-bottom: 0.2rem;">Choose a Google Account</h3>
        <p style="color: var(--text-sub); font-size: 0.85rem;">to continue to <strong>Zeni Translate</strong></p>
      </div>

      <div class="google-account-list">
        <!-- 1-Click Fast Account -->
        <div class="google-account-card" onclick="loginWithGoogleAccount('Harsha Vardhan', 'harsha625@gmail.com')">
          <div class="google-avatar-badge">H</div>
          <div style="flex: 1;">
            <div style="font-weight: 700; font-size: 0.95rem; color: var(--text-bright);">Harsha Vardhan</div>
            <div style="font-size: 0.8rem; color: var(--text-sub);">harsha625@gmail.com</div>
          </div>
          <i class="fa-solid fa-chevron-right" style="color: var(--text-sub); font-size: 0.85rem;"></i>
        </div>

        <div class="google-account-card" onclick="loginWithGoogleAccount('Zeni User', 'user.zeni@gmail.com')">
          <div class="google-avatar-badge" style="background: linear-gradient(135deg, #10b981, #06b6d4);">Z</div>
          <div style="flex: 1;">
            <div style="font-weight: 700; font-size: 0.95rem; color: var(--text-bright);">Zeni Google Account</div>
            <div style="font-size: 0.8rem; color: var(--text-sub);">user.zeni@gmail.com</div>
          </div>
          <i class="fa-solid fa-chevron-right" style="color: var(--text-sub); font-size: 0.85rem;"></i>
        </div>
      </div>

      <div style="margin-top: 1.2rem; border-top: 1px solid var(--border-line); padding-top: 1rem;">
        <label class="form-label">Or sign in with another Google Email:</label>
        <div style="display: flex; gap: 0.5rem; margin-top: 0.45rem;">
          <input type="email" id="googleCustomEmail" class="form-input" placeholder="name@gmail.com" onkeydown="if(event.key==='Enter') submitCustomGoogleLogin()" />
          <button class="auth-submit-btn" style="width: auto; padding: 0 1.2rem; font-size: 0.9rem;" onclick="submitCustomGoogleLogin()">Sign In</button>
        </div>
      </div>

      <div style="text-align: center; margin-top: 1.2rem; font-size: 0.76rem; color: var(--text-sub);">
        Google will share your name, email address, and language preference with Zeni Translate.
      </div>
    </div>
  </div>

  <script>
    const LANG_SPEECH_CODES = {
      'en': 'en-US',
      'te': 'te-IN',
      'hi': 'hi-IN',
      'ta': 'ta-IN',
      'kn': 'kn-IN',
      'ml': 'ml-IN',
      'bn': 'bn-IN',
      'mr': 'mr-IN',
      'gu': 'gu-IN',
      'pa': 'pa-IN',
      'ur': 'ur-PK',
      'es': 'es-ES',
      'fr': 'fr-FR',
      'de': 'de-DE',
      'it': 'it-IT',
      'pt': 'pt-PT',
      'ru': 'ru-RU',
      'ja': 'ja-JP',
      'ko': 'ko-KR',
      'zh-cn': 'zh-CN',
      'ar': 'ar-SA',
      'tr': 'tr-TR',
      'vi': 'vi-VN',
      'th': 'th-TH',
      'nl': 'nl-NL'
    };

    let translateDebounceTimer = null;
    let activeRecognition = null;
    let activeMicSide = null; // 'source' or 'target'
    let activeAudio = null;
    let activeTTSSide = null; // 'source' or 'target'
    let activeUser = localStorage.getItem('zeni_user') ? JSON.parse(localStorage.getItem('zeni_user')) : null;
    let translationHistory = localStorage.getItem('zeni_history') ? JSON.parse(localStorage.getItem('zeni_history')) : [];

    window.addEventListener('DOMContentLoaded', () => {
      const savedTheme = localStorage.getItem('zeni_theme') || 'dark';
      setTheme(savedTheme);
      updateAuthUI();
      renderHistory();
    });

    function toggleTheme() {
      const currentTheme = document.documentElement.getAttribute('data-theme');
      setTheme(currentTheme === 'dark' ? 'light' : 'dark');
    }

    function setTheme(theme) {
      document.documentElement.setAttribute('data-theme', theme);
      localStorage.setItem('zeni_theme', theme);
      
      const icon = document.getElementById('themeIcon');
      const mobIcon = document.getElementById('mobThemeIcon');
      const label = document.getElementById('themeLabel');
      
      if (theme === 'light') {
        if (icon) icon.className = 'fa-solid fa-sun';
        if (mobIcon) mobIcon.className = 'fa-solid fa-sun';
        if (label) label.textContent = 'Light';
      } else {
        if (icon) icon.className = 'fa-solid fa-moon';
        if (mobIcon) mobIcon.className = 'fa-solid fa-moon';
        if (label) label.textContent = 'Dark';
      }
    }

    function showToast(message, type = 'info') {
      const container = document.getElementById('toastContainer');
      if (!container) return;

      const toast = document.createElement('div');
      toast.className = 'toast';

      let iconClass = 'fa-solid fa-circle-info';
      if (type === 'success') iconClass = 'fa-solid fa-circle-check';
      if (type === 'warning') iconClass = 'fa-solid fa-triangle-exclamation';
      if (type === 'error') iconClass = 'fa-solid fa-circle-xmark';

      toast.innerHTML = `<i class="${iconClass}"></i><span>${message}</span>`;
      container.appendChild(toast);

      setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(10px)';
        setTimeout(() => toast.remove(), 300);
      }, 3200);
    }

    function switchTab(tab) {
      const tabTranslate = document.getElementById('tabBtnTranslate');
      const tabScan = document.getElementById('tabBtnScan');
      const mobTranslate = document.getElementById('mobNavTranslate');
      const mobScan = document.getElementById('mobNavScan');
      const secTranslate = document.getElementById('sectionTranslate');
      const secScan = document.getElementById('sectionScan');

      if (tab === 'translate') {
        if (tabTranslate) tabTranslate.classList.add('active');
        if (tabScan) tabScan.classList.remove('active');
        if (mobTranslate) mobTranslate.classList.add('active');
        if (mobScan) mobScan.classList.remove('active');

        secTranslate.style.display = 'block';
        secScan.classList.remove('active');
      } else {
        if (tabScan) tabScan.classList.add('active');
        if (tabTranslate) tabTranslate.classList.remove('active');
        if (mobScan) mobScan.classList.add('active');
        if (mobTranslate) mobTranslate.classList.remove('active');

        secTranslate.style.display = 'none';
        secScan.classList.add('active');
      }
    }

    function setPreset(text) {
      document.getElementById('sourceText').value = text;
      onSourceInput();
      showToast('Preset text inserted!', 'success');
    }

    function onSourceInput() {
      const text = document.getElementById('sourceText').value;
      document.getElementById('sourceCharCount').textContent = `${text.length} chars`;

      clearTimeout(translateDebounceTimer);
      translateDebounceTimer = setTimeout(triggerTranslation, 400);
    }

    function onTargetInput() {
      const text = document.getElementById('targetText').value;
      document.getElementById('targetCharCount').textContent = `${text.length} chars`;
    }

    async function triggerTranslation() {
      const text = document.getElementById('sourceText').value.trim();
      const source = document.getElementById('sourceLang').value;
      const target = document.getElementById('targetLang').value;
      const tone = document.getElementById('toneSelect').value;

      if (!text) {
        document.getElementById('targetText').value = '';
        document.getElementById('targetCharCount').textContent = '0 chars';
        document.getElementById('insightText').textContent = 'Select source & target languages to translate automatically.';
        return;
      }

      document.getElementById('insightText').textContent = 'Translating with Zeni Neural Engine...';

      try {
        const response = await fetch('/api/translate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text, source, target, tone })
        });

        const data = await response.json();

        if (data.status === 'success') {
          document.getElementById('targetText').value = data.translation;
          onTargetInput();
          let insight = data.explanation || `Translated to ${target.toUpperCase()}`;
          if (data.transliteration) {
            insight += ` | ${data.transliteration}`;
          }
          document.getElementById('insightText').textContent = insight;

          // Save translation to history
          saveToHistory(text, data.translation, source, target);
        } else {
          document.getElementById('insightText').textContent = 'Translation error: ' + (data.error || 'Unable to translate');
        }
      } catch (err) {
        console.error(err);
        document.getElementById('insightText').textContent = 'Network error during translation.';
      }
    }

    async function reverseTranslation() {
      const targetText = document.getElementById('targetText').value.trim();
      const sourceLang = document.getElementById('sourceLang').value;
      const targetLang = document.getElementById('targetLang').value;

      if (!targetText) {
        showToast('Target panel is empty!', 'warning');
        return;
      }

      showToast('Translating target back to source...', 'info');

      try {
        const response = await fetch('/api/translate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: targetText, source: targetLang, target: sourceLang, tone: 'standard' })
        });

        const data = await response.json();
        if (data.status === 'success') {
          document.getElementById('sourceText').value = data.translation;
          onSourceInput();
          showToast('Reverse translation complete!', 'success');
        }
      } catch (err) {
        console.error(err);
        showToast('Error doing reverse translation', 'error');
      }
    }

    function swapLanguages() {
      const s = document.getElementById('sourceLang');
      const t = document.getElementById('targetLang');
      const tempVal = s.value;
      s.value = t.value;
      t.value = tempVal;

      const sText = document.getElementById('sourceText');
      const tText = document.getElementById('targetText');
      const tempText = sText.value;
      sText.value = tText.value;
      tText.value = tempText;

      onSourceInput();
      onTargetInput();
      triggerTranslation();
      showToast('Languages and text swapped!', 'success');
    }

    function clearText(side) {
      if (side === 'source') {
        document.getElementById('sourceText').value = '';
        document.getElementById('sourceCharCount').textContent = '0 chars';
        document.getElementById('targetText').value = '';
        document.getElementById('targetCharCount').textContent = '0 chars';
        document.getElementById('insightText').textContent = 'Cleared input.';
        showToast('Source text cleared', 'info');
      } else {
        document.getElementById('targetText').value = '';
        document.getElementById('targetCharCount').textContent = '0 chars';
        showToast('Target text cleared', 'info');
      }
    }

    async function pasteText(elementId) {
      try {
        const text = await navigator.clipboard.readText();
        if (text) {
          document.getElementById(elementId).value = text;
          if (elementId === 'sourceText') onSourceInput();
          if (elementId === 'targetText') onTargetInput();
          showToast('Pasted from clipboard!', 'success');
        }
      } catch (err) {
        showToast('Clipboard access denied or unavailable.', 'warning');
      }
    }

    function copyText(elementId, label = 'Text') {
      const text = document.getElementById(elementId).value;
      if (!text) {
        showToast('Nothing to copy!', 'warning');
        return;
      }
      navigator.clipboard.writeText(text).then(() => {
        showToast(`${label} copied to clipboard!`, 'success');
      });
    }

    /* SPEECH RECOGNITION (LISTENING) ON BOTH SIDES */
    function toggleSpeechRecognition(side) {
      const isSource = side === 'source';
      const micBtn = document.getElementById(isSource ? 'sourceMicBtn' : 'targetMicBtn');
      const badge = document.getElementById(isSource ? 'sourceRecBadge' : 'targetRecBadge');
      const textArea = document.getElementById(isSource ? 'sourceText' : 'targetText');
      const langSelect = document.getElementById(isSource ? 'sourceLang' : 'targetLang');

      if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        showToast('Speech Recognition is not supported in your browser.', 'error');
        return;
      }

      if (activeRecognition && activeMicSide === side) {
        stopSpeechRecognition();
        showToast(`Stopped ${side} voice listening.`, 'info');
        return;
      }

      if (activeRecognition) {
        stopSpeechRecognition();
      }

      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      activeRecognition = new SpeechRecognition();
      activeMicSide = side;

      const langCode = langSelect.value;
      const speechLang = LANG_SPEECH_CODES[langCode] || langCode;
      
      activeRecognition.lang = speechLang;
      activeRecognition.continuous = false;
      activeRecognition.interimResults = true;

      activeRecognition.onstart = () => {
        if (micBtn) micBtn.classList.add('recording');
        if (badge) badge.classList.add('recording');
        showToast(`Listening in ${langCode.toUpperCase()} (${speechLang}). Speak clearly!`, 'success');
      };

      activeRecognition.onresult = (event) => {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          transcript += event.results[i][0].transcript;
        }
        textArea.value = transcript;
        if (isSource) {
          onSourceInput();
        } else {
          onTargetInput();
        }
      };

      activeRecognition.onerror = (e) => {
        console.warn('Speech recognition notice:', e.error);
        stopSpeechRecognition();
        if (e.error !== 'no-speech') {
          showToast(`Voice mic notice: ${e.error}`, 'warning');
        }
      };

      activeRecognition.onend = () => {
        stopSpeechRecognition();
      };

      try {
        activeRecognition.start();
      } catch (err) {
        console.error(err);
        stopSpeechRecognition();
      }
    }

    function stopSpeechRecognition() {
      if (activeRecognition) {
        try { activeRecognition.stop(); } catch(e){}
        activeRecognition = null;
      }
      activeMicSide = null;
      
      const sourceMic = document.getElementById('sourceMicBtn');
      const targetMic = document.getElementById('targetMicBtn');
      const sourceBadge = document.getElementById('sourceRecBadge');
      const targetBadge = document.getElementById('targetRecBadge');
      
      if (sourceMic) sourceMic.classList.remove('recording');
      if (targetMic) targetMic.classList.remove('recording');
      if (sourceBadge) sourceBadge.classList.remove('recording');
      if (targetBadge) targetBadge.classList.remove('recording');
    }

    /* TEXT-TO-SPEECH (SPEAKING) ON BOTH SIDES */
    function playVoiceover(side) {
      const isSource = side === 'source';
      const textArea = document.getElementById(isSource ? 'sourceText' : 'targetText');
      const langSelect = document.getElementById(isSource ? 'sourceLang' : 'targetLang');
      const playBtn = document.getElementById(isSource ? 'sourceTtsBtn' : 'targetTtsBtn');
      const wave = document.getElementById(isSource ? 'sourceSoundwave' : 'targetSoundwave');
      const badge = document.getElementById(isSource ? 'sourceSpeakBadge' : 'targetSpeakBadge');
      const speedSelect = document.getElementById(isSource ? 'sourceAudioSpeed' : 'targetAudioSpeed');

      const text = textArea.value.trim();
      const lang = langSelect.value;
      const speed = parseFloat(speedSelect ? speedSelect.value : '1.0');

      if (!text) {
        showToast(`No text in ${side} panel to speak!`, 'warning');
        return;
      }

      if (activeTTSSide === side) {
        stopVoiceover();
        showToast(`Stopped ${side} audio voiceover.`, 'info');
        return;
      }

      stopVoiceover();

      activeTTSSide = side;
      if (wave) wave.classList.add('playing');
      if (badge) badge.classList.add('speaking');
      if (playBtn) playBtn.innerHTML = '<i class="fa-solid fa-stop"></i>';

      const cleanLang = lang.split('-')[0];
      const speechLang = LANG_SPEECH_CODES[lang] || cleanLang;

      // Get available browser Web Speech API voices
      const voices = ('speechSynthesis' in window) ? window.speechSynthesis.getVoices() : [];
      const matchedVoice = voices.find(v => v.lang.toLowerCase().startsWith(cleanLang.toLowerCase()) || v.lang.toLowerCase().includes(cleanLang.toLowerCase()));

      // Use Web Speech API ONLY if native matching voice exists; otherwise use high-fidelity server TTS engine (for Indian languages)
      if ('speechSynthesis' in window && matchedVoice) {
        try {
          window.speechSynthesis.cancel();
          const utterance = new SpeechSynthesisUtterance(text);
          utterance.rate = speed;
          utterance.lang = speechLang;
          utterance.voice = matchedVoice;

          utterance.onend = () => { stopVoiceover(); };
          utterance.onerror = (e) => {
            console.warn('Web Speech API error, switching to server audio fallback...', e);
            playServerTTS(text, cleanLang, speed, side);
          };

          window.speechSynthesis.speak(utterance);
          showToast(`Speaking ${side} text (${speed}x)`, 'info');
        } catch(err) {
          playServerTTS(text, cleanLang, speed, side);
        }
      } else {
        // High-fidelity Google server TTS fallback for Indian languages (Telugu, Hindi, Tamil, etc.)
        playServerTTS(text, cleanLang, speed, side);
      }
    }

    function playServerTTS(text, cleanLang, speed, side) {
      const isSource = side === 'source';
      const wave = document.getElementById(isSource ? 'sourceSoundwave' : 'targetSoundwave');
      const playBtn = document.getElementById(isSource ? 'sourceTtsBtn' : 'targetTtsBtn');
      const badge = document.getElementById(isSource ? 'sourceSpeakBadge' : 'targetSpeakBadge');
      
      const ttsUrl = `/api/tts?text=${encodeURIComponent(text)}&lang=${cleanLang}`;
      const audio = new Audio(ttsUrl);
      activeAudio = audio;
      audio.playbackRate = speed;

      audio.onplay = () => {
        if (wave) wave.classList.add('playing');
        if (badge) badge.classList.add('speaking');
        if (playBtn) playBtn.innerHTML = '<i class="fa-solid fa-stop"></i>';
      };

      audio.onended = () => {
        stopVoiceover();
      };

      audio.onerror = () => {
        stopVoiceover();
        showToast('Unable to synthesize audio speech.', 'error');
      };

      audio.play().catch(err => {
        console.error('Audio play error:', err);
        stopVoiceover();
      });
    }

    /* TRANSLATION HISTORY LOGIC */
    function toggleHistoryDrawer() {
      const drawer = document.getElementById('historyDrawer');
      const botDrawer = document.getElementById('botDrawer');
      if (botDrawer && botDrawer.classList.contains('open')) botDrawer.classList.remove('open');
      if (drawer) drawer.classList.toggle('open');
    }

    function saveToHistory(sourceText, targetText, sourceLang, targetLang) {
      if (!sourceText || !targetText) return;

      // Avoid immediate duplicate entry
      if (translationHistory.length > 0) {
        const last = translationHistory[0];
        if (last.sourceText === sourceText && last.targetText === targetText && last.targetLang === targetLang) {
          return;
        }
      }

      const item = {
        id: Date.now(),
        sourceText,
        targetText,
        sourceLang,
        targetLang,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      translationHistory.unshift(item);
      if (translationHistory.length > 50) translationHistory.pop(); // Max 50 items

      localStorage.setItem('zeni_history', JSON.stringify(translationHistory));
      renderHistory();
    }

    function renderHistory() {
      const container = document.getElementById('historyBody');
      const badge = document.getElementById('historyBadge');
      const sub = document.getElementById('historyCountSub');

      if (badge) badge.textContent = translationHistory.length;
      if (sub) sub.textContent = `${translationHistory.length} saved translations`;

      if (!container) return;

      if (translationHistory.length === 0) {
        container.innerHTML = `
          <div class="history-empty">
            <i class="fa-solid fa-clock-rotate-left" style="font-size: 2.5rem; margin-bottom: 0.8rem; opacity: 0.4;"></i>
            <p style="font-weight: 500;">No translation history yet.</p>
            <span style="font-size: 0.8rem;">Your translations will automatically appear here.</span>
          </div>
        `;
        return;
      }

      container.innerHTML = translationHistory.map((item, idx) => `
        <div class="history-card">
          <div class="history-card-header">
            <span class="history-lang-tag">
              <i class="fa-solid fa-arrow-right-arrow-left"></i> ${item.sourceLang.toUpperCase()} ➔ ${item.targetLang.toUpperCase()}
            </span>
            <span>${item.timestamp}</span>
          </div>
          <div class="history-source-text">${escapeHtml(item.sourceText)}</div>
          <div class="history-target-text">${escapeHtml(item.targetText)}</div>
          <div class="history-actions">
            <button class="icon-btn" onclick="loadHistoryItem(${idx})" title="Load into Translator">
              <i class="fa-solid fa-arrow-turn-up"></i>
            </button>
            <button class="icon-btn" onclick="playHistoryTTS(${idx})" title="Listen Audio">
              <i class="fa-solid fa-volume-high"></i>
            </button>
            <button class="icon-btn" onclick="copyHistoryText('${escapeJsString(item.targetText)}')" title="Copy Translation">
              <i class="fa-solid fa-copy"></i>
            </button>
            <button class="icon-btn" onclick="deleteHistoryItem(${idx})" title="Delete" style="color: #ef4444;">
              <i class="fa-solid fa-trash-can"></i>
            </button>
          </div>
        </div>
      `).join('');
    }

    function escapeHtml(str) {
      return (str || '').replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
    }

    function escapeJsString(str) {
      return (str || '').replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/"/g, '\\"').replace(/\n/g, '\\n');
    }

    function loadHistoryItem(idx) {
      const item = translationHistory[idx];
      if (!item) return;

      document.getElementById('sourceLang').value = item.sourceLang;
      document.getElementById('targetLang').value = item.targetLang;
      document.getElementById('sourceText').value = item.sourceText;
      document.getElementById('targetText').value = item.targetText;

      onSourceInput();
      onTargetInput();
      toggleHistoryDrawer();
      showToast('Loaded translation into studio!', 'success');
    }

    function playHistoryTTS(idx) {
      const item = translationHistory[idx];
      if (!item) return;
      
      const cleanLang = item.targetLang.split('-')[0];
      const audioUrl = `/api/tts?text=${encodeURIComponent(item.targetText)}&lang=${cleanLang}`;
      
      if (activeAudio) { try { activeAudio.pause(); } catch(e){} }
      
      activeAudio = new Audio(audioUrl);
      activeAudio.play().then(() => {
        showToast(`Playing ${item.targetLang.toUpperCase()} audio`, 'info');
      }).catch(err => {
        showToast('Unable to play audio speech.', 'error');
      });
    }

    function copyHistoryText(text) {
      if (!text) return;
      navigator.clipboard.writeText(text).then(() => {
        showToast('Translation copied to clipboard!', 'success');
      });
    }

    function deleteHistoryItem(idx) {
      translationHistory.splice(idx, 1);
      localStorage.setItem('zeni_history', JSON.stringify(translationHistory));
      renderHistory();
      showToast('Removed from history.', 'info');
    }

    function clearAllHistory() {
      if (translationHistory.length === 0) return;
      if (confirm('Clear all saved translation history?')) {
        translationHistory = [];
        localStorage.removeItem('zeni_history');
        renderHistory();
        showToast('Translation history cleared.', 'info');
      }
    }

    function stopVoiceover() {
      if (activeAudio) {
        try { activeAudio.pause(); } catch(e){}
        activeAudio = null;
      }
      if ('speechSynthesis' in window) {
        try { window.speechSynthesis.cancel(); } catch(e){}
      }
      activeTTSSide = null;

      const sourceWave = document.getElementById('sourceSoundwave');
      const targetWave = document.getElementById('targetSoundwave');
      const sourceBadge = document.getElementById('sourceSpeakBadge');
      const targetBadge = document.getElementById('targetSpeakBadge');
      const sourcePlay = document.getElementById('sourceTtsBtn');
      const targetPlay = document.getElementById('targetTtsBtn');

      if (sourceWave) sourceWave.classList.remove('playing');
      if (targetWave) targetWave.classList.remove('playing');
      if (sourceBadge) sourceBadge.classList.remove('speaking');
      if (targetBadge) targetBadge.classList.remove('speaking');
      if (sourcePlay) sourcePlay.innerHTML = '<i class="fa-solid fa-volume-high"></i>';
      if (targetPlay) targetPlay.innerHTML = '<i class="fa-solid fa-volume-high"></i>';
    }

    function handleImageUpload(e) {
      const file = e.target.files[0];
      if (file) processImageForOCR(file);
    }

    async function processImageForOCR(file) {
      const reader = new FileReader();
      reader.onload = async (e) => {
        const previewContainer = document.getElementById('imagePreviewContainer');
        const preview = document.getElementById('imagePreview');
        const uploadPlaceholder = document.getElementById('uploadPlaceholder');
        const scanLine = document.getElementById('scanLine');
        const scanProgress = document.getElementById('scanProgress');
        const scanProgressFill = document.getElementById('scanProgressFill');
        const scanStatusText = document.getElementById('scanStatusText');

        preview.src = e.target.result;
        uploadPlaceholder.style.display = 'none';
        previewContainer.style.display = 'block';
        scanLine.style.display = 'block';
        scanProgress.style.display = 'block';

        scanStatusText.textContent = 'Initializing OCR Scanner...';
        scanProgressFill.style.width = '20%';

        try {
          const worker = await Tesseract.createWorker('eng+tel+hin+spa+fra');
          scanProgressFill.style.width = '50%';
          scanStatusText.textContent = 'Scanning image text...';

          const ret = await worker.recognize(e.target.result);
          scanProgressFill.style.width = '90%';
          scanStatusText.textContent = 'Finalizing text extraction...';

          await worker.terminate();

          scanLine.style.display = 'none';
          scanProgressFill.style.width = '100%';
          scanStatusText.textContent = 'Scan Complete!';

          const extracted = ret.data.text.trim();
          document.getElementById('extractedOcrText').value = extracted || 'No readable text found in picture.';

          if (extracted) {
            translateScannedText();
          }
        } catch (ocrErr) {
          console.error(ocrErr);
          scanLine.style.display = 'none';
          scanStatusText.textContent = 'OCR Scan failed.';
          document.getElementById('extractedOcrText').value = 'Error scanning text from picture.';
        }
      };
      reader.readAsDataURL(file);
    }

    async function translateScannedText() {
      const text = document.getElementById('extractedOcrText').value.trim();
      const target = document.getElementById('targetLang').value;
      if (!text) return;

      try {
        const response = await fetch('/api/translate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text, source: 'auto', target, tone: 'standard' })
        });
        const data = await response.json();
        if (data.status === 'success') {
          document.getElementById('translatedOcrText').value = data.translation;
        }
      } catch (err) {
        console.error(err);
      }
    }

    function toggleBotDrawer() {
      document.getElementById('botDrawer').classList.toggle('open');
    }

    async function sendBotMessage() {
      const input = document.getElementById('botInput');
      const msg = input.value.trim();
      if (!msg) return;

      const chatBody = document.getElementById('botChatBody');
      
      const userBubble = document.createElement('div');
      userBubble.className = 'chat-bubble user';
      userBubble.textContent = msg;
      chatBody.appendChild(userBubble);

      input.value = '';
      chatBody.scrollTop = chatBody.scrollHeight;

      const botBubble = document.createElement('div');
      botBubble.className = 'chat-bubble bot';
      botBubble.textContent = 'Zeni Bot is thinking...';
      chatBody.appendChild(botBubble);
      chatBody.scrollTop = chatBody.scrollHeight;

      try {
        const response = await fetch('/api/bot/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: msg })
        });
        const data = await response.json();
        botBubble.textContent = data.reply || 'Sorry, I could not process that request.';
      } catch (err) {
        botBubble.textContent = 'Network error connecting to Zeni Bot.';
      }
      chatBody.scrollTop = chatBody.scrollHeight;
    }

    function openAuthModal() {
      const gate = document.getElementById('authGateScreen');
      if (gate) gate.classList.remove('hidden');
    }
    function closeAuthModal() {
      if (!activeUser) {
        openAuthModal();
        return;
      }
      const gate = document.getElementById('authGateScreen');
      if (gate) gate.classList.add('hidden');
    }

    let currentAuthMode = 'signin';
    function setAuthTab(mode) {
      currentAuthMode = mode;
      const btnIn = document.getElementById('tabSignIn');
      const btnUp = document.getElementById('tabSignUp');
      const submitBtn = document.getElementById('authSubmitBtn');

      if (mode === 'signin') {
        btnIn.classList.add('active');
        btnUp.classList.remove('active');
        submitBtn.textContent = 'Sign In';
      } else {
        btnUp.classList.add('active');
        btnIn.classList.remove('active');
        submitBtn.textContent = 'Create Account';
      }
    }

    function handleGoogleSignIn() {
      const modal = document.getElementById('googleAccountModal');
      if (modal) modal.classList.add('active');
    }

    function closeGoogleModal() {
      const modal = document.getElementById('googleAccountModal');
      if (modal) modal.classList.remove('active');
    }

    function loginWithGoogleAccount(name, email) {
      activeUser = {
        username: name,
        email: email,
        provider: 'Google Account',
        avatar: 'https://cdn-icons-png.flaticon.com/512/300/300221.png'
      };

      localStorage.setItem('zeni_user', JSON.stringify(activeUser));
      closeGoogleModal();
      updateAuthUI();
      showToast(`Signed in with Google as ${activeUser.username}!`, 'success');
    }

    function submitCustomGoogleLogin() {
      const input = document.getElementById('googleCustomEmail');
      const email = input ? input.value.trim() : '';

      if (!email || !email.includes('@')) {
        showToast('Please enter a valid Google email address.', 'warning');
        return;
      }

      const rawName = email.split('@')[0];
      const username = rawName.charAt(0).toUpperCase() + rawName.slice(1);
      loginWithGoogleAccount(username, email);
    }

    function handleAuthSubmit(e) {
      if (e) e.preventDefault();
      const inputVal = (document.getElementById('authEmail')?.value || '').trim() || 'User';
      const rawName = inputVal.includes('@') ? inputVal.split('@')[0] : inputVal;
      const username = rawName.charAt(0).toUpperCase() + rawName.slice(1);

      activeUser = {
        username: username,
        email: inputVal.includes('@') ? inputVal : `${username.toLowerCase()}@zeni.app`,
        provider: 'Email Account',
        avatar: ''
      };

      localStorage.setItem('zeni_user', JSON.stringify(activeUser));
      updateAuthUI();
      showToast(`Welcome back, ${activeUser.username}!`, 'success');
    }

    function quickDemoSignIn() {
      activeUser = {
        username: 'Demo User',
        email: 'demo@zeni.app',
        provider: 'Quick Sign In',
        avatar: ''
      };
      localStorage.setItem('zeni_user', JSON.stringify(activeUser));
      updateAuthUI();
      showToast('Signed in as Demo User!', 'success');
    }

    function openAuthModal() {
      const modal = document.getElementById('googleAccountModal');
      if (modal) modal.classList.add('active');
    }
    function closeAuthModal() {
      const modal = document.getElementById('googleAccountModal');
      if (modal) modal.classList.remove('active');
    }

    function updateAuthUI() {
      const authLabel = document.getElementById('userAuthLabel');
      const authBtn = document.getElementById('userAuthBtn');

      if (activeUser) {
        if (authLabel) authLabel.textContent = activeUser.username;
        if (authBtn) {
          authBtn.innerHTML = `<i class="fa-solid fa-user-check"></i> <span id="userAuthLabel" class="desktop-only">${activeUser.username}</span>`;
          authBtn.onclick = () => {
            if (confirm(`Logged in as ${activeUser.username} (${activeUser.provider}). Log out now?`)) {
              activeUser = null;
              localStorage.removeItem('zeni_user');
              updateAuthUI();
              showToast('Logged out.', 'info');
            }
          };
        }
      } else {
        if (authLabel) authLabel.textContent = 'Sign In';
        if (authBtn) {
          authBtn.innerHTML = `<i class="fa-solid fa-user"></i> <span id="userAuthLabel" class="desktop-only">Sign In</span>`;
          authBtn.onclick = openAuthModal;
        }
      }
    }
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE, languages=LANGUAGES)


@app.route("/api/translate", methods=["POST"])
def api_translate():
    """Zeni Neural Translation API endpoint with multi-engine fallback."""
    try:
        data = request.get_json() or {}
        text = data.get("text", "").strip()
        source = data.get("source", "en")
        target = data.get("target", "te")
        tone = data.get("tone", "standard")

        if not text:
            return jsonify({"status": "error", "error": "No text provided."}), 400

        src_lang = "auto" if source == "auto" else source
        translated_text = ""

        if translator:
            try:
                result = translator.translate(text, src=src_lang, dest=target)
                translated_text = result.text
            except Exception as e:
                print(f"googletrans error: {e}", file=sys.stderr)

        if not translated_text and GoogleTranslator:
            try:
                translated_text = GoogleTranslator(source=src_lang, target=target).translate(text)
            except Exception as e:
                print(f"deep_translator error: {e}", file=sys.stderr)

        if not translated_text:
            translated_text = text

        transliteration = ""
        explanation = f"Translated from {source.upper()} to {target.upper()} using Zeni Engine ({tone.capitalize()} Tone)."

        if target == "te":
            transliteration = f"Telugu Script: {translated_text}"
        elif target == "hi":
            transliteration = f"Hindi Script: {translated_text}"

        return jsonify({
            "status": "success",
            "translation": translated_text,
            "transliteration": transliteration,
            "explanation": explanation,
            "engine": "zeni_neural"
        })

    except Exception as exc:
        return jsonify({"status": "error", "error": str(exc)}), 500


@app.route("/api/bot/chat", methods=["POST"])
def api_bot_chat():
    """Zeni AI Assistant chatbot endpoint."""
    data = request.get_json() or {}
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"reply": "Please type a message for Zeni Bot!"})

    msg_lower = message.lower()

    if "hello" in msg_lower or "hi" in msg_lower or "hey" in msg_lower:
        reply = "Hello! I am Zeni Bot. How can I assist with your translations or language learning today?"
    elif "how to say" in msg_lower or "translate" in msg_lower:
        try:
            if translator:
                res = translator.translate(message, dest="te")
                reply = f"Zeni Bot Translation Insight: '{res.text}' (Telugu)."
            elif GoogleTranslator:
                res_text = GoogleTranslator(source='auto', target='te').translate(message)
                reply = f"Zeni Bot Translation Insight: '{res_text}' (Telugu)."
            else:
                reply = f"Zeni Bot Tip: To translate '{message}', type or paste it into the main translation panel!"
        except Exception:
            reply = f"Zeni Bot Tip: To translate '{message}', type or paste it into the main translation panel!"
    elif "picture" in msg_lower or "image" in msg_lower or "scan" in msg_lower or "camera" in msg_lower:
        reply = "Zeni Bot Tip: Tap 'Scan Pic' on the navigation bar to take a photo or upload an image and extract text automatically!"
    elif "theme" in msg_lower or "dark" in msg_lower or "light" in msg_lower:
        reply = "Zeni Bot Tip: You can toggle between Dark Mode and Light Mode anytime using the Theme button!"
    else:
        reply = f"Zeni Bot: I am here to help you translate text, scan pictures, or practice pronunciation. Let me know what language you are exploring!"

    return jsonify({"reply": reply})


@app.route("/api/tts", methods=["GET"])
def api_tts():
    """Text-To-Speech endpoint with robust multi-engine fallback for Indian & global languages."""
    text = request.args.get("text", "").strip()
    lang = request.args.get("lang", "en").strip()

    if not text:
        return jsonify({"status": "error", "error": "No text provided"}), 400

    clean_lang = lang.split("-")[0]

    # 1. Try gTTS first if available
    if gTTS is not None:
        try:
            fp = io.BytesIO()
            tts = gTTS(text=text, lang=clean_lang)
            tts.write_to_fp(fp)
            fp.seek(0)
            return Response(fp.read(), mimetype="audio/mpeg")
        except Exception as e:
            print(f"[TTS Warning] gTTS synthesis failed for {clean_lang}: {e}")

    # 2. Direct Google Translate TTS Audio Proxy fallback
    try:
        import urllib.parse
        import urllib.request
        
        encoded_text = urllib.parse.quote(text)
        gt_url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={encoded_text}&tl={clean_lang}&client=tw-ob"
        req = urllib.request.Request(
            gt_url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            audio_bytes = resp.read()
            return Response(audio_bytes, mimetype="audio/mpeg")
    except Exception as exc:
        print(f"[TTS Error] Google audio stream failed: {exc}")
        return jsonify({"status": "error", "error": str(exc)}), 500


if __name__ == "__main__":
    import socket

    def find_free_port(preferred_ports):
        for port in preferred_ports:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(("127.0.0.1", port))
                    return port
                except OSError:
                    continue
        return 5050

    selected_port = find_free_port([5050, 5000, 8080, 8000])
    print(f"Starting Zeni Translate Web Application on http://127.0.0.1:{selected_port} ...")
    app.run(host="127.0.0.1", port=selected_port, debug=False)
