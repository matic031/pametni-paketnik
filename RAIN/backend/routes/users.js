const express = require('express');
const router = express.Router();
const userController = require('../controllers/userController');
const auth = require('../middleware/auth');
const adminAuth = require('../middleware/adminAuth');



/* GET user by ID. */
router.get('/:id', function(req, res, next) {
  res.json({ user: { id: req.params.id, name: 'Sample User' } });
});

/* POST create new user. */
router.post('/', function(req, res, next) {
  res.status(201).json({ message: 'User created successfully', user: req.body });
});

router.get('/', [auth, adminAuth], userController.getAllUsers);

router.put('/:id/toggle-admin', [auth, adminAuth], userController.toggleAdminStatus);

module.exports = router;