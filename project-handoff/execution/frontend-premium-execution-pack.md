# Frontend Premium Execution Pack

**Branch**: `implementation/frontend-premium`  
**Base Commit**: `65d623b`  
**Target**: Enterprise-grade, luxury SaaS, voice-first, conversion-optimized, mobile-first, accessibility-first, SEO-first  
**Swarm**: 3 BuilderAgents (Design System, Voice Components, Application Screens)  
**Duration**: Parallel execution, zero handoffs

---

## 1. Design System Foundation (`frontend/src/design-system/`)

### Files to Create (17)
```
frontend/src/design-system/
├── tokens/
│   ├── colors.ts                    # Luxury palette
│   ├── typography.ts                # Display/heading/body scales
│   ├── spacing.ts                   # 4px base, golden ratio
│   ├── shadows.ts                   # Layered depth system
│   ├── border-radius.ts             # Rounded XL/2XL/Full
│   └── motion.ts                    # Duration/easing curves
├── components/
│   ├── PremiumCard.tsx
│   ├── PremiumButton.tsx
│   ├── PremiumInput.tsx
│   ├── PremiumDialog.tsx
│   ├── PremiumSheet.tsx
│   ├── PremiumTable.tsx
│   ├── PremiumBadge.tsx
│   └── PremiumTooltip.tsx
├── animations/
│   ├── premiumVariants.ts
│   ├── voicePulse.ts
│   ├── metricCount.ts
│   ├── pageTransitions.ts
│   └── microInteractions.ts
└── index.ts
```

### Implementation Spec

**tokens/colors.ts**
```typescript
export const colors = {
  // Luxury Navy → Gold → Cream palette
  primary: {
    50: '#f0f4f8',
    100: '#d9e2ec',
    200: '#bcccdc',
    300: '#9fb3c8',
    400: '#829ab1',
    500: '#627d98',
    600: '#486581',
    700: '#334e68',
    800: '#243b53',
    900: '#102a43',
  },
  accent: {
    gold: '#D4A843',
    goldLight: '#E8C56D',
    goldDark: '#B89038',
  },
  neutral: {
    white: '#FFFFFF',
    cream: '#FDFBF7',
    gray: {
      50: '#FAFAFA',
      100: '#F5F5F5',
      200: '#E5E5E5',
      300: '#D4D4D4',
      400: '#A3A3A3',
      500: '#737373',
      600: '#525252',
      700: '#404040',
      800: '#262626',
      900: '#171717',
    }
  },
  semantic: {
    success: '#10B981',
    warning: '#F59E0B',
    error: '#EF4444',
    info: '#3B82F6',
  }
};
```

**tokens/typography.ts**
```typescript
export const typography = {
  display: {
    xl: { fontSize: '72px', lineHeight: '80px', fontWeight: 300, letterSpacing: '-0.02em' },
    lg: { fontSize: '60px', lineHeight: '68px', fontWeight: 300, letterSpacing: '-0.01em' },
    md: { fontSize: '48px', lineHeight: '56px', fontWeight: 400 },
    sm: { fontSize: '36px', lineHeight: '44px', fontWeight: 400 },
  },
  heading: {
    xl: { fontSize: '32px', lineHeight: '40px', fontWeight: 600 },
    lg: { fontSize: '28px', lineHeight: '36px', fontWeight: 600 },
    md: { fontSize: '24px', lineHeight: '32px', fontWeight: 600 },
    sm: { fontSize: '20px', lineHeight: '28px', fontWeight: 600 },
  },
  body: {
    lg: { fontSize: '18px', lineHeight: '28px', fontWeight: 400 },
    md: { fontSize: '16px', lineHeight: '24px', fontWeight: 400 },
    sm: { fontSize: '14px', lineHeight: '20px', fontWeight: 400 },
  },
  mono: {
    lg: { fontSize: '16px', lineHeight: '24px', fontFamily: 'JetBrains Mono' },
    md: { fontSize: '14px', lineHeight: '20px', fontFamily: 'JetBrains Mono' },
  }
};
```

**animations/premiumVariants.ts**
```typescript
import { Variants } from 'framer-motion';

export const premiumVariants: Record<string, Variants> = {
  pageEnter: {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.6, ease: [0.25, 0.46, 0.45, 0.94] }
  },
  cardHover: {
    scale: 1.02,
    boxShadow: '0 20px 40px rgba(0,0,0,0.1)',
    transition: { duration: 0.3, ease: 'easeOut' }
  },
  voicePulse: {
    scale: [1, 1.05, 1],
    transition: { repeat: Infinity, duration: 1.5, ease: 'easeInOut' }
  },
  metricCount: {
    initial: 0,
    animate: { value: 100 },
    transition: { duration: 2, ease: 'easeOut' }
  },
  voiceWave: {
    pathLength: [0, 1],
    transition: { duration: 0.5, repeat: Infinity, ease: 'linear' }
  },
  orbState: {
    idle: { scale: 1, opacity: 0.6 },
    listening: { scale: 1.1, opacity: 1, transition: { duration: 0.2 } },
    speaking: { scale: [1, 1.2, 1], transition: { duration: 0.5, repeat: Infinity } },
    thinking: { rotate: 360, transition: { duration: 1, repeat: Infinity, ease: 'linear' } }
  }
};
```

---

## 2. Voice Components (Critical — 7 Components)

### Files to Create
```
frontend/src/components/voice/
├── VoiceOrb.tsx              # Animated orb (idle/listening/speaking/thinking)
├── VoiceWaveform.tsx         # Real-time audio visualization
├── VoiceControls.tsx         # Mute, volume, end call
├── VoiceSession.tsx          # Session wrapper
├── VoiceTranscript.tsx       # Live transcript with highlights
├── VoiceStatus.tsx           # Connection, latency, quality
└── index.ts
```

### Implementation Spec

**VoiceOrb.tsx**
```tsx
import { motion, AnimatePresence } from 'framer-motion';
import { orbState } from '@/design-system/animations/premiumVariants';

export function VoiceOrb({ state }: { state: 'idle' | 'listening' | 'speaking' | 'thinking' }) {
  const variants = {
    idle: { scale: 1, opacity: 0.6 },
    listening: { scale: 1.1, opacity: 1 },
    speaking: { scale: [1, 1.2, 1] },
    thinking: { rotate: 360 }
  };
  
  return (
    <motion.div
      className="w-20 h-20 rounded-full bg-gradient-to-br from-primary-700 to-primary-900"
      animate={state}
      variants={orbState}
      className="shadow-[0_0_40px_rgba(16,42,67,0.4)]"
    />
  );
}
```

**VoiceWaveform.tsx**
```tsx
import { motion } from 'framer-motion';

export function VoiceWaveform({ audioData }: { audioData: number[] }) {
  return (
    <svg className="w-full h-20" viewBox="0 0 400 80">
      <defs>
        <linearGradient id="waveGradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#D4A843" />
          <stop offset="100%" stopColor="#B89038" />
        </linearGradient>
      </defs>
      <motion.path
        d={generateWavePath(audioData)}
        stroke="url(#waveGradient)"
        strokeWidth={2}
        fill="none"
        strokeLinecap="round"
        animate={{ pathLength: [0, 1] }}
        transition={{ duration: 0.5, repeat: Infinity, ease: 'linear' }}
      />
    </svg>
  );
}
```

**VoiceLandingAgent.tsx** (Critical — Landing Page)
```tsx
'use client';
import { useEffect, useRef, useState } from 'react';
import { VoiceOrb, VoiceWaveform, VoiceTranscript } from '@/components/voice';
import { LandingAgent } from '@/agents/landing';

export function VoiceLandingAgent() {
  const [session, setSession] = useState<VoiceSession | null>(null);
  const [state, setState] = useState<'idle' | 'listening' | 'speaking'>('idle');
  const [transcript, setTranscript] = useState('');
  
  // Proactive greeting triggers
  useEffect(() => {
    const timer = setTimeout(() => {
      startSession('proactive_greeting');
    }, 3000);
    
    const scrollHandler = () => {
      if (window.scrollY > window.innerHeight * 0.5) {
        startSession('contextual_offer');
      }
    };
    window.addEventListener('scroll', scrollHandler);
    
    return () => { clearTimeout(timer); window.removeEventListener('scroll', scrollHandler); };
  }, []);
  
  async function startSession(greetingType: string) {
    const session = await VoiceSessionManager.create('visitor', greetingType);
    setSession(session);
    setState('speaking');
    
    // Stream greeting
    const greeting = await LandingAgent.greet(session.id, greetingType);
    await session.streamTTS(greeting);
    setState('listening');
  }
  
  return (
    <div className="fixed bottom-6 right-6 z-50">
      <VoiceOrb state={state} />
      <VoiceWaveform audioData={session?.audioData || []} />
      <VoiceTranscript transcript={transcript} />
    </div>
  );
}
```

---

## 3. Landing Page (`/`)

### Files to Create
```
frontend/src/app/
├── page.tsx                      # Voice-first landing (was redirect)
├── voice-demo/page.tsx           # Live voice trial
├── onboarding/page.tsx           # Voice-guided wizard
├── pricing/page.tsx              # Interactive + voice FAQ
├── dashboard/page.tsx            # Premium + live voice controls
├── agents/page.tsx               # Voice agent management
├── components/landing/
│   ├── VoiceLandingAgent.tsx     # Proactive voice agent
│   ├── VoiceGreeting.tsx         # Proactive greeting
│   ├── FeatureShowcase.tsx       # Voice-narrated features
│   ├── SocialProof.tsx           # Animated testimonials
│   └── CTASection.tsx            # Voice-enabled CTA
└── components/onboarding/
    ├── OnboardingWizard.tsx
    ├── WelcomeStep.tsx
    ├── BusinessProfileStep.tsx
    ├── GoalsStep.tsx
    ├── VoiceSetupStep.tsx
    └── LaunchStep.tsx
```

### Page Specs

**page.tsx (Landing)**
```tsx
import { VoiceLandingAgent } from '@/components/landing/VoiceLandingAgent';
import { FeatureShowcase } from '@/components/landing/FeatureShowcase';
import { SocialProof } from '@/components/landing/SocialProof';
import { CTASection } from '@/components/landing/CTASection';

export default function LandingPage() {
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "SoftwareApplication",
            "name": "Genesis",
            "applicationCategory": "BusinessApplication",
            "operatingSystem": "Cloud",
            "offers": { "@type": "Offer", "price": "39", "priceCurrency": "USD" },
            "featureList": ["Voice AI Agents", "Autonomous Business Launch", "Lead Generation", "Workflow Automation"]
          })
        }}
      />
      <div className="min-h-screen bg-neutral-cream">
        <VoiceLandingAgent />
        <main className="pt-32 pb-20 px-6 max-w-7xl mx-auto">
          <FeatureShowcase />
          <SocialProof />
          <CTASection />
        </main>
      </div>
    </>
  );
}
```

---

## 4. Animation System

### Files to Create
```
frontend/src/design-system/animations/
├── premiumVariants.ts
├── voicePulse.ts
├── metricCount.ts
├── pageTransitions.ts
└── microInteractions.ts
```

---

## 3. Premium Dashboard & Agent Workspace

### Files to Create
```
frontend/src/app/dashboard/
├── page.tsx
├── components/
│   ├── LiveMetrics.tsx           # Animated real-time metrics
│   ├── VoiceActivity.tsx         # Live voice sessions
│   ├── AgentWorkspace.tsx        # Live agent monitoring
│   ├── ConversionFunnel.tsx      # Voice-narrated funnel
│   ├── AgentControls.tsx         # Voice commands for agents
│   └── LiveActivity.tsx          # Real-time activity feed
```

**LiveMetrics.tsx**
```tsx
import { motion } from 'framer-motion';
import { metricCount } from '@/design-system/animations/premiumVariants';

export function LiveMetrics({ data }: { data: DashboardData }) {
  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      <PremiumCard>
        <h3 className="text-sm text-muted-foreground">Total Leads</h3>
        <motion.span
          className="mt-2 text-3xl font-bold"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: [0.25, 0.46, 0.45, 0.94] }}
        >
          {data?.leads || 0}
        </motion.span>
      </PremiumCard>
      {/* ... */}
    </div>
  );
}
```

---

## 4. Voice Demo Experience

### Files to Create
```
frontend/src/app/voice-demo/
├── page.tsx
├── components/
│   ├── VoiceTrial.tsx            # Live voice trial
│   ├── VoiceSelector.tsx         # Voice selection
│   └── TranscriptViewer.tsx      # Live transcript
```

---

## 4. Pricing Experience

### Files to Create
```
frontend/src/app/pricing/
├── page.tsx
├── components/
│   ├── PricingCards.tsx          # Animated tier cards
│   ├── VoiceFAQ.tsx              # Voice-enabled FAQ
│   └── TierComparison.tsx        # Animated comparison
```

---

## 5. Core Web Vitals Targets

| Metric | Target | Implementation |
|--------|--------|----------------|
| **LCP** | <2.5s | Edge rendering, image optimization, font preload |
| **FID** | <100ms | Code splitting, web workers, minimal main thread |
| **CLS** | <0.1 | Font display swap, aspect ratios, reserved space |
| **INP** | <200ms | React 19 concurrent, useTransition, useDeferredValue |

### Implementation
```javascript
// next.config.js
module.exports = {
  images: { formats: ['image/avif', 'image/webp'] },
  experimental: { optimizeCss: true },
  compiler: { removeConsole: process.env.NODE_ENV === 'production' },
  headers: async () => [
    { source: '/:path*', headers: [
      { key: 'X-Content-Type-Options', value: 'nosniff' },
      { key: 'X-Frame-Options', value: 'DENY' },
      { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' }
    ]}
  ]
};
```

---

## 5. Accessibility (WCAG 2.1 AA)

| Requirement | Implementation |
|-------------|----------------|
| Color contrast | 4.5:1 minimum, luxury palette tested |
| Keyboard navigation | All interactive elements reachable |
| Screen readers | ARIA labels, live regions for voice |
| Focus management | Visible focus rings, logical tab order |
| Voice fallback | Text input always available |
| Reduced motion | `prefers-reduced-motion` respected |

---

## 6. Mobile-First Voice UX

| Breakpoint | Voice Behavior |
|------------|----------------|
| < 640px | Voice Orb bottom-center, full-screen transcript |
| 640-1024px | Voice Orb bottom-right, side transcript |
| > 1024px | Voice Orb bottom-right, inline transcript |

---

## 5. SEO Integration

### Files to Create
```
frontend/src/app/
├── layout.tsx                      # JSON-LD, canonical, hreflang
├── robots.ts                       # Dynamic robots.txt
├── sitemap.ts                      # Auto-generated sitemap
├── app/[locale]/layout.tsx         # Hreflang
├── components/seo/
│   ├── SchemaOrg.tsx               # JSON-LD components
│   ├── BreadcrumbSchema.tsx
│   ├── FAQSchema.tsx
│   └── ProductSchema.tsx
└── app/
    ├── templates/[industry]/page.tsx    # 50 industries
    ├── use-cases/[problem]/page.tsx     # 100 problems
    ├── templates/[type]/page.tsx        # 50 templates
    ├── vs/[competitor]/page.tsx         # 20 competitors
    └── glossary/[term]/page.tsx         # 200 terms
```

**SchemaOrg.tsx**
```tsx
export function SoftwareApplicationSchema() {
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{
        __html: JSON.stringify({
          "@context": "https://schema.org",
          "@type": "SoftwareApplication",
          "name": "Genesis",
          "applicationCategory": "BusinessApplication",
          "operatingSystem": "Cloud",
          "offers": { "@type": "Offer", "price": "39", "priceCurrency": "USD" },
          "featureList": ["Voice AI Agents", "Autonomous Business Launch", "Lead Generation", "Workflow Automation"]
        })
      }}
    />
  );
}
```

---

## Files Summary

### New Files (45)
```
frontend/src/design-system/tokens/* (6)
frontend/src/design-system/components/* (8)
frontend/src/design-system/animations/* (5)
frontend/src/components/voice/* (7)
frontend/src/components/landing/* (5)
frontend/src/components/onboarding/* (5)
frontend/src/components/dashboard/* (6)
frontend/src/components/seo/* (4)
frontend/src/app/page.tsx (landing)
frontend/src/app/voice-demo/page.tsx
frontend/src/app/onboarding/page.tsx
frontend/src/app/pricing/page.tsx
frontend/src/app/dashboard/page.tsx
frontend/src/app/agents/page.tsx
frontend/src/app/templates/[industry]/page.tsx
frontend/src/app/use-cases/[problem]/page.tsx
frontend/src/app/templates/[type]/page.tsx
frontend/src/app/vs/[competitor]/page.tsx
frontend/src/app/glossary/[term]/page.tsx
frontend/src/app/layout.tsx (updated)
frontend/src/app/robots.ts
frontend/src/app/sitemap.ts
frontend/src/design-system/index.ts
```

### Modified Files (4)
```
frontend/src/app/layout.tsx          # Schema.org, canonical, hreflang
frontend/src/components/layout/app-shell.tsx  # VoiceOrb, VoiceWaveform
frontend/src/components/layout/sidebar.tsx    # Voice controls
frontend/src/lib/api.ts              # WebSocket voice support
```

---

## Parallelization Map

| Swarm Agent | Components | Can Start | Parallel |
|-------------|------------|-----------|----------|
| **DesignSystemAgent** | Tokens, Components, Animations | Immediate | ✅ 3 parallel |
| **VoiceComponentsAgent** | VoiceOrb, Waveform, Controls, Session, Transcript, Status | Immediate | ✅ 3 parallel |
| **LandingAgent** | VoiceLandingAgent, Greeting, FeatureShowcase, SocialProof, CTA | After DesignSystem | ✅ 3 parallel |
| **OnboardingAgent** | Wizard, 5 Steps | After DesignSystem | ✅ |
| **DashboardAgent** | LiveMetrics, VoiceActivity, AgentWorkspace, Funnel, Controls, Activity | After DesignSystem | ✅ |
| **PricingAgent** | Cards, VoiceFAQ, Comparison | After DesignSystem | ✅ |
| **SEOAgent** | Schema, Sitemap, Robots, 420 programmatic pages | After DesignSystem | ✅ 5 parallel |

---

## Acceptance Criteria

| Component | Criteria |
|-----------|----------|
| VoiceOrb | 4 states (idle/listening/speaking/thinking), smooth transitions |
| VoiceWaveform | Real-time visualization, 60fps |
| VoiceLandingAgent | Proactive greeting at 3s, scroll 50%, exit intent, return visitor |
| OnboardingWizard | 5 voice-guided steps, mic test, voice selection |
| Dashboard | Live metrics animated, voice activity, agent workspace |
| Design System | Tokens, 8 components, 5 animations — all typed |
| LCP | <2.5s on landing page |
| CLS | <0.1 |
| Accessibility | WCAG 2.1 AA, voice fallback, keyboard nav |

---

## Definition of Done

- [ ] All 45 new files created and typed
- [ ] Voice components integrated on landing page
- [ ] Onboarding wizard completes in <10 min
- [ ] Dashboard shows live voice activity
- [ ] Premium design system applied site-wide
- [ ] Core Web Vitals targets met
- [ ] WCAG 2.1 AA compliant
- [ ] Mobile voice UX optimized
- [ ] Schema.org on all pages
- [ ] 420 programmatic SEO pages generated
- [ ] All tests passing