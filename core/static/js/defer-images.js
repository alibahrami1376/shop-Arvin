/**
 * Park non-critical images as they enter the DOM (remove src), then
 * restore them on window `load` so CSS/JS finish first.
 * Keep LCP/brand images loading with data-eager.
 */
(function () {
  var EAGER = "data-eager";

  function shouldPark(img) {
    if (!(img instanceof HTMLImageElement)) return false;
    if (img.hasAttribute(EAGER)) return false;
    if (img.dataset.deferManaged === "1") return false;
    var src = img.getAttribute("src");
    if (!src || src.indexOf("data:") === 0) return false;
    return true;
  }

  function park(img) {
    if (!shouldPark(img)) return;
    img.dataset.src = img.getAttribute("src");
    img.removeAttribute("src");
    img.loading = "lazy";
    img.decoding = "async";
    try {
      img.fetchPriority = "low";
    } catch (e) {}
    img.dataset.deferManaged = "1";
  }

  function parkTree(root) {
    if (!root) return;
    if (root.nodeName === "IMG") park(root);
    if (root.querySelectorAll) {
      root.querySelectorAll("img").forEach(park);
    }
  }

  function activate(img) {
    var src = img.dataset.src;
    if (!src) return;
    img.setAttribute("src", src);
    delete img.dataset.src;
  }

  function activateAll() {
    document.querySelectorAll("img[data-src]").forEach(activate);
  }

  var observer = new MutationObserver(function (mutations) {
    for (var i = 0; i < mutations.length; i++) {
      var nodes = mutations[i].addedNodes;
      for (var j = 0; j < nodes.length; j++) {
        parkTree(nodes[j]);
      }
    }
  });

  observer.observe(document.documentElement, { childList: true, subtree: true });
  parkTree(document);

  function finish() {
    observer.disconnect();
    activateAll();
  }

  if (document.readyState === "complete") {
    finish();
  } else {
    window.addEventListener("load", finish, { once: true });
  }
})();
