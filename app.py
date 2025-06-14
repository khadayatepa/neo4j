import streamlit as st
from neo4j import GraphDatabase
from pyvis.network import Network
import streamlit.components.v1 as components
import tempfile
import os

# Load Neo4j credentials
uri = st.secrets["neo4j"]["uri"]
username = st.secrets["neo4j"]["username"]
password = st.secrets["neo4j"]["password"]

# Connect to Neo4j
driver = GraphDatabase.driver(uri, auth=(username, password))

def run_query(query):
    with driver.session() as session:
        return list(session.run(query))

def visualize_graph(results):
    net = Network(height="600px", width="100%", notebook=False)

    nodes = set()
    for record in results:
        for value in record.values():
            if isinstance(value, dict):
                continue
            if hasattr(value, 'nodes') and hasattr(value, 'relationships'):
                for node in value.nodes:
                    node_id = str(node.id)
                    label = list(node.labels)[0] if node.labels else "Node"
                    props = dict(node)
                    title = "<br>".join(f"{k}: {v}" for k, v in props.items())
                    if node_id not in nodes:
                        net.add_node(node_id, label=label, title=title)
                        nodes.add(node_id)
                for rel in value.relationships:
                    net.add_edge(str(rel.start_node.id), str(rel.end_node.id), label=rel.type)
    
    return net

# UI
st.title("Neo4j + Streamlit + Pyvis")

query = st.text_area("Enter a Cypher Query", "MATCH p=(a)-[r]->(b) RETURN p LIMIT 10")

if st.button("Run Query"):
    try:
        results = run_query(query)
        st.success("Query executed successfully!")

        net = visualize_graph(results)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
            path = tmp_file.name
            net.save_graph(path)
            with open(path, 'r', encoding='utf-8') as f:
                html = f.read()

        components.html(html, height=650, scrolling=True)
        os.unlink(path)

    except Exception as e:
        st.error(f"Error: {e}")
