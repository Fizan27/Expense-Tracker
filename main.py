import io # for I/O operations
import base64 #provides functions for encoding binary data as ASCII characters.
import sqlite3 # for SQLite database operations
import matplotlib.pyplot as plt # for data visualization
import seaborn as sns # for data visualization
import pandas as pd # for data manipulation and analysis
from flask import Flask, render_template, request, redirect, url_for, flash, session # for web application development
from flask import send_file # for sending files in Flask application
from fpdf import FPDF # for creating PDFs
from flask_mail import Mail # for sending emails through Flask application
import threading # for creating and managing threads
import time # for handling time-related operations
from threading import Thread # for creating and managing threads
from email.mime.application import MIMEApplication # for attaching applications in emails
import smtplib # for sending emails through SMTP server
from email.mime.multipart import MIMEMultipart # for creating multipart emails
from email.mime.text import MIMEText # for attaching text in emails
import os # for performing various operating system related tasks
from email.mime.image import MIMEImage # for attaching images in emails
import queue # for implementing queue data structure
from queue import Queue # for implementing queue data structure
import logging # For documentation
import warnings #to ignore matpotlib warning
warnings.filterwarnings("ignore")


class Node: # Defines a Node class for creating nodes in a tree
    def __init__(self, data):
        self.data = data
        self.next = None


class TreeNode: # Defines a TreeNode class which creates a tree structure of expense categories
    def __init__(self, value, children=None):
        self.value = value
        self.children = children if children is not None else []

    def insert_child(self, child_value): # Function to insert a child node to a tree node
        child = TreeNode(child_value)
        self.children.append(child)
        return child

    def delete_child(self, child_value): # Function to delete a child node from a tree node
        for i, child in enumerate(self.children):
            if child.value == child_value:
                del self.children[i]
                return True
        return False

    def search_child(self, child_value): # Function to search for a child node in a tree node
        for child in self.children:
            if child.value == child_value:
                return child
        return None


def create_expense_tree(): # Function to create and return a tree data structure with predefined categories and subcategories
    expense_tree = TreeNode("Expenses")
    housing = expense_tree.insert_child("Housing")
    housing.insert_child("Rent")
    housing.insert_child("Utilities")

    food = expense_tree.insert_child("Food")
    food.insert_child("Groceries")
    food.insert_child("Dining Out")

    transportation = expense_tree.insert_child("Transportation")
    transportation.insert_child("Gas")

    entertainment = expense_tree.insert_child("Entertainment")
    entertainment.insert_child("TV Streaming")
    entertainment.insert_child("Vacation")

    miscellaneous = expense_tree.insert_child("Miscellaneous")
    miscellaneous.insert_child("Clothing, Shoes & Accessories")
    miscellaneous.insert_child("Pets")
    miscellaneous.insert_child("Other Needs")

    return expense_tree


def dfs_traversal_html(node): # Defines a function to perform depth-first search traversal of the expense tree and return HTML string
    html = "<ul>"
    html += f"<li>{node.value}"
    for child in node.children:
        html += dfs_traversal_html(child)
    html += "</li></ul>"
    return html

# Create the expense tree and get its HTML string
expense_tree = create_expense_tree()
expense_categories_html = dfs_traversal_html(expense_tree)

def create_summary_graph(email, data, labels): #This function creates a bar graph of income and expenses for each month for the given user email
    with sqlite3.connect("user.sqlite") as conn: # Connects to the user database and retrieve the user ID based on the email
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE email = ?", (email,))
        user_id = cur.fetchone()[0]

        # Get the total income and expenses for each month
        cur.execute("SELECT month, total_income, rent, utilities, groceries, gas, pets, other_needs, dining_out, vacation, tv_streaming, clothing_shoes_accessories FROM expenses WHERE user_id = ?", (user_id,))
        data = cur.fetchall()

    # Create a pandas DataFrame from the retrieved data
    columns = ["month", "total_income", "rent", "utilities", "groceries", "gas", "pets", "other_needs", "dining_out", "vacation", "tv_streaming", "clothing_shoes_accessories"]
    df = pd.DataFrame(data, columns=columns)

    # Calculate the total expenses for each month
    df["total_expenses"] = df[["rent", "utilities", "groceries", "gas", "pets", "other_needs", "dining_out", "vacation", "tv_streaming", "clothing_shoes_accessories"]].sum(axis=1)

    # Calculate the difference between total income and total expenses for each month
    df["difference"] = df["total_income"] - df["total_expenses"]

    # Create a bar graph using seaborn to show the difference between income and expenses for each month
    sns.set_style("whitegrid")
    sns.set_palette("colorblind")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=df, x="month", y="difference", ax=ax)
    plt.title("Summary of Income and Expenses")
    plt.xlabel("Month")
    plt.ylabel("Difference")

    # Save the plot as a PNG image and return the image bytes in base64 format
    img_bytes = io.BytesIO()
    plt.savefig(img_bytes, format='png')
    plt.close(fig)
    img_bytes.seek(0)

    b64_img = base64.b64encode(img_bytes.getvalue()).decode()
    return img_bytes


def create_expense_pie_chart(email, month): #This function creates a pie chart of expenses for a given month and user email
    with sqlite3.connect("user.sqlite") as conn: # Connect to the user database and retrieve the user ID based on the email
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE email = ?", (email,))
        user_id = cur.fetchone()[0]

        # Gets the expenses for the given month from the expenses table
        cur.execute(
            "SELECT rent, utilities, groceries, gas, pets, other_needs, dining_out, vacation, tv_streaming, clothing_shoes_accessories FROM expenses WHERE user_id = ? AND month = ?",
            (user_id, month))
        expenses = cur.fetchone()

    if expenses: # If expenses exist, create a pie chart using matplotlib and return the image bytes in base64 format
        labels = ["Rent", "Utilities", "Groceries", "Gas", "Pets", "Other Needs", "Dining Out", "Vacation",
                  "TV Streaming", "Clothing, Shoes & Accessories"]

        fig, ax = plt.subplots(figsize=(8, 6)) # Adjust the size of the figure
        ax.pie(expenses, autopct='%1.1f%%', startangle=90) # Plots the pie chart
        ax.axis('equal')

        ax.legend(labels, title="Categories", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1)) # Move the legend outside of the pie chart

        # Save the pie chart as a PNG image
        img_bytes = io.BytesIO()
        plt.savefig(img_bytes, format='png', bbox_inches='tight', pad_inches=0.5)
        plt.close(fig)
        img_bytes.seek(0)

        # Encodes the image bytes in base64 format
        b64_img = base64.b64encode(img_bytes.getvalue()).decode()
        return b64_img
    else:
        return None


def generate_recommendations(total_income, total_expenses, difference, expenses_by_category): #This function generates recommendations based on the budget percentages
    recommendation = ""

    # Calculate the budget percentages
    needs_percentage, wants_percentage, savings_percentage = calculate_budget_percentages(total_income, total_expenses,
                                                                                          expenses_by_category)

    # Provide recommendations based on the financial principles
    if needs_percentage < 50:
        recommendation += "You may be overspending on wants. Consider cutting back on non-essential expenses and redirecting the funds towards needs."
    if savings_percentage < 20:
        if recommendation:
            recommendation += " Additionally, "
        else:
            recommendation += "Consider "
        recommendation += "increasing your savings percentage to at least 20% to build an emergency fund and save for the future."
    if total_income > 0 and total_income < (total_expenses * 6):
        if recommendation:
            recommendation += " Additionally, "
        else:
            recommendation += "Consider "
        recommendation += "building an emergency fund that can cover at least 6 months of your living expenses."

    return recommendation

def calculate_budget_percentages(total_income, total_expenses, expenses_by_category): #This function calculates the budget percentages based on the 50/30/20 rule
    # Calculate the 50/30/20 percentages
    needs_percentage = 50
    wants_percentage = 30
    savings_percentage = 20

    # Calculate the total monthly debt payments
    debt_payments = expenses_by_category["other_needs"]

    # Calculate the debt-to-income ratio
    debt_to_income_ratio = debt_payments / total_income

    # Calculate the emergency fund size
    emergency_fund_size = total_expenses * 6

    # Calculate the retirement savings
    retirement_savings = total_income * 0.15 * 30

    # Adjust the percentages based on the financial principles
    if debt_to_income_ratio > 0.36:
        needs_percentage -= 5
        wants_percentage += 5
    if total_expenses < emergency_fund_size:
        needs_percentage += 5
        savings_percentage -= 5
    if total_income > 0 and total_income < retirement_savings:
        savings_percentage -= 5
        wants_percentage += 5

    return needs_percentage, wants_percentage, savings_percentage

# split into multiple methods

def send_expense_report(email, month, report_queue): #This function is used to generate and send an expense report for a specific month to a given email address.
    try:
        with sqlite3.connect("user.sqlite") as conn:#Fetches the user and expense data for the specified email address and month from the SQLite database.
            cur = conn.cursor()
            cur.execute("SELECT id, name FROM users WHERE email = ?", (email,))
            user_id, user_name = cur.fetchone()

            cur.execute("""
                SELECT month, total_income, rent, utilities, groceries, gas, pets, other_needs, dining_out, vacation, tv_streaming, clothing_shoes_accessories
                FROM expenses WHERE user_id = ? AND month = ?
                """, (user_id, month))

            data = cur.fetchone()

        if not data:
            return

        # Uses the fetched data to generate a PDF report, which contains a summary of the user's expenses for the month.
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Adds the report title
        pdf.cell(200, 10, txt=f"Expense Report for {user_name} - {month}", ln=1, align="C")
        columns = ['Month', 'Total Income', 'Rent', 'Utilities', 'Groceries', 'Gas', 'Pets', 'Other Needs',
                   'Dining Out', 'Vacation', 'TV Streaming', 'Clothing, Shoes, Accessories', 'Total Expenses']

        # Print the month in the first row
        pdf.cell(80, 10, txt=data[0], border=1, ln=1)

        # Set the column widths
        col_width1 = 80
        col_width2 = 40

        # Print the expense data in two columns below the month
        for i in range(1, len(data), 2):
            pdf.cell(col_width1, 10, txt=columns[i], border=1)
            pdf.cell(col_width2, 10, txt=str(data[i]), border=1)
            pdf.ln()
            if i + 1 < len(data):
                pdf.cell(col_width1, 10, txt=columns[i + 1], border=1)
                pdf.cell(col_width2, 10, txt=str(data[i + 1]), border=1)
                pdf.ln()

        # Print the total expenses in a separate row at the bottom
        total_expenses = sum(data[2:-1])
        pdf.cell(col_width1, 10, txt="Total Expenses", border=1)
        pdf.cell(col_width2, 10, txt=str(total_expenses), border=1)
        pdf.cell(col_width2, 10, txt=str(total_expenses), border=1)
        pdf.ln()

        # pdf.output("expense_report.pdf") # same name
        # path = os.getcwd() # no hardcoding
        # pdf.output(path + f"/reports/expense_report_{user_name}.pdf")
        pdf.output(f"/Users/Fizan/PycharmProjects/fromwindows/reports/expense_report_{user_name}.pdf")

       # this would be a queue
        # if the limit reaches -> 10
        # you want to remove the last one

        # Create and save the summary graph
        summary_data = data[1:-1]
        summary_labels = columns[1:-1]
        summary_graph_bytes = create_summary_graph(email, summary_data, summary_labels)
        with open("summary_graph.png", "wb") as f:
            f.write(summary_graph_bytes.getvalue())

        # Create and save the pie chart
        pie_chart_bytes = create_expense_pie_chart(email, month)
        if not pie_chart_bytes:
            report_queue.put((email, False))
            return
        with open("pie_chart.png", "wb") as f:
            f.write(base64.b64decode(pie_chart_bytes))

        # Send the email with expense report, summary graph and pie chart
        with open("expense_report.pdf", "rb") as f:
            attach1 = MIMEApplication(f.read(), _subtype="pdf")
            attach1.add_header("Content-Disposition", "attachment", filename="expense_report.pdf")
            with open("summary_graph.png", "rb") as f:
                attach2 = MIMEImage(f.read(), _subtype="png")
                attach2.add_header("Content-Disposition", "attachment", filename="summary_graph.png")

            with open("pie_chart.png", "rb") as f:
                attach3 = MIMEImage(f.read(), _subtype="png")
                attach3.add_header("Content-Disposition", "attachment", filename="pie_chart.png")

            msg = MIMEMultipart() # Create a multipart message to contain the email content and attachments
            msg.attach(MIMEText("Please find attached your expense report and summary graph for the selected month.")) # Add the email text content
            msg.attach(attach1) # Add the expense report attachment
            msg.attach(attach2) # Add the summary graph attachment
            msg.attach(attach3) # Add the pie chart attachment
            msg["Subject"] = f"Expense Report and Summary Graphs for {month}" # Set the email subject line
            msg["From"] = "expensetrackersender@gmail.com" # Set the email sender address
            msg["To"] = email # Set the email recipient address

            # Sends the email with the expense report, summary graph, and pie chart attachments
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login("expensetrackersender@gmail.com", "jioijrzinwibvfrg")
                server.send_message(msg)

            # Add a tuple with the email, month, and True (indicating success) to the report queue
            report_queue.put((email, month, True))

    except Exception as e: # If there is an error, print it to the console and add a tuple with the email and False (indicating failure) to the report queue
        print(e)
        report_queue.put((email, False))

def process_report_queue(report_queue):
    # Configure the logging module
    logging.basicConfig(filename='expense_report.log', level=logging.INFO,
                        format='%(asctime)s:%(levelname)s:%(message)s')

    # Continuously check the report queue for new reports
    while True:
        # Get the next report from the queue
        email, month, success = report_queue.get()

        # If the report was sent successfully, log a success message
        if success:
            logging.info(f"Expense report for {month} successfully sent to {email}.")
        # Otherwise, log an error message
        else:
            logging.error(f"Failed to send expense report for {month} to {email}.")

        time.sleep(1)  # Sleep for a short duration to avoid excessive CPU usage

conn = sqlite3.connect("user.sqlite")
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, password TEXT)")

# maybe change to two tables (if you can)
#Create a table called 'expenses' if it doesn't already exist in the 'user.sqlite' database
cur.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    month TEXT,
    total_income REAL,
    rent REAL,
    utilities REAL,
    groceries REAL,
    gas REAL,
    pets REAL,
    other_needs REAL,
    dining_out REAL,
    vacation REAL,
    tv_streaming REAL,
    clothing_shoes_accessories REAL,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
""")


#Initialize the Flask app and sets up email configuration
app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
# os is a module to represent environment variables
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
mail = Mail(app)
app.secret_key = "your_secret_key_here" #sets a secret key for the Flask application.


@app.route("/", methods=["GET", "POST"]) #specifies url for the login page
def login():
    # Check if the request method is POST
    if request.method == "POST":
        # Retrieve email and password from the submitted form
        email = request.form["email"]
        password = request.form["password"]

        # Check if the email and password match a record in the database
        with sqlite3.connect("user.sqlite") as conn:
            cur = conn.cursor()
            # Create users table if not exists
            cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, password TEXT)")
            cur.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
            user = cur.fetchone()

        if user:
            # Sets the email in the session and redirect to home page
            session["email"] = email
            return redirect(url_for("home"))
        else:
            # Displays an error message for invalid email or password
            error = "Invalid email or password"

        # Render the login template with the error message
        return render_template("login.html", error=error)
    else:
        return render_template("login.html")     # Render the login template for GET requests

@app.route("/Register", methods=["GET", "POST"]) #Specifies url for registration page and allow GET and POST methods
def register():
    error = None # initializes the error variable as None, which is used to store error messages if there are any.
    if request.method == "POST": # checks if the form has been submitted via POST method.
        name = request.form["name"]  # gets the value of the input field with the name "name" from the submitted form
        email = request.form["email"] # gets the value of the input field with the name "email" from the submitted form.
        password = request.form["password"] #gets the value of the input field with the name "password" from the submitted form.
        password_confirm = request.form["password_confirm"] #gets the value of the input field with the name "password_confirm" from the submitted form.

        if password != password_confirm: # Check if the password and confirm password fields match
            error = "Passwords do not match. Please try again."
            return render_template("Register.html", error=error)

        # Insert the user data into the database
        with sqlite3.connect("user.sqlite") as conn: #connects to the database and sets up a cursor to execute SQL queries.
            cur = conn.cursor()
            # creates the users table in the database if it does not already exist
            cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT,
                email TEXT UNIQUE,
                password TEXT
            )
            """)
            cur.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password)) #Inserts the new user's data into the users table in the database.
            conn.commit() #commits the changes made to the database.

        flash("You have successfully registered.") #flashes a success message to be displayed on the next page.
        return redirect(url_for("login"))  #redirects the user to the login page after successful registration.
    else:
        return render_template("Register.html", error=error) #handles the GET request by rendering the register template with the error message if there is one

@app.route("/form-page", methods=["GET", "POST"])  #Specifies url for form page and allow GET and POST methods
def form_page():
    email = session.get("email") # Get the user's email from the session
    form_data = session.get("form_data", {}) # Get the user's form data from the session, or creates an empty dictionary

    user_name = get_user_name(email)  # Get the user's name using the email

    if request.method == "POST": # Handle POST requests
        form_data.update(request.form) # Update the form_data with the data from the submitted form
        session["form_data"] = form_data # Saves the form_data to the session

        with sqlite3.connect("user.sqlite") as conn: # Saves the new expense data to the database
            cur = conn.cursor()
            cur.execute("SELECT id FROM users WHERE email = ?", (email,))
            user_id = cur.fetchone()[0]

            month = form_data.get("month", None)

        with sqlite3.connect("user.sqlite") as conn:
            cur = conn.cursor()

            # Check if there's already an entry for the given month
            cur.execute("SELECT * FROM expenses WHERE user_id = ? AND month = ?", (user_id, month))
            existing_entry = cur.fetchone()

            if existing_entry:
                flash("Expenses for the selected month have already been submitted.")
                return redirect(url_for("form_page"))  # Add this line
            else:
                # Save the new expense data
                cur.execute("""
                INSERT INTO expenses (
                    user_id,
                    month,
                    total_income,
                    rent,
                    utilities,
                    groceries,
                    gas,
                    pets,
                    other_needs,
                    dining_out,
                    vacation,
                    tv_streaming,
                    clothing_shoes_accessories
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (user_id, month, form_data["total_income"], form_data["rent"], form_data["utilities"], form_data["groceries"], form_data["gas"], form_data["pets"], form_data["other_needs"], form_data["dining_out"], form_data["vacation"], form_data["tv_streaming"], form_data["clothing_shoes_accessories"]))
                conn.commit()

                # Update the form_data and redirect to the form page
                session["form_data"] = form_data
                return redirect(url_for("form_page"))

    # If form_data is empty, set the month to the current month
    if not form_data:
        from datetime import datetime
        form_data["month"] = datetime.today().strftime("%Y-%m")

    return render_template("Form.html", form_data=form_data, user_name=user_name) # Render the form template with the user's form data and name


def get_user_name(email): #This function takes an email address as input and returns the corresponding user's name
    with sqlite3.connect("user.sqlite") as conn: #Connects to the database and execute a SELECT statement to fetch the user's name
        cur = conn.cursor()
        cur.execute("SELECT name FROM users WHERE email = ?", (email,))
        user_name = cur.fetchone()[0]
    return user_name #It returns the user's name as a string.

@app.route("/get-expenses")
def get_expenses():
    email = session.get("email")
    month = request.args.get("month")

    with sqlite3.connect("user.sqlite") as conn:
        cur = conn.cursor()

        if month:
            cur.execute("""
            SELECT users.name, expenses.month, expenses.total_income, expenses.rent, expenses.utilities, expenses.groceries, expenses.gas, expenses.pets, expenses.other_needs, expenses.dining_out, expenses.vacation, expenses.tv_streaming, expenses.clothing_shoes_accessories
            FROM users
            JOIN expenses ON users.id = expenses.user_id
            WHERE users.email = ? AND expenses.month = ?
            """, (email, month))
            expenses = cur.fetchone()

            if expenses:
                total_income = expenses[2]
                rent = expenses[3]
                utilities = expenses[4]
                groceries = expenses[5]
                gas = expenses[6]
                pets = expenses[7]
                other_needs = expenses[8]
                dining_out = expenses[9]
                vacation = expenses[10]
                tv_streaming = expenses[11]
                clothing_shoes_accessories = expenses[12]

                total_expenses = rent + utilities + groceries + gas + pets + other_needs + dining_out + vacation + tv_streaming + clothing_shoes_accessories
                difference = total_income - total_expenses

                return {
                    "name": expenses[0],
                    "month": expenses[1],
                    "total_income": total_income,
                    "rent": rent,
                    "utilities": utilities,
                    "groceries": groceries,
                    "gas": gas,
                    "pets": pets,
                    "other_needs": other_needs,
                    "dining_out": dining_out,
                    "vacation": vacation,
                    "tv_streaming": tv_streaming,
                    "clothing_shoes_accessories": clothing_shoes_accessories,
                    "total_expenses": total_expenses,
                    "difference": difference
                }
            else:
                return {}  # Return an empty dictionary if no expenses are found
    return {}

@app.route('/plot-summary-graph') #generate a summary graph of income and expenses for the user.
def plot_summary_graph():
    email = session.get('email') # Get the email of the current user from the session

    with sqlite3.connect('user.sqlite') as conn:  #Fetches the user ID from the database using their email
        cur = conn.cursor()
        cur.execute('SELECT id FROM users WHERE email = ?', (email,))
        user_id = cur.fetchone()[0]

        # Get the expense data for the user
        cur.execute('SELECT month, total_income, rent, utilities, groceries, gas, pets, other_needs, dining_out, vacation, tv_streaming, clothing_shoes_accessories FROM expenses WHERE user_id = ?', (user_id,))
        data = cur.fetchall()
    #Defines the column names
    columns = ['month', 'total_income', 'rent', 'utilities', 'groceries', 'gas', 'pets', 'other_needs', 'dining_out', 'vacation', 'tv_streaming', 'clothing_shoes_accessories']
    df = pd.DataFrame(data, columns=columns) # Create a DataFrame using the fetched data and column names

    # Calculate the total expenses for each month
    df['total_expenses'] = df[['rent', 'utilities', 'groceries', 'gas', 'pets', 'other_needs', 'dining_out', 'vacation', 'tv_streaming', 'clothing_shoes_accessories']].sum(axis=1)

    # Calculate the difference between total income and total expenses for each month
    df['difference'] = df['total_income'] - df['total_expenses']

    sns.set_style('whitegrid')  # Set the seaborn style to whitegrid
    sns.set_palette('colorblind') # Set the seaborn color palette to colorblind
    fig, ax = plt.subplots(figsize=(10, 6)) # Create a figure and axis object with a size of 10x6
    sns.barplot(data=df, x='month', y='difference', ax=ax) # Create a bargraph using the DataFrame and axis object
    plt.title('Summary of Income and Expenses') # Set the title of the graph
    plt.xlabel('Month') # Set the label for the x-axis
    plt.ylabel('Difference')  # Set the label for the y-axis

    img_bytes = io.BytesIO() # Create a BytesIO object to store the plot image data
    plt.savefig(img_bytes, format='png') # Save the plot as a PNG image to the BytesIO object
    plt.close(fig) # Close the figure
    img_bytes.seek(0)  # Move the file pointer to the beginning of the BytesIO object

    return send_file(img_bytes, mimetype='image/png') # Return the image data as a PNG file


@app.route("/summary-page") #Specifies url for summary page
def summary_page():
    email = session.get("email") # Get the user's email from the session
    month = request.args.get("month") # Get the month from the request parameters

    if not month: #If month is not provided, set it to the current month
        from datetime import datetime
        month = datetime.today().strftime("%Y-%m")

    with sqlite3.connect("user.sqlite") as conn: #connection is made to the users.sqlite database.
        cur = conn.cursor()

        # Get the user ID for the logged in user
        cur.execute("SELECT id FROM users WHERE email = ?", (email,))
        user_id = cur.fetchone()[0]

        # Get the total income for all months, If no income is found, it is set to 0.
        cur.execute("SELECT SUM(total_income) FROM expenses WHERE user_id = ?", (user_id,))
        total_income = cur.fetchone()[0]
        if total_income is None:
            total_income = 0

        # The total expenses for all months are retrieved from the database for the logged in user. If no expenses are found, all expense categories are set to 0.
        cur.execute(
            "SELECT SUM(rent), SUM(utilities), SUM(groceries), SUM(gas), SUM(pets), SUM(other_needs), SUM(dining_out), SUM(vacation), SUM(tv_streaming), SUM(clothing_shoes_accessories) FROM expenses WHERE user_id = ?",
            (user_id,))
        expenses_row = cur.fetchone()

        if expenses_row:
            rent, utilities, groceries, gas, pets, other_needs, dining_out, vacation, tv_streaming, clothing_shoes_accessories = expenses_row
            expenses_by_category = {
                "rent": rent,
                "utilities": utilities,
                "groceries": groceries,
                "gas": gas,
                "pets": pets,
                "other_needs": other_needs,
                "dining_out": dining_out,
                "vacation": vacation,
                "tv_streaming": tv_streaming,
                "clothing_shoes_accessories": clothing_shoes_accessories,
            }
        else:
            expenses_by_category = {
                "rent": 0,
                "utilities": 0,
                "groceries": 0,
                "gas": 0,
                "pets": 0,
                "other_needs": 0,
                "dining_out": 0,
                "vacation": 0,
                "tv_streaming": 0,
                "clothing_shoes_accessories": 0,
            }

        # Extract the data and labels for plotting the pie chart
        data = list(expenses_by_category.values())
        labels = list(expenses_by_category.keys())
        total_expenses = sum(expenses_by_category.values()) #The total_expenses variable is set to the sum of all expenses.
        difference = total_income - total_expenses #The difference variable is set to the difference between total income and total expenses.

        # Get the category with the highest and lowest expenses using aggregate SQL functions
        cur.execute(
            "SELECT MAX(rent), MAX(utilities), MAX(groceries), MAX(gas), MAX(pets), MAX(other_needs), MAX(dining_out), MAX(vacation), MAX(tv_streaming), MAX(clothing_shoes_accessories) FROM expenses WHERE user_id = ? AND month = ?",
            (user_id, month))
        max_expense_row = cur.fetchone()
        max_expense_value = max(max_expense_row)
        max_expense_category = labels[max_expense_row.index(max_expense_value)]

        cur.execute(
            "SELECT MIN(rent), MIN(utilities), MIN(groceries), MIN(gas), MIN(pets), MIN(other_needs), MIN(dining_out), MIN(vacation), MIN(tv_streaming), MIN(clothing_shoes_accessories) FROM expenses WHERE user_id = ? AND month = ?",
            (user_id, month))
        min_expense_row = cur.fetchone()
        min_expense_value = min(min_expense_row)
        min_expense_category = labels[min_expense_row.index(min_expense_value)]

        # Create the summary graph
        img_bytes = create_summary_graph(email, data, labels)
        b64_img = base64.b64encode(img_bytes.read()).decode()

        needs_percentage, wants_percentage, savings_and_investments_percentage = calculate_budget_percentages(
            total_income, total_expenses, expenses_by_category)

        recommendation = generate_recommendations(total_income, total_expenses, difference, expenses_by_category)

        # Create the expense pie chart
        b64_pie_chart = create_expense_pie_chart(email, month)

    return render_template("Summary.html", income=total_income, total_expenses=total_expenses, difference=difference,
                           b64_img=b64_img, recommendation=recommendation, b64_pie_chart=b64_pie_chart,
                           max_expense_category=max_expense_category, min_expense_category=min_expense_category,
                           needs_percentage=needs_percentage, wants_percentage=wants_percentage,
                           savings_and_investments_percentage=savings_and_investments_percentage,
                           expense_categories_html=expense_categories_html)


@app.route("/report-creation", methods=["GET", "POST"])  #Specifies url for report creation page and allows GET and POST methods
def report_creation():
    if request.method == "POST": # Check if the form is submitted using POST method
        email = session.get("email") # Get the email from form data
        month = request.form.get("month") # Get the month from form data

        if not month:     # If month is not specified, use the current month
            from datetime import datetime
            month = datetime.today().strftime("%Y-%m")

        # Generate the expense report and send it to the user's email in a seperate thread
        # multi threading -> concurrency
        t = Thread(target=send_expense_report, args=(email, month, report_queue))
        t.start()
        t.join()

        if report_queue.get():     # Check if the report is generated successfully
            return render_template("Reportcreation.html", success=True)
        else:
            return render_template("Reportcreation.html", error=True)
    return render_template("Reportcreation.html") # If the request method is GET, render the report creation page

@app.route("/Home") #Specifies url for home page
def home():
    return render_template('Home.html') #renders the "Home.html" template and returns it to the client's web browser

if __name__=='__main__':
    # Create the report_queue
    report_queue = queue.Queue()
    # Start the process_report_queue function in a separate thread
    #This starts a thread to run the process_report_queue function, which will process report creation requests from the report_queue
    report_thread = threading.Thread(target=process_report_queue, args=(report_queue,))
    report_thread.start()

    # Start the Flask app
    app.run(debug=True)
