var UsermodelModel = require('../models/userModelModel.js');

/**
 * userModelController.js
 *
 * @description :: Server-side logic for managing userModels.
 */
module.exports = {

    /**
     * userModelController.list()
     */
    list: function (req, res) {
        UsermodelModel.find(function (err, userModels) {
            if (err) {
                return res.status(500).json({
                    message: 'Error when getting userModel.',
                    error: err
                });
            }

            return res.json(userModels);
        });
    },

    /**
     * userModelController.show()
     */
    show: function (req, res) {
        var id = req.params.id;

        UsermodelModel.findOne({_id: id}, function (err, userModel) {
            if (err) {
                return res.status(500).json({
                    message: 'Error when getting userModel.',
                    error: err
                });
            }

            if (!userModel) {
                return res.status(404).json({
                    message: 'No such userModel'
                });
            }

            return res.json(userModel);
        });
    },

    /**
     * userModelController.create()
     */
    create: function (req, res) {
        var userModel = new UsermodelModel({
			username : req.body.username,
			password : req.body.password,
			email : req.body.email
        });

        userModel.save(function (err, userModel) {
            if (err) {
                return res.status(500).json({
                    message: 'Error when creating userModel',
                    error: err
                });
            }

            return res.status(201).json(userModel);
        });
    },

    /**
     * userModelController.update()
     */
    update: function (req, res) {
        var id = req.params.id;

        UsermodelModel.findOne({_id: id}, function (err, userModel) {
            if (err) {
                return res.status(500).json({
                    message: 'Error when getting userModel',
                    error: err
                });
            }

            if (!userModel) {
                return res.status(404).json({
                    message: 'No such userModel'
                });
            }

            userModel.username = req.body.username ? req.body.username : userModel.username;
			userModel.password = req.body.password ? req.body.password : userModel.password;
			userModel.email = req.body.email ? req.body.email : userModel.email;
			
            userModel.save(function (err, userModel) {
                if (err) {
                    return res.status(500).json({
                        message: 'Error when updating userModel.',
                        error: err
                    });
                }

                return res.json(userModel);
            });
        });
    },

    /**
     * userModelController.remove()
     */
    remove: function (req, res) {
        var id = req.params.id;

        UsermodelModel.findByIdAndRemove(id, function (err, userModel) {
            if (err) {
                return res.status(500).json({
                    message: 'Error when deleting the userModel.',
                    error: err
                });
            }

            return res.status(204).json();
        });
    }
};
