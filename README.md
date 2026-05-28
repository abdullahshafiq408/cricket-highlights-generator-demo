# Autonomous Cricket Highlights Pipeline

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-link-here.streamlit.app/)

**Live Demo:** [View the Streamlit Dashboard](https://your-app-link-here.streamlit.app/) *(Replace with your actual URL)*

This repository contains the Streamlit frontend for an automated video processing pipeline. Built as a technical proof-of-concept, the application visualizes the backend telemetry used to extract cricket highlights without manual editing.

## System Architecture

This pipeline maps discrete match events to continuous video feeds. It automates the video editing process by combining NLP, computer vision, and audio analysis.

**1. Data Ingestion & NLP**
* Parses raw ball-by-ball JSON data from Cricsheet.
* Uses OpenAI Whisper to transcribe broadcast audio, filtering for commentary markers and establishing a narrative baseline.

**2. Vision Engine**
* Extracts video frames at 1.0 FPS using OpenCV.
* An EasyOCR pipeline reads the broadcast scoreboard graphics (Innings, Over, Ball) to map video time to match time.
* **Trailing Edge Interpolation:** Broadcast graphics usually lag behind live action. We handle this by anchoring the start of a clip to the exact moment the previous ball's graphic disappears, which consistently aligns with the bowler's run-up.

**3. Audio & Fusion**
* Librosa calculates Root Mean Square (RMS) audio energy to measure crowd volume.
* A scoring algorithm combines the Cricsheet event priority, OCR timestamps, and Audio RMS into a final confidence score to generate the highlight reel.

## Tech Stack
* **Frontend:** Streamlit, Plotly, Pandas
* **Vision & NLP:** OpenCV, EasyOCR, OpenAI Whisper
* **Audio:** Librosa
* **Video Hosting:** Dropbox (Headless direct streaming to bypass GitHub file limits)

## Repository Structure

To accommodate GitHub's 100MB file limit, heavy MP4 files are hosted externally. The repository stores the application logic and lightweight JSON telemetry.

```text
/autonomous-highlights-pipeline
├── app.py                     
├── requirements.txt           
├── .streamlit/
│   └── config.toml            
└── assets/
    └── eng_nz_2023/           
        ├── match_data.json
        ├── ocr_telemetry.json
        └── audio_telemetry.json