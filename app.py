import streamlit as st
from neo4j import GraphDatabase
from pyvis.network import Network
import streamlit.components.v1 as components
import tempfile
import os

# Set a colorful and impressive background using Streamlit's markdown and CSS
def set_background():
    page_bg_img = """
    <style>
    body {
        background: linear-gradient(120deg, #ffecd2 0%, #fcb69f 100%);
    }
    .stApp {
        background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
        min-height: 100vh;
        padding-bottom: 2rem;
    }
    .stTextInput>div>div>input, .stTextArea textarea {
        background-color: #fff7f0;
        border: 1.5px solid #ffb385;
        color: #222;
    }
    .stButton>button {
        background: linear-gradient(90deg, #fcb69f 0%, #ffecd2 100%);
        color: #333;
        border-radius: 10px;
        border: none;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #f6d365 0%, #fda085 100%);
        color: #fff;
    }
    .stAlert {
        background: #ffecd2;
        border-left: 5px solid #fcb69f;
    }
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)

set_background()

# App Title with style
st.markdown(
    "<h1 style='text-align: center; color: #f76d6d; font-size: 3rem; font-weight: bold; "
    "text-shadow: 2px 2px 8px #fff8, 0 0 30px #fcb69f;'>Neo4j + Streamlit + Pyvis</h1>",
    unsafe_allow_html=True,
)

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
    net = Network(height="600px", width="100%", notebook=False, bgcolor='#fff7f0', font_color='#333')

    color_palette = [
        "#fcb69f", "#f6d365", "#fda085", "#a1c4fd", "#c2e9fb", "#96e6a1", "#fdc1c5",
        "#ff9a9e", "#fad0c4", "#a18cd1", "#fbc2eb"
    ]
    node_colors = {}
    nodes = set()
    color_idx = 0

    for record in results:
        for value in record.values():
            if isinstance(value, dict):
                continue
            if hasattr(value, 'nodes') and hasattr(value, 'relationships'):
                for node in value.nodes:
                    node_id = str(node.id)
                    label = list(node.labels)[0] if node.labels else "Node"
                    props = dict(node)
                    title = "<br>".join(f"<b>{k}:</b> {v}" for k, v in props.items())
                    if node_id not in nodes:
                        # Assign a color per label
                        if label not in node_colors:
                            node_colors[label] = color_palette[color_idx % len(color_palette)]
                            color_idx += 1
                        net.add_node(
                            node_id,
                            label=label,
                            title=title,
                            color=node_colors[label],
                            shape="dot",
                            size=25
                        )
                        nodes.add(node_id)
                for rel in value.relationships:
                    net.add_edge(
                        str(rel.start_node.id),
                        str(rel.end_node.id),
                        label=rel.type,
                        color="#f76d6d",
                        width=3,
                        font={"color": "#8e44ad", "size": 14, "strokeWidth": 0}
                    )

    # Add options for a modern UI look
    net.set_options("""
    var options = {
      "nodes": {
        "borderWidth": 2,
        "shadow": true,
        "font": {
          "size": 18,
          "face": "Tahoma"
        }
      },
      "edges": {
        "color": {
          "inherit": false
        },
        "smooth": {
          "type": "dynamic"
        },
        "shadow": true
      },
      "physics": {
        "enabled": true,
        "stabilization": {
          "iterations": 200
        },
        "barnesHut": {
          "gravitationalConstant": -5000,
          "springLength": 150,
          "springConstant": 0.08
        }
      },
      "interaction": {
        "hover": true,
        "multiselect": true,
        "dragView": true
      }
    }
    """)

    return net

# Query Input UI
st.markdown(
    "<div style='margin-top: 30px; margin-bottom: 10px; font-size: 1.2rem; color: #333;'>"
    "<b>Enter a Cypher Query:</b></div>",
    unsafe_allow_html=True,
)
query = st.text_area(
    "",
    "MATCH p=(a)-[r]->(b) RETURN p LIMIT 10",
    height=100,
    key="cypher_query",
)

if st.button("✨ Run Query", use_container_width=True):
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
