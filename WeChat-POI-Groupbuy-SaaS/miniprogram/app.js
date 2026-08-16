// 小程序入口：维护全局登录态 + 商家品牌配置。
const config = require('./config');
const { get } = require('./services/request');

App({
  globalData: {
    token: '',
    consumer: null,
    merchant: null,   // 商家品牌配置（店名/logo/电话）
    stores: [],       // 商家门店
  },
  onLaunch() {
    // 尝试从本地恢复登录态
    try {
      const token = wx.getStorageSync('token');
      if (token) {
        this.globalData.token = token;
      }
    } catch (e) {
      // 忽略
    }
    // 拉取商家配置（单商户模式：用 config.MERCHANT_CODE 定位本商家）
    this.loadMerchantConfig();
  },

  loadMerchantConfig() {
    const code = config.MERCHANT_CODE;
    if (!code) {
      console.warn('[app] 未配置 MERCHANT_CODE，小程序将无法加载商家数据');
      return;
    }
    get('/public/config', { code }, false)
      .then((data) => {
        if (data && data.merchant) {
          this.globalData.merchant = data.merchant;
          this.globalData.stores = data.stores || [];
          // 动态设置导航栏标题为商家名
          if (data.merchant.name) {
            wx.setNavigationBarTitle({ title: data.merchant.name });
          }
        }
      })
      .catch((e) => {
        console.warn('[app] 加载商家配置失败', e);
      });
  },
});
