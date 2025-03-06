FROM python:3.12

WORKDIR /ecommerce

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip

COPY requirements.txt /ecommerce/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /ecommerce/
RUN chmod 777 /ecommerce

EXPOSE 8000

CMD ["sh", "-c", "python sandbox/manage.py migrate && python sandbox/manage.py runserver 0.0.0.0:8000"]
