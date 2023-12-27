# main.py
from flask import Flask
from routes import register_routes
from neo4j_config import configure_neo4j

app = Flask(__name__)
register_routes(app)
configure_neo4j(app)

if __name__ == '__main__':
    app.run(port=443)
