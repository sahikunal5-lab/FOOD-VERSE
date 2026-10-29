
import { useState, useEffect } from "react";
import "./App.css";
import {
  Apple, Bell, CalendarDays, CheckCircle2, ChevronDown,
  ChevronRight, HeartPulse, History,
  Home, ImagePlus, Leaf, Menu, ScanLine,
  ShieldCheck, ChefHat, Sparkles, Users, X, ArrowUpRight,
  CircleHelp, Salad, Upload, RefreshCw, Sun, Moon
} from "lucide-react";
import {
  Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip,
  XAxis, YAxis
} from "recharts";

const navItems = [
  { label: "Overview", icon: Home },
  { label: "Food Recognition", icon: ScanLine },
  { label: "Freshness Detector", icon: Apple },
  { label: "Hygiene Monitor", icon: ShieldCheck },
  { label: "Smart Kitchen", icon: ChefHat },
  { label: "Meal Planner", icon: CalendarDays },
  { label: "Analysis History", icon: History },
];

const trendData = [
  { day: "Mon", calories: 1650, protein: 92 },
  { day: "Tue", calories: 1840, protein: 108 },
  { day: "Wed", calories: 1570, protein: 85 },
  { day: "Thu", calories: 1960, protein: 118 },
  { day: "Fri", calories: 1780, protein: 104 },
  { day: "Sat", calories: 2100, protein: 126 },
  { day: "Sun", calories: 1720, protein: 98 },
];

const featureCards = [
  { title: "Food Recognition", desc: "Identify food and estimate its nutrition.", icon: ScanLine, tone: "green" },
  { title: "Freshness Detector", desc: "Explore visible freshness indicators.", icon: Apple, tone: "orange" },
  { title: "Hygiene Monitor", desc: "Review visible kitchen hygiene indicators.", icon: ShieldCheck, tone: "blue" },
  { title: "Smart Kitchen", desc: "Discover recipes from ingredients.", icon: ChefHat, tone: "purple" },
  { title: "Meal Planner", desc: "Create a plan around your preferences.", icon: CalendarDays, tone: "teal" },
  { title: "Analysis History", desc: "Review your saved food analyses.", icon: History, tone: "pink" },
];

function Sidebar({ active, onNavigate, open, onClose }) {
  return (
    <>
      {open && <button className="mobile-overlay" onClick={onClose} aria-label="Close menu" />}
      <aside className={`sidebar ${open ? "sidebar-open" : ""}`}>
        <div className="brand">
          <div className="brand-mark"><Leaf size={22} /></div>
          <div>
            <strong>FoodVerse</strong>
            <span>AI FOOD INTELLIGENCE</span>
          </div>
          <button className="icon-button mobile-close" onClick={onClose} aria-label="Close menu"><X size={18} /></button>
        </div>

        <div className="workspace-label">WORKSPACE</div>
        <nav className="nav-list">
          {navItems.map(({ label, icon: Icon }) => (
            <button
              key={label}
              onClick={() => { onNavigate(label); onClose(); }}
              className={`nav-item ${active === label ? "nav-active" : ""}`}
            >
              <Icon size={18} strokeWidth={1.8} />
              <span>{label}</span>
              {active === label && <span className="nav-dot" />}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="help-card">
            <div className="help-icon"><CircleHelp size={18} /></div>
            <div><strong>Need a hand?</strong><span>Explore FoodVerse tools</span></div>
            <ChevronRight size={16} />
          </div>
          <div className="system-card">
            <span className="status-dot" />
            <div><strong>Workspace status</strong><span>Frontend preview</span></div>
            <span className="status-label">Ready</span>
          </div>
          <div className="profile-row">
            <div className="avatar">F</div>
            <div className="profile-copy"><strong>Food Explorer</strong><span>Personal workspace</span></div>
            <ChevronDown size={16} />
          </div>
        </div>
      </aside>
    </>
  );
}


function Topbar({ active, onMenu, theme, onToggleTheme, apiStatus }) {
  return (
    <header className="topbar">
      <div className="breadcrumbs">
        <button
          className="icon-button menu-button"
          onClick={onMenu}
          aria-label="Open menu"
        >
          <Menu size={20} />
        </button>
        <span>Workspace</span>
        <ChevronRight size={14} />
        <strong>{active || "Overview"}</strong>
      </div>

      <div className="topbar-actions">
        <div className={`api-pill ${apiStatus === "connected" ? "connected" : apiStatus === "error" ? "error" : ""}`}>
          <span className="status-dot" />
          {apiStatus === "connected" ? "API connected" : apiStatus === "error" ? "API offline" : "Checking API..."}
        </div>

        <button
          className="icon-button theme-toggle"
          onClick={onToggleTheme}
          aria-label={`Switch to ${theme === "light" ? "dark" : "light"} mode`}
          title={`Switch to ${theme === "light" ? "dark" : "light"} mode`}
        >
          {theme === "light" ? <Moon size={18} /> : <Sun size={18} />}
        </button>

        <button
          className="icon-button notification-button"
          aria-label="Notifications"
        >
          <Bell size={18} />
          <i />
        </button>

        <div className="top-avatar">FE</div>
      </div>
    </header>
  );
}


function SectionHeading({ eyebrow, title, subtitle, action }) {
  return (
    <div className="section-heading">
      <div>
        {eyebrow && <div className="eyebrow">{eyebrow}</div>}
        <h2>{title}</h2>
        {subtitle && <p>{subtitle}</p>}
      </div>
      {action}
    </div>
  );
}

function MetricCard({ title, value, unit, caption, icon: Icon, tone, progress }) {
  return (
    <article className="metric-card">
      <div className="metric-top">
        <span>{title}</span>
        <span className={`metric-icon ${tone}`}><Icon size={19} /></span>
      </div>
      <div className="metric-value">{value}<small>{unit}</small></div>
      <div className="metric-caption">{caption}</div>
      <div className="progress-track"><div className={`progress-fill ${tone}`} style={{ width: `${progress}%` }} /></div>
    </article>
  );
}


function FoodPreview({ onNavigate, latestNutrition }) {
  return (
    <article className="panel recent-panel">
      <div className="panel-heading">
        <div>
          <h3>Recent food analysis</h3>
          <p>Your latest food insights</p>
        </div>
        <button
          className="text-button"
          onClick={() => onNavigate("Analysis History")}
        >
          View history <ArrowUpRight size={15} />
        </button>
      </div>

      <div className="recent-content">
        <div className="food-illustration">
          <Salad size={58} strokeWidth={1.2} />
          <span>{latestNutrition?.imageName || "Food image preview"}</span>
        </div>

        <div className="recent-details">
          <div className="recent-title-row">
            <h4>
              {latestNutrition
                ? latestNutrition.dish_name ||
                latestNutrition.food_name ||
                "Food analysis complete"
                : "Ready to explore?"}
            </h4>
            <span className="tag tag-green">
              {latestNutrition ? "Analysis complete" : "Getting started"}
            </span>
          </div>

          <p>
            {latestNutrition
              ? `Latest analysis · ${latestNutrition.portionWeightG || 250} g portion`
              : "Upload a food photo to see an AI-generated analysis and estimated nutrition information."}
          </p>

          <div className="macro-grid">
            <div>
              <strong>Calories</strong>
              <span>
                {latestNutrition?.calories_kcal ??
                  latestNutrition?.calories ??
                  "—"}
                <small> kcal</small>
              </span>
            </div>
            <div>
              <strong>Protein</strong>
              <span>
                {latestNutrition?.protein_g ??
                  latestNutrition?.protein ??
                  "—"}
                <small> g</small>
              </span>
            </div>
            <div>
              <strong>Carbs</strong>
              <span>
                {latestNutrition?.carbs_g ??
                  latestNutrition?.carbohydrates_g ??
                  latestNutrition?.carbs ??
                  "—"}
                <small> g</small>
              </span>
            </div>
            <div>
              <strong>Fat</strong>
              <span>
                {latestNutrition?.fat_g ??
                  latestNutrition?.fat ??
                  "—"}
                <small> g</small>
              </span>
            </div>
          </div>

          <button
            className="primary-button"
            onClick={() => onNavigate("Food Recognition")}
          >
            <ImagePlus size={17} /> Analyze food image
          </button>
        </div>
      </div>

      <div className="note-row">
        <Sparkles size={15} />
        {latestNutrition
          ? "Nutrition values are AI-generated estimates and may be inaccurate."
          : "Your latest analysis will appear here after a successful food analysis."}
      </div>
    </article>
  );
}


function TrendChart() {
  return (
    <article className="panel chart-panel">
      <div className="panel-heading">
        <div><h3>Your weekly activity</h3><p>Sample visualization for the interface preview</p></div>
        <span className="chart-legend"><i /> Illustrative data</span>
      </div>
      <div className="chart-wrap">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={trendData} margin={{ top: 12, right: 8, left: -18, bottom: 0 }}>
            <defs>
              <linearGradient id="calorieFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#059669" stopOpacity={0.2} />
                <stop offset="95%" stopColor="#059669" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="#E2E8F0" strokeDasharray="4 4" vertical={false} />
            <XAxis dataKey="day" tick={{ fill: "#64748B", fontSize: 11 }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fill: "#64748B", fontSize: 11 }} axisLine={false} tickLine={false} />
            <Tooltip contentStyle={{ borderRadius: 12, border: "1px solid #E2E8F0", fontSize: 12, boxShadow: "0 4px 6px -1px rgba(0,0,0,0.06)" }} />
            <Area type="monotone" dataKey="calories" name="Sample calories" stroke="#059669" strokeWidth={2.5} fill="url(#calorieFill)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
      <div className="chart-foot"><span><i style={{ display: "inline-block", width: 8, height: 8, borderRadius: "50%", background: "#059669", marginRight: 6 }} /> Calorie intake overview</span><span>Not connected to personal data</span></div>
    </article>
  );
}

function Dashboard({ onNavigate, latestNutrition }) {
  return (
    <div className="page-content">
      <div className="welcome-banner">
        <div className="welcome-copy">
          <div className="eyebrow">YOUR FOOD INTELLIGENCE SPACE</div>
          <h1>A healthier relationship with food <span>🌿</span></h1>
          <p>Explore your meals, understand nutrition, and discover new ways to eat well.</p>
          <button className="primary-button" onClick={() => onNavigate("Food Recognition")}><ScanLine size={17} /> Start food analysis <ChevronRight size={16} /></button>
        </div>
        <div className="welcome-art"><div className="art-circle circle-one" /><div className="art-circle circle-two" /><div className="art-leaf"><Salad size={70} strokeWidth={1.15} /></div><span className="floating-chip chip-one"><Leaf size={14} /> Eat mindfully</span><span className="floating-chip chip-two"><HeartPulse size={14} /> Feel your best</span></div>
      </div>

      <SectionHeading eyebrow="AT A GLANCE" title="Your overview" subtitle="A quick look at the tools available in your workspace." />

      <div className="metrics-grid">
        <MetricCard title="Food analyses" value={latestNutrition ? "1+" : "Ready"} unit="" caption={latestNutrition ? "Analyses logged" : "Upload food to start"} icon={ScanLine} tone="green" progress={latestNutrition ? 80 : 35} />
        <MetricCard title="Nutrition insights" value={latestNutrition ? `${latestNutrition.health_score ?? 88}` : "Active"} unit={latestNutrition ? "/100" : ""} caption={latestNutrition ? (latestNutrition.health_label || "Evaluated") : "Heuristics active"} icon={HeartPulse} tone="purple" progress={latestNutrition ? (latestNutrition.health_score ?? 85) : 60} />
        <MetricCard title="Recipes to discover" value="Smart AI" unit="" caption="Chef assistant ready" icon={ChefHat} tone="orange" progress={75} />
        <MetricCard title="Meal plans" value="Personal" unit="" caption="Goal-scaled meals" icon={CalendarDays} tone="blue" progress={50} />
      </div>

      <div className="main-grid">
        <div className="main-column">
          <FoodPreview onNavigate={onNavigate} latestNutrition={latestNutrition} />
          <TrendChart />
        </div>
        <div className="side-column">
          <article className="panel explore-panel">
            <div className="panel-heading"><div><h3>Explore FoodVerse</h3><p>Choose a tool to get started</p></div></div>
            <div className="feature-list">
              {featureCards.map(({ title, desc, icon: Icon, tone }) => (
                <button className="feature-row" key={title} onClick={() => onNavigate(title)}>
                  <span className={`feature-icon ${tone}`}><Icon size={18} /></span>
                  <span className="feature-copy"><strong>{title}</strong><small>{desc}</small></span>
                  <ChevronRight size={16} className="feature-arrow" />
                </button>
              ))}
            </div>
          </article>
          <article className="tip-card">
            <div className="tip-icon"><Sparkles size={20} /></div>
            <div><span className="eyebrow">A NOTE ABOUT AI</span><h3>Insights, with context</h3><p>Food and nutrition results are estimates. Visual checks cannot confirm that food is safe to eat or replace professional inspection.</p></div>
          </article>
        </div>
      </div>
      <footer className="app-footer"><Leaf size={15} /> FoodVerse AI <span>•</span> AI-assisted food insights <span>•</span> Estimates are not professional advice</footer>
    </div>
  );
}

const moduleInfo = {
  "Food Recognition": { icon: ScanLine, eyebrow: "FOOD INTELLIGENCE", title: "Food recognition & nutrition", subtitle: "Upload a meal image to explore visible foods and estimated nutrition.", action: "Choose food image", note: "The image-analysis endpoint will be connected in the API integration stage." },
  "Freshness Detector": { icon: Apple, eyebrow: "VISUAL ASSESSMENT", title: "Freshness detector", subtitle: "Review visible freshness indicators with context about storage and handling.", action: "Choose food image", note: "Image-based assessment cannot prove food safety, contamination, or edibility." },
  "Hygiene Monitor": { icon: ShieldCheck, eyebrow: "KITCHEN OBSERVATIONS", title: "Hygiene & safety monitor", subtitle: "Prepare an image or video for review of visible kitchen hygiene indicators.", action: "Choose image or video", note: "AI observations are not an official food-safety inspection or certification." },
  "Smart Kitchen": { icon: ChefHat, eyebrow: "COOK SOMETHING GOOD", title: "Smart kitchen", subtitle: "Generate a recipe from ingredients, a food image, or a dish idea.", action: "Explore recipe generator", note: "Recipe generation will use your backend's text and image inputs." },
  "Meal Planner": { icon: CalendarDays, eyebrow: "YOUR FOOD ROUTINE", title: "Personalized meal planner", subtitle: "Set your preferences to request a daily meal plan.", action: "Set up meal profile", note: "Meal suggestions are general guidance, not a substitute for personalized medical nutrition care." },
  "Analysis History": { icon: History, eyebrow: "YOUR RECORDS", title: "Analysis history", subtitle: "Review food-analysis records saved in your database.", action: "Refresh history", note: "Saved records will appear after we connect and test the history endpoint." },
};

function ModulePage({ name, onNutritionSuccess }) {
  const info = moduleInfo[name] || moduleInfo["Food Recognition"];
  const Icon = info.icon;
  const [fileName, setFileName] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  const [portion, setPortion] = useState("250");
  const [context, setContext] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [nutritionResult, setNutritionResult] = useState(null);
  const [nutritionError, setNutritionError] = useState("");
  const [freshnessResult, setFreshnessResult] = useState(null);
  const [freshnessError, setFreshnessError] = useState("");
  const [hygieneResult, setHygieneResult] = useState(null);
  const [hygieneError, setHygieneError] = useState("");
  const [servings, setServings] = useState("2");
  const [skill, setSkill] = useState("Beginner");
  const [cuisine, setCuisine] = useState("Any");
  const [textInput, setTextInput] = useState("");
  const [recipeResult, setRecipeResult] = useState(null);
  const [recipeError, setRecipeError] = useState("");
  const [recipeLoading, setRecipeLoading] = useState(false);
  const [imagePreview, setImagePreview] = useState(null);
  const [historyList, setHistoryList] = useState(null);
  const [historyLoading, setHistoryLoading] = useState(false);
  // Meal Planner form state
  const [mealProfile, setMealProfile] = useState({
    age: "21",
    height_cm: "170",
    weight_kg: "65",
    activity_level: "moderate",
    goal: "maintain_weight",
    dietary_preference: "vegetarian",
    allergies: "",
    dietary_restrictions: "",
    disliked_foods: "",
    preferred_cuisine: "Indian",
    meals_per_day: "4",
  });

  const [_mealProfileId, setMealProfileId] = useState(null);
  const [mealPlan, setMealPlan] = useState(null);
  const [mealPlannerError, setMealPlannerError] = useState("");
  const [mealPlannerLoading, setMealPlannerLoading] = useState(false);



  function handleFile(file) {
    if (!file) return;

    const isHygiene = name === "Hygiene Monitor";
    const isImage = file.type.startsWith("image/");
    const isVideo = file.type.startsWith("video/");

    if (isHygiene ? !(isImage || isVideo) : !isImage) {
      setMessage(
        isHygiene
          ? "Please select a valid image or video file."
          : "Please select a valid image file."
      );
      return;
    }

    // Release the previous preview URL to avoid memory leaks.
    if (imagePreview) {
      URL.revokeObjectURL(imagePreview);
    }

    const previewUrl = URL.createObjectURL(file);

    setSelectedFile(file);
    setFileName(file.name);
    setImagePreview(previewUrl);
    setMessage("");
    setNutritionResult(null);
    setNutritionError("");
    setFreshnessResult(null);
    setFreshnessError("");
    setHygieneResult(null);
    setHygieneError("");
  }




  async function handleNutritionAnalysis() {
    if (!selectedFile) {
      setMessage("Please select a food image first.");
      return;
    }

    const weight = Number(portion);

    if (!Number.isFinite(weight) || weight <= 0 || weight > 5000) {
      setMessage("Portion weight must be between 1 and 5000 grams.");
      return;
    }

    const formData = new FormData();
    formData.append("image", selectedFile);
    formData.append("portion_weight_g", String(weight));
    formData.append("prompt_context", context);

    setLoading(true);
    setMessage("");
    setNutritionError("");
    setNutritionResult(null);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/nutrition/estimate-and-save",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        const detail = Array.isArray(data.detail)
          ? data.detail.map((item) => item.msg).join(", ")
          : data.detail;

        throw new Error(
          detail || `Request failed with status ${response.status}`
        );
      }

      // Support both nested and flat nutrition responses.

      const nutrition = data.nutrition ?? data;

      const result = {
        ...nutrition,
        health_score: data.health_score ?? nutrition.health_score ?? null,
        health_label: data.health_label ?? nutrition.health_label ?? null,
      };

      setNutritionResult(result);

      onNutritionSuccess?.({
        ...result,
        analyzedAt: new Date().toISOString(),
        imageName: selectedFile?.name ?? "Food image",
        portionWeightG: weight,
      });

    } catch (error) {
      setNutritionError(
        error.message ||
        "Could not connect to FoodVerse AI. Check that the backend is running."
      );
    } finally {
      setLoading(false);
    }
  }


  // Update a single Meal Planner field
  function updateMealProfile(field, value) {
    setMealProfile((previous) => ({
      ...previous,
      [field]: value,
    }));
  }

  // Convert comma-separated input into a clean list
  function parseFoodList(value) {
    return value
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean);
  }

  // Save profile, then generate the daily meal plan
  async function handleGenerateMealPlan() {
    setMealPlannerLoading(true);
    setMealPlannerError("");
    setMealPlan(null);

    try {
      const profilePayload = {
        age: Number(mealProfile.age),
        height_cm: Number(mealProfile.height_cm),
        weight_kg: Number(mealProfile.weight_kg),
        activity_level: mealProfile.activity_level,
        goal: mealProfile.goal,
        dietary_preference: mealProfile.dietary_preference,
        allergies: parseFoodList(mealProfile.allergies),
        dietary_restrictions: parseFoodList(
          mealProfile.dietary_restrictions
        ),
        disliked_foods: parseFoodList(mealProfile.disliked_foods),
        preferred_cuisine: mealProfile.preferred_cuisine.trim() || "Any",
        meals_per_day: Number(mealProfile.meals_per_day),
      };

      if (
        !Number.isFinite(profilePayload.age) ||
        !Number.isFinite(profilePayload.height_cm) ||
        !Number.isFinite(profilePayload.weight_kg) ||
        profilePayload.age < 18 ||
        profilePayload.age > 100 ||
        profilePayload.height_cm <= 0 ||
        profilePayload.height_cm > 250 ||
        profilePayload.weight_kg <= 0 ||
        profilePayload.weight_kg > 500
      ) {
        throw new Error(
          "Enter valid age (18–100), height (up to 250 cm), and weight (up to 500 kg)."
        );
      }

      // Step 1: Save the profile to FastAPI
      const profileResponse = await fetch(
        "http://127.0.0.1:8000/meal-planner/profile",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(profilePayload),
        }
      );

      const profileData = await profileResponse.json();

      if (!profileResponse.ok) {
        const detail = Array.isArray(profileData.detail)
          ? profileData.detail.map((item) => item.msg).join(", ")
          : profileData.detail;

        throw new Error(detail || "Could not save the meal profile.");
      }

      const profileId = profileData.profile_id;
      setMealProfileId(profileId);

      // Step 2: Generate the daily plan using the saved profile ID
      const planResponse = await fetch(
        `http://127.0.0.1:8000/meal-planner/daily/${profileId}`,
        { method: "POST" }
      );

      const planData = await planResponse.json();

      if (!planResponse.ok) {
        const detail = Array.isArray(planData.detail)
          ? planData.detail.map((item) => item.msg).join(", ")
          : planData.detail;

        throw new Error(detail || "Could not generate the meal plan.");
      }

      setMealPlan(planData);
    } catch (error) {
      setMealPlannerError(
        error.message ||
        "Unable to connect to FoodVerse AI. Check that the backend is running."
      );
    } finally {
      setMealPlannerLoading(false);
    }
  }



  async function handleFreshnessAssessment() {
    if (!selectedFile) {
      setFreshnessError("Please select a food image first.");
      return;
    }

    setLoading(true);
    setMessage("");
    setFreshnessError("");
    setFreshnessResult(null);

    try {
      const formData = new FormData();

      // The FastAPI freshness endpoint expects the field name "file".
      formData.append("file", selectedFile);

      const response = await fetch(
        "http://127.0.0.1:8000/freshness/assess",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok || data.success === false) {
        throw new Error(
          data.detail ||
          data.message ||
          "Freshness assessment failed. Please try again."
        );
      }

      setFreshnessResult(data);
    } catch (error) {
      setFreshnessError(
        error.message ||
        "Could not connect to the FoodVerse AI backend."
      );
    } finally {
      setLoading(false);
    }
  }


  async function handleHygieneAnalysis() {
    if (!selectedFile) {
      setHygieneError("Please select a kitchen image or video first.");
      return;
    }

    const isVideo = selectedFile.type.startsWith("video/");
    const endpoint = isVideo
      ? "http://127.0.0.1:8000/hygiene/analyze-video"
      : "http://127.0.0.1:8000/hygiene/analyze-image";

    const formData = new FormData();
    formData.append("file", selectedFile);

    setLoading(true);
    setMessage("");
    setHygieneError("");
    setHygieneResult(null);

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok || data.success === false) {
        const detail = Array.isArray(data.detail)
          ? data.detail.map((item) => item.msg).join(", ")
          : data.detail;

        throw new Error(
          detail || data.message || `Request failed (${response.status})`
        );
      }

      setHygieneResult(data);
    } catch (error) {
      setHygieneError(
        error.message ||
        "Could not connect to FoodVerse AI. Check that the backend is running."
      );
    } finally {
      setLoading(false);
    }
  }


  const handleRecipeGeneration = async () => {
    if (!textInput.trim()) {
      setRecipeError("Please enter a dish or list of ingredients first.");
      setRecipeResult(null);
      return;
    }

    setRecipeLoading(true);
    setRecipeError("");
    setRecipeResult(null);

    try {
      const formData = new FormData();

      formData.append("text_input", textInput.trim());
      formData.append("servings", servings);
      formData.append("skill_level", skill);
      formData.append("dietary_preference", "Vegetarian");
      formData.append("cuisine", cuisine);
      formData.append("available_time_minutes", "30");

      const response = await fetch(
        "http://127.0.0.1:8000/kitchen/generate-recipe",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "Recipe generation failed."
        );
      }

      setRecipeResult(data);
    } catch (error) {
      setRecipeError(
        error.message || "Unable to connect to the FoodVerse AI backend."
      );
    } finally {
      setRecipeLoading(false);
    }
  };

  useEffect(() => {
    if (name === "Analysis History") {
      handleFetchHistory();
    }
  }, [name]);

  const handleFetchHistory = async () => {
    setHistoryLoading(true);
    setMessage("");
    try {
      const response = await fetch("http://127.0.0.1:8000/database/analyses?limit=20");
      if (!response.ok) {
        throw new Error(`History request failed with status ${response.status}`);
      }
      const data = await response.json();
      const records = Array.isArray(data) ? data : data.analyses || [];
      setHistoryList(records);
      if (records.length === 0) {
        setMessage("Database connected. No meal records saved yet.");
      }
    } catch (err) {
      setMessage("Could not load history: " + (err.message || "Network error"));
    } finally {
      setHistoryLoading(false);
    }
  };




  return (
    <div className="page-content module-page">
      <div className="module-intro">
        <div className="module-icon"><Icon size={26} /></div>
        <div><div className="eyebrow">{info.eyebrow}</div><h1>{info.title}</h1><p>{info.subtitle}</p></div>
      </div>

      {name === "Meal Planner" ? (
        <div className="module-two-column">
          <article className="panel form-panel">
            <div className="panel-heading"><div><h3>Your profile</h3><p>Preferences for your meal plan</p></div><Users size={19} /></div>
            <div className="form-grid">

              <label>
                Age (18+)
                <input
                  type="number"
                  min="18"
                  max="100"
                  value={mealProfile.age}
                  onChange={(e) => updateMealProfile("age", e.target.value)}
                  placeholder="e.g. 22"
                />
              </label>

              <label>
                Height (cm)
                <input
                  type="number"
                  min="1"
                  max="250"
                  value={mealProfile.height_cm}
                  onChange={(e) => updateMealProfile("height_cm", e.target.value)}
                  placeholder="e.g. 170"
                />
              </label>

              <label>
                Weight (kg)
                <input
                  type="number"
                  min="1"
                  max="500"
                  value={mealProfile.weight_kg}
                  onChange={(e) => updateMealProfile("weight_kg", e.target.value)}
                  placeholder="e.g. 65"
                />
              </label>

              <label>
                Activity level
                <select
                  value={mealProfile.activity_level}
                  onChange={(e) => updateMealProfile("activity_level", e.target.value)}
                >
                  <option value="sedentary">Sedentary</option>
                  <option value="light">Light</option>
                  <option value="moderate">Moderate</option>
                  <option value="active">Active</option>
                  <option value="very_active">Very active</option>
                </select>
              </label>

              <label>
                Goal
                <select
                  value={mealProfile.goal}
                  onChange={(e) => updateMealProfile("goal", e.target.value)}
                >
                  <option value="lose_weight">Lose weight</option>
                  <option value="maintain_weight">Maintain weight</option>
                  <option value="gain_weight">Gain weight</option>
                </select>
              </label>

              <label>
                Diet preference
                <select
                  value={mealProfile.dietary_preference}
                  onChange={(e) => updateMealProfile("dietary_preference", e.target.value)}
                >
                  <option value="vegetarian">Vegetarian</option>
                  <option value="vegan">Vegan</option>
                  <option value="non_vegetarian">Non-vegetarian</option>
                  <option value="eggetarian">Eggetarian</option>
                </select>
              </label>

              <label className="full-field">
                Allergies
                <input
                  value={mealProfile.allergies}
                  onChange={(e) => updateMealProfile("allergies", e.target.value)}
                  placeholder="e.g. peanuts, dairy"
                />
              </label>

              <label className="full-field">
                Dietary restrictions
                <input
                  value={mealProfile.dietary_restrictions}
                  onChange={(e) => updateMealProfile("dietary_restrictions", e.target.value)}
                  placeholder="e.g. low sodium"
                />
              </label>

              <label className="full-field">
                Disliked foods
                <input
                  value={mealProfile.disliked_foods}
                  onChange={(e) => updateMealProfile("disliked_foods", e.target.value)}
                  placeholder="e.g. mushrooms, olives"
                />
              </label>

              <label>
                Preferred cuisine
                <input
                  value={mealProfile.preferred_cuisine}
                  onChange={(e) => updateMealProfile("preferred_cuisine", e.target.value)}
                  placeholder="e.g. Indian"
                />
              </label>

              <label>
                Meals per day
                <select
                  value={mealProfile.meals_per_day}
                  onChange={(e) => updateMealProfile("meals_per_day", e.target.value)}
                >
                  {[1, 2, 3, 4, 5, 6, 7, 8].map((count) => (
                    <option key={count} value={String(count)}>
                      {count}
                    </option>
                  ))}
                </select>
              </label>

            </div>

            <button
              className="primary-button"
              onClick={handleGenerateMealPlan}
              disabled={mealPlannerLoading}
            >
              <Sparkles size={16} />
              {mealPlannerLoading
                ? "Generating meal plan..."
                : "Generate Meal Plan"}
            </button>

            {mealPlannerError && (
              <div className="inline-message">
                {mealPlannerError}
              </div>
            )}
          </article>

          <article className={`panel empty-state-panel ${mealPlan ? "has-results" : ""}`}>
            {mealPlan ? (
              <div className="meal-plan-results">
                <div className="panel-heading">
                  <div>
                    <h3>Your Daily Meal Plan</h3>
                    <p>Personalized meals and estimated nutrition</p>
                  </div>
                  <CalendarDays size={19} />
                </div>

                <div className="nutrition-summary">
                  <h3>Daily Nutrition</h3>
                  <p>
                    Target:{" "}
                    {mealPlan.targets?.estimated_daily_calories_kcal ?? "—"} kcal
                  </p>

                  <div className="form-grid">
                    <div>
                      <strong>
                        {mealPlan.nutrition_summary?.calories_kcal ?? "—"}
                      </strong>
                      <p>Calories (kcal)</p>
                    </div>
                    <div>
                      <strong>
                        {mealPlan.nutrition_summary?.protein_g ?? "—"} g
                      </strong>
                      <p>Protein</p>
                    </div>
                    <div>
                      <strong>
                        {mealPlan.nutrition_summary?.carbs_g ?? "—"} g
                      </strong>
                      <p>Carbohydrates</p>
                    </div>
                    <div>
                      <strong>
                        {mealPlan.nutrition_summary?.fat_g ?? "—"} g
                      </strong>
                      <p>Fat</p>
                    </div>
                  </div>
                </div>

                <h3>Today's Meals</h3>


                {mealPlan.meals?.map((meal, index) => (
                  <div className="meal-card" key={`${meal.meal_type}-${index}`}>
                    <h4>{meal.meal_type || `Meal ${index + 1}`}</h4>
                    <h3>{meal.name}</h3>

                    {meal.ingredients?.length > 0 && (
                      <p>
                        <strong>Ingredients:</strong>{" "}
                        {meal.ingredients
                          .map((ingredient) =>
                            typeof ingredient === "string"
                              ? ingredient
                              : ingredient.name
                          )
                          .join(", ")}
                      </p>
                    )}

                    <p>
                      <strong>Calories:</strong> {meal.calories ?? "—"} kcal
                    </p>
                    <p>
                      <strong>Protein:</strong> {meal.protein ?? "—"} g
                    </p>
                    <p>
                      <strong>Carbs:</strong> {meal.carbs ?? "—"} g
                    </p>
                    <p>
                      <strong>Fat:</strong> {meal.fat ?? "—"} g
                    </p>

                    {meal.allergens?.length > 0 && (
                      <p>
                        <strong>Potential allergens:</strong>{" "}
                        {meal.allergens.join(", ")}
                      </p>
                    )}
                  </div>
                ))}


                {mealPlan.notes?.length > 0 && (
                  <div className="inline-message">
                    <strong>Notes</strong>
                    <ul>
                      {mealPlan.notes.map((note, index) => (
                        <li key={index}>{note}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ) : (
              <>
                <div className="empty-art">
                  <CalendarDays size={34} />
                </div>
                <h3>Your daily plan will appear here</h3>
                <p>
                  Fill in your profile and click Generate Meal Plan
                  to view your meals and estimated nutrition.
                </p>
                <div className="empty-placeholder">
                  <div />
                  <div />
                  <div />
                </div>
              </>
            )}
          </article>

        </div>
      ) : name === "Smart Kitchen" ? (
        <article className="panel form-panel recipe-form">
          <div className="panel-heading"><div><h3>Recipe generator</h3><p>Describe a dish or the ingredients you have available.</p></div><ChefHat size={20} /></div>
          <label>Dish or ingredients<textarea rows="4" value={textInput} onChange={e => setTextInput(e.target.value)} placeholder="e.g. I have rice, tomatoes, chickpeas and spinach. What can I cook?" /></label>
          <div className="form-grid">
            <label>Servings<select value={servings} onChange={e => setServings(e.target.value)}>{[1, 2, 3, 4, 5, 6, 8, 10, 12].map(n => <option key={n}>{n}</option>)}</select></label>
            <label>Skill level<select value={skill} onChange={e => setSkill(e.target.value)}><option>Beginner</option><option>Intermediate</option><option>Advanced</option></select></label>
            <label>Cuisine<select value={cuisine} onChange={e => setCuisine(e.target.value)}><option>Any</option><option>Indian</option><option>Italian</option><option>Chinese</option><option>Mediterranean</option></select></label>
            <label>Ingredient image<input type="file" accept="image/*" onChange={e => handleFile(e.target.files?.[0])} />
            </label>

          </div>
          {fileName && <div className="file-chip"><CheckCircle2 size={16} /> {fileName}</div>}

          <button
            className="primary-button"
            onClick={handleRecipeGeneration}
            disabled={recipeLoading}
          >
            <Sparkles size={16} />
            {recipeLoading ? "Generating recipe..." : "Generate recipe"}
          </button>


          {recipeError && (
            <div className="inline-message">
              {recipeError}
            </div>
          )}

          {recipeResult && (
            <section className="recipe-results">
              <h2>{recipeResult.dish_name}</h2>
              <p>{recipeResult.description}</p>

              <p>
                <strong>Servings:</strong> {recipeResult.servings} {" | "}
                <strong>Preparation:</strong>{" "}
                {recipeResult.preparation_time_minutes} min {" | "}
                <strong>Cooking:</strong>{" "}
                {recipeResult.cooking_time_minutes} min {" | "}
                <strong>Difficulty:</strong> {recipeResult.difficulty}
              </p>

              <h3>Ingredients</h3>
              <ul>
                {recipeResult.ingredients.map((item, index) => (
                  <li key={index}>
                    <strong>{item.name}</strong> — {item.quantity}
                  </li>
                ))}
              </ul>

              <h3>Cooking steps</h3>
              <ol>
                {recipeResult.steps.map((step, index) => (
                  <li key={index}>
                    {step.instruction}
                    {step.duration_minutes != null &&
                      ` (${step.duration_minutes} min)`}
                  </li>
                ))}
              </ol>

              <h3>Cooking tips</h3>
              <ul>
                {recipeResult.cooking_tips.map((tip, index) => (
                  <li key={index}>{tip}</li>
                ))}
              </ul>

              <h3>Safety notes</h3>
              <ul>
                {recipeResult.safety_notes.map((note, index) => (
                  <li key={index}>{note}</li>
                ))}
              </ul>

              {recipeResult.limitations?.length > 0 && (
                <>
                  <h3>Limitations</h3>
                  <ul>
                    {recipeResult.limitations.map((item, index) => (
                      <li key={index}>{item}</li>
                    ))}
                  </ul>
                </>
              )}
            </section>
          )}

        </article>
      ) : name === "Analysis History" ? (
        <article className="panel" style={{ padding: "28px" }}>
          <div className="panel-heading">
            <div>
              <h3>Saved Analysis Records</h3>
              <p>Records retrieved from your FoodVerse database</p>
            </div>
            <button
              className="secondary-button"
              onClick={handleFetchHistory}
              disabled={historyLoading}
            >
              <RefreshCw size={15} />
              {historyLoading ? "Loading records..." : "Refresh records"}
            </button>
          </div>

          {message && <div className="inline-message" style={{ marginBottom: "16px" }}>{message}</div>}

          {historyList && historyList.length > 0 ? (
            <div style={{ display: "flex", flexDirection: "column", gap: "12px", marginTop: "16px" }}>
              {historyList.map((item, idx) => (
                <div
                  key={item.id || idx}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: "14px 18px",
                    background: "var(--color-card-subtle)",
                    border: "1px solid var(--color-border)",
                    borderRadius: "var(--radius-md)",
                  }}
                >
                  <div>
                    <strong style={{ fontSize: "0.9375rem", color: "var(--color-text-main)" }}>
                      {item.dish_name || item.food_name || "Analyzed Meal"}
                    </strong>
                    <div style={{ fontSize: "0.8125rem", color: "var(--color-text-secondary)", marginTop: "4px" }}>
                      {item.portion_weight_g ? `${item.portion_weight_g}g · ` : ""}{item.calories_kcal ?? item.calories ?? "—"} kcal | Protein: {item.protein_g ?? "—"}g | Carbs: {item.carbs_g ?? "—"}g | Fat: {item.fat_g ?? "—"}g
                    </div>
                  </div>
                  <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                    <span className="tag tag-green">Score {item.health_score ?? "—"}/100</span>
                    {item.health_label && <span className="tag tag-blue">{item.health_label}</span>}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state-panel history-empty" style={{ minHeight: "240px", border: "none", padding: "16px" }}>
              <div className="empty-art"><History size={34} /></div>
              <h3>Your analysis history</h3>
              <p>Click "Refresh records" to retrieve saved records from your database.</p>
            </div>
          )}
        </article>
      ) : (
        <div className="module-two-column">
          <article className="panel upload-panel">
            <div className="panel-heading"><div><h3>{name === "Hygiene Monitor" ? "Kitchen media" : "Upload an image"}</h3><p>Choose a file from your device to prepare an analysis.</p></div><Upload size={20} /></div>

            <label className={`drop-zone ${imagePreview ? "has-preview" : ""}`}>
              <input
                type="file"
                accept={name === "Hygiene Monitor" ? "image/*,video/*" : "image/*"}
                onChange={(e) => handleFile(e.target.files?.[0])}
              />



              {imagePreview ? (
                selectedFile?.type.startsWith("video/") ? (
                  <video
                    src={imagePreview}
                    controls
                    className="drop-zone-preview"
                    style={{
                      display: "block",
                      width: "100%",
                      maxWidth: "380px",
                      height: "240px",
                      objectFit: "contain",
                      margin: "0 auto",
                    }}
                  />
                ) : (
                  <img
                    src={imagePreview}
                    alt="Selected food or kitchen image"
                    className="drop-zone-preview"
                    style={{
                      display: "block",
                      width: "100%",
                      maxWidth: "380px",
                      height: "240px",
                      objectFit: "contain",
                      margin: "0 auto",
                    }}
                  />
                )
              ) : (
                <>
                  <div className="upload-icon">
                    <ImagePlus size={27} />
                  </div>

                  <strong>{fileName || "Click to browse or drop a file"}</strong>

                  <span>
                    {name === "Hygiene Monitor"
                      ? "Supported image or video file"
                      : "Choose a clear image with the food visible"}
                  </span>
                </>
              )}


            </label>

            {name === "Food Recognition" && <div className="form-grid compact-form"><label>Portion weight (g)<input type="number" min="1" max="5000" value={portion} onChange={e => setPortion(e.target.value)} /></label><label>Additional context<input value={context} onChange={e => setContext(e.target.value)} placeholder="Optional details" /></label></div>}
            {name === "Freshness Detector" && <div className="form-grid compact-form"><label>Storage context<select><option>Room temperature</option><option>Refrigerated</option><option>Frozen</option><option>Unknown</option></select></label><label>Stored for<input placeholder="e.g. 2 days" /></label></div>}

            <button
              className="primary-button"
              onClick={
                name === "Food Recognition"
                  ? handleNutritionAnalysis
                  : name === "Freshness Detector"
                    ? handleFreshnessAssessment
                    : name === "Hygiene Monitor"
                      ? handleHygieneAnalysis
                      : () =>
                        setMessage(
                          selectedFile
                            ? "File selected. API integration is coming next."
                            : "Please select a file first."
                        )
              }
              disabled={loading}
            >
              <Sparkles size={16} />
              {loading
                ? "Analyzing food..."
                : name === "Food Recognition"
                  ? "Analyze food & nutrition"
                  : name === "Freshness Detector"
                    ? "Assess freshness"
                    : name === "Hygiene Monitor"
                      ? "Analyze hygiene"
                      : info.action}
            </button>

            {message && <div className="inline-message">{message}</div>}
          </article>

          <article className={`panel results-placeholder ${freshnessResult || hygieneResult || nutritionResult ? "has-results" : ""}`}>



            {name === "Freshness Detector" && freshnessResult ? (
              <>
                {(() => {
                  const result = freshnessResult.assessment ?? {};
                  const list = (value) =>
                    Array.isArray(value) ? value : value ? [value] : [];

                  return (
                    <>
                      <div className="result-heading">
                        <span className="eyebrow">FRESHNESS ASSESSMENT</span>
                        <h2>{result.apparent_freshness ?? "Assessment complete"}</h2>
                        <p>
                          Food identified: {result.food_name ?? "Not identified"}
                        </p>
                      </div>

                      <div className="nutrition-grid">
                        <div>
                          <strong>
                            {result.confidence_score ?? "—"}
                            {result.confidence_score != null ? "%" : ""}
                          </strong>
                          <span>Visual confidence</span>
                        </div>
                      </div>

                      {result.confidence_explanation && (
                        <p>{result.confidence_explanation}</p>
                      )}

                      <h3>Visible evidence</h3>
                      <ul>
                        {list(result.visible_evidence).map((item, index) => (
                          <li key={index}>
                            {typeof item === "string" ? item : JSON.stringify(item)}
                          </li>
                        ))}
                      </ul>

                      {list(result.concerns).length > 0 && (
                        <>
                          <h3>Potential concerns</h3>
                          <ul>
                            {list(result.concerns).map((item, index) => (
                              <li key={index}>
                                {typeof item === "string" ? item : JSON.stringify(item)}
                              </li>
                            ))}
                          </ul>
                        </>
                      )}

                      <h3>Recommendations</h3>
                      <ul>
                        {list(result.recommendations).map((item, index) => (
                          <li key={index}>
                            {typeof item === "string" ? item : JSON.stringify(item)}
                          </li>
                        ))}
                      </ul>

                      {freshnessResult.safety_guidance && (
                        <>
                          <h3>Food-safety guidance</h3>
                          <p>
                            {freshnessResult.safety_guidance.message ??
                              freshnessResult.safety_guidance.action ??
                              "Follow safe food storage and handling practices."}
                          </p>
                        </>
                      )}

                      {freshnessResult.safety_notice && (
                        <p>{freshnessResult.safety_notice}</p>
                      )}

                      <div className="disclaimer">
                        <ShieldCheck size={17} />
                        <span>
                          This is a visual AI estimate, not proof that food is safe to eat.
                          Harmful microorganisms may be present even when food looks fresh.
                        </span>
                      </div>
                    </>
                  );
                })()}
              </>
            ) : name === "Hygiene Monitor" && hygieneResult ? (
              <>
                {(() => {
                  const result = hygieneResult;
                  const indicators = result.indicators ?? {};
                  const violations = Array.isArray(result.violations)
                    ? result.violations
                    : [];

                  return (
                    <>
                      <div className="result-heading">
                        <span className="eyebrow">HYGIENE ASSESSMENT</span>
                        <h2>
                          {result.overall_score != null
                            ? `${result.overall_score}/100`
                            : "Assessment complete"}
                        </h2>
                        <p>
                          {result.analysis_type === "video"
                            ? `Video analyzed: ${result.frames_analyzed ?? 0} frames`
                            : "Image hygiene analysis"}
                        </p>
                      </div>

                      <h3>Hygiene indicators</h3>
                      {Object.keys(indicators).length > 0 ? (
                        <ul>
                          {(Array.isArray(indicators)
                            ? indicators.map((item, index) => [index, item])
                            : Object.entries(indicators)
                          ).map(([key, value]) => (
                            <li key={key}>
                              <strong>
                                {typeof value === "object" && value !== null && value.name
                                  ? value.name
                                  : String(key).replaceAll("_", " ")}
                                :
                              </strong>{" "}
                              {typeof value === "object" && value !== null
                                ? `${value.status ?? "Unknown"} — ${value.evidence ?? ""}`
                                : String(value)}
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p>No hygiene indicators were returned.</p>
                      )}

                      <h3>Detected violations</h3>
                      {violations.length > 0 ? (
                        <ul>
                          {violations.map((item, index) => (
                            <li key={index}>
                              {typeof item === "string"
                                ? item
                                : JSON.stringify(item)}
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p>No violations were reported by the AI analysis.</p>
                      )}

                      {result.ai_summary && (
                        <>
                          <h3>AI Summary</h3>
                          <p>{result.ai_summary}</p>
                        </>
                      )}

                      {Array.isArray(result.frame_results) &&
                        result.frame_results.length > 0 && (
                          <>
                            <h3>Video frame results</h3>
                            {result.frame_results.map((frame, index) => (
                              <div key={index}>
                                <strong>
                                  Frame at {frame.timestamp_seconds ?? 0} seconds
                                </strong>
                                <p>
                                  Score: {frame.overall_score ?? "Not available"}/100
                                </p>
                                <p>{frame.ai_summary ?? "No summary available."}</p>
                              </div>
                            ))}
                          </>
                        )}

                      {result.limitations && (
                        <p>
                          <strong>Limitations:</strong>{" "}
                          {Array.isArray(result.limitations)
                            ? result.limitations.join(" ")
                            : typeof result.limitations === "string"
                              ? result.limitations
                              : JSON.stringify(result.limitations)}
                        </p>
                      )}

                      {result.notice && (
                        <div className="disclaimer">
                          <ShieldCheck size={17} />
                          <span>{result.notice}</span>
                        </div>
                      )}
                    </>
                  );
                })()}
              </>
            ) : name === "Food Recognition" && nutritionResult ? (
              <>
                <div className="empty-art">
                  <Salad size={34} />
                </div>

                <h3>
                  {nutritionResult.dish_name ||
                    nutritionResult.food_name ||
                    "Nutrition estimate"}
                </h3>

                <p>Estimated nutrition for your selected food and portion.</p>

                <div className="macro-grid">
                  <div>
                    <strong>
                      {nutritionResult.calories_kcal ??
                        nutritionResult.calories ??
                        "—"}
                    </strong>
                    <span>Calories (kcal)</span>
                  </div>
                  <div>
                    <strong>
                      {nutritionResult.protein_g ??
                        nutritionResult.protein ??
                        "—"} g
                    </strong>
                    <span>Protein</span>
                  </div>
                  <div>
                    <strong>
                      {nutritionResult.carbs_g ??
                        nutritionResult.carbs ??
                        "—"} g
                    </strong>
                    <span>Carbohydrates</span>
                  </div>
                  <div>
                    <strong>
                      {nutritionResult.fats_g ??
                        nutritionResult.fats ??
                        "—"} g
                    </strong>
                    <span>Fat</span>
                  </div>
                </div>

                <p>
                  <strong>Fiber:</strong>{" "}
                  {nutritionResult.fiber_g ?? nutritionResult.fiber ?? "—"} g
                </p>

                <p>
                  <strong>Health score:</strong>{" "}
                  {nutritionResult.health_score ?? "Not provided"}
                  {nutritionResult.health_label
                    ? ` (${nutritionResult.health_label})`
                    : ""}
                </p>

                {nutritionResult.reasoning && (
                  <p>{nutritionResult.reasoning}</p>
                )}

                {nutritionResult.estimation_notes && (
                  <p>{String(nutritionResult.estimation_notes)}</p>
                )}

                {nutritionResult.alternatives && (
                  <p>
                    <strong>Suggestions:</strong>{" "}
                    {Array.isArray(nutritionResult.alternatives)
                      ? nutritionResult.alternatives.join(", ")
                      : String(nutritionResult.alternatives)}
                  </p>
                )}

                <div className="disclaimer">
                  <ShieldCheck size={17} />
                  <span>
                    Nutrition values are AI estimates, not laboratory measurements.
                    Do not use image-based estimates alone to make food-safety decisions.
                  </span>
                </div>
              </>
            ) : (
              <>
                <div className="empty-art">
                  <Icon size={34} />
                </div>

                <h3>
                  {loading
                    ? "Analyzing your food..."
                    : nutritionError
                      ? "Analysis failed"
                      : "Results will appear here"}
                </h3>

                <p>
                  {name === "Hygiene Monitor"
                    ? hygieneError ||
                    (loading
                      ? "Please wait while FoodVerse AI analyzes hygiene."
                      : "Upload a food-handling image or video and run the analysis.")
                    : name === "Freshness Detector"
                      ? freshnessError ||
                      (loading
                        ? "Please wait while FoodVerse AI assesses freshness."
                        : "Upload a food image to assess its apparent freshness.")
                      : nutritionError ||
                      (loading
                        ? "Please wait while FoodVerse AI processes your image."
                        : "Upload a clear food image and run the analysis to see your results.")}
                </p>

                {!loading &&
                  (name === "Hygiene Monitor"
                    ? !hygieneError
                    : name === "Freshness Detector"
                      ? !freshnessError
                      : !nutritionError) && (
                    <div className="placeholder-lines">
                      <span />
                      <span />
                    </div>
                  )}

                <div className="disclaimer">
                  <ShieldCheck size={17} />
                  <span>{info.note}</span>
                </div>
              </>
            )}
          </article>

        </div>
      )}
      <footer className="app-footer"><Leaf size={15} /> FoodVerse AI <span>•</span> AI-assisted food insights <span>•</span> Estimates are not professional advice</footer>
    </div>
  );
}






export default function App() {
  const [active, setActive] = useState("Overview");
  const [mobileOpen, setMobileOpen] = useState(false);
  const [latestNutrition, setLatestNutrition] = useState(null);
  const [apiStatus, setApiStatus] = useState("checking");

  useEffect(() => {
    let ignore = false;
    fetch("http://127.0.0.1:8000/health")
      .then((res) => {
        if (!ignore) setApiStatus(res.ok ? "connected" : "error");
      })
      .catch(() => {
        if (!ignore) setApiStatus("error");
      });
    return () => {
      ignore = true;
    };
  }, []);

  // Light and dark theme state
  const [theme, setTheme] = useState(
    () => localStorage.getItem("foodverse-theme") || "light"
  );

  function toggleTheme() {
    const nextTheme = theme === "light" ? "dark" : "light";
    setTheme(nextTheme);
    localStorage.setItem("foodverse-theme", nextTheme);
  }

  return (
    <div className={`app-shell theme-${theme}`}>
      <Sidebar active={active} onNavigate={setActive} open={mobileOpen} onClose={() => setMobileOpen(false)} />
      <main className="main-area">
        <Topbar
          active={active}
          onMenu={() => setMobileOpen(true)}
          theme={theme}
          onToggleTheme={toggleTheme}
          apiStatus={apiStatus}
        />
        {active === "Overview" ? (
          <Dashboard
            onNavigate={setActive}
            latestNutrition={latestNutrition}
          />
        ) : (
          <ModulePage
            key={active}
            name={active}
            onNutritionSuccess={setLatestNutrition}
          />
        )}
      </main>
    </div>
  );
}