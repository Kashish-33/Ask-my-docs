FROM python:3.11-slim

WORKDIR /app

# System dependencies for ChromaDB
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Environment variable to fix SQLite version issues in some environments
ENV IS_DOCKER=1

# Script to run both Backend and Frontend with CORS/XSRF disabled for Hugging Face
RUN echo "#!/bin/sh\npython3 -m uvicorn main:app --host 0.0.0.0 --port 8000 & \npython3 -m streamlit run app.py --server.port 7860 --server.address 0.0.0.0 --server.enableCORS false --server.enableXsrfProtection false" > start.sh
RUN chmod +x start.sh

EXPOSE 7860

CMD ["./start.sh"]