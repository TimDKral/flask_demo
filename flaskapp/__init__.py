import os
from flask import Flask

# Swagger
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask_apispec.extension import FlaskApiSpec
from flask_restful import Resource, Api


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flask_DB.sqlite'),
    )
    
    app.config.update({
        'APISPEC_SPEC': APISpec(
            title='Flask Demo project',
            version='v1',
            plugins=[MarshmallowPlugin()],
            openapi_version='2.0.0'
        ),
        'APISPEC_SWAGGER_URL': '/swagger/',  # URI to access API Doc JSON 
        'APISPEC_SWAGGER_UI_URL': '/swagger-ui/'  # URI to access UI of API Doc
    })
    
    api = Api(app)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    from . import db
    db.init_app(app)
    
    from . import items
    app.register_blueprint(items.bp)
    app.add_url_rule('/', endpoint='index')
    
    docs = FlaskApiSpec(app)
    #docs.register(items)
    #api.add_resource(items.bp, '/items')

    return app
