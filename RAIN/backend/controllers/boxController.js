const Box = require('../models/Box');

const boxController = {

    claimBox: async (req, res) => {
        try {
            const { boxId, customName } = req.body;
            const userId = req.user.id;

            if (!boxId || !customName) {
                return res.status(400).json({ success: false, message: 'Manjkata ID paketnika in ime po meri.' });
            }


            const box = await Box.findOne({ boxId: boxId });

            if (!box) {
                return res.status(404).json({ success: false, message: 'Paketnik s tem ID-jem ne obstaja.' });
            }


            if (box.user) {
                // Preveri, če je lastnik trenutni uporabnik
                if (box.user.toString() === userId) {
                    return res.status(409).json({ success: false, message: 'Ta pametna omarica je že vaša.' });
                } else {
                    return res.status(409).json({ success: false, message: 'Pametna omarica je že v lasti drugega uporabnika.' });
                }
            }


            box.user = userId;
            box.customName = customName;
            await box.save();

            res.status(200).json({ success: true, message: 'Paketnik uspešno dodan!', box });

        } catch (err) {
            console.error('Error claiming box:', err.message);
            res.status(500).json({ success: false, message: 'Napaka na strežniku.', error: err.message });
        }
    },


    getUserBoxes: async (req, res) => {
        try {
            const boxes = await Box.find({ user: req.user.id }).sort({ createdAt: 'desc' });
            res.json({ success: true, boxes });
        } catch (err) {
            console.error('Error fetching user boxes:', err.message);
            res.status(500).json({ success: false, message: 'Napaka na strežniku.', error: err.message });
        }
    },

    createBox: async (req, res) => {
        try {
            const { boxId } = req.body;

            if (!boxId) {
                return res.status(400).json({ success: false, message: 'Manjka ID paketnika.' });
            }

            const existingBox = await Box.findOne({ boxId });
            if (existingBox) {
                return res.status(409).json({ success: false, message: 'Paketnik s tem ID-jem že obstaja.' });
            }

            const newBox = new Box({
                boxId
            });

            await newBox.save();
            res.status(201).json({ success: true, message: 'Nova pametna omarica uspešno ustvarjena v bazi.', box: newBox });

        } catch (err) {
            console.error('Error creating box:', err.message);
            res.status(500).json({ success: false, message: 'Napaka na strežniku.', error: err.message });
        }
    },


    getAllBoxes: async (req, res) => {
        try {
            const boxes = await Box.find({}).populate('user', 'username email').sort({ createdAt: -1 });
            res.json({ success: true, boxes });
        } catch (err) {
            console.error('Error fetching all boxes:', err.message);
            res.status(500).json({ success: false, message: 'Napaka na strežniku.', error: err.message });
        }
    },

    disownBox: async (req, res) => {
        try {
            const box = await Box.findById(req.params.id);

            if (!box) {
                return res.status(404).json({ success: false, message: 'Paketnik ni bil najden.' });
            }

            if (!box.user || box.user.toString() !== req.user.id) {
                return res.status(403).json({ success: false, message: 'Nimate dovoljenja za to dejanje.' });
            }

            box.user = null;
            box.customName = null;
            await box.save();

            res.json({ success: true, message: 'Lastništvo nad paketnikom uspešno odstranjeno.' });
        } catch (err) {
            console.error('Error disowning box:', err.message);
            res.status(500).json({ success: false, message: 'Napaka na strežniku.' });
        }
    },

    deleteBox: async (req, res) => {
        try {
            const box = await Box.findByIdAndDelete(req.params.id);

            if (!box) {
                return res.status(404).json({ success: false, message: 'Paketnik ni bil najden za brisanje.' });
            }

            res.json({ success: true, message: 'Paketnik je bil trajno izbrisan iz sistema.' });
        } catch (err) {
            console.error('Error deleting box:', err.message);
            res.status(500).json({ success: false, message: 'Napaka na strežniku.' });
        }
    }
};

module.exports = boxController;