Got it! Let me give you an LLD problem statement to solve.

***

## **Problem: Design a Parking Lot System**

**Requirements:**

Design a parking lot system that handles the following:

1. The parking lot has multiple floors
2. Each floor has multiple parking spots of different types: Compact, Large, and Motorcycle
3. The system should support:
   - Vehicles entering and getting assigned a spot based on vehicle type (Car, Truck, Motorcycle)
   - Vehicles exiting and freeing up the spot
   - Tracking which spots are available/occupied
   - Calculating parking fees based on duration

**Your Task:**

Please provide:
1. **Key classes** you would design (with their main attributes and methods)
2. **Relationships** between classes
3. **Design patterns** you would use (if any)
4. **How you would handle spot assignment** when a vehicle enters

***

ParkingLot
- List<Floor> floors

Floor
- List<ParkingSlot> slots
- int floor_id
- int available_slots

ParkingSlot 
 - slot_id
 - ParkingSlotType
 - Vehicle
 - slot_status

SlotStatus
 - Available
 - Occupied

ParkingSlotType
-  Compact, Large, and Motorcycle

Vehicle
- VehiceType
- reg_number

VehicleType (Enum)
- Car, Truck, Motorcycle

---

ParkingLot (Singleton)
├── List<Floor> floors
├── Map<String, ParkingTicket> activeTickets
├── FeeCalculator feeCalculator
│
├── + getInstance(): ParkingLot
├── + parkVehicle(Vehicle): ParkingTicket
├── + unparkVehicle(String ticketId): Receipt
├── - findAvailableSlot(VehicleType): ParkingSlot
└── + getAvailability(): Map<ParkingSlotType, Integer>

Floor
├── int floorId
├── List<ParkingSlot> slots
├── Map<ParkingSlotType, Integer> availableCount
│
├── + findAvailableSlot(ParkingSlotType): ParkingSlot
├── + updateAvailability(ParkingSlotType, int delta): void
└── + getAvailableCount(ParkingSlotType): int

ParkingSlot
├── String slotId
├── int floorId
├── ParkingSlotType slotType
├── SlotStatus status
├── Vehicle currentVehicle
│
├── + assignVehicle(Vehicle): void
├── + removeVehicle(): Vehicle
├── + isAvailable(): boolean
├── + canFit(VehicleType): boolean
└── + getSlotId(): String

ParkingTicket
├── String ticketId
├── Vehicle vehicle
├── ParkingSlot assignedSlot
├── LocalDateTime entryTime
├── LocalDateTime exitTime
│
├── + getTicketId(): String
├── + markExit(): void
├── + getDuration(): Duration
└── + getDetails(): String

Vehicle
├── String registrationNumber
├── VehicleType type
├── String color (optional)
│
├── + getRegistrationNumber(): String
├── + getType(): VehicleType
└── + toString(): String

Receipt
├── String receiptId
├── ParkingTicket ticket
├── double amount
├── LocalDateTime paymentTime
├── PaymentStatus status
│
├── + getAmount(): double
└── + printReceipt(): String

FeeCalculator (Interface)
└── + calculateFee(Duration, VehicleType): double

HourlyFeeCalculator (implements FeeCalculator)
├── Map<VehicleType, Double> hourlyRates
│
└── + calculateFee(Duration, VehicleType): double
