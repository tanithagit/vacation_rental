import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import API from "../api/axios";

export default function Home() {
  const [properties, setProperties] = useState([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState({
    location: "",
    min_price: "",
    max_price: "",
    max_guests: "",
  });
  const navigate = useNavigate();

  const fetchProperties = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (search.location) params.append("location", search.location);
      if (search.min_price) params.append("min_price", search.min_price);
      if (search.max_price) params.append("max_price", search.max_price);
      if (search.max_guests) params.append("max_guests", search.max_guests);

      const response = await API.get(`/properties/search?${params}`);
      setProperties(response.data.properties || []);
    } catch (err) {
      console.error("Failed to fetch properties", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProperties();
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Hero Section */}
      <div className="bg-blue-600 text-white rounded-2xl p-10 mb-8 text-center">
        <h1 className="text-4xl font-bold mb-2">Find Your Perfect Stay</h1>
        <p className="text-blue-100 mb-6">
          Discover amazing properties around the world
        </p>

        {/* Search Bar */}
        <div className="bg-white rounded-xl p-4 flex flex-wrap gap-3 max-w-3xl mx-auto">
          <input
            type="text"
            placeholder="Search by location..."
            value={search.location}
            onChange={(e) => setSearch({ ...search, location: e.target.value })}
            className="flex-1 border border-gray-200 rounded-lg px-3 py-2 text-gray-800 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <input
            type="number"
            placeholder="Min price"
            value={search.min_price}
            onChange={(e) => setSearch({ ...search, min_price: e.target.value })}
            className="w-28 border border-gray-200 rounded-lg px-3 py-2 text-gray-800 text-sm focus:outline-none"
          />
          <input
            type="number"
            placeholder="Max price"
            value={search.max_price}
            onChange={(e) => setSearch({ ...search, max_price: e.target.value })}
            className="w-28 border border-gray-200 rounded-lg px-3 py-2 text-gray-800 text-sm focus:outline-none"
          />
          <input
            type="number"
            placeholder="Guests"
            value={search.max_guests}
            onChange={(e) => setSearch({ ...search, max_guests: e.target.value })}
            className="w-24 border border-gray-200 rounded-lg px-3 py-2 text-gray-800 text-sm focus:outline-none"
          />
          <button
            onClick={fetchProperties}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg text-sm font-medium hover:bg-blue-700"
          >
            Search
          </button>
        </div>
      </div>

      {/* Properties Grid */}
      <h2 className="text-2xl font-bold text-gray-800 mb-4">
        Available Properties
      </h2>

      {loading ? (
        <div className="text-center py-10 text-gray-500">Loading...</div>
      ) : properties.length === 0 ? (
        <div className="text-center py-10 text-gray-500">
          No properties found
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {properties.map((property) => (
            <div
              key={property.id}
              onClick={() => navigate(`/property/${property.id}`)}
              className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden cursor-pointer hover:shadow-md transition"
            >
              {/* Property Image */}
              <div className="bg-gray-200 h-48 flex items-center justify-center">
                {property.images && property.images.length > 0 ? (
                  <img
                    src={property.images[0].image_url}
                    alt={property.title}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <span className="text-gray-400 text-4xl">🏠</span>
                )}
              </div>

              {/* Property Info */}
              <div className="p-4">
                <h3 className="font-semibold text-gray-800 text-lg">
                  {property.title}
                </h3>
                <p className="text-gray-500 text-sm mt-1">
                  📍 {property.location}
                </p>
                <p className="text-gray-500 text-sm">
                  👥 Up to {property.max_guests} guests
                </p>
                <div className="flex justify-between items-center mt-3">
                  <span className="text-blue-600 font-bold text-lg">
                    ₹{property.price_per_night}
                    <span className="text-gray-400 font-normal text-sm">
                      /night
                    </span>
                  </span>
                  <button className="bg-blue-600 text-white px-4 py-1.5 rounded-lg text-sm hover:bg-blue-700">
                    View
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}