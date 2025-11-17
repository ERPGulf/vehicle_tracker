# import frappe
# import json
# from frappe.utils import get_datetime, format_datetime


# @frappe.whitelist(allow_guest=True)
# def create_vehicle_tracking(data):
#     """
#     API to insert multiple Vehicle Tracking records.
#     Creates Vehicle if it does not exist.
#     :param data: JSON array of vehicle tracking entries
#     """
#     if isinstance(data, str):
#         data = json.loads(data)

#     # Mapping for position
#     position_map = {
#         "Green": "Green - Running",
#         "Orange": "Orange - Vehicle Standing",
#         "Black": "Black - Vehicle Parked"
#     }

#     created = []

#     for entry in data:
#         # Input vehicle identifier (reg_no or unique code)
#         vehicle_input = entry.get("vehicle")
#         if not vehicle_input:
#             frappe.throw("Vehicle identifier is required")

#         # Check if Vehicle exists by license_plate
#         vehicle_docs = frappe.get_all("Vehicle", filters={"license_plate": vehicle_input}, limit=1)
#         if vehicle_docs:
#             vehicle_name = vehicle_docs[0].name
#         else:
#             # Create new Vehicle with extra fields
#             vehicle_doc = frappe.get_doc({
#                 "doctype": "Vehicle",
#                 "vehicle_name": entry.get("vehicle_name") or vehicle_input,
#                 "license_plate": vehicle_input,
#                 "make": entry.get("make"),
#                 "model": entry.get("model"),
#                 "last_odometer": entry.get("last_odometer"),
#                 "uom": entry.get("uom")
#             }).insert(ignore_permissions=True)
#             frappe.db.commit()
#             vehicle_name = vehicle_doc.name

#         # Convert color to full position string
#         color = entry.get("position", "")
#         position_full = position_map.get(color, color)  # fallback to original if unknown
#         last_seen_raw = entry.get("last_seen")
#         custom_last_seen = ""
#         if last_seen_raw:
#             # Convert string to datetime object
#             dt = get_datetime(last_seen_raw)  # returns Python datetime
#             # Format as DD-MM-YYYY HH:MM:SS
#             custom_last_seen = dt.strftime("%d-%m-%Y %H:%M:%S")

#         # Create Vehicle Tracking document
#         doc = frappe.get_doc({
#             "doctype": "Vehicle Tracking",
#             "vehicle": vehicle_name,    
#             "vehicle_name": vehicle_name,    # Link field to Vehicle.name (must match fieldname in doctype)
#             "reg_no": entry.get("reg_no"),  # Take reg_no from JSON
#             # "last_seen": entry.get("last_seen"),
#             "custom_vehicle_last_seen": custom_last_seen ,
#             "last_comm": entry.get("last_comm"),
#             "driver": entry.get("driver"),
#             "driver_mobile": entry.get("driver_mobile"),
#             "kms": entry.get("kms"),
#             "speed": entry.get("speed"),
#             "position": position_full,
#             "duration": entry.get("duration"),
#             "veh_battery": entry.get("veh_battery"),
#             "ac": entry.get("ac"),
#             "fuel_ltrs": entry.get("fuel_ltrs"),
#             "celsius": entry.get("celsius"),
#             "nearest_location": entry.get("nearest_location"),
#             "gmap": entry.get("gmap")
#         })

#         # Even if Vehicle field is hidden, this will set it correctly
#         doc.insert(ignore_permissions=True)
#         frappe.db.commit()
#         created.append(doc.name)


#     return {"status": "success", "inserted_records": created}
import frappe
import json
from frappe.utils import get_datetime
from datetime import datetime

@frappe.whitelist(allow_guest=True)
def create_vehicle_tracking(data):
    """
    API to insert multiple Vehicle Tracking records.
    Creates Vehicle if it does not exist.
    :param data: JSON array of vehicle tracking entries
    """
    if isinstance(data, str):
        data = json.loads(data)

    # Mapping for position colors to full strings
    position_map = {
        "Green": "Green - Running",
        "Orange": "Orange - Vehicle Standing",
        "Black": "Black - Vehicle Parked"
    }

    created = []

    for entry in data:
        # Input vehicle identifier (reg_no or unique code)
        vehicle_input = entry.get("vehicle")
        if not vehicle_input:
            frappe.throw("Vehicle identifier is required")

        # Check if Vehicle exists by license_plate
        vehicle_docs = frappe.get_all("Vehicle", filters={"license_plate": vehicle_input}, limit=1)
        if vehicle_docs:
            vehicle_name = vehicle_docs[0].name
        else:
            # Create new Vehicle
            vehicle_doc = frappe.get_doc({
                "doctype": "Vehicle",
                "vehicle_name": entry.get("vehicle_name") or vehicle_input,
                "license_plate": vehicle_input,
                "make": entry.get("make"),
                "model": entry.get("model"),
                "last_odometer": entry.get("last_odometer"),
                "uom": entry.get("uom")
            }).insert(ignore_permissions=True)
            frappe.db.commit()
            vehicle_name = vehicle_doc.name

        # Convert color to full position string
        color = entry.get("position", "")
        position_full = position_map.get(color, color)  # fallback to original if unknown

        # Parse last_seen safely
        last_seen_raw = entry.get("last_seen")
        custom_last_seen = None
        last_seen_dt = None
        if last_seen_raw:
            try:
                # Try input format: DD-MM-YYYY HH:MM:SS
                last_seen_dt = datetime.strptime(last_seen_raw, "%d-%m-%Y %H:%M:%S")
            except ValueError:
                # Fallback to ISO format
                last_seen_dt = get_datetime(last_seen_raw)

            if last_seen_dt:
                custom_last_seen = last_seen_dt.strftime("%d-%m-%Y %H:%M:%S")

        # Create Vehicle Tracking document
        doc = frappe.get_doc({
            "doctype": "Vehicle Tracking System",
            "vehicle": vehicle_name,
            "vehicle_name": vehicle_name,
            "reg_no": entry.get("reg_no"),
            "last_seen": custom_last_seen or "",
            "last_comm": entry.get("last_comm"),
            "driver": entry.get("driver"),
            "driver_mobile": entry.get("driver_mobile"),
            "kms": entry.get("kms"),
            "speed": entry.get("speed"),
            "position": position_full,
            "duration": entry.get("duration"),
            "veh_battery": entry.get("veh_battery"),
            "ac": entry.get("ac"),
            "fuel_ltrs": entry.get("fuel_ltrs"),
            "celsius": entry.get("celsius"),
            "nearest_location": entry.get("nearest_location"),
            "gmap": entry.get("gmap")
        })

        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        created.append(doc.name)

    return {"status": "success", "inserted_records": created}
