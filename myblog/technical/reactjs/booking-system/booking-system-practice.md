Perfect choice 👍
**Practice Sheet A: Seat Booking Grid** is an excellent test of the *same concepts* you used in Tic-Tac-Toe, without feeling repetitive.

We’ll do this **worksheet-style** again.
You fill in the TODOs. I’ll review like a code reviewer.

---

# 🧪 Practice Sheet A — Seat Booking Grid

## Problem recap

* 3 rows × 4 columns = **12 seats**
* Each seat:

  * starts as `"Available"`
  * click → `"Booked"`
  * clicking a booked seat does nothing
* Show:

  ```
  Booked: X / 12
  ```

### Rules

* ✅ One flat array (length 12)
* ❌ No slicing
* ❌ No local state in Seat
* ✅ Index math only

---

## File structure

```
src/
  App.jsx
  Grid.jsx
  Row.jsx
  Seat.jsx
```

---

# 1️⃣ `Seat.jsx` (very simple)

```jsx
export default function Seat({ status, onClick }) {
  return (
    <button onClick={/* TODO 1 */}>
      {/* TODO 2: show status */}
    </button>
  );
}
```

✅ Expectation: clicking triggers parent handler.

---

# 2️⃣ `Row.jsx` (index math)

```jsx
import Seat from "./Seat";

export default function Row({ rowIndex, seats, onSeatClick }) {
  // TODO 1: calculate rowStart (hint: rowIndex * 4)

  return (
    <div>
      {[0, 1, 2, 3].map((colIndex) => {
        // TODO 2: calculate seatIndex (rowStart + colIndex)

        return (
          <Seat
            key={/* TODO 3 */}
            status={/* TODO 4: seats[seatIndex] */}
            onClick={() => {
              // TODO 5: call onSeatClick(seatIndex)
            }}
          />
        );
      })}
    </div>
  );
}
```

---

# 3️⃣ `Grid.jsx` (renders rows)

```jsx
import Row from "./Row";

export default function Grid({ seats, onSeatClick }) {
  return (
    <div>
      {/* TODO 1: render 3 rows using map */}
      {/* Pass:
          - key
          - rowIndex
          - seats
          - onSeatClick
      */}
    </div>
  );
}
```

---

# 4️⃣ `App.jsx` (state + logic)

```jsx
import { useState } from "react";
import Grid from "./Grid";

export default function App() {
  // TODO 1: seats state (Array(12).fill("Available"))

  function handleSeatClick(index) {
    // TODO 2: if seat already "Booked", ignore

    // TODO 3: create copy of seats
    // TODO 4: mark index as "Booked"
    // TODO 5: update state
  }

  // TODO 6: compute bookedCount (hint: filter or reduce)

  return (
    <div>
      <h2>Seat Booking</h2>

      {/* TODO 7: show "Booked: X / 12" */}

      <Grid
        seats={/* TODO 8 */}
        onSeatClick={/* TODO 9 */}
      />
    </div>
  );
}
```

---

## ✅ Final behavior checklist

When done, your app should:

* Show 12 seats
* Clicking a seat marks it “Booked”
* Clicking again does nothing
* Count updates correctly
* No state outside `App`

---

## Submission order (important)

Paste files in this order:
1️⃣ `Seat.jsx`
2️⃣ `Row.jsx`
3️⃣ `Grid.jsx`
4️⃣ `App.jsx`

I’ll review each one and tell you **what level your understanding is at** (junior / solid / strong).

Take your time — this is a very good evaluation exercise.
