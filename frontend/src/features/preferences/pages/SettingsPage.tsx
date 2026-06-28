import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Settings, Languages, Palette, Bell, 
  Sparkles, Compass, RefreshCw, Loader2, 
  ShieldAlert, CheckCircle2, ArrowLeft 
} from "lucide-react";
import { Link } from "react-router-dom";
import usePreferences from "../hooks/usePreferences";
import type { NotificationPreferences } from "../types";

export const SettingsPage = () => {
  const { preferences, loading, partialUpdatePreferences, resetPreferences } = usePreferences();

  // Operation indicators
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [savingField, setSavingField] = useState<string | null>(null);
  
  // Confirmation Modal State
  const [showConfirmReset, setShowConfirmReset] = useState(false);

  if (loading) {
    return (
      <div className="h-[calc(100vh-4rem)] w-full flex flex-col items-center justify-center bg-background text-primary min-h-[500px]">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
        <p className="mt-4 text-xs font-bold uppercase tracking-wider text-on-surface-variant">Loading settings...</p>
      </div>
    );
  }

  if (!preferences) {
    return (
      <div className="p-8 text-center text-on-surface bg-background min-h-[500px]">
        <p className="text-red-400 text-sm font-semibold">Failed to load preference settings.</p>
        <Link to="/" className="text-primary hover:underline mt-4 inline-block text-xs font-bold uppercase tracking-wider">Return to Dashboard</Link>
      </div>
    );
  }

  const notifySuccess = (message: string) => {
    setSuccessMsg(message);
    setTimeout(() => setSuccessMsg(null), 3000);
  };

  const handleLanguageChange = async (lang: "English" | "Hindi") => {
    setSavingField("language");
    setErrorMsg(null);
    try {
      await partialUpdatePreferences({ preferred_language: lang });
      notifySuccess(`Preferred language changed to ${lang}!`);
    } catch (e: any) {
      setErrorMsg(e.response?.data?.detail || "Failed to update language settings.");
    } finally {
      setSavingField(null);
    }
  };

  const handleThemeChange = async (themeVal: "Light" | "Dark" | "System") => {
    setSavingField("theme");
    setErrorMsg(null);
    try {
      await partialUpdatePreferences({ theme: themeVal });
      notifySuccess(`Appearance theme updated to ${themeVal}!`);
    } catch (e: any) {
      setErrorMsg(e.response?.data?.detail || "Failed to update appearance theme.");
    } finally {
      setSavingField(null);
    }
  };

  const handleNotificationToggle = async (key: keyof NotificationPreferences) => {
    setSavingField(`notif-${key}`);
    setErrorMsg(null);
    try {
      const currentVal = preferences.notifications[key];
      await partialUpdatePreferences({
        notifications: {
          [key]: !currentVal,
        },
      });
      notifySuccess("Notification preferences synchronized successfully.");
    } catch (e: any) {
      setErrorMsg(e.response?.data?.detail || "Failed to update notification toggles.");
    } finally {
      setSavingField(null);
    }
  };

  const handleAiStyleChange = async (style: "Brief" | "Detailed") => {
    setSavingField("ai_response");
    setErrorMsg(null);
    try {
      await partialUpdatePreferences({ ai_response_style: style });
      notifySuccess(`AI response style changed to ${style}!`);
    } catch (e: any) {
      setErrorMsg(e.response?.data?.detail || "Failed to update AI prompt styles.");
    } finally {
      setSavingField(null);
    }
  };

  const handleHomeRedirectChange = async (homePage: "Dashboard" | "Chat" | "Notices" | "Calendar" | "Profile") => {
    setSavingField("home_page");
    setErrorMsg(null);
    try {
      await partialUpdatePreferences({ default_home_page: homePage });
      notifySuccess(`Preferred home page landing updated to ${homePage}!`);
    } catch (e: any) {
      setErrorMsg(e.response?.data?.detail || "Failed to update landing page preferences.");
    } finally {
      setSavingField(null);
    }
  };

  const handleConfirmReset = async () => {
    setSavingField("reset");
    setErrorMsg(null);
    try {
      await resetPreferences();
      setShowConfirmReset(false);
      notifySuccess("All preference settings reverted back to default system values!");
    } catch (e: any) {
      setErrorMsg(e.response?.data?.detail || "Failed to reset settings.");
    } finally {
      setSavingField(null);
    }
  };

  return (
    <div className="max-w-[1000px] mx-auto px-6 py-8 space-y-8 text-on-surface font-sans select-text">
      
      {/* Settings Page Header Area */}
      <header className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-outline-variant/30 pb-6">
        <div>
          <h1 className="text-xl font-extrabold text-primary flex items-center gap-2">
            <Settings className="w-5 h-5 text-primary shrink-0" />
            <span>Portal Preferences</span>
          </h1>
          <p className="text-on-surface-variant mt-1.5 text-xs md:text-sm">
            Customize notification channels, themes, landing paths, and AI response parameters.
          </p>
        </div>

        {/* System Reset Button */}
        <button
          onClick={() => setShowConfirmReset(true)}
          className="px-4 py-2 border border-outline-variant hover:border-red-500/40 hover:bg-red-500/10 text-on-surface-variant hover:text-red-400 rounded-xl text-[10px] font-bold uppercase tracking-wider transition-colors flex items-center gap-1.5 cursor-pointer shrink-0"
        >
          <RefreshCw size={12} className={savingField === "reset" ? "animate-spin" : ""} />
          <span>Reset to Defaults</span>
        </button>
      </header>

      {/* Operation Toast Alerts */}
      {errorMsg && (
        <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl flex items-start gap-3 text-red-400 text-xs">
          <ShieldAlert className="w-4 h-4 shrink-0 mt-0.5" />
          <span>{errorMsg}</span>
          <button className="ml-auto hover:text-white" onClick={() => setErrorMsg(null)}>&times;</button>
        </div>
      )}

      {successMsg && (
        <div className="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl flex items-start gap-3 text-emerald-400 text-xs">
          <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5" />
          <span>{successMsg}</span>
          <button className="ml-auto hover:text-white" onClick={() => setSuccessMsg(null)}>&times;</button>
        </div>
      )}

      {/* Grid options panels */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Left Side: General preferences */}
        <div className="space-y-6">
          
          {/* THEME CONTROL CARD */}
          <div className="matte-card rounded-2xl p-6">
            <div className="flex items-center gap-2 mb-4 pb-3 border-b border-outline-variant/30">
              <Palette className="w-4 h-4 text-primary" />
              <h2 className="text-xs font-bold uppercase tracking-wider text-primary">Appearance Theme</h2>
              {savingField === "theme" && <Loader2 className="w-3.5 h-3.5 animate-spin text-primary ml-auto" />}
            </div>

            <p className="text-[11px] text-on-surface-variant mb-4">Set dark mode options for your dashboard views.</p>

            <div className="grid grid-cols-3 gap-2">
              {(["Light", "Dark", "System"] as const).map((t) => (
                <button
                  key={t}
                  onClick={() => handleThemeChange(t)}
                  className={`py-2 px-3 rounded-xl text-xs font-bold uppercase tracking-wider border transition-all cursor-pointer ${
                    preferences.theme === t
                      ? "bg-primary text-background border-primary"
                      : "border-outline-variant bg-surface-container/30 text-on-surface-variant hover:text-primary hover:border-primary"
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>

          {/* LANGUAGE CONTROL CARD */}
          <div className="matte-card rounded-2xl p-6">
            <div className="flex items-center gap-2 mb-4 pb-3 border-b border-outline-variant/30">
              <Languages className="w-4 h-4 text-primary" />
              <h2 className="text-xs font-bold uppercase tracking-wider text-primary">Preferred Language</h2>
              {savingField === "language" && <Loader2 className="w-3.5 h-3.5 animate-spin text-primary ml-auto" />}
            </div>

            <p className="text-[11px] text-on-surface-variant mb-4">Configure default language translation for platform interfaces.</p>

            <select
              value={preferences.preferred_language}
              onChange={(e) => handleLanguageChange(e.target.value as "English" | "Hindi")}
              className="w-full px-4 py-3 bg-surface-container border border-outline-variant focus:border-primary focus:outline-none rounded-xl text-on-surface transition-all text-xs font-semibold"
            >
              <option value="English">English</option>
              <option value="Hindi">Hindi (हिंदी)</option>
            </select>
          </div>

          {/* DEFAULT HOME PAGE CARD */}
          <div className="matte-card rounded-2xl p-6">
            <div className="flex items-center gap-2 mb-4 pb-3 border-b border-outline-variant/30">
              <Compass className="w-4 h-4 text-primary" />
              <h2 className="text-xs font-bold uppercase tracking-wider text-primary">Default landing view</h2>
              {savingField === "home_page" && <Loader2 className="w-3.5 h-3.5 animate-spin text-primary ml-auto" />}
            </div>

            <p className="text-[11px] text-on-surface-variant mb-4">Configure which platform page you land on immediately after logging in.</p>

            <select
              value={preferences.default_home_page}
              onChange={(e) => handleHomeRedirectChange(e.target.value as any)}
              className="w-full px-4 py-3 bg-surface-container border border-outline-variant focus:border-primary focus:outline-none rounded-xl text-on-surface transition-all text-xs font-semibold"
            >
              <option value="Dashboard">Dashboard Hub</option>
              <option value="Chat">AI Chat Assistant</option>
              <option value="Notices">Notices Directory</option>
              <option value="Calendar">Academics Hub</option>
              <option value="Profile">My Student Profile</option>
            </select>
          </div>

        </div>

        {/* Right Side: Alerts & AI Styles */}
        <div className="space-y-6">
          
          {/* NOTIFICATION PREFERENCES CARD */}
          <div className="matte-card rounded-2xl p-6">
            <div className="flex items-center gap-2 mb-4 pb-3 border-b border-outline-variant/30">
              <Bell className="w-4 h-4 text-primary" />
              <h2 className="text-xs font-bold uppercase tracking-wider text-primary">Notifications</h2>
            </div>

            <p className="text-[11px] text-on-surface-variant mb-5">Configure which email and system alert pathways are active.</p>

            <div className="space-y-4">
              {[
                { key: "email_notifications", label: "Email Notifications" },
                { key: "push_notifications", label: "Push Notifications" },
                { key: "notice_updates", label: "Notice Updates" },
                { key: "event_reminders", label: "Event Reminders" },
                { key: "academic_alerts", label: "Academic Alerts" },
              ].map(({ key, label }) => (
                <div key={key} className="flex items-center justify-between text-xs">
                  <span className="text-on-surface font-semibold">{label}</span>
                  <div className="flex items-center gap-2">
                    {savingField === `notif-${key}` && <Loader2 className="w-3.5 h-3.5 animate-spin text-primary" />}
                    <button
                      onClick={() => handleNotificationToggle(key as keyof NotificationPreferences)}
                      className={`w-10 h-5.5 rounded-full p-0.5 transition-colors cursor-pointer relative ${
                        preferences.notifications[key] ? "bg-primary" : "bg-surface-container border border-outline-variant"
                      }`}
                    >
                      <motion.div
                        layout
                        transition={{ type: "spring", stiffness: 700, damping: 30 }}
                        className={`w-4.5 h-4.5 rounded-full shadow-md ${
                          preferences.notifications[key] ? "bg-background" : "bg-on-surface-variant"
                        }`}
                        style={{
                          marginLeft: preferences.notifications[key] ? "17px" : "0px",
                        }}
                      />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* AI RESPONSE PERSONALIZATION CARD */}
          <div className="matte-card rounded-2xl p-6">
            <div className="flex items-center gap-2 mb-4 pb-3 border-b border-outline-variant/30">
              <Sparkles className="w-4 h-4 text-primary" />
              <h2 className="text-xs font-bold uppercase tracking-wider text-primary">AI Assistant Profile</h2>
              {savingField === "ai_response" && <Loader2 className="w-3.5 h-3.5 animate-spin text-primary ml-auto" />}
            </div>

            <p className="text-[11px] text-on-surface-variant mb-4">Choose default formatting lengths for Gemini LLM responses.</p>

            <div className="grid grid-cols-2 gap-2">
              {(["Brief", "Detailed"] as const).map((style) => (
                <button
                  key={style}
                  onClick={() => handleAiStyleChange(style)}
                  className={`py-2 px-3 rounded-xl text-xs font-bold uppercase tracking-wider border transition-all cursor-pointer ${
                    preferences.ai_response_style === style
                      ? "bg-primary text-background border-primary"
                      : "border-outline-variant bg-surface-container/30 text-on-surface-variant hover:text-primary hover:border-primary"
                  }`}
                >
                  {style}
                </button>
              ))}
            </div>
          </div>

        </div>
      </div>

      {/* Confirmation Modal */}
      <AnimatePresence>
        {showConfirmReset && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm select-none">
            <motion.div 
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.15 }}
              className="w-full max-w-md bg-surface-container border border-outline-variant rounded-2xl overflow-hidden shadow-2xl p-6 space-y-4"
            >
              <div className="flex items-start gap-3 p-3 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-xs">
                <ShieldAlert size={18} className="shrink-0 mt-0.5" />
                <p>Warning: This action will restore your theme, language, notifications, and AI configurations back to system default values.</p>
              </div>

              <h3 className="font-bold text-primary text-sm uppercase tracking-wider">Revert preferences to defaults?</h3>
              <p className="text-xs text-on-surface-variant">Are you sure you want to proceed? This will override your current settings configuration.</p>

              <div className="flex justify-end gap-3 pt-2">
                <button
                  onClick={() => setShowConfirmReset(false)}
                  className="px-4 py-2 border border-outline-variant hover:border-primary rounded-xl text-[10px] font-bold uppercase tracking-wider text-primary cursor-pointer transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleConfirmReset}
                  className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded-xl text-[10px] font-bold uppercase tracking-wider cursor-pointer transition-colors"
                >
                  Revert Settings
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default SettingsPage;
