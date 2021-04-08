FROM python:3.7

ENV PYTHON_ROOT /usr/src/flask-backend
RUN mkdir -p $PYTHON_ROOT

WORKDIR $PYTHON_ROOT

COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock
RUN pip install pipenv
RUN pipenv install --system --deploy --dev

COPY . .

STOPSIGNAL SIGTERM

EXPOSE 5000

CMD [ "python", "run.py" ]
