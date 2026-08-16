/* 种草卡 H5 落地页逻辑：解析 slug、拉取卡片、上报互动事件、跳转目标。 */
(function () {
  "use strict";

  var API = "/api";

  /** 从路径 /c/{slug} 解析短码 */
  function getSlug() {
    var m = window.location.pathname.match(/^\/c\/([^/?#]+)\/?$/);
    return m ? m[1] : null;
  }

  /** 根据 UA 粗略判断设备类型 */
  function deviceFromUA() {
    var ua = navigator.userAgent || "";
    if (/iPhone|Android.*Mobile/i.test(ua)) return "mobile";
    if (/iPad|Tablet/i.test(ua)) return "tablet";
    return "desktop";
  }

  /** 上报互动事件（失败不影响主流程） */
  function postEvent(cardId, type) {
    try {
      fetch(API + "/seed-card/event", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        keepalive: true,
        body: JSON.stringify({
          card_id: cardId,
          event_type: type,
          device: deviceFromUA(),
          referer: document.referrer || ""
        })
      });
    } catch (e) {
      /* 忽略上报失败 */
    }
  }

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  function showError(msg) {
    var app = document.getElementById("app");
    app.innerHTML = "";
    app.appendChild(el("div", "loading", msg));
  }

  function renderCard(card) {
    var app = document.getElementById("app");
    app.innerHTML = "";

    var title = el("h1", "title", card.name || "欢迎了解我们");
    app.appendChild(title);

    // 商家信息区（店名 + 地址 + 电话），提升信任感
    if (card.merchant_name || card.store_name || card.address || card.phone) {
      var infoBox = el("div", "shop-box");
      if (card.merchant_name) {
        infoBox.appendChild(el("div", "shop-name", card.merchant_name));
      }
      if (card.store_name) {
        infoBox.appendChild(el("div", "shop-store", "📍 " + card.store_name));
      }
      var addrLine = card.address || card.store_location;
      if (addrLine) {
        infoBox.appendChild(el("div", "shop-addr", "地址：" + addrLine));
      }
      if (card.phone) {
        var phoneRow = el("div", "shop-phone", "电话：" + card.phone);
        phoneRow.addEventListener("click", function () {
          window.location.href = "tel:" + card.phone;
        });
        infoBox.appendChild(phoneRow);
      }
      app.appendChild(infoBox);
    }

    var tip = el("p", "tip", "扫码成功！点击下方按钮直达，了解更多专属内容。");
    app.appendChild(tip);

    // 跳转目标按钮
    if (card.target_url) {
      var goBtn = el("button", "btn btn-primary", goLabel(card.target_type));
      goBtn.addEventListener("click", function () {
        postEvent(card.id, "click");
        window.open(card.target_url, "_blank");
      });
      app.appendChild(goBtn);
    }

    // —— 好评文案区：AI 生成好评 + 一键复制 ——
    var reviewBox = el("div", "review-box");
    var reviewTitle = el("div", "review-title", "✨ 已为你准备好评，复制后到视频号/小红书粘贴即可");
    reviewBox.appendChild(reviewTitle);

    var reviewText = el("p", "review-text", "好评生成中…");
    reviewBox.appendChild(reviewText);

    var copyBtn = el("button", "btn btn-primary", "复制好评");
    copyBtn.addEventListener("click", function () {
      copyText(reviewText.textContent);
      postEvent(card.id, "comment");
      copyBtn.textContent = "已复制，去粘贴吧 ✓";
      setTimeout(function () { copyBtn.textContent = "复制好评"; }, 2000);
    });
    reviewBox.appendChild(copyBtn);

    var refreshBtn = el("button", "btn btn-ghost", "换一条好评");
    refreshBtn.addEventListener("click", function () {
      pickRandomReview(card.id);
    });
    reviewBox.appendChild(refreshBtn);

    app.appendChild(reviewBox);

    // 分享按钮
    var shareBtn = el("button", "btn btn-ghost", "分享给好友");
    shareBtn.addEventListener("click", function () {
      postEvent(card.id, "share");
      if (navigator.share) {
        navigator.share({
          title: card.name || "推荐给你",
          url: window.location.href
        }).catch(function () {});
      } else {
        copyLink();
      }
    });
    app.appendChild(shareBtn);

    // 加载好评（slug 直接从 URL 取，公开接口不返回 slug 字段）
    loadReviews(card.id, getSlug());
  }

  /** 拉取好评文案并展示第一条 */
  async function loadReviews(cardId, slug) {
    try {
      var resp = await fetch(API + "/seed-card/public/" + encodeURIComponent(slug) + "/review");
      var json = await resp.json();
      if (json && json.code === 0 && json.data && json.data.comments && json.data.comments.length) {
        window._reviews = json.data.comments;
        var reviewText = document.querySelector(".review-text");
        if (reviewText) reviewText.textContent = window._reviews[0];
      } else {
        fallbackReview();
      }
    } catch (e) {
      fallbackReview();
    }
  }

  function pickRandomReview(cardId) {
    if (window._reviews && window._reviews.length > 1) {
      var texts = window._reviews;
      var cur = document.querySelector(".review-text").textContent;
      var next = texts[0];
      for (var i = 0; i < texts.length; i++) {
        if (texts[i] !== cur) { next = texts[i]; break; }
      }
      document.querySelector(".review-text").textContent = next;
    } else {
      var box = document.querySelector(".review-text");
      if (box) box.textContent = "（暂时没有更多好评，请稍后再试）";
    }
  }

  function fallbackReview() {
    var box = document.querySelector(".review-text");
    if (box) box.textContent = "这家店真的不错，环境和体验都很好，值得推荐！";
  }

  function copyText(text) {
    var ta = document.createElement("textarea");
    ta.value = text;
    document.body.appendChild(ta);
    ta.select();
    try {
      document.execCommand("copy");
    } catch (e) {
      /* 忽略 */
    }
    document.body.removeChild(ta);
  }

  function goLabel(type) {
    if (type === "video") return "前往视频号 / 视频";
    if (type === "private") return "进入私域 / 加微信";
    return "查看详情";
  }

  function copyLink() {
    try {
      var input = document.createElement("input");
      input.value = window.location.href;
      document.body.appendChild(input);
      input.select();
      document.execCommand("copy");
      document.body.removeChild(input);
    } catch (e) {
      /* 忽略 */
    }
  }

  async function load() {
    var slug = getSlug();
    if (!slug) {
      showError("无效的访问链接");
      return;
    }
    try {
      var resp = await fetch(API + "/seed-card/public/" + encodeURIComponent(slug));
      var json = await resp.json();
      if (!json || json.code !== 0 || !json.data) {
        showError("卡片不存在或已失效");
        return;
      }
      var card = json.data;
      renderCard(card);
      // 加载即上报 scan
      postEvent(card.id, "scan");
    } catch (e) {
      showError("加载失败，请稍后重试");
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", load);
  } else {
    load();
  }
})();
