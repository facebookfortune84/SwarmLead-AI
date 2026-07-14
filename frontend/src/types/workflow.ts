export interface Workflow {
  id: string;

  name: string;

  description?: string;

  status:
    | "ACTIVE"
    | "PAUSED"
    | "DRAFT";

  created_at?: string;
}