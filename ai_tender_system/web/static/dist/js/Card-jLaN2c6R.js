import { d as defineComponent, r as ref, e as createElementBlock, o as openBlock, U as normalizeClass, l as createCommentVNode, f as createVNode, n as createBaseVNode, aM as renderSlot, R as withModifiers, ad as ElIcon, w as withCtx, k as createBlock, ah as resolveDynamicComponent, h as unref, ap as loading_default, af as Transition, aa as withDirectives, ab as vShow, t as toDisplayString } from "./vendor-MtO928VE.js";
/* empty css                                                                           */
import { _ as _export_sfc } from "./index.js";
const _hoisted_1 = { class: "header-content" };
const _hoisted_2 = { class: "header-title" };
const _hoisted_3 = { class: "title-text" };
const _hoisted_4 = {
  key: 0,
  class: "title-description"
};
const _hoisted_5 = {
  key: 1,
  class: "card-loading"
};
const _hoisted_6 = {
  key: 2,
  class: "card-footer"
};
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "Card",
  props: {
    title: { default: "" },
    description: { default: "" },
    shadow: { default: "hover" },
    hover: { type: Boolean, default: false },
    loading: { type: Boolean, default: false },
    collapsible: { type: Boolean, default: false },
    defaultCollapsed: { type: Boolean, default: false },
    bodyPadding: { default: "20px" }
  },
  emits: ["collapse"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const collapsed = ref(props.defaultCollapsed);
    const bodyStyle = {
      padding: props.bodyPadding
    };
    function handleHeaderClick() {
      if (props.collapsible) {
        collapsed.value = !collapsed.value;
        emit("collapse", collapsed.value);
      }
    }
    return (_ctx, _cache) => {
      const _component_el_icon = ElIcon;
      return openBlock(), createElementBlock("div", {
        class: normalizeClass(["card", {
          "card--shadow": __props.shadow,
          "card--hover": __props.hover,
          "card--collapsed": collapsed.value,
          "card--loading": __props.loading
        }])
      }, [
        _ctx.$slots.header || __props.title ? (openBlock(), createElementBlock("div", {
          key: 0,
          class: normalizeClass(["card-header", { "is-collapsible": __props.collapsible }]),
          onClick: handleHeaderClick
        }, [
          createBaseVNode("div", _hoisted_1, [
            __props.collapsible ? (openBlock(), createElementBlock("i", {
              key: 0,
              class: normalizeClass(["bi collapse-icon", collapsed.value ? "bi-chevron-right" : "bi-chevron-down"])
            }, null, 2)) : createCommentVNode("", true),
            createBaseVNode("div", _hoisted_2, [
              renderSlot(_ctx.$slots, "header", {}, () => [
                createBaseVNode("h3", _hoisted_3, toDisplayString(__props.title), 1),
                __props.description ? (openBlock(), createElementBlock("p", _hoisted_4, toDisplayString(__props.description), 1)) : createCommentVNode("", true)
              ], true)
            ])
          ]),
          _ctx.$slots.actions ? (openBlock(), createElementBlock("div", {
            key: 0,
            class: "header-actions",
            onClick: _cache[0] || (_cache[0] = withModifiers(() => {
            }, ["stop"]))
          }, [
            renderSlot(_ctx.$slots, "actions", {}, void 0, true)
          ])) : createCommentVNode("", true)
        ], 2)) : createCommentVNode("", true),
        __props.loading ? (openBlock(), createElementBlock("div", _hoisted_5, [
          createVNode(_component_el_icon, {
            class: "is-loading",
            size: 24
          }, {
            default: withCtx(() => [
              (openBlock(), createBlock(resolveDynamicComponent(unref(loading_default))))
            ]),
            _: 1
          })
        ])) : createCommentVNode("", true),
        createVNode(Transition, { name: "card-collapse" }, {
          default: withCtx(() => [
            withDirectives(createBaseVNode("div", {
              class: "card-body",
              style: bodyStyle
            }, [
              renderSlot(_ctx.$slots, "default", {}, void 0, true)
            ], 512), [
              [vShow, !collapsed.value]
            ])
          ]),
          _: 3
        }),
        _ctx.$slots.footer ? (openBlock(), createElementBlock("div", _hoisted_6, [
          renderSlot(_ctx.$slots, "footer", {}, void 0, true)
        ])) : createCommentVNode("", true)
      ], 2);
    };
  }
});
const Card = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-2126c24c"]]);
export {
  Card as C
};
