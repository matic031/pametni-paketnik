const User = require('../models/User');

const userController = {

    getAllUsers: async (req, res) => {
        try {
            const users = await User.find({}).select('-password').sort({ username: 1 });
            res.json({ success: true, users });
        } catch (err) {
            console.error('Error fetching users:', err.message);
            res.status(500).json({ success: false, message: 'Napaka na strežniku.' });
        }
    },


    toggleAdminStatus: async (req, res) => {
        try {
            const userToUpdate = await User.findById(req.params.id);

            if (!userToUpdate) {
                return res.status(404).json({ success: false, message: 'Uporabnik ni bil najden.' });
            }

            // KLJUČNO VARNOSTNO PREVERJANJE: Admin si ne sme sam odvzeti pravic!
            if (req.user.id === userToUpdate.id) {
                return res.status(403).json({ success: false, message: 'Ne morete spremeniti lastnih administratorskih pravic.' });
            }

            // Spremenimo status
            userToUpdate.isAdmin = !userToUpdate.isAdmin;
            await userToUpdate.save();

            // Pošljemo nazaj posodobljenega uporabnika (brez gesla)
            const updatedUser = userToUpdate.toObject();
            delete updatedUser.password;

            res.json({ success: true, message: `Status uporabnika ${userToUpdate.username} je bil posodobljen.`, user: updatedUser });

        } catch (err) {
            console.error('Error toggling admin status:', err.message);
            res.status(500).json({ success: false, message: 'Napaka na strežniku.' });
        }
    }
};

module.exports = userController;