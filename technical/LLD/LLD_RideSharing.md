**Ride-Sharing System - Requirement Document**

### Objective
Design a ride-sharing system that allows users to request rides, assigns drivers, calculates fares dynamically, and tracks ride status using industry-standard design patterns.

### Key Features
1. **Vehicle Management**
   - The system should support different types of vehicles (e.g., Car, Bike).
   - Each vehicle should have a unique vehicle number and an assigned driver.

2. **Ride Management**
   - Users should be able to request a ride specifying the vehicle type and distance.
   - The system should notify available drivers about new ride requests.

3. **Driver Notification System**
   - Drivers should be notified of new ride requests.

4. **Fare Calculation**
   - Different fare strategies should be applied based on vehicle type.

5. **Ride Status Management**
   - A ride should transition through different states: Requested, Accepted, Completed.


### Functional Requirements
1. **User Requests a Ride**
   - The user specifies the vehicle type and distance.
   - The system logs the request and informs registered drivers.

2. **Driver Assignment**
   - The system should be able to assign a driver to a requested ride.
   - The assigned driver should be notified.

3. **Fare Calculation**
   - The system should compute the fare dynamically based on the selected vehicle type and distance.

4. **Ride Status Tracking**
   - The ride should transition through different states automatically.
   - The system should maintain the current state of the ride.

### Non-Functional Requirements
- The system should be scalable to support multiple concurrent ride requests.
- Notifications should be real-time.
- The system should be extendable to support new vehicle types and pricing models.

### Assumptions
- Drivers are pre-registered in the system.
- The ride allocation process is not automated but managed by notifications to available drivers.
- Payment processing is out of scope for this version.

### Future Enhancements
- Implement automated driver matching.
- Support for additional ride types like Auto, Pool rides.
- Integration with payment gateways.

This document outlines the high-level requirements of the ride-sharing system without going into exact implementation details while ensuring clarity on expected functionalities and design patterns.

