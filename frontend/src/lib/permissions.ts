import {
  Permission,
  UserRole,
} from "@/types/rbac";

const ROLE_MAP: Record<
  UserRole,
  Permission[]
> = {
  user: [
    Permission.READ_OWN_DATA,
    Permission.WRITE_OWN_DATA,
    Permission.DELETE_OWN_DATA,

    Permission.CREATE_COMPANY,
    Permission.READ_COMPANY,
    Permission.UPDATE_COMPANY,
    Permission.DELETE_COMPANY,

    Permission.CREATE_DEPLOYMENT,
    Permission.READ_DEPLOYMENT,
    Permission.UPDATE_DEPLOYMENT,
    Permission.DELETE_DEPLOYMENT,
  ],

  admin: [
    Permission.READ_OWN_DATA,
    Permission.WRITE_OWN_DATA,
    Permission.DELETE_OWN_DATA,

    Permission.CREATE_COMPANY,
    Permission.READ_COMPANY,
    Permission.UPDATE_COMPANY,
    Permission.DELETE_COMPANY,

    Permission.CREATE_DEPLOYMENT,
    Permission.READ_DEPLOYMENT,
    Permission.UPDATE_DEPLOYMENT,
    Permission.DELETE_DEPLOYMENT,

    Permission.READ_ALL_USERS,
    Permission.READ_ALL_COMPANIES,
    Permission.READ_ALL_DEPLOYMENTS,

    Permission.VIEW_ANALYTICS,
    Permission.MANAGE_BILLING,
  ],

  superadmin:
    Object.values(
      Permission
    ) as Permission[],
};

export function hasPermission(
  role: UserRole,
  permission: Permission
): boolean {
  return ROLE_MAP[
    role
  ].includes(
    permission
  );
}