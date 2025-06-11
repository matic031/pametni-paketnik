import { Link } from "react-router-dom";
import { useContext } from "react";
import { AuthContext } from "../components/AuthContext";
import {
    FaBox,
    FaLock,
    FaMobileAlt,
    FaBell,
    FaArrowRight,
    FaShieldAlt,
    FaCheck,
    FaClock,
    FaMapMarkerAlt,
} from "react-icons/fa";

const HomePage = () => {
    const { user } = useContext(AuthContext);

    // Add function to handle carousel navigation
    const handleCarouselNav = (e, slideId) => {
        e.preventDefault();
        document.getElementById(slideId).scrollIntoView({
            behavior: "smooth",
            block: "nearest",
            inline: "center",
        });
    };

    const features = [
        {
            icon: <FaShieldAlt className="text-4xl text-primary mb-4" />,
            title: "2FA obrazna verifikacija",
            text: "Napredna tehnologija prepoznave obraza zagotavlja, da lahko do vaših stvari dostopate samo vi.",
        },
        {
            icon: <FaLock className="text-4xl text-primary mb-4" />,
            title: "24/7 dostop",
            text: "Varno shranjevanje osebnih stvari z dostopom kadarkoli med delom.",
        },
        {
            icon: <FaMobileAlt className="text-4xl text-primary mb-4" />,
            title: "Mobilno upravljanje",
            text: "Preprosto upravljanje in dostop preko intuitivne mobilne aplikacije.",
        },
        {
            icon: <FaBox className="text-4xl text-primary mb-4" />,
            title: "Varno shranjevanje",
            text: "Zaščitite svoje osebne predmete med delovnim časom v varni pametni omarici.",
        },
    ];

    const testimonials = [
        {
            name: "Marija Horvat",
            role: "Delavka v tovarni",
            content:
                "Končno lahko varno shranim svojo torbico in osebne stvari med delom. Obrazna verifikacija je super hitra in varna!",
            avatar: "https://randomuser.me/api/portraits/women/12.jpg",
        },
        {
            name: "Janez Kranjec",
            role: "Vodja izmene",
            content:
                "Kot vodja izmene cenim, da se naši delavci počutijo varno glede svojih osebnih stvari. To izboljša delovno vzdušje.",
            avatar: "https://randomuser.me/api/portraits/men/32.jpg",
        },
    ];

    return (
        <div className="bg-base-100 text-neutral" data-theme="light">
            <div className="hero min-h-screen bg-base-200">
                <div className="hero-content flex-col lg:flex-row-reverse gap-8">
                    <div className="carousel w-full max-w-md lg:max-w-lg rounded-box overflow-hidden shadow-2xl border border-base-300">
                        <div id="slide1" className="carousel-item relative w-full h-96">
                            <img
                                src="/images/paketnik.png"
                                className="w-full h-full object-cover"
                                alt="Pametni paketnik"
                            />
                            <div className="absolute flex justify-between transform -translate-y-1/2 left-5 right-5 top-1/2">
                                <button
                                    onClick={(e) => handleCarouselNav(e, "slide3")}
                                    className="btn btn-circle btn-primary"
                                >
                                    ❮
                                </button>
                                <button
                                    onClick={(e) => handleCarouselNav(e, "slide2")}
                                    className="btn btn-circle btn-primary"
                                >
                                    ❯
                                </button>
                            </div>
                            <div className="absolute bottom-0 w-full bg-base-100/75 p-4">
                                <h3 className="text-xl font-bold">Pametna omarica</h3>
                                <p>Varno shranjevanje v delovnem okolju</p>
                            </div>
                        </div>
                        <div id="slide2" className="carousel-item relative w-full h-96">
                            <img
                                src="/images/paketnik2.png"
                                className="w-full h-full object-cover"
                                alt="Pametni paketnik v uporabi"
                            />
                            <div className="absolute flex justify-between transform -translate-y-1/2 left-5 right-5 top-1/2">
                                <button
                                    onClick={(e) => handleCarouselNav(e, "slide1")}
                                    className="btn btn-circle btn-primary"
                                >
                                    ❮
                                </button>
                                <button
                                    onClick={(e) => handleCarouselNav(e, "slide3")}
                                    className="btn btn-circle btn-primary"
                                >
                                    ❯
                                </button>
                            </div>
                            <div className="absolute bottom-0 w-full bg-base-100/75 p-4">
                                <h3 className="text-xl font-bold">Obrazna verifikacija</h3>
                                <p>2FA zaščita z obrazno prepoznavo</p>
                            </div>
                        </div>
                        <div id="slide3" className="carousel-item relative w-full h-96">
                            <img
                                src="/images/paketnik3.png"
                                className="w-full h-full object-cover"
                                alt="Paketnik na lokaciji"
                            />
                            <div className="absolute flex justify-between transform -translate-y-1/2 left-5 right-5 top-1/2">
                                <button
                                    onClick={(e) => handleCarouselNav(e, "slide2")}
                                    className="btn btn-circle btn-primary"
                                >
                                    ❮
                                </button>
                                <button
                                    onClick={(e) => handleCarouselNav(e, "slide1")}
                                    className="btn btn-circle btn-primary"
                                >
                                    ❯
                                </button>
                            </div>
                            <div className="absolute bottom-0 w-full bg-base-100/75 p-4">
                                <h3 className="text-xl font-bold">Tovarne po Sloveniji</h3>
                                <p>Dostopno na različnih lokacijah</p>
                            </div>
                        </div>
                    </div>

                    <div className="text-center lg:text-left lg:max-w-md">
                        <h1 className="text-5xl font-bold text-neutral">
                            Pametne Omarice
                        </h1>
                        <p className="py-6 text-neutral">
                            Revolucija v varnem shranjevanju osebnih stvari za delavce v tovarnah.
                            Naše pametne omarice z obrazno verifikacijo zagotavljajo največjo varnost
                            za vaše dragocene predmete med delovnim časom.
                        </p>
                        <div className="flex flex-col sm:flex-row gap-4">
                            {!user ? (
                                <>
                                    <Link to="/register" className="btn btn-primary">
                                        Začni zdaj <FaArrowRight className="ml-2" />
                                    </Link>
                                    <Link to="/login" className="btn btn-outline btn-primary">
                                        Prijava
                                    </Link>
                                </>
                            ) : (
                                <Link to="/dashboard" className="btn btn-primary">
                                    Moj Profil <FaArrowRight className="ml-2" />
                                </Link>
                            )}
                        </div>
                        <div className="flex flex-wrap items-center mt-6 gap-2">
                            <div className="badge badge-lg badge-success gap-2">
                                <FaShieldAlt /> Obrazna verifikacija
                            </div>
                            <div className="badge badge-lg badge-success gap-2">
                                <FaCheck /> Brezplačna registracija
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div className="py-16 bg-base-100">
                <div className="max-w-7xl mx-auto px-4">
                    <div className="text-center mb-16">
                        <h2 className="text-3xl font-bold text-neutral">
                            Zakaj izbrati pametno omarico?
                        </h2>
                        <div className="divider max-w-xs mx-auto"></div>
                        <p className="mt-4 text-neutral max-w-2xl mx-auto">
                            Naše pametne omarice so zasnovane z mislijo na varnost delavcev v tovarnah,
                            da bi bilo shranjevanje osebnih stvari čim bolj varno in preprosto.
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                        {features.map((feature, index) => (
                            <div
                                key={index}
                                className="card bg-base-100 shadow-xl hover:shadow-2xl transition-all duration-300 border border-base-200"
                            >
                                <div className="card-body items-center text-center p-6">
                                    {feature.icon}
                                    <h3 className="card-title text-xl mb-2 text-neutral">
                                        {feature.title}
                                    </h3>
                                    <p className="text-neutral">{feature.text}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            <div className="py-16 bg-base-200">
                <div className="max-w-7xl mx-auto px-4">
                    <div className="text-center mb-12">
                        <h2 className="text-3xl font-bold text-neutral">Kako deluje?</h2>
                        <div className="divider max-w-xs mx-auto"></div>
                        <p className="mt-4 text-neutral max-w-2xl mx-auto">
                            Uporaba pametne omarice je preprosta in varna z obrazno verifikacijo
                            za največjo zaščito vaših osebnih stvari.
                        </p>
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                        <div>
                            <img
                                src="/images/paketnik_in_use.png"
                                alt="Pametna omarica v uporabi"
                                className="rounded-lg shadow-xl w-full object-cover h-[400px]"
                            />
                        </div>
                        <div>
                            <ul className="steps steps-vertical lg:steps-horizontal w-full mb-8">
                                <li className="step step-primary">Registracija</li>
                                <li className="step step-primary">Obrazna verifikacija</li>
                                <li className="step step-primary">Izbira omarice</li>
                                <li className="step">Varno shranjevanje</li>
                            </ul>

                            <div className="mt-8">
                                <div className="collapse collapse-plus bg-base-100 shadow-lg mb-4 border border-base-300">
                                    <input type="radio" name="my-accordion-2" defaultChecked />
                                    <div className="collapse-title text-xl font-medium flex items-center text-neutral">
                                        <span className="badge badge-primary mr-3">1</span>{" "}
                                        Registrirajte se
                                    </div>
                                    <div className="collapse-content text-neutral">
                                        <p>
                                            Ustvarite svoj račun v samo nekaj preprostih korakih in
                                            pridobite dostop do varnega shranjevanja v tovarni.
                                        </p>
                                    </div>
                                </div>

                                <div className="collapse collapse-plus bg-base-100 shadow-lg mb-4 border border-base-300">
                                    <input type="radio" name="my-accordion-2" />
                                    <div className="collapse-title text-xl font-medium flex items-center text-neutral">
                                        <span className="badge badge-primary mr-3">2</span> Nastavite
                                        obrazno verifikacijo
                                    </div>
                                    <div className="collapse-content text-neutral">
                                        <p>
                                            Varno 2FA preverjanje z obrazno prepoznavo zagotavlja, da lahko
                                            do vaših stvari dostopate samo vi.
                                        </p>
                                    </div>
                                </div>

                                <div className="collapse collapse-plus bg-base-100 shadow-lg mb-4 border border-base-300">
                                    <input type="radio" name="my-accordion-2" />
                                    <div className="collapse-title text-xl font-medium flex items-center text-neutral">
                                        <span className="badge badge-primary mr-3">3</span>{" "}
                                        Izberite omarico
                                    </div>
                                    <div className="collapse-content text-neutral">
                                        <p>
                                            Izberite omarico v vaši tovarni, ki vam najbolj ustreza po
                                            velikosti in lokaciji za lažji dostop.
                                        </p>
                                    </div>
                                </div>

                                <div className="collapse collapse-plus bg-base-100 shadow-lg border border-base-300">
                                    <input type="radio" name="my-accordion-2" />
                                    <div className="collapse-title text-xl font-medium flex items-center text-neutral">
                                        <span className="badge badge-primary mr-3">4</span>{" "}
                                        Varno shranjujte
                                    </div>
                                    <div className="collapse-content text-neutral">
                                        <p>
                                            Shranite svoje osebne stvari varno med delom in do njih dostopajte
                                            z obrazno verifikacijo kadarkoli jih potrebujete.
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div className="py-12 bg-base-100">
                <div className="max-w-7xl mx-auto px-4">
                    <div className="stats shadow w-full border border-base-200">
                        <div className="stat">
                            <div className="stat-figure text-primary">
                                <FaBox className="text-4xl" />
                            </div>
                            <div className="stat-title text-neutral">
                                Varno shranjenih predmetov
                            </div>
                            <div className="stat-value text-neutral">5000+</div>
                        </div>

                        <div className="stat">
                            <div className="stat-figure text-primary">
                                <FaMapMarkerAlt className="text-4xl" />
                            </div>
                            <div className="stat-title text-neutral">Aktivnih omaric</div>
                            <div className="stat-value text-neutral">200+</div>
                            <div className="stat-desc text-neutral">V tovarnah po Sloveniji</div>
                        </div>

                        <div className="stat">
                            <div className="stat-figure text-primary">
                                <FaClock className="text-4xl" />
                            </div>
                            <div className="stat-title text-neutral">
                                Povprečni čas dostopa
                            </div>
                            <div className="stat-value text-neutral">3 sek</div>
                            <div className="stat-desc text-neutral">Z obrazno verifikacijo</div>
                        </div>
                    </div>
                </div>
            </div>

            <div className="py-16 bg-base-200">
                <div className="max-w-7xl mx-auto px-4">
                    <div className="text-center mb-12">
                        <h2 className="text-3xl font-bold text-neutral">
                            Kaj pravijo naši uporabniki
                        </h2>
                        <div className="divider max-w-xs mx-auto"></div>
                        <p className="mt-4 text-neutral max-w-2xl mx-auto">
                            Več kot 2000 zadovoljnih delavcev v tovarnah po vsej Sloveniji.
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        {testimonials.map((item, index) => (
                            <div
                                key={index}
                                className="card bg-base-100 shadow-xl border border-base-200"
                            >
                                <div className="card-body">
                                    <div className="flex items-center mb-4">
                                        <div className="avatar mr-4">
                                            <div className="w-16 rounded-full ring ring-primary ring-offset-base-100 ring-offset-2">
                                                <img src={item.avatar} alt={item.name} />
                                            </div>
                                        </div>
                                        <div>
                                            <p className="font-bold text-lg text-neutral">
                                                {item.name}
                                            </p>
                                            <p className="text-sm text-neutral">{item.role}</p>
                                        </div>
                                    </div>
                                    <p className="italic text-neutral">"{item.content}"</p>
                                    <div className="rating mt-4">
                                        <input
                                            type="radio"
                                            name={`rating-${index}`}
                                            className="mask mask-star-2 bg-orange-400"
                                        />
                                        <input
                                            type="radio"
                                            name={`rating-${index}`}
                                            className="mask mask-star-2 bg-orange-400"
                                        />
                                        <input
                                            type="radio"
                                            name={`rating-${index}`}
                                            className="mask mask-star-2 bg-orange-400"
                                        />
                                        <input
                                            type="radio"
                                            name={`rating-${index}`}
                                            className="mask mask-star-2 bg-orange-400"
                                        />
                                        <input
                                            type="radio"
                                            name={`rating-${index}`}
                                            className="mask mask-star-2 bg-orange-400"
                                            defaultChecked
                                        />
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            <div className="py-16 bg-gradient-to-r from-primary to-secondary text-white">
                <div className="max-w-7xl mx-auto px-4 text-center">
                    <h2 className="text-3xl font-bold mb-6">
                        Pripravljeni za varno shranjevanje vaših osebnih stvari?
                    </h2>
                    <p className="mb-8 max-w-2xl mx-auto">
                        Pridružite se tisočim zadovoljnih delavcev v tovarnah in začnite uporabljati
                        pametno omarico z obrazno verifikacijo že danes!
                    </p>
                    <div className="flex flex-col sm:flex-row justify-center gap-4">
                        {!user ? (
                            <>
                                <Link
                                    to="/register"
                                    className="btn bg-white text-primary hover:bg-white/90"
                                >
                                    Registrirajte se zdaj
                                </Link>
                                <Link
                                    to="/login"
                                    className="btn btn-outline border-white text-white hover:bg-white hover:text-primary"
                                >
                                    Prijava
                                </Link>
                            </>
                        ) : (
                            <Link
                                to="/dashboard"
                                className="btn bg-white text-primary hover:bg-white/90"
                            >
                                Moj profil
                            </Link>
                        )}
                    </div>
                </div>
            </div>

            <footer className="bg-neutral text-neutral-content">
                <div className="max-w-7xl mx-auto px-4">
                    <div className="footer py-10 grid-cols-2 md:grid-cols-4">
                        <div>
                            <FaBox className="text-3xl" />
                            <p className="font-bold text-lg">Pametne Omarice d.o.o.</p>
                            <p>Zagotavljamo varno shranjevanje</p>
                        </div>
                        <div>
                            <span className="footer-title">Storitve</span>
                            <a className="link link-hover">Obrazna verifikacija</a>
                            <a className="link link-hover">Varno shranjevanje</a>
                            <a className="link link-hover">Mobilni dostop</a>
                            <a className="link link-hover">Podpora</a>
                        </div>
                        <div>
                            <span className="footer-title">Podjetje</span>
                            <a className="link link-hover">O nas</a>
                            <a className="link link-hover">Kontakt</a>
                            <a className="link link-hover">Kariera</a>
                        </div>
                        <div>
                            <span className="footer-title">Pravno</span>
                            <a className="link link-hover">Pogoji uporabe</a>
                            <a className="link link-hover">Zasebnost</a>
                        </div>
                    </div>

                    <div className="footer footer-center p-4 border-t border-base-300">
                        <div>
                            <p>© 2025 Pametne Omarice d.o.o. - Vse pravice pridržane</p>
                        </div>
                    </div>
                </div>
            </footer>
        </div>
    );
};

export default HomePage;
