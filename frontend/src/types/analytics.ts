export interface DailyOutreachMetric {
  date: string;

  sent: number;

  delivered: number;

  opened: number;

  replied: number;
}

export type DailyOutreachResponse =
  DailyOutreachMetric[];

export interface AnalyticsSummary {
  totalSent: number;

  totalDelivered: number;

  totalOpened: number;

  totalReplies: number;

  averageOpenRate: number;

  averageReplyRate: number;
}