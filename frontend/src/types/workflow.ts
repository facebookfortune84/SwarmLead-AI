export type WorkflowStatus =
  | "pending"
  | "running"
  | "paused"
  | "completed"
  | "failed";

export interface Workflow {
  id: string;

  name: string;

  status: WorkflowStatus;

  current_step?: number;

  total_steps?: number;

  retry_count?: number;

  error_message?: string | null;

  created_at?: string | null;

  updated_at?: string | null;

  completed_at?: string | null;
}

export interface WorkflowStep {
  id: string;

  step_name: string;

  step_type: string;

  status: string;

  retry_count: number;

  error_message: string | null;

  started_at: string | null;

  completed_at: string | null;
}

export interface WorkflowDetail
  extends Workflow {
  steps: WorkflowStep[];
}