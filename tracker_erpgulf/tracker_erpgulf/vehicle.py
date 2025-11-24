# import frappe
# from frappe.utils import getdate
# from pypika.functions import Date
# @frappe.whitelist()
# def get_nearest_locations(vehicle, route_date):

#     tracking = frappe.qb.DocType("Vehicle Tracking System")
#     route_date = getdate(route_date)

#     rows = (
#         frappe.qb.from_(tracking)
#         .select(tracking.nearest_location)
#         .where(tracking.reg_no == vehicle)
#         .where(Date(tracking.date) == route_date)
#         .orderby(tracking.date)
#     ).run(as_dict=True)

#     # Extract clean list
#     locations = [r.nearest_location for r in rows if r.nearest_location]

#     # 🔥 Remove only *consecutive* duplicates
#     cleaned = []
#     last = None
#     for loc in locations:
#         if loc != last:       # add only when different from previous
#             cleaned.append(loc)
#         last = loc            # update last seen location

#     return cleaned
import frappe
from frappe.utils import get_datetime

@frappe.whitelist()
def get_nearest_locations(vehicle, route_date):
    tracking = frappe.qb.DocType("Vehicle Tracking System")

    rows = (
        frappe.qb.from_(tracking)
        .select(
            tracking.nearest_location,
            tracking.date   # datetime field
        )
        .where(tracking.reg_no == vehicle)
        .where(tracking.date.like(f"{route_date}%"))
        .orderby(tracking.date)
    ).run(as_dict=True)

    cleaned = []
    last_location = None

    for r in rows:
        location = r.nearest_location
        time_str = ""

        # extract time from datetime
        if r.date:
            dt = get_datetime(r.date)
            time_str = dt.strftime("%H:%M:%S")

        if location != last_location:
            cleaned.append({
                "location": location,
                "time": time_str
            })

        last_location = location

    return cleaned
