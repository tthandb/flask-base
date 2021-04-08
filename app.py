import json
import operator
import types
import uuid
import os
import copy
import time

from flask import Flask, request, g, Blueprint, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from marshmallow import ValidationError
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from common.errors import (
    UPermissionDenied, UNotFound, UUnprocessableEntity, UConflict, UBadRequest,
    OtherPaymentProcessing, OrderPaidError
)
from middlewares.logger import write_log
from ddtrace import tracer


db = types.SimpleNamespace()


def init_app(app_name=__name__):
    load_dotenv()
    environment = os.getenv('ENVIRONMENT', 'development'),

    # sentry_sdk.init(
    #     dsn=os.getenv('SENTRY_DSN', ''),
    #     environment=environment,
    #     integrations=[FlaskIntegration(), SqlalchemyIntegration()]
    # )

    from database.session import db_engine, db_flask_session

    # Config App
    app = Flask(app_name, instance_relative_config=True)
    app.url_map.strict_slashes = False
    CORS(app)

    # Config DB
    engine = db_engine()
    db_flask_session.configure(bind=engine)
    db.session_factory = db_flask_session

    __config_blueprints(app)
    _config_error_handlers(app)
    _configure_request_callback(app)
    _config_cli(app)

    return app


def __config_blueprints(app):
    def _config_blueprint(app):
        from apis import routes
        app.register_blueprint(routes, url_prefix='/api/v1')

    def _config_swagger(app):
        SWAGGER_UI_DIST_DIR = 'swagger/dist'

        swagger_page = Blueprint('simple_page', __name__)

        @swagger_page.route('/swagger/')
        def swagger_ui():
            return send_from_directory(SWAGGER_UI_DIST_DIR, 'index.html')

        @swagger_page.route('/<asset>')
        def swagger_assets(asset):
            return send_from_directory(SWAGGER_UI_DIST_DIR, asset)

        @swagger_page.route('/swagger-yaml/<yaml_file>')
        def swagger_checkout(yaml_file):
            return send_from_directory('swagger', yaml_file)

        app.register_blueprint(swagger_page)

    handle_exception = app.handle_exception
    handle_user_exception = app.handle_user_exception

    _config_blueprint(app)
    _config_swagger(app)

    app.handle_exception = handle_exception
    app.handle_user_exception = handle_user_exception


def _config_error_handlers(app):
    """
    Inspired by
    http://flask.pocoo.org/docs/latest/errorhandling/
    https://httpstatuses.com/
    """
    @app.errorhandler(ValidationError)
    def validation_error_handler(error):
        # TODO: Should change the error message format in future
        return json.dumps(
            {
                'error': 'Bad request',
                'messages': error.messages
            }
        ), 400

    @app.errorhandler(UBadRequest)
    def bad_request(error):
        error_message = str(error) or 'Bad request'
        return json.dumps({'error': error_message}), 400

    @app.errorhandler(500)
    def server_error_page(error):
        return json.dumps({'error': 'Internal server error'}), 500

    @app.errorhandler(UConflict)
    def conflict(error):
        return json.dumps({'error': str(error) or 'Conflict'}), 409

    @app.errorhandler(404)
    def page_not_found(error):
        return json.dumps({'error': 'Resource not found'}), 404

    @app.errorhandler(UPermissionDenied)
    def permission_denied(error):
        error_message = str(error) or 'Permission denied'
        return json.dumps({'error': error_message}), 401

    @app.errorhandler(UNotFound)
    def not_found(error):
        error_message = str(error) or 'Resource not found'
        return json.dumps({'error': error_message}), 404

    @app.errorhandler(UUnprocessableEntity)
    def unprocessable_entity(error):
        error_message = str(error) or 'Unprocessable Entity'
        return json.dumps({'error': error_message}), 422

    @app.errorhandler(OtherPaymentProcessing)
    def other_payment_processing(error):
        error_message = str(error) or 'Other Payment Is Processing'
        return json.dumps({'error': error_message}), 409

    @app.errorhandler(OrderPaidError)
    def order_paid_error(error):
        error_message = str(error) or 'Order was paid'
        return json.dumps({'error': error_message}), 469


def _config_cli(app):
    @app.cli.command()
    def initdb():
        print('init db - sample cli')

    @app.cli.command()
    def routes():
        """Display registered routes"""
        rules = []
        for rule in app.url_map.iter_rules():
            methods = ','.join(sorted(rule.methods))
            rules.append((rule.endpoint, methods, str(rule)))

        sort_by_rule = operator.itemgetter(2)
        for endpoint, methods, rule in sorted(rules, key=sort_by_rule):
            route = '{:50s} {:25s} {}'.format(endpoint, methods, rule)
            print(route)


def _configure_request_callback(app):
    @app.before_request
    def before_request_callback():
        request_id = request.headers.get('X-Request-ID')
        if not request_id:
            request_id = str(uuid.uuid4())
        g.request_id = request_id
        g.context = {} # define context
        g.start_time = time.time()
        try:
            action = request.url_rule.rule
        except Exception:
            action = ''
        g.extra_log = {
            'request_id': request_id,
            'tags': request_id,
            'environment': os.getenv('ENVIRONMENT', 'development'),
            'headers': request.headers,
            'request_type': 'API',
            'action': action
        }
        write_log(
            raw_message={'request_info': request.__dict__}, extra=g.extra_log
        )
        try:
            request_body = copy.deepcopy(
                request.get_json(force=True)) if request.is_json else None
        except Exception:
            request_body = None
        if request_body:
            request_body.pop('password', None)
            request_body.pop('credit_card_info', None)
        write_log(
            raw_message={
                'request_params': {
                    'form': request.form.to_dict(),
                    'args': request.args.to_dict(),
                    'body': request_body
                }
            },
            extra=g.extra_log
        )

    @app.after_request
    def after_request_callback(response):
        # TO DO: need format response data
        excute_time = time.time() - g.start_time
        write_log(
            raw_message={
                'response_info': {
                    'status_code': response.status_code,
                    'data': response.json,
                    'excute_time': excute_time
                }
            },
            extra=g.extra_log
        )
        return response
