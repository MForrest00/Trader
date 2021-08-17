FROM python:3.7.9-slim

WORKDIR /app

RUN apt-get update
RUN apt-get install -y \
  gcc \
  build-essential

RUN apt-get clean

RUN pip install pipenv==2020.6.2

COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy --ignore-pipfile

COPY . .

CMD ["rq" "worker" "-c" "trader.utilities.worker_config" "--with-scheduler"]
