import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.models.social_media import SocialMediaAccount, SocialMediaPost, AIImageGeneration, PostingSchedule
from src.routes.user import user_bp
from src.routes.social_media import social_media_bp
from src.routes.seo_routes import seo_bp
from src.routes.brand_voice_routes import brand_voice_bp
from src.routes.alternative_brand_voice_routes import alternative_brand_voice_bp
from src.routes.manual_content_routes import manual_content_bp
from src.routes.ab_testing_routes import ab_testing_bp
from src.routes.learning_algorithm_routes import learning_algorithm_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Enable CORS for all routes
CORS(app, origins="*")

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(social_media_bp, url_prefix='/api')
app.register_blueprint(seo_bp, url_prefix='/api/seo')
app.register_blueprint(brand_voice_bp, url_prefix='/api/brand-voice')
app.register_blueprint(alternative_brand_voice_bp, url_prefix='/api/alternative-brand-voice')
app.register_blueprint(manual_content_bp, url_prefix='/api/manual-content')
app.register_blueprint(ab_testing_bp, url_prefix='/api/ab-testing')
app.register_blueprint(learning_algorithm_bp, url_prefix='/api/learning')

# uncomment if you need to use database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///" + os.path.join(os.path.dirname(__file__), "database", "app.db"))
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["DEBUG"] = False
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
