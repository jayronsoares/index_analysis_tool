### **MySQL index visualization tool**

#### **1. Setting up the environment**

1. **Install required packages**:
   Make sure you have the necessary Python packages installed:
   ```bash
   pip install pandas sqlalchemy mysql-connector-python python-dotenv streamlit networkx plotly
   ```

2. **Create and configure `.env` file**:
   - Create a `.env` file in your project directory.
   - Add your MySQL credentials:
     ```
     MYSQL_HOST=localhost
     MYSQL_USER=your_username
     MYSQL_PASSWORD=your_password
     ```

#### **2. Running the application**

1. **Save the script**:
   Save the provided script to a file named `index_visualization.py`.

2. **Run the Streamlit app**:
   Execute the script using Streamlit:
   ```bash
   streamlit run index_visualization.py
   ```
   This will start a local server and open the application in your web browser.

#### **3. Using the application**

1. **Select a schema**:
   - From the dropdown menu, choose the schema you want to analyze. This will load all tables and indexes within the selected schema.

2. **Select a table**:
   - Choose a specific table from the dropdown menu to view its index structure.

3. **View visualization**:
   - The plot will display a graph of tables, indexes, and columns.
   - Nodes represent tables, indexes, and columns, while edges show relationships between them.

#### **4. Interpreting the results**

1. **Nodes**:
   - **Table nodes**: Represent your database tables.
   - **Index nodes**: Show the indexes associated with tables. The label indicates the index name and whether it's unique.
   - **Column nodes**: Represent the columns indexed by each index.

2. **Edges**:
   - **Table to index**: Connects a table to its indexes.
   - **Index to column**: Connects an index to the columns it covers.

3. **Hover text**:
   - Hover over index nodes to see detailed metrics:
     - **Index name**: The name of the index.
     - **Index type**: The type of index (e.g., BTREE, HASH).
     - **Cardinality**: The number of unique values in the index (higher cardinality typically indicates better selectivity).
     - **Size**: The size of the index in megabytes (larger indexes may affect performance).

4. **Node colors and sizes**:
   - **Colors**: Indicate the number of connections (node degree). Nodes with more connections may be central to the database structure.
   - **Sizes**: Reflect node importance based on its connections.

#### **5. Actionable insights**

1. **Optimize queries**:
   - Ensure that your queries use indexes effectively, particularly those with high cardinality.

2. **Index management**:
   - Review and manage indexes to optimize performance. Remove redundant indexes and address any missing ones.

3. **Performance tuning**:
   - Use insights on cardinality and index size to fine-tune your database. Large indexes might need optimization or maintenance.

#### **6. Practical example**

1. **If a table node shows many indexes**:
   - **Action**: Verify if each index is needed or if they can be consolidated to improve performance and reduce storage overhead.

2. **If an index has low cardinality**:
   - **Action**: Consider if the index is being used effectively or if a different index might be more suitable for your queries.

3. **If index size is large**:
   - **Action**: Assess the impact on performance and consider strategies for index optimization or maintenance.
