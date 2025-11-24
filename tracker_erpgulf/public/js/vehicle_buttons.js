frappe.ui.form.on("Vehicle", {
    refresh(frm) {

        // 📌 1. View Daily Route Map
        frm.add_custom_button("View Daily Route Map", function () {
            let vehicle = frm.doc.name;

            frappe.set_route("query-report", "Vehicle Daily Route Map", {
                vehicle: vehicle
            });
        }, "Actions");

        // 📌 2. View Vehicle Tracking Report
        frm.add_custom_button("View Vehicle Tracking Report", function () {
            let vehicle = frm.doc.name;

            frappe.set_route("query-report", "Vehicle Tracking Report", {
                vehicle: vehicle
            });
        }, "Actions");
    }
});
