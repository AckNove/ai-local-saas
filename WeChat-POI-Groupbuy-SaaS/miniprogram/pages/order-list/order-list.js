const { get } = require('../../services/request');
const { ensureLogin } = require('../../services/auth');
const { formatMoney, formatTime } = require('../../utils/format');

Page({
  data: { orders: [] },
  async onShow() {
    await ensureLogin();
    await this.load();
  },
  async onPullDownRefresh() {
    await this.load();
    wx.stopPullDownRefresh();
  },
  async load() {
    try {
      const data = await get('/orders?page_size=50');
      const list = (data.list || []).map((o) => ({
        ...o,
        total_yuan: formatMoney(o.total_amount),
        created: formatTime(o.created_at),
      }));
      this.setData({ orders: list });
    } catch (e) {
      wx.showToast({ title: e.message || '加载失败', icon: 'none' });
    }
  },
  goDetail(e) {
    wx.navigateTo({ url: '/pages/order-detail/order-detail?no=' + e.currentTarget.dataset.no });
  },
});
