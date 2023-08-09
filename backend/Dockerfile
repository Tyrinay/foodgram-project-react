FROM python:3.9-slim

WORKDIR /app

COPY requirements/requirements.txt .
#COPY entrypoint.sh /usr/bin/entrypoint.sh

RUN apt-get update && apt-get upgrade -y && \
    pip install --upgrade pip && pip install -r requirements.txt --no-cache-dir
#RUN chmod +x /usr/bin/entrypoint.sh

COPY . .

#ENTRYPOINT ["/usr/bin/entrypoint.sh"]
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]