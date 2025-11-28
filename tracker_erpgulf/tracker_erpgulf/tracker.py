import frappe
import requests
import json
from datetime import datetime
from frappe.utils.data import get_datetime
from datetime import datetime, timezone



@frappe.whitelist(allow_guest=True)
def create_vehicle_tracking():
    """
    Fetch data from Vamosys API and insert/update Vehicle Tracking System docs.
    Position must be P, M, or S. AC is mapped from boolean to On/Off.
    """
    try:
        settings = frappe.get_single("Vehicle Tracking Setting")
        base_url = settings.base_url          
        username = settings.username          
        fcode = settings.get_password("fcode")            
        # password = settings.get_password("password")  # New

        # # ❌ Block API call if no password
        # if not password:
        #     frappe.log_error("Password missing in Vehicle Tracking Setting", "VT Password Validation Error")
        #     return {"status": "error", "message": "Please set the password in Vehicle Tracking Setting"}
        url = base_url
        params = {
            "providerName": username,
            "fcode": fcode
        }


        # Position mapping: use P, M, S codes
        position_map = {
            "P": "P - Parked Vehicle",
            "M": "M - Moving Vehicle",
            "S": "S - Stopped Vehicle"
        }

        try:
            response = requests.get(url, params=params)
        except Exception as e:
            frappe.log_error(message=str(e), title="Vehicle Tracking API Request Failed")
            return {"status": "error", "message": "API request failed", "error": str(e)}

        if response.status_code != 200:
            frappe.log_error(
                message=f"Status {response.status_code}: {response.text}",
                title="Vehicle Tracking API Error"
            )
            return {"status": "error", "message": f"Failed API request. Status: {response.status_code}"}

        # Safely parse JSON
        try:
            if not response.text.strip():
                frappe.log_error("Empty response from Vamosys API", "Vehicle Tracking API Empty Response")
                return {"status": "error", "message": "Empty API response"}
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            frappe.log_error(
                message=f"Invalid JSON: {response.text}",
                title="Vehicle Tracking API JSON Decode Error"
            )
            return {"status": "error", "message": "Invalid JSON response", "response": response.text}

        if not isinstance(data, list):
            frappe.log_error(
                message=f"Unexpected response type: {type(data)} - {data}",
                title="Vehicle Tracking API Unexpected Response"
            )
            return {"status": "error", "message": "Unexpected response format from API"}

        created = []

        for entry in data:
            # Vehicle identifier
            vehicle_input = entry.get("vehicleId")
            if not vehicle_input:
                continue

            # Check if Vehicle exists
            vehicle_docs = frappe.get_all("Vehicle", filters={"license_plate": vehicle_input}, limit=1)
            if vehicle_docs:
                vehicle_name = vehicle_docs[0].name
            else:
                # Create new Vehicle
                vehicle_doc = frappe.get_doc({
                    "doctype": "Vehicle",
                    "vehicle_name": entry.get("vehicleId") or vehicle_input,
                    "license_plate": vehicle_input,
                    "make": entry.get("vehicleMake") or "Unknown",
                    "model": entry.get("vehicleModel") or "Unknown" ,
                    "last_odometer": entry.get("odoDistance") ,
                    "uom": "Meter"  # Make sure this UOM exists in your system
                }).insert(ignore_permissions=True)
                frappe.db.commit()
                vehicle_name = vehicle_doc.name

            # Map position code
            position_code = (entry.get("position") or entry.get("color") or "").upper()
            position_full = position_map.get(position_code, "P - Parked Vehicle")  # Default to Parked

            # Parse last_seen
            last_seen_raw = entry.get("lastSeen")
            last_seen_str = None
            if last_seen_raw:
                try:
                    last_seen_dt = datetime.strptime(last_seen_raw, "%d-%m-%Y %H:%M:%S")
                except:
                    last_seen_dt = datetime.fromtimestamp(int(last_seen_raw)/1000, tz=timezone.utc)
                last_seen_str = last_seen_dt.strftime("%Y-%m-%d %H:%M:%S")
            # Map AC boolean to On/Off
            ac_value =  "ON" if entry.get("ac") in [True, "true", "True", 1, "1"] else "OFF"
            last_comm_ms = entry.get("lastComunicationTime")  
            last_comm_dt = datetime.fromtimestamp(last_comm_ms / 1000, tz=timezone.utc) 
            last_comm_str = last_comm_dt.strftime("%Y-%m-%d %H:%M:%S")
            timestamp_ms = entry.get("date")
            date_str = None
            if timestamp_ms:
                dt = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)  # Convert ms → seconds
                date_str = dt.strftime("%Y-%m-%d %H:%M:%S")


            over_speed_value = "YES" if entry.get("isOverSpeed") in ["Y", "YES", "y", "yes"] else "NO"
            vehicle_busy_value = "YES" if entry.get("vehicleBusy") in ["Y", "YES", "y", "yes"] else "NO"

            camera_value = "ON" if entry.get("cameraEnabled") else "OFF"
            live_status = "YES" if entry.get("live", "").lower() == "yes" else "NO"
            

            def seconds_to_hms(seconds):
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                secs = seconds % 60
                return f"{hours:02d}:{minutes:02d}:{secs:02d}"

            parked_time_sec = entry.get("parkedTime", 0)
            moving_time_sec = entry.get("movingTime", 0)
            idle_time_sec = entry.get("idleTime", 0)
            date_sec=entry.get("dateSec",0)
            expired_value = "YES" if str(entry.get("expired")).lower() in ["yes", "y", "true", "1"] else "NO"
            onboard_raw = entry.get("onboardDate")
            onboard_date = None
            if onboard_raw:
                    onboard_dt = datetime.strptime(onboard_raw, "%d-%m-%Y")
                    onboard_date = onboard_dt.strftime("%Y-%m-%d")

            used_keys = [
                "vehicleId", "regNo", "driverName", "communicatingPortNo", "safetyParking", 
                "driverMobile", "timeZone", "odoDistance", "lat", "lng", "deviceModel",
                "vehicleTypeLabel", "expiryDate", "forwardOrBackward", "expiryDays",
                "error", "distanceCovered", "chassisNumber", "speed", "routeName", 
                "altitude", "tankSize", "deviceVolt", "gpsSimNo", "fuelLitre", 
                "todayWorkingHours", "fuelLitres", "temperature", "vehicleType", 
                "overSpeedLimit", "ignitionStatus", "status", "oprName", "alert", 
                "fuelSensorType", "deviceId", "tripName", "shortName", "licenceType", 
                "direction", "vehicleModel", "engineStatus", "calibrateMode", "vehicleMode",
                "address", "rigMode", "orgId", "color", "sensorBasedVehicleMode",
                "ac", "vehicleBusy", "live", "position", "expired", "parkedTime",
                "movingTime", "idleTime", "dateSec", "lastSeen", "lastComunicationTime", 
                "onboardDate","rowId","latitude", "longitude","date","isOverSpeed","insideGeoFence",
                "powerStatus","deviceStatus","tankSize","cameraEnabled","fcode","vehicleName","expiryStatus",
                "madeIn"
                
            ]

            # Only include keys from entry that are NOT used in the doc
            more_details = {k: v for k, v in entry.items() if k not in used_keys}
            more_details_json = json.dumps(more_details, indent=2)
            expiry_status_value = "YES" if str(entry.get("expiryStatus", "")).lower() in ["yes", "y", "true", "1"] else "NO"


            expiry_raw = entry.get("expiryDate")
            expiry_date = None

            if expiry_raw:
                    expiry_dt = datetime.strptime(expiry_raw, "%d-%m-%Y")
                    expiry_date = expiry_dt.strftime("%Y-%m-%d")
            lat = entry.get('lat')
            lng = entry.get('lng')

            if lat and lng:
                google_map_url = f"https://www.google.com/maps?q={lat},{lng}"
                
                # Create Vehicle T  racking System document
            doc = frappe.get_doc({
                "doctype": "Vehicle Tracking System",
                # "date":date_str,
                "date":entry.get("date"),
                "vehicle": vehicle_name,
                "vehicle_name": vehicle_name,
                "onboard_date":onboard_date,
                "reg_no": entry.get("regNo"),
                "last_seen": entry.get("lastComunicationTime"),
                "last_comm": last_seen_str,
                "driver": entry.get("driverName"),
                "communicating_port_no":entry.get("communicatingPortNo"),
                "safety_parking":entry.get("safetyParking"),
                "driver_mobile": entry.get("driverMobile"),
                "time_zone":entry.get("timeZone"),
                "kms": entry.get("odoDistance"),
                "live" :live_status,
                "latitude": entry.get("lat") or entry.get("latitude"),
                "longitude": entry.get("lng") or entry.get("longitude"),
                "device_model": entry.get("deviceModel"),
                "vehicle_type_label":entry.get("vehicleTypeLabel"),
                "vehilce_type":entry.get("vehicleTypeLabel"),
                "expiry_date": expiry_date,
                "parked_time":entry.get("parkedTime"),
                "expired":expired_value,
                "moving_time": entry.get("movingTime"),
                "forward_or_backward":entry.get("forwardOrBackward"),
                "expiry_days":entry.get("expiryDays"),
                "idle_time": entry.get("idleTime"),
                # "date_sec":seconds_to_hms(date_sec),
                "date_sec":entry.get("dateSec"),
                "error":entry.get("error") or "-",
                "distance_covered":entry.get("distanceCovered"),
                "chassis_number": entry.get("chassisNumber"),
                "speed": entry.get("speed"),
                "route_name":entry.get("routeName"),
                "altitude":entry.get("altitude")or "-",
                "expirystatus":expiry_status_value,
                "device_status":entry.get("deviceStatus"),
                "tank_size":entry.get("tankSize"),
                "made_in":entry.get("madeIn"),
                "device_volt":entry.get("deviceVolt"),
                "position": position_full,
                "gps_sim_no":entry.get("gpsSimNo"),
                "fuel_litre":entry.get("fuelLitre"),
                "camera_enabled":camera_value,
                # "duration": entry.get("todayWorkingHours"),
                "veh_battery": entry.get("powerStatus"),
                "insidegeofence":entry.get("insideGeoFence"),
                # "sensor_based_vehicle_mode":entry.get("sensorBasedVehicleMode"),
                "ac": ac_value,
                "vehicle_busy":vehicle_busy_value,
                "today_workinghours":entry.get("todayWorkingHours"),
                "fuel_ltrs": entry.get("fuelLitres") or entry.get("fuelLitre"),
                "celsius": entry.get("temperature"),
                "vehicle_type": entry.get("vehicleType"),
                "over_speed_limit": entry.get("overSpeedLimit"),
                "ignition_status": entry.get("ignitionStatus"),
                "status": entry.get("status"),
                "oprname":entry.get("oprName"),
                "alert": entry.get("alert"),
                "fuel_sensor_type": entry.get("fuelSensorType"),
                "device_id": entry.get("deviceId"),
                "trip_name": entry.get("tripName"),
                "short_name":entry.get("shortName"),
                "licence_type": entry.get("licenceType"),
                "direction": entry.get("direction") or entry.get("forwardOrBackward"),
                "vehicle_model": entry.get("vehicleModel"),
                "engine_status": entry.get("engineStatus"),
                "is_over_speed":over_speed_value ,
                "calibrate_mode": entry.get("calibrateMode"),
                "vehicle_mode": entry.get("vehicleMode"),
                "nearest_location": entry.get("address"),
                "gmap": google_map_url,
                "fcode":entry.get("fcode"),
                "rig_mode":entry.get("rigMode"),
                "org_id":entry.get("orgId"),
                "color":entry.get("color"),
                "more_details":more_details_json
            })
            doc.sensor_based_vehicle_mode = json.dumps(entry.get("sensorBasedVehicleMode", []))
            doc.insert(ignore_permissions=True)
            frappe.db.commit()
            created.append(doc.name)

        return {"status": "success", "inserted_records": created}


    except Exception as e:
        
        frappe.log_error(message=str(e), title="Vehicle Tracking Critical Error")
        return {"status": "error", "message": "Critical error in tracking process", "error": str(e)}