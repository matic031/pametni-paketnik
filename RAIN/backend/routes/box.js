const express = require('express');
const router = express.Router();
const boxController = require('../controllers/boxController');
const auth = require('../middleware/auth');
const adminAuth = require('../middleware/adminAuth');


router.post('/claim',auth ,boxController.claimBox);

router.get('/',auth ,boxController.getUserBoxes);
router.delete('/:id', auth, boxController.disownBox);


router.post('/admin/create', [auth, adminAuth], boxController.createBox);
router.get('/admin/all', [auth, adminAuth], boxController.getAllBoxes);
router.delete('/admin/:id', [auth, adminAuth], boxController.deleteBox);

module.exports = router;