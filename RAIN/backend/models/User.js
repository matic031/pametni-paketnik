const mongoose = require('mongoose');
const bcrypt = require('bcrypt');
const Schema = mongoose.Schema;

const UserSchema = new Schema({
    username: {
        type: String,
        required: true,
        unique: true
    },
    email: {
        type: String,
        required: true,
        unique: true
    },
    password: {
        type: String,
        required: true
    },
    name: {
        type: String,
        required: false
    },
    lastName: {
        type: String,
        required: false
    },
    isAdmin: {
        type: Boolean,
        default: false
    },
    faceRegistered: {
        type: Boolean,
        default: false
    },
    faceRegisteredAt: {
        type: Date,
        default: null
    },
    lastFaceVerification: {
        type: Date,
        default: null
    }
}, {
    timestamps: true
});

UserSchema.pre('save', async function (next) {
    try {
        if (!this.isModified('password')) {
            return next();
        }

        const salt = bcrypt.genSaltSync(10);

        this.password = bcrypt.hashSync(this.password, salt);

        return next();
    } catch (error) {
        console.error('Password hashing error:', error);
        return next(error);
    }
});

UserSchema.methods.comparePassword = async function (candidatePassword) {
    try {
        return await bcrypt.compare(candidatePassword, this.password);
    } catch (error) {
        console.error('Password comparison error:', error);
        return false;
    }
};

module.exports = mongoose.model('User', UserSchema);