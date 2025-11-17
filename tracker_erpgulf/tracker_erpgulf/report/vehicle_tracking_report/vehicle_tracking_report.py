# Copyright (c) 2025, ERPGulf and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate

def execute(filters=None):
    """
    Execute function for Vehicle Tracking Report.
    Supports filtering by vehicle and date range.
    """
    filters = filters or {}
    vehicle = filters.get("vehicle")
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")

    # Default to today if no dates provided
    if not from_date:
        from_date = getdate()
    if not to_date:
        to_date = getdate()

    # Build SQL query
    query = """
        SELECT
            vehicle_name,
            reg_no,
            position,
            last_comm,
            duration,
            kms,
            ac AS ac_status
        FROM `tabVehicle Tracking System`
        WHERE last_comm BETWEEN %(from_date)s AND %(to_date)s
    """

    query_filters = {"from_date": f"{from_date} 00:00:00", "to_date": f"{to_date} 23:59:59"}

    if vehicle:
        query += " AND vehicle_name = %(vehicle)s"
        query_filters["vehicle"] = vehicle

    # Execute query
    data = frappe.db.sql(query, query_filters, as_dict=True)

    # Optionally, define report columns
    columns = [
        {"fieldname": "vehicle_name", "label": "Vehicle", "fieldtype": "Data", "width": 150},
        {"fieldname": "reg_no", "label": "Reg No", "fieldtype": "Data", "width": 120},
        {"fieldname": "position", "label": "Position", "fieldtype": "Data", "width": 150},
        {"fieldname": "last_comm", "label": "Last Communication", "fieldtype": "Datetime", "width": 180},
        {"fieldname": "duration", "label": "Duration", "fieldtype": "Data", "width": 120},
        {"fieldname": "kms", "label": "Kms", "fieldtype": "Float", "width": 100},
        {"fieldname": "ac_status", "label": "AC Status", "fieldtype": "Data", "width": 100},
    ]

    return columns, data
