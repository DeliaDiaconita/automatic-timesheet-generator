import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, timedelta

from database import (
    create_database,
    add_company,
    get_companies,
    add_employee,
    get_employees,
    update_employee,
    add_leave,
    get_leaves,
    delete_leave,
    delete_employee,
    delete_company,
    add_school_holiday,
    get_school_holidays,
    delete_school_holiday,
)

from main import generate_timesheets, generate_excel


def clear_generated_timesheet():
    if "timesheets" in st.session_state:
        del st.session_state["timesheets"]


@st.dialog("Confirma stergerea")
def confirm_delete_employee(employee):
    st.write(f"Sigur vrei sa elimini angajatul {employee['name']} ?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Da, elimina"):
            delete_employee(employee["id"])
            clear_generated_timesheet()
            st.rerun()
    with col2:
        if st.button("Anuleaza"):
            st.rerun()


@st.dialog("Confirma stergerea")
def confirm_delete_company(company_id, company_name):
    st.write(f"Sigur vrei sa elimini firma {company_name} ?")
    st.warning("Vor fi eliminati si angajatii firmei")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Da, elimina"):
            delete_company(company_id)
            clear_generated_timesheet()
            st.rerun()

    with col2:
        if st.button("Anuleaza"):
            st.rerun()


create_database()

st.set_page_config(
    page_title="Pontaj",
    layout="wide",
)

st.title("Pontaj")
st.caption("Generator automat de pontaj")


st.markdown("## Vacanțe an școlar curent")

with st.container(border=True):

    st.markdown("#### Adaugă vacanță")

    col1, col2 = st.columns(2)

    with col1:
        school_holiday_start = st.date_input(
            "Prima zi de vacanta",
            key="school_holiday_start",
        )
    with col2:
        school_holiday_end = st.date_input(
            "Ultima zi de vacanță",
            key="school_holiday_end",
        )

    if st.button(
        "Adauga vacanta",
        use_container_width=True,
    ):
        if school_holiday_start <= school_holiday_end:
            add_school_holiday(
                # transforma formatul datei in unul agreat de sql
                school_holiday_start.isoformat(),
                school_holiday_end.isoformat(),
            )
            clear_generated_timesheet()
            st.rerun()
        else:
            st.error("Data de început trebuie să fie înaintea datei de sfârșit.")


st.markdown("#### Vacanțe introduse")

school_holidays = get_school_holidays()

if not school_holidays:
    st.write("Nu exista vacante introduse")

for holiday in school_holidays:
    col1, col2 = st.columns([5, 1])

    with col1:
        st.write(
            f"{holiday['start_date'].strftime('%d.%m.%Y')} - "
            f"{holiday['end_date'].strftime('%d.%m.%Y')}"
        )

    with col2:
        if st.button(
            "Elimina",
            key=f"delete_school_holiday_{holiday['id']}",
        ):
            delete_school_holiday(holiday["id"])
            clear_generated_timesheet()
            st.rerun()


st.divider()

st.markdown("## Firme")

companies = get_companies()

# company returneaza (id, nume), de aceea folosim company[1]
company_names = [company[1] for company in companies]
company_names.append("➕ Adaugă firmă")

# Lista dropdown cu firmele
selected_company = st.selectbox(
    "Selecteaza firma",
    company_names,
)


if selected_company == "➕ Adaugă firmă":
    new_company_name = st.text_input("Numele firmei")

    if st.button("Salveaza firma"):

        new_company_name = new_company_name.strip()

        existing_company_names = [company[1].strip().lower() for company in companies]

        if not new_company_name:
            st.error("Introdu numele firmei.")
        elif new_company_name.lower() in existing_company_names:
            st.error("Firma există deja.")
        else:
            add_company(new_company_name)
            st.success("Firma a fost adaugata")
            clear_generated_timesheet()
            # Reincarca pagina pentru ca noua firma sa apara in dropdown
            st.rerun()

else:
    selected_company_id = None

    for company in companies:
        if company[1] == selected_company:
            selected_company_id = company[0]
            break

    if st.button(
        "Elimina firma",
        key=f"delete_company_{selected_company_id}",
    ):
        confirm_delete_company(selected_company_id, selected_company)

    st.subheader("Angajati")

    if st.session_state.get("employee_updated"):
        st.success("Modificarile au fost salvate")
        st.session_state["employee_updated"] = False

    employees = get_employees(selected_company_id)

    employee_names = [employee["name"] for employee in employees]
    employee_names.append("➕ Adaugă angajat")

    selected_employee_name = st.selectbox(
        "Selecteaza angajatul",
        employee_names,
    )

    if selected_employee_name == "➕ Adaugă angajat":
        new_employee_name = st.text_input("Numele angajatului")

        new_hours = st.number_input(
            "Ore lucrate pe zi",
            min_value=1,
            max_value=12,
            value=8,
        )

        new_start_time = st.time_input("Ora inceput program")
        new_end_time = (
            datetime.combine(
                datetime.today().date(),
                new_start_time,
            )
            + timedelta(hours=new_hours)
        ).time()

        st.text_input(
            "Ora sfârșit program",
            value=new_end_time.strftime("%H:%M"),
            disabled=True,
        )
        weekdays = {
            "Luni": 0,
            "Marți": 1,
            "Miercuri": 2,
            "Joi": 3,
            "Vineri": 4,
        }

        selected_days = st.multiselect("Zile lucratoare", options=list(weekdays.keys()))

        selected_workdays = [weekdays[day] for day in selected_days]

        if st.button("Salveaza angajatul"):

            new_employee_name = new_employee_name.strip()

            existing_employee_names = [
                employee["name"].strip().lower() for employee in employees
            ]
            # strip elimina spatiile de la inceputul si sfarsitul unui string
            if not new_employee_name.strip():
                st.error("Introdu numele angajatului")
            elif new_employee_name.lower() in existing_employee_names:
                st.error("Angajatul există deja în această firmă.")
            elif not selected_workdays:
                st.error("Selecteaza cel putin o zi lucratoare")
            elif new_end_time <= new_start_time:
                st.error("Ora de sfarsiot trebuie sa fie dupa ora de inceput")
            else:
                add_employee(
                    selected_company_id,
                    new_employee_name.strip(),
                    new_hours,
                    new_start_time.strftime("%H:%M"),
                    new_end_time.strftime("%H:%M"),
                    selected_workdays,
                )

                st.success("Angajatul a fost adaugat")
                clear_generated_timesheet()
                st.rerun()

    else:
        selected_employee = None

        for employee in employees:
            if selected_employee_name == employee["name"]:
                selected_employee = employee
                break

        if selected_employee is not None:

            with st.container(border=True):

                st.markdown("#### Date angajat")

                employee_name = st.text_input(
                    "Nume",
                    value=selected_employee["name"],
                    key=f"name_{selected_employee['id']}",
                )
                col1, col2, col3 = st.columns(3)

                with col1:
                    hours_per_day = st.number_input(
                        "Ore lucrate pe zi",
                        min_value=1,
                        max_value=12,
                        value=selected_employee["hours_per_day"],
                        key=f"hours_{selected_employee['id']}",
                    )
                with col2:
                    start_time = st.time_input(
                        "Ora inceput program",
                        value=datetime.strptime(
                            selected_employee["start_time"],
                            "%H:%M",
                        ).time(),
                        key=f"start_{selected_employee['id']}",
                    )
                with col3:
                    end_time = (
                        datetime.combine(
                            datetime.today().date(),
                            start_time,
                        )
                        + timedelta(hours=hours_per_day)
                    ).time()

                    st.text_input(
                        "Ora sfârșit program",
                        value=end_time.strftime("%H:%M"),
                        disabled=True,
                    )

                weekdays = {
                    "Luni": 0,
                    "Marți": 1,
                    "Miercuri": 2,
                    "Joi": 3,
                    "Vineri": 4,
                }
                # face o losta cu zilele care sunt in programul angajatului
                current_days = [
                    day_name
                    for day_name, day_number in weekdays.items()
                    if day_number in selected_employee["workdays"]
                ]

                selected_days = st.multiselect(
                    "Zile lucratoare",
                    options=list(weekdays.keys()),
                    default=current_days,
                    key=f"days_{selected_employee['id']}",
                )

                selected_workdays = [weekdays[day] for day in selected_days]

                col_save, col_delete = st.columns(2)

                with col_save:

                    if st.button(
                        "Salveaza modificarea",
                        key=f"save_employee_{selected_employee['id']}",
                        use_container_width=True,
                    ):
                        if not selected_workdays:
                            st.error("Selectează cel puțin o zi lucrătoare.")
                        elif end_time <= start_time:
                            st.error(
                                "Ora de sfârșit trebuie să fie după ora de început."
                            )
                        else:
                            update_employee(
                                selected_employee["id"],
                                hours_per_day,
                                start_time.strftime("%H:%M"),
                                end_time.strftime("%H:%M"),
                                selected_workdays,
                            )

                            st.session_state["employee_updated"] = True
                            clear_generated_timesheet()
                            st.rerun()

                with col_delete:
                    if st.button(
                        "Elimină angajat",
                        key=f"delete_employee_{selected_employee['id']}",
                        use_container_width=True,
                    ):
                        confirm_delete_employee(selected_employee)

            with st.container(border=True):

                st.markdown("#### Adauga concediu")

                leave_options = {
                    "Concediu de odihnă": "CO",
                    "Concediu medical": "CM",
                    "Concediu fără plată": "CFP",
                    "Nemotivat": "N",
                    "Concediu îngrijire copil": "CIC",
                }

                leave_label = st.selectbox(
                    "Tip concediu",
                    list(leave_options.keys()),
                    key=f"leave_type_{selected_employee['id']}",
                )

                leave_type = leave_options[leave_label]

                col1, col2 = st.columns(2)

                with col1:
                    start_date = st.date_input(
                        "Prima zi de concediu",
                        key=f"leave_start_{selected_employee['id']}",
                    )
                with col2:
                    end_date = st.date_input(
                        "Ultima zi de concediu",
                        key=f"leave_end_{selected_employee['id']}",
                    )

                if st.button(
                    "Adauga concediu",
                    key=f"add_leave_{selected_employee['id']}",
                    use_container_width=True,
                ):
                    if start_date <= end_date:
                        add_leave(
                            selected_employee["id"],
                            start_date.isoformat(),
                            end_date.isoformat(),
                            leave_type,
                        )
                        st.success("Concediu salvat")
                        clear_generated_timesheet()

                    else:
                        st.error(
                            "Data de inceput trebuie sa fie inaintea datei de sfarsit"
                        )

            st.markdown("#### Concedii introduse")

            leaves = get_leaves(selected_employee["id"])

            for leave in leaves:
                col1, col2 = st.columns([4, 1])

                with col1:
                    st.write(
                        f"{leave['leave_type']} | "
                        f"{leave['start_date'].strftime('%d.%m.%Y')} - "
                        f"{leave['end_date'].strftime('%d.%m.%Y')}"
                    )

                with col2:
                    if st.button(
                        "Sterege",
                        key=f"delete_leave_{leave['id']}",
                    ):
                        delete_leave(leave["id"])
                        clear_generated_timesheet()
                        st.rerun()

    st.divider()

    st.markdown("## Genereaza pontaj")

    with st.container(border=True):
        col1, col2 = st.columns(2)
        months = {
            "Ianuarie": 1,
            "Februarie": 2,
            "Martie": 3,
            "Aprilie": 4,
            "Mai": 5,
            "Iunie": 6,
            "Iulie": 7,
            "August": 8,
            "Septembrie": 9,
            "Octombrie": 10,
            "Noiembrie": 11,
            "Decembrie": 12,
        }
        with col1:
            selected_month_name = st.selectbox(
                "Luna",
                months.keys(),
            )
        with col2:
            selected_year = st.number_input(
                "Anul", min_value=2026, max_value=2100, value=2026, step=1
            )
        selected_month = months[selected_month_name]

        if st.button("Genereaza pontaj", use_container_width=True):
            if not employees:
                st.error("Firma selectata nu are angajati")
            else:
                employee_leaves = {}

                for employee in employees:
                    employee_leaves[employee["id"]] = get_leaves(employee["id"])

                school_holidays = get_school_holidays()

                timesheets = generate_timesheets(
                    selected_year,
                    selected_month,
                    employees,
                    school_holidays,
                    employee_leaves,
                )

                st.session_state["timesheets"] = timesheets
                st.session_state["selected_year"] = selected_year
                st.session_state["selected_month"] = selected_month
                st.session_state["selected_month_name"] = selected_month_name
                st.session_state["selected_company_name"] = selected_company
                st.session_state["selected_company_id"] = selected_company_id

    if (
        "timesheets" in st.session_state
        and st.session_state["selected_company_id"] == selected_company_id
        and st.session_state["selected_year"] == selected_year
        and st.session_state["selected_month"] == selected_month
    ):
        timesheets = st.session_state["timesheets"]

        selected_year = st.session_state["selected_year"]
        selected_month = st.session_state["selected_month"]
        selected_month_name = st.session_state["selected_month_name"]
        selected_company_name = st.session_state["selected_company_name"]

        preview_rows = []

        for index, timesheet in enumerate(timesheets, start=1):
            row = {
                "Nr. crt.": index,
                "Angajat": timesheet["name"],
                "ore/zi": timesheet["hours_per_day"],
                "Ora începere program": timesheet.get(
                    "start_time",
                    "",
                ),
                "Ora sfârșit program": timesheet.get(
                    "end_time",
                    "",
                ),
            }

            for day_number, value in enumerate(timesheet["days"], start=1):
                row[str(day_number)] = value

            row["Total zile"] = timesheet["total_days"]
            row["Total ore"] = timesheet["total_hours"]

            row["Nr. zile CO"] = sum(1 for value in timesheet["days"] if value == "CO")

            preview_rows.append(row)
        # afiseaza dictionarul ca tabel
        if preview_rows:
            columns = preview_rows[0].keys()

            leave_codes = {
                "CO",
                "CM",
                "CFP",
                "N",
                "CIC",
            }

            html = '<div style="overflow-x: auto;">'
            html += '<table style="border-collapse: collapse; width: max-content; font-size: 14px;">'
            html += "<tr>"

            # antet
            for column in columns:
                html += f"""
                <th style="border: 1px solid #ccc;
                padding: 6px;
                background-color: #f2f2f2;
                white-space: nowrap;">
                {column}
                </th>
                """

            html += "</tr>"

            # randurile angajatilor
            for row in preview_rows:
                html += "<tr>"

                for column in columns:
                    value = row[column]

                    if value == "X":
                        text_color = "red"

                    elif value in leave_codes:
                        text_color = "#0066CC"
                    else:
                        text_color = "black"

                    html += (
                        '<td style="'
                        "border: 1px solid #ccc; "
                        "padding: 6px; "
                        "text-align: center; "
                        "white-space: nowrap; "
                        f'color: {text_color};">'
                        f"{value}"
                        "</td>"
                    )

                html += "</tr>"

            html += "</table>"
            html += "</div>"

            components.html(
                html,
                height=100,
                scrolling=True,
            )

        excel_file = generate_excel(
            timesheets,
            selected_year,
            selected_month,
            selected_company_name,
        )
        st.download_button(
            label="Salveaza ca Excel",
            # fisierul propriu zis de descarcat
            data=excel_file,
            file_name=f"Pontaj_{selected_month_name}_{selected_year}.xlsx",
            # ii spune browserului ce fisier descarca
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
