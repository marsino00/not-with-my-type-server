# 1. Base image
FROM python:3.12-slim

# 2. Set working dir
WORKDIR /app

# 3. Copy requirements
COPY requirements.txt .

# 4. Purge pip cache and install deps (no caching during install)
RUN pip cache purge \
 && pip install --no-cache-dir -r requirements.txt

# 5. Copy your app code
COPY . .

# 6. Run Procfile command (you can also just do CMD directly)
CMD ["bash", "-lc", "gunicorn app:app -b 0.0.0.0:$PORT"]