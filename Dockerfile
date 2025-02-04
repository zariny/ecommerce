FROM python:3.12

RUN mkdir /ecommerce
WORKDIR /ecommerce

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip

# Copy requirements.txt into the correct directory
COPY requirements.txt /ecommerce/

# Install dependencies from the correct location
RUN pip install --no-cache-dir -r /ecommerce/requirements.txt

# Copy the rest of the application
COPY . /ecommerce/

EXPOSE 8000

RUN python sandbox/manage.py migrate
CMD ["python", "sandbox/manage.py", "runserver", "0.0.0.0:8000"]
