const User = require('../models/User');
const jwt = require('jsonwebtoken');

const JWT_SECRET = process.env.JWT_SECRET || 'pametni_paketnik_secret_key';

/**
 * Authentication controller
 */
const authController = {
    register: async (req, res) => {
        try {
            console.log('Registration request received:', req.body);

            const { username, email, password, name, lastName } = req.body;

            if (!username || !email || !password) {
                console.log('Missing required fields');
                return res.status(400).json({
                    success: false,
                    message: 'Manjkajo zahtevana polja: uporabniško ime, e-pošta in geslo so obvezni'
                });
            }

            console.log('Checking if user already exists...');
            const existingUser = await User.findOne({
                $or: [{ email }, { username }]
            });

            if (existingUser) {
                console.log('User already exists');
                return res.status(400).json({
                    success: false,
                    message: 'Uporabnik s tem e-poštnim naslovom ali uporabniškim imenom že obstaja'
                });
            }

            console.log('Creating new user...');
            const newUser = new User({
                username,
                email,
                password,
                name: name || '',
                lastName: lastName || ''
            });

            console.log('Saving user to database...');
            try {
                await newUser.save();
                console.log('User saved successfully');
            } catch (saveError) {
                console.error('Error saving user:', saveError);
                return res.status(500).json({
                    success: false,
                    message: 'Napaka pri shranjevanju uporabnika',
                    error: saveError.message
                });
            }

            const userToReturn = {
                id: newUser._id,
                username: newUser.username,
                email: newUser.email,
                name: newUser.name,
                lastName: newUser.lastName
            };

            return res.status(201).json({
                success: true,
                message: 'Uporabnik uspešno registriran',
                user: userToReturn
            });
        } catch (error) {
            console.error('Error in registration:', error);
            return res.status(500).json({
                success: false,
                message: 'Napaka pri registraciji uporabnika',
                error: error.message,
                stack: process.env.NODE_ENV === 'development' ? error.stack : undefined
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