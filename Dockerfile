FROM python:3.8-alpine

WORKDIR /

# update gcc and stuff
RUN apk add build-base

COPY Pipfile* ./

RUN pip install --no-cache-dir pipenv && \
    pipenv install --system --deploy --clear

ADD rollbot /rollbot
COPY bot.py /
COPY .env /
CMD ["python3", "bot.py"]