var express = require('express');
var router = express.Router();
var userModelController = require('../controllers/userModelController.js');

/*
 * GET
 */
router.get('/', userModelController.list);

/*
 * GET
 */
router.get('/:id', userModelController.show);

/*
 * POST
 */
router.post('/', userModelController.create);

/*
 * PUT
 */
router.put('/:id', userModelController.update);

/*
 * DELETE
 */
router.delete('/:id', userModelController.remove);

module.exports = router;
