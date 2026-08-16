const { get, post } = require('../../services/request');
const { scanCode } = require('../../services/wechat');
const { formatTime } = require('../../utils/format');

Page({
  data: {
    needLogin: true,
    username: '',
    password: '',
    code: '',
    result: null,
    today: [],
  },
  onLoad() {
    const app = getApp();
    if (
      app.globalData.token &&
      app.globalData.consumer &&
      app.globalData.consumer.role === 'verifier'
    ) {
      this.setData({ needLogin: false });
      this.loadToday();
    }
  },
  onInput(e) {
    this.setData({ [e.currentTarget.dataset.k]: e.detail.value });
  },
  async doLogin() {
    try {
      const data = await post('/auth/web-login', {
        username: this.data.username,
        password: this.data.password,
      });
      const app = getApp();
      app.globalData.token = data.token;
      app.globalData.consumer = data.user;
      wx.setStorageSync('token', data.token);
      this.setData({ needLogin: false });
      this.loadToday();
    } catch (e) {
      wx.showToast({ title: e.message || '登录失败', icon: 'none' });
    }
  },
  async loadToday() {
    try {
      const d = await get('/verify/today');
      const list = (d.list || []).map((t) => ({ ...t, at: formatTime(t.verified_at) }));
      this.setData({ today: list });
    } catch (e) { /* ignore */ }
  },
  async scan() {
    const code = await scanCode();
    this.setData({ code });
    await this.verify(code);
  },
  async verify(code) {
    code = code || this.data.code;
    if (!code) return;
    try {
      const d = await post('/verify', { code });
      this.setData({ result: { ok: true, msg: '核销成功', order_no: d.order_no } });
      this.loadToday();
    } catch (e) {
      this.setData({ result: { ok: false, msg: e.message || '核销失败' } });
    }
  },
});
