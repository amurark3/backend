from flask import Flask
from flask_cors import CORS
from routes.use_case_1 import use_case_1_bp
from routes.use_case_2 import use_case_2_bp
from routes.use_case_3 import use_case_3_bp
from routes.use_case_4 import use_case_4_bp

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests for front-end integration

# Register routes
app.register_blueprint(use_case_1_bp, url_prefix="/api")
app.register_blueprint(use_case_2_bp, url_prefix="/api")
app.register_blueprint(use_case_3_bp, url_prefix="/api")
app.register_blueprint(use_case_4_bp, url_prefix="/api")
print(app.url_map)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
