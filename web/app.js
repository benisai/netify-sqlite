// app.js
const express = require('express');
const app = express();
const sqliteNetify = require('./js/sqlite-netify');
const deviceCountRoute = require('./js/clients/deviceCountRoute');

// Mount the device count route
app.use('/api', deviceCountRoute);



// Connect to the SQLite database
const db = sqliteNetify.connectToSQLite();

// Use the API routes from sqliteNetify
app.use('/', sqliteNetify.router);

// Serve static files from the "public" directory
app.use(express.static('public'));

// Define a route handler for the dashboard page
app.get('/dashboard', (req, res) => {
  res.sendFile(__dirname + '/pages/dashboard.html');
});

// Define a route handler for the devices page
app.get('/devices', (req, res) => {
  res.sendFile(__dirname + '/pages/devices.html');
});

// Define a route handler for the netify page
app.get('/netify', (req, res) => {
  res.sendFile(__dirname + '/pages/netify.html');
});

// Define a route handler for the root path
app.get('/', (req, res) => {
  res.redirect('/netify'); // Redirect to the dashboard page by default
});

// Start the server
const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
