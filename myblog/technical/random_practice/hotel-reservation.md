# LLD Practice: Hotel Reservation System

## Problem Statement

Design a Hotel Reservation System that allows customers to search for available rooms, make reservations, check-in, check-out, and handle cancellations.

---

## Requirements

### Functional Requirements
1. **Room Management**
   - Hotel has multiple room types (Single, Double, Suite)
   - Each room has a unique room number, type, price, and status (Available, Booked, Occupied, Maintenance)

2. **Reservation Management**
   - Customers can search for available rooms by date range and room type
   - Customers can make a reservation for specific dates
   - System should prevent double-booking
   - Support reservation cancellation with refund policy

3. **Check-in/Check-out**
   - Customers can check-in if they have a valid reservation
   - Generate bill on check-out
   - Calculate total amount including extra charges

4. **Payment**
   - Support multiple payment methods (Credit Card, Cash, Digital Wallet)
   - Process refunds for cancellations

### Non-Functional Requirements
- Thread-safe (multiple users booking simultaneously)
- Extensible (easy to add new room types, payment methods)
- Maintain SOLID principles

---

## Hints

### Think About These Questions First

1. **What are the main entities in the system?**
   - What properties and behaviors should they have?
   - Which entities need to be created/managed?

2. **State Management**
   - What states can a room have?
   - What states can a reservation have?
   - How do states transition?

3. **Design Patterns**
   - How will you handle multiple payment methods? (Strategy Pattern?)
   - How will you prevent double-booking in a concurrent environment?
   - How will you create different types of rooms? (Factory Pattern?)

4. **SOLID Principles**
   - Is each class doing one thing?
   - Can you add new room types without modifying existing code?
   - Are payment methods easily swappable?

5. **Concurrency**
   - What happens if two users try to book the same room at the same time?
   - Which operations need synchronization?

### Key Classes to Consider
- Room, RoomType
- Reservation, ReservationStatus
- Customer
- Payment, PaymentMethod
- Hotel/ReservationManager
- Bill

### Edge Cases
- Overlapping reservations
- Cancellation after check-in
- Room maintenance during active reservation
- Payment failure scenarios

---

## Interview Strategy: How to Ace This Problem

### The Golden Rule
**Don't jump into coding!** The interview is 80% design discussion, 20% code.

### Interview Flow (45-60 min typical)

#### Phase 1: Requirements Clarification (5-7 min)
**What to Ask:**
- "Is this a single hotel or multi-hotel system?" (Scope)
- "Do we need to handle pricing variations (weekend rates, seasonal pricing)?" (Complexity)
- "Should we support room amenities filtering?" (Features)
- "What's the cancellation policy?" (Business logic)
- "Do we need persistence or in-memory is fine?" (Infrastructure)

**Why This Matters:** Shows you think beyond code, understand business context, and won't build the wrong thing.

---

#### Phase 2: High-Level Design + Sketch (10-15 min)

**Start with a diagram on whiteboard/paper:**

```
┌─────────────────────────────────────────────────────────┐
│                  HotelReservationSystem                 │
│  ┌────────────────────────────────────────────────┐    │
│  │  - List<Room> rooms                            │    │
│  │  - Map<String, Reservation> reservations       │    │
│  │  - searchAvailableRooms()                      │    │
│  │  - createReservation()                         │    │
│  │  - checkIn() / checkOut()                      │    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
           │                    │
           │ manages            │ manages
           ▼                    ▼
    ┌──────────┐         ┌──────────────┐
    │   Room   │         │ Reservation  │
    ├──────────┤         ├──────────────┤
    │ - id     │◄────────│ - customer   │
    │ - type   │ booked  │ - room       │
    │ - status │         │ - dates      │
    │ - price  │         │ - status     │
    └──────────┘         └──────────────┘
         │                      │
         │                      │ has
         ▼                      ▼
  ┌────────────┐         ┌──────────┐
  │ RoomStatus │         │ Customer │
  │ (enum)     │         ├──────────┤
  ├────────────┤         │ - id     │
  │ AVAILABLE  │         │ - name   │
  │ BOOKED     │         │ - email  │
  │ OCCUPIED   │         └──────────┘
  │ MAINTENANCE│
  └────────────┘
                              │
                              │ pays via
                              ▼
                       ┌──────────────┐
                       │PaymentMethod │◄─── Strategy Pattern
                       │ (interface)  │
                       └──────────────┘
                              △
                ┌─────────────┼─────────────┐
                │             │             │
         ┌─────────┐   ┌──────────┐  ┌──────────┐
         │CreditCard│   │   Cash   │  │  Wallet  │
         └─────────┘   └──────────┘  └──────────┘
```

**While drawing, verbally explain:**
- "The central manager coordinates everything"
- "Room and Reservation are our core entities with clear state machines"
- "Payment uses Strategy Pattern for flexibility"
- "We'll use enums for type-safety of statuses"

---

#### Phase 3: Deep Dive into Critical Aspects (15-20 min)

**Topic 1: Double-Booking Prevention (CRITICAL)**

```
Interviewer: "How do you prevent two users from booking the same room?"

Your Answer:
"This is a race condition problem. Here's my approach:

1. Use synchronized block around the critical section:
   - Check room availability
   - Create reservation
   - Update room status

2. The check must include:
   - Room's current status
   - Date overlap with existing reservations

   isOverlapping = !(newCheckOut <= existingCheckIn ||
                     newCheckIn >= existingCheckOut)

3. Use ConcurrentHashMap for reservations but still need
   synchronized block because we're doing check-then-act.

4. Alternative: Optimistic locking with version numbers
   if we had a database."
```

**Why This Matters:** Shows you understand concurrency, not just syntax.

---

**Topic 2: State Management**

```
Interviewer: "Walk me through the state transitions"

Your Answer:
"Two state machines:

Room States:
  AVAILABLE → BOOKED (when reservation confirmed)
  BOOKED → OCCUPIED (when checked in)
  OCCUPIED → AVAILABLE (when checked out)
  ANY → MAINTENANCE (maintenance needed)
  MAINTENANCE → AVAILABLE (maintenance done)

Reservation States:
  PENDING → CONFIRMED (payment successful)
  CONFIRMED → CHECKED_IN (on check-in date)
  CHECKED_IN → CHECKED_OUT (on check-out)
  CONFIRMED → CANCELLED (user cancels)

Key rule: Status changes must be atomic and validated.
Only allow valid transitions."
```

---

**Topic 3: Design Patterns (Show, Don't Tell)**

```
Interviewer: "Why use Strategy Pattern for payments?"

Your Answer:
"Three reasons:

1. Open/Closed Principle: Add new payment methods
   without modifying existing code

2. Runtime flexibility: User chooses payment method
   at checkout, not compile time

3. Testability: Easy to mock payment methods

Alternative considered: If payment logic was very similar,
could use Template Method. But payment methods differ
significantly (card needs CVV, wallet needs OTP), so
Strategy is better."
```

**Why This Matters:** Shows you know WHY, not just WHAT.

---

**Topic 4: Thread Safety Discussion**

```
Your Explanation:
"Three levels of synchronization:

1. Method-level: Room.updateStatus(), Reservation state
   changes - protects individual object state

2. Block-level: HotelReservationSystem.createReservation()
   - protects multi-step operations (check-then-act)

3. Data structure: ConcurrentHashMap for reservation
   storage - thread-safe reads

Trade-off: Using synchronized reduces throughput but
prevents data corruption. For high-scale, we'd use:
- Database with row-level locking
- Distributed locks (Redis)
- Event sourcing"
```

---

#### Phase 4: Code Key Methods (10-15 min)

**Don't code everything!** Pick 2-3 critical methods:

1. **isRoomAvailable()** - Shows date logic + concurrency
2. **createReservation()** - Shows synchronized multi-step operation
3. **PaymentMethod interface** - Shows Strategy Pattern

```java
// Show this level of detail
private boolean isRoomAvailable(Room room, LocalDate checkIn, LocalDate checkOut) {
    synchronized (lock) {
        if (room.getStatus() != RoomStatus.AVAILABLE) return false;

        for (Reservation res : reservations.values()) {
            if (res.getRoom().equals(room) &&
                res.getStatus() != CANCELLED &&
                !(checkOut.isBefore(res.getCheckInDate()) ||  // Key logic!
                  checkIn.isAfter(res.getCheckOutDate()))) {
                return false;
            }
        }
        return true;
    }
}
```

**While coding, narrate:**
- "I'm using synchronized here because..."
- "This date overlap check handles edge cases where..."
- "I'm filtering out cancelled reservations because..."

---

#### Phase 5: Trade-offs & Extensions (5-10 min)

**Proactively discuss limitations:**

```
"Current design limitations:

1. Single JVM - won't scale horizontally
   → Solution: Move to distributed system with DB

2. Coarse-grained locking - low concurrency
   → Solution: Lock per room, not entire system

3. No reservation expiry
   → Enhancement: Add TTL, background job to cancel

4. In-memory storage - data loss on crash
   → Solution: Add persistence layer

5. No partial date modification
   → Enhancement: Add updateReservation() method"
```

**Why This Matters:** Shows you think about production systems, not just toy problems.

---

### What Interviewers Are Really Evaluating

#### ✅ Must Haves (You fail without these)
1. **Correct entities**: Room, Reservation, Customer, Payment
2. **Thread safety awareness**: Know WHERE and WHY synchronization is needed
3. **Prevent double-booking**: The core problem - must solve correctly
4. **Clean OOP**: Encapsulation, clear responsibilities

#### ⭐ Nice to Haves (Sets you apart)
1. **Design patterns with justification**: Not just "I used Strategy" but WHY
2. **Edge cases**: Overlapping dates, concurrent access, cancellation after check-in
3. **Trade-off discussions**: "This works for single server but for distributed..."
4. **Code clarity**: Readable names, comments on complex logic

#### 🚩 Red Flags (What NOT to do)
1. ❌ Jump straight to coding without clarifying requirements
2. ❌ Say "I'll use synchronized" without explaining the race condition
3. ❌ Ignore date overlap logic (most common mistake!)
4. ❌ Make everything static/singleton without justification
5. ❌ Claim design is "scalable" without discussing database/distributed systems
6. ❌ Write getters/setters for 20 minutes instead of focusing on core logic

---

### The Winning Formula

```
Success = Requirements (20%)
        + Design Discussion (40%)
        + Critical Code (20%)
        + Trade-offs (20%)
```

**Time allocation:**
- Spend MORE time on design/discussion
- Spend LESS time on boilerplate code (getters, constructors)
- ALWAYS leave time for trade-offs discussion

---

### Quick Self-Check Before Interview

Can you answer these in 30 seconds each?
- [ ] What's the race condition in this system?
- [ ] How do you check if dates overlap?
- [ ] Why Strategy Pattern for payments?
- [ ] What are Room's state transitions?
- [ ] Where do you use synchronized and why?
- [ ] How would you scale this to 1M requests/sec?

If yes → You're ready! 🚀

---

## Try to Implement Before Looking at the Solution!

Think through the design, sketch out the classes, and consider how they interact.

---

---

---

# Solution

## Class Diagram Overview

```
Hotel
  - manages rooms and reservations
  - singleton or main coordinator

Room
  - id, type, price, status

RoomType (enum)
  - SINGLE, DOUBLE, SUITE

RoomStatus (enum)
  - AVAILABLE, BOOKED, OCCUPIED, MAINTENANCE

Reservation
  - id, customer, room, checkIn, checkOut, status

ReservationStatus (enum)
  - PENDING, CONFIRMED, CHECKED_IN, CHECKED_OUT, CANCELLED

Customer
  - id, name, email, phone

Payment (interface/abstract)
  - processPayment(), refund()

PaymentStrategy implementations
  - CreditCardPayment, CashPayment, DigitalWalletPayment

Bill
  - reservation, baseAmount, extras, total
```

---

## Implementation

### 1. Enums

```java
public enum RoomType {
    SINGLE(100.0),
    DOUBLE(150.0),
    SUITE(300.0);

    private final double basePrice;

    RoomType(double basePrice) {
        this.basePrice = basePrice;
    }

    public double getBasePrice() {
        return basePrice;
    }
}

public enum RoomStatus {
    AVAILABLE,
    BOOKED,
    OCCUPIED,
    MAINTENANCE
}

public enum ReservationStatus {
    PENDING,
    CONFIRMED,
    CHECKED_IN,
    CHECKED_OUT,
    CANCELLED
}
```

### 2. Core Entities

```java
public class Room {
    private final String roomNumber;
    private final RoomType type;
    private RoomStatus status;
    private final double pricePerNight;

    public Room(String roomNumber, RoomType type) {
        this.roomNumber = roomNumber;
        this.type = type;
        this.pricePerNight = type.getBasePrice();
        this.status = RoomStatus.AVAILABLE;
    }

    public synchronized boolean isAvailable() {
        return status == RoomStatus.AVAILABLE;
    }

    public synchronized void updateStatus(RoomStatus newStatus) {
        this.status = newStatus;
    }

    // Getters
    public String getRoomNumber() { return roomNumber; }
    public RoomType getType() { return type; }
    public RoomStatus getStatus() { return status; }
    public double getPricePerNight() { return pricePerNight; }
}

public class Customer {
    private final String customerId;
    private final String name;
    private final String email;
    private final String phone;

    public Customer(String customerId, String name, String email, String phone) {
        this.customerId = customerId;
        this.name = name;
        this.email = email;
        this.phone = phone;
    }

    // Getters
    public String getCustomerId() { return customerId; }
    public String getName() { return name; }
    public String getEmail() { return email; }
    public String getPhone() { return phone; }
}

public class Reservation {
    private final String reservationId;
    private final Customer customer;
    private final Room room;
    private final LocalDate checkInDate;
    private final LocalDate checkOutDate;
    private ReservationStatus status;

    public Reservation(String reservationId, Customer customer, Room room,
                      LocalDate checkInDate, LocalDate checkOutDate) {
        this.reservationId = reservationId;
        this.customer = customer;
        this.room = room;
        this.checkInDate = checkInDate;
        this.checkOutDate = checkOutDate;
        this.status = ReservationStatus.PENDING;
    }

    public synchronized void confirm() {
        if (status == ReservationStatus.PENDING) {
            this.status = ReservationStatus.CONFIRMED;
            room.updateStatus(RoomStatus.BOOKED);
        }
    }

    public synchronized void checkIn() {
        if (status == ReservationStatus.CONFIRMED) {
            this.status = ReservationStatus.CHECKED_IN;
            room.updateStatus(RoomStatus.OCCUPIED);
        }
    }

    public synchronized void checkOut() {
        if (status == ReservationStatus.CHECKED_IN) {
            this.status = ReservationStatus.CHECKED_OUT;
            room.updateStatus(RoomStatus.AVAILABLE);
        }
    }

    public synchronized void cancel() {
        if (status == ReservationStatus.CONFIRMED || status == ReservationStatus.PENDING) {
            this.status = ReservationStatus.CANCELLED;
            room.updateStatus(RoomStatus.AVAILABLE);
        }
    }

    public long getNumberOfNights() {
        return ChronoUnit.DAYS.between(checkInDate, checkOutDate);
    }

    // Getters
    public String getReservationId() { return reservationId; }
    public Customer getCustomer() { return customer; }
    public Room getRoom() { return room; }
    public LocalDate getCheckInDate() { return checkInDate; }
    public LocalDate getCheckOutDate() { return checkOutDate; }
    public ReservationStatus getStatus() { return status; }
}
```

### 3. Payment Strategy Pattern

```java
public interface PaymentMethod {
    boolean processPayment(double amount);
    boolean refund(double amount);
}

public class CreditCardPayment implements PaymentMethod {
    private final String cardNumber;
    private final String cardHolder;

    public CreditCardPayment(String cardNumber, String cardHolder) {
        this.cardNumber = cardNumber;
        this.cardHolder = cardHolder;
    }

    @Override
    public boolean processPayment(double amount) {
        System.out.println("Processing credit card payment of $" + amount);
        // Integration with payment gateway
        return true;
    }

    @Override
    public boolean refund(double amount) {
        System.out.println("Refunding $" + amount + " to credit card");
        return true;
    }
}

public class CashPayment implements PaymentMethod {
    @Override
    public boolean processPayment(double amount) {
        System.out.println("Received cash payment of $" + amount);
        return true;
    }

    @Override
    public boolean refund(double amount) {
        System.out.println("Refunding $" + amount + " in cash");
        return true;
    }
}

public class DigitalWalletPayment implements PaymentMethod {
    private final String walletId;

    public DigitalWalletPayment(String walletId) {
        this.walletId = walletId;
    }

    @Override
    public boolean processPayment(double amount) {
        System.out.println("Processing wallet payment of $" + amount + " from " + walletId);
        return true;
    }

    @Override
    public boolean refund(double amount) {
        System.out.println("Refunding $" + amount + " to wallet " + walletId);
        return true;
    }
}
```

### 4. Bill

```java
public class Bill {
    private final Reservation reservation;
    private double baseAmount;
    private double extraCharges;
    private double total;

    public Bill(Reservation reservation) {
        this.reservation = reservation;
        calculateBill();
    }

    private void calculateBill() {
        long nights = reservation.getNumberOfNights();
        this.baseAmount = nights * reservation.getRoom().getPricePerNight();
        this.extraCharges = 0; // Can be extended for room service, etc.
        this.total = baseAmount + extraCharges;
    }

    public void addExtraCharge(double charge) {
        this.extraCharges += charge;
        this.total = baseAmount + extraCharges;
    }

    public double getTotal() {
        return total;
    }

    public void printBill() {
        System.out.println("===== BILL =====");
        System.out.println("Reservation ID: " + reservation.getReservationId());
        System.out.println("Room: " + reservation.getRoom().getRoomNumber());
        System.out.println("Nights: " + reservation.getNumberOfNights());
        System.out.println("Base Amount: $" + baseAmount);
        System.out.println("Extra Charges: $" + extraCharges);
        System.out.println("Total: $" + total);
        System.out.println("================");
    }
}
```

### 5. Hotel Manager (Singleton + Coordinator)

```java
public class HotelReservationSystem {
    private static HotelReservationSystem instance;
    private final List<Room> rooms;
    private final Map<String, Reservation> reservations;
    private final Object lock = new Object();

    private HotelReservationSystem() {
        rooms = new ArrayList<>();
        reservations = new ConcurrentHashMap<>();
    }

    public static synchronized HotelReservationSystem getInstance() {
        if (instance == null) {
            instance = new HotelReservationSystem();
        }
        return instance;
    }

    public void addRoom(Room room) {
        rooms.add(room);
    }

    public List<Room> searchAvailableRooms(RoomType type, LocalDate checkIn, LocalDate checkOut) {
        return rooms.stream()
            .filter(room -> room.getType() == type)
            .filter(room -> isRoomAvailable(room, checkIn, checkOut))
            .collect(Collectors.toList());
    }

    private boolean isRoomAvailable(Room room, LocalDate checkIn, LocalDate checkOut) {
        synchronized (lock) {
            // Check if room is in available status
            if (room.getStatus() != RoomStatus.AVAILABLE) {
                return false;
            }

            // Check for overlapping reservations
            for (Reservation reservation : reservations.values()) {
                if (reservation.getRoom().getRoomNumber().equals(room.getRoomNumber()) &&
                    reservation.getStatus() != ReservationStatus.CANCELLED &&
                    reservation.getStatus() != ReservationStatus.CHECKED_OUT) {

                    // Check for date overlap
                    if (!(checkOut.isBefore(reservation.getCheckInDate()) ||
                          checkIn.isAfter(reservation.getCheckOutDate()))) {
                        return false;
                    }
                }
            }
            return true;
        }
    }

    public Reservation createReservation(Customer customer, Room room,
                                        LocalDate checkIn, LocalDate checkOut) {
        synchronized (lock) {
            if (!isRoomAvailable(room, checkIn, checkOut)) {
                throw new IllegalStateException("Room not available for selected dates");
            }

            String reservationId = "RES-" + System.currentTimeMillis();
            Reservation reservation = new Reservation(reservationId, customer, room, checkIn, checkOut);
            reservation.confirm();

            reservations.put(reservationId, reservation);
            return reservation;
        }
    }

    public void checkIn(String reservationId) {
        Reservation reservation = reservations.get(reservationId);
        if (reservation == null) {
            throw new IllegalArgumentException("Reservation not found");
        }
        reservation.checkIn();
    }

    public Bill checkOut(String reservationId, PaymentMethod paymentMethod) {
        Reservation reservation = reservations.get(reservationId);
        if (reservation == null) {
            throw new IllegalArgumentException("Reservation not found");
        }

        Bill bill = new Bill(reservation);
        boolean paymentSuccess = paymentMethod.processPayment(bill.getTotal());

        if (paymentSuccess) {
            reservation.checkOut();
            return bill;
        } else {
            throw new RuntimeException("Payment failed");
        }
    }

    public void cancelReservation(String reservationId, PaymentMethod paymentMethod) {
        Reservation reservation = reservations.get(reservationId);
        if (reservation == null) {
            throw new IllegalArgumentException("Reservation not found");
        }

        // Refund policy: 50% refund if cancelled
        double refundAmount = reservation.getNumberOfNights() *
                             reservation.getRoom().getPricePerNight() * 0.5;

        paymentMethod.refund(refundAmount);
        reservation.cancel();
    }
}
```

### 6. Usage Example

```java
public class Main {
    public static void main(String[] args) {
        HotelReservationSystem hotel = HotelReservationSystem.getInstance();

        // Add rooms to hotel
        hotel.addRoom(new Room("101", RoomType.SINGLE));
        hotel.addRoom(new Room("102", RoomType.DOUBLE));
        hotel.addRoom(new Room("201", RoomType.SUITE));

        // Create customer
        Customer customer = new Customer("C001", "John Doe", "john@email.com", "1234567890");

        // Search available rooms
        LocalDate checkIn = LocalDate.now().plusDays(1);
        LocalDate checkOut = LocalDate.now().plusDays(3);

        List<Room> availableRooms = hotel.searchAvailableRooms(RoomType.DOUBLE, checkIn, checkOut);

        if (!availableRooms.isEmpty()) {
            // Make reservation
            Room selectedRoom = availableRooms.get(0);
            Reservation reservation = hotel.createReservation(customer, selectedRoom, checkIn, checkOut);
            System.out.println("Reservation created: " + reservation.getReservationId());

            // Check-in
            hotel.checkIn(reservation.getReservationId());
            System.out.println("Checked in successfully");

            // Check-out with payment
            PaymentMethod payment = new CreditCardPayment("1234-5678-9012-3456", "John Doe");
            Bill bill = hotel.checkOut(reservation.getReservationId(), payment);
            bill.printBill();
        }
    }
}
```

---

## Key Design Decisions

### 1. **Thread Safety**
- Used `synchronized` blocks in critical sections (room availability check, reservation creation)
- Used `ConcurrentHashMap` for reservation storage
- Synchronized methods in Room and Reservation for status updates

### 2. **Design Patterns Used**
- **Strategy Pattern**: For payment methods (easy to add new payment types)
- **Singleton Pattern**: For HotelReservationSystem (single instance managing all operations)
- **Encapsulation**: Room status changes only through controlled methods

### 3. **SOLID Principles**
- **SRP**: Each class has a single responsibility (Room manages room state, Reservation manages booking state)
- **OCP**: Open for extension (new payment methods, room types) without modifying existing code
- **DIP**: HotelReservationSystem depends on PaymentMethod interface, not concrete implementations

### 4. **Preventing Double Booking**
- Synchronized critical section when checking availability and creating reservation
- Check both room status and existing reservations for date overlap

### 5. **Extensibility**
- New room types: Add to RoomType enum
- New payment methods: Implement PaymentMethod interface
- Additional features: Bill can be extended for room service, taxes, etc.

---

## Possible Enhancements
1. Add persistence layer (database)
2. Implement room pricing strategies (seasonal pricing, dynamic pricing)
3. Add user authentication and authorization
4. Support partial cancellations (modify dates)
5. Add notification service for confirmations/reminders
6. Implement reservation expiry (auto-cancel if not paid within time)
7. Add inventory management for amenities
8. Support for multiple hotels in the system
