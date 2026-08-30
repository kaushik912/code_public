
## 0) Vite setup (do this exactly)

```bash
npm create vite@latest tic-tac-toe -- --template react
cd tic-tac-toe
npm install
npm run dev
```

Create these files in `src/`:

* `App.jsx`
* `Board.jsx`
* `Row.jsx`
* `Square.jsx`

---

# 1) `Square.jsx` (easy)

**Goal:** button that displays value, calls `onClick`.

```jsx
export default function Square({ value, onClick }) {
  return (
    <button onClick={/* TODO 1 */}>
      {/* TODO 2: render value */}
    </button>
  );
}
```

✅ Test expectation: clicking should call whatever handler you pass.

---

# 2) `Row.jsx` (index math)

**Goal:** render 3 squares using `map`, compute `boardIndex`.

```jsx
import Square from "./Square";

export default function Row({ rowIndex, squares, onSquareClick }) {
  // TODO 1: compute rowStart (hint: rowIndex * 3)

  return (
    <div>
      {[0, 1, 2].map((colIndex) => {
        // TODO 2: compute boardIndex (hint: rowStart + colIndex)

        return (
          <Square
            key={/* TODO 3: stable key */}
            value={/* TODO 4: value from squares using boardIndex */}
            onClick={() => {
              // TODO 5: call onSquareClick with boardIndex
            }}
          />
        );
      })}
    </div>
  );
}
```

✅ Test expectation: clicking row 2 col 2 should update index **8** in the array.

---

# 3) `Board.jsx` (renders 3 rows)

**Goal:** render 3 rows using `map`, no slicing.

```jsx
import Row from "./Row";

export default function Board({ squares, onSquareClick }) {
  return (
    <div>
      {/* TODO 1: map over [0,1,2] */}
      {/* TODO 2: render Row with props:
          - key
          - rowIndex
          - squares (full array)
          - onSquareClick
      */}
    </div>
  );
}
```

✅ Test expectation: board shows 3 rows (even if they look like lines).

---

# 4) `App.jsx` (state + click logic + winner)

**Goal:** App owns state, passes props down, handles clicks, shows status.

```jsx
import { useState } from "react";
import Board from "./Board";

function calculateWinner(squares) {
  // TODO 1: define winning lines (8 lines total)
  const lines = [
    // TODO: add arrays like [0,1,2], ...
  ];

  // TODO 2: loop lines, destructure [a,b,c]
  // TODO 3: if squares[a] exists and equals squares[b] and squares[c], return squares[a]
  // TODO 4: return null otherwise
}

export default function App() {
  // TODO 5: squares state (hint: Array(9).fill(null))
  // const [squares, setSquares] = ...

  // TODO 6: xIsNext state (true initially)

  // TODO 7: compute winner ONCE (hint: calculateWinner(squares))

  // TODO 8: compute status:
  // - if winner: `Winner: X`
  // - else: `Next: X` or `Next: O`

  function handleSquareClick(index) {
    // TODO 9: if winner exists, ignore click
    // TODO 10: if squares[index] already filled, ignore click

    // TODO 11: create copy of squares (hint: slice or [...])
    // TODO 12: set copied[index] to "X" or "O"
    // TODO 13: update squares state
    // TODO 14: flip xIsNext
  }

  function reset() {
    // TODO 15: reset squares + xIsNext
  }

  return (
    <div>
      <h2>Tic Tac Toe</h2>

      {/* TODO 16: show status */}

      <Board
        squares={/* TODO 17 */}
        onSquareClick={/* TODO 18 */}
      />

      <button onClick={/* TODO 19 */}>Reset</button>
    </div>
  );
}
```

✅ Final test expectations:

* X/O alternate
* can’t overwrite squares
* winner stops further moves
* status shows “Winner: X/O”
* Reset clears the board

---

## Your “submission order” (so it stays manageable)

1. Paste your completed `Square.jsx`
2. Then `Row.jsx`
3. Then `Board.jsx`
4. Finally `App.jsx`

If you paste all at once, I’ll still grade it — but step-by-step keeps it more “test-like.”
