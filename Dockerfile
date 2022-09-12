FROM python:3.10-slim@sha256:c0a3f67a6c43f11313e853e7937d87ebf0353c967eb7deccfc5f7d39a1d644b3

WORKDIR /

# update gcc and stuff
RUN apt-get update \
 && apt-get  install -y build-essential

COPY Pipfile* ./

RUN pip install --no-cache-dir pipenv && \
    pipenv install --system --deploy --clear

ADD rollbot /rollbot
COPY bot.py /
COPY .env /
CMD ["python3", "bot.py"]
