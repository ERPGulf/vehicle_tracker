import frappe
from frappe.utils import getdate, nowdate
from datetime import datetime

@frappe.whitelist()
def get_dashboard_data():
    today = getdate(nowdate())
    start_of_day = datetime.combine(today, datetime.min.time())
    end_of_day = datetime.combine(today, datetime.max.time())

    # Fetch all records
    all_records = frappe.get_all(
        "Vehicle Tracking System",
        fields=[
            "vehicle_name", "reg_no", "position", "last_seen", "last_comm",
            "duration", "kms", "ac"
        ],
        order_by="modified desc"
    )

    # Today's records
    today_records = [rec for rec in all_records if rec.last_comm and start_of_day <= rec.last_comm <= end_of_day]

    # Position mapping
    status_map = {
        "Green - Running": "running",
        "Orange - Vehicle Standing": "standing",
        "Black - Vehicle Parked": "parked",
        "SORNAGE": "parked"
    }

    # Initialize metrics
    running = standing = parked = 0
    ac_on = ac_off = 0
    total_distance = total_duration_seconds = 0
    most_run = None
    distance_chart_labels = []
    distance_chart_values = []

    vehicle_distances = {}

    for rec in today_records:
        pos = rec.get("position") or ""
        status_key = status_map.get(pos, "parked")
        if status_key == "running":
            running += 1
        elif status_key == "standing":
            standing += 1
        else:
            parked += 1

        # Distance
        kms = rec.get("kms") or 0
        total_distance += kms

        # Duration (HH:MM:SS -> seconds)
        dur = rec.get("duration") or "00:00:00"
        try:
            h, m, s = [int(x) for x in dur.split(":")]
            total_duration_seconds += h * 3600 + m * 60 + s
        except Exception:
            pass

        vehicle_distances[rec.vehicle_name] = kms

        # AC status
        ac_value = (rec.get("ac") or "").upper()
        if ac_value == "ON":
            ac_on += 1
        else:
            ac_off += 1

    # Top 8 vehicles by distance
    top_vehicles = sorted(vehicle_distances.items(), key=lambda x: x[1], reverse=True)[:8]
    for v, d in top_vehicles:
        distance_chart_labels.append(v)
        distance_chart_values.append(d)

    # Most run vehicle
    if vehicle_distances:
        most_run = max(vehicle_distances.items(), key=lambda x: x[1])[0]

    # Vehicles not run today
    today_vehicle_set = set(rec.vehicle_name for rec in today_records)
    all_vehicles = frappe.get_all("Vehicle", fields=["name"])
    not_run_today = len([v for v in all_vehicles if v.name not in today_vehicle_set])

    # Average duration & distance
    vehicle_count = len(vehicle_distances) or 1
    avg_duration_seconds = total_duration_seconds // vehicle_count
    avg_distance = total_distance // vehicle_count
    h = avg_duration_seconds // 3600
    m = (avg_duration_seconds % 3600) // 60
    s = avg_duration_seconds % 60
    avg_duration_str = f"{h:02d}:{m:02d}:{s:02d}"

    # Prepare full vehicle list for table
    vehicle_list = []
    for rec in all_records:
        vehicle_list.append({
            "vehicle_name": rec.vehicle_name,
            "reg_no": rec.reg_no,
            "position": rec.position,
            "last_seen": rec.last_seen.strftime("%d-%m-%Y %H:%M:%S") if rec.last_seen else "-",
            "last_comm": rec.last_comm.strftime("%d-%m-%Y %H:%M:%S") if rec.last_comm else "-",
            "duration": rec.duration or "00:00:00",
            "kms": rec.kms or 0,
            "ac": rec.ac or "-"
        })

    return {
        "running": running,
        "standing": standing,
        "parked": parked,
        "ac_on": ac_on,
        "ac_off": ac_off,
        "most_run": most_run,
        "not_run_today": not_run_today,
        "avg_duration": avg_duration_str,
        "avg_distance": avg_distance,
        "distance_chart": {
            "labels": distance_chart_labels,
            "values": distance_chart_values
        },
        "vehicle_list": vehicle_list
    }
