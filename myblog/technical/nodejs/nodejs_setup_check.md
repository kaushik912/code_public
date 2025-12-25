# NPM Health Check

## 0) Quick sanity: versions + registry + connectivity

```bash
node -v
npm -v
npm config get registry
npm ping
```

Expected:

* registry should be `https://registry.npmjs.org/`
* `npm ping` should return quickly with `PONG`

If `npm ping` hangs or errors, npm itself is fine but **network/DNS/proxy/VPN** is likely the issue.

---

## 1) Create a sample npm project (no frameworks)

```bash
mkdir npm-test && cd npm-test
npm init -y
```

This should create `package.json`.

---

## 2) Install lodash and run a quick script

Install:

```bash
npm install lodash
```

Create `index.js`:

```bash
cat > index.js <<'EOF'
const _ = require("lodash");

const nums = [1, 2, 3, 4, 5];
console.log("chunk:", _.chunk(nums, 2));
console.log("sum:", _.sum(nums));
EOF
```

Run it:

```bash
node index.js
```

You should see chunk + sum output. If install worked and this runs, npm is basically working.

---

## 3) Check npm scripts work

Add a script in `package.json` (quick way using npm itself):

```bash
npm pkg set scripts.start="node index.js"
npm run start
```

