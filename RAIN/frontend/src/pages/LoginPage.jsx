import { useState, useContext } from "react";
import { Link, useNavigate } from "react-router-dom";
import { AuthContext } from "../components/AuthContext";
import { FaUser, FaLock, FaExclamationCircle } from "react-icons/fa";

const LoginPage = () => {
  const [formData, setFormData] = useState({ username: "", password: "" });
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    const { username, password } = formData;

    if (!username || !password) {
      setError("Prosim, izpolnite vsa polja");
      setIsLoading(false);
      return;
    }

    try {
      const result = await login(username, password);

      if (result.success && result.user) {
        const destination = result.user.isAdmin ? "/admin/dashboard" : "/dashboard";
        console.log("Login Result:", result);
        console.log("Is Admin?:", result.user?.isAdmin);
        navigate(destination, { state: { user: result.user } });
      } else if (result.requiresFaceVerification) {
        setError("Potrebna je verifikacija obraza na aplikaciji");

      } else {
        setError(result.message || "Prijava ni uspela");
      }
    } catch (error) {
      console.error("Login error:", error);
      setError("Prišlo je do napake pri prijavi");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/5 via-base-200 to-secondary/5 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent mb-2">
            Prijava
          </h1>
          <p className="text-base-content/70 text-lg">Prijavite se v svoj račun</p>
        </div>

        {/* Card */}
        <div className="bg-base-100 rounded-2xl shadow-xl border border-base-300/50 backdrop-blur-sm">
          <div className="p-8">
            {/* Alert */}
            {error && (
              <div className="alert alert-error mb-6 rounded-xl">
                <FaExclamationCircle className="text-lg" />
                <span className="font-medium">{error}</span>
              </div>
            )}

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="form-control">
                <label className="label pb-2">
                  <span className="label-text font-medium text-base-content/90 flex items-center gap-2">
                    <FaUser />
                    Uporabniško ime
                  </span>
                </label>
                <div className="relative">
                  <input
                    type="text"
                    name="username"
                    value={formData.username}
                    onChange={handleChange}
                    className="input input-bordered w-full h-12 pl-4 pr-4 text-base rounded-xl border-2 focus:border-primary focus:outline-none transition-all duration-200 hover:border-primary/50"
                    placeholder="Vnesite uporabniško ime"
                    required
                  />
                </div>
              </div>

              <div className="form-control">
                <label className="label pb-2">
                  <span className="label-text font-medium text-base-content/90 flex items-center gap-2">
                    <FaLock />
                    Geslo
                  </span>
                </label>
                <div className="relative">
                  <input
                    type="password"
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    className="input input-bordered w-full h-12 pl-4 pr-4 text-base rounded-xl border-2 focus:border-primary focus:outline-none transition-all duration-200 hover:border-primary/50"
                    placeholder="Vnesite geslo"
                    required
                  />
                </div>
              </div>

              {/* Submit Button */}
              <div className="form-control pt-4">
                <button
                  type="submit"
                  className="btn btn-primary h-12 text-base font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all duration-200 transform hover:-translate-y-0.5"
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <>
                      <span className="loading loading-spinner loading-sm"></span>
                      Prijavlja...
                    </>
                  ) : (
                    "Prijava"
                  )}
                </button>
              </div>
            </form>

            {/* Footer Links */}
            <div className="text-center mt-8 space-y-3">
              <p className="text-base-content/70">
                Nimate računa?{" "}
                <Link
                  to="/register"
                  className="link link-primary font-semibold hover:link-hover transition-colors duration-200"
                >
                  Registrirajte se
                </Link>
              </p>
              <p>
                <Link
                  to="/"
                  className="link link-neutral text-sm hover:link-hover transition-colors duration-200"
                >
                  ← Nazaj na domačo stran
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
