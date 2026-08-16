import { useCallback, useEffect, useState } from "react";
import * as authApi from "../api/auth";
import { getToken, setToken, clearToken } from "../api/http";

export interface CurrentUser {
  id: number;
  username: string;
  role: authApi.UserRole;
  merchant_id: number | null;
  status?: string;
  created_at?: string;
}

function loadUser(): CurrentUser | null {
  const raw = localStorage.getItem("user");
  if (!raw) return null;
  try {
    return JSON.parse(raw) as CurrentUser;
  } catch {
    return null;
  }
}

function saveUser(user: CurrentUser): void {
  localStorage.setItem("user", JSON.stringify(user));
}

/**
 * 登录态管理：token 读写、当前用户、登录/登出。
 * 刷新后若无内存态但本地有 token，则自动拉取 profile 恢复用户。
 */
export function useAuth() {
  const [user, setUser] = useState<CurrentUser | null>(() =>
    getToken() ? loadUser() : null
  );
  const [booting, setBooting] = useState<boolean>(false);

  // 刷新恢复：存在 token 但无 user 时拉取 profile
  useEffect(() => {
    if (getToken() && !user) {
      setBooting(true);
      authApi
        .getProfile()
        .then((p) => {
          const u: CurrentUser = {
            id: p.id,
            username: p.username,
            role: p.role as authApi.UserRole,
            merchant_id: p.merchant_id,
            status: p.status,
            created_at: p.created_at,
          };
          saveUser(u);
          setUser(u);
        })
        .catch(() => {
          clearToken();
          setUser(null);
        })
        .finally(() => setBooting(false));
    }
  }, [user]);

  const login = useCallback(async (username: string, password: string) => {
    const res = await authApi.login(username, password);
    setToken(res.token);
    const u: CurrentUser = {
      id: res.user.id,
      username: res.user.username,
      role: res.user.role,
      merchant_id: res.user.merchant_id,
    };
    saveUser(u);
    setUser(u);
    return u;
  }, []);

  const logout = useCallback(() => {
    clearToken();
    setUser(null);
  }, []);

  return {
    user,
    booting,
    token: getToken(),
    login,
    logout,
    isAuthenticated: !!getToken(),
  };
}
