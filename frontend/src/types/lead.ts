export type LeadStatus =
  | "NEW"
  | "CONTACTED"
  | "QUALIFIED"
  | "MEETING"
  | "PROPOSAL"
  | "CUSTOMER"
  | "LOST";

export interface Lead {
  id: string;

  email: string;

  name: string | null;

  company: string | null;

  status: LeadStatus | string;

  metadata: Record<
    string,
    unknown
  > | null;

  created_at: string;

  owner?: string | null;

  tags?: string[];

  score?: number | null;

  agent_source?: string | null;

  discovery_agent?: string | null;

  last_contacted?: string | null;

  next_action?: string | null;

  notes?: string | null;
}