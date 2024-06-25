FROM python:3.8.0
WORKDIR /utasaba-gamble-bot
COPY requirements.txt /utasaba-gamble-bot/
RUN pip install -r requirements.txt
COPY . /utasaba-gamble-bot
CMD python main.py