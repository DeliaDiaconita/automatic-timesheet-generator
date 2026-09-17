import calendar
from datetime import date
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from io import BytesIO

months = {
    1: "Ianuarie",
    2: "Februarie",
    3: "Martie",
    4: "Aprilie",
    5: "Mai",
    6: "Iunie",
    7: "Iulie",
    8: "August",
    9: "Septembrie",
    10: "Octombrie",
    11: "Noiembrie",
    12: "Decembrie",
}


def get_days_in_month(year, month):
    # daca era [0] imi dadea startul rangeului adica 1
    days = calendar.monthrange(year, month)[1]
    return days


# .weekday() returneaza un nr de la 0 la 6
def is_weekend(current_date):
    return current_date.weekday() >= 5


def is_school_holiday(current_date, school_holidays):
    for holiday in school_holidays:
        if holiday["start_date"] <= current_date <= holiday["end_date"]:
            return True
    return False


# folosim get pt ca daca nu gaseste niciun concediu returneaza lista goala
def is_employee_leave(employee_id, current_date, employee_leaves):
    # employee_id e ce caut si [] e ce vreau sa primesc daca nu exista niciun id
    leaves = employee_leaves.get(employee_id, [])

    for leave in leaves:
        if leave["start_date"] <= current_date <= leave["end_date"]:
            return leave["leave_type"]
    return None


def generate_timesheets(year, month, employees, school_holidays, employee_leaves):
    days = get_days_in_month(year, month)
    timesheets = []

    for employee in employees:
        daily_values = []
        total_days = 0
        leave_days = 0

        for day in range(1, days + 1):
            current_date = date(year, month, day)

            if (
                is_weekend(current_date)
                or is_school_holiday(current_date, school_holidays)
                or current_date.weekday() not in employee["workdays"]
            ):
                daily_values.append("X")
            else:
                leave_type = is_employee_leave(
                    employee["id"],
                    current_date,
                    employee_leaves,
                )
                if leave_type:
                    daily_values.append(leave_type)

                    if leave_type == "CO":
                        leave_days += 1
                else:
                    daily_values.append(employee["hours_per_day"])
                    total_days += 1

        timesheets.append(
            {
                "name": employee["name"],
                "hours_per_day": employee["hours_per_day"],
                "start_time": employee["start_time"],
                "end_time": employee["end_time"],
                "workdays": employee["workdays"],
                "days": daily_values,
                "total_days": total_days,
                "total_hours": employee["hours_per_day"] * total_days,
                "leave_days": leave_days,
            }
        )

    return timesheets


def generate_excel(timesheets, year, month, company_name):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = f"Pontaj {months[month]}"

    days = get_days_in_month(year, month)

    # Coloanele fixe
    first_day_column = 6  # coloana F
    last_day_column = first_day_column + days - 1

    total_hours_column = last_day_column + 1
    total_days_column = last_day_column + 2
    leave_days_column = last_day_column + 3

    last_table_letter = get_column_letter(leave_days_column)

    # Stiluri
    thin_side = Side(style="thin", color="000000")

    thin_border = Border(
        left=thin_side,
        right=thin_side,
        top=thin_side,
        bottom=thin_side,
    )

    grey_fill = PatternFill(
        fill_type="solid",
        fgColor="C0C0C0",
    )

    normal_font = Font(
        name="Arial",
        size=10,
    )

    bold_font = Font(
        name="Arial",
        size=10,
        bold=True,
    )

    red_font = Font(
        name="Arial",
        size=10,
        color="FF0000",
    )

    blue_font = Font(
        name="Arial",
        size=10,
        color="0066CC",
    )

    centered = Alignment(
        horizontal="center",
        vertical="center",
    )

    centered_wrapped = Alignment(
        horizontal="center",
        vertical="center",
        wrap_text=True,
    )

    # Tipurile de concediu / absență
    leave_codes = {
        "CO",
        "CM",
        "CFP",
        "N",
        "CIC",
    }

    # Titlul firmei
    sheet["A1"] = company_name.upper()
    sheet["A1"].font = bold_font

    # Titlul pontajului
    sheet.merge_cells(
        start_row=2,
        start_column=2,
        end_row=2,
        end_column=last_day_column,
    )

    sheet["B2"] = "FOAIE COLECTIVĂ DE PREZENȚĂ"
    sheet["B2"].font = Font(
        name="Arial",
        size=14,
    )
    sheet["B2"].alignment = centered

    # Luna și anul
    sheet["A3"] = "Luna"
    sheet["B3"] = months[month]

    sheet["A4"] = "Anul:"
    sheet["B4"] = year

    for address in ("A3", "B3", "A4", "B4"):
        sheet[address].font = bold_font

    # Antetul tabelului
    sheet.merge_cells("A5:A6")
    sheet.merge_cells("B5:B6")

    sheet.merge_cells(
        start_row=5,
        start_column=3,
        end_row=5,
        end_column=last_day_column,
    )

    sheet.merge_cells(
        start_row=5,
        start_column=total_hours_column,
        end_row=6,
        end_column=total_hours_column,
    )

    sheet.merge_cells(
        start_row=5,
        start_column=total_days_column,
        end_row=6,
        end_column=total_days_column,
    )

    sheet.merge_cells(
        start_row=5,
        start_column=leave_days_column,
        end_row=6,
        end_column=leave_days_column,
    )

    sheet["A5"] = "Nr. crt."
    sheet["B5"] = "Nume și prenume angajat"

    sheet["C6"] = "ore/zi"
    sheet["D6"] = "Ora începere program"
    sheet["E6"] = "Ora sfârșit program"

    # Zilele lunii
    for day in range(1, days + 1):
        column_number = first_day_column + day - 1
        sheet.cell(
            row=6,
            column=column_number,
            value=day,
        )

    sheet.cell(
        row=5,
        column=total_hours_column,
        value="Nr. ore",
    )

    sheet.cell(
        row=5,
        column=total_days_column,
        value="Nr. zile",
    )

    sheet.cell(
        row=5,
        column=leave_days_column,
        value="Nr. zile CO",
    )

    # Formatarea antetului
    for row_number in range(5, 7):
        for column_number in range(1, leave_days_column + 1):
            cell = sheet.cell(
                row=row_number,
                column=column_number,
            )

            cell.border = thin_border
            cell.font = bold_font
            cell.alignment = centered_wrapped

    sheet.row_dimensions[6].height = 48

    # Angajații încep pe rândul 7
    first_employee_row = 7

    for index, timesheet in enumerate(timesheets, start=1):
        row_number = first_employee_row + index - 1

        day_values = list(timesheet["days"][:days])

        # Completează lista dacă are mai puține elemente
        if len(day_values) < days:
            day_values.extend([""] * (days - len(day_values)))

        # Nr. crt.
        sheet.cell(
            row=row_number,
            column=1,
            value=index,
        )

        # Nume angajat
        sheet.cell(
            row=row_number,
            column=2,
            value=timesheet["name"],
        )

        # Ore pe zi
        sheet.cell(
            row=row_number,
            column=3,
            value=timesheet.get("hours_per_day", ""),
        )

        # Ora început
        sheet.cell(
            row=row_number,
            column=4,
            value=timesheet.get("start_time", ""),
        )

        # Ora sfârșit
        sheet.cell(
            row=row_number,
            column=5,
            value=timesheet.get("end_time", ""),
        )

        # Formatarea întregului rând
        for column_number in range(1, leave_days_column + 1):
            cell = sheet.cell(
                row=row_number,
                column=column_number,
            )

            cell.border = thin_border
            cell.font = normal_font
            cell.alignment = centered

        # Numele angajatului
        name_cell = sheet.cell(
            row=row_number,
            column=2,
        )

        name_cell.font = bold_font
        name_cell.alignment = Alignment(
            horizontal="left",
            vertical="center",
        )

        # Fundal gri pentru ore/zi și program
        for column_number in range(3, 6):
            cell = sheet.cell(
                row=row_number,
                column=column_number,
            )

            cell.fill = grey_fill
            cell.font = bold_font

        # Orele, X sau tipul de concediu pentru fiecare zi
        for day_index, value in enumerate(day_values):
            column_number = first_day_column + day_index

            cell = sheet.cell(
                row=row_number,
                column=column_number,
                value=value,
            )

            # X cu roșu
            if value == "X":
                cell.font = red_font

            # Tipurile de concediu / absență cu albastru
            elif value in leave_codes:
                cell.font = blue_font

        # Total ore
        sheet.cell(
            row=row_number,
            column=total_hours_column,
            value=timesheet["total_hours"],
        )

        # Total zile lucrate
        sheet.cell(
            row=row_number,
            column=total_days_column,
            value=timesheet["total_days"],
        )

        # Numără doar zilele CO
        leave_days = sum(1 for value in day_values if value == "CO")

        sheet.cell(
            row=row_number,
            column=leave_days_column,
            value=leave_days,
        )

        # Totalurile cu bold
        for column_number in (
            total_hours_column,
            total_days_column,
            leave_days_column,
        ):
            sheet.cell(
                row=row_number,
                column=column_number,
            ).font = bold_font

    # Legenda
    last_employee_row = first_employee_row + len(timesheets) - 1
    legend_start_row = last_employee_row + 2

    legend = [
        ("CM", "concediu medical"),
        ("CO", "concediu de odihnă"),
        ("CFP", "concediu fără plată"),
        ("N", "nemotivat"),
        ("CIC", "concediu îngrijire copil"),
    ]

    for offset, (code, explanation) in enumerate(legend):
        row_number = legend_start_row + offset

        sheet.cell(
            row=row_number,
            column=1,
            value=code,
        )

        sheet.cell(
            row=row_number,
            column=2,
            value=explanation,
        )

        for column_number in (1, 2):
            cell = sheet.cell(
                row=row_number,
                column=column_number,
            )

            cell.border = thin_border
            cell.font = Font(
                name="Arial",
                size=10,
                bold=True,
                color="0066CC",
            )

    # Zona pentru semnătură
    prepared_column = min(
        last_day_column,
        first_day_column + 18,
    )

    sheet.cell(
        row=legend_start_row + 1,
        column=prepared_column,
        value="Întocmit,",
    )

    # Lățimea coloanelor
    sheet.column_dimensions["A"].width = 6
    sheet.column_dimensions["B"].width = 32
    sheet.column_dimensions["C"].width = 8
    sheet.column_dimensions["D"].width = 12
    sheet.column_dimensions["E"].width = 12

    for column_number in range(
        first_day_column,
        last_day_column + 1,
    ):
        column_letter = get_column_letter(column_number)
        sheet.column_dimensions[column_letter].width = 4

    for column_number in (
        total_hours_column,
        total_days_column,
        leave_days_column,
    ):
        column_letter = get_column_letter(column_number)
        sheet.column_dimensions[column_letter].width = 10

    # Setări pentru afișare și tipărire
    sheet.freeze_panes = "D7"
    sheet.sheet_view.showGridLines = False

    sheet.page_setup.orientation = "landscape"
    sheet.page_setup.paperSize = sheet.PAPERSIZE_A4
    sheet.page_setup.fitToWidth = 1
    sheet.page_setup.fitToHeight = 0

    sheet.sheet_properties.pageSetUpPr.fitToPage = True

    sheet.print_area = f"A1:{last_table_letter}" f"{legend_start_row + len(legend) - 1}"

    excel_file = BytesIO()
    workbook.save(excel_file)
    excel_file.seek(0)

    return excel_file
