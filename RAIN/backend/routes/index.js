const express = require('express');
const router = express.Router();

/* GET home page. */
router.get('/', function(req, res, next) {
  res.json({ title: 'Smart Parcel Box API', message: 'Welcome to the Smart Parcel Box API' });
});

module.exports = router;