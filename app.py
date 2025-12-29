import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import json

# Page configuration
st.set_page_config(
    page_title="Food Delivery Graph Database",
    page_icon="🍕",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #ff7f0e;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .node-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
    }
    .query-box {
        background-color: #1e1e1e;
        color: #00ff00;
        padding: 1rem;
        border-radius: 0.5rem;
        font-family: 'Courier New', monospace;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">🍕 Food Delivery System - Graph Database Demo</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #666;">Using LanceGraph / Nebula Graph</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/150/1f77b4/FFFFFF?text=Graph+DB", use_container_width=True)
    st.markdown("## 📊 Navigation")
    page = st.radio(
        "Select Section:",
        ["📖 Overview", "🔷 Nodes", "🔗 Edges", "🔍 Queries", "📈 Visualization", "💾 Implementation"]
    )
    
    st.markdown("---")
    st.markdown("### 🎯 Quick Stats")
    st.metric("Node Types", "5")
    st.metric("Edge Types", "6")
    st.metric("Sample Queries", "6")

# Data Model
graph_model = {
    'nodes': [
        {
            'type': 'Customer',
            'properties': ['customer_id', 'name', 'phone', 'address', 'join_date'],
            'color': '#60a5fa',
            'icon': '👤'
        },
        {
            'type': 'Restaurant',
            'properties': ['restaurant_id', 'name', 'cuisine_type', 'rating', 'location'],
            'color': '#f472b6',
            'icon': '🏪'
        },
        {
            'type': 'Dish',
            'properties': ['dish_id', 'name', 'price', 'category', 'is_vegetarian'],
            'color': '#fbbf24',
            'icon': '🍽️'
        },
        {
            'type': 'DeliveryPerson',
            'properties': ['person_id', 'name', 'phone', 'vehicle_type', 'rating'],
            'color': '#34d399',
            'icon': '🏍️'
        },
        {
            'type': 'Order',
            'properties': ['order_id', 'order_date', 'total_amount', 'status', 'delivery_time'],
            'color': '#a78bfa',
            'icon': '📦'
        }
    ],
    'edges': [
        {'from': 'Customer', 'to': 'Order', 'relationship': 'PLACES', 'properties': ['timestamp']},
        {'from': 'Order', 'to': 'Restaurant', 'relationship': 'FROM', 'properties': ['order_date']},
        {'from': 'Order', 'to': 'Dish', 'relationship': 'CONTAINS', 'properties': ['quantity', 'price']},
        {'from': 'DeliveryPerson', 'to': 'Order', 'relationship': 'DELIVERS', 'properties': ['pickup_time', 'delivery_time']},
        {'from': 'Restaurant', 'to': 'Dish', 'relationship': 'SERVES', 'properties': ['availability']},
        {'from': 'Customer', 'to': 'Restaurant', 'relationship': 'REVIEWS', 'properties': ['rating', 'comment', 'date']}
    ]
}

# Sample Queries
queries = [
    {
        'title': 'Find all orders by a customer',
        'description': 'Retrieve all orders placed by customer "Alice"',
        'query': """MATCH (c:Customer {name: 'Alice'})-[:PLACES]->(o:Order)
RETURN c.name, o.order_id, o.total_amount, o.status""",
        'result': pd.DataFrame({
            'customer': ['Alice', 'Alice'],
            'order_id': ['ORD001', 'ORD005'],
            'amount': [450, 320],
            'status': ['delivered', 'in_transit']
        })
    },
    {
        'title': 'Find dishes from a restaurant',
        'description': 'Get all dishes served by "Spice Garden"',
        'query': """MATCH (r:Restaurant {name: 'Spice Garden'})-[:SERVES]->(d:Dish)
RETURN r.name, d.name, d.price, d.category""",
        'result': pd.DataFrame({
            'restaurant': ['Spice Garden', 'Spice Garden'],
            'dish': ['Butter Chicken', 'Paneer Tikka'],
            'price': [280, 220],
            'category': ['Main Course', 'Appetizer']
        })
    },
    {
        'title': 'Track order delivery chain',
        'description': 'Complete delivery chain for an order',
        'query': """MATCH (c:Customer)-[:PLACES]->(o:Order)-[:FROM]->(r:Restaurant),
      (o)-[:CONTAINS]->(d:Dish),
      (dp:DeliveryPerson)-[:DELIVERS]->(o)
WHERE o.order_id = 'ORD001'
RETURN c.name, r.name, d.name, dp.name, o.status""",
        'result': pd.DataFrame({
            'customer': ['Alice'],
            'restaurant': ['Spice Garden'],
            'dish': ['Butter Chicken'],
            'delivery_person': ['Raj'],
            'status': ['delivered']
        })
    },
    {
        'title': 'Find highly rated restaurants',
        'description': 'Restaurants with average rating > 4.5',
        'query': """MATCH (c:Customer)-[r:REVIEWS]->(rest:Restaurant)
WHERE r.rating >= 4.5
RETURN rest.name, rest.cuisine_type, AVG(r.rating) as avg_rating
ORDER BY avg_rating DESC""",
        'result': pd.DataFrame({
            'restaurant': ['Spice Garden', 'Pizza Paradise'],
            'cuisine': ['Indian', 'Italian'],
            'avg_rating': [4.7, 4.6]
        })
    },
    {
        'title': 'Delivery person performance',
        'description': 'Find all orders delivered by a specific person',
        'query': """MATCH (dp:DeliveryPerson {name: 'Raj'})-[del:DELIVERS]->(o:Order)
RETURN dp.name, COUNT(o) as total_deliveries, 
       AVG(del.delivery_time) as avg_delivery_time""",
        'result': pd.DataFrame({
            'delivery_person': ['Raj'],
            'total_deliveries': [15],
            'avg_delivery_time': ['28 mins']
        })
    },
    {
        'title': 'Customer preferences',
        'description': 'Find most ordered dish categories by customer',
        'query': """MATCH (c:Customer {name: 'Alice'})-[:PLACES]->(o:Order)-[:CONTAINS]->(d:Dish)
RETURN d.category, COUNT(d) as order_count
ORDER BY order_count DESC""",
        'result': pd.DataFrame({
            'category': ['Main Course', 'Dessert', 'Appetizer'],
            'count': [8, 5, 3]
        })
    }
]

# Overview Page
if page == "📖 Overview":
    st.markdown('<h2 class="sub-header">📖 Graph Data Model Overview</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        ### 🎯 Model Description
        
        This food delivery system models the complete ecosystem including:
        - **Customers** placing orders
        - **Restaurants** serving dishes
        - **Dishes** being ordered
        - **Delivery Personnel** delivering orders
        - **Orders** connecting all entities
        
        The graph structure allows efficient traversal of relationships and complex queries.
        """)
    
    with col2:
        st.success("""
        ### ✨ Key Features
        
        - **Real-time order tracking**
        - **Customer preference analysis**
        - **Restaurant performance metrics**
        - **Delivery optimization**
        - **Recommendation systems**
        - **Network effect analysis**
        """)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🔷 Node Types", "5", help="Customer, Restaurant, Dish, DeliveryPerson, Order")
    with col2:
        st.metric("🔗 Edge Types", "6", help="PLACES, FROM, CONTAINS, DELIVERS, SERVES, REVIEWS")
    with col3:
        st.metric("🔍 Query Examples", "6", help="Common graph traversal patterns")

# Nodes Page
elif page == "🔷 Nodes":
    st.markdown('<h2 class="sub-header">🔷 Node Types (Vertices)</h2>', unsafe_allow_html=True)
    
    for node in graph_model['nodes']:
        with st.container():
            col1, col2 = st.columns([1, 4])
            with col1:
                st.markdown(f"<h1 style='text-align: center; font-size: 4rem;'>{node['icon']}</h1>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"### {node['type']}")
                st.markdown(f"**Properties:**")
                props_text = ", ".join([f"`{prop}`" for prop in node['properties']])
                st.markdown(props_text)
            st.markdown("---")

# Edges Page
elif page == "🔗 Edges":
    st.markdown('<h2 class="sub-header">🔗 Edge Types (Relationships)</h2>', unsafe_allow_html=True)
    
    for idx, edge in enumerate(graph_model['edges']):
        with st.expander(f"**{edge['relationship']}**: {edge['from']} → {edge['to']}", expanded=True):
            col1, col2, col3 = st.columns([2, 1, 2])
            with col1:
                st.markdown(f"**From:** `{edge['from']}`")
            with col2:
                st.markdown(f"<p style='text-align: center; font-size: 1.5rem;'>➡️</p>", unsafe_allow_html=True)
            with col3:
                st.markdown(f"**To:** `{edge['to']}`")
            
            if edge['properties']:
                st.markdown(f"**Properties:** {', '.join([f'`{prop}`' for prop in edge['properties']])}")

# Queries Page
elif page == "🔍 Queries":
    st.markdown('<h2 class="sub-header">🔍 Graph Queries</h2>', unsafe_allow_html=True)
    
    query_option = st.selectbox(
        "Select a query to view:",
        [f"{i+1}. {q['title']}" for i, q in enumerate(queries)]
    )
    
    query_idx = int(query_option.split('.')[0]) - 1
    selected_query = queries[query_idx]
    
    st.markdown(f"### {selected_query['title']}")
    st.markdown(f"*{selected_query['description']}*")
    
    st.markdown("#### 💻 LanceGraph Query:")
    st.code(selected_query['query'], language='cypher')
    
    st.markdown("#### 📊 Sample Result:")
    st.dataframe(selected_query['result'], use_container_width=True)
    
    # Download button
    csv = selected_query['result'].to_csv(index=False)
    st.download_button(
        label="📥 Download Result as CSV",
        data=csv,
        file_name=f"query_{query_idx+1}_result.csv",
        mime="text/csv"
    )

# Visualization Page
elif page == "📈 Visualization":
    st.markdown('<h2 class="sub-header">📈 Graph Visualization</h2>', unsafe_allow_html=True)
    
    # Create NetworkX graph
    G = nx.DiGraph()
    
    # Add nodes
    node_colors = {}
    for node in graph_model['nodes']:
        G.add_node(node['type'])
        node_colors[node['type']] = node['color']
    
    # Add edges
    edge_labels = {}
    for edge in graph_model['edges']:
        G.add_edge(edge['from'], edge['to'])
        edge_labels[(edge['from'], edge['to'])] = edge['relationship']
    
    # Create visualization
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Layout
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    
    # Draw nodes
    for node in G.nodes():
        nx.draw_networkx_nodes(
            G, pos,
            nodelist=[node],
            node_color=node_colors[node],
            node_size=3000,
            alpha=0.9,
            ax=ax
        )
    
    # Draw edges
    nx.draw_networkx_edges(
        G, pos,
        edge_color='#666666',
        width=2,
        alpha=0.6,
        arrows=True,
        arrowsize=20,
        arrowstyle='->',
        connectionstyle='arc3,rad=0.1',
        ax=ax
    )
    
    # Draw labels
    nx.draw_networkx_labels(
        G, pos,
        font_size=10,
        font_weight='bold',
        font_color='white',
        ax=ax
    )
    
    # Draw edge labels
    nx.draw_networkx_edge_labels(
        G, pos,
        edge_labels,
        font_size=8,
        font_color='#333333',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7),
        ax=ax
    )
    
    ax.set_title("Food Delivery System - Graph Structure", fontsize=16, fontweight='bold')
    ax.axis('off')
    plt.tight_layout()
    
    st.pyplot(fig)
    
    # Legend
    st.markdown("### 🎨 Legend")
    cols = st.columns(5)
    for idx, node in enumerate(graph_model['nodes']):
        with cols[idx]:
            st.markdown(f"<div style='background-color: {node['color']}; padding: 10px; border-radius: 5px; text-align: center; color: white; font-weight: bold;'>{node['icon']} {node['type']}</div>", unsafe_allow_html=True)

# Implementation Page
elif page == "💾 Implementation":
    st.markdown('<h2 class="sub-header">💾 Implementation Details</h2>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🔧 Setup", "📝 Code Examples", "🚀 Deployment"])
    
    with tab1:
        st.markdown("""
        ### 🔧 Database Setup
        
        #### LanceGraph Installation:
        ```bash
        pip install lancegraph
        ```
        
        #### Nebula Graph Installation:
        ```bash
        # Install Nebula Graph
        docker pull vesoft/nebula-graphd:latest
        docker pull vesoft/nebula-storaged:latest
        docker pull vesoft/nebula-metad:latest
        ```
        
        ### 📊 Schema Creation
        """)
        
        st.code("""
# Create Node Types
CREATE TAG Customer (customer_id string, name string, phone string, address string, join_date date)
CREATE TAG Restaurant (restaurant_id string, name string, cuisine_type string, rating float, location string)
CREATE TAG Dish (dish_id string, name string, price float, category string, is_vegetarian bool)
CREATE TAG DeliveryPerson (person_id string, name string, phone string, vehicle_type string, rating float)
CREATE TAG Order (order_id string, order_date datetime, total_amount float, status string, delivery_time int)

# Create Edge Types
CREATE EDGE PLACES (timestamp datetime)
CREATE EDGE FROM (order_date datetime)
CREATE EDGE CONTAINS (quantity int, price float)
CREATE EDGE DELIVERS (pickup_time datetime, delivery_time datetime)
CREATE EDGE SERVES (availability bool)
CREATE EDGE REVIEWS (rating float, comment string, date datetime)
        """, language='sql')
    
    with tab2:
        st.markdown("### 📝 Python Code Examples")
        
        st.code("""
from lancegraph import Graph

# Initialize connection
graph = Graph("food_delivery")

# Insert Customer
graph.execute('''
    INSERT VERTEX Customer (customer_id, name, phone, address, join_date)
    VALUES ("C001", "Alice", "+91-9876543210", "Mumbai, MH", "2024-01-15")
''')

# Insert Order
graph.execute('''
    INSERT VERTEX Order (order_id, order_date, total_amount, status, delivery_time)
    VALUES ("ORD001", "2024-12-29 14:30:00", 450.00, "delivered", 28)
''')

# Create Relationship
graph.execute('''
    INSERT EDGE PLACES (timestamp)
    VALUES ("C001" -> "ORD001", "2024-12-29 14:30:00")
''')

# Query Example
result = graph.execute('''
    MATCH (c:Customer {name: 'Alice'})-[:PLACES]->(o:Order)
    RETURN c.name, o.order_id, o.total_amount
''')

for row in result:
    print(row)
        """, language='python')
    
    with tab3:
        st.markdown("""
        ### 🚀 Deployment Considerations
        
        #### Scalability:
        - **Horizontal Scaling**: Distribute graph across multiple nodes
        - **Sharding**: Partition by customer regions or restaurant zones
        - **Replication**: Multi-master setup for high availability
        
        #### Performance Optimization:
        - Index frequently queried properties (customer_id, order_id)
        - Cache hot paths (popular restaurants, frequent customers)
        - Use connection pooling for concurrent queries
        
        #### Monitoring:
        - Query performance metrics
        - Graph size and growth rate
        - Relationship traversal depth
        - Cache hit rates
        
        #### Use Cases:
        1. **Real-time Recommendations**: Suggest dishes based on order history
        2. **Fraud Detection**: Identify suspicious ordering patterns
        3. **Delivery Optimization**: Find optimal delivery routes
        4. **Customer Segmentation**: Group customers by preferences
        5. **Restaurant Analytics**: Performance and popularity metrics
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p><strong>Food Delivery Graph Database Demo</strong></p>
    <p>Built with Streamlit | Designed for LanceGraph / Nebula Graph</p>
    <p>For Technical Evaluation - Graph Database Assignment</p>
</div>
""", unsafe_allow_html=True)