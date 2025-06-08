// File: controllers/logController.js
const Log = require('../models/log');

const logController = {
    /**
     * @route   POST /api/logs
     * @desc    Create a new log entry
     * @access  Private
     */
    createLog: async (req, res) => {
        try {
            const { boxId, status, message, responseCode } = req.body;

            // Basic validation
            if (boxId === undefined || !status || !message || responseCode === undefined) {
                return res.status(400).json({ success: false, message: 'Missing required fields: boxId, status, message, responseCode' });
            }

            const newLog = new Log({
                boxId,
                status,
                message,
                responseCode,
                user: req.user.id
            });

            await newLog.save();
            res.status(201).json({ success: true, message: 'Log created successfully', log: newLog });

        } catch (err) {
            console.error('Error creating log:', err.message);
            res.status(500).json({ success: false, message: 'Server Error', error: err.message });
        }
    },

    /**
     * @route   GET /api/logs
     * @desc    Get all logs for the currently logged-in user
     * @access  Private
     */
    getLogs: async (req, res) => {
        try {
            const logs = await Log.find({ user: req.user.id }).sort({ createdAt: -1 });

            res.json({ success: true, logs });

        } catch (err) {
            console.error('Error fetching logs:', err.message);
            res.status(500).json({ success: false, message: 'Server Error', error: err.message });
        }
    }
};

module.exports = logController;