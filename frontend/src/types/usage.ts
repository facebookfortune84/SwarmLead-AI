export interface UsageRecord {
  project_id?: string;

  event_type: string;

  amount?: string;

  metadata?: Record<
    string,
    unknown
  >;
}