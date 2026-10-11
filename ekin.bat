@echo off
rem Ekin - Windows kısayolu. Bu klasörü PATH'e eklerseniz her yerden "ekin" yazabilirsiniz.
chcp 65001 >nul
python "%~dp0ekin.py" %*
