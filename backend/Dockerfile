FROM python:3.11-slim

# Cài đặt ffmpeg cho hệ điều hành
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirement file
COPY requirements.txt .

# Cài đặt thư viện Python
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code backend
COPY . .

# Expose port (tùy chọn)
EXPOSE 8000

# Chạy FastAPI (có thể thay đổi uvicorn command)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
