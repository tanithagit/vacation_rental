import { useState, useEffect } from "react";
import API from "../../api/axios";
import { useNavigate } from "react-router-dom";

export default function GuestDashboard() {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchBookings();
  }, []);

  const fetchBookings = async () => {
    try {
      const res = await API.get("/bookings/my-bookings");
      setBookings(res.data);
    } catch (err) {
      console.error("Failed to fetch bookings");
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = async (bookingId) => {
    if (!window.confirm("Cancel this booking?")) return;
    try {
      await API.put(`/bookings/${bookingId}/cancel`);
      fetchBookings();
    } catch (err) {
      alert(err.response?.data?.detail || "Cancel failed");
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: "bg-yellow-100 text-yellow-700",
      confirmed: "bg-green-100 text-green-700",
      canceled: "bg-red-100 text-red-700",
      completed: "bg-blue-100 text-blue-700",
    };
    return colors[status] || "bg-gray-100 text-gray-700";
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">My Bookings</h1>

      {loading ? (
        <div className="text-center py-10">Loading...</div>
      ) : bookings.length === 0 ? (
        <div className="text-center py-10">
          <p className="text-gray-500 mb-4">No bookings yet</p>
          <button
            onClick={() => navigate("/")}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg"
          >
            Browse Properties
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {bookings.map((booking) => (
            <div
              key={booking.id}
              className="bg-white border border-gray-100 rounded-xl p-6 shadow-sm"
            >
              <div className="flex justify-between items-start">
                <div>
                  <p className="font-semibold text-gray-800">
                    Booking #{booking.id}
                  </p>
                  <p className="text-gray-500 text-sm mt-1">
                    📅 {booking.check_in_date} → {booking.check_out_date}
                  </p>
                  <p className="text-blue-600 font-medium mt-1">
                    ₹{booking.total_amount}
                  </p>
                </div>
                <div className="flex flex-col items-end gap-2">
                  <span className={`text-xs px-3 py-1 rounded-full font-medium ${getStatusColor(booking.status)}`}>
                    {booking.status}
                  </span>
                  {booking.status === "pending" && (
                    <button
                      onClick={() => navigate(`/guest/booking/${booking.id}/payment`)}
                      className="text-xs bg-green-600 text-white px-3 py-1 rounded-full"
                    >
                      Pay Now
                    </button>
                  )}
                  {["pending", "confirmed"].includes(booking.status) && (
                    <button
                      onClick={() => handleCancel(booking.id)}
                      className="text-xs text-red-500 hover:underline"
                    >
                      Cancel
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}