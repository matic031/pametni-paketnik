const express = require('express');
const router = express.Router();
const logController = require('../controllers/logController');
const auth = require('../middleware/auth');


router.use(auth);

router.post('/', logController.createLog);

router.get('/', logController.getLogs);

module.exports = router;