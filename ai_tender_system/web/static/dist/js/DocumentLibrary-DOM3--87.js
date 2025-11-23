import { d as defineComponent, e as createElementBlock, o as openBlock, f as createVNode, w as withCtx, h as unref } from "./vendor-_9UVkM6-.js";
/* empty css                                                                           */
import { E as Empty } from "./Empty-Cafyq6jd.js";
import { C as Card } from "./Card-C-BxBgcH.js";
/* empty css                                                                         */
import { _ as _export_sfc } from "./index.js";
const _hoisted_1 = { class: "document-library" };
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "DocumentLibrary",
  setup(__props) {
    return (_ctx, _cache) => {
      return openBlock(), createElementBlock("div", _hoisted_1, [
        createVNode(unref(Card), { title: "文档列表" }, {
          default: withCtx(() => [
            createVNode(unref(Empty), {
              type: "no-data",
              description: "暂无文档数据"
            })
          ]),
          _: 1
        })
      ]);
    };
  }
});
const DocumentLibrary = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-aff08ef0"]]);
export {
  DocumentLibrary as default
};
