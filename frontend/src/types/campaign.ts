export interface Campaign {
  id: string;

  name: string;

  status:
    | "DRAFT"
    | "RUNNING"
    | "PAUSED"
    | "COMPLETED";

  lead_count: number;

  created_at?: string;
}