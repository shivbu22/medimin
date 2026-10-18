"use client";

import { useState, useEffect, useRef, useCallback } from "react";

// ═══════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════
interface MedicineBasic {
  id: number;
  name: string;
  slug: string;
  active_salt: string;
  manufacturer: string;
  category: string | null;
  dosage_form: string;
  pack_size_label: string;
  lowest_price: number | null;
  highest_price: number | null;
  pharmacy_count: number;
  has_cheaper_substitute: boolean;
  cheapest_substitute_price: number | null;
}

interface PriceOut {
  id: number;
  pharmacy_id: number;
  pharmacy_name: string;
  pharmacy_slug: string;
  pharmacy_logo: string | null;
  pharmacy_url: string;
  pack_size: string;
  mrp: number;
  selling_price: number;
  unit_price: number | null;
  discount_percentage: number;
  in_stock: boolean;
  product_url: string | null;
  savings: number | null;
}

interface SubstituteOut {
  id: number;
  name: string;
  slug: string;
  manufacturer: string;
  lowest_price: number | null;
  price_diff_percentage: number | null;
}

interface MedicineDetail {
  id: number;
  name: string;
  slug: string;
  active_salt: string;
  manufacturer: string;
  category: string | null;
  dosage_form: string;
  pack_size_label: string;
  description: string | null;
  uses: string | null;
  side_effects: string | null;
  is_otc: boolean;
  is_prescription: boolean;
  dpco_controlled: boolean;
  prices: PriceOut[];
  substitutes_count: number;
  is_syncing: boolean;
  last_updated: string | null;
}

interface CompareResponse {
  medicine: MedicineDetail;
  prices: PriceOut[];
  cheapest: PriceOut | null;
  most_expensive: PriceOut | null;
  max_savings_percentage: number;
  substitutes: SubstituteOut[];
}

interface SearchResponse {
  query: string;
  results: MedicineBasic[];
  count: number;
  total_pages: number;
  page: number;
  syncing?: boolean;
}

interface AutocompleteItem {
  id: number;
  name: string;
  slug: string;
  active_salt: string;
  manufacturer: string;
  category: string | null;
}

interface CategoryOut {
  id: number;
  name: string;
  slug: string;
  icon: string;
  description: string | null;
  medicine_count: number;
}

interface StatsResponse {
  total_medicines: number;
  total_pharmacies: number;
  total_prices: number;
  avg_savings_percentage: number;
  max_savings_percentage: number;
  categories_count: number;
}

// ═══════════════════════════════════════════
// CONSTANTS
// ═══════════════════════════════════════════
const API_BASE = "http://localhost:8000/api/v1";

// Pharmacy brand colors
const PHARMACY_COLORS: Record<string, string> = {
  "tata-1mg": "#FF6F61",
  "apollo-pharmacy": "#1A73E8",
  pharmeasy: "#10B981",
  netmeds: "#E91E63",
  truemeds: "#7C3AED",
  medplusmart: "#F59E0B",
};

// ═══════════════════════════════════════════
// COMPONENT: Stat Card
// ═══════════════════════════════════════════
function StatCard({
  icon,
  label,
  value,
  suffix,
}: {
  icon: string;
  label: string;
  value: number | string;
  suffix?: string;
}) {
  return (
    <div className="glass rounded-2xl px-5 py-4 flex items-center gap-4 price-card">
      <span className="text-2xl">{icon}</span>
      <div>
        <p className="text-2xl font-extrabold text-white stat-number">
          {value}
          {suffix && (
            <span className="text-sm font-semibold text-[#0D9488] ml-1">
              {suffix}
            </span>
          )}
        </p>
        <p className="text-xs font-medium text-[#64748B] uppercase tracking-wider">
          {label}
        </p>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════
// COMPONENT: Skeleton Loader
// ═══════════════════════════════════════════
function SkeletonCard() {
  return (
    <div className="bg-[#18181B] rounded-2xl p-5 border border-[#27272A]">
      <div className="animate-shimmer h-5 w-48 rounded mb-3" />
      <div className="animate-shimmer h-4 w-32 rounded mb-4" />
      <div className="flex gap-3">
        <div className="animate-shimmer h-8 w-20 rounded-full" />
        <div className="animate-shimmer h-8 w-24 rounded-full" />
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════
// COMPONENT: Price Comparison Row
// ═══════════════════════════════════════════
function PriceRow({
  price,
  isCheapest,
  index,
  medicineId,
  onRedirect,
}: {
  price: PriceOut;
  isCheapest: boolean;
  index: number;
  medicineId: number;
  onRedirect: (priceId: number, name: string) => void;
}) {
  const brandColor = PHARMACY_COLORS[price.pharmacy_slug] || "#6B7280";

  return (
    <div
      className="price-card bg-[#18181B] sm:bg-transparent rounded-xl p-4 sm:p-5 border-b border-[#27272A] hover:bg-[#27272A]/30 transition-colors animate-float-up flex flex-col sm:flex-row sm:items-center justify-between gap-4"
      style={{ animationDelay: `${index * 0.05}s`, opacity: 0 }}
    >
      {/* LEFT: Pharmacy Info */}
      <div className="flex items-center gap-4 min-w-[200px]">
        <div
          className="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-sm shadow-md shadow-black/50"
          style={{ background: brandColor }}
        >
          {price.pharmacy_name.charAt(0)}
        </div>
        <div>
          <p className="font-bold text-base text-white truncate max-w-[150px] sm:max-w-none">
            {price.pharmacy_name}
          </p>
          {(!price.in_stock) && (
            <span className="text-[10px] text-red-500 font-bold uppercase">Out of Stock</span>
          )}
        </div>
      </div>

      {/* RIGHT: Price, Savings, Buy Button */}
      <div className="flex items-center justify-between sm:justify-end gap-6 flex-1">
        {/* Savings */}
        <div className="w-20 text-center">
          {price.discount_percentage > 0 && price.in_stock ? (
            <span className="text-xs font-bold text-emerald-500">
              Save {price.discount_percentage.toFixed(0)}%
            </span>
          ) : null}
        </div>

        {/* Price */}
        <div className="w-24 text-right">
          <span className={`text-xl font-black ${isCheapest ? "text-emerald-500" : "text-white"}`}>
            ₹{price.selling_price.toFixed(2)}
          </span>
        </div>

        {/* Buy Now Button */}
        <div>
          <a
            onClick={(e) => {
              e.preventDefault();
              onRedirect(price.id, price.pharmacy_name);
            }}
            href={`${API_BASE}/redirect/${price.id}/`}
            className={`border rounded-lg px-4 py-2 text-sm font-semibold flex items-center gap-2 transition-all duration-200 ${
              price.in_stock 
                ? "border-[#475569] text-[#94A3B8] hover:text-white hover:border-white hover:bg-[#27272A]"
                : "border-[#27272A] text-[#3F3F46] cursor-not-allowed"
            }`}
          >
            Buy Now
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9 18l6-6-6-6"/></svg>
          </a>
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════
// MAIN PAGE COMPONENT
// ═══════════════════════════════════════════
export default function Home() {
  // State
  const [query, setQuery] = useState("");
  const [searchResults, setSearchResults] = useState<MedicineBasic[]>([]);
  const [searchCount, setSearchCount] = useState(0);
  const [isRedirecting, setIsRedirecting] = useState(false);
  const [redirectTarget, setRedirectTarget] = useState<{name: string, url: string} | null>(null);
  const [isSyncing, setIsSyncing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [selectedMedicine, setSelectedMedicine] =
    useState<CompareResponse | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [autocompleteItems, setAutocompleteItems] = useState<
    AutocompleteItem[]
  >([]);
  const [showAutocomplete, setShowAutocomplete] = useState(false);
  const [categories, setCategories] = useState<CategoryOut[]>([]);
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [popularMeds, setPopularMeds] = useState<MedicineBasic[]>([]);
  const [activeView, setActiveView] = useState<
    "home" | "search" | "detail" | "browse"
  >("home");
  const [browseResults, setBrowseResults] = useState<MedicineBasic[]>([]);
  const [browseLetter, setBrowseLetter] = useState<string>("");

  const searchRef = useRef<HTMLDivElement>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const handleRedirect = (priceId: number, pharmacyName: string) => {
    setRedirectTarget({
      name: pharmacyName,
      url: `${API_BASE}/redirect/${priceId}/`
    });
    setIsRedirecting(true);
    
    // Aesthetic pause for premium hand-off feel
    setTimeout(() => {
      window.location.href = `${API_BASE}/redirect/${priceId}/`;
    }, 800);
  };

  // ─── Load initial data ─────────────────
  useEffect(() => {
    const loadInitial = async () => {
      try {
        const [statsRes, catsRes, popularRes] = await Promise.all([
          fetch(`${API_BASE}/stats`),
          fetch(`${API_BASE}/categories`),
          fetch(`${API_BASE}/medicines/popular?limit=8`),
        ]);
        if (statsRes.ok) setStats(await statsRes.json());
        if (catsRes.ok) setCategories(await catsRes.json());
        if (popularRes.ok) setPopularMeds(await popularRes.json());
      } catch {
        /* API may be offline */
      }
    };
    loadInitial();
  }, []);

  // ─── Close autocomplete on outside click ───
  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (
        searchRef.current &&
        !searchRef.current.contains(e.target as Node)
      ) {
        setShowAutocomplete(false);
      }
    };
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  // ─── Autocomplete with debounce ─────────
  const handleQueryChange = (val: string) => {
    setQuery(val);
    if (debounceRef.current) clearTimeout(debounceRef.current);

    if (val.length < 2) {
      setAutocompleteItems([]);
      setShowAutocomplete(false);
      return;
    }

    debounceRef.current = setTimeout(async () => {
      try {
        const res = await fetch(
          `${API_BASE}/medicines/autocomplete?q=${encodeURIComponent(val)}`
        );
        if (res.ok) {
          const items = await res.json();
          setAutocompleteItems(items);
          setShowAutocomplete(items.length > 0);
        }
      } catch {
        /* skip */
      }
    }, 2000);
  };

  // ─── Polling for JIT Sync ────────────────
  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    if (selectedMedicine?.medicine.is_syncing) {
      interval = setInterval(async () => {
        try {
          const res = await fetch(`${API_BASE}/medicines/${selectedMedicine.medicine.id}`);
          if (res.ok) {
            const data: CompareResponse = await res.json();
            setSelectedMedicine(data);
            if (!data.medicine.is_syncing) {
              clearInterval(interval);
            }
          }
        } catch (e) {
          console.error("Polling error:", e);
        }
      }, 3000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [selectedMedicine?.medicine.is_syncing, selectedMedicine?.medicine.id]);

  // ─── Search ────────────────────────────
  const handleSearch = useCallback(
    async (searchQuery?: string) => {
      const q = searchQuery || query;
      if (!q.trim()) return;

      setLoading(true);
      setIsSyncing(false);
      setShowAutocomplete(false);
      setActiveView("search");
      setSelectedMedicine(null);

      try {
        const res = await fetch(
          `${API_BASE}/search?q=${encodeURIComponent(q)}&limit=20`
        );
        if (res.ok) {
          const data: SearchResponse = await res.json();
          setSearchResults(data.results);
          setSearchCount(data.count);
          setIsSyncing(!!data.syncing);
        }
      } catch {
        setSearchResults([]);
      } finally {
        setLoading(false);
      }
    },
    [query]
  );

  // ─── Category search ──────────────────
  const handleCategorySearch = async (catSlug: string, catName: string) => {
    setLoading(true);
    setActiveView("search");
    setQuery(catName);
    setSelectedMedicine(null);

    try {
      const res = await fetch(
        `${API_BASE}/search?q=a&category=${catSlug}&limit=50`
      );
      if (res.ok) {
        const data: SearchResponse = await res.json();
        setSearchResults(data.results);
        setSearchCount(data.count);
      }
    } catch {
      setSearchResults([]);
    } finally {
      setLoading(false);
    }
  };

  // ─── Medicine Detail ──────────────────
  const handleViewDetail = async (medicineId: number) => {
    setDetailLoading(true);
    setActiveView("detail");

    try {
      const res = await fetch(`${API_BASE}/medicines/${medicineId}`);
      if (res.ok) {
        const data: CompareResponse = await res.json();
        setSelectedMedicine(data);
      }
    } catch {
      /* skip */
    } finally {
      setDetailLoading(false);
    }
  };

  // ─── Browse A-Z ────────────────────────
  const handleBrowse = async (letter: string) => {
    setLoading(true);
    setBrowseLetter(letter);
    setActiveView("browse");
    setSelectedMedicine(null);

    try {
      const res = await fetch(`${API_BASE}/browse/${letter}`);
      if (res.ok) {
        const data = await res.json();
        setBrowseResults(data.medicines);
      }
    } catch {
      setBrowseResults([]);
    } finally {
      setLoading(false);
    }
  };

  // ─── Go Home ───────────────────────────
  const goHome = () => {
    setActiveView("home");
    setQuery("");
    setSearchResults([]);
    setSelectedMedicine(null);
  };

  // ═══════════════════════════════════════════
  // RENDER
  // ═══════════════════════════════════════════
  return (
    <div className="min-h-screen bg-[#09090B] font-sans">
      {isRedirecting && (
        <div className="fixed inset-0 z-[100] bg-[#09090B]/90 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[#18181B] border border-[#27272A] p-8 rounded-3xl text-center max-w-sm w-full shadow-2xl">
            <div className="w-16 h-16 bg-teal-500/10 rounded-full flex items-center justify-center mx-auto mb-6 animate-pulse">
              <svg className="w-8 h-8 text-teal-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
            </div>
            <h3 className="text-xl font-bold text-white mb-2">Redirecting to {redirectTarget?.name}</h3>
            <p className="text-[#94A3B8] text-sm">We're finding the best deal for you...</p>
          </div>
        </div>
      )}
      {/* ── HEADER ─────────────────────────────── */}
      <header className="sticky top-0 z-50 glass-dark">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-3 flex items-center justify-between">
          <button
            onClick={goHome}
            className="flex items-center gap-2.5 group"
            id="brand-logo"
          >
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-[#0D9488] to-[#0891B2] flex items-center justify-center shadow-lg shadow-teal-500/20 group-hover:shadow-teal-500/40 transition-shadow">
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="white"
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M12 2L2 7l10 5 10-5-10-5z" />
                <path d="M2 17l10 5 10-5" />
                <path d="M2 12l10 5 10-5" />
              </svg>
            </div>
            <div>
              <h1 className="text-lg font-extrabold text-white tracking-tight leading-none">
                Medimin
              </h1>
              <p className="text-[9px] font-semibold text-teal-300 uppercase tracking-[0.2em]">
                Price Engine
              </p>
            </div>
          </button>

          {/* Inline search bar (visible when not on home) */}
          {activeView !== "home" && (
            <div className="hidden sm:block flex-1 max-w-md mx-6" ref={searchRef}>
              <div className="relative">
                <input
                  type="text"
                  value={query}
                  onChange={(e) => handleQueryChange(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                  placeholder="Search medicines..."
                  className="w-full px-4 py-2 rounded-xl bg-[#18181B]/10 border border-white/15 text-white placeholder:text-white/40 text-sm font-medium focus:outline-none focus:bg-[#18181B]/15 focus:border-teal-400/50 transition-all search-input"
                  id="header-search-input"
                />
                {showAutocomplete && autocompleteItems.length > 0 && (
                  <div className="absolute top-full left-0 right-0 mt-2 bg-[#18181B] rounded-xl shadow-2xl border border-[#27272A] autocomplete-dropdown z-50 overflow-hidden">
                    {autocompleteItems.map((item) => (
                      <button
                        key={item.id}
                        onClick={() => {
                          setQuery(item.name);
                          setShowAutocomplete(false);
                          handleSearch(item.name);
                        }}
                        className="w-full px-4 py-3 text-left hover:bg-teal-50 transition-colors border-b border-[#3F3F46] last:border-0 flex items-center justify-between group"
                      >
                        <div>
                          <p className="text-sm font-semibold text-white group-hover:text-[#0D9488]">
                            {item.name}
                          </p>
                          <p className="text-xs text-[#94A3B8]">
                            {item.active_salt}
                          </p>
                        </div>
                        <span className="text-[10px] font-medium text-[#94A3B8] bg-[#27272A] px-2 py-0.5 rounded-full">
                          {item.manufacturer}
                        </span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {activeView !== "home" && (
            <button
              onClick={goHome}
              className="text-sm font-semibold text-teal-300 hover:text-white transition-colors"
              id="home-link"
            >
              ← Home
            </button>
          )}
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 sm:px-6 py-6">
        {/* ════════════════════════════════════════
            HOME VIEW
        ════════════════════════════════════════ */}
        {activeView === "home" && (
          <div className="animate-float-up">
            {/* Hero Section */}
            <section className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-[#0F172A] via-[#0F766E] to-[#0891B2] p-8 sm:p-12 mb-8 shadow-2xl">
              <div className="absolute inset-0 opacity-10">
                <svg width="100%" height="100%">
                  <defs>
                    <pattern
                      id="grid"
                      width="40"
                      height="40"
                      patternUnits="userSpaceOnUse"
                    >
                      <path
                        d="M 40 0 L 0 0 0 40"
                        fill="none"
                        stroke="white"
                        strokeWidth="0.5"
                      />
                    </pattern>
                  </defs>
                  <rect width="100%" height="100%" fill="url(#grid)" />
                </svg>
              </div>

              <div className="relative z-10 max-w-2xl">
                <h2 className="text-3xl sm:text-4xl font-extrabold text-white leading-tight mb-3">
                  Compare Medicine Prices.
                  <br />
                  <span className="text-teal-300">Save up to 85%.</span>
                </h2>
                <p className="text-base text-white/70 mb-8 leading-relaxed max-w-lg">
                  Search across 6 top pharmacy platforms. Find the lowest price
                  and discover cheaper generic alternatives — instantly.
                </p>

                {/* Hero Search */}
                <div className="relative" ref={searchRef}>
                  <div className="flex gap-3">
                    <div className="relative flex-1">
                      <svg
                        className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[#94A3B8]"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                        strokeWidth="2"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z"
                        />
                      </svg>
                      <input
                        type="text"
                        value={query}
                        onChange={(e) => handleQueryChange(e.target.value)}
                        onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                        placeholder="Search by medicine name, salt, or brand..."
                        className="w-full pl-12 pr-4 py-4 rounded-2xl bg-[#18181B] border-2 border-transparent text-white text-base font-medium placeholder:text-[#94A3B8] focus:outline-none focus:border-[#0D9488] transition-all shadow-lg search-input"
                        id="main-search-input"
                      />

                      {/* Autocomplete */}
                      {showAutocomplete && autocompleteItems.length > 0 && (
                        <div className="absolute top-full left-0 right-0 mt-2 bg-[#18181B] rounded-2xl shadow-2xl border border-[#27272A] autocomplete-dropdown z-50 overflow-hidden max-h-[320px] overflow-y-auto">
                          {autocompleteItems.map((item) => (
                            <button
                              key={item.id}
                              onClick={() => {
                                setQuery(item.name);
                                setShowAutocomplete(false);
                                handleSearch(item.name);
                              }}
                              className="w-full px-5 py-3.5 text-left hover:bg-teal-50 transition-colors border-b border-[#3F3F46] last:border-0 flex items-center justify-between group"
                            >
                              <div>
                                <p className="text-sm font-bold text-white group-hover:text-[#0D9488] transition-colors">
                                  {item.name}
                                </p>
                                <p className="text-xs text-[#94A3B8] mt-0.5">
                                  {item.active_salt} · {item.manufacturer}
                                </p>
                              </div>
                              {item.category && (
                                <span className="text-[10px] font-semibold text-teal-700 bg-teal-50 px-2.5 py-1 rounded-full">
                                  {item.category}
                                </span>
                              )}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                    <button
                      onClick={() => handleSearch()}
                      disabled={loading || !query.trim()}
                      className="bg-gradient-to-r from-[#0D9488] to-[#059669] hover:from-[#0F766E] hover:to-[#047857] text-white font-bold px-8 py-4 rounded-2xl shadow-lg shadow-teal-600/30 transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed whitespace-nowrap"
                      id="search-button"
                    >
                      {loading ? (
                        <span className="flex items-center gap-2">
                          <svg
                            className="animate-spin w-4 h-4"
                            viewBox="0 0 24 24"
                          >
                            <circle
                              className="opacity-25"
                              cx="12"
                              cy="12"
                              r="10"
                              stroke="currentColor"
                              strokeWidth="4"
                              fill="none"
                            />
                            <path
                              className="opacity-75"
                              fill="currentColor"
                              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                            />
                          </svg>
                          Searching
                        </span>
                      ) : (
                        "Compare"
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </section>

            {/* Stats Strip */}
            {stats && (
              <section className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-8">
                <StatCard
                  icon="💊"
                  label="Medicines"
                  value={stats.total_medicines}
                />
                <StatCard
                  icon="🏪"
                  label="Pharmacies"
                  value={stats.total_pharmacies}
                />
                <StatCard
                  icon="📊"
                  label="Price Points"
                  value={stats.total_prices}
                />
                <StatCard
                  icon="💰"
                  label="Avg. Savings"
                  value={stats.avg_savings_percentage}
                  suffix="%"
                />
              </section>
            )}

            {/* Categories */}
            {categories.length > 0 && (
              <section className="mb-8">
                <h3 className="text-lg font-extrabold text-white mb-4 flex items-center gap-2">
                  <span className="w-1.5 h-6 rounded-full bg-gradient-to-b from-[#0D9488] to-[#0891B2]" />
                  Browse by Category
                </h3>
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 stagger-children">
                  {categories.map((cat) => (
                    <button
                      key={cat.id}
                      onClick={() => handleCategorySearch(cat.slug, cat.name)}
                      className="category-pill bg-[#18181B] rounded-2xl p-4 border border-[#27272A] text-left group animate-float-up"
                      style={{ opacity: 0 }}
                      id={`category-${cat.slug}`}
                    >
                      <span className="text-2xl block mb-2">{cat.icon}</span>
                      <p className="font-bold text-sm text-white group-hover:text-[#0D9488] transition-colors">
                        {cat.name}
                      </p>
                      <p className="text-xs text-[#94A3B8] mt-0.5">
                        {cat.medicine_count} medicines
                      </p>
                    </button>
                  ))}
                </div>
              </section>
            )}

            {/* A-Z Browser */}
            <section className="mb-8">
              <h3 className="text-lg font-extrabold text-white mb-4 flex items-center gap-2">
                <span className="w-1.5 h-6 rounded-full bg-gradient-to-b from-[#0891B2] to-[#0369A1]" />
                Browse A–Z
              </h3>
              <div className="flex flex-wrap gap-1.5">
                {"ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("").map((letter) => (
                  <button
                    key={letter}
                    onClick={() => handleBrowse(letter)}
                    className="w-10 h-10 rounded-xl bg-[#18181B] border border-[#27272A] text-sm font-bold text-[#475569] hover:bg-[#0D9488] hover:text-white hover:border-transparent transition-all duration-200 shadow-sm"
                    id={`browse-${letter}`}
                  >
                    {letter}
                  </button>
                ))}
              </div>
            </section>

            {/* Popular Medicines */}
            {popularMeds.length > 0 && (
              <section>
                <h3 className="text-lg font-extrabold text-white mb-4 flex items-center gap-2">
                  <span className="w-1.5 h-6 rounded-full bg-gradient-to-b from-[#059669] to-[#0D9488]" />
                  Popular Medicines
                </h3>
                <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3 stagger-children">
                  {popularMeds.map((med) => (
                    <button
                      key={med.id}
                      onClick={() => handleViewDetail(med.id)}
                      className="price-card bg-[#18181B] rounded-2xl p-4 border border-[#27272A] text-left group animate-float-up"
                      style={{ opacity: 0 }}
                      id={`popular-${med.slug}`}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <p className="font-bold text-sm text-white group-hover:text-[#0D9488] transition-colors leading-tight">
                          {med.name}
                        </p>
                        {med.has_cheaper_substitute && (
                          <span className="savings-badge text-[8px] font-bold bg-emerald-100 text-emerald-700 px-1.5 py-0.5 rounded-full ml-1 flex-shrink-0">
                            SWITCH
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-[#94A3B8] mb-3">
                        {med.active_salt}
                      </p>
                      <div className="flex items-center justify-between">
                        {med.lowest_price ? (
                          <span className="text-base font-extrabold text-white">
                            ₹{med.lowest_price.toFixed(0)}
                          </span>
                        ) : (
                          <span className="text-xs text-[#94A3B8]">
                            Price N/A
                          </span>
                        )}
                        <span className="text-[10px] font-semibold text-[#94A3B8] bg-[#3F3F46] px-2 py-1 rounded-full">
                          {med.pharmacy_count} stores
                        </span>
                      </div>
                    </button>
                  ))}
                </div>
              </section>
            )}
          </div>
        )}

        {/* ════════════════════════════════════════
            SEARCH RESULTS VIEW
        ════════════════════════════════════════ */}
        {activeView === "search" && (
          <div className="animate-float-up">
            {/* Mobile search bar */}
            <div className="sm:hidden mb-4" ref={searchRef}>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={query}
                  onChange={(e) => handleQueryChange(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                  placeholder="Search medicines..."
                  className="flex-1 px-4 py-3 rounded-xl bg-[#18181B] border border-gray-200 text-sm font-medium text-white focus:outline-none focus:border-[#0D9488] search-input"
                  id="mobile-search-input"
                />
                <button
                  onClick={() => handleSearch()}
                  className="bg-[#0D9488] text-white px-4 py-3 rounded-xl font-bold text-sm"
                >
                  Go
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between mb-5">
              <div>
                <h2 className="text-xl font-extrabold text-white">
                  Search Results
                </h2>
                <p className="text-sm text-[#64748B]">
                  {searchCount} results for &quot;{query}&quot;
                </p>
              </div>
              {isSyncing && (
                <div className="flex items-center gap-2 px-4 py-2 bg-teal-500/10 border border-teal-500/20 rounded-full animate-pulse">
                  <div className="w-2 h-2 rounded-full bg-teal-500 shadow-[0_0_10px_rgba(20,184,166,1)]" />
                  <span className="text-xs font-bold text-teal-500 uppercase tracking-wider">Live Crawling</span>
                </div>
              )}
            </div>

            {loading ? (
              <div className="grid sm:grid-cols-2 gap-3">
                {[...Array(4)].map((_, i) => (
                  <SkeletonCard key={i} />
                ))}
              </div>
            ) : searchResults.length === 0 && isSyncing ? (
               <div className="bg-[#18181B] border border-[#27272A] rounded-3xl p-10 text-center animate-float-up">
                  <div className="w-16 h-16 bg-teal-500/10 rounded-full flex items-center justify-center mx-auto mb-6">
                    <svg className="w-8 h-8 text-teal-500 animate-spin-slow" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                  </div>
                  <h3 className="text-xl font-bold text-white mb-2">Finding &quot;{query}&quot; across pharmacies...</h3>
                  <p className="text-[#94A3B8] text-sm max-w-sm mx-auto mb-8">
                    We didn't find this in our local database, so our crawler is searching live for the best prices right now.
                  </p>
                  <button 
                    onClick={() => handleSearch()} 
                    className="bg-[#0D9488] hover:bg-[#0F766E] text-white px-8 py-3 rounded-xl font-bold text-sm transition-all shadow-lg shadow-teal-500/10"
                  >
                    Refresh Results
                  </button>
               </div>
            ) : (
              <div className="grid sm:grid-cols-2 gap-3 stagger-children">
                {searchResults.map((med) => (
                  <button
                    key={med.id}
                    onClick={() => handleViewDetail(med.id)}
                    className="price-card bg-[#18181B] rounded-2xl p-5 border border-[#27272A] text-left group animate-float-up relative"
                    style={{ opacity: 0 }}
                    id={`result-${med.slug}`}
                  >
                    {/* Switch & Save Badge */}
                    {med.has_cheaper_substitute && (
                      <div className="absolute -top-2 right-4 bg-gradient-to-r from-emerald-500 to-teal-500 text-white text-[9px] font-bold uppercase px-3 py-0.5 rounded-full shadow-lg tracking-wider flex items-center gap-1">
                        <svg
                          className="w-3 h-3"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" />
                        </svg>
                        Switch &amp; Save
                      </div>
                    )}

                    <div className="flex items-start justify-between mb-1">
                      <div className="flex-1 mr-3">
                        <p className="font-bold text-white group-hover:text-[#0D9488] transition-colors leading-snug">
                          {med.name}
                        </p>
                        <p className="text-xs font-semibold text-[#94A3B8] uppercase mt-1">
                          {med.manufacturer}
                        </p>
                      </div>
                      {med.lowest_price && (
                        <div className="text-right flex-shrink-0">
                          <p className="text-lg font-black text-white">
                            ₹{med.lowest_price.toFixed(0)}
                          </p>
                          {med.highest_price &&
                            med.highest_price !== med.lowest_price && (
                              <p className="text-[10px] text-[#94A3B8]">
                                to ₹{med.highest_price.toFixed(0)}
                              </p>
                            )}
                        </div>
                      )}
                    </div>

                    <div className="flex items-center gap-2 mt-3 flex-wrap">
                      <span className="text-[10px] font-semibold text-teal-700 bg-teal-50 px-2.5 py-1 rounded-full">
                        {med.active_salt}
                      </span>
                      {med.category && (
                        <span className="text-[10px] font-semibold text-[#64748B] bg-[#27272A] px-2.5 py-1 rounded-full">
                          {med.category}
                        </span>
                      )}
                      <span className="text-[10px] font-medium text-[#94A3B8] ml-auto">
                        {med.pharmacy_count} stores
                      </span>
                    </div>

                    {/* Switch & Save inline info */}
                    {med.has_cheaper_substitute &&
                      med.cheapest_substitute_price && (
                        <div className="mt-3 pt-3 border-t border-emerald-100 bg-emerald-50/50 -mx-5 -mb-5 px-5 pb-4 rounded-b-2xl">
                          <p className="text-xs font-bold text-emerald-700 flex items-center gap-1.5">
                            <svg
                              className="w-3.5 h-3.5"
                              fill="currentColor"
                              viewBox="0 0 20 20"
                            >
                              <path
                                fillRule="evenodd"
                                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L9 9.414V13a1 1 0 102 0V9.414l1.293 1.293a1 1 0 001.414-1.414z"
                                clipRule="evenodd"
                              />
                            </svg>
                            Generic alternative from ₹
                            {med.cheapest_substitute_price.toFixed(0)}
                            {med.lowest_price && (
                              <span className="text-emerald-600 font-extrabold">
                                — Save ₹
                                {(
                                  med.lowest_price -
                                  med.cheapest_substitute_price
                                ).toFixed(0)}
                              </span>
                            )}
                          </p>
                        </div>
                      )}
                  </button>
                ))}
              </div>
            )}

            {!loading && searchResults.length === 0 && (
              <div className="text-center py-16 bg-[#18181B] rounded-2xl border border-[#27272A] shadow-sm">
                <p className="text-4xl mb-3">🔍</p>
                <p className="text-lg font-bold text-[#475569]">
                  No medicines found
                </p>
                <p className="text-sm text-[#94A3B8] mt-1">
                  Try searching by brand name, salt composition, or
                  manufacturer
                </p>
              </div>
            )}
          </div>
        )}

        {/* ════════════════════════════════════════
            BROWSE A-Z VIEW
        ════════════════════════════════════════ */}
        {activeView === "browse" && (
          <div className="animate-float-up">
            <div className="flex items-center gap-3 mb-5">
              <button
                onClick={() => setActiveView("home")}
                className="text-sm font-semibold text-[#0D9488] hover:text-[#0F766E]"
              >
                ← Back
              </button>
              <h2 className="text-xl font-extrabold text-white">
                Medicines starting with &quot;{browseLetter}&quot;
              </h2>
              <span className="text-sm text-[#94A3B8]">
                ({browseResults.length} found)
              </span>
            </div>

            {/* A-Z Navigation */}
            <div className="flex flex-wrap gap-1 mb-5">
              {"ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("").map((letter) => (
                <button
                  key={letter}
                  onClick={() => handleBrowse(letter)}
                  className={`w-8 h-8 rounded-lg text-xs font-bold transition-all duration-200 ${
                    browseLetter === letter
                      ? "bg-[#0D9488] text-white shadow-md"
                      : "bg-[#18181B] border border-[#27272A] text-[#475569] hover:bg-teal-50"
                  }`}
                >
                  {letter}
                </button>
              ))}
            </div>

            {loading ? (
              <div className="grid sm:grid-cols-2 gap-3">
                {[...Array(4)].map((_, i) => (
                  <SkeletonCard key={i} />
                ))}
              </div>
            ) : (
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3 stagger-children">
                {browseResults.map((med) => (
                  <button
                    key={med.id}
                    onClick={() => handleViewDetail(med.id)}
                    className="price-card bg-[#18181B] rounded-2xl p-4 border border-[#27272A] text-left group animate-float-up"
                    style={{ opacity: 0 }}
                  >
                    <p className="font-bold text-sm text-white group-hover:text-[#0D9488] mb-1">
                      {med.name}
                    </p>
                    <p className="text-xs text-[#94A3B8] mb-2">
                      {med.active_salt}
                    </p>
                    <div className="flex items-center justify-between">
                      {med.lowest_price ? (
                        <span className="font-extrabold text-white">
                          ₹{med.lowest_price.toFixed(0)}
                        </span>
                      ) : (
                        <span className="text-xs text-[#94A3B8]">—</span>
                      )}
                      <span className="text-[10px] text-[#94A3B8]">
                        {med.pharmacy_count} stores
                      </span>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ════════════════════════════════════════
            MEDICINE DETAIL VIEW (Price Comparison)
        ════════════════════════════════════════ */}
        {activeView === "detail" && (
          <div className="animate-float-up">
            <button
              onClick={() => {
                if (searchResults.length > 0) setActiveView("search");
                else setActiveView("home");
              }}
              className="text-sm font-semibold text-[#0D9488] hover:text-[#0F766E] mb-5 inline-flex items-center gap-1"
              id="back-to-results"
            >
              ← Back to results
            </button>

            {detailLoading ? (
              <div className="grid gap-3">
                {[...Array(3)].map((_, i) => (
                  <SkeletonCard key={i} />
                ))}
              </div>
            ) : selectedMedicine ? (
              <div className="grid lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 space-y-6">
                  {/* Title & Filter Bar (Matching RxJinn Structurally) */}
                  <div>
                    <h2 className="text-3xl font-extrabold text-white leading-tight flex items-center justify-between flex-wrap gap-3">
                      <div className="flex items-center gap-3">
                        {selectedMedicine.medicine.name}
                        {selectedMedicine.medicine.is_syncing && (
                          <div className="flex items-center gap-1.5 px-3 py-1 bg-teal-500/10 border border-teal-500/20 rounded-full animate-pulse">
                            <div className="w-1.5 h-1.5 rounded-full bg-teal-500 shadow-[0_0_8px_rgba(20,184,166,1)]" />
                            <span className="text-[10px] font-bold text-teal-500 uppercase tracking-wider">Live Syncing</span>
                          </div>
                        )}
                      </div>
                      <span className="text-sm font-semibold text-[#64748B] flex items-center gap-1">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/></svg>
                        Available Online
                      </span>
                    </h2>
                    <div className="flex items-center gap-3 mt-1">
                      <p className="text-sm text-[#94A3B8] font-medium">
                        {selectedMedicine.medicine.active_salt}
                      </p>
                      {selectedMedicine.medicine.last_updated && !selectedMedicine.medicine.is_syncing && (
                        <>
                          <span className="text-[#3F3F46]">•</span>
                          <p className="text-[10px] font-bold text-[#64748B] uppercase tracking-wide">
                            Price Updated {new Date(selectedMedicine.medicine.last_updated).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </p>
                        </>
                      )}
                    </div>
                    <a href="#substitutes" onClick={(e) => { e.preventDefault(); document.getElementById('substitutes-section')?.scrollIntoView({ behavior: 'smooth' }); }} className="text-sm font-bold text-red-500 hover:text-red-400 mt-2 inline-block transition-colors">
                      View Substitutes
                    </a>

                    {/* Filter Bar */}
                    <div className="mt-5 bg-[#18181B] border border-[#27272A] rounded-xl p-3 flex flex-wrap lg:flex-nowrap gap-3 items-end shadow-sm">
                      <div className="flex-1 min-w-[120px]">
                         <label className="text-[10px] uppercase font-bold text-[#64748B] mb-1 block">Medication</label>
                         <input type="text" readOnly value={selectedMedicine.medicine.name} className="w-full bg-[#09090B] border border-[#3F3F46] text-sm text-white rounded-lg px-3 py-2" />
                      </div>
                      <div className="flex-1 min-w-[120px]">
                         <label className="text-[10px] uppercase font-bold text-[#64748B] mb-1 block">Form</label>
                         <input type="text" readOnly value={selectedMedicine.medicine.dosage_form} className="w-full bg-[#09090B] border border-[#3F3F46] text-sm text-white rounded-lg px-3 py-2" />
                      </div>
                      <div className="flex-1 min-w-[120px]">
                         <label className="text-[10px] uppercase font-bold text-[#64748B] mb-1 block">Quantity</label>
                         <input type="text" readOnly value={selectedMedicine.medicine.pack_size_label} className="w-full bg-[#09090B] border border-[#3F3F46] text-sm text-white rounded-lg px-3 py-2" />
                      </div>
                      <button className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-bold px-6 py-2 rounded-lg h-[38px] transition-colors">
                        Filter
                      </button>
                    </div>
                  </div>

                  {/* Price Comparison Matrix (Lowest pharmacy prices) */}
                  <div className="bg-[#18181B] rounded-2xl border border-[#27272A] shadow-sm overflow-hidden">
                    <div className="bg-[#18181B] px-5 py-4 border-b border-[#27272A] flex items-center justify-between">
                       <div>
                         <h3 className="text-lg font-black text-white">Lowest pharmacy prices</h3>
                         <p className="text-xs text-[#94A3B8]">Choose a pharmacy to get lowest price</p>
                       </div>
                       <div className="hidden sm:block opacity-60">
                         {/* Optional icon space */}
                         <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
                       </div>
                    </div>
                    <div className="flex flex-col">
                      {selectedMedicine.prices.map((price, idx) => (
                        <PriceRow
                          key={price.pharmacy_id}
                          price={price}
                          isCheapest={idx === 0}
                          index={idx}
                          medicineId={selectedMedicine.medicine.id}
                          onRedirect={(id, name) => handleRedirect(id, name)}
                        />
                      ))}
                    </div>
                  </div>
                  
                  {/* Tabs Section */}
                  <div className="mt-8">
                     <div className="flex flex-wrap gap-2 border-b border-[#27272A] pb-3 mb-5">
                       <button className="text-sm font-bold text-[#94A3B8] hover:text-white px-4 py-1.5 border border-[#3F3F46] rounded-full transition-colors">Overview</button>
                       <button className="text-sm font-bold text-[#94A3B8] hover:text-white px-4 py-1.5 border border-[#3F3F46] rounded-full transition-colors">Uses</button>
                       <button className="text-sm font-bold text-[#94A3B8] hover:text-white px-4 py-1.5 border border-[#3F3F46] rounded-full transition-colors">Side effects</button>
                       <button className="text-sm font-bold text-white bg-blue-600 border border-blue-600 px-4 py-1.5 rounded-full transition-colors">Substitutes</button>
                     </div>
                     
                     <div id="substitutes-section" className="bg-[#18181B] rounded-2xl p-6 border border-[#27272A] text-center">
                        <h3 className="text-2xl font-black text-white mb-6">Substitutes</h3>
                        {selectedMedicine.substitutes.length > 0 ? (
                           <>
                             <div className="flex flex-wrap justify-center gap-3 max-w-2xl mx-auto">
                               {selectedMedicine.substitutes.slice(0, 5).map(sub => (
                                  <button key={sub.id} onClick={() => handleViewDetail(sub.id)} className="bg-[#09090B] border border-[#27272A] hover:border-[#64748B] text-sm font-bold text-white px-4 py-3 rounded-xl flex items-center justify-between gap-3 min-w-[200px] transition-colors">
                                    {sub.name}
                                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#94A3B8" strokeWidth="2"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.3-4.3"/></svg>
                                  </button>
                               ))}
                             </div>
                             <div className="mt-8">
                                <button className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-bold px-6 py-2.5 rounded-full transition-colors shadow-lg">
                                  View All Substitutes
                                </button>
                             </div>
                           </>
                        ) : (
                           <p className="text-[#94A3B8]">No generic substitutes available for this medicine.</p>
                        )}
                     </div>
                  </div>
                </div>

                {/* Sidebar — Quick Summary only (matches new layout structure) */}
                <div className="space-y-5">
                  {/* Quick Stats */}
                  <div className="bg-[#18181B] rounded-2xl p-5 border border-[#27272A] shadow-sm sticky top-24">
                    <h4 className="text-sm font-extrabold text-white mb-3 uppercase tracking-wider">
                      Quick Summary
                    </h4>
                    <div className="space-y-3">
                      {selectedMedicine.cheapest && (
                        <div className="flex justify-between items-center">
                          <span className="text-xs text-[#64748B]">
                            Lowest Price
                          </span>
                          <span className="text-sm font-extrabold text-emerald-600">
                            ₹
                            {selectedMedicine.cheapest.selling_price.toFixed(2)}
                          </span>
                        </div>
                      )}
                      {selectedMedicine.most_expensive && (
                        <div className="flex justify-between items-center">
                          <span className="text-xs text-[#64748B]">
                            Highest Price
                          </span>
                          <span className="text-sm font-bold text-red-500">
                            ₹
                            {selectedMedicine.most_expensive.selling_price.toFixed(
                              2
                            )}
                          </span>
                        </div>
                      )}
                      {selectedMedicine.cheapest &&
                        selectedMedicine.most_expensive && (
                          <div className="flex justify-between items-center pt-2 border-t border-[#27272A]">
                            <span className="text-xs text-[#64748B]">
                              You Save
                            </span>
                            <span className="text-sm font-extrabold text-emerald-600">
                              ₹
                              {(
                                selectedMedicine.most_expensive.selling_price -
                                selectedMedicine.cheapest.selling_price
                              ).toFixed(2)}
                            </span>
                          </div>
                        )}
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-16">
                <p className="text-lg font-bold text-[#475569]">
                  Medicine not found
                </p>
              </div>
            )}
          </div>
        )}
      </main>

      {/* ── FOOTER ─────────────────────────────── */}
      <footer className="mt-auto border-t border-gray-200 bg-[#18181B]/80 backdrop-blur-sm">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-6 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-[#0D9488] to-[#0891B2] flex items-center justify-center">
              <svg
                width="12"
                height="12"
                viewBox="0 0 24 24"
                fill="none"
                stroke="white"
                strokeWidth="3"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M12 2L2 7l10 5 10-5-10-5z" />
                <path d="M2 17l10 5 10-5" />
              </svg>
            </div>
            <span className="text-sm font-bold text-[#475569]">
              Medimin
            </span>
            <span className="text-xs text-[#94A3B8]">
              © {new Date().getFullYear()}
            </span>
          </div>
          <p className="text-xs text-[#94A3B8] text-center sm:text-right max-w-md">
            Prices shown are for informational purposes only. Always consult
            your doctor before switching medicines. Medimin doesn&apos;t sell
            medicines.
          </p>
        </div>
      </footer>
    </div>
  );
}
