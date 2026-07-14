export interface Lead {
  id: string;

  email: string;

  name: string | null;

  company: string | null;

  status: string;

  metadata: Record<
    string,
    unknown
  > | null;

  created_at: string;

  agent_source?: string;

  owner?: string;

  tags?: string[];

  last_contacted?: string;
}
