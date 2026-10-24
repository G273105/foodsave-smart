@echo off
cd /d "%~dp0"
echo Open http://127.0.0.1:3000/index.html in your browser.
echo Keep this window open. Press Ctrl+C to stop.
py -m http.server 3000 --bind 127.0.0.1
if errorlevel 1 pause
