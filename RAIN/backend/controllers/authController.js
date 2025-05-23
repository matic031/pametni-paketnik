const User = require('../models/User');
const jwt = require('jsonwebtoken');

const JWT_SECRET = process.env.JWT_SECRET || 'pametni_paketnik_secret_key';

/**
 * Authentication controller
 */
const authController = {
    register: async (req, res) => {
        try {
            const { username, email, password, name, lastName } = req.body;

            const existingUser = await User.findOne({
                $or: [{ email }, { username }]
            });

            if (existingUser) {
                return res.status(400).json({
                    success: false,
                    message: 'Uporabnik s tem e-poštnim naslovom ali uporabniškim imenom že obstaja'
                });
            }

            const newUser = new User({
                username,
                email,
                password,
                name,
                lastName
            });

            await newUser.save();

            const userToReturn = newUser.toObject();
            delete userToReturn.password;

            res.status(201).json({
                success: true,
                message: 'Uporabnik uspešno registriran',
                user: userToReturn
            });
        } catch (error) {
            res.status(500).json({
                success: false,
                message: 'Napaka pri registraciji uporabnika',
                error: error.message
            });
        }
    },

    /**
     * Login user
     */
    login: async (req, res) => {
        try {
            const { username, password } = req.body;

            const user = await User.findOne({ username });
            if (!user) {
                return res.status(401).json({
                    success: false,
                    message: 'Napačno uporabniško ime ali geslo'
                });
            }

            const isMatch = await user.comparePassword(password);
            if (!isMatch) {
                return res.status(401).json({
                    success: false,
                    message: 'Napačno uporabniško ime ali geslo'
                });
            }

            const payload = {
                id: user._id,
                username: user.username,
                isAdmin: user.isAdmin
            };

            const token = jwt.sign(
                payload,
                JWT_SECRET,
                { expiresIn: '24h' }
            );

            res.json({
                success: true,
                message: 'Prijava uspešna',
                token: `Bearer ${token}`,
                user: {
                    id: user._id,
                    username: user.username,
                    email: user.email,
                    name: user.name,
                    lastName: user.lastName
                }
            });
        } catch (error) {
            res.status(500).json({
                success: false,
                message: 'Napaka pri prijavi',
                error: error.message
            });
        }
    },

    /**
     * Get current user profile
     */
    getCurrentUser: async (req, res) => {
        try {
            const user = await User.findById(req.user.id).select('-password');

            if (!user) {
                return res.status(404).json({
                    success: false,
                    message: 'Uporabnik ni bil najden'
                });
            }

            res.json({
                success: true,
                user
            });
        } catch (error) {
            res.status(500).json({
                success: false,
                message: 'Napaka pri pridobivanju profila',
                error: error.message
            });
        }
    }
};

module.exports = authController;