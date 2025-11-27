# # Copyright (c) 2025, ERPGulf and contributors
# # For license information, please see license.txt

# # import frappe


# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data
import frappe
from frappe import _
from datetime import datetime

def execute(filters=None):
    filters = filters or {}

    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)

    return columns, data, None, chart


def get_columns():
    return [
        {"label": "Employee ID", "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 140},
        {"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 160},
        {"label": "Check-In Time", "fieldname": "check_in", "fieldtype": "Datetime", "width": 170},
        {"label": "Check-Out Time", "fieldname": "check_out", "fieldtype": "Datetime", "width": 170},
        {"label": "Working Hours", "fieldname": "working_hours", "fieldtype": "Float", "width": 130},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 100},
        {"label": "Department", "fieldname": "department", "fieldtype": "Link", "options": "Department", "width": 150},
        {"label": "Device ID", "fieldname": "device_id", "fieldtype": "Data", "width": 120},
    ]


def get_data(filters):
    sql = """
        SELECT 
            ec.employee,
            ec.employee_name,
            ec.device_id,
            ec.log_type,
            ec.time,
            ec.name
        FROM `tabEmployee Checkin` ec
        ORDER BY ec.employee, ec.time
    """

    raw = frappe.db.sql(sql, as_dict=True)

    data = []
    employee_logs = {}

    # Group by employee & date
    for row in raw:
        key = (row.employee, row.time.date())

        if key not in employee_logs:
            employee_logs[key] = {"IN": None, "OUT": None, "meta": row}

        employee_logs[key][row.log_type] = row.time

    for (employee, log_date), logs in employee_logs.items():
        emp_doc = frappe.db.get_value("Employee", employee, ["department"], as_dict=True)

        check_in = logs["IN"]
        check_out = logs["OUT"]

        working_hours = ""
        status = ""

        if check_in and check_out:
            diff = check_out - check_in
            working_hours = round(diff.total_seconds() / 3600, 2)
            status = "Present"

        data.append({
            "employee": employee,
            "employee_name": logs["meta"].employee_name,
            "device_id": logs["meta"].device_id,
            "check_in": check_in,
            "check_out": check_out,
            "working_hours": working_hours,
            "status": status,
            "department": emp_doc.department if emp_doc else "",
        })

    return data


def get_chart(data):
    labels = [d["employee"] for d in data]
    hours = [d["working_hours"] or 0 for d in data]

    return {
        "data": {
            "labels": labels,
            "datasets": [{
                "name": "Working Hours",
                "values": hours
            }]
        },
        "type": "bar",
        "colors": ["#23a9f2"],
    }
