import { d as defineComponent, r as ref, c as computed, S as onMounted, e as createElementBlock, o as openBlock, n as createBaseVNode, aa as withDirectives, N as createStaticVNode, f as createVNode, h as unref, aT as refresh_default, g as ElButton, bd as link_default, aJ as vLoading, l as createCommentVNode, w as withCtx, p as createTextVNode, b5 as ElResult } from "./vendor-_9UVkM6-.js";
import { _ as _export_sfc } from "./index.js";
const _hoisted_1 = { class: "user-management-wrapper" };
const _hoisted_2 = { class: "page-header" };
const _hoisted_3 = { class: "header-content" };
const _hoisted_4 = { class: "action-buttons" };
const _hoisted_5 = {
  class: "iframe-container",
  "element-loading-text": "加载中..."
};
const _hoisted_6 = ["src"];
const _hoisted_7 = {
  key: 0,
  class: "error-overlay"
};
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "UserManagement",
  setup(__props) {
    const userManagementFrame = ref(null);
    const loading = ref(true);
    const error = ref(false);
    const errorMessage = ref("");
    const iframeUrl = computed(() => {
      return "/abtest/management";
    });
    function handleIframeLoad() {
      loading.value = false;
      error.value = false;
    }
    function handleIframeError() {
      loading.value = false;
      error.value = true;
      errorMessage.value = "无法加载用户管理页面,请检查服务是否正常运行";
    }
    function refreshFrame() {
      if (userManagementFrame.value) {
        loading.value = true;
        error.value = false;
        userManagementFrame.value.src = userManagementFrame.value.src;
      }
    }
    function openInNewTab() {
      window.open(iframeUrl.value, "_blank");
    }
    onMounted(() => {
      setTimeout(() => {
        if (loading.value) {
          error.value = true;
          loading.value = false;
          errorMessage.value = "加载超时,请刷新页面重试";
        }
      }, 1e4);
    });
    return (_ctx, _cache) => {
      const _directive_loading = vLoading;
      return openBlock(), createElementBlock("div", _hoisted_1, [
        createBaseVNode("div", _hoisted_2, [
          createBaseVNode("div", _hoisted_3, [
            _cache[0] || (_cache[0] = createStaticVNode('<div class="title-section" data-v-01a77649><i class="bi-people header-icon" data-v-01a77649></i><div class="title-group" data-v-01a77649><h1 class="page-title" data-v-01a77649>用户管理</h1><p class="page-description" data-v-01a77649>管理系统用户和角色权限</p></div></div>', 1)),
            createBaseVNode("div", _hoisted_4, [
              createVNode(unref(ElButton), {
                onClick: refreshFrame,
                icon: unref(refresh_default),
                circle: "",
                title: "刷新"
              }, null, 8, ["icon"]),
              createVNode(unref(ElButton), {
                onClick: openInNewTab,
                icon: unref(link_default),
                circle: "",
                title: "在新标签页打开"
              }, null, 8, ["icon"])
            ])
          ])
        ]),
        withDirectives((openBlock(), createElementBlock("div", _hoisted_5, [
          createBaseVNode("iframe", {
            ref_key: "userManagementFrame",
            ref: userManagementFrame,
            src: iframeUrl.value,
            class: "user-management-iframe",
            frameborder: "0",
            onLoad: handleIframeLoad,
            onError: handleIframeError
          }, null, 40, _hoisted_6),
          error.value ? (openBlock(), createElementBlock("div", _hoisted_7, [
            createVNode(unref(ElResult), {
              icon: "error",
              title: "加载失败",
              "sub-title": errorMessage.value
            }, {
              extra: withCtx(() => [
                createVNode(unref(ElButton), {
                  type: "primary",
                  onClick: refreshFrame
                }, {
                  default: withCtx(() => [..._cache[1] || (_cache[1] = [
                    createTextVNode("重新加载", -1)
                  ])]),
                  _: 1
                })
              ]),
              _: 1
            }, 8, ["sub-title"])
          ])) : createCommentVNode("", true)
        ])), [
          [_directive_loading, loading.value]
        ])
      ]);
    };
  }
});
const UserManagement = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-01a77649"]]);
export {
  UserManagement as default
};
