FROM python:3.7.3

ENV APP_PATH /usr/src/flask-backend
ENV WORKER core-interact
RUN mkdir -p $APP_PATH
RUN mkdir $APP_PATH/temp

WORKDIR $APP_PATH

ENV AWS_CONFIG_FILE $APP_PATH/configs/.aws/config
ENV AWS_SHARED_CREDENTIALS_FILE $APP_PATH/configs/.aws/credentials

COPY . .
RUN chmod +x start.sh
RUN chmod 400 configs/.ssh/id_rsa
RUN pip install pipenv
RUN pipenv install --system --deploy --dev


STOPSIGNAL SIGTERM
