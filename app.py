def visualize_graph(results):
    net = Network(height="600px", width="100%", notebook=False, bgcolor="#000000", font_color="white")

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
                        net.add_node(node_id, label=label, title=title, shape="circle", color="#1f78b4")
                        nodes.add(node_id)
                for rel in value.relationships:
                    net.add_edge(str(rel.start_node.id), str(rel.end_node.id), label=rel.type, color="white")
    
    # Optional: improve physics layout for better appearance
    net.set_options("""
    var options = {
      "nodes": {
        "font": {
          "color": "white"
        },
        "borderWidth": 2
      },
      "edges": {
        "color": {
          "color": "white"
        }
      },
      "physics": {
        "barnesHut": {
          "gravitationalConstant": -30000,
          "centralGravity": 0.3,
          "springLength": 95
        },
        "minVelocity": 0.75
      }
    }
    """)

    return net
