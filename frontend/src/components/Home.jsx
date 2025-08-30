import React, { useState, useEffect } from "react";
import { FaQuoteLeft, FaChevronLeft, FaChevronRight, FaEnvelope } from "react-icons/fa";
import { FiAward, FiUsers, FiClock, FiMapPin } from "react-icons/fi";
import { IoMdClose } from "react-icons/io";
import { GiHamburgerMenu } from "react-icons/gi";
import { useNavigate } from "react-router-dom";
import "./CSS/Home.css";
import ContactPage from "./ContactPage";
import { fetchPlatformStats, fetchSiteStatus } from "../BackendConn/api";
import { subscribeNewsletter } from "../BackendConn/api";
import API from "../BackendConn/api";

function Home() {
  const [counts, setCounts] = useState({
    students: null,
    sessions: null,
    mentors: null
  });
  const [loadingStats, setLoadingStats] = useState(true);
  // const toggleNav = () => {
  //   setIsOpen(!isOpen);
  // };


  const navigate = useNavigate();

  // Fetch actual stats from backend
  useEffect(() => {
    let mounted = true;
    fetchPlatformStats()
      .then((data) => {
        if (mounted) {
          setCounts({
            students: data.total_students,
            sessions: data.total_sessions,
            mentors: data.total_mentors,
          });
          setLoadingStats(false);
        }
      })
      .catch(() => {
        if (mounted) setLoadingStats(false);
      });
    return () => { mounted = false; };
  }, []);

  // Maintenance mode (global, backend-controlled)
  const [maintenance, setMaintenance] = useState(false);
  useEffect(() => {
    let mounted = true;
    const checkStatus = async () => {
      try {
        const res = await fetchSiteStatus();
        if (mounted) setMaintenance(!!res.maintenance_mode);
      } catch {}
    };
    checkStatus();
    const interval = setInterval(checkStatus, 30000); // check every 30s
    return () => { mounted = false; clearInterval(interval); };
  }, []);

  // Use more mentors and randomuser.me images
  const mentors = [
    {
      id: 1,
      name: "Dr. Sarah Johnson",
      expertise: "Career Development",
      experience: "15 years in HR & Career Coaching",
      image: "https://randomuser.me/api/portraits/women/44.jpg",
      quote: "Helping individuals find their true potential is my passion."
    },
    {
      id: 2,
      name: "Mark Williams",
      expertise: "Tech Industry",
      experience: "Ex-Google, 10 years in Tech",
      image: "https://randomuser.me/api/portraits/men/32.jpg",
      quote: "Technology changes fast, but fundamentals remain the same."
    },
    {
      id: 3,
      name: "Lisa Chen",
      expertise: "Entrepreneurship",
      experience: "Founder of 3 successful startups",
      image: "https://randomuser.me/api/portraits/women/68.jpg",
      quote: "Every failure is a stepping stone to success."
    },
    {
      id: 4,
      name: "Carlos Rivera",
      expertise: "Product Management",
      experience: "PM at top SaaS companies",
      image: "https://randomuser.me/api/portraits/men/45.jpg",
      quote: "Great products are built by great teams."
    },
    {
      id: 5,
      name: "Emily Smith",
      expertise: "Design & UX",
      experience: "Award-winning UX Designer",
      image: "https://randomuser.me/api/portraits/women/12.jpg",
      quote: "Design is intelligence made visible."
    },
    {
      id: 6,
      name: "Raj Patel",
      expertise: "Data Science",
      experience: "PhD, Data Science Lead",
      image: "https://randomuser.me/api/portraits/men/76.jpg",
      quote: "Data tells the story behind every decision."
    }
  ];

  // Show 3 mentors at a time, auto-slide every 5s
  const [currentSlide, setCurrentSlide] = useState(0);
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentSlide((prev) => (prev + 3) % mentors.length);
    }, 5000);
    return () => clearInterval(interval);
  }, [mentors.length]);

  const nextSlide = () => {
    setCurrentSlide((prev) => (prev + 3) % mentors.length);
  };
  const prevSlide = () => {
    setCurrentSlide((prev) => (prev - 3 + mentors.length) % mentors.length);
  };
  // Get 3 mentors for current slide
  const visibleMentors = [
    mentors[currentSlide],
    mentors[(currentSlide + 1) % mentors.length],
    mentors[(currentSlide + 2) % mentors.length],
  ];

  const testimonials = [
    {
      id: 1,
      name: "Rahul Sharma",
      role: "Computer Science Student",
      text: "My mentor helped me land my dream internship at a top tech company. The guidance was invaluable!",
      rating: 5
    },
    {
      id: 2,
      name: "Priya Patel",
      role: "Aspiring Entrepreneur",
      text: "The business insights I gained from my mentor saved me from making costly mistakes in my startup.",
      rating: 5
    },
    {
      id: 3,
      name: "Amit Kumar",
      role: "Career Changer",
      text: "Switching careers was daunting, but my mentor made the transition smooth and gave me confidence.",
      rating: 4
    }
  ];

  // Newsletter state
  const [newsletterEmail, setNewsletterEmail] = useState("");
  const [newsletterStatus, setNewsletterStatus] = useState("");
  const [newsletterLoading, setNewsletterLoading] = useState(false);

  // Auth state for showing/hiding login/signup/profile
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userRole, setUserRole] = useState(null); // 'student' or 'mentor'
  const [userProfile, setUserProfile] = useState(null);

  useEffect(() => {
    // Check for tokens in localStorage
    const studentToken = localStorage.getItem('token');
    const mentorToken = localStorage.getItem('Mentortoken');
    if (mentorToken) {
      setIsAuthenticated(true);
      setUserRole('mentor');
    } else if (studentToken) {
      setIsAuthenticated(true);
      setUserRole('student');
    } else {
      setIsAuthenticated(false);
      setUserRole(null);
    }
  }, []);

  // Fetch user profile (photo, name) if authenticated
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        if (userRole === 'mentor') {
          const res = await API.get('mentor/profile/');
          setUserProfile(res.data);
        } else if (userRole === 'student') {
          const res = await API.get('student/profile/');
          setUserProfile(res.data);
        } else {
          setUserProfile(null);
        }
      } catch {
        setUserProfile(null);
      }
    };
    if (isAuthenticated && userRole) fetchProfile();
  }, [isAuthenticated, userRole]);

  // Helper to get initials from name
  const getInitials = (name) => {
    if (!name) return '?';
    return name.split(' ').map(part => part[0]).join('').toUpperCase().slice(0, 2);
  };

  // Profile dropdown state
  const [profileDropdownOpen, setProfileDropdownOpen] = useState(false);
  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('Mentortoken');
    setIsAuthenticated(false);
    setUserRole(null);
    setProfileDropdownOpen(false);
    navigate('/');
  };

  // Remove mobile-menu-overlay and related state
  // Refactor navbar to be unified and responsive
  // Hamburger toggles nav-links on mobile
  const [navOpen, setNavOpen] = useState(false);
  const handleNavToggle = () => setNavOpen((open) => !open);
  const closeNav = () => setNavOpen(false);

  // Track window width for responsive rendering
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);
  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth <= 768);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <>
      {/* Navigation */}
      <nav className={`navbar${navOpen ? ' mobile-open' : ''}`}> 
        <div className="nav-logo" onClick={() => { navigate('/'); closeNav(); }}>AspireX</div>
        <ul className={`nav-links${navOpen ? ' mobile-open' : ''}`}> 
          {/* Mobile-only login/signup or profile dropdown AT THE TOP */}
          {isMobile && (
            <li className="mobile-nav-auth">
              {!isAuthenticated ? (
                <>
                  <button className="btn-login" onClick={() => { navigate("/login"); closeNav(); }}>Login</button>
                  <button className="btn-signup" onClick={() => { navigate("/signup"); closeNav(); }}>Sign Up</button>
                </>
              ) : (
                <div className="profile-dropdown">
                  <span
                    tabIndex={0}
                    onClick={() => setProfileDropdownOpen((open) => !open)}
                    onBlur={() => setTimeout(() => setProfileDropdownOpen(false), 150)}
                  >
                    {userProfile?.profile_photo ? (
                      <img src={userProfile.profile_photo} alt="Profile" className="profile-photo-navbar" />
                    ) : (
                      <span className="profile-initials-navbar">{getInitials(userProfile?.name)}</span>
                    )}
                  </span>
                  {profileDropdownOpen && (
                    <div className="dropdown-menu" style={{zIndex: 2000}}>
                      <button onClick={() => {
                        setProfileDropdownOpen(false);
                        closeNav();
                        if (userRole === 'mentor') navigate('/mentor/dashboard');
                        else navigate('/student/dashboard');
                      }}>Dashboard</button>
                      <button onClick={() => { handleLogout(); closeNav(); }}>Logout</button>
                    </div>
                  )}
                </div>
              )}
            </li>
          )}
          <li><a href="#home" onClick={closeNav}>Home</a></li>
          <li><a href="#about" onClick={closeNav}>About</a></li>
          <li><a href="#mentors" onClick={closeNav}>Mentors</a></li>
          <li><a href="#testimonials" onClick={closeNav}>Testimonials</a></li>
          <li><a href="/services" onClick={e => { e.preventDefault(); navigate('/services'); closeNav(); }}>Services</a></li>
          {/* Removed Events from AspireX navbar */}
          {/* <li><a href="/events" onClick={e => { e.preventDefault(); navigate('/events'); closeNav(); }}>Events</a></li> */}
          
        </ul>
        <div className="nav-buttons">
          {/* Desktop-only login/signup or profile dropdown */}
          {!isAuthenticated ? (
            <>
              <button className="btn-login" onClick={() => { navigate("/login"); closeNav(); }}>Login</button>
              <button className="btn-signup" onClick={() => { navigate("/signup"); closeNav(); }}>Sign Up</button>
            </>
          ) : (
            <div className="profile-dropdown">
              <span
                tabIndex={0}
                onClick={() => setProfileDropdownOpen((open) => !open)}
                onBlur={() => setTimeout(() => setProfileDropdownOpen(false), 150)}
              >
                {userProfile?.profile_photo ? (
                  <img src={userProfile.profile_photo} alt="Profile" className="profile-photo-navbar" />
                ) : (
                  <span className="profile-initials-navbar">{getInitials(userProfile?.name)}</span>
                )}
              </span>
              {profileDropdownOpen && (
                <div className="dropdown-menu" style={{zIndex: 2000}}>
                  <button onClick={() => {
                    setProfileDropdownOpen(false);
                    closeNav();
                    if (userRole === 'mentor') navigate('/mentor/dashboard');
                    else navigate('/student/dashboard');
                  }}>Dashboard</button>
                  <button onClick={() => { handleLogout(); closeNav(); }}>Logout</button>
                </div>
              )}
            </div>
          )}
        </div>
        <div className="hamburger" onClick={handleNavToggle}>
          {navOpen ? <IoMdClose /> : <GiHamburgerMenu />}
        </div>
      </nav>
      {/* Mobile overlay for closing menu */}
      {isMobile && navOpen && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: '80vw',
            width: '20vw',
            height: '100vh',
            background: 'rgba(0,0,0,0.18)',
            zIndex: 10500,
          }}
          onClick={closeNav}
        />
      )}


      {/* Hero Section */}
      <section className="hero" id="home">
        <div className="hero-content">
          <div className="hero-text">
            <h4>Hi, there!</h4>
            <h1>
              Your Journey, Our Guidance! <br />
              <span>AspireX</span> for More!
            </h1>
            <p>
              An adaptive mentorship platform designed to connect aspiring
              individuals with expert mentors, fostering growth through
              personalized guidance and meaningful connections.
            </p>
            <div className="hero-buttons">
              <button className="btn-primary" onClick={() => navigate("/login")}>Find a Mentor</button>
              <button className="btn-secondary" onClick={() => navigate("/signup")}>Become a Mentor</button>
            </div>
          </div>
          <div className="hero-image">
            <div className="image-container">
              <div className="background-square"></div>
              <div className="image-wrapper">
                <img src="/smiling.png" alt="Smiling person" />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="stats-section">
        <div className="stats-container">
          <div className="stat-card">
            <div className="stat-icon">
              <FiUsers />
            </div>
            <div className="stat-number">
              {loadingStats ? '...' : (counts.students !== null ? counts.students : '--')}+
            </div>
            <div className="stat-label">Students Enrolled</div>
          </div>
          
          <div className="stat-card">
            <div className="stat-icon">
              <FiClock />
            </div>
            <div className="stat-number">
              {loadingStats ? '...' : (counts.sessions !== null ? counts.sessions : '--')}+
            </div>
            <div className="stat-label">Sessions Completed</div>
          </div>
          
          <div className="stat-card">
            <div className="stat-icon">
              <FiAward />
            </div>
            <div className="stat-number">
              {loadingStats ? '...' : (counts.mentors !== null ? counts.mentors : '--')}+
            </div>
            <div className="stat-label">Expert Mentors</div>
          </div>
        </div>
      </section>

      {/* About Section */}
      <section className="about-section" id="about">
        <div className="about-container">
          <div className="about-image">
            <img src="/team-spirit.svg" alt="Team spirit illustration" />
          </div>
          <div className="about-content">
            <h2>About AspireX</h2>
            <p>
              AspireX was founded with a simple mission: to bridge the gap
              between ambition and achievement. We believe everyone deserves
              access to quality mentorship regardless of their background or
              circumstances.
            </p>
            <p>
              Our platform uses intelligent matching algorithms to connect
              mentees with mentors who are not just experts in their field, but
              also the right personality fit for optimal learning and growth.
            </p>
            <div className="about-features">
              <div className="feature">
                <div className="feature-icon">✓</div>
                <div className="feature-text">Personalized Matching</div>
              </div>
              <div className="feature">
                <div className="feature-icon">✓</div>
                <div className="feature-text">Flexible Scheduling</div>
              </div>
              <div className="feature">
                <div className="feature-icon">✓</div>
                <div className="feature-text">Progress Tracking</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Top Mentors Section */}
      <section className="mentors-section" id="mentors">
        <h2>Top Mentors</h2>
        <p className="section-subtitle">Meet our most inspiring mentors</p>
        <div className="mentors-carousel">
          <button className="carousel-btn left" onClick={prevSlide} aria-label="Previous mentor">
            <FaChevronLeft />
          </button>
          {visibleMentors.map((mentor, idx) => (
            <div className="mentor-card-3d" key={mentor.id}>
              <div className="mentor-card-inner">
                <div className="mentor-card-front">
                  <img src={mentor.image} alt={mentor.name} className="mentor-img" />
                  <h3>{mentor.name}</h3>
                  <p className="mentor-expertise">{mentor.expertise}</p>
                </div>
                <div className="mentor-card-back">
                  <p className="mentor-quote">“{mentor.quote}”</p>
                  <p className="mentor-experience">{mentor.experience}</p>
                </div>
              </div>
            </div>
          ))}
          <button className="carousel-btn right" onClick={nextSlide} aria-label="Next mentor">
            <FaChevronRight />
          </button>
        </div>
        <div className="mentor-indicators">
          {Array.from({ length: Math.ceil(mentors.length / 3) }).map((_, idx) => (
            <span
              key={idx}
              className={`indicator-dot ${Math.floor(currentSlide / 3) === idx ? "active" : ""}`}
              onClick={() => setCurrentSlide((idx * 3) % mentors.length)}
            ></span>
          ))}
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="testimonials-section" id="testimonials">
        <h2>What Our Students Say</h2>
        <p className="section-subtitle">
          Success stories from our mentees
        </p>
        
        <div className="testimonials-container">
          {testimonials.map((testimonial) => (
            <div key={testimonial.id} className="testimonial-card">
              <div className="testimonial-rating">
                {Array.from({ length: testimonial.rating }).map((_, i) => (
                  <span key={i}>★</span>
                ))}
              </div>
              <div className="testimonial-text">
                <FaQuoteLeft /> {testimonial.text}
              </div>
              <div className="testimonial-author">
                <div className="author-name">{testimonial.name}</div>
                <div className="author-role">{testimonial.role}</div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Contact Section (aligned right, interactive) */}
      <section className="home-contact-section">
        <div className="home-contact-flex">
          <div className="home-contact-left">
            <h2>Contact Our Team</h2>
            <p>Have questions, suggestions, or need help? Reach out and we'll respond promptly!</p>
            <ul className="home-contact-info">
              <li><FiMapPin /> India</li>
              {/* <li><span role="img" aria-label="phone">📞</span> +1 (234) 567-8900</li> */}
              <li><FaEnvelope /> contactaspirexdigital@gmail.com</li>
            </ul>
            <div className="home-contact-illustration">
              <img src="/logoBlack.png" alt="Contact Illustration" style={{maxWidth: '180px', marginTop: '4px'}} />
            </div>
          </div>
          <div className="home-contact-right">
            <ContactPage />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="cta-container">
          <h2>Ready to Transform Your Journey?</h2>
          <p>
            Whether you're looking for guidance or eager to share your expertise,
            AspireX is the platform for meaningful mentorship connections.
          </p>
          <div className="cta-buttons">
            <button className="btn-primary" onClick={() => navigate("/login")}>Find Your Mentor</button>
            <button className="btn-secondary" onClick={() => navigate("/signup")}>Become a Mentor</button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="footer-container">
          <div className="footer-brand">
            <div className="footer-logo">AspireX</div>
            <p>
              Bridging the gap between ambition and achievement through
              meaningful mentorship.
            </p>
            <div className="social-icons">
              <a href="#"><i className="fab fa-facebook"></i></a>
              <a href="#"><i className="fab fa-twitter"></i></a>
              <a href="https://www.linkedin.com/company/aspirexdigital/"><i className="fab fa-linkedin"></i></a>
              <a href="#"><i className="fab fa-instagram"></i></a>
            </div>
          </div>
          
          <div className="footer-links">
            <h4>Quick Links</h4>
            <ul>
              <li><a href="#home">Home</a></li>
              <li><a href="#about">About</a></li>
              <li><a href="#mentors">Mentors</a></li>
              <li><a href="#testimonials">Testimonials</a></li>
              <li><a href="#contact">Contact</a></li>
            </ul>
          </div>
          
          <div className="footer-contact" id="contact">
            <h4>Contact Us</h4>
            <ul>
              <li><FiMapPin /> India</li>
              {/* <li><i className="fas fa-phone"></i> +1 (234) 567-8900</li> */}
              <li><FaEnvelope /> contactaspirexdigital@gmail.com</li>
            </ul>
          </div>
          
          <div className="footer-newsletter">
            <h4>Subscribe to Newsletter</h4>
            <p>Get updates on new mentors and resources</p>
            <form
              onSubmit={async (e) => {
                e.preventDefault();
                setNewsletterStatus("");
                setNewsletterLoading(true);
                try {
                  const res = await subscribeNewsletter(newsletterEmail);
                  if (res.success) {
                    setNewsletterStatus(res.message || "Subscribed!");
                    setNewsletterEmail("");
                  } else {
                    setNewsletterStatus(res.message || "Subscription failed.");
                  }
                } catch (err) {
                  setNewsletterStatus("Subscription failed. Try again later.");
                }
                setNewsletterLoading(false);
              }}
            >
              <input
                type="email"
                placeholder="Your email address"
                value={newsletterEmail}
                onChange={e => setNewsletterEmail(e.target.value)}
                required
                disabled={newsletterLoading}
              />
              <button type="submit" disabled={newsletterLoading || !newsletterEmail}>
                {newsletterLoading ? "Subscribing..." : "Subscribe"}
              </button>
            </form>
            {newsletterStatus && (
              <div style={{ marginTop: 8, color: newsletterStatus.includes('success') ? 'green' : 'crimson' }}>
                {newsletterStatus}
              </div>
            )}
          </div>
        </div>
        
        <div className="footer-bottom">
          <p>&copy; {new Date().getFullYear()} AspireX Platform. All rights reserved.</p>
        </div>
      </footer>
    </>
  );
}

export default Home;