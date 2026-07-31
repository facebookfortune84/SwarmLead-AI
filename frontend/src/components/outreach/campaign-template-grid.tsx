"use client";

import { motion } from "framer-motion";
import { Zap, ArrowRight, Send, CalendarClock, RefreshCcw } from "lucide-react";

export interface CampaignTemplate {
  name: string;
  description: string;
  icon: typeof Send;
  subject: string;
  body: string;
}

export const CAMPAIGN_TEMPLATES: CampaignTemplate[] = [
  {
    name: "Cold Outreach",
    description: "Initial prospecting sequence for new leads.",
    icon: Zap,
    subject: "Quick question about {company}",
    body: "Hi {first_name},\n\nI noticed {company} is doing some interesting things in your space. We help teams like yours automate lead qualification and outreach.\n\nWould you be open to a 15-minute call this week?\n\nBest,\n{from_name}",
  },
  {
    name: "Follow-Up",
    description: "Re-engagement sequence for warm leads.",
    icon: Send,
    subject: "Following up — {company}",
    body: "Hi {first_name},\n\nJust checking in on my earlier note. I'd love to show you how we cut lead response times in half.\n\nAre you available for a quick chat?\n\nBest,\n{from_name}",
  },
  {
    name: "Product Demo",
    description: "Demo scheduling campaign for qualified prospects.",
    icon: CalendarClock,
    subject: "See SwarmLead in action",
    body: "Hi {first_name},\n\nI'd love to walk you through a live demo of how our AI agents qualify and convert leads for you automatically.\n\nPick a time that works: {booking_link}\n\nBest,\n{from_name}",
  },
  {
    name: "Customer Reactivation",
    description: "Previous client re-engagement outreach.",
    icon: RefreshCcw,
    subject: "We've missed you, {company}",
    body: "Hi {first_name},\n\nWe've shipped major upgrades since we last spoke — including new voice agents and workflow automation.\n\nWould you like to see what's new?\n\nBest,\n{from_name}",
  },
];

interface CampaignTemplateGridProps {
  onSelect?: (template: CampaignTemplate) => void;
}

export function CampaignTemplateGrid({ onSelect }: CampaignTemplateGridProps) {
  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      {CAMPAIGN_TEMPLATES.map((template, i) => {
        const Icon = template.icon;
        return (
          <motion.button
            key={template.name}
            type="button"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.06 }}
            onClick={() => onSelect?.(template)}
            className="group text-left rounded-xl border border-white/[0.06] bg-white/[0.02] p-5 hover:border-indigo-500/40 hover:bg-white/[0.04] hover:shadow-lg hover:shadow-indigo-500/5 transition-all"
          >
            <div className="flex items-center justify-between">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center">
                <Icon className="w-5 h-5 text-white" />
              </div>
              {onSelect && (
                <ArrowRight className="w-4 h-4 text-white/20 group-hover:text-indigo-400 group-hover:translate-x-0.5 transition-all" />
              )}
            </div>
            <h3 className="mt-4 font-medium text-white">{template.name}</h3>
            <p className="mt-1 text-sm text-white/50">{template.description}</p>
          </motion.button>
        );
      })}
    </div>
  );
}
