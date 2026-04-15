# 1. Base image (Python setup)
FROM python:3.11-slim

# 2. working folder inside the container
WORKDIR /app

# 3. installing requirements copy
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. copying all the code
COPY . .

# 5. starting fastAPi (0.0.0.0 is VERY important for Render)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]