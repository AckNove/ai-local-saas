type ToastType = "success" | "error" | "info";

interface ToastOptions {
  duration?: number;
}

/**
 * 极简 toast：向 body 追加一个浮层元素，自动消失。
 * 用于统一提示后端返回的 message（尤其 code != 0 的错误）。
 */
export function toast(message: string, type: ToastType = "info", opts: ToastOptions = {}): void {
  const duration = opts.duration ?? 3000;

  const container = document.createElement("div");
  container.style.position = "fixed";
  container.style.top = "20px";
  container.style.left = "50%";
  container.style.transform = "translateX(-50%)";
  container.style.zIndex = "9999";
  container.style.maxWidth = "90vw";

  const colorMap: Record<ToastType, string> = {
    success: "background:#16a34a;",
    error: "background:#dc2626;",
    info: "background:#0f172a;",
  };

  const el = document.createElement("div");
  el.textContent = message;
  el.style.cssText = `
    ${colorMap[type]}
    color:#fff;
    padding:10px 16px;
    border-radius:8px;
    font-size:14px;
    box-shadow:0 4px 12px rgba(0,0,0,0.15);
    margin-bottom:8px;
    opacity:0;
    transition:opacity 0.2s ease;
  `;
  container.appendChild(el);
  document.body.appendChild(container);

  // 触发进入动画
  requestAnimationFrame(() => {
    el.style.opacity = "1";
  });

  window.setTimeout(() => {
    el.style.opacity = "0";
    window.setTimeout(() => {
      if (container.parentNode) {
        container.parentNode.removeChild(container);
      }
    }, 220);
  }, duration);
}
