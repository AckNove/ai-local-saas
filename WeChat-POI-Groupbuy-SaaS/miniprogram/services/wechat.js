// 微信能力 Provider：Mock / Real 切换（登录 / 支付 / 扫码）。
const config = require('../config');

function wxLogin() {
  return new Promise((resolve) => {
    if (config.MOCK) {
      resolve('mock_code_' + Date.now());
      return;
    }
    wx.login({ success: (r) => resolve(r.code), fail: () => resolve('') });
  });
}

function requestPayment(payParams) {
  return new Promise((resolve) => {
    if (config.MOCK) {
      // Mock：直接视为支付成功
      resolve({ ok: true });
      return;
    }
    wx.requestPayment({
      ...payParams,
      success: () => resolve({ ok: true }),
      fail: () => resolve({ ok: false }),
    });
  });
}

function scanCode() {
  return new Promise((resolve, reject) => {
    if (config.MOCK) {
      resolve('MOCKCODE123'); // 测试码
      return;
    }
    wx.scanCode({
      success: (r) => resolve(r.result),
      fail: (err) => reject(err),
    });
  });
}

module.exports = { wxLogin, requestPayment, scanCode };
