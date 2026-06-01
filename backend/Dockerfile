FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

WORKDIR /backend

# Install git, git-lfs, and build-essential if any compilation is needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    git-lfs \
    curl \
    build-essential \
    libpq-dev \
    && git lfs install \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
