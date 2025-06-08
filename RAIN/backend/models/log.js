// File: models/Log.js
const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const LogSchema = new Schema({
    boxId: {
        type: Number,
        required: [true, 'Box ID is required.']
    },
    status: {
        type: String,
        enum: ['SUCCESS', 'FAILURE'],
        required: [true, 'Status is required.']
    },
    message: {
        type: String,
        required: [true, 'A message is required.']
    },

    responseCode: {
        type: Number,
        required: [true, 'Response code is required.']
    },

    user: {
        type: Schema.Types.ObjectId,
        ref: 'User',
        required: true
    }
}, {
    timestamps: true
});

module.exports = mongoose.model('Log', LogSchema);