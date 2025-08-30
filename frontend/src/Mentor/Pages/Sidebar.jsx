import React, { useEffect } from 'react';
import { 
  FiTarget, 
  FiBarChart, 
  FiDollarSign, 
  FiMail, 
  FiUser, 
  FiCalendar, 
  FiStar, 
  FiHeadphones, 
  FiLogOut,
  FiChevronRight,
  FiChevronLeft,
  FiMessageCircle
} from 'react-icons/fi';
import './CSS/Dashboard.css';
import { API_BASE_URL } from '../../BackendConn/api';

const Sidebar = ({ activeTab, setActiveTab, sidebarOpen, setSidebarOpen, mentorProfile, mentor, isMobile, sidebarCollapsed, setSidebarCollapsed }) => {
  const isVerified = mentor?.details?.is_approved || false;
  const profilePhoto = mentor?.details?.profile_photo || '';

  // Close sidebar on ESC for accessibility
  useEffect(() => {
    if (!sidebarOpen) return;
    const handleEsc = (e) => {
      if (e.key === 'Escape') setSidebarOpen(false);
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [sidebarOpen, setSidebarOpen]);

  const handleLogout = () => {
    const confirmLogout = window.confirm("Are you sure you want to logout?");
    if (confirmLogout) {
      localStorage.removeItem('token');
      window.location.href = '/';
    }
  };

  // Calculate total sessions from mentor.meetings if available
  const totalSessions = mentor?.meetings ? mentor.meetings.filter(m => m.status !== 'cancelled').length : (mentorProfile.sessionsCompleted || 0);

  // Backdrop for mobile overlay
  const backdrop = isMobile && sidebarOpen ? (
    <div className="sidebar-backdrop" onClick={() => setSidebarOpen(false)}></div>
  ) : null;

  return (
    <>
      {backdrop}
      <div className={`sidebar${isMobile ? ' sidebar-mobile' : ''} ${sidebarOpen ? 'sidebar-open' : ''}`}> 
        <div className="sidebar-header">
          <h2>AspireX</h2>
          {/* Only show collapse toggle in sidebar on desktop */}
          {!isMobile && (
            <button className="toggle-sidebar" onClick={() => setSidebarCollapsed(!sidebarCollapsed)}>
              {sidebarCollapsed ? <FiChevronRight /> : <FiChevronLeft />}
            </button>
          )}
          {/* Only show open/close toggle in sidebar on mobile */}
          {isMobile && (
            <button className="toggle-sidebar" onClick={() => setSidebarOpen(!sidebarOpen)}>
              {sidebarOpen ? <FiChevronLeft /> : <FiChevronRight />}
            </button>
          )}
        </div>
        {/* Profile Section */}
        <div className="profile-section">
          <div className="profile-photo-container">
            {profilePhoto ? (
              <img 
                src={profilePhoto} 
                alt="Profile" 
                className="profile-photo"
                onError={(e) => {
                  e.target.style.display = 'none';
                  if (e.target.nextElementSibling) {
                    e.target.nextElementSibling.style.display = 'flex';
                  }
                }}
              />
            ) : <div className="profile-photo">
              {mentor?.name.split(' ').map(n => n[0]).join('') || mentorProfile.name.split(' ').map(n => n[0]).join('')}
            </div>}
            <div className={`verification-badge ${isVerified ? 'verified' : 'not-verified'}`}>
              {isVerified ? '✓' : '✗'}
            </div>
          </div>
          {(!sidebarCollapsed && sidebarOpen) && (
            <div className="profile-info">
              <h3>{mentor?.name || mentorProfile.name}</h3>
              <p>{mentor?.email || mentorProfile.email}</p>
              <div className="mentor-stats">
                <span><FiStar /> {mentor?.details?.average_rating ? mentor.details.average_rating.toFixed(1) : '0.0'} Rating</span>
                <span><FiTarget /> {totalSessions} sessions</span>
                <span><FiMessageCircle /> {mentor?.feedback_count || 0} feedback</span>
              </div>
            </div>
          )}
        </div>
        {/* Navigation */}
        <nav>
          <ul>
            <li className={activeTab === 'dashboard' ? 'active' : ''} onClick={() => setActiveTab('dashboard')}>
              <span><FiBarChart /></span> {(!sidebarCollapsed && sidebarOpen) && 'Dashboard'}
            </li>
            <li className={activeTab === 'earning' ? 'active' : ''} onClick={() => setActiveTab('earning')}>
              <span><FiDollarSign /></span> {(!sidebarCollapsed && sidebarOpen) && 'Earnings'}
            </li>
            <li className={activeTab === 'messages' ? 'active' : ''} onClick={() => setActiveTab('messages')}>
              <span><FiMail /></span> {(!sidebarCollapsed && sidebarOpen) && 'Messages'}
            </li>
            <li className={activeTab === 'profile' ? 'active' : ''} onClick={() => setActiveTab('profile')}>
              <span><FiUser /></span> {(!sidebarCollapsed && sidebarOpen) && 'Profile'}
            </li>
            <li className={activeTab === 'sessions' ? 'active' : ''} onClick={() => setActiveTab('sessions')}>
              <span><FiCalendar /></span> {(!sidebarCollapsed && sidebarOpen) && 'Sessions'}
            </li>
            <li className={activeTab === 'events' ? 'active' : ''} onClick={() => setActiveTab('events')}>
              <span><FiCalendar /></span> {(!sidebarCollapsed && sidebarOpen) && 'Events'}
            </li>
            <li className={activeTab === 'feedback' ? 'active' : ''} onClick={() => setActiveTab('feedback')}>
              <span><FiStar /></span> {(!sidebarCollapsed && sidebarOpen) && 'Feedback'}
            </li>
            <li className={activeTab === 'customerService' ? 'active' : ''} onClick={() => setActiveTab('customerService')}>
              <span><FiHeadphones /></span> {(!sidebarCollapsed && sidebarOpen) && 'Customer Service'}
            </li>
          </ul>
        </nav>
        {/* Logout */}
        <div className="logout-section">
          <button className="logout-button" onClick={handleLogout}>
            <span><FiLogOut /></span> {(!sidebarCollapsed && sidebarOpen) && 'Logout'}
          </button>
        </div>
      </div>
    </>
  );
};

export default Sidebar;