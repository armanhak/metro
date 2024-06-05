FROM python:3.10.3-slim as builder

RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
		postgresql-client \
	&& rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt .

RUN pip install --upgrade pip
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt

FROM python:3.10.3-slim
RUN mkdir -p /home/app
# create the app user
# RUN addgroup -S app && adduser -S app -G app

# create the appropriate directories
ENV HOME=/home/app
ENV APP_HOME=/home/app/metro_assist
RUN mkdir $APP_HOME
# RUN mkdir $APP_HOME/certbot
# RUN mkdir $APP_HOME/certbot/conf
# RUN mkdir $APP_HOME/certbot/www
# RUN mkdir $APP_HOME/certbot/live/
# RUN mkdir $APP_HOME/certbot/live/subscription.inform-ocenka-calc.online/

WORKDIR $APP_HOME

COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --no-cache /wheels/*

COPY . $APP_HOME