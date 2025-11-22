import { d as defineComponent, r as ref, c as computed, e as createElementBlock, o as openBlock, f as createVNode, at as ElUpload, aN as mergeProps, w as withCtx, aM as renderSlot, A as ElMessage, n as createBaseVNode, k as createBlock, l as createCommentVNode, ad as ElIcon, h as unref, ae as document_default, t as toDisplayString, aL as ElProgress, aO as circle_check_default, aP as circle_close_default, p as createTextVNode, aQ as info_filled_default, g as ElButton, aF as upload_default, aR as upload_filled_default } from "./vendor-MtO928VE.js";
import { s as smartCompressImage } from "./imageCompressor-DC3BCfPz.js";
/* empty css                                                                           */
import { _ as _export_sfc } from "./index.js";
const _hoisted_1 = { class: "document-uploader" };
const _hoisted_2 = {
  key: 1,
  class: "upload-drag-area"
};
const _hoisted_3 = {
  key: 0,
  class: "upload-hint"
};
const _hoisted_4 = {
  key: 0,
  class: "upload-tip"
};
const _hoisted_5 = { class: "upload-file-item" };
const _hoisted_6 = { class: "file-name" };
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "DocumentUploader",
  props: {
    uploadUrl: { default: "/api/upload" },
    uploadHeaders: {},
    uploadData: {},
    httpRequest: {},
    accept: { default: ".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx" },
    limit: { default: 10 },
    maxSize: { default: 50 },
    multiple: { type: Boolean, default: false },
    drag: { type: Boolean, default: false },
    showFileList: { type: Boolean, default: true },
    triggerText: { default: "选择文件" },
    tipText: { default: "" },
    modelValue: {},
    autoCompressImage: { type: Boolean, default: true },
    imageType: { default: "default" }
  },
  emits: ["update:modelValue", "success", "error", "exceed", "remove"],
  setup(__props, { expose: __expose, emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const uploadRef = ref();
    const fileList = computed({
      get: () => props.modelValue || [],
      set: (value) => emit("update:modelValue", value)
    });
    const handleBeforeUpload = async (rawFile) => {
      var _a;
      if (props.maxSize && rawFile.size / 1024 / 1024 > props.maxSize) {
        ElMessage.error(`文件大小不能超过 ${props.maxSize}MB`);
        return false;
      }
      if (props.accept) {
        const acceptTypes = props.accept.split(",").map((t) => t.trim());
        const fileExt = "." + ((_a = rawFile.name.split(".").pop()) == null ? void 0 : _a.toLowerCase());
        if (!acceptTypes.some((type) => fileExt === type.toLowerCase())) {
          ElMessage.error(`不支持的文件格式：${fileExt}`);
          return false;
        }
      }
      if (props.autoCompressImage && rawFile.type.startsWith("image/")) {
        try {
          console.log(`[DocumentUploader] 检测到图片文件，开始压缩: ${rawFile.name}, ${(rawFile.size / 1024).toFixed(0)}KB`);
          const compressedFile = await smartCompressImage(rawFile, props.imageType);
          const originalSize = rawFile.size;
          const compressedSize = compressedFile.size;
          const savings = ((originalSize - compressedSize) / originalSize * 100).toFixed(1);
          if (compressedSize < originalSize) {
            console.log(
              `[DocumentUploader] ✅ 图片已压缩: ${(originalSize / 1024).toFixed(0)}KB → ${(compressedSize / 1024).toFixed(0)}KB (节省${savings}%)`
            );
            return compressedFile;
          } else {
            console.log(`[DocumentUploader] 图片无需压缩，使用原文件`);
          }
        } catch (error) {
          console.error("[DocumentUploader] 图片压缩失败:", error);
          ElMessage.warning("图片压缩失败，将上传原文件");
        }
      }
      return true;
    };
    const handleProgress = (event, file, fileList2) => {
    };
    const handleSuccess = (response, file, fileList2) => {
      emit("success", file, fileList2);
      emit("update:modelValue", fileList2);
    };
    const handleError = (error, file, fileList2) => {
      ElMessage.error("文件上传失败：" + error.message);
      emit("error", error, file, fileList2);
    };
    const handleExceed = (files, fileList2) => {
      ElMessage.warning(`最多只能上传 ${props.limit} 个文件`);
      emit("exceed", files, fileList2);
    };
    const handleRemove = (file, fileList2) => {
      emit("remove", file, fileList2);
      emit("update:modelValue", fileList2);
    };
    const clearFiles = () => {
      var _a;
      (_a = uploadRef.value) == null ? void 0 : _a.clearFiles();
      emit("update:modelValue", []);
    };
    const submit = () => {
      var _a;
      (_a = uploadRef.value) == null ? void 0 : _a.submit();
    };
    const abort = (file) => {
      var _a;
      (_a = uploadRef.value) == null ? void 0 : _a.abort(file);
    };
    __expose({
      clearFiles,
      submit,
      abort
    });
    return (_ctx, _cache) => {
      const _component_el_button = ElButton;
      const _component_el_icon = ElIcon;
      const _component_el_progress = ElProgress;
      const _component_el_upload = ElUpload;
      return openBlock(), createElementBlock("div", _hoisted_1, [
        createVNode(_component_el_upload, mergeProps({
          ref_key: "uploadRef",
          ref: uploadRef,
          action: __props.uploadUrl,
          "http-request": __props.httpRequest,
          headers: __props.uploadHeaders,
          data: __props.uploadData,
          accept: __props.accept,
          limit: __props.limit,
          multiple: __props.multiple,
          drag: __props.drag,
          "show-file-list": __props.showFileList,
          "before-upload": handleBeforeUpload,
          "on-progress": handleProgress,
          "on-success": handleSuccess,
          "on-error": handleError,
          "on-exceed": handleExceed,
          "on-remove": handleRemove,
          "file-list": fileList.value
        }, _ctx.$attrs), {
          default: withCtx(() => [
            renderSlot(_ctx.$slots, "trigger", {}, () => [
              !__props.drag ? (openBlock(), createBlock(_component_el_button, {
                key: 0,
                type: "primary",
                icon: unref(upload_default)
              }, {
                default: withCtx(() => [
                  createTextVNode(toDisplayString(__props.triggerText), 1)
                ]),
                _: 1
              }, 8, ["icon"])) : (openBlock(), createElementBlock("div", _hoisted_2, [
                createVNode(_component_el_icon, { class: "upload-icon" }, {
                  default: withCtx(() => [
                    createVNode(unref(upload_filled_default))
                  ]),
                  _: 1
                }),
                _cache[0] || (_cache[0] = createBaseVNode("div", { class: "upload-text" }, [
                  createTextVNode(" 将文件拖到此处，或"),
                  createBaseVNode("em", null, "点击上传")
                ], -1)),
                __props.accept ? (openBlock(), createElementBlock("div", _hoisted_3, " 支持的文件格式：" + toDisplayString(__props.accept), 1)) : createCommentVNode("", true)
              ]))
            ], true)
          ]),
          tip: withCtx(() => [
            renderSlot(_ctx.$slots, "tip", {}, () => [
              __props.tipText ? (openBlock(), createElementBlock("div", _hoisted_4, [
                createVNode(_component_el_icon, null, {
                  default: withCtx(() => [
                    createVNode(unref(info_filled_default))
                  ]),
                  _: 1
                }),
                createTextVNode(" " + toDisplayString(__props.tipText), 1)
              ])) : createCommentVNode("", true)
            ], true)
          ]),
          file: withCtx(({ file }) => [
            renderSlot(_ctx.$slots, "file", { file }, () => [
              createBaseVNode("div", _hoisted_5, [
                createVNode(_component_el_icon, { class: "file-icon" }, {
                  default: withCtx(() => [
                    createVNode(unref(document_default))
                  ]),
                  _: 1
                }),
                createBaseVNode("span", _hoisted_6, toDisplayString(file.name), 1),
                file.status === "uploading" ? (openBlock(), createBlock(_component_el_progress, {
                  key: 0,
                  percentage: file.percentage,
                  "stroke-width": 2
                }, null, 8, ["percentage"])) : createCommentVNode("", true),
                file.status === "success" ? (openBlock(), createBlock(_component_el_icon, {
                  key: 1,
                  class: "status-icon success"
                }, {
                  default: withCtx(() => [
                    createVNode(unref(circle_check_default))
                  ]),
                  _: 1
                })) : createCommentVNode("", true),
                file.status === "fail" ? (openBlock(), createBlock(_component_el_icon, {
                  key: 2,
                  class: "status-icon error"
                }, {
                  default: withCtx(() => [
                    createVNode(unref(circle_close_default))
                  ]),
                  _: 1
                })) : createCommentVNode("", true)
              ])
            ], true)
          ]),
          _: 3
        }, 16, ["action", "http-request", "headers", "data", "accept", "limit", "multiple", "drag", "show-file-list", "file-list"])
      ]);
    };
  }
});
const DocumentUploader = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-ddbb8fd4"]]);
export {
  DocumentUploader as D
};
