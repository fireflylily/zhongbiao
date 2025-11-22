import { d as defineComponent, c as computed, e as createElementBlock, o as openBlock, U as normalizeClass, n as createBaseVNode, l as createCommentVNode, aM as renderSlot, t as toDisplayString, k as createBlock, w as withCtx, p as createTextVNode, g as ElButton } from "./vendor-MtO928VE.js";
/* empty css                                                                           */
import { _ as _export_sfc } from "./index.js";
const _hoisted_1 = { class: "empty-icon" };
const _hoisted_2 = {
  key: 0,
  class: "bi bi-inbox empty-icon-svg"
};
const _hoisted_3 = {
  key: 1,
  class: "bi bi-search empty-icon-svg"
};
const _hoisted_4 = {
  key: 2,
  class: "bi bi-exclamation-triangle empty-icon-svg error"
};
const _hoisted_5 = {
  key: 3,
  class: "bi bi-lock empty-icon-svg"
};
const _hoisted_6 = {
  key: 4,
  class: "bi bi-wifi-off empty-icon-svg error"
};
const _hoisted_7 = { class: "empty-description" };
const _hoisted_8 = { class: "empty-title" };
const _hoisted_9 = {
  key: 0,
  class: "empty-text"
};
const _hoisted_10 = {
  key: 0,
  class: "empty-action"
};
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "Empty",
  props: {
    type: { default: "no-data" },
    icon: { default: "bi-inbox" },
    title: { default: "" },
    description: { default: "" },
    small: { type: Boolean, default: false },
    action: { type: Boolean, default: false },
    actionText: { default: "刷新" },
    actionType: { default: "primary" },
    actionIcon: {}
  },
  emits: ["action"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const defaultTitle = computed(() => {
      const titles = {
        "no-data": "暂无数据",
        "no-search": "无搜索结果",
        "error": "加载失败",
        "no-permission": "暂无权限",
        "network-error": "网络连接失败",
        "custom": "暂无数据"
      };
      return titles[props.type];
    });
    function handleAction() {
      emit("action");
    }
    return (_ctx, _cache) => {
      const _component_el_button = ElButton;
      return openBlock(), createElementBlock("div", {
        class: normalizeClass(["empty-container", { "empty--small": __props.small }])
      }, [
        createBaseVNode("div", _hoisted_1, [
          renderSlot(_ctx.$slots, "icon", {}, () => [
            __props.type === "no-data" ? (openBlock(), createElementBlock("i", _hoisted_2)) : __props.type === "no-search" ? (openBlock(), createElementBlock("i", _hoisted_3)) : __props.type === "error" ? (openBlock(), createElementBlock("i", _hoisted_4)) : __props.type === "no-permission" ? (openBlock(), createElementBlock("i", _hoisted_5)) : __props.type === "network-error" ? (openBlock(), createElementBlock("i", _hoisted_6)) : (openBlock(), createElementBlock("i", {
              key: 5,
              class: normalizeClass([__props.icon, "empty-icon-svg"])
            }, null, 2))
          ], true)
        ]),
        createBaseVNode("div", _hoisted_7, [
          renderSlot(_ctx.$slots, "description", {}, () => [
            createBaseVNode("p", _hoisted_8, toDisplayString(__props.title || defaultTitle.value), 1),
            __props.description ? (openBlock(), createElementBlock("p", _hoisted_9, toDisplayString(__props.description), 1)) : createCommentVNode("", true)
          ], true)
        ]),
        _ctx.$slots.action || __props.action ? (openBlock(), createElementBlock("div", _hoisted_10, [
          renderSlot(_ctx.$slots, "action", {}, () => [
            __props.action ? (openBlock(), createBlock(_component_el_button, {
              key: 0,
              type: __props.actionType,
              icon: __props.actionIcon,
              onClick: handleAction
            }, {
              default: withCtx(() => [
                createTextVNode(toDisplayString(__props.actionText), 1)
              ]),
              _: 1
            }, 8, ["type", "icon"])) : createCommentVNode("", true)
          ], true)
        ])) : createCommentVNode("", true)
      ], 2);
    };
  }
});
const Empty = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-f8f8e09a"]]);
export {
  Empty as E
};
