export type UserRole =
  | "user"
  | "admin"
  | "superadmin";

export interface User {
  id: string;

  email: string;

  full_name: string;

  role: UserRole;

  subscription_tier: string;

  created_at: string;

  updated_at: string;

  is_active: boolean;
}