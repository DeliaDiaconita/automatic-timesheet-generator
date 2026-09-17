import sqlite3
from datetime import date
from pathlib import Path

DB_PATH = Path(__file__).parent / "timesheet.db"


def create_database():
    # creaza(daca nu exista) sau deschide baze de date
    connection = sqlite3.connect(DB_PATH)
    # Activează relațiile dintre tabele
    connection.execute("PRAGMA foreign_keys = ON")
    # cursorul trimite comenzi SQL catre baza de date
    # CREATE TABLE IF NOT EXISTS companies = daca nu exista tabelul fa l si numste l companies
    # id INTEGER PRIMARY KEY AUTOINCREMENT=  fiecare firma e numerotata unic crescator
    # name TEXT NOT NULL= adica coloana nume e obligatoriu de completat
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
        """)
    # FOREIGN KEY (company_id) REFERENCES companies(id)=arata relatia dintre cele 2 tabele
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        hours_per_day INTEGER NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL,
        FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
    )
    """)

    # Fiecare rand leaga un angajat de o zi a saptamanii
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employee_workdays (
            employee_id INTEGER NOT NULL,
            weekday INTEGER NOT NULL
                CHECK (weekday BETWEEN 0 AND 4),

            PRIMARY KEY (employee_id, weekday),

            FOREIGN KEY (employee_id)
                REFERENCES employees(id)
                ON DELETE CASCADE
        )
        """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leaves (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        leave_type TEXT NOT NULL DEFAULT 'CO'
            CHECK (leave_type IN ('CO', 'CM', 'CFP', 'N', 'CIC')),
        FOREIGN KEY (employee_id) REFERENCES employees(id)
    )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS  school_holidays(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL
            )
        """)

    connection.commit()
    connection.close()


def add_company(name):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    # INSERT INTO companies (name) VALUES (?) = adaugam un rand in tabelul companies
    # ? = placeholder
    # (name,)= tuple cu un singur elem , reprez valoare pusa in locul lui ?
    # folosim tuple pt ca cursor. execute vrea minim 2 val pt a inlocui ?, si noi avem doar una
    cursor.execute(
        "INSERT INTO companies (name) VALUES (?)",
        (name,),
    )
    connection.commit()
    connection.close()


def get_companies():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM companies")
    companies = cursor.fetchall()
    connection.close()
    return companies


def add_employee(company_id, name, hours_per_day, start_time, end_time, workdays):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    # trimite valorile ca parametru pt a putea fi inlocuite in tabel
    cursor.execute(
        """
        INSERT INTO employees (company_id, name, hours_per_day, start_time, end_time)
        VALUES (?, ?, ?, ?, ?)
        """,
        (company_id, name, hours_per_day, start_time, end_time),
    )

    employee_id = cursor.lastrowid

    for weekday in workdays:
        cursor.execute(
            """
            INSERT INTO employee_workdays (
                employee_id,
                weekday
            )
            VALUES (?,?)
            """,
            (employee_id, weekday),
        )

    connection.commit()
    connection.close()


def get_employees(company_id):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM employees WHERE company_id = ?", (company_id,))
    rows = cursor.fetchall()
    employees = []
    for row in rows:

        employee_id = row[0]

        cursor.execute(
            """
            SELECT weekday
            FROM employee_workdays
            WHERE employee_id = ?
            ORDER BY weekday
            """,
            (employee_id,),
        )

        workdays_rows = cursor.fetchall()

        workdays = [workday[0] for workday in workdays_rows]

        employees.append(
            {
                "id": row[0],
                "company_id": row[1],
                "name": row[2],
                "hours_per_day": row[3],
                "start_time": row[4],
                "end_time": row[5],
                "workdays": workdays,
            }
        )
    connection.close()

    return employees


def add_leave(employee_id, start_date, end_date, leave_type):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO leaves (employee_id, start_date, end_date,leave_type)
        VALUES (?, ?, ?, ?)
        """,
        (employee_id, start_date, end_date, leave_type),
    )

    connection.commit()
    connection.close()


def get_leaves(employee_id):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT id, start_date,end_date, leave_type
        FROM leaves
        WHERE employee_id = ?
        """,
        (employee_id,),
    )

    rows = cursor.fetchall()
    connection.close()

    leaves = []
    for row in rows:
        leaves.append(
            {
                "id": row[0],
                "start_date": date.fromisoformat(row[1]),
                "end_date": date.fromisoformat(row[2]),
                "leave_type": row[3],
            }
        )

    return leaves


def update_employee(employee_id, hours_per_day, start_time, end_time, workdays):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
    UPDATE employees
    SET hours_per_day = ?,
        start_time = ?,
        end_time = ?
    WHERE id = ?
    """,
        (hours_per_day, start_time, end_time, employee_id),
    )

    cursor.execute(
        """
        DELETE FROM employee_workdays
        WHERE employee_id = ?
        """,
        (employee_id,),
    )

    for weekday in workdays:
        cursor.execute(
            """
            INSERT INTO employee_workdays(
            employee_id, weekday)
            VALUES (?, ?)
            """,
            (employee_id, weekday),
        )

    connection.commit()
    connection.close()


def delete_leave(leave_id):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM leaves WHERE id = ?",
        (leave_id,),
    )

    connection.commit()
    connection.close()


def delete_employee(employee_id):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM leaves WHERE employee_id = ?",
        (employee_id,),
    )

    cursor.execute(
        "DELETE FROM employee_workdays WHERE employee_id = ?", (employee_id,)
    )

    cursor.execute(
        "DELETE FROM employees WHERE id = ?",
        (employee_id,),
    )

    connection.commit()
    connection.close()


def delete_company(company_id):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM leaves
        WHERE employee_id IN (
            SELECT id
            FROM employees
            WHERE company_id = ?
        )
        """,
        (company_id,),
    )

    cursor.execute(
        "DELETE FROM employees WHERE company_id = ?",
        (company_id,),
    )

    cursor.execute(
        "DELETE FROM companies WHERE id = ?",
        (company_id,),
    )

    connection.commit()
    connection.close()


def add_school_holiday(start_date, end_date):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO school_holidays (start_date, end_date)
        VALUES ( ?,? )
        """,
        (start_date, end_date),
    )

    connection.commit()
    connection.close()


def get_school_holidays():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id,start_date,end_date
        FROM school_holidays
        ORDER BY start_date
        """)

    rows = cursor.fetchall()
    connection.close()

    holidays = []

    for row in rows:
        holidays.append(
            {
                "id": row[0],
                "start_date": date.fromisoformat(row[1]),
                "end_date": date.fromisoformat(row[2]),
            }
        )

    return holidays


def delete_school_holiday(holiday_id):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM school_holidays WHERE id = ?",
        (holiday_id,),
    )

    connection.commit()
    connection.close()
