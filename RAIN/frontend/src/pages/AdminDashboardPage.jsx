import { useState, useEffect, useContext } from "react";
import { Link } from "react-router-dom";
import { AuthContext } from "../components/AuthContext";
import axios from "axios";
import {
    FaBox, FaPlusCircle, FaSpinner, FaSignOutAlt, FaTachometerAlt, FaTrash,
    FaUsersCog, FaUserShield, FaUser
} from "react-icons/fa";

const AdminDashboardPage = () => {
    const { user: loggedInUser, logout } = useContext(AuthContext);

    const [allBoxes, setAllBoxes] = useState([]);
    const [isLoadingBoxes, setIsLoadingBoxes] = useState(true);

    const [users, setUsers] = useState([]);
    const [isLoadingUsers, setIsLoadingUsers] = useState(true);

    const [error, setError] = useState("");
    const [newBoxId, setNewBoxId] = useState("");

    const API_URL = import.meta.env.VITE_API_URL || "http://localhost:3000";

    const fetchAllData = async () => {
        setIsLoadingBoxes(true);
        setIsLoadingUsers(true);
        setError("");
        try {
            // Uporabimo Promise.all, da hkrati pošljemo oba zahtevka
            const [boxesResponse, usersResponse] = await Promise.all([
                axios.get(`${API_URL}/api/boxes/admin/all`),
                axios.get(`${API_URL}/api/users`)
            ]);
            setAllBoxes(boxesResponse.data.boxes);
            setUsers(usersResponse.data.users);
        } catch (err) {
            setError("Napaka pri nalaganju podatkov.");
        } finally {
            setIsLoadingBoxes(false);
            setIsLoadingUsers(false);
        }
    };

    useEffect(() => {
        fetchAllData();
    }, []);

    const handleCreateBox = async (e) => {
        e.preventDefault();
        setError("");
        try {
            await axios.post(`${API_URL}/api/boxes/admin/create`, {
                boxId: parseInt(newBoxId)
            });
            setNewBoxId("");
            fetchAllData();
        } catch (err) {
            setError(err.response?.data?.message || "Napaka pri ustvarjanju.");
        }
    };

    const handleAdminDeleteBox = async (boxId) => {
        if (!window.confirm("Ali ste prepričani, da želite TRAJNO izbrisati paketnik?")) {
            return;
        }
        try {
            await axios.delete(`${API_URL}/api/boxes/admin/${boxId}`);
            fetchAllData();
        } catch (err) {
            setError(err.response?.data?.message || "Napaka pri brisanju.");
        }
    };

    const handleToggleAdmin = async (userId) => {
        try {
            await axios.put(`${API_URL}/api/users/${userId}/toggle-admin`);
            fetchAllData();
        } catch (err) {
            setError(err.response?.data?.message || "Napaka pri spreminjanju pravic.");
        }
    };

    return (
        <div className="min-h-screen bg-base-200 p-4">
            <div className="navbar bg-base-100 rounded-box shadow-lg mb-6">
                <div className="flex-1">
                    <Link to="/" className="btn btn-ghost normal-case text-xl">Pametni Paketnik - ADMIN</Link>
                </div>
                <div className="flex-none gap-2">
                    <Link to="/dashboard" className="btn btn-ghost">
                        <FaTachometerAlt className="mr-2"/> Uporabniški portal
                    </Link>
                    <button onClick={logout} className="btn btn-error btn-sm">
                        <FaSignOutAlt className="mr-2" /> Odjava
                    </button>
                </div>
            </div>

            <h1 className="text-3xl font-bold mb-6 text-center">Administratorska plošča</h1>
            {error && <div className="alert alert-error mb-4">{error}</div>}

            <div className="card bg-base-100 shadow-xl mb-8">
                <div className="card-body">
                    <h2 className="card-title"><FaPlusCircle /> Dodaj nov paketnik v sistem</h2>
                    <form onSubmit={handleCreateBox}>
                        <div className="form-control">
                            <label className="label"><span className="label-text">ID Paketnika</span></label>
                            <input type="number" value={newBoxId} onChange={(e) => setNewBoxId(e.target.value)} className="input input-bordered" placeholder="npr. 123456"/>
                        </div>
                        <div className="card-actions justify-end mt-4">
                            <button type="submit" className="btn btn-primary">Ustvari paketnik</button>
                        </div>
                    </form>
                </div>
            </div>

            {/* --- VRNJENA KARTICA ZA PREGLED PAKETNIKOV --- */}
            <div className="card bg-base-100 shadow-xl">
                <div className="card-body">
                    <h2 className="card-title"><FaBox /> Pregled vseh paketnikov</h2>
                    {isLoadingBoxes ? (
                        <div className="text-center p-4"><FaSpinner className="animate-spin text-primary text-2xl mx-auto" /></div>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="table w-full">
                                <thead>
                                <tr>
                                    <th>ID Paketnika</th>
                                    <th>Ime po meri</th>
                                    <th>Lastnik</th>
                                    <th>Status</th>
                                    <th>Dejanja</th>
                                </tr>
                                </thead>
                                <tbody>
                                {allBoxes.map(box => (
                                    <tr key={box._id}>
                                        <td className="font-bold">{box.boxId}</td>
                                        <td>{box.customName || '/'}</td>
                                        <td>{box.user ? box.user.username : <span className="opacity-50">Brez lastnika</span>}</td>
                                        <td>
                                                <span className={`badge ${box.user ? 'badge-success' : 'badge-warning'}`}>
                                                    {box.user ? 'Dodeljen' : 'Prost'}
                                                </span>
                                        </td>
                                        <td>
                                            <button onClick={() => handleAdminDeleteBox(box._id)} className="btn btn-xs btn-error"><FaTrash /></button>
                                        </td>
                                    </tr>
                                ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            </div>

            <div className="card bg-base-100 shadow-xl mt-8">
                <div className="card-body">
                    <h2 className="card-title"><FaUsersCog /> Upravljanje z uporabniki</h2>
                    {isLoadingUsers ? (
                        <div className="text-center p-4"><FaSpinner className="animate-spin text-primary text-2xl mx-auto" /></div>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="table w-full">
                                <thead>
                                <tr>
                                    <th>Uporabniško ime</th>
                                    <th>E-pošta</th>
                                    <th>Status</th>
                                    <th>Dejanja</th>
                                </tr>
                                </thead>
                                <tbody>
                                {users.map(user => (
                                    <tr key={user._id}>
                                        <td className="font-bold">{user.username}</td>
                                        <td>{user.email}</td>
                                        <td>
                                            {user.isAdmin ? (
                                                <span className="badge badge-info gap-2"><FaUserShield /> Admin</span>
                                            ) : (
                                                <span className="badge badge-ghost gap-2"><FaUser /> Uporabnik</span>
                                            )}
                                        </td>
                                        <td>
                                            <button
                                                onClick={() => handleToggleAdmin(user._id)}
                                                disabled={loggedInUser._id === user._id}
                                                className={`btn btn-xs ${user.isAdmin ? 'btn-warning' : 'btn-success'}`}
                                            >
                                                {user.isAdmin ? 'Odstrani admina' : 'Dodaj admina'}
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default AdminDashboardPage;