import { useState, useContext } from "react";
import { Link, useNavigate } from "react-router-dom";
import { AuthContext } from "../components/AuthContext";
import {
  FaUser,
  FaEnvelope,
  FaLock,
  FaUserAlt,
  FaExclamationCircle,
  FaCheckCircle,
} from "react-icons/fa";

const RegisterPage = () => {
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
    name: "",
    lastName: "",
  });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const { register } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setIsLoading(true);

    const { username, email, password, confirmPassword, name, lastName } =
      formData;

    // validation
    if (!username || !email || !password) {
      setError("Prosim, izpolnite vsa obvezna polja");
      setIsLoading(false);
      return;
    }

    if (password !== confirmPassword) {
      setError("Gesli se ne ujemata");
      setIsLoading(false);
      return;
    }

    try {
      const result = await register({
        username,
        email,
        password,
        name,
        lastName,
      });

      if (result.success) {
        setSuccess("Registracija uspešna. Zdaj se lahko prijavite.");
        setTimeout(() => navigate("/login"), 2000);
      } else {
        setError(result.message || "Registracija ni uspela");
      }
    } catch (err) {
      setError("Prišlo je do napake pri registraciji");
    } finally {
      setIsLoading(false);
    }
  };

  const formFields = [
    {
      name: "username",
      label: "Uporabniško ime*",
      type: "text",
      icon: <FaUser />,
      required: true,
    },
    {
      name: "email",
      label: "E-pošta*",
      type: "email",
      icon: <FaEnvelope />,
      required: true,
    },
    {
      name: "password",
      label: "Geslo*",
      type: "password",
      icon: <FaLock />,
      required: true,
    },
    {
      name: "confirmPassword",
      label: "Potrdi geslo*",
      type: "password",
      icon: <FaLock />,
      required: true,
    },
    {
      name: "name",
      label: "Ime",
      type: "text",
      icon: <FaUserAlt />,
      required: false,
    },
    {
      name: "lastName",
      label: "Priimek",
      type: "text",
      icon: <FaUserAlt />,
      required: false,
    },
  ];

  return (
    <div className="hero min-h-screen bg-base-200">
      <div className="hero-content flex-col">
        <div className="text-center">
          <h1 className="text-4xl font-bold">Registracija</h1>
        </div>

        <div className="card flex-shrink-0 w-full max-w-md shadow-2xl bg-base-100">
          <div className="card-body">
            {error && (
              <div className="alert alert-error">
                <FaExclamationCircle />
                <span>{error}</span>
              </div>
            )}

            {success && (
              <div className="alert alert-success">
                <FaCheckCircle />
                <span>{success}</span>
              </div>
            )}

            <form onSubmit={handleSubmit}>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {formFields.map((field) => (
                  <div key={field.name} className="form-control">
                    <label className="label">
                      <span className="label-text">{field.label}</span>
                    </label>
                    <div className="input-group">
                      <span>{field.icon}</span>
                      <input
                        type={field.type}
                        name={field.name}
                        value={formData[field.name]}
                        onChange={handleChange}
                        className="input input-bordered w-full"
                        required={field.required}
                      />
                    </div>
                  </div>
                ))}
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
                    "Registriraj se"
                  )}
                </button>
              </div>
            </form>

            <div className="text-center mt-4">
              <p>
                Že imate račun?{" "}
                <Link to="/login" className="link link-primary">
                  Prijavite se
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

export default RegisterPage;
