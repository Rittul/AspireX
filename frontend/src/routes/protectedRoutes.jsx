// routes/protectedRoutes.js
import PrivateRoute from "../components/PrivateRoute";
import Dashboard from "../Mentor/Pages/Dashboard";
import DashboardLayout from "../components/DashboardLayout";
import StuDashboard from "../Student/pages/Dashboard";
import MentorProfile from "../Student/pages/MentorProfile";
import CommunityFeed from "../components/CommunityFeed";

export const protectedRoutes = [
  { path: "/services/share", element: <PrivateRoute><CommunityFeed /></PrivateRoute> },
  { path: "/student/dashboard", element: <PrivateRoute role="student"><StuDashboard /></PrivateRoute> },
  { path: "/student/dashboard/mentor/:mentorId", element: <PrivateRoute role="student"><StuDashboard /></PrivateRoute> },
  { path: "/mentor/dashboard", element: <PrivateRoute role="mentor"><Dashboard /></PrivateRoute> },
  { path: "/mentor/dashboardLayout", element: <PrivateRoute role="mentor"><DashboardLayout /></PrivateRoute> },
  { path: "/mentor/:id", element: <MentorProfile /> },
];
