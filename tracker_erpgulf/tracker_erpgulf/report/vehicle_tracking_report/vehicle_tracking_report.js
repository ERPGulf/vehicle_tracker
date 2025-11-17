// Copyright (c) 2025, ERPGulf and contributors
// For license information, please see license.txt

frappe.query_reports["Vehicle Tracking Report"] = {
    "filters": [
        {
            fieldname: "vehicle",
            label: __("Vehicle"),
            fieldtype: "Link",
            options: "Vehicle",
            reqd: 0
        },
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            default: frappe.datetime.get_today(),
            reqd: 0
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            default: frappe.datetime.get_today(),
            reqd: 0
        }
    ]
};
