frappe.pages['vehicle-tracking-dashboard'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Vehicle Tracking Dashboard',
        single_column: true
    });
    new VehicleTrackingDashboard(page);
};

class VehicleTrackingDashboard {
    constructor(page) {
        this.page = page;
        this.make_form();
        this.load_dashboard_data();
    }

    make_form() {
        this.form = new frappe.ui.FieldGroup({
            fields: [
                { fieldtype: "HTML", fieldname: "summary_cards" },
                { label: __("Charts"), fieldname: "vehicle_charts", fieldtype: "HTML" },
                { label: __("Vehicle List"), fieldtype: "HTML", fieldname: "vehicle_list" }
            ],
            body: this.page.body
        });
        this.form.make();
    }

    load_dashboard_data() {
        frappe.call({
            method: "tracker_erpgulf.tracker_erpgulf.vehicle_tracking_dashboard.get_dashboard_data",
            callback: (r) => {
                if (!r.message) return;
                const data = r.message;
                this.render_cards(data);
                this.render_charts(data);
                this.render_list(data.vehicle_list || []);
            }
        });
    }

    render_cards(data) {
        const metrics = [
            { label: 'Moving', value: data.moving },
            { label: 'Stopped', value: data.stopped },
            { label: 'Parked', value: data.parked },
            { label: 'AC ON', value: data.ac_on },
            { label: 'AC OFF', value: data.ac_off },
            { label: 'Most Run Today', value: data.most_run || '-' },
            { label: 'Vehicles Not Run Today', value: data.not_run_today },
            { label: 'Avg Duration Today', value: data.avg_duration },
            { label: 'Avg Distance Today', value: data.avg_distance + ' km' }
        ];

        let cardHtml = '';
        for (let i = 0; i < metrics.length; i += 3) {
            cardHtml += `<div style="display:flex; gap:20px; margin-bottom:20px;">`;
            for (let j = i; j < i + 3 && j < metrics.length; j++) {
                const m = metrics[j];
                cardHtml += `
                    <div style="flex:1; background:#f8f9fa; padding:20px; border-radius:8px; text-align:center; box-shadow:0 0 5px rgba(0,0,0,0.1);">
                        <h5 style="color:#6c757d;">${m.label}</h5>
                        <div style="font-size:22px; font-weight:bold;">${m.value}</div>
                    </div>`;
            }
            cardHtml += `</div>`;
        }
        this.form.get_field("summary_cards").html(cardHtml);
    }

    render_charts(data) {
        const chart_html = `
            <div style="display:flex; gap:20px; justify-content:center; flex-wrap:wrap;">
                <div style="flex:0 0 300px; background:#f8f9fa; padding:10px; border-radius:8px;">
                    <canvas id="vehicleStatusChart" style="height:250px; width:250px;"></canvas>
                </div>
                <div style="flex:0 0 300px; background:#f8f9fa; padding:10px; border-radius:8px;">
                    <canvas id="acStatusChart" style="height:250px; width:250px;"></canvas>
                </div>
                <div style="flex:0 0 400px; background:#f8f9fa; padding:10px; border-radius:8px;">
                    <canvas id="distanceChart" style="height:250px; width:400px;"></canvas>
                </div>
            </div>`;
        this.form.get_field("vehicle_charts").html(chart_html);

        if (typeof Chart === "undefined") {
            const script = document.createElement("script");
            script.src = "https://cdn.jsdelivr.net/npm/chart.js";
            script.onload = () => this.draw_charts(data);
            document.head.appendChild(script);
        } else {
            this.draw_charts(data);
        }
    }

    draw_charts(data) {
        new Chart(document.getElementById("vehicleStatusChart").getContext("2d"), {
            type: "pie",
            data: {
                labels: ["Moving", "Stopped", "Parked"],
                datasets: [{ data: [data.moving, data.stopped, data.parked], backgroundColor: ["#28a745", "#ffc107", "#dc3545"] }]
            },
            options: { responsive: true, plugins: { legend: { position: "bottom" }, title: { display: true, text: "Vehicle Status Distribution" } } }
        });

        new Chart(document.getElementById("acStatusChart").getContext("2d"), {
            type: "pie",
            data: {
                labels: ["AC ON", "AC OFF"],
                datasets: [{ data: [data.ac_on, data.ac_off], backgroundColor: ["#17a2b8", "#6c757d"] }]
            },
            options: { responsive: true, plugins: { legend: { position: "bottom" }, title: { display: true, text: "AC Status" } } }
        });

        new Chart(document.getElementById("distanceChart").getContext("2d"), {
            type: "bar",
            data: { labels: data.distance_chart.labels, datasets: [{ label: "Distance (km)", data: data.distance_chart.values, backgroundColor: "#007bff" }] },
            options: { responsive: true, plugins: { legend: { display: false }, title: { display: true, text: "Top 5 Vehicles by Distance Today" } }, scales: { y: { beginAtZero: true } } }
        });
    }

    render_list(vehicle_list) {
        if (!vehicle_list.length) {
            this.form.get_field("vehicle_list").html("<p>No vehicle data available.</p>");
            return;
        }

        const rows = vehicle_list.map(v => `
            <tr>
                <td>${v.vehicle_name || '-'}</td>
                <td>${v.reg_no || '-'}</td>
                <td>${v.position || '-'}</td>
                <td>${v.last_comm || '-'}</td>
                <td>${v.today_workinghours || '00:00:00'}</td>
                <td>${v.kms || 0} km</td>
                <td>${v.ac || '-'}</td>
            </tr>
        `).join("");

        const table_html = `
            <table class="table table-bordered table-striped">
                <thead>
                    <tr>
                        <th>Vehicle</th>
                        <th>Reg No</th>
                        <th>Position</th>
                        <th>Last Communication</th>
                        <th>Today Working Hours</th>
                        <th>Kms</th>
                        <th>AC</th>
                    </tr>
                </thead>
                <tbody>${rows}</tbody>
            </table>`;
        this.form.get_field("vehicle_list").html(table_html);
    }
}
