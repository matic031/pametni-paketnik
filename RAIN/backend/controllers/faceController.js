const axios = require('axios');
const User = require('../models/User');

const FACE_API_URL = process.env.FACE_API_URL || 'http://localhost:5000';

/**
 * 2FA Face Recognition Controller
 */
const faceController = {

    /**
     * Register user's face for 2FA
     */
    registerFace: async (req, res) => {
        try {
            console.log('Face registration request received');

            // Check if user is authenticated
            if (!req.user || !req.user.id) {
                return res.status(401).json({
                    success: false,
                    message: 'Authentication required'
                });
            }

            const userId = req.user.id;

            if (!req.file) {
                return res.status(400).json({
                    success: false,
                    message: 'No image file provided'
                });
            }

            const FormData = require('form-data');
            const formData = new FormData();
            formData.append('user_id', userId);
            formData.append('image', req.file.buffer, {
                filename: req.file.originalname,
                contentType: req.file.mimetype
            });

            console.log(`Sending face registration to ${FACE_API_URL}/register for user ${userId}`);

            const response = await axios.post(`${FACE_API_URL}/register`, formData, {
                headers: {
                    ...formData.getHeaders(),
                },
                timeout: 30000
            });

            if (response.data.success) {
                await User.findByIdAndUpdate(userId, {
                    faceRegistered: true,
                    faceRegisteredAt: new Date()
                });

                console.log(`Face registration successful for user ${userId}`);

                return res.json({
                    success: true,
                    message: 'Face registered successfully for 2FA',
                    embeddings_count: response.data.embeddings_count
                });
            } else {
                return res.status(400).json({
                    success: false,
                    message: response.data.message || 'Face registration failed'
                });
            }

        } catch (error) {
            console.error('Face registration error:', error.message);

            if (error.response) {
                return res.status(error.response.status || 500).json({
                    success: false,
                    message: error.response.data?.message || 'Face registration failed'
                });
            } else if (error.code === 'ECONNREFUSED') {
                return res.status(503).json({
                    success: false,
                    message: 'Face recognition service unavailable'
                });
            } else {
                return res.status(500).json({
                    success: false,
                    message: 'Internal server error during face registration'
                });
            }
        }
    },

    /**
     * Verify user's face for 2FA login
     */
    verifyFace: async (req, res) => {
        try {
            console.log('Face verification request received');

            const { user_id } = req.body;

            if (!user_id) {
                return res.status(400).json({
                    success: false,
                    message: 'user_id is required'
                });
            }

            const user = await User.findById(user_id);
            if (!user) {
                return res.status(404).json({
                    success: false,
                    message: 'User not found'
                });
            }

            if (!user.faceRegistered) {
                return res.status(400).json({
                    success: false,
                    message: 'User has not registered face for 2FA'
                });
            }

            if (!req.file) {
                return res.status(400).json({
                    success: false,
                    message: 'No image file provided'
                });
            }

            const FormData = require('form-data');
            const formData = new FormData();
            formData.append('user_id', user_id);
            formData.append('image', req.file.buffer, {
                filename: req.file.originalname,
                contentType: req.file.mimetype
            });

            console.log(`Sending face verification to ${FACE_API_URL}/verify for user ${user_id}`);

            const response = await axios.post(`${FACE_API_URL}/verify`, formData, {
                headers: {
                    ...formData.getHeaders(),
                },
                timeout: 30000 // 30 second timeout
            });

            if (response.data.success) {
                const { verified, similarity_score, threshold } = response.data;

                if (verified) {
                    await User.findByIdAndUpdate(user_id, {
                        lastFaceVerification: new Date()
                    });

                    console.log(`Face verification successful for user ${user_id} (score: ${similarity_score})`);

                    return res.json({
                        success: true,
                        verified: true,
                        message: 'Verifikacija obraza uspešna',
                        similarity_score,
                        threshold
                    });
                } else {
                    console.log(`Face verification failed for user ${user_id} (score: ${similarity_score})`);

                    return res.status(401).json({
                        success: false,
                        verified: false,
                        message: 'Verifikacija obraza ni uspela - obraz se ne ujema',
                        similarity_score,
                        threshold
                    });
                }
            } else {
                return res.status(400).json({
                    success: false,
                    message: response.data.message || 'Face verification failed'
                });
            }

        } catch (error) {
            console.error('Face verification error:', error.message);

            if (error.response) {
                return res.status(error.response.status || 500).json({
                    success: false,
                    message: error.response.data?.message || 'Face verification failed'
                });
            } else if (error.code === 'ECONNREFUSED') {
                return res.status(503).json({
                    success: false,
                    message: 'Face recognition service unavailable'
                });
            } else {
                return res.status(500).json({
                    success: false,
                    message: 'Internal server error during face verification'
                });
            }
        }
    },

    /**
     * Check if user has face registered
     */
    getFaceStatus: async (req, res) => {
        try {
            const userId = req.user.id;

            const user = await User.findById(userId);
            if (!user) {
                return res.status(404).json({
                    success: false,
                    message: 'User not found'
                });
            }

            return res.json({
                success: true,
                faceRegistered: user.faceRegistered || false,
                faceRegisteredAt: user.faceRegisteredAt || null,
                lastFaceVerification: user.lastFaceVerification || null
            });

        } catch (error) {
            console.error('Face status error:', error);
            return res.status(500).json({
                success: false,
                message: 'Internal server error'
            });
        }
    },

    /**
     * Delete user's face registration
     */
    deleteFace: async (req, res) => {
        try {
            const userId = req.user.id;

            try {
                await axios.delete(`${FACE_API_URL}/user/${userId}`, {
                    timeout: 10000
                });
            } catch (apiError) {
                console.warn(`Warning: Could not delete face data from API for user ${userId}:`, apiError.message);
            }

            await User.findByIdAndUpdate(userId, {
                faceRegistered: false,
                faceRegisteredAt: null,
                lastFaceVerification: null
            });

            return res.json({
                success: true,
                message: 'Face registration deleted successfully'
            });

        } catch (error) {
            console.error('Face deletion error:', error);
            return res.status(500).json({
                success: false,
                message: 'Internal server error during face deletion'
            });
        }
    }
};

module.exports = faceController;
