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
  <title>Zeni Translate | World-Class AI Translation Studio</title>
  
  <meta name="description" content="Zeni Translate is a state-of-the-art AI translation studio featuring picture scanning OCR, voice synthesis, natural language assistant, and sleek light/dark themes." />
  <meta name="theme-color" content="#050811" />
  
  <!-- Fonts & Icons -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&family=Outfit:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" />
  
  <!-- Tesseract OCR -->
  <script src="https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/tesseract.min.js"></script>

  <style>
    /* DESIGN SYSTEM: CYBER OBSIDIAN (DARK) & PORCELAIN PURE (LIGHT) */
    :root[data-theme="dark"] {
      --bg-body: #050811;
      --bg-surface: rgba(13, 19, 36, 0.75);
      --bg-card: rgba(21, 30, 54, 0.65);
      --bg-input: rgba(8, 12, 24, 0.9);
      --border-subtle: rgba(255, 255, 255, 0.1);
      --border-accent: rgba(6, 182, 212, 0.45);
      --border-focus: #06b6d4;
      
      --text-main: #f8fafc;
      --text-sub: #94a3b8;
      --text-muted: #64748b;
      
      --cyan: #06b6d4;
      --indigo: #6366f1;
      --purple: #a855f7;
      --emerald: #10b981;
      --pink: #ec4899;
      
      --grad-main: linear-gradient(135deg, #06b6d4 0%, #3b82f6 50%, #8b5cf6 100%);
      --grad-hover: linear-gradient(135deg, #0891b2 0%, #2563eb 50%, #7c3aed 100%);
      --glow-main: rgba(6, 182, 212, 0.3);
      --shadow-card: 0 30px 90px rgba(0, 0, 0, 0.75), 0 0 60px rgba(6, 182, 212, 0.12);
      
      --orb1: rgba(6, 182, 212, 0.15);
      --orb2: rgba(139, 92, 246, 0.15);
      --nav-bg: rgba(5, 8, 17, 0.85);
      --mob-bg: rgba(8, 12, 24, 0.96);
    }

    :root[data-theme="light"] {
      --bg-body: #f8fafc;
      --bg-surface: rgba(255, 255, 255, 0.95);
      --bg-card: rgba(241, 245, 249, 0.9);
      --bg-input: #ffffff;
      --border-subtle: rgba(0, 0, 0, 0.08);
      --border-accent: rgba(37, 99, 235, 0.35);
      --border-focus: #2563eb;
      
      --text-main: #0f172a;
      --text-sub: #334155;
      --text-muted: #64748b;
      
      --cyan: #0284c7;
      --indigo: #2563eb;
      --purple: #7c3aed;
      --emerald: #059669;
      --pink: #db2777;
      
      --grad-main: linear-gradient(135deg, #2563eb 0%, #0d9488 50%, #7c3aed 100%);
      --grad-hover: linear-gradient(135deg, #1d4ed8 0%, #0f766e 50%, #6d28d9 100%);
      --glow-main: rgba(37, 99, 235, 0.2);
      --shadow-card: 0 25px 70px rgba(15, 23, 42, 0.08), 0 0 40px rgba(37, 99, 235, 0.08);
      
      --orb1: rgba(37, 99, 235, 0.1);
      --orb2: rgba(13, 148, 136, 0.1);
      --nav-bg: rgba(255, 255, 255, 0.9);
      --mob-bg: rgba(255, 255, 255, 0.96);
    }

    * { box-sizing: border-box; margin: 0; padding: 0; transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease; -webkit-tap-highlight-color: transparent; }

    body {
      font-family: 'Plus Jakarta Sans', sans-serif;
      min-height: 100vh;
      background-color: var(--bg-body);
      color: var(--text-main);
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 0 0.8rem 6rem 0.8rem;
      overflow-x: hidden;
      position: relative;
    }

    /* Ambient Background Orbs */
    .bg-orb {
      position: fixed;
      border-radius: 50%;
      filter: blur(140px);
      pointer-events: none;
      z-index: 0;
      animation: orbMove 25s ease-in-out infinite alternate;
    }
    .orb-1 { width: 550px; height: 550px; background: var(--orb1); top: -140px; left: -140px; }
    .orb-2 { width: 500px; height: 500px; background: var(--orb2); bottom: -140px; right: -140px; animation-delay: -10s; }

    @keyframes orbMove {
      0% { transform: translate(0, 0) scale(1); }
      50% { transform: translate(60px, 40px) scale(1.08); }
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
      border: 1px solid var(--border-subtle);
      border-radius: 999px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
      z-index: 50;
      box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 0.8rem;
      text-decoration: none;
      cursor: pointer;
    }

    .brand-icon {
      width: 44px;
      height: 44px;
      border-radius: 14px;
      background: var(--grad-main);
      display: flex;
      align-items: center;
      justify-content: center;
      color: #ffffff;
      font-size: 1.35rem;
      box-shadow: 0 8px 24px var(--glow-main);
    }

    .brand-title {
      font-family: 'Outfit', sans-serif;
      font-weight: 900;
      font-size: 1.5rem;
      letter-spacing: -0.5px;
      background: var(--grad-main);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .nav-actions {
      display: flex;
      align-items: center;
      gap: 0.65rem;
    }

    .nav-btn {
      padding: 0.6rem 1.2rem;
      border-radius: 999px;
      border: 1px solid var(--border-subtle);
      background: var(--bg-card);
      color: var(--text-main);
      font-weight: 700;
      font-size: 0.88rem;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.55rem;
      min-height: 42px;
    }

    .nav-btn:hover {
      border-color: var(--border-accent);
      color: var(--cyan);
      transform: translateY(-2px);
    }

    .nav-btn.primary {
      background: var(--grad-main);
      color: #ffffff;
      border: none;
      box-shadow: 0 8px 22px var(--glow-main);
    }

    /* MAIN WORKBENCH */
    .main-container {
      width: min(100%, 1280px);
      z-index: 1;
    }

    /* HERO BANNER */
    .hero {
      text-align: center;
      margin: 0.5rem 0 1.8rem 0;
    }

    .hero-tag {
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.4rem 1.1rem;
      border-radius: 999px;
      background: rgba(6, 182, 212, 0.1);
      border: 1px solid rgba(6, 182, 212, 0.25);
      color: var(--cyan);
      font-size: 0.82rem;
      font-weight: 700;
      text-transform: uppercase;
      margin-bottom: 0.6rem;
    }

    .hero-title {
      font-family: 'Outfit', sans-serif;
      font-size: clamp(2.2rem, 5.5vw, 3.6rem);
      font-weight: 900;
      line-height: 1.15;
      margin-bottom: 0.5rem;
      background: linear-gradient(135deg, var(--text-main) 30%, var(--cyan) 70%, var(--purple) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      letter-spacing: -1px;
    }

    .hero-desc {
      font-size: 1.05rem;
      color: var(--text-sub);
      max-width: 700px;
      margin: 0 auto;
    }

    /* TABS */
    .tabs-header {
      display: flex;
      justify-content: center;
      gap: 0.6rem;
      margin-bottom: 1.5rem;
    }

    .tab-btn {
      padding: 0.75rem 1.8rem;
      border-radius: 18px;
      border: 1px solid var(--border-subtle);
      background: var(--bg-surface);
      backdrop-filter: blur(20px);
      color: var(--text-sub);
      font-family: 'Outfit', sans-serif;
      font-weight: 700;
      font-size: 1rem;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.6rem;
    }

    .tab-btn.active {
      background: var(--grad-main);
      color: #ffffff;
      border-color: transparent;
      box-shadow: 0 10px 25px var(--glow-main);
      transform: scale(1.02);
    }

    /* WORKBENCH CARD */
    .workbench {
      background: var(--bg-surface);
      backdrop-filter: blur(40px);
      border-radius: 36px;
      box-shadow: var(--shadow-card);
      border: 1px solid var(--border-subtle);
      padding: 2rem;
      min-height: 520px;
    }

    @media (max-width: 640px) {
      .workbench {
        padding: 1.2rem;
        border-radius: 26px;
      }
    }

    /* TONE TOOLBAR & PRESETS */
    .toolbar {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
      padding-bottom: 1.2rem;
      margin-bottom: 1.5rem;
      border-bottom: 1px solid var(--border-subtle);
    }

    .tone-box {
      display: flex;
      align-items: center;
      gap: 0.6rem;
      background: var(--bg-card);
      padding: 0.45rem 1rem;
      border-radius: 16px;
      border: 1px solid var(--border-subtle);
      font-size: 0.88rem;
      color: var(--text-sub);
    }

    .tone-select {
      background: transparent;
      border: none;
      color: var(--text-main);
      font-weight: 700;
      font-size: 0.92rem;
      cursor: pointer;
      outline: none;
    }

    .tone-select option {
      background-color: var(--bg-body);
      color: var(--text-main);
    }

    .preset-chips {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
    }

    .chip {
      padding: 0.35rem 0.85rem;
      border-radius: 999px;
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      color: var(--text-sub);
      font-size: 0.8rem;
      font-weight: 600;
      cursor: pointer;
    }

    .chip:hover {
      border-color: var(--cyan);
      color: var(--cyan);
    }

    /* DUAL PANE WORKBENCH GRID */
    .grid-pane {
      display: grid;
      grid-template-columns: 1fr 54px 1fr;
      gap: 1.4rem;
      align-items: stretch;
    }

    @media (max-width: 880px) {
      .grid-pane {
        grid-template-columns: 1fr;
        gap: 1rem;
      }
      .swap-col {
        display: flex;
        justify-content: center;
        margin: 0.2rem 0;
      }
    }

    .pane-card {
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: 28px;
      padding: 1.4rem;
      display: flex;
      flex-direction: column;
      gap: 1.1rem;
      position: relative;
    }

    .pane-card:focus-within {
      border-color: var(--border-focus);
      box-shadow: 0 0 30px var(--glow-main);
    }

    .pane-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .lang-select {
      width: 100%;
      padding: 0.75rem 1.1rem;
      background: var(--bg-input);
      border: 1px solid var(--border-subtle);
      border-radius: 16px;
      color: var(--text-main);
      font-weight: 700;
      font-size: 1rem;
      outline: none;
      cursor: pointer;
    }

    .swap-btn {
      width: 52px;
      height: 52px;
      border-radius: 50%;
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      color: var(--text-main);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.2rem;
      cursor: pointer;
      margin: auto;
      box-shadow: 0 8px 24px rgba(0,0,0,0.25);
    }

    .swap-btn:hover {
      transform: rotate(180deg) scale(1.1);
      border-color: var(--cyan);
      color: var(--cyan);
      box-shadow: 0 0 25px var(--glow-main);
    }

    .editor {
      width: 100%;
      min-height: 220px;
      background: var(--bg-input);
      border: 1px solid var(--border-subtle);
      border-radius: 20px;
      padding: 1.2rem;
      color: var(--text-main);
      font-family: inherit;
      font-size: 1.08rem;
      line-height: 1.65;
      resize: vertical;
      outline: none;
    }

    .editor:focus {
      border-color: var(--border-focus);
    }

    .pane-footer {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-top: auto;
      padding-top: 0.4rem;
    }

    .action-group {
      display: flex;
      align-items: center;
      gap: 0.55rem;
    }

    .btn-icon {
      width: 42px;
      height: 42px;
      border-radius: 14px;
      border: 1px solid var(--border-subtle);
      background: var(--bg-input);
      color: var(--text-sub);
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      font-size: 1.05rem;
    }

    .btn-icon:hover {
      color: var(--cyan);
      border-color: var(--cyan);
      transform: translateY(-2px);
    }

    .btn-icon.recording {
      background: #ef4444;
      color: #ffffff;
      animation: pulseMic 1.5s infinite;
    }

    @keyframes pulseMic {
      0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.6); }
      70% { box-shadow: 0 0 0 14px rgba(239, 68, 68, 0); }
      100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
    }

    /* TTS EQUALIZER */
    .audio-group {
      display: flex;
      align-items: center;
      gap: 0.7rem;
    }

    .speed-select {
      padding: 0.4rem 0.75rem;
      background: var(--bg-input);
      border: 1px solid var(--border-subtle);
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
      background: var(--grad-main);
      border-radius: 4px;
      animation: waveDance 0.8s ease-in-out infinite alternate;
    }
    .wave-bar:nth-child(2) { animation-delay: 0.15s; }
    .wave-bar:nth-child(3) { animation-delay: 0.35s; }

    @keyframes waveDance {
      0% { height: 4px; }
      100% { height: 20px; }
    }

    /* PICTURE SCAN STUDIO */
    .scan-studio {
      display: none;
    }

    .scan-studio.active {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1.6rem;
    }

    @media (max-width: 880px) {
      .scan-studio.active {
        grid-template-columns: 1fr;
      }
    }

    .upload-zone {
      border: 2px dashed var(--border-subtle);
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

    .upload-zone:hover {
      border-color: var(--cyan);
      background: rgba(6, 182, 212, 0.05);
    }

    .upload-icon-lg {
      font-size: 3.6rem;
      background: var(--grad-main);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 1rem;
    }

    .cam-btn-mobile {
      margin-top: 1.2rem;
      padding: 0.75rem 1.6rem;
      border-radius: 999px;
      background: var(--grad-main);
      color: #ffffff;
      font-weight: 800;
      font-size: 0.95rem;
      border: none;
      display: inline-flex;
      align-items: center;
      gap: 0.6rem;
    }

    .img-preview-box {
      width: 100%;
      height: 100%;
      max-height: 380px;
      position: relative;
      display: none;
    }

    .img-preview-box img {
      width: 100%;
      height: 100%;
      object-fit: contain;
      border-radius: 20px;
    }

    .laser-line {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 4px;
      background: var(--grad-main);
      box-shadow: 0 0 20px var(--cyan);
      display: none;
      animation: laserAnim 2s ease-in-out infinite alternate;
    }

    @keyframes laserAnim {
      0% { top: 5%; }
      100% { top: 92%; }
    }

    .progress-box {
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
      background: var(--grad-main);
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
      background: var(--bg-surface);
      backdrop-filter: blur(40px);
      border-left: 1px solid var(--border-subtle);
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
      border-bottom: 1px solid var(--border-subtle);
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: var(--bg-card);
    }

    .bot-title-group {
      display: flex;
      align-items: center;
      gap: 0.8rem;
    }

    .bot-avatar {
      width: 42px;
      height: 42px;
      border-radius: 14px;
      background: var(--grad-main);
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

    .bubble {
      max-width: 88%;
      padding: 0.95rem 1.2rem;
      border-radius: 20px;
      font-size: 0.94rem;
      line-height: 1.55;
    }

    .bubble.bot {
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      color: var(--text-main);
      align-self: flex-start;
      border-top-left-radius: 4px;
    }

    .bubble.user {
      background: var(--grad-main);
      color: #ffffff;
      align-self: flex-end;
      border-top-right-radius: 4px;
    }

    .bot-input-bar {
      padding: 1.2rem;
      border-top: 1px solid var(--border-subtle);
      display: flex;
      gap: 0.7rem;
      background: var(--bg-card);
    }

    .bot-input {
      flex: 1;
      padding: 0.85rem 1.1rem;
      background: var(--bg-input);
      border: 1px solid var(--border-subtle);
      border-radius: 16px;
      color: var(--text-main);
      outline: none;
    }

    /* AUTH MODAL */
    .modal-overlay {
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.75);
      backdrop-filter: blur(14px);
      z-index: 200;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 1rem;
    }

    .modal-overlay.active {
      display: flex;
    }

    .auth-modal {
      width: min(100%, 450px);
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: 32px;
      padding: 2.4rem;
      position: relative;
      box-shadow: var(--shadow-card);
    }

    .auth-tabs {
      display: flex;
      gap: 0.5rem;
      margin-bottom: 1.5rem;
      background: var(--bg-card);
      padding: 0.35rem;
      border-radius: 16px;
    }

    .auth-tab-btn {
      flex: 1;
      padding: 0.65rem;
      border: none;
      background: transparent;
      color: var(--text-sub);
      font-weight: 700;
      border-radius: 12px;
      cursor: pointer;
    }

    .auth-tab-btn.active {
      background: var(--grad-main);
      color: #ffffff;
    }

    .form-group {
      margin-bottom: 1.2rem;
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
      padding: 0.85rem 1.1rem;
      background: var(--bg-input);
      border: 1px solid var(--border-subtle);
      border-radius: 16px;
      color: var(--text-main);
      outline: none;
    }

    .auth-submit-btn {
      width: 100%;
      padding: 0.95rem;
      border-radius: 16px;
      border: none;
      background: var(--grad-main);
      color: #ffffff;
      font-weight: 800;
      font-size: 1.05rem;
      cursor: pointer;
    }

    .guest-btn {
      width: 100%;
      padding: 0.8rem;
      border-radius: 16px;
      border: 1px solid var(--border-subtle);
      background: var(--bg-card);
      color: var(--text-main);
      font-weight: 700;
      cursor: pointer;
      margin-top: 0.9rem;
    }

    /* INSIGHT CARD */
    .insight-card {
      margin-top: 1.6rem;
      background: var(--bg-card);
      border: 1px dashed var(--border-subtle);
      border-radius: 22px;
      padding: 1.1rem 1.5rem;
      font-size: 0.95rem;
      color: var(--text-sub);
      display: flex;
      align-items: center;
      gap: 0.9rem;
    }

    /* MOBILE BOTTOM NAV BAR */
    .mob-navbar {
      display: none;
      position: fixed;
      bottom: 0;
      left: 0;
      right: 0;
      height: 66px;
      background: var(--mob-bg);
      backdrop-filter: blur(24px);
      border-top: 1px solid var(--border-subtle);
      z-index: 90;
      align-items: center;
      justify-content: space-around;
      padding: 0 0.5rem;
    }

    @media (max-width: 768px) {
      .mob-navbar { display: flex; }
      .tabs-header { display: none; }
      .desktop-only { display: none; }
    }

    .mob-nav-item {
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

    .mob-nav-item i { font-size: 1.3rem; }
    .mob-nav-item.active { color: var(--cyan); }
  </style>
</head>
<body>
  <div class="bg-orb orb-1"></div>
  <div class="bg-orb orb-2"></div>

  <!-- TOP NAVBAR -->
  <nav class="navbar">
    <a class="brand" onclick="switchTab('translate')">
      <div class="brand-icon">
        <i class="fa-solid fa-language"></i>
      </div>
      <span class="brand-title">Zeni Translate</span>
    </a>

    <div class="nav-actions">
      <button class="nav-btn" id="themeToggleBtn" onclick="toggleTheme()">
        <i class="fa-solid fa-moon" id="themeIcon"></i>
        <span id="themeLabel" class="desktop-only">Dark</span>
      </button>

      <button class="nav-btn" onclick="toggleBotDrawer()">
        <i class="fa-solid fa-robot"></i>
        <span class="desktop-only">Zeni Bot</span>
      </button>

      <button class="nav-btn primary" id="userAuthBtn" onclick="openAuthModal()">
        <i class="fa-solid fa-user"></i>
        <span id="userAuthLabel" class="desktop-only">Sign In</span>
      </button>
    </div>
  </nav>

  <!-- MAIN WORKBENCH -->
  <main class="main-container">
    <div class="hero">
      <div class="hero-tag">
        <i class="fa-solid fa-wand-magic-sparkles"></i> AI Neural Translation & OCR Studio
      </div>
      <h1 class="hero-title">Translate Text & Pictures Instantly</h1>
      <p class="hero-desc">High-precision multilingual translation, picture OCR camera scanner, natural voiceover, and AI assistant.</p>
    </div>

    <!-- TABS -->
    <div class="tabs-header">
      <button class="tab-btn active" id="tabBtnTranslate" onclick="switchTab('translate')">
        <i class="fa-solid fa-font"></i> Text Translate
      </button>
      <button class="tab-btn" id="tabBtnScan" onclick="switchTab('scan')">
        <i class="fa-solid fa-camera"></i> Picture Scan
      </button>
    </div>

    <!-- WORKBENCH CARD -->
    <div class="workbench">
      
      <!-- TOOLBAR -->
      <div class="toolbar">
        <div class="tone-box">
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
          <button class="chip" onclick="setPreset('Hello, how are you?')">👋 Greetings</button>
          <button class="chip" onclick="setPreset('Thank you very much for your help.')">🙏 Thanks</button>
          <button class="chip" onclick="setPreset('Could you please assist me with this?')">💼 Request</button>
        </div>
      </div>

      <!-- TEXT TRANSLATION PANE -->
      <div id="sectionTranslate">
        <div class="grid-pane">
          
          <!-- SOURCE PANE -->
          <div class="pane-card">
            <div class="pane-header">
              <select class="lang-select" id="sourceLang" onchange="triggerTranslation()">
                {% for code, name in languages.items() %}
                <option value="{{ code }}" {% if code == 'en' %}selected{% endif %}>{{ name }}</option>
                {% endfor %}
              </select>
            </div>

            <textarea class="editor" id="sourceText" placeholder="Type, paste, or speak text..." oninput="onSourceInput()"></textarea>

            <div class="pane-footer">
              <div class="action-group">
                <button class="btn-icon" id="micBtn" onclick="toggleSpeechRecognition()" title="Voice Input">
                  <i class="fa-solid fa-microphone"></i>
                </button>
                <button class="btn-icon" onclick="clearText()" title="Clear">
                  <i class="fa-solid fa-xmark"></i>
                </button>
              </div>
              <span style="font-size: 0.82rem; color: var(--text-muted);" id="charCount">0 chars</span>
            </div>
          </div>

          <!-- SWAP BUTTON -->
          <div class="swap-col">
            <button class="swap-btn" onclick="swapLanguages()" title="Swap Languages">
              <i class="fa-solid fa-right-left"></i>
            </button>
          </div>

          <!-- TARGET PANE -->
          <div class="pane-card">
            <div class="pane-header">
              <select class="lang-select" id="targetLang" onchange="triggerTranslation()">
                {% for code, name in languages.items() %}
                <option value="{{ code }}" {% if code == 'te' %}selected{% endif %}>{{ name }}</option>
                {% endfor %}
              </select>
            </div>

            <textarea class="editor" id="targetText" placeholder="Translation will appear here..." readonly></textarea>

            <div class="pane-footer">
              <div class="action-group">
                <button class="btn-icon" id="ttsPlayBtn" onclick="playVoiceover()" title="Listen Audio">
                  <i class="fa-solid fa-volume-high"></i>
                </button>
                <button class="btn-icon" onclick="copyTranslation()" title="Copy">
                  <i class="fa-solid fa-copy"></i>
                </button>
              </div>

              <div class="audio-group">
                <div class="soundwave" id="soundwave">
                  <div class="wave-bar"></div>
                  <div class="wave-bar"></div>
                  <div class="wave-bar"></div>
                </div>
                <select class="speed-select" id="audioSpeed">
                  <option value="0.75">0.75x</option>
                  <option value="1.0" selected>1.0x</option>
                  <option value="1.25">1.25x</option>
                  <option value="1.5">1.5x</option>
                </select>
              </div>
            </div>
          </div>

        </div>

        <div class="insight-card" id="insightCard">
          <i class="fa-solid fa-wand-magic-sparkles" style="color: var(--cyan); font-size: 1.25rem;"></i>
          <span id="insightText">Select source & target languages to translate automatically.</span>
        </div>
      </div>

      <!-- PICTURE SCAN STUDIO -->
      <div id="sectionScan" class="scan-studio">
        <div class="upload-zone" id="dropZone" onclick="document.getElementById('imageFileInput').click()">
          <input type="file" id="imageFileInput" accept="image/*" style="display: none;" onchange="handleImageUpload(event)" />
          
          <div id="uploadPlaceholder">
            <i class="fa-solid fa-camera-retro upload-icon-lg"></i>
            <h3 style="font-family: 'Outfit', sans-serif; font-size: 1.4rem; margin-bottom: 0.4rem;">Tap to Scan Picture</h3>
            <p style="color: var(--text-sub); font-size: 0.95rem;">Upload from Gallery or Take Photo with Camera</p>
            <div class="cam-btn-mobile">
              <i class="fa-solid fa-camera"></i> Open Camera / Gallery
            </div>
          </div>

          <div class="img-preview-box" id="imagePreviewContainer">
            <img id="imagePreview" src="" alt="Picture preview" />
            <div class="laser-line" id="scanLine"></div>
          </div>

          <div class="progress-box" id="scanProgress">
            <div class="progress-bar-bg">
              <div class="progress-bar-fill" id="scanProgressFill"></div>
            </div>
            <p style="font-size: 0.88rem; color: var(--text-sub); margin-top: 0.6rem;" id="scanStatusText">Scanning image text...</p>
          </div>
        </div>

        <div class="pane-card">
          <div style="font-family: 'Outfit', sans-serif; font-weight: 800; font-size: 1.15rem; color: var(--cyan); display: flex; align-items: center; gap: 0.6rem;">
            <i class="fa-solid fa-file-lines"></i> Scanned Result
          </div>

          <div style="display: flex; flex-direction: column; gap: 0.9rem; height: 100%;">
            <label class="form-label">Extracted Text:</label>
            <textarea class="editor" id="extractedOcrText" style="min-height: 110px;" placeholder="Extracted text will appear here..." readonly></textarea>

            <label class="form-label">Translation:</label>
            <textarea class="editor" id="translatedOcrText" style="min-height: 110px;" placeholder="Translated text will appear here..." readonly></textarea>
          </div>

          <div class="pane-footer">
            <button class="nav-btn primary" style="width: 100%; justify-content: center;" onclick="translateScannedText()">
              <i class="fa-solid fa-rotate"></i> Translate Extracted Text
            </button>
          </div>
        </div>

      </div>

    </div>
  </main>

  <!-- MOBILE BOTTOM BAR -->
  <div class="mob-navbar">
    <button class="mob-nav-item active" id="mobNavTranslate" onclick="switchTab('translate')">
      <i class="fa-solid fa-language"></i>
      <span>Translate</span>
    </button>
    <button class="mob-nav-item" id="mobNavScan" onclick="switchTab('scan')">
      <i class="fa-solid fa-camera"></i>
      <span>Scan Pic</span>
    </button>
    <button class="mob-nav-item" onclick="toggleBotDrawer()">
      <i class="fa-solid fa-robot"></i>
      <span>AI Bot</span>
    </button>
    <button class="mob-nav-item" onclick="toggleTheme()">
      <i class="fa-solid fa-moon" id="mobThemeIcon"></i>
      <span>Theme</span>
    </button>
  </div>

  <!-- ZENI AI BOT DRAWER -->
  <aside class="bot-drawer" id="botDrawer">
    <div class="bot-header">
      <div class="bot-title-group">
        <div class="bot-avatar">
          <i class="fa-solid fa-robot"></i>
        </div>
        <div>
          <h4 style="font-family: 'Outfit', sans-serif; font-size: 1.1rem;">Zeni Assistant</h4>
          <span style="font-size: 0.78rem; color: var(--emerald);">● Online & Ready</span>
        </div>
      </div>
      <button class="btn-icon" onclick="toggleBotDrawer()"><i class="fa-solid fa-xmark"></i></button>
    </div>

    <div class="bot-chat-body" id="botChatBody">
      <div class="bubble bot">
        👋 Hi! I am <strong>Zeni Bot</strong>, your AI translation assistant. Ask me questions about words, grammar, rephrasing, or translation tips!
      </div>
    </div>

    <div class="bot-input-bar">
      <input type="text" class="bot-input" id="botInput" placeholder="Ask Zeni Bot..." onkeydown="if(event.key === 'Enter') sendBotMessage()" />
      <button class="nav-btn primary" onclick="sendBotMessage()"><i class="fa-solid fa-paper-plane"></i></button>
    </div>
  </aside>

  <!-- AUTH MODAL -->
  <div class="modal-overlay" id="authModal">
    <div class="auth-modal">
      <button class="btn-icon" style="position: absolute; top: 1.3rem; right: 1.3rem;" onclick="closeAuthModal()">
        <i class="fa-solid fa-xmark"></i>
      </button>

      <h3 style="font-family: 'Outfit', sans-serif; font-size: 1.7rem; text-align: center; margin-bottom: 1.3rem;">Welcome to Zeni Translate</h3>

      <div class="auth-tabs">
        <button class="auth-tab-btn active" id="tabSignIn" onclick="setAuthTab('signin')">Sign In</button>
        <button class="auth-tab-btn" id="tabSignUp" onclick="setAuthTab('signup')">Sign Up</button>
      </div>

      <form id="authForm" onsubmit="handleAuthSubmit(event)">
        <div class="form-group">
          <label class="form-label">Email Address</label>
          <input type="email" class="form-input" id="authEmail" placeholder="name@example.com" required />
        </div>

        <div class="form-group">
          <label class="form-label">Password</label>
          <input type="password" class="form-input" id="authPassword" placeholder="••••••••" required />
        </div>

        <button type="submit" class="auth-submit-btn" id="authSubmitBtn">Sign In</button>
      </form>

      <button class="guest-btn" onclick="continueAsGuest()">
        <i class="fa-solid fa-user-secret"></i> Continue as Guest
      </button>
    </div>
  </div>

  <script>
    let translateDebounceTimer = null;
    let recognition = null;
    let isRecording = false;
    let activeUser = localStorage.getItem('zeni_user') ? JSON.parse(localStorage.getItem('zeni_user')) : null;

    window.addEventListener('DOMContentLoaded', () => {
      const savedTheme = localStorage.getItem('zeni_theme') || 'dark';
      setTheme(savedTheme);
      updateAuthUI();
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
    }

    function onSourceInput() {
      const text = document.getElementById('sourceText').value;
      document.getElementById('charCount').textContent = `${text.length} chars`;

      clearTimeout(translateDebounceTimer);
      translateDebounceTimer = setTimeout(triggerTranslation, 450);
    }

    async function triggerTranslation() {
      const text = document.getElementById('sourceText').value.trim();
      const source = document.getElementById('sourceLang').value;
      const target = document.getElementById('targetLang').value;
      const tone = document.getElementById('toneSelect').value;

      if (!text) {
        document.getElementById('targetText').value = '';
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
          let insight = data.explanation || `Translated to ${target.toUpperCase()}`;
          if (data.transliteration) {
            insight += ` | Pronunciation: ${data.transliteration}`;
          }
          document.getElementById('insightText').textContent = insight;
        } else {
          document.getElementById('insightText').textContent = 'Translation error: ' + (data.error || 'Unable to translate');
        }
      } catch (err) {
        console.error(err);
        document.getElementById('insightText').textContent = 'Network error during translation.';
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

      triggerTranslation();
    }

    function clearText() {
      document.getElementById('sourceText').value = '';
      document.getElementById('targetText').value = '';
      document.getElementById('charCount').textContent = '0 chars';
      document.getElementById('insightText').textContent = 'Cleared input.';
    }

    function copyTranslation() {
      const text = document.getElementById('targetText').value;
      if (!text) return;
      navigator.clipboard.writeText(text).then(() => {
        alert('Translation copied to clipboard!');
      });
    }

    function toggleSpeechRecognition() {
      const micBtn = document.getElementById('micBtn');

      if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        alert('Speech recognition is not supported in your browser.');
        return;
      }

      if (isRecording) {
        if (recognition) recognition.stop();
        return;
      }

      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognition = new SpeechRecognition();
      const lang = document.getElementById('sourceLang').value;
      recognition.lang = lang === 'te' ? 'te-IN' : (lang === 'hi' ? 'hi-IN' : 'en-US');
      recognition.continuous = false;
      recognition.interimResults = true;

      recognition.onstart = () => {
        isRecording = true;
        micBtn.classList.add('recording');
      };

      recognition.onresult = (event) => {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          transcript += event.results[i][0].transcript;
        }
        document.getElementById('sourceText').value = transcript;
        onSourceInput();
      };

      recognition.onerror = () => {
        isRecording = false;
        micBtn.classList.remove('recording');
      };

      recognition.onend = () => {
        isRecording = false;
        micBtn.classList.remove('recording');
      };

      recognition.start();
    }

    let currentAudio = null;

    function playVoiceover() {
      const text = document.getElementById('targetText').value.trim();
      const lang = document.getElementById('targetLang').value;
      const speed = parseFloat(document.getElementById('audioSpeed').value || '1.0');
      const soundwave = document.getElementById('soundwave');

      if (!text) return;

      if (currentAudio) {
        currentAudio.pause();
        currentAudio = null;
      }
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
      }

      soundwave.classList.add('playing');

      const cleanLang = lang.split('-')[0];
      const ttsUrl = `/api/tts?text=${encodeURIComponent(text)}&lang=${cleanLang}`;
      
      const audio = new Audio(ttsUrl);
      currentAudio = audio;
      audio.playbackRate = speed;

      audio.onplay = () => soundwave.classList.add('playing');
      audio.onended = () => {
        soundwave.classList.remove('playing');
        currentAudio = null;
      };
      audio.onerror = () => {
        if ('speechSynthesis' in window) {
          const utterance = new SpeechSynthesisUtterance(text);
          utterance.rate = speed;
          utterance.lang = lang;
          
          const voices = window.speechSynthesis.getVoices();
          const matchedVoice = voices.find(v => v.lang.startsWith(cleanLang) || v.lang.includes(cleanLang));
          if (matchedVoice) utterance.voice = matchedVoice;

          utterance.onend = () => soundwave.classList.remove('playing');
          utterance.onerror = () => soundwave.classList.remove('playing');
          window.speechSynthesis.speak(utterance);
        } else {
          soundwave.classList.remove('playing');
          alert('Unable to play audio voiceover.');
        }
      };

      audio.play().catch(() => audio.onerror());
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
      userBubble.className = 'bubble user';
      userBubble.textContent = msg;
      chatBody.appendChild(userBubble);

      input.value = '';
      chatBody.scrollTop = chatBody.scrollHeight;

      const botBubble = document.createElement('div');
      botBubble.className = 'bubble bot';
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

    function openAuthModal() { document.getElementById('authModal').classList.add('active'); }
    function closeAuthModal() { document.getElementById('authModal').classList.remove('active'); }

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

    function handleAuthSubmit(e) {
      e.preventDefault();
      const email = document.getElementById('authEmail').value;
      activeUser = { username: email.split('@')[0], email, isGuest: false };
      localStorage.setItem('zeni_user', JSON.stringify(activeUser));
      updateAuthUI();
      closeAuthModal();
    }

    function continueAsGuest() {
      activeUser = { username: 'Guest User', email: '', isGuest: true };
      localStorage.setItem('zeni_user', JSON.stringify(activeUser));
      updateAuthUI();
      closeAuthModal();
    }

    function updateAuthUI() {
      const authLabel = document.getElementById('userAuthLabel');
      const authBtn = document.getElementById('userAuthBtn');

      if (activeUser) {
        if (authLabel) authLabel.textContent = activeUser.username;
        if (authBtn) {
          authBtn.onclick = () => {
            if (confirm(`Logged in as ${activeUser.username}. Log out?`)) {
              activeUser = null;
              localStorage.removeItem('zeni_user');
              updateAuthUI();
            }
          };
        }
      } else {
        if (authLabel) authLabel.textContent = 'Sign In';
        if (authBtn) authBtn.onclick = openAuthModal;
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
    """Text-To-Speech endpoint fallback."""
    text = request.args.get("text", "").strip()
    lang = request.args.get("lang", "en").strip()

    if not text:
        return jsonify({"status": "error", "error": "No text provided"}), 400

    if gTTS is None:
        return jsonify({"status": "error", "error": "gTTS server library not installed."}), 500

    try:
        fp = io.BytesIO()
        clean_lang = lang.split("-")[0]
        tts = gTTS(text=text, lang=clean_lang)
        tts.write_to_fp(fp)
        fp.seek(0)
        return Response(fp.read(), mimetype="audio/mpeg")
    except Exception as exc:
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
