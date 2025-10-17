# build_app.py
import PyInstaller.__main__
import os
import shutil

def build_app():
    print("🚀 Сборка приложения...")
    
    # Очистка предыдущих сборок
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    # Параметры сборки
    params = [
        'run_scout.py',           # главный файл
        '--name=ConstructionPriceScout',  # название приложения
        '--onefile',              # один exe файл
        '--windowed',             # без консоли (или убрать для отладки)
        '--icon=app_icon.ico',    # иконка (если есть)
        '--add-data=config;config',  # добавляем папку config
        '--add-data=src;src',        # добавляем папку src
        '--clean',                # очистка кэша
    ]
    
    PyInstaller.__main__.run(params)
    
    print("✅ Сборка завершена!")
    print("📁 EXE файл находится в папке: dist/ConstructionPriceScout.exe")

if __name__ == "__main__":
    build_app()