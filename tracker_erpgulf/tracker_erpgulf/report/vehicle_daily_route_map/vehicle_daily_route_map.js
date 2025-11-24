// // Copyright (c) 2025, ERPGulf and contributors
// // For license information, please see license.txt

// frappe.query_reports["Vehicle Daily Route Map"] = {
// 	"filters": [

// 	]
// };
frappe.query_reports["Vehicle Daily Route Map"] = {
    filters: [
        {
            fieldname: "vehicle",
            label: "Vehicle",
            fieldtype: "Link",
            options: "Vehicle",
            reqd: 1
        },
        {
            fieldname: "route_date",
            label: "Date",
            fieldtype: "Date",
            reqd: 1
        }
    ],

    onload(report) {
        console.log("🔥 Report Loaded (Vehicle Daily Route Map)");

        function render_map(locations) {
            console.log("📍 Cleaned Locations (with time):", locations);

            const mapDivId = "vehicle-route-map";
            let mapDiv = document.getElementById(mapDivId);

            if (!mapDiv) {
                mapDiv = document.createElement("div");
                mapDiv.id = mapDivId;
                mapDiv.style.height = "500px";
                mapDiv.style.width = "100%";
                mapDiv.style.marginTop = "20px";
                report.page.wrapper.append(mapDiv);
            } else {
                mapDiv.innerHTML = "";
            }

            const map = new google.maps.Map(mapDiv, {
                center: { lat: 25.3, lng: 51.5 },
                zoom: 12
            });

            const geocoder = new google.maps.Geocoder();
            const path = [];
            const bounds = new google.maps.LatLngBounds();
            let index = 0;

            function geocodeNext() {
                if (index >= locations.length) {
                    if (path.length > 1) {
                        new google.maps.Polyline({
                            path,
                            geodesic: true,
                            strokeColor: "#FF0000",
                            strokeOpacity: 1.0,
                            strokeWeight: 6
                        }).setMap(map);

                        map.fitBounds(bounds);
                    }
                    return;
                }

                let loc = locations[index];
                console.log("📍 Geocoding:", loc);

                geocoder.geocode({ address: loc.location }, function (results, status) {
                    if (status === "OK" && results[0]) {
                        let pos = results[0].geometry.location;

                        // ⭐ TITLE = location + time
                        let markerLabel = `${loc.location} (${loc.time})`;

                        new google.maps.Marker({
                            position: pos,
                            map,
                            title: markerLabel,
                            label: {
                                text: loc.time,
                                color: "black",
                                fontSize: "12px",
                                fontWeight: "bold"
                            }
                        });

                        path.push({ lat: pos.lat(), lng: pos.lng() });
                        bounds.extend(pos);
                    } else {
                        console.warn("❌ Geocode Failed:", loc, status);
                    }

                    index++;
                    geocodeNext();
                });
            }

            geocodeNext();
        }

        report.refresh = function () {
            let vehicle = report.get_filter_value("vehicle");
            let date = report.get_filter_value("route_date");

            console.log("🚗 (REFRESH) Vehicle:", vehicle);
            console.log("📅 (REFRESH) Date:", date);

            if (!vehicle || !date) return;

            frappe.call({
                method: "myinvois_erpgulf.vehicle.get_nearest_locations",
                args: { vehicle, route_date: date },
                callback: function (r) {
                    console.log("📌 Python Returned:", r.message);
                    render_map(r.message || []);
                }
            });
        };

        window.initVehicleRouteMap = function () {
            report.refresh();
        };

        if (!window.__gmaps_loading) {
            window.__gmaps_loading = true;

            const script = document.createElement("script");
            script.src =
                "https://maps.googleapis.com/maps/api/js?key=AIzaSyD8WEVYP9uypGT53GWXHHdpwHpCu7n3Jxg&callback=initVehicleRouteMap";
            script.async = true;
            script.defer = true;
            document.head.appendChild(script);
        } else if (window.google && window.google.maps) {
            initVehicleRouteMap();
        }
    }
};
