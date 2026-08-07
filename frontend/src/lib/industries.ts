export type Industry = {
  slug: string;
  name: string;
  title: string;
  description: string;
  keywords: string[];
  h1: string;
  body: string;
  painPoints: string[];
  outcome: string;
};

export const industries: Industry[] = [
  {
    slug: "e-commerce",
    name: "E-Commerce",
    title: "E-Commerce Lead Generation with AI",
    description:
      "Automate E-Commerce lead generation with Genesis AI agents. Voice-first outreach, workflow automation, and autonomous business launch.",
    keywords: ["E-Commerce lead generation", "E-Commerce automation", "AI E-Commerce"],
    h1: "AI-Powered Lead Generation for E-Commerce",
    body: "E-commerce brands waste hours on repetitive outreach and follow-up. Genesis runs a full-duplex voice agent and a 19-agent workforce that answer your line in real time, qualify inbound traffic, and keep every lead moving through your funnel automatically.",
    painPoints: ["Missed calls and slow response times", "Manual outreach that never scales", "Leads going cold between first touch and follow-up"],
    outcome: "Never miss a buyer again — your voice agent answers in real time and routes hot leads straight to your team.",
  },
  {
    slug: "real-estate",
    name: "Real Estate",
    title: "Real Estate Lead Generation with AI",
    description:
      "Automate Real Estate lead generation with Genesis AI agents. Voice-first outreach, workflow automation, and autonomous business launch.",
    keywords: ["Real Estate lead generation", "Real Estate automation", "AI Real Estate"],
    h1: "AI-Powered Lead Generation for Real Estate",
    body: "Real estate is a speed game. Genesis answers every inbound call with a full-duplex voice agent, qualifies buyer and seller intent, books showings, and triggers outreach sequences — so your team only talks to ready clients.",
    painPoints: ["Callers hitting voicemail", "Buyers and sellers contacted too late", "Manual CRM follow-up slipping through the cracks"],
    outcome: "Respond in seconds, qualify in one call, and close more listings with the same headcount.",
  },
  {
    slug: "home-services",
    name: "Home Services",
    title: "Home Services Lead Generation with AI",
    description:
      "Automate Home Services lead generation with Genesis AI agents. Voice-first outreach, workflow automation, and autonomous business launch.",
    keywords: ["Home Services lead generation", "Home Services automation", "AI Home Services"],
    h1: "AI-Powered Lead Generation for Home Services",
    body: "Plumbers, electricians, and contractors win the job that answers first. Genesis answers your business line around the clock, captures every service request, and automates appointment booking and follow-up.",
    painPoints: ["After-hours calls going unanswered", "Estimates booked days late", "No-shows and forgotten appointments"],
    outcome: "Answer every call, book every job, and cut missed-revenue to zero.",
  },
  {
    slug: "dental-clinics",
    name: "Dental Clinics",
    title: "Dental Clinics Lead Generation with AI",
    description:
      "Automate Dental Clinics lead generation with Genesis AI agents. Voice-first outreach, workflow automation, and autonomous business launch.",
    keywords: ["Dental Clinics lead generation", "Dental Clinics automation", "AI Dental Clinics"],
    h1: "AI-Powered Lead Generation for Dental Clinics",
    body: "Dental practices lose patients to the practice that answers first. Genesis answers every call with a full-duplex voice agent, schedules appointments, and runs patient reactivation campaigns automatically.",
    painPoints: ["Missed appointment calls", "Front desk overwhelmed during peak hours", "No-shows and lapsed patients"],
    outcome: "Fill your schedule, reduce no-shows, and rebook lapsed patients on autopilot.",
  },
  {
    slug: "fitness-coaching",
    name: "Fitness Coaching",
    title: "Fitness Coaching Lead Generation with AI",
    description:
      "Automate Fitness Coaching lead generation with Genesis AI agents. Voice-first outreach, workflow automation, and autonomous business launch.",
    keywords: ["Fitness Coaching lead generation", "Fitness Coaching automation", "AI Fitness Coaching"],
    h1: "AI-Powered Lead Generation for Fitness Coaches",
    body: "Coaches lose prospects to slow follow-up. Genesis qualifies inbound interest, answers questions in real time, and runs onboarding and reactivation sequences so you spend your time coaching, not chasing.",
    painPoints: ["Prospects going cold after inquiry", "Manual intro-call scheduling", "Churn without a reactivation plan"],
    outcome: "Turn inquiries into signed clients faster and keep them engaged automatically.",
  },
  {
    slug: "legal-practices",
    name: "Legal Practices",
    title: "Legal Practices Lead Generation with AI",
    description:
      "Automate Legal Practices lead generation with Genesis AI agents. Voice-first outreach, workflow automation, and autonomous business launch.",
    keywords: ["Legal Practices lead generation", "Legal Practices automation", "AI Legal Practices"],
    h1: "AI-Powered Lead Generation for Law Firms",
    body: "The firm that responds first wins the case. Genesis screens intake calls with a full-duplex voice agent, captures case details, and routes qualified leads to the right attorney instantly.",
    painPoints: ["Missed intake calls after hours", "Prospects consulting a faster firm", "Paralegals buried in screening calls"],
    outcome: "Never miss a consultation — qualify intake 24/7 and staff your calendar with ready clients.",
  },
  {
    slug: "e-commerce-fulfillment",
    name: "E-Commerce Fulfillment",
    title: "E-Commerce Fulfillment Lead Generation with AI",
    description:
      "Automate E-Commerce Fulfillment lead generation with Genesis AI agents. Voice-first outreach, workflow automation, and autonomous business launch.",
    keywords: ["E-Commerce Fulfillment lead generation", "Fulfillment automation", "AI Fulfillment"],
    h1: "AI-Powered Lead Generation for Fulfillment",
    body: "Fulfillment and 3PL providers run on volume and speed. Genesis answers carrier and merchant inquiries instantly, qualifies new accounts, and keeps quotes and follow-ups moving automatically.",
    painPoints: ["High-volume inquiry answering", "Slow quote turnaround", "Merchant churn after onboarding"],
    outcome: "Quote faster, onboard more merchants, and protect revenue with automated follow-up.",
  },
  {
    slug: "boutique-agencies",
    name: "Boutique Agencies",
    title: "Boutique Agencies Lead Generation with AI",
    description:
      "Automate Boutique Agencies lead generation with Genesis AI agents. Voice-first outreach, workflow automation, and autonomous business launch.",
    keywords: ["Boutique Agencies lead generation", "Agency automation", "AI Agencies"],
    h1: "AI-Powered Lead Generation for Boutique Agencies",
    body: "Agencies live and die by pipeline. Genesis answers discovery-call requests in real time, qualifies fit, and runs the outreach sequences that fill your funnel while you deliver the work.",
    painPoints: ["Inconsistent prospecting", "Slow discovery-call scheduling", "No time for outbound while delivering"],
    outcome: "A 19-agent workforce fills your pipeline so you can focus on client work.",
  },
  {
    slug: "property-management",
    name: "Property Management",
    title: "Property Management Lead Generation with AI",
    description:
      "Automate Property Management lead generation with Genesis AI agents. Voice-first outreach, workflow automation, and autonomous business launch.",
    keywords: ["Property Management lead generation", "Property Management automation", "AI Property Management"],
    h1: "AI-Powered Lead Generation for Property Managers",
    body: "Property managers juggle tenants, owners, and maintenance. Genesis answers after-hours tenant calls, qualifies new owner leads, and routes maintenance requests automatically.",
    painPoints: ["After-hours tenant calls", "Owner acquisition going cold", "Maintenance requests falling through the cracks"],
    outcome: "Answer every tenant, win every owner, and keep operations running around the clock.",
  },
  {
    slug: "auto-dealerships",
    name: "Auto Dealerships",
    title: "Auto Dealerships Lead Generation with AI",
    description:
      "Automate Auto Dealerships lead generation with Genesis AI agents. Voice-first outreach, workflow automation, and autonomous business launch.",
    keywords: ["Auto Dealerships lead generation", "Dealership automation", "AI Dealerships"],
    h1: "AI-Powered Lead Generation for Auto Dealerships",
    body: "Dealerships lose sales to the 10-second response rule. Genesis answers every inquiry in real time, qualifies buyer intent, and books test drives automatically.",
    painPoints: ["Leads lost to slow response", "Showroom staff on the phone all day", "Used-car inquiries going cold"],
    outcome: "Respond in under 10 seconds, qualify more buyers, and sell more cars per lead.",
  },
  {
    slug: "med-spas",
    name: "MedSpas",
    title: "MedSpas Lead Generation with AI",
    description:
      "Automate MedSpas lead generation with Genesis AI agents. Voice-first outreach, workflow automation, and autonomous business launch.",
    keywords: ["MedSpas lead generation", "MedSpa automation", "AI MedSpas"],
    h1: "AI-Powered Lead Generation for MedSpas",
    body: "MedSpas compete on first response and booking ease. Genesis answers calls around the clock, books consultations, and runs patient reactivation campaigns automatically.",
    painPoints: ["Missed consultation calls", "No-shows eating into revenue", "Lapsed clients not reactivated"],
    outcome: "Book more consultations, fill your calendar, and keep clients coming back.",
  },
  {
    slug: "contractors",
    name: "Contractors",
    title: "Contractors Lead Generation with AI",
    description:
      "Automate Contractors lead generation with Genesis AI agents. Voice-first outreach, workflow automation, and autonomous business launch.",
    keywords: ["Contractors lead generation", "Contractor automation", "AI Contractors"],
    h1: "AI-Powered Lead Generation for Contractors",
    body: "Contractors win bids by responding first. Genesis answers every call on the jobsite, captures project details, and books estimates automatically — even when you're covered in dust.",
    painPoints: ["Calls missed on the jobsite", "Estimates booked days late", "Follow-up that never happens"],
    outcome: "Answer every call from any jobsite and book more estimates automatically.",
  },
];

export function industryBySlug(slug: string): Industry | undefined {
  return industries.find((i) => i.slug === slug);
}
