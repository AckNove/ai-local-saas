// 小程序全局配置：API 基址、商家标识、Mock 开关。
// 【单商户小程序模式】每个商家一个小程序，部署时只需改这里：
//   - MERCHANT_CODE：该商家的唯一标识（在后台「商户管理」里配置）
//   - APP_ID：该商家小程序的 AppID（商家自己注册认证的）
const config = {
  API_BASE: 'http://127.0.0.1:8000/api/v1',
  MERCHANT_CODE: '',        // ★ 商家的唯一标识（填了才会自动加载该商家的品牌和套餐）
  MOCK: true,               // Mock 模式下无需真实微信凭证即可联调
  APP_ID: '',               // 商家小程序的真实 appid
};

module.exports = config;
