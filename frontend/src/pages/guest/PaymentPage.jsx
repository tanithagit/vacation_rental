import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import API from "../../api/axios";

export default function PaymentPage() {
  const { bookingId } = useParams();
  const navigate = useNavigate();
  const [booking, setBooking] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [paymentIntent, setPaymentIntent] = useState(null);

  useEffect(() => {
    fetchBooking();
  }, [bookingId]);

  const fetchBooking = async () => {
    try {
      const res = await API.get(`/bookings/${bookingId}`);
      setBooking(res.data);
    } catch (err) {
      setError("Booking not found");
    }
  };

  const handleCreateIntent = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await API.post("/payments/create-intent", {
        booking_id: parseInt(bookingId),
      });
      setPaymentIntent(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to create payment");
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmPayment = async () => {
    setLoading(true);
    setError("");
    try {
      await API.post("/payments/confirm", {
        payment_intent_id: paymentIntent.payment_intent_id,
      });
      alert("Payment confirmed! Booking is now confirmed.");
      navigate("/guest/dashboard");
    } catch (err) {
      setError(err.response?.data?.detail || "Payment confirmation failed");
    } finally {
      setLoading(false);
    }
  };

  if (!booking) return <div className="text-center py-20">Loading...</div>;

  return (
    <div className="max-w-lg mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">
        Complete Payment
      </h1>

      {/* Booking Summary */}
      <div className="bg-white border border-gray-100 rounded-xl p-6 shadow-sm mb-6">
        <h2 className="font-semibold text-gray-800 mb-3">Booking Summary</h2>
        <div className="space-y-2 text-sm text-gray-600">
          <div className="flex justify-between">
            <span>Booking ID</span>
            <span>#{booking.id}</span>
          </div>
          <div className="flex justify-between">
            <span>Check-in</span>
            <span>{booking.check_in_date}</span>
          </div>
          <div className="flex justify-between">
            <span>Check-out</span>
            <span>{booking.check_out_date}</span>
          </div>
          <div className="flex justify-between font-bold text-gray-800 pt-2 border-t">
            <span>Total Amount</span>
            <span>₹{booking.total_amount}</span>
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-red-100 text-red-600 p-3 rounded-lg mb-4 text-sm">
          {error}
        </div>
      )}

      {!paymentIntent ? (
        <button
          onClick={handleCreateIntent}
          disabled={loading}
          className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700"
        >
          {loading ? "Processing..." : "Proceed to Payment"}
        </button>
      ) : (
        <div className="space-y-4">
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-sm">
            <p className="text-green-700 font-medium">Payment Intent Created!</p>
            <p className="text-green-600 text-xs mt-1">
              ID: {paymentIntent.payment_intent_id}
            </p>
          </div>
          <button
            onClick={handleConfirmPayment}
            disabled={loading}
            className="w-full bg-green-600 text-white py-3 rounded-lg font-medium hover:bg-green-700"
          >
            {loading ? "Confirming..." : "Confirm Payment ₹" + booking.total_amount}
          </button>
        </div>
      )}
    </div>
  );
}