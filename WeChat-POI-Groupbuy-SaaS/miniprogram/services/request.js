// 封装 wx.request：注入 JWT、解析统一响应 {code, message, data}。
const config = require('../config');

function request(path, method, data, auth) {
  return new Promise((resolve, reject) => {
    const header = { 'content-type': 'application/json' };
    if (auth !== false) {
      const app = getApp();
      if (app && app.globalData.token) {
        header['Authorization'] = 'Bearer ' + app.globalData.token;
      }
    }
    wx.request({
      url: config.API_BASE + path,
      method: method || 'GET',
      data: data || {},
      header: header,
      success(res) {
        const body = res.data;
        if (body && body.code === 0) {
          resolve(body.data);
        } else if (body) {
          reject(body); // {code, message, data}
        } else {
          reject({ code: 9000, message: '网络错误' });
        }
      },
      fail(err) {
        reject({ code: 9000, message: err.errMsg || '请求失败' });
      },
    });
  });
}

module.exports = {
  request,
  // GET：第二个参数为 query（对象），第三个参数为 auth
  get: (p, params, auth) => request(p, 'GET', params || null, auth),
  post: (p, d, auth) => request(p, 'POST', d, auth),
  patch: (p, d, auth) => request(p, 'PATCH', d, auth),
};
