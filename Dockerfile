FROM python:3.13-alpine

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV ENV=dev

COPY requirements.txt /app/
RUN pip install --no-cache-dir wheel
RUN pip install --no-cache-dir --no-binary python-logstash -r requirements.txt

RUN pip install watchdog

COPY ./app /app/app/
COPY manage.py /app/

COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

RUN mkdir -p /app/data/logs

EXPOSE 8000

RUN pip install python-logstash

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["sh", "-c", "\
    if [ \"$ENV\" = 'dev' ]; then \
        python manage.py runserver 0.0.0.0:8000; \
    else \
        gunicorn --bind 0.0.0.0:8000 my_driving_school.wsgi:application; \
    fi \
"]
