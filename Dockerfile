FROM python:3.8

WORKDIR /cloudmetrics

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

ENV OPTION=''

CMD ["sh", "-c", "python main.py ${OPTION}"]