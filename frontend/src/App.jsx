import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import Navbar from "./components/Navbar";
import Login from "./pages/auth/Login";
import Register from "./pages/auth/Register";
import Home from "./pages/Home";
import PropertyDetail from "./pages/PropertyDetail";
import GuestDashboard from "./pages/guest/GuestDashboard";
import HostDashboard from "./pages/host/HostDashboard";
import AddProperty from "./pages/host/AddProperty";
import PaymentPage from "./pages/guest/PaymentPage";

function ProtectedRoute({ children, role }) {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" />;
  if (role && user.role !== role) return <Navigate to="/" />;
  return children;
}

function AppRoutes() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/property/:id" element={<PropertyDetail />} />
        <Route path="/guest/dashboard" element={<ProtectedRoute><GuestDashboard /></ProtectedRoute>} />
        <Route path="/guest/booking/:bookingId/payment" element={<ProtectedRoute><PaymentPage /></ProtectedRoute>} />
        <Route path="/host/dashboard" element={<ProtectedRoute role="host"><HostDashboard /></ProtectedRoute>} />
        <Route path="/host/add-property" element={<ProtectedRoute role="host"><AddProperty /></ProtectedRoute>} />
      </Routes>
    </>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}