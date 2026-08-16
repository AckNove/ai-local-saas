// 格式化工具：金额（分->元）/ 时间（ISO -> 本地可读）。
function formatMoney(fen) {
  const n = Number(fen || 0) / 100;
  return n.toFixed(2);
}

function formatTime(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  if (isNaN(d.getTime())) return iso;
  const pad = (x) => (x < 10 ? '0' + x : '' + x);
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

module.exports = { formatMoney, formatTime };
