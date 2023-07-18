FROM python:3.10.12
WORKDIR /app

COPY ./core/requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ADD ./core/src /app
COPY ./modules /opt/modules
CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
