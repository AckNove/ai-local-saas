import axios, {
  AxiosInstance,
  AxiosError,
  InternalAxiosRequestConfig,
} from "axios";
import { toast } from "../utils/toast";

const TOKEN_KEY = "token";
const USER_KEY = "user";

/** 读取本地 token。 */
export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

/** 持久化 token。 */
export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

/** 清除登录态（token + user）。 */
export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

/** 自定义 API 错误（携带业务 code）。 */
export class ApiError extends Error {
  code: number;
  constructor(code: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.code = code;
  }
}

/**
 * axios 实例：baseURL 使用同源相对路径 /api。
 * 生产环境 FastAPI 同时托管前端与 /api，因此无需跨域。
 */
const http: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || "/api",
  timeout: 15000,
});

// 请求拦截：注入 Bearer token
http.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = getToken();
  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 响应拦截：统一解包 {code, message, data}
http.interceptors.response.use(
  (response) => {
    const body = response.data;
    // 二进制响应（如二维码 PNG）直接透传
    if (body && typeof body === "object" && "code" in body) {
      if (body.code !== 0) {
        if (body.code === 401) {
          clearToken();
          window.location.href = "/login";
          return Promise.reject(new ApiError(401, "登录已过期，请重新登录"));
        }
        toast(body.message || "请求失败", "error");
        return Promise.reject(new ApiError(body.code, body.message || "请求失败"));
      }
      return body.data;
    }
    return body;
  },
  (error: AxiosError) => {
    if (error.response) {
      const status = error.response.status;
      const body = error.response.data as { message?: string } | undefined;
      if (status === 401) {
        clearToken();
        window.location.href = "/login";
        return Promise.reject(new ApiError(401, "登录已过期，请重新登录"));
      }
      const msg = body?.message || error.message || "网络错误";
      toast(msg, "error");
      return Promise.reject(new ApiError(status, msg));
    }
    toast(error.message || "网络错误", "error");
    return Promise.reject(new ApiError(-1, error.message || "网络错误"));
  }
);

export default http;
