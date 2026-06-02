import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import API from "../api/axios";
import { useAuth } from "../context/AuthContext";

export default function PropertyDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [property, setProperty] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [checkIn, setCheckIn] = useState("");
  const [checkOut, setCheckOut] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchProperty();
    fetchReviews();
  }, [id]);

  const fetchProperty = async () => {
    try {
      const res = await API.get(`/properties/${id}`);
      setProperty(res.data);
    } catch (err) {
      console.error("Failed to fetch property");
    }
  };

  const fetchReviews = async () => {
    try {
      const res = await API.get(`/reviews/property/${id}`);
      setReviews(res.data.reviews || []);
    } catch (err) {
      console.error("Failed to fetch reviews");
    }
  };

  const handleBook = async () => {
    if (!user) {
      navigate("/login");
      return;
    }
    if (!checkIn || !checkOut) {
      setError("Please select check-in and check-out dates");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const res = await API.post("/bookings/", {
        property_id: parseInt(id),
        check_in_date: checkIn,
        check_out_date: checkOut,
      });
      navigate(`/guest/booking/${res.data.id}/payment`);
    } catch (err) {
      setError(err.response?.data?.detail || "Booking failed");
    } finally {
      setLoading(false);
    }
  };

  if (!property) {
    return <div className="text-center py-20">Loading...</div>;
  }

  const nights =
    checkIn && checkOut
      ? Math.ceil(
          (new Date(checkOut) - new Date(checkIn)) / (1000 * 60 * 60 * 24)
        )
      : 0;

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      {/* Images */}
      <div className="bg-gray-200 h-72 rounded-2xl flex items-center justify-center mb-6 overflow-hidden">
        {property.images && property.images.length > 0 ? (
          <img
            src={property.images[0].image_url}
            alt={property.title}
            className="w-full h-full object-cover"
          />
        ) : (
          <span className="text-gray-400 text-6xl">🏠</span>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Property Info */}
        <div className="md:col-span-2">
          <h1 className="text-3xl font-bold text-gray-800">{property.title}</h1>
          <p className="text-gray-500 mt-1">📍 {property.location}</p>
          <p className="text-gray-500">👥 Up to {property.max_guests} guests</p>

          {property.average_rating && (
            <p className="text-yellow-500 mt-1">
              ⭐ {property.average_rating} ({property.total_reviews} reviews)
            </p>
          )}

          <p className="text-gray-700 mt-4">{property.description}</p>

          {/* Reviews */}
          <div className="mt-8">
            <h2 className="text-xl font-bold text-gray-800 mb-4">Reviews</h2>
            {reviews.length === 0 ? (
              <p className="text-gray-500">No reviews yet</p>
            ) : (
              reviews.map((review) => (
                <div
                  key={review.id}
                  className="border-b border-gray-100 py-4"
                >
                  <div className="flex justify-between">
                    <span className="font-medium">{review.guest_name}</span>
                    <span className="text-yellow-500">
                      {"⭐".repeat(review.rating)}
                    </span>
                  </div>
                  <p className="text-gray-600 text-sm mt-1">{review.comment}</p>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Booking Card */}
        <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm h-fit">
          <p className="text-2xl font-bold text-blue-600">
            ₹{property.price_per_night}
            <span className="text-gray-400 font-normal text-base">/night</span>
          </p>

          <div className="mt-4 space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Check-in
              </label>
              <input
                type="date"
                value={checkIn}
                onChange={(e) => setCheckIn(e.target.value)}
                min={new Date().toISOString().split("T")[0]}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Check-out
              </label>
              <input
                type="date"
                value={checkOut}
                onChange={(e) => setCheckOut(e.target.value)}
                min={checkIn || new Date().toISOString().split("T")[0]}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {nights > 0 && (
              <div className="bg-gray-50 rounded-lg p-3 text-sm">
                <div className="flex justify-between">
                  <span>₹{property.price_per_night} × {nights} nights</span>
                  <span>₹{property.price_per_night * nights}</span>
                </div>
                <div className="flex justify-between font-bold mt-2 pt-2 border-t">
                  <span>Total</span>
                  <span>₹{property.price_per_night * nights}</span>
                </div>
              </div>
            )}

            {error && (
              <p className="text-red-500 text-sm">{error}</p>
            )}

            <button
              onClick={handleBook}
              disabled={loading}
              className="w-full bg-blue-600 text-white py-2.5 rounded-lg font-medium hover:bg-blue-700 transition"
            >
              {loading ? "Booking..." : "Book Now"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}