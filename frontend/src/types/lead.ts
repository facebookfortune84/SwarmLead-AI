/**
 * Lead type definitions used across the frontend
 * File: frontend/src/types/lead.ts
 */

export interface Lead {
  id: string
  email: string
  name: string | null
  company: string | null
  status: string
  metadata: Record<string, unknown> | null
  created_at: string
}

export type LeadId = Lead['id']
export type Leads = Lead[]
