/**
 * Admin product images: live preview + optional Cropper.js crop
 * (original file inputs stay intact; crop blobs go to hidden crop fields).
 */
(function () {
  function fileToURL(file) {
    return file ? URL.createObjectURL(file) : "";
  }

  function initPreview(input, imgEl, emptyEl) {
    if (!input || !imgEl) return;
    input.addEventListener("change", function () {
      var file = input.files && input.files[0];
      if (!file) return;
      var url = fileToURL(file);
      imgEl.src = url;
      imgEl.hidden = false;
      if (emptyEl) emptyEl.hidden = true;
    });
  }

  function bindCropper(opts) {
    var sourceInput = document.querySelector(opts.sourceSelector);
    var cropInput = document.querySelector(opts.cropSelector);
    var stage = document.querySelector(opts.stageSelector);
    var img = document.querySelector(opts.imgSelector);
    var applyBtn = document.querySelector(opts.applySelector);
    var resetBtn = document.querySelector(opts.resetSelector);
    var statusEl = document.querySelector(opts.statusSelector);
    var previewImg = document.querySelector(opts.previewSelector);
    var previewEmpty = document.querySelector(opts.previewEmptySelector);
    var cropper = null;

    if (!sourceInput || !cropInput || !stage || !img || typeof Cropper === "undefined") {
      return;
    }

    function destroyCropper() {
      if (cropper) {
        cropper.destroy();
        cropper = null;
      }
    }

    function setStatus(text) {
      if (statusEl) statusEl.textContent = text || "";
    }

    sourceInput.addEventListener("change", function () {
      var file = sourceInput.files && sourceInput.files[0];
      destroyCropper();
      cropInput.value = "";
      if (!file) {
        stage.hidden = true;
        setStatus("");
        return;
      }
      var url = fileToURL(file);
      img.src = url;
      stage.hidden = false;
      setStatus("محدوده برش را انتخاب کنید (اختیاری)، سپس «اعمال برش» را بزنید.");
      cropper = new Cropper(img, {
        aspectRatio: opts.aspectRatio,
        viewMode: 1,
        autoCropArea: 0.9,
        background: false,
        responsive: true,
      });
      if (previewImg) {
        previewImg.src = url;
        previewImg.hidden = false;
      }
      if (previewEmpty) previewEmpty.hidden = true;
    });

    if (applyBtn) {
      applyBtn.addEventListener("click", function () {
        if (!cropper) return;
        var canvas = cropper.getCroppedCanvas({
          width: opts.outputWidth,
          height: opts.outputHeight,
          imageSmoothingEnabled: true,
          imageSmoothingQuality: "high",
        });
        if (!canvas) return;
        canvas.toBlob(
          function (blob) {
            if (!blob) return;
            var croppedName = "crop-" + (opts.name || "image") + ".jpg";
            var croppedFile = new File([blob], croppedName, { type: "image/jpeg" });
            var dt = new DataTransfer();
            dt.items.add(croppedFile);
            cropInput.files = dt.files;
            var previewURL = URL.createObjectURL(blob);
            if (previewImg) {
              previewImg.src = previewURL;
              previewImg.hidden = false;
            }
            if (previewEmpty) previewEmpty.hidden = true;
            setStatus("برش اعمال شد. فایل اصلی جداگانه ذخیره می‌شود.");
          },
          "image/jpeg",
          0.92
        );
      });
    }

    if (resetBtn) {
      resetBtn.addEventListener("click", function () {
        cropInput.value = "";
        if (cropper) cropper.reset();
        var file = sourceInput.files && sourceInput.files[0];
        if (file && previewImg) {
          previewImg.src = fileToURL(file);
        }
        setStatus("برش لغو شد؛ در صورت ذخیره، از فایل اصلی استفاده می‌شود.");
      });
    }
  }

  function initGallerySort() {
    var list = document.getElementById("js-gallery-sort-list");
    var form = document.getElementById("js-gallery-reorder-form");
    var idsInput = document.getElementById("js-gallery-image-ids");
    if (!list || !form || !idsInput) return;

    var dragEl = null;
    list.querySelectorAll(".js-gallery-item").forEach(function (item) {
      item.setAttribute("draggable", "true");
      item.addEventListener("dragstart", function (e) {
        dragEl = item;
        item.classList.add("is-dragging");
        e.dataTransfer.effectAllowed = "move";
      });
      item.addEventListener("dragend", function () {
        item.classList.remove("is-dragging");
        dragEl = null;
      });
      item.addEventListener("dragover", function (e) {
        e.preventDefault();
        var target = e.currentTarget;
        if (!dragEl || dragEl === target) return;
        var rect = target.getBoundingClientRect();
        var before = e.clientY < rect.top + rect.height / 2;
        list.insertBefore(dragEl, before ? target : target.nextSibling);
      });
    });

    form.addEventListener("submit", function () {
      var ids = Array.prototype.map.call(
        list.querySelectorAll(".js-gallery-item"),
        function (el) {
          return el.getAttribute("data-id");
        }
      );
      idsInput.value = ids.join(",");
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    initPreview(
      document.getElementById("id_image"),
      document.getElementById("js-preview-detail-img"),
      document.getElementById("js-preview-detail-empty")
    );
    initPreview(
      document.getElementById("id_card_image"),
      document.getElementById("js-preview-card-img"),
      document.getElementById("js-preview-card-empty")
    );

    bindCropper({
      sourceSelector: "#id_image",
      cropSelector: "#id_image_crop",
      stageSelector: "#js-crop-detail-stage",
      imgSelector: "#js-crop-detail-img",
      applySelector: "#js-crop-detail-apply",
      resetSelector: "#js-crop-detail-reset",
      statusSelector: "#js-crop-detail-status",
      previewSelector: "#js-preview-detail-img",
      previewEmptySelector: "#js-preview-detail-empty",
      aspectRatio: 3 / 4,
      outputWidth: 1080,
      outputHeight: 1440,
      name: "detail",
    });

    bindCropper({
      sourceSelector: "#id_card_image",
      cropSelector: "#id_card_image_crop",
      stageSelector: "#js-crop-card-stage",
      imgSelector: "#js-crop-card-img",
      applySelector: "#js-crop-card-apply",
      resetSelector: "#js-crop-card-reset",
      statusSelector: "#js-crop-card-status",
      previewSelector: "#js-preview-card-img",
      previewEmptySelector: "#js-preview-card-empty",
      aspectRatio: 3 / 4,
      outputWidth: 1080,
      outputHeight: 1440,
      name: "card",
    });

    initGallerySort();
  });
})();
