import { d as defineComponent, r as ref, c as computed, a_ as k, D as watch, e as createElementBlock, o as openBlock, U as normalizeClass, f as createVNode, l as createCommentVNode, w as withCtx, n as createBaseVNode, ad as ElIcon, h as unref, ap as loading_default, as as ElCard, k as createBlock, g as ElButton, a$ as video_pause_default, p as createTextVNode, b0 as copy_document_default, aE as download_default, aG as refresh_right_default, A as ElMessage, aK as nextTick } from "./vendor-_9UVkM6-.js";
/* empty css                                                                           */
import { _ as _export_sfc } from "./index.js";
const _hoisted_1 = ["innerHTML"];
const _hoisted_2 = {
  key: 0,
  class: "streaming-indicator"
};
const _hoisted_3 = {
  key: 0,
  class: "stream-actions"
};
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "SSEStreamViewer",
  props: {
    content: {},
    isStreaming: { type: Boolean, default: false },
    enableMarkdown: { type: Boolean, default: true },
    autoScroll: { type: Boolean, default: true }
  },
  emits: ["stop", "regenerate"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const contentRef = ref(null);
    const formattedContent = computed(() => {
      if (!props.content) return "";
      if (props.enableMarkdown) {
        try {
          return k.parse(props.content);
        } catch (error) {
          console.error("Markdown 解析失败:", error);
          return props.content;
        }
      }
      return props.content.replace(/\n/g, "<br>");
    });
    watch(() => props.content, async () => {
      if (props.autoScroll && props.isStreaming) {
        await nextTick();
        scrollToBottom();
      }
    });
    const scrollToBottom = () => {
      if (contentRef.value) {
        contentRef.value.scrollTop = contentRef.value.scrollHeight;
      }
    };
    const handleCopy = async () => {
      try {
        await navigator.clipboard.writeText(props.content);
        ElMessage.success("内容已复制到剪贴板");
      } catch (error) {
        console.error("复制失败:", error);
        ElMessage.error("复制失败，请手动复制");
      }
    };
    const handleDownload = () => {
      try {
        const blob = new Blob([props.content], { type: "text/plain;charset=utf-8" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = `ai-content-${Date.now()}.txt`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        ElMessage.success("文档下载成功");
      } catch (error) {
        console.error("下载失败:", error);
        ElMessage.error("下载失败，请重试");
      }
    };
    return (_ctx, _cache) => {
      const _component_el_icon = ElIcon;
      const _component_el_card = ElCard;
      const _component_el_button = ElButton;
      return openBlock(), createElementBlock("div", {
        class: normalizeClass(["sse-stream-viewer", { "is-loading": __props.isStreaming }])
      }, [
        createVNode(_component_el_card, {
          class: "stream-content",
          shadow: "never"
        }, {
          default: withCtx(() => [
            createBaseVNode("div", {
              ref_key: "contentRef",
              ref: contentRef,
              class: "content-wrapper",
              innerHTML: formattedContent.value
            }, null, 8, _hoisted_1),
            __props.isStreaming ? (openBlock(), createElementBlock("div", _hoisted_2, [
              createVNode(_component_el_icon, { class: "is-loading" }, {
                default: withCtx(() => [
                  createVNode(unref(loading_default))
                ]),
                _: 1
              }),
              _cache[2] || (_cache[2] = createBaseVNode("span", null, "正在生成中...", -1))
            ])) : createCommentVNode("", true)
          ]),
          _: 1
        }),
        __props.content ? (openBlock(), createElementBlock("div", _hoisted_3, [
          __props.isStreaming ? (openBlock(), createBlock(_component_el_button, {
            key: 0,
            type: "warning",
            icon: unref(video_pause_default),
            onClick: _cache[0] || (_cache[0] = ($event) => emit("stop"))
          }, {
            default: withCtx(() => [..._cache[3] || (_cache[3] = [
              createTextVNode(" 停止生成 ", -1)
            ])]),
            _: 1
          }, 8, ["icon"])) : (openBlock(), createBlock(_component_el_button, {
            key: 1,
            type: "primary",
            icon: unref(copy_document_default),
            onClick: handleCopy
          }, {
            default: withCtx(() => [..._cache[4] || (_cache[4] = [
              createTextVNode(" 复制内容 ", -1)
            ])]),
            _: 1
          }, 8, ["icon"])),
          !__props.isStreaming && __props.content ? (openBlock(), createBlock(_component_el_button, {
            key: 2,
            type: "success",
            icon: unref(download_default),
            onClick: handleDownload
          }, {
            default: withCtx(() => [..._cache[5] || (_cache[5] = [
              createTextVNode(" 下载文档 ", -1)
            ])]),
            _: 1
          }, 8, ["icon"])) : createCommentVNode("", true),
          !__props.isStreaming && __props.content ? (openBlock(), createBlock(_component_el_button, {
            key: 3,
            icon: unref(refresh_right_default),
            onClick: _cache[1] || (_cache[1] = ($event) => emit("regenerate"))
          }, {
            default: withCtx(() => [..._cache[6] || (_cache[6] = [
              createTextVNode(" 重新生成 ", -1)
            ])]),
            _: 1
          }, 8, ["icon"])) : createCommentVNode("", true)
        ])) : createCommentVNode("", true)
      ], 2);
    };
  }
});
const SSEStreamViewer = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-1badfff5"]]);
export {
  SSEStreamViewer as S
};
