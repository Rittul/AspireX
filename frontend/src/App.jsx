import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { useEffect, useState } from "react";
import { fetchSiteStatus } from "./BackendConn/api";
import { AuthProvider } from "./components/AuthContext";
import ScrollToTopButton from "./components/ScrollToTopButton";

import { publicRoutes } from "./routes/publicRoutes.jsx";
import { protectedRoutes } from "./routes/protectedRoutes.jsx";


function renderRoutes(routeArray) {
  return routeArray.map(({ path, element, children }, index) => (
    <Route key={index} path={path} element={element}>
      {children && renderRoutes(children)}
    </Route>
  ));
}
function App() {
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
    const interval = setInterval(checkStatus, 30000);
    return () => { mounted = false; clearInterval(interval); };
  }, []);

  if (maintenance) {
    return (
      <div className="fixed inset-0 bg-white bg-opacity-95 z-[99999] flex flex-col items-center justify-center">
        <img src="/server-down.svg" alt="Server Down" className="max-w-xs w-[90%] mb-8" />
        <h1 className="text-4xl text-indigo-600 mb-4">🚧 Site Under Construction</h1>
        <p className="text-lg text-gray-800">We'll be back soon. Thank you for your patience!</p>
      </div>
    );
  }

  return (
    <AuthProvider>
      <Router>
        <Routes>
          {renderRoutes([...publicRoutes, ...protectedRoutes])}
        </Routes>
        <ScrollToTopButton />
      </Router>
    </AuthProvider>
  );
}

export default App;
