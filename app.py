from flask import Flask, jsonify, g
from extensions import db
from routes import auth_bp
from middleware import jwt_required

app = Flask(__name__)
app.config.from_object("config.Config")

db.init_app(app)
app.register_blueprint(auth_bp, url_prefix="/auth")

# Import models after db initialization so metadata is registered
import models  # noqa: E402,F401

@app.route("/")
def home():
    return "Hello, Planventure!"


@app.route("/ciao")
def ciao():
    return "Ciao Paolo"


@app.route("/me")
@jwt_required
def me():
    return jsonify(
        {
            "id": g.current_user.id,
            "email": g.current_user.email,
        }
    )

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)