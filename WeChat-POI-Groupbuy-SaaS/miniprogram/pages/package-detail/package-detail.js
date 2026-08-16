const { get } = require('../../services/request');
const { formatMoney } = require('../../utils/format');

Page({
  data: {
    pkg: null,
    group_price_yuan: '0.00',
    original_price_yuan: '0.00',
    validText: '',
  },
  async onLoad(opt) {
    const id = opt.id;
    try {
      const pkg = await get('/catalog/packages/' + id);
      this.setData({
        pkg,
        group_price_yuan: formatMoney(pkg.group_price),
        original_price_yuan: formatMoney(pkg.original_price),
        validText: (pkg.valid_from || '').slice(0, 10) + ' ~ ' + (pkg.valid_to || '').slice(0, 10),
      });
    } catch (e) {
      wx.showToast({ title: e.message || '加载失败', icon: 'none' });
    }
  },
  buy(e) {
    const type = e.currentTarget.dataset.type;
    if (type === 'reservation') {
      const sid = this.data.pkg.store_ids[0];
      wx.navigateTo({ url: `/pages/reservation/reservation?store_id=${sid}` });
      return;
    }
    wx.navigateTo({ url: `/pages/checkout/checkout?id=${this.data.pkg.id}&type=${type}` });
  },
});
