import os
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine
from dotenv import load_dotenv
import streamlit as st
import networkx as nx
import plotly.graph_objs as go
import logging

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to create SQLAlchemy engine using environment variables
def create_engine_from_env():
    try:
        engine = create_engine(
            sqlalchemy.engine.url.URL.create(
                drivername='mysql+mysqlconnector',
                host=os.getenv('MYSQL_HOST'),
                username=os.getenv('MYSQL_USER'),
                password=os.getenv('MYSQL_PASSWORD'),
                database=''
            )
        )
        logging.info("SQLAlchemy engine created successfully.")
        return engine
    except Exception as e:
        st.error(f"Error: {e}")
        logging.error(f"Engine creation failed: {e}")
        return None

# Function to fetch schemas
def fetch_schemas(engine):
    query = """
    SELECT SCHEMA_NAME
    FROM information_schema.SCHEMATA;
    """
    logging.info("Fetching schemas...")
    return pd.read_sql(query, engine)

# Function to fetch index information with performance metrics
def fetch_index_info(engine, schema_name):
    query = f"""
    SELECT 
        s.TABLE_SCHEMA, 
        s.TABLE_NAME, 
        s.INDEX_NAME, 
        s.SEQ_IN_INDEX, 
        s.COLUMN_NAME, 
        s.NON_UNIQUE, 
        s.INDEX_TYPE,
        t.ENGINE, 
        t.TABLE_ROWS, 
        s.CARDINALITY,
        ROUND(s.CARDINALITY * @@innodb_page_size / 1024 / 1024, 2) AS INDEX_SIZE_MB
    FROM 
        information_schema.STATISTICS s
    INNER JOIN 
        information_schema.TABLES t 
        ON s.TABLE_SCHEMA = t.TABLE_SCHEMA 
        AND s.TABLE_NAME = t.TABLE_NAME
    WHERE 
        s.TABLE_SCHEMA = '{schema_name}'
    ORDER BY 
        s.TABLE_NAME, s.INDEX_NAME, s.SEQ_IN_INDEX;
    """
    logging.info(f"Fetching index information for schema: {schema_name}...")
    return pd.read_sql(query, engine)

# Class for Index Visualization
class IndexVisualizer:
    def __init__(self, data, selected_table):
        self.data = data
        self.selected_table = selected_table
        self.graph = nx.DiGraph()  # Ensure networkx is imported

    def build_graph(self):
        df_table = self.data[self.data['TABLE_NAME'] == self.selected_table]

        # Add nodes and edges for each index and its columns
        for _, row in df_table.iterrows():
            table_node = row['TABLE_NAME']
            index_node = f"{row['INDEX_NAME']} (Non-Unique)" if row['NON_UNIQUE'] else f"{row['INDEX_NAME']} (Unique)"
            column_node = row['COLUMN_NAME']

            # Add performance metrics as hover text
            index_hover_text = (
                f"Index: {row['INDEX_NAME']}<br>"
                f"Type: {row['INDEX_TYPE']}<br>"
                f"Cardinality: {row['CARDINALITY']}<br>"
                f"Index Size: {row['INDEX_SIZE_MB']} MB"
            )

            self.graph.add_node(table_node, label=table_node)
            self.graph.add_node(index_node, label=index_node, hover_text=index_hover_text)
            self.graph.add_node(column_node, label=column_node)

            self.graph.add_edge(table_node, index_node)
            self.graph.add_edge(index_node, column_node)

    def render(self):
        pos = nx.spring_layout(self.graph, seed=42)
        edges = self.graph.edges()

        edge_trace = []
        for edge in edges:
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_trace.append(go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                line=dict(width=2, color='lightgray'),
                hoverinfo='none',
                mode='lines'))

        # Create node trace
        node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            hovertext=[],
            mode='markers+text',
            hoverinfo='text',
            marker=dict(
                showscale=True,
                colorscale='YlGnBu',
                reversescale=True,
                color=[],
                size=20,
                colorbar=dict(
                    thickness=15,
                    title='Node Connections',
                    xanchor='left',
                    titleside='right'
                ),
                line_width=2))

        for node in self.graph.nodes(data=True):
            x, y = pos[node[0]]
            node_trace['x'] += (x,)
            node_trace['y'] += (y,)
            node_trace['text'] += (node[0],)
            node_trace['hovertext'] += (node[1].get('hover_text', node[0]),)
            node_trace['marker']['color'] += (len(self.graph.adj[node[0]]),)

        fig = go.Figure(data=edge_trace + [node_trace],
                        layout=go.Layout(
                            title='<br>MySQL Index Structure Visualization',
                            titlefont_size=16,
                            showlegend=False,
                            hovermode='closest',
                            margin=dict(b=20, l=5, r=5, t=40),
                            annotations=[dict(
                                text="Visualization of MySQL indexes using NetworkX and Plotly",
                                showarrow=False,
                                xref="paper", yref="paper",
                                x=0.005, y=-0.002)],
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                        )

        st.plotly_chart(fig, use_container_width=True)

# Main function for Streamlit app
def main():
    st.title("MySQL Index Visualization Tool")

    # Create SQLAlchemy engine
    engine = create_engine_from_env()
    if engine:
        # Fetch schemas
        df_schemas = fetch_schemas(engine)
        schemas = df_schemas['SCHEMA_NAME'].unique()
        selected_schema = st.selectbox("Select a Schema", schemas)

        if selected_schema:
            # Fetch index information
            df_indexes = fetch_index_info(engine, selected_schema)

            # List of tables
            tables = df_indexes['TABLE_NAME'].unique()
            selected_table = st.selectbox("Select a Table", tables)

            # Show index visualization
            if selected_table:
                st.subheader(f"Index Structure for Table: {selected_table}")
                visualizer = IndexVisualizer(df_indexes, selected_table)
                visualizer.build_graph()
                visualizer.render()

if __name__ == "__main__":
    main()