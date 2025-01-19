FROM python:latest

RUN mkdir ./project

COPY . ./project

COPY requirements.txt ./project

WORKDIR ./project

RUN pip install -r requirements.txt

CMD ["python3", "./SMT/main.py"]