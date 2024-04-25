// app.js
const express = require('express');
const bodyParser = require('body-parser');
const sqlite3 = require('sqlite3').verbose();

const router = express.Router();
const db = new sqlite3.Database('../database/netifyDB.sqlite', (err) => {
  if (err) {
    console.error('Database connection error:', err.message);
  } else {
    console.log('Connected to the SQLite database.');
  }
});

router.use(bodyParser.json());

// Define the array of column names
const columns = [
  'timeinsert',
  'hostname',
  'local_ip',
  'local_mac',
  'local_port',
  'fqdn',    
  'dest_ip',
  'dest_mac',
  'dest_port',
  'dest_type',
  'detected_protocol_name',
  'detected_app_name',
  'digest',
  'first_seen_at',
  'first_update_at',
  'vlan_id',
  'interface',
  'internal',
  'ip_version',
  'last_seen_at',
  'type',
  'dest_country',
  'dest_state',
  'dest_city',
  'risk_score',
  'risk_score_client',
  'risk_score_server'
];

// Set up the route to fetch data from the SQLite database
router.get('/data', (req, res) => {
  const query = `
    SELECT ${columns.join(', ')}
    FROM netify_flow
  `;

  db.all(query, (err, rows) => {
    if (err) {
      console.error(err);
      res.status(500).json({ error: 'Failed to fetch data from the database' });
    } else {
      res.json(rows);
    }
  });
});

// Add new data to the database
router.post('/data', (req, res) => {
  const data = req.body;

  const query = `
    INSERT INTO netify (${columns.join(', ')})
    VALUES (${columns.map(() => '?').join(', ')})
  `;

  db.run(query, columns.map(col => data[col]), function (err) {
    if (err) {
      console.error(err);
      res.status(500).json({ error: 'Failed to add data to the database' });
    } else {
      res.json({ id: this.lastID });
    }
  });
});

// Update data in the database
router.put('/data/:id', (req, res) => {
  const data = req.body;
  const id = req.params.id;

  const setClause = columns.map(col => `${col} = ?`).join(', ');
  const query = `
    UPDATE netify SET ${setClause}
    WHERE rowid = ?
  `;

  db.run(query, [...columns.map(col => data[col]), id], function (err) {
    if (err) {
      console.error(err);
      res.status(500).json({ error: 'Failed to update data in the database' });
    } else {
      res.json({ message: 'Data updated successfully.' });
    }
  });
});

// Delete data from the database
router.delete('/data/:id', (req, res) => {
  const id = req.params.id;
  const query = `DELETE FROM netify WHERE rowid = ?`;

  db.run(query, id, function (err) {
    if (err) {
      console.error(err);
      res.status(500).json({ error: 'Failed to delete data from the database' });
    } else {
      res.json({ message: 'Data deleted successfully.' });
    }
  });
});

// Delete data from the database based on a specific condition
router.delete('/data', (req, res) => {
  const condition = req.query.condition;
  if (!condition) {
    return res.status(400).json({ error: 'Missing condition parameter in the request query.' });
  }

  const query = `DELETE FROM netify WHERE ${condition}`;

  db.run(query, function (err) {
    if (err) {
      console.error(err);
      res.status(500).json({ error: 'Failed to delete data from the database' });
    } else {
      res.json({ message: `Data matching condition "${condition}" deleted successfully.` });
    }
  });
});

// Update data in the database where a specific column matches the given value
router.put('/data/by-column-value', (req, res) => {
  const { column, value } = req.query;
  if (!column || !value) {
    return res.status(400).json({ error: 'Missing column or value parameter in the request query.' });
  }

  const updateFields = req.body;
  const setClause = Object.keys(updateFields).map(col => `${col} = ?`).join(', ');

  const query = `UPDATE netify SET ${setClause} WHERE ${column} = ?`;

  db.run(
    query,
    [...Object.values(updateFields), value],
    function (err) {
      if (err) {
        console.error(err);
        res.status(500).json({ error: 'Failed to update data in the database' });
      } else {
        res.json({ message: `Data where ${column} = "${value}" updated successfully.` });
      }
    }
  );
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

module.exports = {
  router,
  connectToSQLite: () => {
    return db;
  }
};
