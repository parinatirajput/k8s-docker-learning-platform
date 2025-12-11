FROM python:3.9-slim

ENV PIP_NO_PROGRESS_BAR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

# Disable pip progress bar to avoid thread creation issues
RUN pip3 install --upgrade pip --progress-bar off

RUN pip3 install -r requirements.txt --no-cache-dir --progress-bar off

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]

