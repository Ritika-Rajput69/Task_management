import pyodbc

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

# Create stored procedure to retrieve task information along with assigned users
def create_stored_procedure(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE PROCEDURE GetTaskInfoWithUsers
            AS
            BEGIN
                SELECT 
                    t.TaskID,
                    t.Title,
                    t.Assignee,
                    t.DueDate,
                    t.Completed,
                    u.Username AS AssignedUser
                FROM 
                    Tasks t
                LEFT JOIN 
                    Users u ON t.Assignee = u.UserID;
            END;
        """)
        conn.commit()
        print("Stored procedure 'GetTaskInfoWithUsers' created successfully.")
    except pyodbc.Error as e:
        print("Error creating stored procedure:", e)

# Add a new task to the Tasks table
def add_new_task(conn):
    try:
        cursor = conn.cursor()
        title = input("Enter task title: ")
        assignee_name = input("Enter your name: ")
        assignee_email = input("Enter your email: ")
        due_date = input("Enter due date (YYYY-MM-DD): ")
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
def assign_task(conn):
    try:
        cursor = conn.cursor()
        task_id = int(input("Enter task ID to assign: "))
        assignee_email = input("Enter assignee's email: ")
        due_date = input("Enter due date (YYYY-MM-DD): ")
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
def mark_task_as_completed(conn):
    try:
        cursor = conn.cursor()
        task_id = int(input("Enter task ID to mark as completed: "))
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

# Generate reports
def generate_reports(conn):
    try:
        cursor = conn.cursor()
        task_id = int(input("Enter task ID: "))
        cursor.execute("EXEC GetTaskInfoWithUsers")
        rows = cursor.fetchall()
        for row in rows:
            if row[0] == task_id:
                print("Task ID:", row[0])
                print("Title:", row[1])
                print("Assignee:", row[2])
                print("Due Date:", row[3])
                print("Status:", "Completed" if row[4] else "Pending")
                print("Assigned User:", row[5])
                break
    except pyodbc.Error as e:
        print("Error generating reports:", e)

# View all tasks
def view_all_tasks(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Tasks")
        rows = cursor.fetchall()
        print("All Tasks:")
        for row in rows:
            print("Task ID:", row[0])
            print("Title:", row[1])
            print("Assignee:", row[2])
            print("Due Date:", row[3])
            print("Status:", "Completed" if row[4] else "Pending")
            print()
    except pyodbc.Error as e:
        print("Error viewing all tasks:", e)

# Main function
def main():
    conn = connect_to_database()
    if conn:
        create_table_tasks(conn)
        create_stored_procedure(conn)
        while True:
            print("\nTask Management System Menu:")
            print("1. Add New Task")
            print("2. Assign Task")
            print("3. Mark Task as Completed")
            print("4. Generate Reports")
            print("5. View All Tasks")
            print("6. Exit")
            choice = input("Enter your choice: ")
            if choice == '1':
                add_new_task(conn)
            elif choice == '2':
                assign_task(conn)
            elif choice == '3':
                mark_task_as_completed(conn)
            elif choice == '4':
                generate_reports(conn)
            elif choice == '5':
                view_all_tasks(conn)
            elif choice == '6':
                print("Exiting program.")
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 6.")
    else:
        print("Cannot proceed without a valid database connection.")

if __name__ == "__main__":
    main()
