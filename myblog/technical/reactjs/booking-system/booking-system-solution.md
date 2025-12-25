Here’s the **fully filled practice sheet solution** (Seat Booking Grid) with the same architecture you practiced:

**App → Grid → Row → Seat**, using

* flat array (length 12)
* index math (no slicing)
* immutable updates
* derived booked count

---

## `src/Seat.jsx`

```jsx
export default function Seat({ status, onClick }) {
  return <button onClick={onClick}>{status}</button>;
}
```

---

## `src/Row.jsx`

```jsx
import Seat from "./Seat";

export default function Row({ rowIndex, seats, onSeatClick }) {
  const rowStart = rowIndex * 4;

  return (
    <div>
      {[0, 1, 2, 3].map((colIndex) => {
        const seatIndex = rowStart + colIndex;

        return (
          <Seat
            key={seatIndex}
            status={seats[seatIndex]}
            onClick={() => onSeatClick(seatIndex)}
          />
        );
      })}
    </div>
  );
}
```

---

## `src/Grid.jsx`

```jsx
import Row from "./Row";

export default function Grid({ seats, onSeatClick }) {
  return (
    <div>
      {[0, 1, 2].map((rowIndex) => (
        <Row
          key={rowIndex}
          rowIndex={rowIndex}
          seats={seats}
          onSeatClick={onSeatClick}
        />
      ))}
    </div>
  );
}
```

---

## `src/App.jsx`

```jsx
import { useState } from "react";
import Grid from "./Grid";

export default function App() {
  const [seats, setSeats] = useState(Array(12).fill("Available"));

  function handleSeatClick(index) {
    if (seats[index] === "Booked") return;

    const next = seats.slice();
    next[index] = "Booked";
    setSeats(next);
  }

  const bookedCount = seats.filter((s) => s === "Booked").length;

  function reset() {
    setSeats(Array(12).fill("Available"));
  }

  return (
    <div>
      <h2>Seat Booking</h2>

      <div>
        Booked: {bookedCount} / {seats.length}
      </div>

      <Grid seats={seats} onSeatClick={handleSeatClick} />

      <button onClick={reset}>Reset</button>
    </div>
  );
}
```


