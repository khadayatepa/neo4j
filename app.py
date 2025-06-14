import streamlit as st
from neo4j import GraphDatabase

# Load credentials
uri = st.secrets["neo4j"]["uri"]
username = st.secrets["neo4j"]["username"]
password = st.secrets["neo4j"]["password"]

# Neo4j driver
driver = GraphDatabase.driver(uri, auth=(username, password))

def run_query(query, parameters=None):
    with driver.session() as session:
        result = session.run(query, parameters or {})
        return [record.data() for record in result]

st.title("Neo4j + Streamlit Demo")

query = st.text_area("Cypher Query", "MATCH (n) RETURN n LIMIT 5")

if st.button("Run Query"):
    try:
        results = run_query(query)
        st.write("Results:")
        st.json(results)
    except Exception as e:
        st.error(f"Error: {e}")
