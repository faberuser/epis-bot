FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && groupadd --gid 10001 bot \
    && useradd --uid 10001 --gid bot --no-create-home bot \
    && mkdir /app/data \
    && chown bot:bot /app/data

COPY main.py settings.py ./
COPY cogs/ ./cogs/
COPY kingsraid-data/assets/ ./kingsraid-data/assets/
COPY kingsraid-data/table-data/ ./kingsraid-data/table-data/
COPY kingsraid-data/LICENSE ./kingsraid-data/LICENSE

RUN test -d kingsraid-data/table-data/legacy

USER bot:bot

CMD ["python", "main.py"]
