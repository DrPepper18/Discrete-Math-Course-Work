# Кубик Рубика — бэкенд (FastAPI) + раздача фронтенда (index.html, app.js)
FROM python:3.13-slim

WORKDIR /app

# зависимости отдельным слоем — кэшируются, пока requirements не менялся
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# код: backend/ + корневые index.html, app.js (их раздаёт app.py из ../)
COPY . .

WORKDIR /app/backend
EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
