import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { GiHamburgerMenu } from 'react-icons/gi';
import { IoMdClose } from 'react-icons/io';
import './CSS/ServicesPage.css';

const ServicesNavbar = () => {
  const navigate = useNavigate();
  const profileInitials = 'SA';
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Get user role and authentication status
  const userRole = localStorage.getItem('userRole');
  const mentorToken = localStorage.getItem('Mentortoken');
  const studentToken = localStorage.getItem('token');
  const isAuthenticated = mentorToken || studentToken;

  // Detect mobile view
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 700);
  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth <= 700);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const handleLogout = () => {
    setDropdownOpen(false);
    localStorage.removeItem('Mentortoken');
    localStorage.removeItem('token');
    localStorage.removeItem('userRole');
    localStorage.removeItem('userData');
    navigate('/');
  };

  const handleDashboard = () => {
    setDropdownOpen(false);
    if (userRole === 'mentor') {
      navigate('/mentor/dashboard');
    } else if (userRole === 'student') {
      navigate('/student/dashboard');
    } else {
      // Fallback - try to determine role from token
      if (mentorToken) {
        navigate('/mentor/dashboard');
      } else if (studentToken) {
        navigate('/student/dashboard');
      } else {
        navigate('/');
      }
    }
  };

  return (
    <nav className="services-navbar">
      <div className="services-navbar-logo" onClick={() => navigate('/')}>AspireX</div>
      {isMobile && (
        <div className="services-hamburger" onClick={() => setMobileMenuOpen(open => !open)}>
          {mobileMenuOpen ? <IoMdClose size={28} /> : <GiHamburgerMenu size={28} />}
        </div>
      )}
      <div className={`services-navbar-menu${isMobile ? (mobileMenuOpen ? ' open' : '') : ''}`}> 
        {isAuthenticated && (
          <ul className="services-navbar-links">
            <li onClick={() => {navigate('/services/share'); setMobileMenuOpen(false);}}>Share</li>
            
            <li onClick={() => {navigate('/events'); setMobileMenuOpen(false);}}>Events</li>

          </ul>
        )}
        <div className="services-navbar-profile">
          <span
            className="services-profile-avatar"
            tabIndex={0}
            onClick={() => setDropdownOpen(open => !open)}
            onBlur={() => setTimeout(() => setDropdownOpen(false), 150)}
          >
            {profileInitials}
          </span>
          {dropdownOpen && (
            <div className="services-dropdown-menu">
              {isAuthenticated && (
                <button onClick={handleDashboard}>Dashboard</button>
              )}
              <button onClick={handleLogout}>Logout</button>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};

export default ServicesNavbar; 