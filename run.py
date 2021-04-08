from app import init_app, db
app = init_app()


@app.teardown_appcontext
def shutdown_session(response_or_exc):
    db.session_factory.remove()
    return response_or_exc


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
