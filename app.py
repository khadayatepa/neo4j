import streamlit as st
from neo4j import GraphDatabase
from pyvis.network import Network
import streamlit.components.v1 as components
import tempfile
import os

# Load credentials
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
        bgcolor="#ffffff", font_color="black", notebook=False
    )

    net.barnes_hut()  # Force-directed layout

    nodes = set()
    for record in results:
        for value in record.values():
            if isinstance(value, dict):
                continue
            if hasattr(value, 'nodes') and hasattr(value, 'relationships'):
                for node in value.nodes:
                    node_id = str(node.element_id)
                    label = list(node.labels)[0] if node.labels else "Node"
                    props = dict(node)
                    title = "<br>".join(f"{k}: {v}" for k, v in props.items())

                    if node_id not in nodes:
                        net.add_node(
                            node_id,
                            label=props.get("name", props.get("title", label)),
                            title=title,
                            color="#%06x" % (hash(label) & 0xFFFFFF)
                        )
                        nodes.add(node_id)

                for rel in value.relationships:
                    net.add_edge(
                        str(rel.start_node.element_id),
                        str(rel.end_node.element_id),
                        label=rel.type
                    )

    net.set_options("""
    var options = {
      layout: { improvedLayout: true },
      nodes: {
        shape: 'dot',
        size: 20,
        font: { size: 16, color: '#000000' },
        borderWidth: 2
      },
      edges: {
        width: 2,
        smooth: {
          type: "cubicBezier",
          forceDirection: "horizontal",
          roundness: 0.4
        }
      },
      physics: {
        forceAtlas2Based: {
          gravitationalConstant: -50,
          centralGravity: 0.005,
          springLength: 230,
          springConstant: 0.18
        },
        maxVelocity: 50,
        solver: 'forceAtlas2Based',
        timestep: 0.35,
        stabilization: { iterations: 150 }
      }
    }
    """)

    return net

# Streamlit UI
st.set_page_config(layout="wide")
st.title("🧠 Neo4j + Streamlit + Pyvis Graph Viewer")

query = st.text_area("Enter Cypher Query", "MATCH p=(a)-[r]->(b) RETURN p LIMIT 25")

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

        components.html(html, height=850, width=1200, scrolling=False)
        os.unlink(path)

    except Exception as e:
        st.error(f"Error: {e}")
