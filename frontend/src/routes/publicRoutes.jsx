// routes/publicRoutes.js
import Home from "../components/Home";
import UnifiedLogin from "../components/UnifiedLogin";
import UnifiedSignup from "../components/UnifiedSignup";
import ContactPage from "../components/ContactPage";
import CommunityFeed from "../components/CommunityFeed";
import ServicesPage from "../components/ServicesPage";

import EventsList from "../components/EventsList";

export const publicRoutes = [
  { path: "/", element: <Home /> },
  { path: "/login", element: <UnifiedLogin /> },
  { path: "/signup", element: <UnifiedSignup /> },
  { path: "/contact", element: <ContactPage /> },
  { path: "/services", element: <ServicesPage /> },

  { path: "/events", element: <EventsList /> },
];
