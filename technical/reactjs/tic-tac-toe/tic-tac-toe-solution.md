Below is a **neat, follow-along tutorial** from **Vite setup → final working Tic-Tac-Toe** using the approach you liked: **one flat `squares` array + index math**, minimal/no CSS, and clean component flow: **App → Board → Row → Square**.

---

## 0) Create the React project (Vite)

```bash
npm create vite@latest tic-tac-toe -- --template react
cd tic-tac-toe
npm install
npm run dev
```

Open the local dev URL Vite prints.

Now clean the starter files.

---

## 1) Clean the starter

### `src/App.jsx`

Replace it completely (we’ll build it in step 3, for now just keep a placeholder):

```jsx
export default function App() {
  return <div>Loading...</div>;
}
```

### `src/main.jsx`

Leave as-is (Vite already renders `<App />`).

Optional: delete `src/App.css` and remove any import of it if present.

---

## 2) Create your component files

Create these files in `src/`:

* `Board.jsx`
* `Row.jsx`
* `Square.jsx`

So you’ll have:

```
src/
  App.jsx
  Board.jsx
  Row.jsx
  Square.jsx
  main.jsx
```

---

## 3) Build Square (smallest component)

### `src/Square.jsx`

```jsx
export default function Square({ value, onClick }) {
  return <button onClick={onClick}>{value}</button>;
}
```

That’s it. No state here.

---

## 4) Build Row (index math, no slicing)

Row receives:

* `rowIndex` (0,1,2)
* full `squares` array (length 9)
* `onSquareClick(boardIndex)`

### `src/Row.jsx`

```jsx
import Square from "./Square";

export default function Row({ rowIndex, squares, onSquareClick }) {
  const rowStart = rowIndex * 3;

  return (
    <div>
      {[0, 1, 2].map((colIndex) => {
        const boardIndex = rowStart + colIndex;

        return (
          <Square
            key={boardIndex}
            value={squares[boardIndex]}
            onClick={() => onSquareClick(boardIndex)}
          />
        );
      })}
    </div>
  );
}
```

---

## 5) Build Board (renders 3 rows)

Board receives:

* `squares`
* `onSquareClick`

### `src/Board.jsx`

```jsx
import Row from "./Row";

export default function Board({ squares, onSquareClick }) {
  return (
    <div>
      {[0, 1, 2].map((rowIndex) => (
        <Row
          key={rowIndex}
          rowIndex={rowIndex}
          squares={squares}
          onSquareClick={onSquareClick}
        />
      ))}
    </div>
  );
}
```

---

## 6) Build App (state lives here)

App owns:

* `squares` (Array(9).fill(null))
* `xIsNext` (boolean)
* click handler
* status line

### `src/App.jsx`

```jsx
import { useState } from "react";
import Board from "./Board";

function calculateWinner(squares) {
  const lines = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8], // rows
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8], // cols
    [0, 4, 8],
    [2, 4, 6], // diagonals
  ];

  for (const [a, b, c] of lines) {
    if (squares[a] && squares[a] === squares[b] && squares[a] === squares[c]) {
      return squares[a];
    }
  }

  return null;
}

export default function App() {
  const [squares, setSquares] = useState(Array(9).fill(null));
  const [xIsNext, setXIsNext] = useState(true);

  const winner = calculateWinner(squares);
  const status = winner
    ? `Winner: ${winner}`
    : `Next: ${xIsNext ? "X" : "O"}`;

  function handleSquareClick(index) {
    if (winner) return;
    if (squares[index]) return;

    const next = squares.slice();
    next[index] = xIsNext ? "X" : "O";

    setSquares(next);
    setXIsNext(!xIsNext);
  }

  function reset() {
    setSquares(Array(9).fill(null));
    setXIsNext(true);
  }

  return (
    <div>
      <h2>Tic Tac Toe</h2>
      <div>{status}</div>

      <Board squares={squares} onSquareClick={handleSquareClick} />

      <button onClick={reset}>Reset</button>
    </div>
  );
}
```

Run your app (it should already be running from `npm run dev`). You should now have:

* clickable 3×3
* alternating X/O
* no overwriting
* winner detection
* reset

---

## 7) Tiny optional “minimum CSS” (only if you want a visible grid)

You said “without minimum css”, so skip this.
But if you want the squares to look like a grid, you can use **inline style** without a stylesheet. Example:

In `Square.jsx`, add minimal style:

```jsx
export default function Square({ value, onClick }) {
  return (
    <button
      onClick={onClick}
      style={{ width: 40, height: 40, margin: 2 }}
    >
      {value}
    </button>
  );
}
```

That’s still “no CSS file”.

---

## What you should understand after following this

* **State lives at the top** (App)
* **Board/Row/Square are pure** and just render UI
* A flat array + index math is clean and scalable

---

