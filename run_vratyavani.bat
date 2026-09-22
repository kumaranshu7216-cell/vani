@echo off
title VratyaVani AI Platform Launcher
echo ===================================================
echo Starting VratyaVani AI Unified Engine...
echo ===================================================
call .venv\Scripts\activate
uvicorn gateway:app --reload --port 8000
pause