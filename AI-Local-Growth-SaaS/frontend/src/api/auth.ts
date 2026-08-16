import http from "./http";

export type UserRole = "admin" | "merchant" | "agent";

export interface LoginUser {
  id: number;
  username: string;
  role: UserRole;
  merchant_id: number | null;
}

export interface LoginResult {
  token: string;
  token_type: string;
  user: LoginUser;
}

export interface Profile {
  id: number;
  username: string;
  role: string;
  merchant_id: number | null;
  status: string;
  created_at: string;
}

export function login(username: string, password: string): Promise<LoginResult> {
  return http.post("/auth/login", { username, password }) as Promise<LoginResult>;
}

export function getProfile(): Promise<Profile> {
  return http.get("/user/profile") as Promise<Profile>;
}

export function changePassword(oldPassword: string, newPassword: string): Promise<{ changed: boolean }> {
  return http.post("/user/change-password", { old_password: oldPassword, new_password: newPassword }) as Promise<{ changed: boolean }>;
}
