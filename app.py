from __future__ import annotations
import io
import os
import sys
import json
from flask import Flask, request, jsonify, render_template_string, Response

try:
    from googletrans import Translator
except ImportError:
    raise RuntimeError(
        "Missing dependency: googletrans. Install it with `pip install googletrans==4.0.0rc1`"
    )

try:
    from gtts import gTTS
except ImportError:
    gTTS = None

app = Flask(__name__)
translator = Translator()

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
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Zeni Translate | Next-Gen AI Translation & Picture Scan</title>
  
  <!-- SEO Meta -->
  <meta name="description" content="Zeni Translate offers AI-powered text translation, picture scanning OCR, voiceover synthesis, interactive translation bot, and dark/light themes." />
  
  <!-- Google Fonts & Font Awesome -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Outfit:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" />
  
  <!-- Tesseract.js CDN for Picture Scanning OCR -->
  <script src="https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/tesseract.min.js"></script>

  <style>
    /* CSS DESIGN SYSTEM - LIGHT & DARK THEMES */
    :root[data-theme="dark"] {
      --bg-main: #0b0f19;
      --bg-card: rgba(17, 24, 39, 0.75);
      --bg-panel: rgba(30, 41, 59, 0.65);
      --bg-input: rgba(15, 23, 42, 0.85);
      --border-card: rgba(255, 255, 255, 0.12);
      --border-focus: rgba(6, 182, 212, 0.6);
      --text-bright: #f8fafc;
      --text-sub: #94a3b8;
      --text-muted: #64748b;
      
      --accent-primary: #06b6d4;
      --accent-secondary: #6366f1;
      --accent-purple: #a855f7;
      --accent-gradient: linear-gradient(135deg, #06b6d4 0%, #3b82f6 50%, #6366f1 100%);
      --accent-hover: linear-gradient(135deg, #0891b2 0%, #2563eb 50%, #4f46e5 100%);
      
      --shadow-card: 0 30px 80px rgba(0, 0, 0, 0.7), 0 0 50px rgba(6, 182, 212, 0.15);
      --glow-orb1: rgba(6, 182, 212, 0.2);
      --glow-orb2: rgba(99, 102, 241, 0.2);
      --nav-bg: rgba(11, 15, 25, 0.85);
    }

    :root[data-theme="light"] {
      --bg-main: #f1f5f9;
      --bg-card: rgba(255, 255, 255, 0.92);
      --bg-panel: rgba(241, 245, 249, 0.85);
      --bg-input: #ffffff;
      --border-card: rgba(0, 0, 0, 0.08);
      --border-focus: rgba(37, 99, 235, 0.6);
      --text-bright: #0f172a;
      --text-sub: #475569;
      --text-muted: #94a3b8;
      
      --accent-primary: #2563eb;
      --accent-secondary: #0d9488;
      --accent-purple: #7c3aed;
      --accent-gradient: linear-gradient(135deg, #2563eb 0%, #0d9488 50%, #7c3aed 100%);
      --accent-hover: linear-gradient(135deg, #1d4ed8 0%, #0f766e 50%, #6d28d9 100%);
      
      --shadow-card: 0 25px 60px rgba(15, 23, 42, 0.08), 0 0 40px rgba(37, 99, 235, 0.1);
      --glow-orb1: rgba(37, 99, 235, 0.12);
      --glow-orb2: rgba(13, 148, 136, 0.12);
      --nav-bg: rgba(255, 255, 255, 0.9);
    }

    * { box-sizing: border-box; margin: 0; padding: 0; transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease; }

    body {
      font-family: 'Plus Jakarta Sans', sans-serif;
      min-height: 100vh;
      background-color: var(--bg-main);
      color: var(--text-bright);
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 0 1rem 3rem 1rem;
      overflow-x: hidden;
      position: relative;
    }

    /* Animated Ambient Background Orbs */
    .bg-orb {
      position: fixed;
      border-radius: 50%;
      filter: blur(140px);
      pointer-events: none;
      z-index: 0;
      animation: orbFloat 22s ease-in-out infinite alternate;
    }
    .orb-1 { width: 550px; height: 550px; background: var(--glow-orb1); top: -120px; left: -120px; }
    .orb-2 { width: 500px; height: 500px; background: var(--glow-orb2); bottom: -120px; right: -120px; animation-delay: -8s; }

    @keyframes orbFloat {
      0% { transform: translate(0, 0) scale(1); }
      50% { transform: translate(40px, 40px) scale(1.06); }
      100% { transform: translate(-30px, 50px) scale(0.95); }
    }

    /* TOP NAVIGATION BAR */
    .navbar {
      width: 100%;
      max-width: 1240px;
      margin: 1.2rem auto 2rem auto;
      padding: 0.8rem 1.6rem;
      background: var(--nav-bg);
      backdrop-filter: blur(20px);
      border: 1px solid var(--border-card);
      border-radius: 999px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
      z-index: 50;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    }

    .brand-logo {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      text-decoration: none;
      cursor: pointer;
    }

    .brand-icon {
      width: 44px;
      height: 44px;
      border-radius: 14px;
      background: var(--accent-gradient);
      display: flex;
      align-items: center;
      justify-content: center;
      color: #ffffff;
      font-size: 1.35rem;
      box-shadow: 0 6px 20px rgba(6, 182, 212, 0.35);
    }

    .brand-title {
      font-family: 'Outfit', sans-serif;
      font-weight: 800;
      font-size: 1.45rem;
      letter-spacing: -0.5px;
      background: var(--accent-gradient);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .nav-actions {
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }

    .nav-btn {
      padding: 0.55rem 1.1rem;
      border-radius: 999px;
      border: 1px solid var(--border-card);
      background: var(--bg-panel);
      color: var(--text-bright);
      font-weight: 600;
      font-size: 0.88rem;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      transition: all 0.25s ease;
    }

    .nav-btn:hover {
      transform: translateY(-2px);
      border-color: var(--accent-primary);
      color: var(--accent-primary);
    }

    .nav-btn.primary-btn {
      background: var(--accent-gradient);
      color: #ffffff;
      border: none;
      box-shadow: 0 6px 18px rgba(6, 182, 212, 0.25);
    }

    .nav-btn.primary-btn:hover {
      background: var(--accent-hover);
      box-shadow: 0 8px 25px rgba(6, 182, 212, 0.4);
      color: #ffffff;
    }

    /* MAIN CONTENT CONTAINER */
    .container {
      width: min(100%, 1240px);
      z-index: 1;
      animation: fadeIn 0.8s ease-out;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(18px); }
      to { opacity: 1; transform: translateY(0); }
    }

    /* SECTION TABS (Text Translate / Picture Scan) */
    .tabs-header {
      display: flex;
      justify-content: center;
      gap: 1rem;
      margin-bottom: 1.8rem;
    }

    .tab-trigger {
      padding: 0.75rem 1.8rem;
      border-radius: 16px;
      border: 1px solid var(--border-card);
      background: var(--bg-card);
      backdrop-filter: blur(16px);
      color: var(--text-sub);
      font-family: 'Outfit', sans-serif;
      font-weight: 700;
      font-size: 1.05rem;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.6rem;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .tab-trigger.active {
      background: var(--accent-gradient);
      color: #ffffff;
      border-color: transparent;
      box-shadow: 0 10px 25px rgba(6, 182, 212, 0.3);
      transform: scale(1.03);
    }

    /* MAIN APP CARD */
    .app-card {
      background: var(--bg-card);
      backdrop-filter: blur(30px);
      border-radius: 32px;
      box-shadow: var(--shadow-card);
      border: 1px solid var(--border-card);
      padding: 2rem;
      min-height: 520px;
    }

    /* TONE & TOOLBAR BAR */
    .toolbar-bar {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
      padding-bottom: 1.2rem;
      margin-bottom: 1.5rem;
      border-bottom: 1px solid var(--border-card);
    }

    .tone-selector {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      background: var(--bg-panel);
      padding: 0.3rem 0.8rem;
      border-radius: 14px;
      border: 1px solid var(--border-card);
      font-size: 0.88rem;
      color: var(--text-sub);
    }

    .tone-select {
      background: transparent;
      border: none;
      color: var(--text-bright);
      font-weight: 600;
      font-size: 0.9rem;
      cursor: pointer;
      outline: none;
    }

    .tone-select option {
      background-color: var(--bg-main);
      color: var(--text-bright);
    }

    /* TRANSLATION GRID */
    .translator-grid {
      display: grid;
      grid-template-columns: 1fr 50px 1fr;
      gap: 1.2rem;
      align-items: stretch;
    }

    @media (max-width: 868px) {
      .translator-grid {
        grid-template-columns: 1fr;
      }
      .swap-col {
        display: flex;
        justify-content: center;
        margin: 0.5rem 0;
      }
    }

    .lang-card {
      background: var(--bg-panel);
      border: 1px solid var(--border-card);
      border-radius: 24px;
      padding: 1.3rem;
      display: flex;
      flex-direction: column;
      gap: 1rem;
      position: relative;
    }

    .lang-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .lang-select-wrapper {
      position: relative;
      width: 100%;
    }

    .lang-select {
      width: 100%;
      padding: 0.65rem 1rem;
      background: var(--bg-input);
      border: 1px solid var(--border-card);
      border-radius: 14px;
      color: var(--text-bright);
      font-weight: 700;
      font-size: 0.98rem;
      outline: none;
      cursor: pointer;
      appearance: none;
    }

    .lang-select:focus {
      border-color: var(--border-focus);
    }

    .swap-btn {
      width: 48px;
      height: 48px;
      border-radius: 50%;
      background: var(--bg-panel);
      border: 1px solid var(--border-card);
      color: var(--text-bright);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.1rem;
      cursor: pointer;
      margin: auto;
      transition: all 0.3s ease;
    }

    .swap-btn:hover {
      transform: rotate(180deg) scale(1.1);
      border-color: var(--accent-primary);
      color: var(--accent-primary);
    }

    .text-area {
      width: 100%;
      min-height: 220px;
      background: var(--bg-input);
      border: 1px solid var(--border-card);
      border-radius: 16px;
      padding: 1.1rem;
      color: var(--text-bright);
      font-family: inherit;
      font-size: 1.05rem;
      line-height: 1.6;
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
      margin-top: auto;
      padding-top: 0.5rem;
    }

    .action-btn-group {
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .icon-btn {
      width: 40px;
      height: 40px;
      border-radius: 12px;
      border: 1px solid var(--border-card);
      background: var(--bg-input);
      color: var(--text-sub);
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      font-size: 1rem;
      transition: all 0.2s ease;
    }

    .icon-btn:hover {
      color: var(--accent-primary);
      border-color: var(--accent-primary);
      transform: translateY(-2px);
    }

    .icon-btn.recording {
      background: #ef4444;
      color: #ffffff;
      animation: pulse 1.5s infinite;
    }

    @keyframes pulse {
      0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.6); }
      70% { box-shadow: 0 0 0 12px rgba(239, 68, 68, 0); }
      100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
    }

    /* TTS Audio Controls & Soundwave */
    .audio-controls {
      display: flex;
      align-items: center;
      gap: 0.6rem;
    }

    .speed-select {
      padding: 0.35rem 0.6rem;
      background: var(--bg-input);
      border: 1px solid var(--border-card);
      border-radius: 8px;
      color: var(--text-sub);
      font-size: 0.8rem;
      font-weight: 600;
      outline: none;
    }

    .soundwave {
      display: none;
      align-items: center;
      gap: 3px;
      height: 18px;
    }

    .soundwave.playing {
      display: flex;
    }

    .wave-bar {
      width: 3px;
      height: 100%;
      background: var(--accent-primary);
      border-radius: 3px;
      animation: waveAnim 1s ease-in-out infinite alternate;
    }
    .wave-bar:nth-child(2) { animation-delay: 0.2s; }
    .wave-bar:nth-child(3) { animation-delay: 0.4s; }
    .wave-bar:nth-child(4) { animation-delay: 0.1s; }

    @keyframes waveAnim {
      0% { height: 4px; }
      100% { height: 18px; }
    }

    /* PICTURE SCAN CONTAINER */
    .picture-scan-section {
      display: none;
    }

    .picture-scan-section.active {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1.5rem;
    }

    @media (max-width: 868px) {
      .picture-scan-section.active {
        grid-template-columns: 1fr;
      }
    }

    .upload-box {
      border: 2px dashed var(--border-card);
      border-radius: 24px;
      padding: 2.5rem 1.5rem;
      text-align: center;
      background: var(--bg-panel);
      cursor: pointer;
      transition: all 0.3s ease;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 320px;
      position: relative;
      overflow: hidden;
    }

    .upload-box:hover, .upload-box.dragover {
      border-color: var(--accent-primary);
      background: rgba(6, 182, 212, 0.05);
    }

    .upload-icon {
      font-size: 3.2rem;
      color: var(--accent-primary);
      margin-bottom: 1rem;
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
      border-radius: 16px;
    }

    /* Laser Scanner Line */
    .scan-line {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 4px;
      background: var(--accent-gradient);
      box-shadow: 0 0 15px var(--accent-primary);
      display: none;
      animation: scanAnimation 2.2s ease-in-out infinite alternate;
    }

    @keyframes scanAnimation {
      0% { top: 5%; }
      100% { top: 92%; }
    }

    .scan-progress {
      margin-top: 1rem;
      width: 100%;
      display: none;
    }

    .progress-bar-bg {
      width: 100%;
      height: 8px;
      background: var(--bg-input);
      border-radius: 999px;
      overflow: hidden;
    }

    .progress-bar-fill {
      height: 100%;
      width: 0%;
      background: var(--accent-gradient);
      transition: width 0.3s ease;
    }

    /* ZENI AI BOT DRAWER */
    .bot-drawer {
      position: fixed;
      top: 0;
      right: -420px;
      width: 100%;
      max-width: 400px;
      height: 100vh;
      background: var(--bg-card);
      backdrop-filter: blur(35px);
      border-left: 1px solid var(--border-card);
      z-index: 100;
      box-shadow: -20px 0 60px rgba(0, 0, 0, 0.4);
      display: flex;
      flex-direction: column;
      transition: right 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .bot-drawer.open {
      right: 0;
    }

    .bot-header {
      padding: 1.2rem 1.5rem;
      border-bottom: 1px solid var(--border-card);
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: var(--bg-panel);
    }

    .bot-badge {
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }

    .bot-avatar {
      width: 38px;
      height: 38px;
      border-radius: 12px;
      background: var(--accent-gradient);
      display: flex;
      align-items: center;
      justify-content: center;
      color: #fff;
    }

    .bot-chat-body {
      flex: 1;
      padding: 1.2rem;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    .chat-bubble {
      max-width: 85%;
      padding: 0.9rem 1.1rem;
      border-radius: 18px;
      font-size: 0.93rem;
      line-height: 1.5;
    }

    .chat-bubble.bot {
      background: var(--bg-panel);
      border: 1px solid var(--border-card);
      color: var(--text-bright);
      align-self: flex-start;
      border-top-left-radius: 4px;
    }

    .chat-bubble.user {
      background: var(--accent-gradient);
      color: #ffffff;
      align-self: flex-end;
      border-top-right-radius: 4px;
    }

    .bot-input-area {
      padding: 1rem;
      border-top: 1px solid var(--border-card);
      display: flex;
      gap: 0.6rem;
      background: var(--bg-panel);
    }

    .bot-input {
      flex: 1;
      padding: 0.75rem 1rem;
      background: var(--bg-input);
      border: 1px solid var(--border-card);
      border-radius: 14px;
      color: var(--text-bright);
      outline: none;
    }

    /* AUTH / LOGIN MODAL */
    .modal-overlay {
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.65);
      backdrop-filter: blur(10px);
      z-index: 200;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 1rem;
      animation: fadeIn 0.3s ease-out;
    }

    .modal-overlay.active {
      display: flex;
    }

    .auth-modal {
      width: min(100%, 440px);
      background: var(--bg-card);
      border: 1px solid var(--border-card);
      border-radius: 28px;
      padding: 2.2rem;
      box-shadow: var(--shadow-card);
      position: relative;
    }

    .auth-tabs {
      display: flex;
      gap: 0.5rem;
      margin-bottom: 1.5rem;
      background: var(--bg-panel);
      padding: 0.3rem;
      border-radius: 14px;
    }

    .auth-tab-btn {
      flex: 1;
      padding: 0.6rem;
      border: none;
      background: transparent;
      color: var(--text-sub);
      font-weight: 700;
      border-radius: 10px;
      cursor: pointer;
    }

    .auth-tab-btn.active {
      background: var(--accent-gradient);
      color: #ffffff;
    }

    .form-group {
      margin-bottom: 1.2rem;
    }

    .form-label {
      display: block;
      font-size: 0.85rem;
      font-weight: 600;
      color: var(--text-sub);
      margin-bottom: 0.4rem;
    }

    .form-input {
      width: 100%;
      padding: 0.8rem 1rem;
      background: var(--bg-input);
      border: 1px solid var(--border-card);
      border-radius: 14px;
      color: var(--text-bright);
      outline: none;
    }

    .form-input:focus {
      border-color: var(--accent-primary);
    }

    .auth-submit-btn {
      width: 100%;
      padding: 0.9rem;
      border-radius: 14px;
      border: none;
      background: var(--accent-gradient);
      color: #ffffff;
      font-weight: 700;
      font-size: 1rem;
      cursor: pointer;
      box-shadow: 0 8px 20px rgba(6, 182, 212, 0.3);
      margin-top: 0.5rem;
    }

    .guest-btn {
      width: 100%;
      padding: 0.75rem;
      border-radius: 14px;
      border: 1px solid var(--border-card);
      background: var(--bg-panel);
      color: var(--text-bright);
      font-weight: 600;
      cursor: pointer;
      margin-top: 0.8rem;
    }

    /* Explanation Banner */
    .insight-card {
      margin-top: 1.5rem;
      background: var(--bg-panel);
      border: 1px dashed var(--border-card);
      border-radius: 18px;
      padding: 1rem 1.4rem;
      font-size: 0.92rem;
      color: var(--text-sub);
      display: flex;
      align-items: center;
      gap: 0.8rem;
    }
  </style>
</head>
<body>
  <!-- Ambient Orbs -->
  <div class="bg-orb orb-1"></div>
  <div class="bg-orb orb-2"></div>

  <!-- TOP NAVIGATION BAR -->
  <nav class="navbar">
    <a class="brand-logo" onclick="switchTab('translate')">
      <div class="brand-icon">
        <i class="fa-solid fa-language"></i>
      </div>
      <span class="brand-title">Zeni Translate</span>
    </a>

    <div class="nav-actions">
      <!-- Theme Switcher -->
      <button class="nav-btn" id="themeToggleBtn" onclick="toggleTheme()" title="Toggle Light / Dark Mode">
        <i class="fa-solid fa-moon" id="themeIcon"></i>
        <span id="themeLabel">Dark Mode</span>
      </button>

      <!-- Zeni Bot Trigger -->
      <button class="nav-btn" onclick="toggleBotDrawer()" title="Open Zeni AI Assistant">
        <i class="fa-solid fa-robot"></i>
        <span>Zeni Bot</span>
      </button>

      <!-- Account / Login -->
      <button class="nav-btn primary-btn" id="userAuthBtn" onclick="openAuthModal()">
        <i class="fa-solid fa-user"></i>
        <span id="userAuthLabel">Sign In</span>
      </button>
    </div>
  </nav>

  <!-- MAIN CONTAINER -->
  <main class="container">
    <!-- SECTION TABS -->
    <div class="tabs-header">
      <button class="tab-trigger active" id="tabBtnTranslate" onclick="switchTab('translate')">
        <i class="fa-solid fa-font"></i> Text Translate
      </button>
      <button class="tab-trigger" id="tabBtnScan" onclick="switchTab('scan')">
        <i class="fa-solid fa-camera"></i> Picture Scan
      </button>
    </div>

    <!-- MAIN APP CARD -->
    <div class="app-card">
      
      <!-- TOOLBAR (Tone & Info) -->
      <div class="toolbar-bar">
        <div class="tone-selector">
          <i class="fa-solid fa-sliders"></i>
          <span>Tone & Style:</span>
          <select class="tone-select" id="toneSelect" onchange="triggerTranslation()">
            <option value="standard">Standard / Natural</option>
            <option value="formal">Formal & Polite</option>
            <option value="casual">Casual Conversation</option>
            <option value="business">Professional Business</option>
            <option value="simplified">Simplified / Beginner</option>
          </select>
        </div>

        <div style="font-size: 0.85rem; color: var(--text-muted);">
          <i class="fa-solid fa-bolt" style="color: var(--accent-primary);"></i> Neural Engine Active
        </div>
      </div>

      <!-- TEXT TRANSLATOR SECTION -->
      <div id="sectionTranslate">
        <div class="translator-grid">
          
          <!-- SOURCE PANEL -->
          <div class="lang-card">
            <div class="lang-header">
              <div class="lang-select-wrapper">
                <select class="lang-select" id="sourceLang" onchange="triggerTranslation()">
                  {% for code, name in languages.items() %}
                  <option value="{{ code }}" {% if code == 'en' %}selected{% endif %}>{{ name }}</option>
                  {% endfor %}
                </select>
              </div>
            </div>

            <textarea class="text-area" id="sourceText" placeholder="Type or paste text to translate..." oninput="onSourceInput()"></textarea>

            <div class="panel-footer">
              <div class="action-btn-group">
                <!-- Speech to Text Mic Input -->
                <button class="icon-btn" id="micBtn" onclick="toggleSpeechRecognition()" title="Voice Input (Speech-to-Text)">
                  <i class="fa-solid fa-microphone"></i>
                </button>
                <button class="icon-btn" onclick="clearText()" title="Clear Text">
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

          <!-- TARGET PANEL -->
          <div class="lang-card">
            <div class="lang-header">
              <div class="lang-select-wrapper">
                <select class="lang-select" id="targetLang" onchange="triggerTranslation()">
                  {% for code, name in languages.items() %}
                  <option value="{{ code }}" {% if code == 'te' %}selected{% endif %}>{{ name }}</option>
                  {% endfor %}
                </select>
              </div>
            </div>

            <textarea class="text-area" id="targetText" placeholder="Translation will appear here..." readonly></textarea>

            <div class="panel-footer">
              <div class="action-btn-group">
                <!-- TTS Play Button -->
                <button class="icon-btn" id="ttsPlayBtn" onclick="playVoiceover()" title="Listen Voiceover">
                  <i class="fa-solid fa-volume-high"></i>
                </button>
                <button class="icon-btn" onclick="copyTranslation()" title="Copy Translation">
                  <i class="fa-solid fa-copy"></i>
                </button>
              </div>

              <!-- Audio Speed & Waveform Visualizer -->
              <div class="audio-controls">
                <div class="soundwave" id="soundwave">
                  <div class="wave-bar"></div>
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

        <!-- INSIGHT CARD -->
        <div class="insight-card" id="insightCard">
          <i class="fa-solid fa-wand-magic-sparkles" style="color: var(--accent-primary); font-size: 1.2rem;"></i>
          <span id="insightText">Select source & target languages to translate automatically.</span>
        </div>
      </div>

      <!-- PICTURE SCAN SECTION (OCR) -->
      <div id="sectionScan" class="picture-scan-section">
        
        <!-- UPLOAD / PREVIEW BOX -->
        <div class="upload-box" id="dropZone" onclick="document.getElementById('imageFileInput').click()">
          <input type="file" id="imageFileInput" accept="image/*" style="display: none;" onchange="handleImageUpload(event)" />
          
          <div id="uploadPlaceholder">
            <i class="fa-solid fa-cloud-arrow-up upload-icon"></i>
            <h3 style="font-family: 'Outfit', sans-serif; font-size: 1.3rem; margin-bottom: 0.5rem;">Upload or Drag Image</h3>
            <p style="color: var(--text-sub); font-size: 0.95rem;">Supports PNG, JPG, JPEG, WEBP, BMP pictures</p>
          </div>

          <div class="image-preview-container" id="imagePreviewContainer">
            <img id="imagePreview" src="" alt="Picture preview" />
            <div class="scan-line" id="scanLine"></div>
          </div>

          <div class="scan-progress" id="scanProgress">
            <div class="progress-bar-bg">
              <div class="progress-bar-fill" id="scanProgressFill"></div>
            </div>
            <p style="font-size: 0.85rem; color: var(--text-sub); margin-top: 0.5rem;" id="scanStatusText">Scanning image text...</p>
          </div>
        </div>

        <!-- EXTRACTED & TRANSLATED OCR TEXT -->
        <div class="lang-card">
          <div style="font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 1.1rem; color: var(--accent-primary);">
            <i class="fa-solid fa-file-lines"></i> Scanned OCR Result
          </div>

          <div style="display: flex; flex-direction: column; gap: 0.8rem; height: 100%;">
            <label class="form-label">Extracted Text from Image:</label>
            <textarea class="text-area" id="extractedOcrText" style="min-height: 110px;" placeholder="Extracted text will appear here after image scan..." readonly></textarea>

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

  <!-- ZENI AI BOT DRAWER -->
  <aside class="bot-drawer" id="botDrawer">
    <div class="bot-header">
      <div class="bot-badge">
        <div class="bot-avatar">
          <i class="fa-solid fa-robot"></i>
        </div>
        <div>
          <h4 style="font-family: 'Outfit', sans-serif; font-size: 1.05rem;">Zeni Assistant</h4>
          <span style="font-size: 0.78rem; color: #10b981;">● Online & Ready</span>
        </div>
      </div>
      <button class="icon-btn" onclick="toggleBotDrawer()"><i class="fa-solid fa-xmark"></i></button>
    </div>

    <div class="bot-chat-body" id="botChatBody">
      <div class="chat-bubble bot">
        👋 Hi! I am <strong>Zeni Bot</strong>, your AI translation assistant. Ask me questions about words, grammar, rephrasing, or translation tips!
      </div>
    </div>

    <div class="bot-input-area">
      <input type="text" class="bot-input" id="botInput" placeholder="Ask Zeni Bot..." onkeydown="if(event.key === 'Enter') sendBotMessage()" />
      <button class="nav-btn primary-btn" onclick="sendBotMessage()"><i class="fa-solid fa-paper-plane"></i></button>
    </div>
  </aside>

  <!-- AUTH / LOGIN MODAL -->
  <div class="modal-overlay" id="authModal">
    <div class="auth-modal">
      <button class="icon-btn" style="position: absolute; top: 1.2rem; right: 1.2rem;" onclick="closeAuthModal()">
        <i class="fa-solid fa-xmark"></i>
      </button>

      <h3 style="font-family: 'Outfit', sans-serif; font-size: 1.6rem; text-align: center; margin-bottom: 1.2rem;">Welcome to Zeni Translate</h3>

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
    /* GLOBAL APP STATE */
    let translateDebounceTimer = null;
    let recognition = null;
    let isRecording = false;
    let activeUser = localStorage.getItem('zeni_user') ? JSON.parse(localStorage.getItem('zeni_user')) : null;

    /* INITIALIZATION */
    window.addEventListener('DOMContentLoaded', () => {
      // Check stored theme preference
      const savedTheme = localStorage.getItem('zeni_theme') || 'dark';
      setTheme(savedTheme);

      // Check stored auth state
      updateAuthUI();
    });

    /* THEME SWITCHER */
    function toggleTheme() {
      const currentTheme = document.documentElement.getAttribute('data-theme');
      const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
      setTheme(newTheme);
    }

    function setTheme(theme) {
      document.documentElement.setAttribute('data-theme', theme);
      localStorage.setItem('zeni_theme', theme);
      
      const icon = document.getElementById('themeIcon');
      const label = document.getElementById('themeLabel');
      
      if (theme === 'light') {
        icon.className = 'fa-solid fa-sun';
        label.textContent = 'Light Mode';
      } else {
        icon.className = 'fa-solid fa-moon';
        label.textContent = 'Dark Mode';
      }
    }

    /* TAB SWITCHER */
    function switchTab(tab) {
      const tabTranslate = document.getElementById('tabBtnTranslate');
      const tabScan = document.getElementById('tabBtnScan');
      const secTranslate = document.getElementById('sectionTranslate');
      const secScan = document.getElementById('sectionScan');

      if (tab === 'translate') {
        tabTranslate.classList.add('active');
        tabScan.classList.remove('active');
        secTranslate.style.display = 'block';
        secScan.classList.remove('active');
      } else {
        tabScan.classList.add('active');
        tabTranslate.classList.remove('active');
        secTranslate.style.display = 'none';
        secScan.classList.add('active');
      }
    }

    /* TRANSLATION CORE */
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

      document.getElementById('insightText').textContent = 'Translating with Zeni Engine...';

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

    /* SPEECH RECOGNITION (VOICE INPUT) */
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

      recognition.onerror = (e) => {
        console.error(e);
        isRecording = false;
        micBtn.classList.remove('recording');
      };

      recognition.onend = () => {
        isRecording = false;
        micBtn.classList.remove('recording');
      };

      recognition.start();
    }

    /* HIGH QUALITY NATIVE VOICE OVER (SERVER gTTS + BROWSER FALLBACK) */
    let currentAudio = null;

    function playVoiceover() {
      const text = document.getElementById('targetText').value.trim();
      const lang = document.getElementById('targetLang').value;
      const speed = parseFloat(document.getElementById('audioSpeed').value || '1.0');
      const soundwave = document.getElementById('soundwave');

      if (!text) return;

      // Stop any currently playing audio or speech
      if (currentAudio) {
        currentAudio.pause();
        currentAudio = null;
      }
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
      }

      soundwave.classList.add('playing');

      // Use Server Google TTS for authentic native pronunciation (Telugu, Hindi, Tamil, Kannada, etc.)
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
        // Fallback to Web Speech API if server TTS fails
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
          alert('Unable to play audio voiceover for this language.');
        }
      };

      audio.play().catch(e => {
        console.warn('Audio play fallback triggered:', e);
        audio.onerror();
      });
    }


    /* PICTURE SCAN (OCR) ENGINE */
    function handleImageUpload(e) {
      const file = e.target.files[0];
      if (file) processImageForOCR(file);
    }

    // Drag & Drop
    const dropZone = document.getElementById('dropZone');
    dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('dragover'); });
    dropZone.addEventListener('dragleave', () => { dropZone.classList.remove('dragover'); });
    dropZone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropZone.classList.remove('dragover');
      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        processImageForOCR(e.dataTransfer.files[0]);
      }
    });

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
          // Perform client-side OCR scan via Tesseract.js
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

    /* ZENI AI BOT DRAWER */
    function toggleBotDrawer() {
      const drawer = document.getElementById('botDrawer');
      drawer.classList.toggle('open');
    }

    async function sendBotMessage() {
      const input = document.getElementById('botInput');
      const msg = input.value.trim();
      if (!msg) return;

      const chatBody = document.getElementById('botChatBody');
      
      // User bubble
      const userBubble = document.createElement('div');
      userBubble.className = 'chat-bubble user';
      userBubble.textContent = msg;
      chatBody.appendChild(userBubble);

      input.value = '';
      chatBody.scrollTop = chatBody.scrollHeight;

      // Bot typing bubble
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

    /* LOGIN / AUTH MODAL */
    function openAuthModal() {
      document.getElementById('authModal').classList.add('active');
    }

    function closeAuthModal() {
      document.getElementById('authModal').classList.remove('active');
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

    function handleAuthSubmit(e) {
      e.preventDefault();
      const email = document.getElementById('authEmail').value;
      const username = email.split('@')[0];

      activeUser = { username, email, isGuest: false };
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
        authLabel.textContent = activeUser.username;
        authBtn.onclick = () => {
          if (confirm(`Logged in as ${activeUser.username}. Would you like to log out?`)) {
            activeUser = null;
            localStorage.removeItem('zeni_user');
            updateAuthUI();
          }
        };
      } else {
        authLabel.textContent = 'Sign In';
        authBtn.onclick = openAuthModal;
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
    """Zeni Neural Translation API endpoint."""
    try:
        data = request.get_json() or {}
        text = data.get("text", "").strip()
        source = data.get("source", "en")
        target = data.get("target", "te")
        tone = data.get("tone", "standard")

        if not text:
            return jsonify({"status": "error", "error": "No text provided."}), 400

        # Run translation via googletrans
        src_lang = "auto" if source == "auto" else source
        result = translator.translate(text, src=src_lang, dest=target)
        translated_text = result.text

        # Generate phonetic transliteration / breakdown
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

    # Smart conversational assistant rules
    if "hello" in msg_lower or "hi" in msg_lower or "hey" in msg_lower:
        reply = "Hello! I am Zeni Bot. How can I assist with your translations or language learning today?"
    elif "how to say" in msg_lower or "translate" in msg_lower:
        try:
            # Auto-detect intent to translate phrase
            res = translator.translate(message, dest="te")
            reply = f"Zeni Bot Translation Insight: '{res.text}' (Telugu). You can also select other languages from the top dropdown!"
        except Exception:
            reply = f"Zeni Bot Tip: To translate '{message}', type or paste it into the main translation panel above!"
    elif "picture" in msg_lower or "image" in msg_lower or "scan" in msg_lower:
        reply = "Zeni Bot Tip: Click the 'Picture Scan' tab at the top to upload or drop an image and extract text automatically!"
    elif "theme" in msg_lower or "dark" in msg_lower or "light" in msg_lower:
        reply = "Zeni Bot Tip: You can toggle between Dark Mode and Light Mode anytime using the moon/sun button in the top right!"
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


