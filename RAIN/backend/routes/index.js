const express = require('express');
const router = express.Router();

/* GET home page. */
router.get('/', function (req, res, next) {
  res.json({ title: 'Pametni paketnik API', message: 'Message from API' });
});

module.exports = router;