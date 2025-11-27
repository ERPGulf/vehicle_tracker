// // Copyright (c) 2025, ERPGulf and contributors
// // For license information, please see license.txt

// frappe.query_reports["Employee Checkin Summary"] = {
// 	"filters": [

// 	]
// };
frappe.query_reports["Employee Checkin Summary"] = {
    "filters": [
        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date",
            reqd: 0
        },
        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date",
            reqd: 0
        },
        {
            fieldname: "employee",
            label: "Employee",
            fieldtype: "Link",
            options: "Employee",
            reqd: 0
        }
    ]
};
