const { get } = require('../../services/request');
const { ensureLogin } = require('../../services/auth');
const { formatMoney } = require('../../utils/format');

Page({
  data: { order: null, codes: [], total_yuan: '0.00', pickupText: '' },
  async onLoad(opt) {
    await ensureLogin();
    await this.load(opt.no);
  },
  async load(no) {
    try {
      const o = await get('/orders/' + no);
      let pickupText = '';
      if (o.fulfillment_type === 'self_pickup') {
        pickupText = { preparing: '备餐中', ready: '待取餐', picked_up: '已取餐' }[o.pickup_status] || '';
      }
      this.setData({
        order: o,
        codes: o.verification_codes || [],
        total_yuan: formatMoney(o.total_amount),
        pickupText,
      });
    } catch (e) {
      wx.showToast({ title: e.message || '加载失败', icon: 'none' });
    }
  },
});
