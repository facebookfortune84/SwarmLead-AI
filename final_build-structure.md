# Final Frontend Directory Structure as of Jul 14, 2026

frontend/src
│
├── app
│   ├── dashboard
│   ├── leads
│   ├── workflows
│   ├── tenants
│   ├── tickets
│   ├── outreach
│   └── settings
│
├── components
│   │
│   ├── ui
│   │   ├── badge.tsx
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── dialog.tsx
│   │   ├── dropdown-menu.tsx
│   │   ├── input.tsx
│   │   ├── sheet.tsx
│   │   ├── sonner.tsx
│   │   └── table.tsx
│   │
│   ├── leads
│   │   ├── lead-table.tsx
│   │   ├── lead-search.tsx
│   │   ├── lead-status-badge.tsx
│   │   ├── lead-create-dialog.tsx
│   │   ├── lead-edit-dialog.tsx
│   │   └── lead-detail-sheet.tsx
│   │
│   ├── workflows
│   ├── tenants
│   ├── tickets
│   └── outreach
│
├── hooks
│   ├── use-dashboard.ts
│   ├── use-leads.ts
│   ├── use-tenants.ts
│   ├── use-tickets.ts
│   └── use-workflows.ts
│
├── lib
│   └── api.ts
│
└── types
    ├── lead.ts
    ├── ticket.ts
    ├── workflow.ts
    └── tenant.ts
