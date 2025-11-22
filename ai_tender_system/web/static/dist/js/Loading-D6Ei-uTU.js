import { d as defineComponent, c as computed, e as createElementBlock, l as createCommentVNode, o as openBlock, ac as normalizeStyle, U as normalizeClass, n as createBaseVNode, k as createBlock, w as withCtx, ah as resolveDynamicComponent, h as unref, ap as loading_default, ad as ElIcon, t as toDisplayString, f as createVNode, aL as ElProgress } from "./vendor-MtO928VE.js";
/* empty css                                                                           */
import { _ as _export_sfc } from "./index.js";
const _hoisted_1 = { class: "loading-content" };
const _hoisted_2 = {
  key: 0,
  class: "loading-spinner"
};
const _hoisted_3 = {
  key: 1,
  class: "loading-dots"
};
const _hoisted_4 = {
  key: 2,
  class: "loading-pulse"
};
const _hoisted_5 = {
  key: 3,
  class: "loading-bars"
};
const _hoisted_6 = {
  key: 5,
  class: "loading-text"
};
const _hoisted_7 = {
  key: 6,
  class: "loading-progress"
};
const _hoisted_8 = { class: "progress-text" };
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "Loading",
  props: {
    visible: { type: Boolean, default: true },
    fullscreen: { type: Boolean, default: true },
    type: { default: "spinner" },
    text: { default: "加载中..." },
    iconSize: { default: 48 },
    background: { default: "#ffffff" },
    opacity: { default: 0.9 },
    showProgress: { type: Boolean, default: false },
    progress: {},
    progressColor: { default: "#4a89dc" }
  },
  setup(__props) {
    const props = __props;
    const containerStyle = computed(() => {
      if (props.fullscreen) {
        return {
          backgroundColor: `rgba(255, 255, 255, ${props.opacity})`
        };
      }
      return {
        backgroundColor: props.background
      };
    });
    return (_ctx, _cache) => {
      const _component_el_icon = ElIcon;
      const _component_el_progress = ElProgress;
      return __props.visible ? (openBlock(), createElementBlock("div", {
        key: 0,
        class: normalizeClass(["loading-container", {
          "loading--fullscreen": __props.fullscreen,
          "loading--inline": !__props.fullscreen,
          [`loading--${__props.type}`]: true
        }]),
        style: normalizeStyle(containerStyle.value)
      }, [
        createBaseVNode("div", _hoisted_1, [
          __props.type === "spinner" ? (openBlock(), createElementBlock("div", _hoisted_2, [..._cache[0] || (_cache[0] = [
            createBaseVNode("div", { class: "spinner-circle" }, null, -1)
          ])])) : __props.type === "dots" ? (openBlock(), createElementBlock("div", _hoisted_3, [..._cache[1] || (_cache[1] = [
            createBaseVNode("span", { class: "dot" }, null, -1),
            createBaseVNode("span", { class: "dot" }, null, -1),
            createBaseVNode("span", { class: "dot" }, null, -1)
          ])])) : __props.type === "pulse" ? (openBlock(), createElementBlock("div", _hoisted_4, [..._cache[2] || (_cache[2] = [
            createBaseVNode("div", { class: "pulse-ring" }, null, -1)
          ])])) : __props.type === "bars" ? (openBlock(), createElementBlock("div", _hoisted_5, [..._cache[3] || (_cache[3] = [
            createBaseVNode("span", { class: "bar" }, null, -1),
            createBaseVNode("span", { class: "bar" }, null, -1),
            createBaseVNode("span", { class: "bar" }, null, -1),
            createBaseVNode("span", { class: "bar" }, null, -1)
          ])])) : (openBlock(), createBlock(_component_el_icon, {
            key: 4,
            class: "loading-icon is-loading",
            size: __props.iconSize
          }, {
            default: withCtx(() => [
              (openBlock(), createBlock(resolveDynamicComponent(unref(loading_default))))
            ]),
            _: 1
          }, 8, ["size"])),
          __props.text ? (openBlock(), createElementBlock("p", _hoisted_6, toDisplayString(__props.text), 1)) : createCommentVNode("", true),
          __props.showProgress && __props.progress !== void 0 ? (openBlock(), createElementBlock("div", _hoisted_7, [
            createVNode(_component_el_progress, {
              percentage: __props.progress,
              "show-text": false,
              "stroke-width": 3,
              color: __props.progressColor
            }, null, 8, ["percentage", "color"]),
            createBaseVNode("span", _hoisted_8, toDisplayString(__props.progress) + "%", 1)
          ])) : createCommentVNode("", true)
        ])
      ], 6)) : createCommentVNode("", true);
    };
  }
});
const Loading = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-f2bc700a"]]);
export {
  Loading as L
};
