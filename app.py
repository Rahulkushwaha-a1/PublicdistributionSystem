// app.js - Public Distribution System
// Run: npm install express better-sqlite3 bcrypt body-parser
// Start: node app.js

const express = require("express");
const bcrypt = require("bcrypt");
const bodyParser = require("body-parser");
const Database = require("better-sqlite3");
const path = require("path");

const app = express();
const PORT = 4000;

// Middleware
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, "public"))); // serve frontend

// Database setup
const db = new Database("pds.sqlite");
db.exec(`
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT,
  role TEXT CHECK(role IN ('admin','dealer','beneficiary')),
  ration_card TEXT UNIQUE,
  password_hash TEXT
);

CREATE TABLE IF NOT EXISTS stock (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  item TEXT,
  quantity INTEGER,
  unit TEXT
);

CREATE TABLE IF NOT EXISTS feedback (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER,
  rating INTEGER,
  comment TEXT,
  date DATETIME DEFAULT CURRENT_TIMESTAMP
);
`);

// Seed if empty
if (db.prepare("SELECT COUNT(*) as c FROM users").get().c === 0) {
  const hash = (p) => bcrypt.hashSync(p, 10);
  db.prepare("INSERT INTO users (name,role,ration_card,password_hash) VALUES (?,?,?,?)")
    .run("Admin", "admin", "ADMIN-1", hash("admin123"));
  db.prepare("INSERT INTO users (name,role,ration_card,password_hash) VALUES (?,?,?,?)")
    .run("Dealer One", "dealer", "DEALER-1", hash("dealer123"));
  db.prepare("INSERT INTO users (name,role,ration_card,password_hash) VALUES (?,?,?,?)")
    .run("User Beneficiary", "beneficiary", "RC-1001", hash("user123"));
  db.prepare("INSERT INTO stock (item,quantity,unit) VALUES (?,?,?)")
    .run("Rice", 1000, "kg");
  db.prepare("INSERT INTO stock (item,quantity,unit) VALUES (?,?,?)")
    .run("Wheat", 800, "kg");
  db.prepare("INSERT INTO stock (item,quantity,unit) VALUES (?,?,?)")
    .run("Sugar", 500, "kg");
  console.log("Seeded default users (admin123 / dealer123 / user123).");
}

// ---------------- API Endpoints ----------------

// Login
app.post("/api/login", (req, res) => {
  const { ration_card, password, role } = req.body;
  const user = db.prepare("SELECT * FROM users WHERE ration_card=? AND role=?").get(ration_card, role);
  if (!user) return res.status(400).json({ error: "User not found" });
  if (!bcrypt.compareSync(password, user.password_hash)) {
    return res.status(401).json({ error: "Invalid password" });
  }
  res.json({ id: user.id, name: user.name, role: user.role });
});

// Get stock
app.get("/api/stock", (req, res) => {
  res.json(db.prepare("SELECT * FROM stock").all());
});

// Add stock (admin)
app.post("/api/stock", (req, res) => {
  const { item, quantity } = req.body;
  db.prepare("INSERT INTO stock (item,quantity,unit) VALUES (?,?,?)").run(item, quantity, "kg");
  res.json({ success: true });
});

// Distribute ration (dealer)
app.post("/api/distribute", (req, res) => {
  const { ration_card, item, qty } = req.body;
  const stock = db.prepare("SELECT * FROM stock WHERE item=?").get(item);
  if (!stock || stock.quantity < qty) return res.status(400).json({ error: "Insufficient stock" });
  db.prepare("UPDATE stock SET quantity=quantity-? WHERE id=?").run(qty, stock.id);
  res.json({ success: true });
});

// Feedback
app.post("/api/feedback", (req, res) => {
  const { user_id, rating, comment } = req.body;
  db.prepare("INSERT INTO feedback (user_id,rating,comment) VALUES (?,?,?)").run(user_id, rating, comment);
  res.json({ success: true });
});

app.get("/api/feedback", (req, res) => {
  res.json(db.prepare("SELECT * FROM feedback ORDER BY date DESC").all());
});

// ------------------------------------------------
app.listen(PORT, () => console.log(`PDS running on http://localhost:${PORT}`));
