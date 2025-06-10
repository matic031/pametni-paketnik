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

            if (!username || !email || !password) {
                return res.status(400).json({
                    success: false,
                    message: 'Required fields missing'
                });
            }

            const existingUser = await User.findOne({
                $or: [{ email }, { username }]
            });

            if (existingUser) {
                return res.status(409).json({
                    success: false,
                    message: 'User already exists'
                });
            }

            const newUser = new User({
                username,
                email,
                password,
                name,
                lastName
            });

            let savedUser;
            try {
                console.log('Attempting to save user...');
                savedUser = await newUser.save();
                console.log('User saved with ID:', savedUser._id);
            } catch (saveError) {
                console.error('Save error:', saveError);
                throw new Error(`Failed to save user: ${saveError.message}`);
            }

            const userToReturn = {
                id: savedUser._id,
                username: savedUser.username,
                email: savedUser.email,
                name: savedUser.name,
                lastName: savedUser.lastName
            };

            return res.status(201).json({
                success: true,
                message: 'User registered successfully',
                user: userToReturn
            });

        } catch (error) {
            console.error('Registration error:', error);
            return res.status(500).json({
                success: false,
                message: 'Registration failed',
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

            const now = new Date();
            const twoHoursAgo = new Date(now.getTime() - 2 * 60 * 60 * 1000);
            const clientType = req.headers['x-client-type'] || 'web';

            console.log('Client type:', clientType);
            console.log('User:', user);

            if (clientType !== 'app') {
                if (!user.faceRegistered) {
                    await User.findByIdAndUpdate(user._id, {
                        pendingNotification: 'Potrebna je registracija obraza pred prvo prijavo',
                        notificationTimestamp: new Date()
                    });

                    return res.status(403).json({
                        success: false,
                        requiresFaceVerification: true,
                        message: 'Potrebna je registracija obraza pred prvo prijavo',
                        userId: user._id,
                        faceRegistered: user.faceRegistered,
                        lastFaceVerification: user.lastFaceVerification
                    });
                }

                if (user.faceRegistered &&
                    (!user.lastFaceVerification || user.lastFaceVerification < twoHoursAgo)) {
                    await User.findByIdAndUpdate(user._id, {
                        pendingNotification: 'Potrebna je ponovna verifikacija obraza',
                        notificationTimestamp: new Date()
                    });

                    return res.status(403).json({
                        success: false,
                        requiresFaceVerification: true,
                        message: 'Potrebna je ponovna verifikacija obraza',
                        userId: user._id,
                        faceRegistered: user.faceRegistered,
                        lastFaceVerification: user.lastFaceVerification
                    });
                }
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
                    lastName: user.lastName,
                    isAdmin: user.isAdmin,
                    faceRegistered: user.faceRegistered,
                    lastFaceVerification: user.lastFaceVerification
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
    },

    /**
     * Check for pending notifications (for mobile app)
     */
    checkNotifications: async (req, res) => {
        try {
            const user = await User.findById(req.user.id);

            if (!user) {
                return res.status(404).json({
                    success: false,
                    message: 'Uporabnik ni bil najden'
                });
            }

            if (user.pendingNotification) {
                await User.findByIdAndUpdate(req.user.id, {
                    pendingNotification: null,
                    notificationTimestamp: null
                });

                return res.json({
                    success: true,
                    hasNotification: true,
                    message: user.pendingNotification,
                    timestamp: user.notificationTimestamp
                });
            }

            res.json({
                success: true,
                hasNotification: false
            });
        } catch (error) {
            res.status(500).json({
                success: false,
                message: 'Napaka pri preverjanju obvestil',
                error: error.message
            });
        }
    }
};

module.exports = authController;