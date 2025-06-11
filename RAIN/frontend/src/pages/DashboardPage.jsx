import { useContext, useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import { AuthContext } from "../components/AuthContext";
import axios from "axios";
import {
  FaSignOutAlt, FaUser, FaEnvelope, FaIdCard, FaBox, FaPlusCircle,
  FaInfoCircle, FaSpinner, FaTimes, FaUserShield, FaTrash, FaHistory
} from "react-icons/fa";

const DashboardPage = () => {
  const { user: contextUser, logout } = useContext(AuthContext);
  const location = useLocation();
  const user = location.state?.user || contextUser;

  const [boxes, setBoxes] = useState([]);
  const [logs, setLogs] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);


  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newBoxId, setNewBoxId] = useState("");
  const [newBoxName, setNewBoxName] = useState("");
  const [modalError, setModalError] = useState("");


  const API_URL = import.meta.env.VITE_API_URL || "http://localhost:3000";

  const fetchDashboardData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [boxesResponse, logsResponse] = await Promise.all([
        axios.get(`${API_URL}/api/boxes`),
        axios.get(`${API_URL}/api/logs`)
      ]);

      if (boxesResponse.data.success) setBoxes(boxesResponse.data.boxes);
      if (logsResponse.data.success) setLogs(logsResponse.data.logs);

    } catch (err) {
      setError("Napaka pri nalaganju podatkov.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);


  const handleAddBox = async (e) => {
    e.preventDefault();
    setModalError("");
    if (!newBoxId || !newBoxName) {
      setModalError("Prosim, izpolnite vsa polja.");
      return;
    }
    try {
      await axios.post(`${API_URL}/api/boxes/claim`, {
        boxId: parseInt(newBoxId, 10),
        customName: newBoxName,
      });
      setIsModalOpen(false);
      setNewBoxId("");
      setNewBoxName("");
      fetchDashboardData();
    } catch (err) {
      setModalError(err.response?.data?.message || "Napaka pri dodajanju.");
    }
  };


  const handleRemoveBox = async (boxId) => {
    if (!window.confirm("Ali ste prepričani, da želite odstraniti ta pametno omarico?")) {
      return;
    }
    try {
      await axios.delete(`${API_URL}/api/boxes/${boxId}`);
      fetchDashboardData();
    } catch (err) {
      setError(err.response?.data?.message || "Napaka pri odstranjevanju.");
    }
  };

  const userInfo = [
    { label: "Uporabniško ime", value: user?.username, icon: <FaUser className="text-primary" /> },
    { label: "E-pošta", value: user?.email, icon: <FaEnvelope className="text-primary" /> },
    ...(user?.name ? [{ label: "Ime", value: user.name, icon: <FaIdCard className="text-primary" /> }] : []),
    ...(user?.lastName ? [{ label: "Priimek", value: user.lastName, icon: <FaIdCard className="text-primary" /> }] : []),
  ];

  return (
    <div className="min-h-screen bg-base-200 p-4">
      <div className="navbar bg-base-100 rounded-box shadow-lg mb-6">
        <div className="flex-1">
          <Link to="/" className="btn btn-ghost normal-case text-xl">Pametne omarice</Link>
        </div>
        <div className="flex-none gap-2">
          {user && user.isAdmin && (
            <Link to="/admin/dashboard" className="btn btn-ghost">
              <FaUserShield className="mr-2" /> Administratorska plošča
            </Link>
          )}
          <button onClick={logout} className="btn btn-error btn-sm"><FaSignOutAlt className="mr-2" /> Odjava</button>
        </div>
      </div>

      <div className="hero bg-base-100 rounded-box shadow-lg mb-6">
        <div className="hero-content text-center">
          <div>
            <h1 className="text-3xl font-bold">Dobrodošli, {user?.name || user?.username}!</h1>
            <p className="py-4">Uspešno ste prijavljeni v sistem Pametne omarice.</p>
          </div>
        </div>
      </div>

      {error && <div className="alert alert-error mb-4">{error}</div>}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card bg-base-100 shadow-lg">
          <div className="card-body">
            <h2 className="card-title"><FaUser className="text-primary" /> Moji podatki</h2>
            <div className="divider"></div>
            <div className="space-y-3">
              {userInfo.map((item, index) => (
                <div key={index} className="flex items-center">
                  <div className="w-8">{item.icon}</div>
                  <span className="font-bold w-32">{item.label}:</span>
                  <span>{item.value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="card bg-base-100 shadow-lg">
          <div className="card-body">
            <h2 className="card-title"><FaBox className="text-primary" /> Moji paketniki</h2>
            <div className="divider"></div>
            {isLoading ? (
              <div className="text-center p-4"><FaSpinner className="animate-spin text-primary text-2xl mx-auto" /></div>
            ) : boxes.length === 0 ? (
              <div className="alert shadow-lg"><FaInfoCircle className="text-info" /><span>Nimate dodanih paketnikov.</span></div>
            ) : (
              <div className="space-y-2">
                {boxes.map(box => (
                  <div key={box._id} className="p-3 bg-base-200 rounded-lg flex justify-between items-center">
                    <div>
                      <p className="font-bold">{box.customName}</p>
                      <p className="text-sm opacity-60">ID: {box.boxId}</p>
                    </div>
                    <button onClick={() => handleRemoveBox(box._id)} className="btn btn-sm btn-error btn-outline"><FaTrash className="mr-1" /> Odstrani</button>
                  </div>
                ))}
              </div>
            )}
            <div className="card-actions justify-end mt-4">
              <button className="btn btn-primary" onClick={() => setIsModalOpen(true)}><FaPlusCircle className="mr-2" /> Dodaj pametno omarico</button>
            </div>
          </div>
        </div>
      </div>

      <div className="card bg-base-100 shadow-lg mt-6">
        <div className="card-body">
          <h2 className="card-title"><FaHistory className="text-primary" /> Dnevnik odklepov</h2>
          <div className="divider"></div>
          {isLoading ? (
            <div className="text-center p-4"><FaSpinner className="animate-spin text-primary text-2xl mx-auto" /></div>
          ) : logs.length === 0 ? (
            <div className="alert shadow-lg"><FaInfoCircle className="text-info" /><span>Ni zabeleženih poskusov odklepa.</span></div>
          ) : (
            <div className="overflow-x-auto">
              <table className="table w-full">
                <thead>
                  <tr>
                    <th>Datum in čas</th>
                    <th>ID Pametne omarice</th>
                    <th>Status</th>
                    <th>Sporočilo</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.map(log => (
                    <tr key={log._id} className="hover">
                      <td>{new Date(log.createdAt).toLocaleString('sl-SI')}</td>
                      <td>{log.boxId}</td>
                      <td>
                        <span className={`badge ${log.status === 'SUCCESS' ? 'badge-success' : 'badge-error'}`}>
                          {log.status === 'SUCCESS' ? 'Uspešno' : 'Neuspešno'}
                        </span>
                      </td>
                      <td className="text-xs">{log.message}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* --- VRNJEN MODAL ZA DODAJANJE PAKETNIKA --- */}
      {isModalOpen && (
        <div className="modal modal-open">
          <div className="modal-box">
            <button onClick={() => setIsModalOpen(false)} className="btn btn-sm btn-circle absolute right-2 top-2"><FaTimes /></button>
            <h3 className="font-bold text-lg">Dodaj novo pametno omarico</h3>
            <p className="py-4">Vnesite ID pametne omarice in ji določite ime po meri.</p>

            <form onSubmit={handleAddBox}>
              <div className="form-control">
                <label className="label"><span className="label-text">ID Pametne omarice</span></label>
                <input type="number" placeholder="npr. 123456" className="input input-bordered" value={newBoxId} onChange={(e) => setNewBoxId(e.target.value)} />
              </div>
              <div className="form-control mt-4">
                <label className="label"><span className="label-text">Ime po meri</span></label>
                <input type="text" placeholder="npr. Janezova pametna omarica" className="input input-bordered" value={newBoxName} onChange={(e) => setNewBoxName(e.target.value)} />
              </div>

              {modalError && <p className="text-error text-sm mt-4">{modalError}</p>}

              <div className="modal-action">
                <button type="button" className="btn" onClick={() => setIsModalOpen(false)}>Prekliči</button>
                <button type="submit" className="btn btn-primary">Dodaj</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default DashboardPage;