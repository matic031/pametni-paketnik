const jwt = require('jsonwebtoken');

const JWT_SECRET = process.env.JWT_SECRET || 'pametni_paketnik_secret_key';

/**
 * Authentication middleware
 */
const auth = (req, res, next) => {
    const authHeader = req.headers.authorization;

    if (!authHeader || !authHeader.startsWith('Bearer ')) {
        return res.status(401).json({
            success: false,
            message: 'Dostop zavrnjen. Potrebna je prijava.'
        });
    }

    const token = authHeader.split(' ')[1];     // remove "Bearer" string form token

    try {
        const decoded = jwt.verify(token, JWT_SECRET);

        req.user = decoded;
        next();
    } catch (error) {
        return res.status(401).json({
            success: false,
            message: 'Neveljaven žeton. Prosimo, prijavite se ponovno.',
            error: error.message
        });
    }
};

module.exports = auth;