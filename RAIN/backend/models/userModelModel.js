var mongoose = require('mongoose');
var Schema   = mongoose.Schema;

var userModelSchema = new Schema({
	'username' : String,
	'password' : String,
	'email' : String
});

module.exports = mongoose.model('userModel', userModelSchema);
