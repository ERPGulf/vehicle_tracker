import frappe
from frappe.utils import getdate, nowdate
from datetime import datetime

@frappe.whitelist()
def get_dashboard_data():
    today = getdate(nowdate())
    start_of_day = datetime.combine(today, datetime.min.time())
    end_of_day = datetime.combine(today, datetime.max.time())

    # Fetch all Vehicle Tracking System records
    all_records = frappe.get_all(
        "Vehicle Tracking System",
        fields=[
            "vehicle_name", "reg_no", "position", "last_comm",
            "kms", "ac", "today_workinghours"
        ],
        order_by="modified desc"
    )

    # Filter today's records based on last_comm
    today_records = [
        rec for rec in all_records
        if rec.last_comm and start_of_day <= rec.last_comm <= end_of_day
    ]

    # Position mapping
    status_map = {
        "P - Parked Vehicle": "parked",
        "M - Moving Vehicle": "moving",
        "S - Stopped Vehicle": "stopped"
    }

    moving = stopped = parked = 0
    ac_on = ac_off = 0
    total_distance = 0
    total_working_seconds = 0
    vehicle_distances = {}

    def ms_to_hms(ms):
        """Convert milliseconds (str or number) to HH:MM:SS"""
        try:
            ms = float(ms)
        except (ValueError, TypeError):
            ms = 0
        seconds = int(ms // 1000)
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return h, m, s, seconds

    vehicle_count_for_avg = 0

    for rec in today_records:
        status_key = status_map.get(rec.position, "parked")
        if status_key == "moving":
            moving += 1
        elif status_key == "stopped":
            stopped += 1
        else:
            parked += 1

        kms = rec.kms or 0
        total_distance += kms
        vehicle_distances[rec.vehicle_name] = kms

        # Today working hours in milliseconds
        wh_ms = getattr(rec, "today_workinghours", 0) or 0
        h, m, s, sec = ms_to_hms(wh_ms)
        if sec > 0:
            total_working_seconds += sec
            vehicle_count_for_avg += 1

        ac_value = (rec.ac or "").upper()
        if ac_value == "ON":
            ac_on += 1
        else:
            ac_off += 1

    # Top 8 vehicles by distance
    top_vehicles = sorted(vehicle_distances.items(), key=lambda x: x[1], reverse=True)[:8]
    distance_chart_labels = [v for v, _ in top_vehicles]
    distance_chart_values = [d for _, d in top_vehicles]

    most_run = max(vehicle_distances.items(), key=lambda x: x[1])[0] if vehicle_distances else None

    today_vehicle_set = set(rec.vehicle_name for rec in today_records)
    all_vehicles = frappe.get_all("Vehicle", fields=["name"])
    not_run_today = len([v for v in all_vehicles if v.name not in today_vehicle_set])

    # Average working hours
    vehicle_count_for_avg = vehicle_count_for_avg or 1
    avg_seconds = total_working_seconds // vehicle_count_for_avg
    h = avg_seconds // 3600
    m = (avg_seconds % 3600) // 60
    s = avg_seconds % 60
    avg_duration_str = f"{h:02d}:{m:02d}:{s:02d}"

    # Vehicle list for dashboard
    vehicle_list = []
    for rec in all_records:
        status_key = status_map.get(rec.position, "parked")
        wh_ms = getattr(rec, "today_workinghours", 0) or 0
        h, m, s, sec = ms_to_hms(wh_ms)
        vehicle_list.append({
            "vehicle_name": rec.vehicle_name,
            "reg_no": rec.reg_no,
            "position": status_key.capitalize(),
            "last_comm": rec.last_comm.strftime("%d-%m-%Y %H:%M:%S") if rec.last_comm else "-",
            "today_workinghours": f"{h:02d}:{m:02d}:{s:02d}",
            "kms": rec.kms or 0,
            "ac": rec.ac or "-"
        })

    return {
        "moving": moving,
        "stopped": stopped,
        "parked": parked,
        "ac_on": ac_on,
        "ac_off": ac_off,
        "most_run": most_run,
        "not_run_today": not_run_today,
        "avg_duration": avg_duration_str,
        "avg_distance": total_distance // (len(today_records) or 1),
        "distance_chart": {
            "labels": distance_chart_labels,
            "values": distance_chart_values
        },
        "vehicle_list": vehicle_list
    }
