```java
import java.util.HashMap;
import java.util.Map;
import java.util.Scanner;

// Factory Pattern: Create different vending items
abstract class Item {
    protected String name;
    protected double price;

    public String getName() { return name; }
    public double getPrice() { return price; }

    public abstract void dispense();
}

class Chips extends Item {
    public Chips() { this.name = "Chips"; this.price = 1.50; }
    public void dispense() { System.out.println("Dispensing Chips"); }
}

class Soda extends Item {
    public Soda() { this.name = "Soda"; this.price = 2.00; }
    public void dispense() { System.out.println("Dispensing Soda"); }
}

class ItemFactory {
    public static Item createItem(String itemType) {
        switch (itemType) {
            case "Chips": return new Chips();
            case "Soda": return new Soda();
            default: throw new IllegalArgumentException("Invalid item");
        }
    }
}

// State Pattern: Define Vending Machine States
interface VendingState {
    void handle(VendingMachine machine);
}

class IdleState implements VendingState {
    public void handle(VendingMachine machine) {
        System.out.println("Waiting for user selection...");
    }
}

class DispensingState implements VendingState {
    public void handle(VendingMachine machine) {
        System.out.println("Dispensing item...");
    }
}

class OutOfStockState implements VendingState {
    public void handle(VendingMachine machine) {
        System.out.println("Item is out of stock. Please choose another.");
    }
}

// Strategy Pattern: Payment Processing
interface PaymentStrategy {
    boolean processPayment(double amount);
}

class CashPayment implements PaymentStrategy {
    public boolean processPayment(double amount) {
        System.out.println("Processing cash payment: $" + amount);
        return amount > 0;
    }
}

class CardPayment implements PaymentStrategy {
    public boolean processPayment(double amount) {
        System.out.println("Processing card payment: $" + amount);
        return amount > 0;
    }
}

class MobilePayment implements PaymentStrategy {
    public boolean processPayment(double amount) {
        System.out.println("Processing mobile payment: $" + amount);
        return amount > 0;
    }
}

// Observer Pattern: Inventory Tracking
interface InventoryObserver {
    void update(String message);
}

class InventorySystem implements InventoryObserver {
    public void update(String message) {
        System.out.println("Inventory alert: " + message);
    }
}

// Vending Machine Class
class VendingMachine {
    private VendingState state = new IdleState();
    private Map<String, Integer> inventory = new HashMap<>();

    public VendingMachine() {
        inventory.put("Chips", 5);
        inventory.put("Soda", 5);
    }

    public void setState(VendingState state) {
        this.state = state;
    }

    public void start() {
        System.out.println("Vending Machine Ready.");
        state.handle(this);
    }

    public void selectItem(String itemName, PaymentStrategy paymentStrategy) {
        if (!inventory.containsKey(itemName) || inventory.get(itemName) == 0) {
            setState(new OutOfStockState());
            state.handle(this);
            return;
        }
        
        Item item = ItemFactory.createItem(itemName);
        if (paymentStrategy.processPayment(item.getPrice())) {
            setState(new DispensingState());
            state.handle(this);
            item.dispense();
            inventory.put(itemName, inventory.get(itemName) - 1);
        } else {
            System.out.println("Payment failed. Please try again.");
        }
    }
}

// Main class to test the system
public class VendingMachineSystem {
    public static void main(String[] args) {
        VendingMachine vendingMachine = new VendingMachine();
        vendingMachine.start();

        Scanner scanner = new Scanner(System.in);
        System.out.println("Select item (Chips/Soda):");
        String itemChoice = scanner.next();

        System.out.println("Select payment method (1 - Cash, 2 - Card, 3 - Mobile):");
        int paymentChoice = scanner.nextInt();
        PaymentStrategy strategy;
        switch (paymentChoice) {
            case 1: strategy = new CashPayment(); break;
            case 2: strategy = new CardPayment(); break;
            case 3: strategy = new MobilePayment(); break;
            default: throw new IllegalArgumentException("Invalid payment method");
        }

        vendingMachine.selectItem(itemChoice, strategy);
    }
}

```
