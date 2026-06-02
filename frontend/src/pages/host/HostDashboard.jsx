import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import API from "../../api/axios";

export default function HostDashboard() {
  const [dashboard, setDashboard] = useState(null);
  const [properties, setProperties] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    fetchDashboard();
    fetchProperties();
  }, []);

  const fetchDashboard = async () => {
    try {
      const res = await API.get("/bookings/host-dashboard");
      setDashboard(res.data);
    } catch (err) {
      console.error("Failed to fetch dashboard");
    }
  };

  const fetchProperties = async () => {
    try {
      const res = await API.get("/properties/host/my-properties");
      setProperties(res.data);
    } catch (err) {
      console.error("Failed to fetch properties");
    }
  };

  const handleDelete = async (propertyId) => {
    if (!window.confirm("Delete this property?")) return;
    try {
      await API.delete(`/properties/${propertyId}`);
      fetchProperties();
    } catch (err) {
      alert(err.response?.data?.detail || "Delete failed");
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Host Dashboard</h1>
        <button
          onClick={() => navigate("/host/add-property")}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700"
        >
          + Add Property
        </button>
      </div>

      {/* Stats Cards */}
      {dashboard && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="bg-blue-50 rounded-xl p-5">
            <p className="text-blue-600 text-sm font-medium">Total Bookings</p>
            <p className="text-3xl font-bold text-blue-700 mt-1">
              {dashboard.total_bookings}
            </p>
          </div>
          <div className="bg-green-50 rounded-xl p-5">
            <p className="text-green-600 text-sm font-medium">Total Revenue</p>
            <p className="text-3xl font-bold text-green-700 mt-1">
              ₹{dashboard.total_revenue}
            </p>
          </div>
          <div className="bg-purple-50 rounded-xl p-5">
            <p className="text-purple-600 text-sm font-medium">Upcoming Stays</p>
            <p className="text-3xl font-bold text-purple-700 mt-1">
              {dashboard.upcoming_stays}
            </p>
          </div>
        </div>
      )}

      {/* Properties List */}
      <h2 className="text-xl font-bold text-gray-800 mb-4">My Properties</h2>
      {properties.length === 0 ? (
        <div className="text-center py-10 text-gray-500">
          No properties yet. Add your first property!
        </div>
      ) : (
        <div className="space-y-4">
          {properties.map((property) => (
            <div
              key={property.id}
              className="bg-white border border-gray-100 rounded-xl p-5 shadow-sm flex justify-between items-center"
            >
              <div>
                <h3 className="font-semibold text-gray-800">{property.title}</h3>
                <p className="text-gray-500 text-sm">📍 {property.location}</p>
                <p className="text-blue-600 font-medium text-sm">
                  ₹{property.price_per_night}/night
                </p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => navigate(`/property/${property.id}`)}
                  className="text-sm text-blue-600 border border-blue-600 px-3 py-1.5 rounded-lg hover:bg-blue-50"
                >
                  View
                </button>
                <button
                  onClick={() => handleDelete(property.id)}
                  className="text-sm text-red-500 border border-red-500 px-3 py-1.5 rounded-lg hover:bg-red-50"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}