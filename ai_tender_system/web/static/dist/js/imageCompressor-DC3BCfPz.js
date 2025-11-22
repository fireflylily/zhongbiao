const COMPRESSION_PRESETS = {
  // 营业执照：需要较高质量
  license: {
    maxWidth: 1500,
    quality: 0.8,
    mimeType: "image/jpeg"
  },
  // 资质证书：标准质量
  qualification: {
    maxWidth: 1200,
    quality: 0.75,
    mimeType: "image/jpeg"
  },
  // 身份证：可读即可
  id_card: {
    maxWidth: 1e3,
    quality: 0.7,
    mimeType: "image/jpeg"
  },
  // 公章：必须清晰
  seal: {
    maxWidth: 800,
    quality: 0.85,
    mimeType: "image/jpeg"
  },
  // 照片：标准质量
  photo: {
    maxWidth: 800,
    quality: 0.75,
    mimeType: "image/jpeg"
  },
  // 默认配置
  default: {
    maxWidth: 1200,
    quality: 0.75,
    mimeType: "image/jpeg"
  }
};
const COMPRESSION_THRESHOLDS = {
  // 文件大小阈值（小于此值不压缩）
  minFileSize: 300 * 1024,
  // 300KB
  // 尺寸阈值
  minWidth: 1200,
  minHeight: 1200,
  // PNG转JPEG阈值
  pngToJpegSize: 100 * 1024,
  // 100KB
  // 压缩效果阈值（压缩后如果只减少<10%，使用原图）
  minSavingRatio: 0.1
};
function loadImage(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      var _a;
      const img = new Image();
      img.onload = () => resolve(img);
      img.onerror = () => reject(new Error("图片加载失败"));
      img.src = (_a = e.target) == null ? void 0 : _a.result;
    };
    reader.onerror = () => reject(new Error("文件读取失败"));
    reader.readAsDataURL(file);
  });
}
function shouldCompress(file, img) {
  const { size, type } = file;
  const { width, height } = img;
  if (size < 100 * 1024) {
    console.log("[ImageCompressor] 文件<100KB，跳过压缩");
    return false;
  }
  if (size > COMPRESSION_THRESHOLDS.minFileSize) {
    console.log("[ImageCompressor] 文件大小超过阈值，需要压缩");
    return true;
  }
  if (width > COMPRESSION_THRESHOLDS.minWidth || height > COMPRESSION_THRESHOLDS.minHeight) {
    console.log("[ImageCompressor] 图片尺寸过大，需要压缩");
    return true;
  }
  if (type === "image/png" && size > COMPRESSION_THRESHOLDS.pngToJpegSize) {
    console.log("[ImageCompressor] PNG图片>100KB，转JPEG可节省空间");
    return true;
  }
  console.log("[ImageCompressor] 图片符合要求，不需要压缩");
  return false;
}
async function compressImage(file, config = COMPRESSION_PRESETS.default) {
  try {
    const img = await loadImage(file);
    console.log(`[ImageCompressor] 原始图片: ${img.width}x${img.height}, ${formatFileSize(file.size)}`);
    if (!shouldCompress(file, img)) {
      return file;
    }
    let { width, height } = img;
    const maxWidth = config.maxWidth || 1200;
    const maxHeight = config.maxHeight || maxWidth;
    if (width > maxWidth || height > maxHeight) {
      const ratio = Math.min(maxWidth / width, maxHeight / height);
      width = Math.round(width * ratio);
      height = Math.round(height * ratio);
    }
    const canvas = document.createElement("canvas");
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext("2d");
    ctx.fillStyle = "#FFFFFF";
    ctx.fillRect(0, 0, width, height);
    ctx.drawImage(img, 0, 0, width, height);
    const blob = await new Promise((resolve, reject) => {
      canvas.toBlob(
        (blob2) => {
          if (blob2) {
            resolve(blob2);
          } else {
            reject(new Error("Canvas转Blob失败"));
          }
        },
        config.mimeType || "image/jpeg",
        config.quality || 0.75
      );
    });
    const compressedFile = new File(
      [blob],
      file.name.replace(/\.(png|jpg|jpeg|gif|bmp)$/i, ".jpg"),
      // 统一扩展名为.jpg
      {
        type: config.mimeType || "image/jpeg",
        lastModified: Date.now()
      }
    );
    const savingRatio = (file.size - compressedFile.size) / file.size;
    if (savingRatio < COMPRESSION_THRESHOLDS.minSavingRatio) {
      console.log(`[ImageCompressor] 压缩效果不明显（节省${(savingRatio * 100).toFixed(1)}%），使用原图`);
      return file;
    }
    console.log(
      `[ImageCompressor] ✅ 压缩成功: ${img.width}x${img.height} → ${width}x${height}, ${formatFileSize(file.size)} → ${formatFileSize(compressedFile.size)} (节省${(savingRatio * 100).toFixed(1)}%)`
    );
    return compressedFile;
  } catch (error) {
    console.error("[ImageCompressor] 压缩失败:", error);
    return file;
  }
}
async function smartCompressImage(file, imageType = "default") {
  if (!file.type.startsWith("image/")) {
    console.warn("[ImageCompressor] 不是图片文件，跳过压缩");
    return file;
  }
  const config = COMPRESSION_PRESETS[imageType] || COMPRESSION_PRESETS.default;
  return compressImage(file, config);
}
function formatFileSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
}
export {
  smartCompressImage as s
};
