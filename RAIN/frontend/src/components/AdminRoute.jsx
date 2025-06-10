import { useContext } from "react";
import { Navigate, Outlet } from "react-router-dom";
import { AuthContext } from "./AuthContext";

const AdminRoute = () => {
    const { user, loading } = useContext(AuthContext);

    if (loading) {
        return <div>Nalaganje...</div>;
    }

    // Preveri, če je uporabnik prijavljen IN če je admin
    return user && user.isAdmin ? <Outlet /> : <Navigate to="/dashboard" replace />;
};

export default AdminRoute;