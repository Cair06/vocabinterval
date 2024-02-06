FROM python:3.11

WORKDIR /app
COPY requirements.txt requirements.txt

RUN pip3 install --upgrade setuptools
RUN pip3 install -r requirements.txt


# Копируем необходимые файлы и папки
COPY core/scheduler/ ./core/scheduler/
COPY core/db/ ./core/db/
COPY core/settings.py ./core/
COPY core/__init__.py ./core/

# Устанавливаем PYTHONPATH
ENV PYTHONPATH=/app


CMD ["arq", "core.scheduler.main.WorkerSettings"]