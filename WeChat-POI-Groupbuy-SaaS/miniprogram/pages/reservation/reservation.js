const { get, post } = require('../../services/request');
const { ensureLogin } = require('../../services/auth');

Page({
  data: {
    storeId: null,
    date: '2030-01-01',
    slot: '18:00-19:00',
    party: 2,
    slots: ['12:00-13:00', '18:00-19:00', '19:00-20:00', '20:00-21:00'],
  },
  async onLoad(opt) {
    await ensureLogin();
    this.setData({ storeId: Number(opt.store_id) || null });
  },
  onField(e) {
    const k = e.currentTarget.dataset.k;
    const v = k === 'party' ? Number(e.detail.value) : e.detail.value;
    this.setData({ [k]: v });
  },
  async submit() {
    try {
      await post('/fulfillment/reservations', {
        store_id: this.data.storeId,
        reserve_date: this.data.date,
        time_slot: this.data.slot,
        party_size: this.data.party,
      });
      wx.showToast({ title: '预约成功，待确认', icon: 'success' });
      setTimeout(() => wx.navigateBack(), 800);
    } catch (e) {
      wx.showToast({ title: e.message || '预约失败', icon: 'none' });
    }
  },
});
