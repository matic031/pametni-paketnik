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
    <div className="min-h-screen bg-gradient-to-br from-primary/5 via-base-200 to-secondary/5 flex items-center justify-center p-4">
      <div className="w-full max-w-lg">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent mb-2">
            Registracija
          </h1>
          <p className="text-base-content/70 text-lg">Ustvarite nov račun</p>
        </div>

        {/* Card */}
        <div className="bg-base-100 rounded-2xl shadow-xl border border-base-300/50 backdrop-blur-sm">
          <div className="p-8">
            {/* Alerts */}
            {error && (
              <div className="alert alert-error mb-6 rounded-xl">
                <FaExclamationCircle className="text-lg" />
                <span className="font-medium">{error}</span>
              </div>
            )}

            {success && (
              <div className="alert alert-success mb-6 rounded-xl">
                <FaCheckCircle className="text-lg" />
                <span className="font-medium">{success}</span>
              </div>
            )}

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {formFields.map((field) => (
                  <div key={field.name} className="form-control">
                    <label className="label pb-2">
                      <span className="label-text font-medium text-base-content/90 flex items-center gap-2">
                        {field.icon}
                        {field.label}
                      </span>
                    </label>
                    <div className="relative">
                      <input
                        type={field.type}
                        name={field.name}
                        value={formData[field.name]}
                        onChange={handleChange}
                        className="input input-bordered w-full h-12 pl-4 pr-4 text-base rounded-xl border-2 focus:border-primary focus:outline-none transition-all duration-200 hover:border-primary/50"
                        placeholder={`Vnesite ${field.label.toLowerCase().replace('*', '')}`}
                        required={field.required}
                      />
                    </div>
                  </div>
                ))}
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
                      Registriranje...
                    </>
                  ) : (
                    "Registriraj se"
                  )}
                </button>
              </div>
            </form>

            {/* Footer Links */}
            <div className="text-center mt-8 space-y-3">
              <p className="text-base-content/70">
                Že imate račun?{" "}
                <Link
                  to="/login"
                  className="link link-primary font-semibold hover:link-hover transition-colors duration-200"
                >
                  Prijavite se
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

export default RegisterPage;
