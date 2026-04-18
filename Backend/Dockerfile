FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./requirements.txt

# requirements.txt is UTF-16 in this repository; convert to UTF-8 for pip.
RUN python -c "from pathlib import Path; Path('requirements-utf8.txt').write_text(Path('requirements.txt').read_text(encoding='utf-16'), encoding='utf-8')" \
    && pip install --no-cache-dir -r requirements-utf8.txt

COPY . .

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
