const { get } = require('../../services/request');
const { ensureLogin } = require('../../services/auth');
const config = require('../../config');

Page({
  data: {
    merchant: null,
    packages: [],
    loading: true,
  },
  async onLoad() {
    try { await ensureLogin(); } catch (e) { /* 未登录也可浏览 */ }
    this.loadData();
  },

  async loadData() {
    try {
      const app = getApp();
      // 单商户模式：按 MERCHANT_CODE 拉取本商家配置与套餐
      const data = await get('/public/config', { code: config.MERCHANT_CODE }, false);
      this.setData({
        merchant: data.merchant,
        packages: data.packages || [],
        loading: false,
      });
      // 同步全局商家信息
      if (data.merchant) {
        app.globalData.merchant = data.merchant;
        app.globalData.stores = data.stores || [];
        wx.setNavigationBarTitle({ title: data.merchant.name });
      }
    } catch (e) {
      this.setData({ loading: false });
      wx.showToast({ title: e.message || '加载失败', icon: 'none' });
    }
  },

  goDetail(e) {
    const id = e.detail.id;
    wx.navigateTo({ url: '/pages/package-detail/package-detail?id=' + id });
  },
});
