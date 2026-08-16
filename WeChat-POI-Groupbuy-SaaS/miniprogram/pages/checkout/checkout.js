const { get, post } = require('../../services/request');
const { ensureLogin } = require('../../services/auth');
const { requestPayment } = require('../../services/wechat');
const { formatMoney } = require('../../utils/format');

Page({
  data: {
    pkg: null,
    type: 'dine_in',
    phone: '',
    storeId: null,
    total_yuan: '0.00',
    submitting: false,
  },
  async onLoad(opt) {
    await ensureLogin();
    const id = opt.id;
    this.data.type = opt.type || 'dine_in';
    try {
      const pkg = await get('/catalog/packages/' + id);
      this.setData({
        pkg,
        type: this.data.type,
        storeId: pkg.store_ids[0] || null,
        total_yuan: formatMoney(pkg.group_price),
      });
    } catch (e) {
      wx.showToast({ title: e.message || '加载失败', icon: 'none' });
    }
  },
  onPhone(e) {
    this.setData({ phone: e.detail.value });
  },
  async submit() {
    if (this.data.submitting) return;
    if (!this.data.storeId) {
      wx.showToast({ title: '请选择门店', icon: 'none' });
      return;
    }
    this.setData({ submitting: true });
    try {
      const r = await post('/orders', {
        package_id: this.data.pkg.id,
        store_id: this.data.storeId,
        quantity: 1,
        phone: this.data.phone,
        fulfillment_type: this.data.type,
      });
      const orderNo = r.order.order_no;
      const paid = await requestPayment(r.pay_params);
      if (paid.ok) {
        await post(`/orders/${orderNo}/pay-notify`);
        wx.redirectTo({ url: '/pages/order-detail/order-detail?no=' + orderNo });
      } else {
        wx.showToast({ title: '支付失败', icon: 'none' });
      }
    } catch (e) {
      wx.showToast({ title: e.message || '下单失败', icon: 'none' });
    } finally {
      this.setData({ submitting: false });
    }
  },
});
