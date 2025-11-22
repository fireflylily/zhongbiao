import { d as defineComponent, e as createElementBlock, o as openBlock, f as createVNode, w as withCtx, h as unref } from "./vendor-MtO928VE.js";
/* empty css                                                                           */
import { E as Empty } from "./Empty-B61dCWeQ.js";
import { C as Card } from "./Card-jLaN2c6R.js";
/* empty css                                                                         */
import { _ as _export_sfc } from "./index.js";
const _hoisted_1 = { class: "tender-processing" };
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "Processing",
  setup(__props) {
    return (_ctx, _cache) => {
      return openBlock(), createElementBlock("div", _hoisted_1, [
        createVNode(unref(Card), { title: "处理流程" }, {
          default: withCtx(() => [
            createVNode(unref(Empty), {
              type: "no-data",
              description: "请上传招标文档开始处理..."
            })
          ]),
          _: 1
        })
      ]);
    };
  }
});
const Processing = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-9ab75094"]]);
export {
  Processing as default
};
