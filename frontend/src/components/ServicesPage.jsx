import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './CSS/ServicesPage.css';
import { GiHamburgerMenu } from 'react-icons/gi';
import { IoMdClose } from 'react-icons/io';
import Services from './services';
import ServicesNavbar from './ServicesNavbar';

const ServicesPage = () => {
  const navigate = useNavigate();
  const profileInitials = 'SA';
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Get user role and authentication status
  const userRole = localStorage.getItem('userRole');
  const mentorToken = localStorage.getItem('Mentortoken');
  const studentToken = localStorage.getItem('token');
  const isAuthenticated = mentorToken || studentToken;

  const handleLogout = () => {
    setDropdownOpen(false);
    localStorage.removeItem('Mentortoken');
    localStorage.removeItem('token');
    localStorage.removeItem('userRole');
    localStorage.removeItem('userData');
    navigate('/');
  };

  const handleDashboardClick = () => {
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

  // Detect mobile view
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 700);
  React.useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth <= 700);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <div className="services-root">
      <ServicesNavbar />
      <div className="services-content">
        {/* <h1>Services</h1> */}
        {/* <p>Welcome to the Services page! Choose an option from the navbar above.</p> */}
        <Services/>
      </div>
    </div>
  );
};

export default ServicesPage; 