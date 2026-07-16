export interface OutreachPayload {
  email: string;

  subject: string;

  body: string;
}

export interface CampaignPayload {
  recipients: string[];

  subject: string;

  body: string;

  from_name?: string;
}