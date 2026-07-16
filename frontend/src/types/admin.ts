import { User } from "./user";

export type UserListResponse =
  User[];

export interface AdminUserAction {
  message: string;
}