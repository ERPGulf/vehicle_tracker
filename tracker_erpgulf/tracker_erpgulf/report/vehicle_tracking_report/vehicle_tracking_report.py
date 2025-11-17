import frappe
from frappe.utils import getdate

def execute(filters=None):
    """
    Vehicle Tracking Report
    Supports filtering by vehicle and date range.
    Includes: speed, status, position, expiry_date, gmap, is_over_speed
    """
    filters = filters or {}
    vehicle = filters.get("vehicle")
    from_date = filters.get("from_date") or getdate()
    to_date = filters.get("to_date") or getdate()

    # Build SQL query
    query = """
        SELECT
            vehicle_name,
            reg_no,
            position,
            last_comm,
            today_workinghours,
            kms,
            ac AS ac_status,
            speed,
            status,
            expiry_date,
            gmap,
            is_over_speed
        FROM `tabVehicle Tracking System`
        WHERE last_comm BETWEEN %(from_date)s AND %(to_date)s
    """

    query_filters = {
        "from_date": f"{from_date} 00:00:00",
        "to_date": f"{to_date} 23:59:59"
    }

    if vehicle:
        query += " AND vehicle_name = %(vehicle)s"
        query_filters["vehicle"] = vehicle

    # Execute query
    data = frappe.db.sql(query, query_filters, as_dict=True)

    # Define report columns
    columns = [
        {"fieldname": "vehicle_name", "label": "Vehicle", "fieldtype": "Data", "width": 150},
        {"fieldname": "reg_no", "label": "Reg No", "fieldtype": "Data", "width": 120},
        {"fieldname": "position", "label": "Position", "fieldtype": "Data", "width": 100},
        {"fieldname": "last_comm", "label": "Last Communication", "fieldtype": "Datetime", "width": 180},
        {"fieldname": "today_workinghours", "label": "Today Working Hours", "fieldtype": "Data", "width": 120},
        {"fieldname": "kms", "label": "Kms", "fieldtype": "Float", "width": 100},
        {"fieldname": "ac_status", "label": "AC Status", "fieldtype": "Data", "width": 100},
        {"fieldname": "speed", "label": "Speed", "fieldtype": "Float", "width": 100},
        {"fieldname": "status", "label": "Status", "fieldtype": "Data", "width": 100},
        {"fieldname": "expiry_date", "label": "Expiry Date", "fieldtype": "Date", "width": 120},
        {"fieldname": "gmap", "label": "Google Map", "fieldtype": "Data", "width": 150},
        {"fieldname": "is_over_speed", "label": "Over Speed", "fieldtype": "Check", "width": 80},
    ]

    return columns, data
