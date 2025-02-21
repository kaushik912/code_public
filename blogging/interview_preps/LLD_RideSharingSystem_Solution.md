```java
import java.util.*;

// Factory Pattern for Vehicle Creation
abstract class Vehicle {
    protected String vehicleNumber;
    protected String driverName;

    public Vehicle(String vehicleNumber, String driverName) {
        this.vehicleNumber = vehicleNumber;
        this.driverName = driverName;
    }

    public abstract void displayInfo();
}

class Car extends Vehicle {
    public Car(String vehicleNumber, String driverName) {
        super(vehicleNumber, driverName);
    }

    @Override
    public void displayInfo() {
        System.out.println("Car - " + vehicleNumber + " driven by " + driverName);
    }
}

class Bike extends Vehicle {
    public Bike(String vehicleNumber, String driverName) {
        super(vehicleNumber, driverName);
    }

    @Override
    public void displayInfo() {
        System.out.println("Bike - " + vehicleNumber + " driven by " + driverName);
    }
}

class VehicleFactory {
    public static Vehicle createVehicle(String type, String vehicleNumber, String driverName) {
        return switch (type) {
            case "Car" -> new Car(vehicleNumber, driverName);
            case "Bike" -> new Bike(vehicleNumber, driverName);
            default -> throw new IllegalArgumentException("Unknown vehicle type");
        };
    }
}

// Singleton Pattern for RideManager
class RideManager {
    private static RideManager instance;
    private List<DriverObserver> drivers = new ArrayList<>();

    private RideManager() {}

    public static synchronized RideManager getInstance() {
        if (instance == null) {
            instance = new RideManager();
        }
        return instance;
    }

    public void requestRide(String vehicleType, String user, double distance) {
        System.out.println(user + " requested a " + vehicleType + " ride for " + distance + " km.");
        notifyDrivers("New ride available: " + vehicleType);
    }

    public void registerDriver(DriverObserver driver) {
        drivers.add(driver);
    }

    private void notifyDrivers(String message) {
        for (DriverObserver driver : drivers) {
            driver.update(message);
        }
    }
}

// Observer Pattern for Driver Notifications
interface DriverObserver {
    void update(String message);
}

class Driver implements DriverObserver {
    private String name;

    public Driver(String name) {
        this.name = name;
    }

    @Override
    public void update(String message) {
        System.out.println(name + " received notification: " + message);
    }
}

// Strategy Pattern for Fare Calculation
interface FareStrategy {
    double calculateFare(double distance);
}

class CarFare implements FareStrategy {
    public double calculateFare(double distance) {
        return distance * 10;
    }
}

class BikeFare implements FareStrategy {
    public double calculateFare(double distance) {
        return distance * 5;
    }
}

// State Pattern for Ride Status
interface RideState {
    void handleState(RideContext context);
}

class RequestedState implements RideState {
    public void handleState(RideContext context) {
        System.out.println("Ride has been requested.");
        context.setState(new AcceptedState());
    }
}

class AcceptedState implements RideState {
    public void handleState(RideContext context) {
        System.out.println("Ride has been accepted.");
        context.setState(new CompletedState());
    }
}

class CompletedState implements RideState {
    public void handleState(RideContext context) {
        System.out.println("Ride has been completed.");
    }
}

class RideContext {
    private RideState state;

    public RideContext() {
        this.state = new RequestedState();
    }

    public void setState(RideState state) {
        this.state = state;
    }

    public void applyState() {
        state.handleState(this);
    }
}

// Testing the system
public class RideSharingSystem {
    public static void main(String[] args) {
        RideManager rideManager = RideManager.getInstance();

        // Registering drivers
        Driver driver1 = new Driver("Alice");
        Driver driver2 = new Driver("Bob");
        rideManager.registerDriver(driver1);
        rideManager.registerDriver(driver2);

        // Requesting rides
        rideManager.requestRide("Car", "User1", 10.0);
        rideManager.requestRide("Bike", "User2", 5.0);

        // Testing Fare Calculation
        FareStrategy carFare = new CarFare();
        System.out.println("Car Fare for 10km: " + carFare.calculateFare(10));

        FareStrategy bikeFare = new BikeFare();
        System.out.println("Bike Fare for 5km: " + bikeFare.calculateFare(5));

        // Testing Ride State Transitions
        RideContext rideContext = new RideContext();
        rideContext.applyState(); // Requested -> Accepted
        rideContext.applyState(); // Accepted -> Completed
    }
}
```
