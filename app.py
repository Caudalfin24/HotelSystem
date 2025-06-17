from flask import Flask
from routes import auth_bp,dashboard_bp

app = Flask(__name__)
app.secret_key = '123'

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)

if __name__ == "__main__":
    app.run(debug=True)