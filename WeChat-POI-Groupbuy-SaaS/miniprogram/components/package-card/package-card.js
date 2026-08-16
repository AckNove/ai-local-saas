Component({
  properties: {
    pkg: { type: Object, value: {} },
  },
  data: {
    group_price_yuan: '0.00',
    original_price_yuan: '0.00',
  },
  observers: {
    pkg(pkg) {
      if (!pkg) return;
      this.setData({
        group_price_yuan: (Number(pkg.group_price || 0) / 100).toFixed(2),
        original_price_yuan: (Number(pkg.original_price || 0) / 100).toFixed(2),
      });
    },
  },
  methods: {
    onTap() {
      this.triggerEvent('select', { id: this.data.pkg.id });
    },
  },
});
