import { d as defineComponent, M as useRouter, e as createElementBlock, o as openBlock, n as createBaseVNode, f as createVNode, w as withCtx, p as createTextVNode, g as ElButton } from "./vendor-MtO928VE.js";
import { _ as _export_sfc } from "./index.js";
const _hoisted_1 = { class: "error-page" };
const _hoisted_2 = { class: "error-container" };
const _hoisted_3 = { class: "error-actions" };
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "NotFound",
  setup(__props) {
    const router = useRouter();
    function goHome() {
      router.push("/");
    }
    function goBack() {
      router.back();
    }
    return (_ctx, _cache) => {
      const _component_el_button = ElButton;
      return openBlock(), createElementBlock("div", _hoisted_1, [
        createBaseVNode("div", _hoisted_2, [
          _cache[2] || (_cache[2] = createBaseVNode("div", { class: "error-code" }, "404", -1)),
          _cache[3] || (_cache[3] = createBaseVNode("div", { class: "error-title" }, "页面未找到", -1)),
          _cache[4] || (_cache[4] = createBaseVNode("div", { class: "error-description" }, " 抱歉，您访问的页面不存在或已被删除 ", -1)),
          createBaseVNode("div", _hoisted_3, [
            createVNode(_component_el_button, {
              type: "primary",
              onClick: goHome
            }, {
              default: withCtx(() => [..._cache[0] || (_cache[0] = [
                createBaseVNode("i", { class: "bi bi-house-fill" }, null, -1),
                createTextVNode(" 返回首页 ", -1)
              ])]),
              _: 1
            }),
            createVNode(_component_el_button, { onClick: goBack }, {
              default: withCtx(() => [..._cache[1] || (_cache[1] = [
                createBaseVNode("i", { class: "bi bi-arrow-left" }, null, -1),
                createTextVNode(" 返回上一页 ", -1)
              ])]),
              _: 1
            })
          ])
        ]),
        _cache[5] || (_cache[5] = createBaseVNode("div", { class: "error-illustration" }, [
          createBaseVNode("i", { class: "bi bi-file-earmark-x illustration-icon" })
        ], -1))
      ]);
    };
  }
});
const NotFound = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-258309a5"]]);
export {
  NotFound as default
};
