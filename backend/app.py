from flask import Flask, jsonify
from flask_cors import CORS

import config
from database import Base, init_engine


def create_app():
    app = Flask(__name__)
    app.config.from_object(config.Config)
    CORS(app)

    # Initialise le moteur et la session SQLAlchemy
    engine, _ = init_engine(app.config["SQLALCHEMY_DATABASE_URI"])

    # Importe les modèles puis crée les tables si absentes
    import models  # noqa: F401
    Base.metadata.create_all(engine)

    # Enregistre les blueprints
    from routes import ALL_BLUEPRINTS
    for bp in ALL_BLUEPRINTS:
        app.register_blueprint(bp)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "service": "CityReport API"})

    @app.teardown_appcontext
    def cleanup(exc=None):
        from database import SessionLocal
        if SessionLocal is not None:
            SessionLocal.remove()

    return app


app = create_app()


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
