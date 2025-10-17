@echo off
echo 🚀 Сборка Construction Price Scout...
pip install -r requirements.txt
python build_app.py
echo.
echo ✅ Сборка завершена!
echo 📁 EXE файл: dist\ConstructionPriceScout.exe
pause