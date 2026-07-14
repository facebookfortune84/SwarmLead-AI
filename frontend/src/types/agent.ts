export type AgentType =
  | "DISCOVERY"
  | "QUALIFICATION"
  | "OUTREACH"
  | "VOICE";

export interface Agent {
  id: string;

  name: string;

  type: AgentType;

  status:
    | "READY"
    | "RUNNING"
    | "PAUSED";
}