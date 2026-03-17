@echo off
set PROJECT_NAME=ProcessadorXML

echo ==========================================
echo   %PROJECT_NAME% - INICIANDO BUILD  
echo ==========================================

REM Limpeza de builds anteriores
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

echo [1/4] Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo [2/4] Atualizando ferramentas e dependencias...
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

echo [3/4] Gerando executavel...
pyinstaller --clean ProcessadorXML.spec

echo [4/4] Finalizado! Verifique a pasta dist.
explorer dist\%PROJECT_NAME%
pause