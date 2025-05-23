import { useContext } from "react";
import { Link } from "react-router-dom";
import { AuthContext } from "../components/AuthContext";
import {
  FaSignOutAlt,
  FaUser,
  FaEnvelope,
  FaIdCard,
  FaBox,
  FaPlusCircle,
  FaInfoCircle,
} from "react-icons/fa";

const DashboardPage = () => {
  const { user, logout } = useContext(AuthContext);

  const userInfo = [
    {
      label: "Uporabniško ime",
      value: user?.username,
      icon: <FaUser className="text-primary" />,
    },
    {
      label: "E-pošta",
      value: user?.email,
      icon: <FaEnvelope className="text-primary" />,
    },
    ...(user?.name
      ? [
          {
            label: "Ime",
            value: user?.name,
            icon: <FaIdCard className="text-primary" />,
          },
        ]
      : []),
    ...(user?.lastName
      ? [
          {
            label: "Priimek",
            value: user?.lastName,
            icon: <FaIdCard className="text-primary" />,
          },
        ]
      : []),
  ];

  return (
    <div className="min-h-screen bg-base-200 p-4">
      <div className="navbar bg-base-100 rounded-box shadow-lg mb-6">
        <div className="flex-1">
          <Link to="/" className="btn btn-ghost normal-case text-xl">
            Pametni Paketnik
          </Link>
        </div>
        <div className="flex-none">
          <button onClick={logout} className="btn btn-error btn-sm">
            <FaSignOutAlt className="mr-2" /> Odjava
          </button>
        </div>
      </div>

      <div className="hero bg-base-100 rounded-box shadow-lg mb-6">
        <div className="hero-content text-center">
          <div>
            <h1 className="text-3xl font-bold">
              Dobrodošli, {user?.name || user?.username}!
            </h1>
            <p className="py-4">
              Uspešno ste prijavljeni v sistem Pametni Paketnik.
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card bg-base-100 shadow-lg">
          <div className="card-body">
            <h2 className="card-title">
              <FaUser className="text-primary" /> Moji podatki
            </h2>
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
            <h2 className="card-title">
              <FaBox className="text-primary" /> Moji paketniki
            </h2>
            <div className="divider"></div>
            <div className="alert shadow-lg">
              <FaInfoCircle className="text-info" />
              <span>Trenutno nimate dodanih paketnikov.</span>
            </div>
            <div className="card-actions justify-end mt-4">
              <button className="btn btn-primary">
                <FaPlusCircle className="mr-2" /> Dodaj paketnik
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
