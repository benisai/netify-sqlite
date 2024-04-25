// Filename: deviceCountRoute.js

const express = require('express');
const router = express.Router();
const sqlite3 = require('sqlite3').verbose();

// Connect to the SQLite database
const db = new sqlite3.Database('../database/netifyDB.sqlite', (err) => {
  if (err) {
    console.error('Database connection error:', err.message);
  } else {
    console.log('Connected to the SQLite database.');
  }
});

// Define the route to fetch the total number of unique devices
router.get('/devices/count', (req, res) => {
  const query = `
    SELECT COUNT(DISTINCT hostname) AS deviceCount
    FROM netify_flow
  `;

  db.get(query, (err, row) => {
    if (err) {
      console.error(err);
      res.status(500).json({ error: 'Failed to fetch device count from the database' });
    } else {
      res.json({ deviceCount: row.deviceCount });
    }
  });
});

module.exports = router;
