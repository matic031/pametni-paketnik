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
        navigate(destination, {state: {user: result.user}});
      } else {
        setError(result.message || "Prijava ni uspela");
      }
    } catch (err) {
      setError("Prišlo je do napake pri prijavi");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="hero min-h-screen bg-base-200">
      <div className="hero-content flex-col">
        <div className="text-center">
          <h1 className="text-4xl font-bold">Prijava</h1>
        </div>

        <div className="card flex-shrink-0 w-full max-w-sm shadow-2xl bg-base-100">
          <div className="card-body">
            {error && (
              <div className="alert alert-error">
                <FaExclamationCircle />
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleSubmit}>
              <div className="form-control">
                <label className="label">
                  <span className="label-text">Uporabniško ime</span>
                </label>
                <div className="input-group">
                  <span>
                    <FaUser />
                  </span>
                  <input
                    type="text"
                    name="username"
                    value={formData.username}
                    onChange={handleChange}
                    className="input input-bordered w-full"
                    required
                  />
                </div>
              </div>

              <div className="form-control">
                <label className="label">
                  <span className="label-text">Geslo</span>
                </label>
                <div className="input-group">
                  <span>
                    <FaLock />
                  </span>
                  <input
                    type="password"
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    className="input input-bordered w-full"
                    required
                  />
                </div>
              </div>

              <div className="form-control mt-6">
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <span className="loading loading-spinner loading-sm"></span>
                  ) : (
                    "Prijava"
                  )}
                </button>
              </div>
            </form>

            <div className="text-center mt-4">
              <p>
                Nimate računa?{" "}
                <Link to="/register" className="link link-primary">
                  Registrirajte se
                </Link>
              </p>
              <p className="mt-2">
                <Link to="/" className="link link-neutral">
                  Nazaj na domačo stran
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
