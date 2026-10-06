@echo off

echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo SmartFarm AI setup complete.
echo.
echo To start the application, run:
echo uvicorn app.api:app --reload
echo.
echo Then open:
echo http://127.0.0.1:8000/
echo.
pause