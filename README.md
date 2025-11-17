## Tracker ERPGulf

# Vehicle Tracking System for ERPNext/Frappe

*Tracker ERPGulf is a Frappe application that fetches vehicle data from Vamosys API and updates the Vehicle Tracking System in ERPNext. It supports live location tracking, vehicle status, AC/engine state, over-speed alerts, and generates Google Maps links for vehicle positions.*

## Features

Fetch vehicle data from Vamosys API.

Create or update Vehicle and Vehicle Tracking System records.

Tracks:

> Vehicle location (latitude, longitude)
> 
> Last seen and communication timestamps
> 
> Driver details
> 
> Vehicle status: moving, parked, idle
> 
> AC and camera state
> 
> Over-speed and vehicle busy status
> 
> Odometer readings and fuel levels
> 
> Generates Google Maps links for each vehicle location.
> 
> Handles expired vehicles and onboard dates.
> 
> Safely logs API errors and invalid data.

## Installation

Clone the repository into your Frappe apps folder:

cd frappe-bench/apps
git clone https://github.com/ERPGulf/vehicle_tracker.git


## Install the app in your site:

cd ../
bench --site your-site install-app tracker_erpgulf

Configuration

Go to Vehicle Tracking Setting in ERPNext.

**Enter your Vamosys API credentials:

Base URL

Username

Fcode (password field)**

### Set any additional settings, like tracking frequency# vehicle_tracker
