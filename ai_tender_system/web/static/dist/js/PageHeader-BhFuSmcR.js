import { d as defineComponent, M as useRouter, e as createElementBlock, o as openBlock, U as normalizeClass, l as createCommentVNode, n as createBaseVNode, t as toDisplayString, aM as renderSlot, F as Fragment, V as renderList, k as createBlock, w as withCtx, p as createTextVNode, X as ElTag } from "./vendor-MtO928VE.js";
/* empty css                                                                           */
import { _ as _export_sfc } from "./index.js";
const _hoisted_1 = { class: "back-text" };
const _hoisted_2 = { class: "page-header-main" };
const _hoisted_3 = { class: "page-header-heading" };
const _hoisted_4 = { class: "heading-title" };
const _hoisted_5 = { class: "title-text" };
const _hoisted_6 = {
  key: 0,
  class: "heading-tags"
};
const _hoisted_7 = {
  key: 0,
  class: "heading-description"
};
const _hoisted_8 = { class: "description-text" };
const _hoisted_9 = {
  key: 1,
  class: "heading-extra"
};
const _hoisted_10 = {
  key: 0,
  class: "page-header-actions"
};
const _hoisted_11 = {
  key: 1,
  class: "page-header-footer"
};
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "PageHeader",
  props: {
    title: { default: "" },
    description: { default: "" },
    showBack: { type: Boolean, default: false },
    backText: { default: "返回" },
    ghost: { type: Boolean, default: false },
    tags: { default: () => [] }
  },
  emits: ["back"],
  setup(__props, { emit: __emit }) {
    const emit = __emit;
    const router = useRouter();
    function handleBack() {
      emit("back");
      if (!emit("back")) {
        router.back();
      }
    }
    return (_ctx, _cache) => {
      const _component_el_tag = ElTag;
      return openBlock(), createElementBlock("div", {
        class: normalizeClass(["page-header", { "page-header--ghost": __props.ghost }])
      }, [
        __props.showBack ? (openBlock(), createElementBlock("div", {
          key: 0,
          class: "page-header-back",
          onClick: handleBack
        }, [
          _cache[0] || (_cache[0] = createBaseVNode("i", { class: "bi bi-arrow-left back-icon" }, null, -1)),
          createBaseVNode("span", _hoisted_1, toDisplayString(__props.backText), 1)
        ])) : createCommentVNode("", true),
        createBaseVNode("div", _hoisted_2, [
          createBaseVNode("div", _hoisted_3, [
            createBaseVNode("div", _hoisted_4, [
              renderSlot(_ctx.$slots, "title", {}, () => [
                createBaseVNode("h1", _hoisted_5, toDisplayString(__props.title), 1)
              ], true),
              _ctx.$slots.tags || __props.tags ? (openBlock(), createElementBlock("div", _hoisted_6, [
                renderSlot(_ctx.$slots, "tags", {}, () => [
                  (openBlock(true), createElementBlock(Fragment, null, renderList(__props.tags, (tag, index) => {
                    return openBlock(), createBlock(_component_el_tag, {
                      key: index,
                      type: tag.type,
                      size: tag.size || "default"
                    }, {
                      default: withCtx(() => [
                        createTextVNode(toDisplayString(tag.text), 1)
                      ]),
                      _: 2
                    }, 1032, ["type", "size"]);
                  }), 128))
                ], true)
              ])) : createCommentVNode("", true)
            ]),
            _ctx.$slots.description || __props.description ? (openBlock(), createElementBlock("div", _hoisted_7, [
              renderSlot(_ctx.$slots, "description", {}, () => [
                createBaseVNode("p", _hoisted_8, toDisplayString(__props.description), 1)
              ], true)
            ])) : createCommentVNode("", true),
            _ctx.$slots.extra ? (openBlock(), createElementBlock("div", _hoisted_9, [
              renderSlot(_ctx.$slots, "extra", {}, void 0, true)
            ])) : createCommentVNode("", true)
          ]),
          _ctx.$slots.actions ? (openBlock(), createElementBlock("div", _hoisted_10, [
            renderSlot(_ctx.$slots, "actions", {}, void 0, true)
          ])) : createCommentVNode("", true)
        ]),
        _ctx.$slots.footer ? (openBlock(), createElementBlock("div", _hoisted_11, [
          renderSlot(_ctx.$slots, "footer", {}, void 0, true)
        ])) : createCommentVNode("", true)
      ], 2);
    };
  }
});
const PageHeader = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-57518d3e"]]);
export {
  PageHeader as P
};
