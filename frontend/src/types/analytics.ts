export interface DailyOutreachMetric {
  date: string;

  sent: number;

  delivered: number;

  opened: number;

  replied: number;
}

export interface DailyOutreachResponse
  extends Array<
    DailyOutreachMetric
  > {}

export interface AnalyticsSummary {
  totalSent: number;

  totalDelivered: number;

  totalOpened: number;

  totalReplies: number;

  averageOpenRate: number;

  averageReplyRate: number;
}