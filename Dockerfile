FROM python:3.12

RUN mkdir /ecommerce
WORKDIR /ecommerce

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip

COPY requirements.txt /ecommerce/
RUN pip install --no-cache-dir -r /ecommerce/requirements.txt

COPY . /ecommerce/
COPY ../entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV DJANGO_SUPERUSER_EMAIL=root@email.com
ENV DJANGO_SUPERUSER_PASSWORD=root

EXPOSE 8000
RUN sh /entrypoint.sh
CMD ["python", "sandbox/manage.py", "runserver", "0.0.0.0:8000"]
