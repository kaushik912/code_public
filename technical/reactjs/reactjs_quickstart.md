## ReactJS QuickStrt

1. Install Node.js and npm (if not installed).
```
node -v  # Should show a version number
npm -v   # Should show a version number
```

2. Create a React app
```
npx create-react-app my-react-app
```

4. Go into the project folder
```
cd my-react-app
```

5. Start the development server
```
npm start
```

### Editing
Now you can open src/App.js (or any other file) in your code editor (such as VSCode) and start writing your React code.
```
import React from 'react';

function App() {
  return (
    <div>
      <h1>Hello, React!</h1>
    </div>
  );
}

export default App;
```

### Speed up Creation Tip
If you're creating multiple React apps or doing it regularly, installing create-react-app globally might help because the global package is cached and doesn't need to be downloaded every time.

```
npm install -g create-react-app
create-react-app my-app
```

