// // src/pages/Dashboard.jsx
// import React, { useEffect, useState } from 'react';
// import API from "../../BackendConn/api";

// const Dashboard = () => {
  // const [mentor, setMentor] = useState(null);
  // const [error, setError] = useState('');

  // useEffect(() => {
  //   const fetchMentorProfile = async () => {
  //     try {
  //       const token = localStorage.getItem('token');
  //       console.log(token);
        
  //       const response = await API.get('mentor/profile/',{
  //         headers: {
  //           Authorization: `Token ${token}`,
  //         }
  //       });
  //       console.log(response.data);
        
  //       setMentor(response.data);
  //     } catch (err) {
  //       setError('Failed to fetch mentor profile');
  //       console.error(err);
  //     }
  //   };

  //   fetchMentorProfile();
  // }, []);

  // useEffect(() => {
  //   if (!localStorage.getItem('token')) {
  //       window.location.href = '/login';
  //   }
  //   }, []);


  // if (error) return <div className="text-red-600">{error}</div>;

//   return (
//     <div className="p-8 text-white bg-gray-900 min-h-screen">
//       <h1 className="text-2xl font-bold mb-4">Mentor Dashboard</h1>
//       {mentor ? (
//         <div className="bg-gray-800 p-4 rounded-lg shadow">
//           <p><strong>Mentor ID:</strong> {mentor.mentor_id}</p>
//           <p><strong>Name:</strong> {mentor.name}</p>
//         </div>
//       ) : (
//         <p>Loading mentor data...</p>
//       )}
//     </div>
//   );
// };

// export default Dashboard;














import React, { useEffect, useState } from 'react';
import Sidebar from './Sidebar';
import DashboardHome from './DashboardHome';
import MenteesPage from './MenteesPage';
import EarningsPage from './EarningsPage';
import Messages from './Messages';
import ProfilePage from './ProfilePage';
import SessionsPage from './SessionsPage';
import FeedbackPage from './FeedbackPage';
import CustomerServicePage from './CustomerServicePage';
import './CSS/Dashboard.css';
import API from "../../BackendConn/api";
import Loader from '../../components/ui/loader';
import Modal from '../../components/ui/Modal';
import CommunityFeed from '../../components/CommunityFeed';
import EventsForm from './EventsForm';

const Dashboard = () => {

  const [activeTab, setActiveTab] = useState(() => {
    if (window.innerWidth < 992) {
      return 'profile';
    }
    return 'dashboard';
  });
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [isMobile, setIsMobile] = useState(window.innerWidth < 992);
  const [mentor, setMentor] = useState(null);
  const [error, setError] = useState('');
  const [showAttendanceModal, setShowAttendanceModal] = useState(false);
  const [attendanceMeeting, setAttendanceMeeting] = useState(null);
  const [attendanceKey, setAttendanceKey] = useState('');
  const [attendanceStatus, setAttendanceStatus] = useState('');
  const [attendanceError, setAttendanceError] = useState('');

  const fetchMentorProfile = async () => {
    try {
      const token = localStorage.getItem('Mentortoken');
      
      const response = await API.get('mentor/profile/',{
        headers: {
          Authorization: `Token ${token}`,
        }
      });
      // console.log(response.data);
      
      setMentor(response.data);
    } catch (err) {
      setError('Failed to fetch mentor profile');
    }
  };

  useEffect(() => {
    fetchMentorProfile();
  }, []);

  useEffect(() => {
    if (!localStorage.getItem('Mentortoken')) {
        window.location.href = '/login';
    }
    }, []);

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 992);
      if (window.innerWidth >= 992) {
        setSidebarOpen(true);
      } else {
        setSidebarOpen(false);
      }
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);


  if (error) return <div className="text-red-600">{error}</div>;
  if (!mentor) return <Loader />;



  
  
  // Mock profile data
  const mentorProfile = {
    name: 'Dr. Sarah Johnson',
    email: 'sarah.johnson@mentor.com',
    expertise: 'Career Counseling & Leadership',
    rating: 4.9,
    sessionsCompleted: 142
  };

  // Function to open modal for a meeting
  const openAttendanceModal = (meeting) => {
    setAttendanceMeeting(meeting);
    setAttendanceKey('');
    setAttendanceStatus('');
    setAttendanceError('');
    setShowAttendanceModal(true);
  };

  // Function to submit attendance key
  const submitAttendanceKey = async () => {
    if (!attendanceMeeting || !attendanceMeeting.meeting_id) {
      setAttendanceError('Meeting ID is missing. Please refresh and try again.');
      return;
    }
    if (!attendanceKey) {
      setAttendanceError('Please enter the student\'s attendance key.');
      return;
    }
    try {
      const token = localStorage.getItem('Mentortoken');
      const res = await API.post('mentor/record_meeting_attendance/', {
        meeting_id: attendanceMeeting.meeting_id,
        role: 'mentor',
        attendance_key: attendanceKey
      }, {
        headers: { Authorization: `Token ${token}` }
      });
      if (res.data.success) {
        setAttendanceStatus('Attendance marked successfully!');
        setAttendanceError('');
        // Optionally update meeting status in UI
      } else if (res.data.message) {
        setAttendanceStatus(res.data.message);
        setAttendanceError('');
      } else {
        setAttendanceError(res.data.error || 'Failed to mark attendance.');
      }
    } catch (err) {
      setAttendanceError(err.response?.data?.error || 'Failed to mark attendance.');
    }
  };

  // Render the appropriate page based on activeTab
  const renderPage = () => {
    switch (activeTab) {
      case 'dashboard':
        return <DashboardHome mentorProfile={mentorProfile} mentor = {mentor} />;
      case 'mentees':
        return <MenteesPage />;
      case 'earning':
        return <EarningsPage />;
      case 'messages':
        return <Messages />;
      case 'profile':
        return <ProfilePage mentorProfile={mentor} onProfileUpdate={fetchMentorProfile} />;
      case 'sessions':
        return <SessionsPage sessions={mentor.meetings || []} />;
      case 'events':
        return <EventsForm />;
      case 'feedback':
        return <FeedbackPage />;
      case 'customerService':
        return <CustomerServicePage />;
      case 'community':
        return <CommunityFeed />;
      default:
        return <DashboardHome mentorProfile={mentorProfile} />;
    }
  };

  return (
    <div className={`mentor-dashboard${sidebarCollapsed ? ' sidebar-collapsed' : ''}`}>
      {/* Sidebar */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        sidebarOpen={sidebarOpen}
        setSidebarOpen={setSidebarOpen}
        mentorProfile={mentorProfile}
        mentor={mentor}
        isMobile={isMobile}
        sidebarCollapsed={sidebarCollapsed}
        setSidebarCollapsed={setSidebarCollapsed}
      />
      {/* Main Content */}
      <div className="main-content">
        {/* Header */}
        <header>
          <div className="header-left">
            {/* Hamburger for mobile */}
            {isMobile && (
              <button className="toggle-sidebar" onClick={() => setSidebarOpen(!sidebarOpen)} style={{marginRight: 12}}>
                {sidebarOpen ? '\u25c0' : '\u2630'}
              </button>
            )}
            {/* Collapse button for desktop */}
            {!isMobile && (
              <button className="toggle-sidebar" onClick={() => setSidebarCollapsed(!sidebarCollapsed)} style={{marginRight: 12}}>
                {sidebarCollapsed ? '\u25b6' : '\u25c0'}
              </button>
            )}
            <h1>Welcome, <span>{mentor?.name || 'Mentor'}!</span></h1>
            <div className="welcome-message">Manage all the things from single dashboard. See latest info sessions, recent conversation and update your recommendations.</div>
          </div>
        </header>
        {renderPage()}
      </div>
      <Modal isOpen={showAttendanceModal} onClose={() => setShowAttendanceModal(false)} title="Mark Attendance">
        <div style={{ marginBottom: 12 }}>
          Ask your student for their attendance key and enter it below to mark your attendance for this meeting.
        </div>
        <input
          type="text"
          value={attendanceKey}
          onChange={e => setAttendanceKey(e.target.value)}
          placeholder="Enter student's attendance key"
          style={{ width: '100%', padding: 8, marginBottom: 8 }}
        />
        <button onClick={submitAttendanceKey} style={{ width: '100%', padding: 10, background: '#1089d3', color: 'white', border: 'none', borderRadius: 6, fontWeight: 'bold' }}>
          Submit
        </button>
        {attendanceStatus && <div style={{ color: 'green', marginTop: 8 }}>{attendanceStatus}</div>}
        {attendanceError && <div style={{ color: 'red', marginTop: 8 }}>{attendanceError}</div>}
      </Modal>
    </div>
  );
};

export default Dashboard;