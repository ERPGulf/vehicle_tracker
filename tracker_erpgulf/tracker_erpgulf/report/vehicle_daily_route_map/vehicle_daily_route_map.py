# # Copyright (c) 2025, ERPGulf and contributors
# # For license information, please  see license.txt

# # import frappe


# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data

import frappe
from frappe import _
from frappe.utils import getdate
from pypika.functions import Date     # <-- IMPORTANT FIX


def execute(filters=None):
    filters = filters or {}

    columns = get_columns()
    data = get_data(filters)

    if not data:
        return columns, [{
            "reg_no": filters.get("vehicle"),
            "event_time": "",
            "latitude": "",
            "longitude": "",
            "nearest_location": "No GPS data found",
            "speed": "",
            "vehicle_mode": "",
        }]

    return columns, data


def get_columns():
    return [
        {"label": "Vehicle", "fieldname": "reg_no", "fieldtype": "Data", "width": 100},
        {"label": "Time", "fieldname": "event_time", "fieldtype": "Datetime", "width": 150},
        {"label": "Latitude", "fieldname": "latitude", "fieldtype": "Float", "width": 120},
        {"label": "Longitude", "fieldname": "longitude", "fieldtype": "Float", "width": 120},
        {"label": "Speed", "fieldname": "speed", "fieldtype": "Float", "width": 80},
        {"label": "Mode", "fieldname": "vehicle_mode", "fieldtype": "Data", "width": 120},
        {"label": "Location", "fieldname": "nearest_location", "fieldtype": "Data", "width": 250},
    ]


def get_data(filters):
    vehicle = filters.get("vehicle")
    route_date = filters.get("route_date")

    if not vehicle or not route_date:
        return []

    tracking = frappe.qb.DocType("Vehicle Tracking System")

    rows = (
        frappe.qb.from_(tracking)
        .select(
            tracking.reg_no,
            tracking.date.as_("event_time"),
            tracking.latitude,
            tracking.longitude,
            tracking.speed,
            tracking.vehicle_mode,
            tracking.nearest_location,
        )
        .where(tracking.reg_no == vehicle)
        .where(Date(tracking.date) == getdate(route_date))   # <-- FIXED
        .orderby(tracking.date)
    ).run(as_dict=True)

    return rows
