import frappe
from datetime import datetime, timezone
from tracker_erpgulf.tracker_erpgulf.tracker import create_vehicle_tracking
def scheduled_vehicle_tracking(force_run=False):
    try:
        settings = frappe.get_single("Vehicle Tracking Setting")
        frequency_minutes = float(settings.frequency)

        cache_key = "vehicle_tracking_last_run"
        last_run_str = frappe.cache().get_value(cache_key)
        now = datetime.now(timezone.utc)

        last_run = None
        if last_run_str:
            try:
                last_run = datetime.fromisoformat(last_run_str)
            except Exception:
                last_run = None

        if not last_run or (now - last_run).total_seconds() >= frequency_minutes * 60:
            create_vehicle_tracking()
            frappe.cache().set_value(cache_key, now.isoformat())
       

    except Exception as e:
        frappe.log_error(f"Scheduler Exception: {str(e)}", "Vehicle Tracker Error")