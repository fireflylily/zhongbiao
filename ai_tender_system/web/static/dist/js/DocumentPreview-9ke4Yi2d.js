import { d as defineComponent, r as ref, c as computed, D as watch, k as createBlock, o as openBlock, w as withCtx, aa as withDirectives, e as createElementBlock, l as createCommentVNode, m as ElAlert, f as createVNode, h as unref, aI as mC, aJ as vLoading, j as ElDialog, aK as nextTick, A as ElMessage } from "./vendor-MtO928VE.js";
/* empty css                                                                         */
import { _ as _export_sfc } from "./index.js";
const _hoisted_1 = {
  "element-loading-text": "正在加载文档...",
  class: "preview-container"
};
const _hoisted_2 = {
  key: 1,
  class: "editor-preview-wrapper"
};
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "DocumentPreview",
  props: {
    modelValue: { type: Boolean, default: false },
    fileUrl: { default: "" },
    fileName: { default: "文档预览" },
    htmlContent: { default: "" }
  },
  emits: ["update:modelValue"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const loading = ref(false);
    const error = ref("");
    const previewContent = ref("");
    const editorRef = ref(null);
    const dialogVisible = computed({
      get: () => props.modelValue,
      set: (value) => emit("update:modelValue", value)
    });
    const dialogTitle = computed(() => {
      return `文档预览 - ${props.fileName || "未命名文档"}`;
    });
    const loadDocument = async () => {
      if (props.htmlContent) {
        console.log("[DocumentPreview] 使用HTML内容预览");
        previewContent.value = props.htmlContent;
        return;
      }
      if (!props.fileUrl) {
        error.value = "文档地址不能为空";
        return;
      }
      loading.value = true;
      error.value = "";
      try {
        console.log("[DocumentPreview] 开始加载文档:", props.fileUrl);
        const response = await fetch("/api/editor/convert-word-to-html", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ file_path: props.fileUrl })
        });
        const result = await response.json();
        if (result.success && result.html_content) {
          previewContent.value = result.html_content;
          console.log("[DocumentPreview] Word转HTML成功，长度:", result.html_content.length);
        } else {
          throw new Error(result.error || "Word转HTML失败");
        }
        console.log("[DocumentPreview] 文档渲染成功");
      } catch (err) {
        console.error("[DocumentPreview] 文档预览失败:", err);
        error.value = `文档预览失败: ${err.message || "未知错误"}`;
        ElMessage.error("文档预览失败，请检查文件是否正确或尝试下载后查看");
      } finally {
        loading.value = false;
      }
    };
    const handleEditorCreated = () => {
      console.log("[DocumentPreview] 编辑器已创建，设置内容...");
      if (editorRef.value && previewContent.value) {
        setTimeout(() => {
          if (typeof editorRef.value.setContent === "function") {
            editorRef.value.setContent(previewContent.value);
            console.log("[DocumentPreview] 内容已设置，长度:", previewContent.value.length);
          } else {
            console.error("[DocumentPreview] setContent方法不可用");
          }
        }, 300);
      }
    };
    const handleClose = () => {
      dialogVisible.value = false;
    };
    watch(
      () => props.modelValue,
      async (newValue) => {
        if (newValue && (props.fileUrl || props.htmlContent)) {
          await nextTick();
          loadDocument();
        } else {
          error.value = "";
          previewContent.value = "";
        }
      }
    );
    return (_ctx, _cache) => {
      const _component_el_alert = ElAlert;
      const _component_el_dialog = ElDialog;
      const _directive_loading = vLoading;
      return openBlock(), createBlock(_component_el_dialog, {
        modelValue: dialogVisible.value,
        "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => dialogVisible.value = $event),
        title: dialogTitle.value,
        width: "90%",
        "before-close": handleClose,
        "destroy-on-close": "",
        class: "document-preview-dialog"
      }, {
        default: withCtx(() => [
          withDirectives((openBlock(), createElementBlock("div", _hoisted_1, [
            error.value ? (openBlock(), createBlock(_component_el_alert, {
              key: 0,
              type: "error",
              title: error.value,
              closable: false,
              "show-icon": "",
              style: { "margin-bottom": "20px" }
            }, null, 8, ["title"])) : createCommentVNode("", true),
            !error.value && previewContent.value ? (openBlock(), createElementBlock("div", _hoisted_2, [
              createVNode(unref(mC), {
                ref_key: "editorRef",
                ref: editorRef,
                document: { readOnly: true },
                onCreated: handleEditorCreated
              }, null, 512)
            ])) : createCommentVNode("", true)
          ])), [
            [_directive_loading, loading.value]
          ])
        ]),
        _: 1
      }, 8, ["modelValue", "title"]);
    };
  }
});
const DocumentPreview = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-62c282b6"]]);
export {
  DocumentPreview as D
};
