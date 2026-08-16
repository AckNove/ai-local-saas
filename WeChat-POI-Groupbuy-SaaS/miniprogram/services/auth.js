// 登录态缓存：wx.login -> /auth/wx-login -> 保存 JWT。
const { post } = require('./request');
const { wxLogin } = require('./wechat');

async function ensureLogin() {
  const app = getApp();
  if (app.globalData.token) return app.globalData.token;
  const code = await wxLogin();
  const data = await post('/auth/wx-login', { code });
  app.globalData.token = data.token;
  app.globalData.consumer = data.user;
  try { wx.setStorageSync('token', data.token); } catch (e) { /* ignore */ }
  return data.token;
}

module.exports = { ensureLogin };
