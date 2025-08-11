const express = require("express");
const cors = require("cors");
require("dotenv").config();

const app = express();
const PORT = process.env.PORT || 5002;

// Middleware
app.use(cors());
app.use(express.json());

// Import routes
const mlRoutes = require("./routes/ml");

// Routes
app.use("/api/ml", mlRoutes);

// Test Route
app.get("/", (req, res) => {
  res.send("🎉 Backend is running successfully!");
});

app.listen(PORT, () => {
  console.log(`✅ Backend server is running at http://localhost:${PORT}`);
  console.log(`🤖 ML API routes available at http://localhost:${PORT}/api/ml`);
});
