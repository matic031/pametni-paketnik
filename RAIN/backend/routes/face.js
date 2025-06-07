const express = require('express');
const router = express.Router();
const faceController = require('../controllers/faceController');
const auth = require('../middleware/auth');
const upload = require('../middleware/upload');

router.post('/register', auth, upload.single('image'), faceController.registerFace);
router.get('/status', auth, faceController.getFaceStatus);
router.delete('/delete', auth, faceController.deleteFace);

router.post('/verify', upload.single('image'), faceController.verifyFace);

module.exports = router;
