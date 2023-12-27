# neo4j_config.py
from neo4j import GraphDatabase, basic_auth

def configure_neo4j(app):
    password="Give the password here"
    app.driver = GraphDatabase.driver(
        "bolt://3.238.138.75:7687",
        auth=basic_auth("neo4j", password), max_connection_lifetime=200)
