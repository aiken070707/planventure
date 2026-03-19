from flask import Flask
from extensions import db

app = Flask(__name__)
app.config.from_object("config.Config")

db.init_app(app)

# Import models after db initialization so metadata is registered
import models  # noqa: E402,F401


@app.route("/")
def home():
    return "Hello, Planventure!"


@app.route("/ciao")
def ciao():
    return "Ciao Paolo"


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)