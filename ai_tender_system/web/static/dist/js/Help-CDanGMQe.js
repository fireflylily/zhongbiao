import { d as defineComponent, e as createElementBlock, o as openBlock, f as createVNode, w as withCtx, h as unref } from "./vendor-MtO928VE.js";
/* empty css                                                                           */
import { E as Empty } from "./Empty-B61dCWeQ.js";
import { C as Card } from "./Card-jLaN2c6R.js";
/* empty css                                                                         */
import { _ as _export_sfc } from "./index.js";
const _hoisted_1 = { class: "help-center" };
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "Help",
  setup(__props) {
    return (_ctx, _cache) => {
      return openBlock(), createElementBlock("div", _hoisted_1, [
        createVNode(unref(Card), { title: "帮助文档" }, {
          default: withCtx(() => [
            createVNode(unref(Empty), {
              type: "no-data",
              description: "帮助文档正在编写中..."
            })
          ]),
          _: 1
        })
      ]);
    };
  }
});
const Help = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-aba8d535"]]);
export {
  Help as default
};
