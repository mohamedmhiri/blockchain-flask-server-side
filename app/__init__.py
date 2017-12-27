from flask import Flask
def _initialize_blueprints(application):
    '''
    Register Flask blueprints
    '''
    from app.views.blockchain import blockchain_view
    application.register_blueprint(blockchain_view, url_prefix='/api')
def create_app():
    '''
    Create an app by initializing components.
    '''
    application = Flask(__name__)
    _initialize_blueprints(application)
    # Do it!
    return application
