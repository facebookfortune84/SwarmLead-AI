export type UserRole =
  | "user"
  | "admin"
  | "superadmin";

export enum Permission {
  READ_OWN_DATA =
    "read:own_data",

  WRITE_OWN_DATA =
    "write:own_data",

  DELETE_OWN_DATA =
    "delete:own_data",

  CREATE_COMPANY =
    "create:company",

  READ_COMPANY =
    "read:company",

  UPDATE_COMPANY =
    "update:company",

  DELETE_COMPANY =
    "delete:company",

  CREATE_DEPLOYMENT =
    "create:deployment",

  READ_DEPLOYMENT =
    "read:deployment",

  UPDATE_DEPLOYMENT =
    "update:deployment",

  DELETE_DEPLOYMENT =
    "delete:deployment",

  READ_ALL_USERS =
    "read:all_users",

  UPDATE_ANY_USER =
    "update:any_user",

  DELETE_ANY_USER =
    "delete:any_user",

  READ_ALL_COMPANIES =
    "read:all_companies",

  READ_ALL_DEPLOYMENTS =
    "read:all_deployments",

  VIEW_ANALYTICS =
    "view:analytics",

  MANAGE_BILLING =
    "manage:billing",

  MANAGE_SYSTEM =
    "manage:system",
}