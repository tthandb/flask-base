FROM python:3.7.3
COPY --from=lachlanevenson/k8s-kubectl:v1.18.9 /usr/local/bin/kubectl /usr/local/bin/kubectl
ENV APP_PATH /usr/src/flask-backend
ENV WORKER core-interact
RUN mkdir -p $APP_PATH
RUN mkdir $APP_PATH/temp

WORKDIR $APP_PATH

ENV AWS_CONFIG_FILE $APP_PATH/.aws/config
ENV AWS_SHARED_CREDENTIALS_FILE $APP_PATH/.aws/credentials

COPY . .
RUN chmod +x start.sh
RUN pip install pipenv
RUN pipenv install --system --deploy --dev


STOPSIGNAL SIGTERM
