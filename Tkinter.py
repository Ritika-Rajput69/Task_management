from flask import Flask, render_template, request
import pyodbc

app = Flask(__name__)

# Define your server and database
server = "DESKTOP-L5534HF\\SQLEXPRESS"
database = "task_manag_sys"

# Establish a connection to the SQL Server database
def connect_to_database():
    conn_str = f"DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;"
    try:
        conn = pyodbc.connect(conn_str)
        return conn
    except pyodbc.Error as e:
        print("Error connecting to the database:", e)
        return None

# Create the Tasks table if it doesn't exist
def create_table_tasks(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Tasks' AND xtype='U')
            CREATE TABLE Tasks (
                TaskID INT IDENTITY(1,1) PRIMARY KEY,
                Title NVARCHAR(255),
                Assignee NVARCHAR(255),
                DueDate DATE,
                Completed BIT
            )
        """)
        conn.commit()
        print("Table 'Tasks' created successfully.")
    except pyodbc.Error as e:
        print("Error creating table Tasks:", e)

# Add a new task to the Tasks table
def add_new_task(conn, title, assignee_name, assignee_email, due_date):
    try:
        cursor = conn.cursor()
        completed = 0  # New tasks are not completed by default
        # Insert the new task into the Tasks table
        cursor.execute("""
            INSERT INTO Tasks (Title, Assignee, DueDate, Completed)
            VALUES (?, ?, ?, ?)
        """, (title, assignee_name + ' (' + assignee_email + ')', due_date, completed))
        conn.commit()
        print("New task added successfully.")
    except pyodbc.Error as e:
        print("Error adding new task:", e)

# Assign a task to an assignee
def assign_task(conn, task_id, assignee_email, due_date):
    try:
        cursor = conn.cursor()
        # Update the task in the Tasks table
        cursor.execute("""
            UPDATE Tasks
            SET Assignee = ?, DueDate = ?
            WHERE TaskID = ?
        """, (assignee_email, due_date, task_id))
        conn.commit()
        print("Task assigned successfully.")
    except pyodbc.Error as e:
        print("Error assigning task:", e)

# Mark a task as completed
def mark_task_as_completed(conn, task_id):
    try:
        cursor = conn.cursor()
        # Update the task in the Tasks table
        cursor.execute("""
            UPDATE Tasks
            SET Completed = 1
            WHERE TaskID = ?
        """, (task_id,))
        conn.commit()
        print("Task marked as completed successfully.")
    except pyodbc.Error as e:
        print("Error marking task as completed:", e)

# Main route to display the form
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle form submission for adding a new task
@app.route('/add_task', methods=['POST'])
def add_task():
    conn = connect_to_database()
    if conn:
        title = request.form['title']
        assignee_name = request.form['assignee_name']
        assignee_email = request.form['assignee_email']
        due_date = request.form['due_date']
        add_new_task(conn, title, assignee_name, assignee_email, due_date)
        conn.close()
        return "Task added successfully."
    else:
        return "Cannot proceed without a valid database connection."

# Route to handle form submission for assigning a task
@app.route('/assign_task', methods=['POST'])
def assign_task_route():
    conn = connect_to_database()
    if conn:
        task_id = request.form['task_id']
        assignee_email = request.form['assignee_email']
        due_date = request.form['due_date']
        assign_task(conn, task_id, assignee_email, due_date)
        conn.close()
        return "Task assigned successfully."
    else:
        return "Cannot proceed without a valid database connection."

# Route to handle form submission for marking a task as completed
@app.route('/mark_completed', methods=['POST'])
def mark_completed():
    conn = connect_to_database()
    if conn:
        task_id = request.form['task_id']
        mark_task_as_completed(conn, task_id)
        conn.close()
        return "Task marked as completed successfully."
    else:
        return "Cannot proceed without a valid database connection."

if __name__ == '__main__':
    app.run(debug=True)
