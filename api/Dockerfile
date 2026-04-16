FROM python:3.11-slim

WORKDIR /app

# Requirements installing
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copying old code
COPY . .

# Ek choti si script  hain jo dono ko ek sath chalaye
RUN echo "#!/bin/sh\nuvicorn main:app --host 0.0.0.0 --port 8000 & \nstreamlit run app.py --server.port 7860 --server.address 0.0.0.0" > start.sh
RUN chmod +x start.sh

#  using HF Spaces port 7860 
EXPOSE 7860

CMD ["./start.sh"]