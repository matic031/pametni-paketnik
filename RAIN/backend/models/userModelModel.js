var mongoose = require('mongoose');
var Schema   = mongoose.Schema;

var userModelSchema = new Schema({
	username: {
		type: String,
		required: true,
		unique: true
	},
	password: {
		type: String,
		required: true
	},
	email: {
		type: String,
		required: true,
		unique: true
	},
	'name': String,
	'last_name': String,
	'phone': String,
},{
	timestamps: true
});

module.exports = mongoose.model('userModel', userModelSchema);
