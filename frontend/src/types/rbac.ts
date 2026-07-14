export type UserRole =
  | "user"
  | "admin"
  | "superadmin";

export enum Permission {
  READ_OWN_DATA =
    "read:own_