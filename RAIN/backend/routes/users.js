const express = require('express');
const router = express.Router();

/* GET users listing. */
router.get('/', function(req, res, next) {
  res.json({ users: [] });
});

/* GET user by ID. */
router.get('/:id', function(req, res, next) {
  res.json({ user: { id: req.params.id, name: 'Sample User' } });
});

/* POST create new user. */
router.post('/', function(req, res, next) {
  res.status(201).json({ message: 'User created successfully', user: req.body });
});

module.exports = router;