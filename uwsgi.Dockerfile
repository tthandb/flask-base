FROM python:3.7.3

# Environment variables
ENV APP_PATH /usr/src/flask-backend
RUN mkdir -p $APP_PATH
RUN mkdir $APP_PATH/temp
WORKDIR $APP_PATH

ENV AWS_CONFIG_FILE $APP_PATH/configs/.aws/config
ENV AWS_SHARED_CREDENTIALS_FILE $APP_PATH/configs/.aws/credentials

# Setup nginx
RUN apt-get update && apt-get install -y nginx
COPY configs/nginx/sites-available /etc/nginx/sites-enabled
COPY configs/nginx/ssl /etc/nginx/ssl
COPY configs/nginx/nginx.conf /etc/nginx/nginx.conf
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
&& ln -sf /dev/stderr /var/log/nginx/error.log
RUN rm /etc/nginx/sites-enabled/default

# Setup uwsgi
RUN pip install uwsgi
COPY configs/uwsgi.ini /etc/uwsgi/

# Install Supervisord
RUN apt-get update && apt-get install -y supervisor \
&& rm -rf /var/lib/apt/lists/*
COPY configs/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Setup application
COPY . .
RUN chmod +x start.sh
RUN chmod 400 configs/.ssh/id_rsa
RUN pip install pipenv
RUN pipenv install --system --deploy

EXPOSE 80
EXPOSE 443

CMD [ "./start.sh", "api" ]
