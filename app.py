def visualize_graph(results):
    net = Network(
        height="800px",
        width="100%",
        bgcolor="#111111",  # Dark background
        font_color="white"
    )
    net.barnes_hut()

    nodes = set()
    label_colors = {}

    def get_color(label):
        if label not in label_colors:
            # Assign vibrant random color
            label_colors[label] = "#%06x" % random.randint(0x444444, 0xFFFFFF)
        return label_colors[label]

    for record in results:
        for value in record.values():
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
                            color=get_color(label)
                        )
                        nodes.add(node_id)

                for rel in value.relationships:
                    net.add_edge(
                        str(rel.start_node.element_id),
                        str(rel.end_node.element_id),
                        label=rel.type,
                        color={"color": "#%06x" % random.randint(0x666666, 0xFFFFFF)}
                    )

    # Force background using vis.js options
    net.set_options("""
    var options = {
      layout: { improvedLayout: true },
      nodes: {
        shape: 'dot',
        size: 20,
        font: { size: 16, color: '#ffffff' },
        borderWidth: 2
      },
      edges: {
        color: { color: '#999999' },
        width: 2,
        smooth: {
          type: "dynamic",
          forceDirection: "none",
          roundness: 0.3
        }
      },
      physics: {
        forceAtlas2Based: {
          gravitationalConstant: -80,
          centralGravity: 0.005,
          springLength: 200,
          springConstant: 0.18
        },
        maxVelocity: 75,
        solver: 'forceAtlas2Based',
        timestep: 0.4,
        stabilization: { iterations: 200 }
      }
    }
    """)

    return net
