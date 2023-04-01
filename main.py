import base64
import io
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask import send_file
from fpdf import FPDF
from flask_mail import Mail
import threading
import time
from threading import Thread
from email.mime.application import MIMEApplication
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from email.mime.image import MIMEImage
import queue
from queue import Queue
import logging
# For documentation
import warnings
warnings.filterwarnings("ignore")


class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class TreeNode:
    def __init__(self, value, children=None):
        self.value = value
        self.children = children if children is not None else []

    def insert_child(self, child_value):
        child = TreeNode(child_value)
        self.children.append(child)
        return child

    def delete_child(self, child_value):
        for i, child in enumerate(self.children):
            if child.value == child_value:
                del self.children[i]
                return True
        return False

    def search_child(self, child_value):
        for child in self.children:
            if child.value == child_value:
                return child
        return None


def create_expense_tree():
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


def dfs_traversal_html(node):
    html = "<ul>"
    html += f"<li>{node.value}"
    for child in node.children:
        html += dfs_traversal_html(child)
    html += "</li></ul>"
    return html

expense_tree = create_expense_tree()
expense_categories_html = dfs_traversal_html(expense_tree)

def create_summary_graph(email, data, labels):
    with sqlite3.connect("user.sqlite") as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE email = ?", (email,))
        user_id = cur.fetchone()[0]

        # Get the total income and expenses for each month
        cur.execute("SELECT month, total_income, rent, utilities, groceries, gas, pets, other_needs, dining_out, vacation, tv_streaming, clothing_shoes_accessories FROM expenses WHERE user_id = ?", (user_id,))
        data = cur.fetchall()

    # Create a pandas DataFrame from the data
    columns = ["month", "total_income", "rent", "utilities", "groceries", "gas", "pets", "other_needs", "dining_out", "vacation", "tv_streaming", "clothing_shoes_accessories"]
    df = pd.DataFrame(data, columns=columns)

    # Calculate the total expenses for each month
    df["total_expenses"] = df[["rent", "utilities", "groceries", "gas", "pets", "other_needs", "dining_out", "vacation", "tv_streaming", "clothing_shoes_accessories"]].sum(axis=1)

    # Calculate the difference between total income and total expenses for each month
    df["difference"] = df["total_income"] - df["total_expenses"]

    # Create a bar plot using seaborn
    sns.set_style("whitegrid")
    sns.set_palette("colorblind")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=df, x="month", y="difference", ax=ax)
    plt.title("Summary of Income and Expenses")
    plt.xlabel("Month")
    plt.ylabel("Difference")

    # Save the plot as a PNG image
    img_bytes = io.BytesIO()
    plt.savefig(img_bytes, format='png')
    plt.close(fig)
    img_bytes.seek(0)

    b64_img = base64.b64encode(img_bytes.getvalue()).decode()
    return img_bytes

def create_expense_pie_chart(email, month):
    with sqlite3.connect("user.sqlite") as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE email = ?", (email,))
        user_id = cur.fetchone()[0]

        cur.execute(
            "SELECT rent, utilities, groceries, gas, pets, other_needs, dining_out, vacation, tv_streaming, clothing_shoes_accessories FROM expenses WHERE user_id = ? AND month = ?",
            (user_id, month))
        expenses = cur.fetchone()

    if expenses:
        labels = ["Rent", "Utilities", "Groceries", "Gas", "Pets", "Other Needs", "Dining Out", "Vacation",
                  "TV Streaming", "Clothing, Shoes & Accessories"]

        # Adjust the size of the figure
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.pie(expenses, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')

        # Move the legend outside of the pie chart
        ax.legend(labels, title="Categories", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

        img_bytes = io.BytesIO()
        plt.savefig(img_bytes, format='png', bbox_inches='tight', pad_inches=0.5)
        plt.close(fig)
        img_bytes.seek(0)

        b64_img = base64.b64encode(img_bytes.getvalue()).decode()
        return b64_img
    else:
        return None


def generate_recommendations(total_income, total_expenses, difference, expenses_by_category):
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

def calculate_budget_percentages(total_income, total_expenses, expenses_by_category):
    # Calculate the 50/30/20 percentages
    needs_percentage = 50
    wants_percentage = 30
    savings_percentage = 20

    # Calculate the total monthly debt payments
    debt_payments = expenses_by_category["other_needs"] + expenses_by_category["pets"]

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
def get_expenses_data(email, month):
    # Implement your logic for retrieving the expense data for the given month
    # For demonstration purposes, we will use a dummy dataset
    expenses_data = {
        "rent": 1000,
        "utilities": 150,
        "groceries": 200,
        "gas": 50,
        "pets": 25,
        "other_needs": 100,
        "dining_out": 75,
        "vacation": 500,
        "tv_streaming": 30,
        "clothing_shoes_accessories": 150
    }

    return expenses_data

def send_expense_report(email, month, report_queue):
    try:
        # Fetch user and expense data
        with sqlite3.connect("user.sqlite") as conn:
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

        # Create a PDF report
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

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

            msg = MIMEMultipart()
            msg.attach(MIMEText("Please find attached your expense report and summary graph for the selected month."))
            msg.attach(attach1)
            msg.attach(attach2)
            msg.attach(attach3)
            msg["Subject"] = f"Expense Report and Summary Graphs for {month}"
            # cange the email
            msg["From"] = "expensetrackersender@gmail.com"
            msg["To"] = email

            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                # create a fake email
                server.login("expensetrackersender@gmail.com", "jioijrzinwibvfrg")
                server.send_message(msg)

            report_queue.put((email, month, True))

    except Exception as e:
        print(e)
        report_queue.put((email, False))

def process_report_queue(report_queue):
    # Configure the logging module
    # mention this in the documentation
    logging.basicConfig(filename='expense_report.log', level=logging.INFO,
                        format='%(asctime)s:%(levelname)s:%(message)s')

    while True:
        email, month, success = report_queue.get()

        if success:
            logging.info(f"Expense report for {month} successfully sent to {email}.")
        else:
            logging.error(f"Failed to send expense report for {month} to {email}.")

        time.sleep(1)  # Sleep for a short duration to avoid excessive CPU usage

conn = sqlite3.connect("user.sqlite")
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, password TEXT)")

# maybe change to two tables (if you can)
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

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
# os is a module to represent environment variables
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
mail = Mail(app)
app.secret_key = "your_secret_key_here"

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Check if the email and password match a record in the database
        with sqlite3.connect("user.sqlite") as conn:
            cur = conn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, password TEXT)")
            cur.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
            user = cur.fetchone()

        if user:
            session["email"] = email
            return redirect(url_for("home"))
        else:
            error = "Invalid email or password"

        return render_template("login.html", error=error)
    else:
        return render_template("login.html")

@app.route("/Register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        password_confirm = request.form["password_confirm"]

        if password != password_confirm:
            error = "Passwords do not match. Please try again."
            return render_template("Register.html", error=error)

        # Insert the user data into the database
        with sqlite3.connect("user.sqlite") as conn:
            cur = conn.cursor()
            cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT,
                email TEXT UNIQUE,
                password TEXT
            )
            """)
            cur.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
            conn.commit()

        flash("You have successfully registered.")
        return redirect(url_for("login"))
    else:
        return render_template("Register.html", error=error)

@app.route("/form-page", methods=["GET", "POST"])
def form_page():
    email = session.get("email")
    form_data = session.get("form_data", {})

    user_name = get_user_name(email)  # Get the user's name using the email

    if request.method == "POST":
        form_data.update(request.form)
        session["form_data"] = form_data

        with sqlite3.connect("user.sqlite") as conn:
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

    return render_template("Form.html", form_data=form_data, user_name=user_name)


def get_user_name(email):
    with sqlite3.connect("user.sqlite") as conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM users WHERE email = ?", (email,))
        user_name = cur.fetchone()[0]
    return user_name

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

@app.route('/plot-summary-graph')
def plot_summary_graph():
    email = session.get('email')

    with sqlite3.connect('user.sqlite') as conn:
        cur = conn.cursor()
        cur.execute('SELECT id FROM users WHERE email = ?', (email,))
        user_id = cur.fetchone()[0]

        cur.execute('SELECT month, total_income, rent, utilities, groceries, gas, pets, other_needs, dining_out, vacation, tv_streaming, clothing_shoes_accessories FROM expenses WHERE user_id = ?', (user_id,))
        data = cur.fetchall()

    columns = ['month', 'total_income', 'rent', 'utilities', 'groceries', 'gas', 'pets', 'other_needs', 'dining_out', 'vacation', 'tv_streaming', 'clothing_shoes_accessories']
    df = pd.DataFrame(data, columns=columns)

    df['total_expenses'] = df[['rent', 'utilities', 'groceries', 'gas', 'pets', 'other_needs', 'dining_out', 'vacation', 'tv_streaming', 'clothing_shoes_accessories']].sum(axis=1)

    df['difference'] = df['total_income'] - df['total_expenses']

    sns.set_style('whitegrid')
    sns.set_palette('colorblind')
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=df, x='month', y='difference', ax=ax)
    plt.title('Summary of Income and Expenses')
    plt.xlabel('Month')
    plt.ylabel('Difference')

    img_bytes = io.BytesIO()
    plt.savefig(img_bytes, format='png')
    plt.close(fig)
    img_bytes.seek(0)

    return send_file(img_bytes, mimetype='image/png')

@app.route("/summary-page")
def summary_page():
    email = session.get("email")
    month = request.args.get("month")

    if not month:
        from datetime import datetime
        month = datetime.today().strftime("%Y-%m")

    with sqlite3.connect("user.sqlite") as conn:
        cur = conn.cursor()

        # Get the user ID for the logged in user
        cur.execute("SELECT id FROM users WHERE email = ?", (email,))
        user_id = cur.fetchone()[0]

        # Get the total income for all months
        cur.execute("SELECT SUM(total_income) FROM expenses WHERE user_id = ?", (user_id,))
        total_income = cur.fetchone()[0]
        if total_income is None:
            total_income = 0

        # Get the total expenses for all months
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
        data = list(expenses_by_category.values())
        labels = list(expenses_by_category.keys())
        total_expenses = sum(expenses_by_category.values())
        difference = total_income - total_expenses

        # Get the category with the highest and lowest expenses using aggregate functions
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

@app.route("/report-creation", methods=["GET", "POST"])
def report_creation():
    if request.method == "POST":
        email = session.get("email")
        month = request.form.get("month")

        if not month:
            from datetime import datetime
            month = datetime.today().strftime("%Y-%m")

        # Generate the expense report and send it to the user's email
        # multi threading -> concurrency
        t = Thread(target=send_expense_report, args=(email, month, report_queue))
        t.start()
        t.join() # run

        if report_queue.get():
            return render_template("Reportcreation.html", success=True)
        else:
            return render_template("Reportcreation.html", error=True)
    return render_template("Reportcreation.html")

@app.route("/Home")
def home():
    return render_template('Home.html')

if __name__=='__main__':
    # Create the report_queue
    # class of queue
    report_queue = queue.Queue()
    # Start the process_report_queue function in a separate thread
    # mult-threading
    report_thread = threading.Thread(target=process_report_queue, args=(report_queue,))
    report_thread.start()

    # Start the Flask app
    app.run(debug=True)
