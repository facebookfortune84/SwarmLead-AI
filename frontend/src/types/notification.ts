export interface NotificationMetadata {
  [key: string]: unknown;
}

export interface Notification {
  id: string;

  user_id: string;

  type: string;

  title: string;

  message: string;

  is_read: boolean;

  metadata: NotificationMetadata | null;

  created_at: string | null;
}

export interface NotificationResponse {
  total: number;

  skip: number;

  limit: number;

  items: Notification[];
}