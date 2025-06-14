import streamlit as st
from neo4j import GraphDatabase
from pyvis.network import Network
import streamlit.components.v1 as components
import tempfile
import os

# Load credentials from Streamlit secrets
uri = st.secrets["neo4j"]["uri"]
username = st.secrets["neo4j"]["username"]
password = st.secrets["neo4j"]["password"]

# Connect to Neo4j
driver = GraphDatabase.driver(uri, auth=(username, password))

# Run Cypher query
def run_query(query):
    with driver.session() as session:
        return list(session.run(query))

# Build Pyvis graph from results
def visualize_graph(results):
    net = Network(
        height="800px", width="100%",
        bgcolor="#ffffff", font_color="black"
    )
    net.barnes_hut()
    nodes = set()

    for record in results:
        for value in record.values():
            if hasattr(value, 'nodes') and hasattr(value, 'relationships'
