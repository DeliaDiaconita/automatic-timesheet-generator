# Automatic Timesheet Generator

A Python and Streamlit application for creating monthly employee timesheets and exporting them to formatted Excel files.

The application was built around a real administrative workflow and automates the calculation of working days, employee schedules, holidays and different types of employee leave.

## Features

- Manage multiple companies
- Add, edit and delete employees
- Configure individual employee schedules:
  - working hours per day
  - start time
  - end time
  - selected working days from Monday to Friday
- Configure school holiday periods manually
- Add and remove employee leave periods
- Support multiple absence types:
  - `CO` – Annual leave
  - `CM` – Medical leave
  - `CFP` – Unpaid leave
  - `N` – Unexcused absence
  - `CIC` – Childcare leave
- Automatically identify:
  - weekends
  - school holidays
  - employee non-working days
  - leave periods
- Automatically calculate:
  - total working days
  - total working hours
  - number of annual leave days (`CO`)
- Preview the generated timesheet directly in the application
- Export the final timesheet to a formatted Excel file
- Store company, employee and leave data locally using SQLite

## Timesheet Logic

For every day of the selected month, the application determines the correct value automatically.

Possible values are:

- working hours – when the employee is scheduled to work
- `X` – weekend, school holiday or non-working weekday
- `CO` – annual leave
- `CM` – medical leave
- `CFP` – unpaid leave
- `N` – unexcused absence
- `CIC` – childcare leave

Only regular working days are included in the total number of worked days and working hours.

The `Nr. zile CO` field counts only annual leave days marked with `CO`.

## Excel Export

The generated Excel document includes:

- company name
- month and year
- employee name
- working hours per day
- start and end time
- one column for every calendar day
- total working hours
- total working days
- total annual leave days
- absence legend

For easier reading:

- `X` values are displayed in red
- employee absence codes are displayed in blue

The Excel document is formatted for landscape A4 printing.

## Technologies

- Python
- Streamlit
- SQLite
- OpenPyXL
- HTML/CSS

## Project Structure

```text
timesheet/
│
├── app.py
├── database.py
├── main.py
│
├── docs/
│   ├── screenshot-1-holidays.png
│   ├── screenshot-2-employee-schedule.png
│   ├── screenshot-3-leave-management.png
│   ├── screenshot-4-timesheet-preview.png
│   └── screenshot-5-excel-output.png
│
├── requirements.txt
├── .gitignore
└── README.md
```

## Screenshots


### School Holiday Management

School holiday periods can be added and removed manually, allowing the timesheet generator to automatically exclude non-working school days.

![School holiday management](docs/screenshot-1-holidays.png)

### Employee Schedule Management

Each employee can have individual working days and daily hours, while the end time is calculated automatically from the selected start time and number of working hours.

![Employee schedule management](docs/screenshot-2-employee-schedule.png)

### Leave and Absence Management

Leave periods can be added per employee using predefined absence types such as annual leave, medical leave, unpaid leave, unexcused absence and childcare leave.

![Leave and absence management](docs/screenshot-3-leave-management.png)


### Timesheet Generation and Preview

The application generates the monthly timesheet automatically, applies working-day and leave rules, calculates totals, and provides an on-screen preview before Excel export.

![Timesheet generation and preview](docs/screenshot-4-timesheet-preview.png)

### Excel Export

The generated timesheet is exported to a formatted Excel file containing employee schedules, daily attendance values, working-day totals, annual leave totals and an absence-code legend.

![Generated Excel timesheet](docs/screenshot-5-excel-output.png)


### Holiday and Company Management

The application allows school holiday periods to be configured manually and supports multiple companies.

![Holiday and company management](docs/screenshot-1.png)

### Employee Management

Employees can have individual working hours, schedules and selected working days.

![Employee management](docs/screenshot-2.png)

### Timesheet Generation

The monthly timesheet is generated automatically and can be previewed directly in the Streamlit application.

![Timesheet generation](docs/screenshot-3.png)

### Generated Excel Timesheet

The final result can be exported as a formatted Excel attendance sheet.

![Generated Excel timesheet](docs/screenshot-4.png)

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd timesheet
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

## Running the Application

Start the Streamlit application with:

```bash
streamlit run app.py
```

The application will open in your browser.

## How to Use

1. Add the school holiday periods.
2. Create or select a company.
3. Add employees.
4. Configure each employee's:
   - working hours
   - start and end time
   - working weekdays
5. Add employee leave periods when necessary.
6. Select the leave or absence type.
7. Choose the month and year.
8. Generate the timesheet.
9. Review the preview.
10. Export the result to Excel.

## Data Storage

The application uses SQLite for local data storage.

The database stores:

- companies
- employees
- employee working days
- employee leave periods and absence types
- school holiday periods

Foreign key relationships are used to keep employee and company data consistent.

## Project Purpose

This project was developed as a practical Python automation project based on a real business requirement.

It demonstrates the use of Python for:

- business process automation
- relational database management
- calendar and date logic
- employee schedule management
- dynamic web interfaces
- Excel file generation and formatting
- persistent local data storage


