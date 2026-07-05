from .signalements import bp as signalements_bp
from .agents import bp as agents_bp
from .citoyens import bp as citoyens_bp
from .stats import bp as stats_bp
from .ml_routes import bp as ml_bp
from .export import bp as export_bp
from .auth import bp as auth_bp
from .citoyen_espace import bp as citoyen_espace_bp
from .assistant import bp as assistant_bp

ALL_BLUEPRINTS = [
    auth_bp,
    signalements_bp,
    agents_bp,
    citoyens_bp,
    stats_bp,
    ml_bp,
    export_bp,
    citoyen_espace_bp,
    assistant_bp,
]
