from payments_api import app
from payments_api.views import general, payments

def register_blueprints(app):
    """
    Adds all blueprint objects into the app.
    """
    app.register_blueprint(general.general)
    app.register_blueprint(payments.payment)

    # All done!
    app.logger.info("Blueprints registered")
