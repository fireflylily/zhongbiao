import { d as defineComponent, c as computed, k as createBlock, o as openBlock, w as withCtx, f as createVNode, Z as ElBadge, n as createBaseVNode, e as createElementBlock, ad as ElIcon, ah as resolveDynamicComponent, h as unref, ap as loading_default, ac as normalizeStyle, U as normalizeClass, E as ElTooltip } from "./vendor-MtO928VE.js";
/* empty css                                                                           */
import { _ as _export_sfc } from "./index.js";
const _hoisted_1 = ["disabled"];
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "IconButton",
  props: {
    icon: { default: "bi-question-circle" },
    tooltip: { default: "" },
    tooltipPlacement: { default: "top" },
    type: { default: "default" },
    size: { default: "default" },
    circle: { type: Boolean, default: false },
    disabled: { type: Boolean, default: false },
    loading: { type: Boolean, default: false },
    badge: { default: "" },
    badgeMax: { default: 99 },
    badgeType: { default: "danger" }
  },
  emits: ["click"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const buttonClasses = computed(() => ({
      [`icon-button--${props.type}`]: true,
      [`icon-button--${props.size}`]: true,
      "icon-button--circle": props.circle,
      "is-disabled": props.disabled,
      "is-loading": props.loading
    }));
    const iconSize = computed(() => {
      const sizeMap = {
        large: 20,
        default: 18,
        small: 16
      };
      return sizeMap[props.size];
    });
    const iconStyle = computed(() => ({
      fontSize: `${iconSize.value}px`
    }));
    function handleClick(event) {
      if (!props.disabled && !props.loading) {
        emit("click", event);
      }
    }
    return (_ctx, _cache) => {
      const _component_el_icon = ElIcon;
      const _component_el_badge = ElBadge;
      const _component_el_tooltip = ElTooltip;
      return openBlock(), createBlock(_component_el_tooltip, {
        content: __props.tooltip,
        placement: __props.tooltipPlacement,
        disabled: !__props.tooltip
      }, {
        default: withCtx(() => [
          createVNode(_component_el_badge, {
            value: __props.badge,
            hidden: !__props.badge,
            max: __props.badgeMax,
            type: __props.badgeType
          }, {
            default: withCtx(() => [
              createBaseVNode("button", {
                class: normalizeClass(["icon-button", buttonClasses.value]),
                disabled: __props.disabled || __props.loading,
                onClick: handleClick
              }, [
                __props.loading ? (openBlock(), createBlock(_component_el_icon, {
                  key: 0,
                  class: "is-loading",
                  size: iconSize.value
                }, {
                  default: withCtx(() => [
                    (openBlock(), createBlock(resolveDynamicComponent(unref(loading_default))))
                  ]),
                  _: 1
                }, 8, ["size"])) : (openBlock(), createElementBlock("i", {
                  key: 1,
                  class: normalizeClass([__props.icon, "icon-button-icon"]),
                  style: normalizeStyle(iconStyle.value)
                }, null, 6))
              ], 10, _hoisted_1)
            ]),
            _: 1
          }, 8, ["value", "hidden", "max", "type"])
        ]),
        _: 1
      }, 8, ["content", "placement", "disabled"]);
    };
  }
});
const IconButton = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-628ec5f8"]]);
export {
  IconButton as I
};
