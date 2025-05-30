import { createContext, useState, useEffect } from "react";
import axios from "axios";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const checkLoggedIn = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem("token");

        if (token) {
          axios.defaults.headers.common["Authorization"] = token;

          //TODO: use env var here isntead of hardcoding
          const response = await axios.get("http://localhost:3001/auth/me");
          if (response.data.success) {
            setUser(response.data.user);
          } else {
            localStorage.removeItem("token");
            delete axios.defaults.headers.common["Authorization"];
          }
        }
      } catch (err) {
        localStorage.removeItem("token");
        delete axios.defaults.headers.common["Authorization"];
      } finally {
        setLoading(false);
      }
    };

    checkLoggedIn();
  }, []);

  const register = async (userData) => {
    setError(null);
    try {
      const response = await axios.post(
        "http://localhost:3001/auth/register",
        userData
      );
      return { success: true, message: response.data.message };
    } catch (err) {
      const errorMsg =
        err.response?.data?.message || "Prišlo je do napake pri registraciji.";
      setError(errorMsg);
      return { success: false, message: errorMsg };
    }
  };

  const login = async (username, password) => {
    setError(null);
    try {
      const response = await axios.post("http://localhost:3001/auth/login", {
        username,
        password,
      });
      if (response.data.success) {
        localStorage.setItem("token", response.data.token);
        axios.defaults.headers.common["Authorization"] = response.data.token;
        setUser(response.data.user);
        return { success: true };
      }
    } catch (err) {
      const errorMsg =
        err.response?.data?.message || "Napačno uporabniško ime ali geslo.";
      setError(errorMsg);
      return { success: false, message: errorMsg };
    }
  };

  const logout = () => {
    localStorage.removeItem("token");
    delete axios.defaults.headers.common["Authorization"];
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        error,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
