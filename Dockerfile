FROM python:3.8-slim@sha256:cef447cdd9fd212790b0571779a52bd1230636b60a7fda1f838ff9a2159a8593

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
