const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const BoxSchema = new Schema({
    boxId: {
        type: Number,
        required: [true, 'Box ID is required.'],
        unique: true
    },
    customName: {
        type: String,
        required: false
    },
    location: {
        type: String,
        default: 'Neznana lokacija'
    },
    user: {
        type: Schema.Types.ObjectId,
        ref: 'User',
        default: null
    }
}, {
    timestamps: true
});

module.exports = mongoose.model('Box', BoxSchema);