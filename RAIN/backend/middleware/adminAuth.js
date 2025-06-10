const adminAuth = (req, res, next) => {
    if (req.user && req.user.isAdmin) {
        next();
    } else {
        res.status(403).json({
            success: false,
            message: 'Dostop zavrnjen. Potrebne so administratorske pravice.'
        });
    }
};

module.exports = adminAuth;