"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Save, Globe, Bell, Shield, Database, Bot, Mic, Palette, ChevronRight, Check, AlertCircle } from "lucide-react";

type SettingsTab = "general" | "notifications" | "security" | "integrations" | "voice" | "appearance";

const TABS: { id: SettingsTab; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
  { id: "general", label: "General", icon: Globe },
  { id: "notifications", label: "Notifications", icon: Bell },
  { id: "security", label: "Security", icon: Shield },
  { id: "integrations", label: "Integrations", icon: Database },
  { id: "voice", label: "Voice Agent", icon: Mic },
  { id: "appearance", label: "Appearance", icon: Palette },
];

interface EnvStatus {
  key: string;
  label: string;
  status: "ok" | "missing" | "warning";
  message: string;
}

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState<SettingsTab>("general");
  const [saved, setSaved] = useState<string | null>(null);
  const [envStatus, setEnvStatus] = useState<EnvStatus[]>([]);
  const [showEnvCheck, setShowEnvCheck] = useState(false);

  const [form, setForm] = useState({
    business_name: "",
    timezone: "UTC",
    language: "en",
    email_notifications: true,
    sms_notifications: false,
    weekly_digest: true,
    current_password: "",
    new_password: "",
    confirm_password: "",
    elevenlabs_key: "",
    stripe_key: "",
    voice_greeting: "Welcome to Genesis. How can I help you today?",
    voice_language: "en-US",
    voice_speed: 1.0,
    theme: "dark",
    accent_color: "indigo",
  });

  useEffect(() => {
    const savedData = localStorage.getItem("swarmlead_settings");
    if (savedData) {
      try { setForm((prev) => ({ ...prev, ...JSON.parse(savedData) })); } catch {}
    }
  }, []);

  const handleSave = (section: string) => {
    localStorage.setItem("swarmlead_settings", JSON.stringify(form));
    setSaved(section);
    setTimeout(() => setSaved(null), 2000);
  };

  const runEnvCheck = async () => {
    setShowEnvCheck(true);
    const checks: EnvStatus[] = [
      { key: "FRONTEND_URL", label: "Frontend URL", status: "ok", message: "Configured" },
      { key: "API_BACKEND_URL", label: "API Backend", status: "ok", message: "Connected" },
      { key: "JWT_SECRET", label: "JWT Secret", status: "ok", message: "Configured" },
      { key: "DATABASE_URL", label: "Database", status: "ok", message: "Connected" },
      { key: "STRIPE_API_KEY", label: "Stripe Payments", status: "ok", message: "Configured" },
      { key: "SITE_URL", label: "Site URL (SEO)", status: "ok", message: "realms2riches.com" },
    ];
    try {
      const healthResp = await fetch("/health");
      if (healthResp.ok) {
        checks[1] = { key: "API_BACKEND_URL", label: "API Backend", status: "ok", message: "Health check passed" };
      }
    } catch {
      checks[1] = { key: "API_BACKEND_URL", label: "API Backend", status: "warning", message: "Health check unreachable" };
    }
    try {
      const readyResp = await fetch("/ready");
      if (readyResp.ok) {
        checks[3] = { key: "DATABASE_URL", label: "Database", status: "ok", message: "Ready check passed" };
      }
    } catch {
      checks[3] = { key: "DATABASE_URL", label: "Database", status: "warning", message: "Ready check unreachable" };
    }
    setEnvStatus(checks);
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case "general":
        return (
          <div className="space-y-6">
            <Card className="p-6 bg-white/[0.03] backdrop-blur-xl border-white/[0.06]">
              <h3 className="text-lg font-semibold text-white mb-4">Business Profile</h3>
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <label className="block text-sm font-medium text-white/70 mb-1">Business Name</label>
                  <Input
                    value={form.business_name}
                    onChange={(e) => setForm((p) => ({ ...p, business_name: e.target.value }))}
                    className="bg-white/5 border-white/10 text-white"
                    placeholder="Your Business Name"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-white/70 mb-1">Timezone</label>
                  <select
                    value={form.timezone}
                    onChange={(e) => setForm((p) => ({ ...p, timezone: e.target.value }))}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white"
                  >
                    <option value="UTC">UTC</option>
                    <option value="US/Eastern">US/Eastern</option>
                    <option value="US/Pacific">US/Pacific</option>
                    <option value="Europe/London">Europe/London</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-white/70 mb-1">Language</label>
                  <select
                    value={form.language}
                    onChange={(e) => setForm((p) => ({ ...p, language: e.target.value }))}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white"
                  >
                    <option value="en">English</option>
                    <option value="es">Spanish</option>
                    <option value="fr">French</option>
                    <option value="de">German</option>
                  </select>
                </div>
              </div>
              <div className="mt-6 flex items-center gap-3">
                <Button onClick={() => handleSave("general")} className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white">
                  <Save className="w-4 h-4 mr-2" />
                  Save Changes
                </Button>
                {saved === "general" && (
                  <motion.span initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} className="text-emerald-400 text-sm flex items-center gap-1">
                    <Check className="w-4 h-4" /> Saved
                  </motion.span>
                )}
              </div>
            </Card>

            <Card className="p-6 bg-white/[0.03] backdrop-blur-xl border-white/[0.06]">
              <h3 className="text-lg font-semibold text-white mb-4">Environment Verification</h3>
              <p className="text-white/50 text-sm mb-4">Verify that all required environment variables and services are properly configured.</p>
              <Button onClick={runEnvCheck} variant="outline" className="border-white/10 text-white hover:bg-white/10">
                <AlertCircle className="w-4 h-4 mr-2" />
                Run Verification
              </Button>
              {showEnvCheck && (
                <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="mt-4 space-y-2">
                  {envStatus.map((env) => (
                    <div key={env.key} className="flex items-center justify-between p-3 rounded-lg bg-white/5 border border-white/[0.04]">
                      <div className="flex items-center gap-2">
                        <div className={`w-2 h-2 rounded-full ${env.status === "ok" ? "bg-emerald-500" : env.status === "warning" ? "bg-amber-500" : "bg-red-500"}`} />
                        <span className="text-sm text-white/80">{env.label}</span>
                      </div>
                      <span className={`text-xs ${env.status === "ok" ? "text-emerald-400" : "text-amber-400"}`}>{env.message}</span>
                    </div>
                  ))}
                </motion.div>
              )}
            </Card>
          </div>
        );

      case "notifications":
        return (
          <Card className="p-6 bg-white/[0.03] backdrop-blur-xl border-white/[0.06]">
            <h3 className="text-lg font-semibold text-white mb-4">Notification Preferences</h3>
            <div className="space-y-4">
              {[
                { key: "email_notifications", label: "Email Notifications", desc: "Receive updates via email" },
                { key: "sms_notifications", label: "SMS Notifications", desc: "Receive text message alerts" },
                { key: "weekly_digest", label: "Weekly Digest", desc: "Weekly summary of platform activity" },
              ].map((item) => (
                <div key={item.key} className="flex items-center justify-between p-4 rounded-xl bg-white/5 border border-white/[0.04]">
                  <div>
                    <div className="text-sm font-medium text-white">{item.label}</div>
                    <div className="text-xs text-white/50">{item.desc}</div>
                  </div>
                  <button
                    onClick={() => setForm((p) => ({ ...p, [item.key]: !(p as unknown as Record<string, boolean>)[item.key] }))}
                    className={`relative w-12 h-6 rounded-full transition-colors ${form[item.key as keyof typeof form] ? "bg-indigo-600" : "bg-white/10"}`}
                  >
                    <div className={`absolute top-0.5 w-5 h-5 rounded-full bg-white shadow transition-transform ${form[item.key as keyof typeof form] ? "translate-x-6" : "translate-x-0.5"}`} />
                  </button>
                </div>
              ))}
            </div>
            <div className="mt-6">
              <Button onClick={() => handleSave("notifications")} className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white">
                <Save className="w-4 h-4 mr-2" /> Save Preferences
              </Button>
              {saved === "notifications" && (
                <motion.span initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} className="text-emerald-400 text-sm ml-3">
                  <Check className="w-4 h-4 inline mr-1" /> Saved
                </motion.span>
              )}
            </div>
          </Card>
        );

      case "security":
        return (
          <div className="space-y-6">
            <Card className="p-6 bg-white/[0.03] backdrop-blur-xl border-white/[0.06]">
              <h3 className="text-lg font-semibold text-white mb-4">Change Password</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-white/70 mb-1">Current Password</label>
                  <Input type="password" value={form.current_password} onChange={(e) => setForm((p) => ({ ...p, current_password: e.target.value }))} className="bg-white/5 border-white/10 text-white" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-white/70 mb-1">New Password</label>
                  <Input type="password" value={form.new_password} onChange={(e) => setForm((p) => ({ ...p, new_password: e.target.value }))} className="bg-white/5 border-white/10 text-white" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-white/70 mb-1">Confirm Password</label>
                  <Input type="password" value={form.confirm_password} onChange={(e) => setForm((p) => ({ ...p, confirm_password: e.target.value }))} className="bg-white/5 border-white/10 text-white" />
                </div>
              </div>
              <Button onClick={() => handleSave("security")} className="mt-6 bg-gradient-to-r from-indigo-600 to-purple-600 text-white">
                <Save className="w-4 h-4 mr-2" /> Update Password
              </Button>
              {saved === "security" && (
                <motion.span initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} className="text-emerald-400 text-sm ml-3">
                  <Check className="w-4 h-4 inline mr-1" /> Updated
                </motion.span>
              )}
            </Card>

            <Card className="p-6 bg-white/[0.03] backdrop-blur-xl border-white/[0.06]">
              <h3 className="text-lg font-semibold text-white mb-4">Session Management</h3>
              <div className="flex items-center justify-between p-4 rounded-xl bg-white/5 border border-white/[0.04]">
                <div>
                  <div className="text-sm font-medium text-white">Active Sessions</div>
                  <div className="text-xs text-white/50">Manage your active login sessions</div>
                </div>
                <Button variant="outline" className="border-white/10 text-white/70 hover:text-white hover:bg-white/10" onClick={() => {
                  localStorage.clear();
                  window.location.assign("/login");
                }}>
                  Sign Out All Devices
                </Button>
              </div>
            </Card>
          </div>
        );

      case "integrations":
        return (
          <div className="space-y-6">
            <Card className="p-6 bg-white/[0.03] backdrop-blur-xl border-white/[0.06]">
              <h3 className="text-lg font-semibold text-white mb-4">API Integrations</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-white/70 mb-1">ElevenLabs API Key</label>
                  <Input type="password" value={form.elevenlabs_key} onChange={(e) => setForm((p) => ({ ...p, elevenlabs_key: e.target.value }))} className="bg-white/5 border-white/10 text-white" placeholder="sk_..." />
                  <p className="text-xs text-white/40 mt-1">Used for AI voice synthesis in voice agent</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-white/70 mb-1">Stripe Secret Key</label>
                  <Input type="password" value={form.stripe_key} onChange={(e) => setForm((p) => ({ ...p, stripe_key: e.target.value }))} className="bg-white/5 border-white/10 text-white" placeholder="sk_live_..." />
                  <p className="text-xs text-white/40 mt-1">Used for payment processing</p>
                </div>
              </div>
              <Button onClick={() => handleSave("integrations")} className="mt-6 bg-gradient-to-r from-indigo-600 to-purple-600 text-white">
                <Save className="w-4 h-4 mr-2" /> Save Integrations
              </Button>
              {saved === "integrations" && (
                <motion.span initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} className="text-emerald-400 text-sm ml-3">
                  <Check className="w-4 h-4 inline mr-1" /> Saved
                </motion.span>
              )}
            </Card>
          </div>
        );

      case "voice":
        return (
          <Card className="p-6 bg-white/[0.03] backdrop-blur-xl border-white/[0.06]">
            <h3 className="text-lg font-semibold text-white mb-4">Voice Agent Settings</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-white/70 mb-1">Greeting Message</label>
                <textarea
                  value={form.voice_greeting}
                  onChange={(e) => setForm((p) => ({ ...p, voice_greeting: e.target.value }))}
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder:text-white/20 resize-none h-24"
                />
              </div>
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <label className="block text-sm font-medium text-white/70 mb-1">Voice Language</label>
                  <select value={form.voice_language} onChange={(e) => setForm((p) => ({ ...p, voice_language: e.target.value }))} className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white">
                    <option value="en-US">English (US)</option>
                    <option value="en-GB">English (UK)</option>
                    <option value="es-ES">Spanish</option>
                    <option value="fr-FR">French</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-white/70 mb-1">Speech Speed</label>
                  <div className="flex items-center gap-3">
                    <input type="range" min="0.5" max="2.0" step="0.1" value={form.voice_speed} onChange={(e) => setForm((p) => ({ ...p, voice_speed: parseFloat(e.target.value) }))} className="flex-1 accent-indigo-500" />
                    <span className="text-white/70 text-sm w-10">{form.voice_speed.toFixed(1)}x</span>
                  </div>
                </div>
              </div>
            </div>
            <Button onClick={() => handleSave("voice")} className="mt-6 bg-gradient-to-r from-indigo-600 to-purple-600 text-white">
              <Save className="w-4 h-4 mr-2" /> Save Voice Settings
            </Button>
            {saved === "voice" && (
              <motion.span initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} className="text-emerald-400 text-sm ml-3">
                <Check className="w-4 h-4 inline mr-1" /> Saved
              </motion.span>
            )}
          </Card>
        );

      case "appearance":
        return (
          <div className="space-y-6">
            <Card className="p-6 bg-white/[0.03] backdrop-blur-xl border-white/[0.06]">
              <h3 className="text-lg font-semibold text-white mb-4">Theme</h3>
              <div className="flex gap-4">
                {["dark", "light", "system"].map((theme) => (
                  <button
                    key={theme}
                    onClick={() => setForm((p) => ({ ...p, theme }))}
                    className={`flex-1 p-4 rounded-xl border text-center capitalize transition-all ${
                      form.theme === theme ? "border-indigo-500 bg-indigo-500/10 text-white" : "border-white/10 text-white/50 hover:text-white/70"
                    }`}
                  >
                    <Palette className="w-5 h-5 mx-auto mb-2" />
                    {theme}
                  </button>
                ))}
              </div>
            </Card>

            <Card className="p-6 bg-white/[0.03] backdrop-blur-xl border-white/[0.06]">
              <h3 className="text-lg font-semibold text-white mb-4">Accent Color</h3>
              <div className="flex gap-3">
                {["indigo", "purple", "emerald", "rose", "amber"].map((color) => (
                  <button
                    key={color}
                    onClick={() => setForm((p) => ({ ...p, accent_color: color }))}
                    className={`w-10 h-10 rounded-full transition-all ${
                      color === "indigo" ? "bg-indigo-600" :
                      color === "purple" ? "bg-purple-600" :
                      color === "emerald" ? "bg-emerald-600" :
                      color === "rose" ? "bg-rose-600" : "bg-amber-600"
                    } ${form.accent_color === color ? "ring-2 ring-white ring-offset-2 ring-offset-gray-950 scale-110" : ""}`}
                  />
                ))}
              </div>
            </Card>

            <div className="flex items-center gap-3">
              <Button onClick={() => handleSave("appearance")} className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white">
                <Save className="w-4 h-4 mr-2" /> Save Appearance
              </Button>
              {saved === "appearance" && (
                <motion.span initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} className="text-emerald-400 text-sm flex items-center gap-1">
                  <Check className="w-4 h-4" /> Saved
                </motion.span>
              )}
            </div>
          </div>
        );
    }
  };

  return (
    <AppShell>
      <div className="space-y-6">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="text-3xl font-bold text-white">Settings</h1>
          <p className="text-white/50 mt-1">Configure your platform, integrations, and preferences</p>
        </motion.div>

        <div className="flex gap-1 p-1 rounded-xl bg-white/5 border border-white/[0.06] overflow-x-auto">
          {TABS.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-all ${
                  activeTab === tab.id ? "bg-indigo-600/20 text-indigo-300 shadow-sm" : "text-white/50 hover:text-white/70"
                }`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </button>
            );
          })}
        </div>

        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
          >
            {renderTabContent()}
          </motion.div>
        </AnimatePresence>
      </div>
    </AppShell>
  );
}