# --- Build frontend ---
FROM node:20 AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# --- Build backend ---
FROM python:3.10-slim AS backend
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY app/ ./app/
COPY uploaded_docs/ ./uploaded_docs/

# Copy built frontend static files
COPY --from=frontend-build /app/frontend/dist ./static

# (Optional) If using FastAPI to serve static files:
RUN pip install fastapi[all] uvicorn

EXPOSE 7860

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]