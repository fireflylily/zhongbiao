import { d as defineComponent, M as useRouter, r as ref, c as computed, S as onMounted, T as onBeforeUnmount, e as createElementBlock, o as openBlock, U as normalizeClass, n as createBaseVNode, l as createCommentVNode, k as createBlock, f as createVNode, w as withCtx, F as Fragment, V as renderList, W as ElOption, t as toDisplayString, X as ElTag, p as createTextVNode, Y as ElSelect, E as ElTooltip, Z as ElBadge, $ as ElDropdown, a0 as ElAvatar, a1 as ElDropdownMenu, a2 as ElDropdownItem, A as ElMessage, z as ElMessageBox, u as useRoute, D as watch, a3 as ElMenu, a4 as ElMenuItem, a5 as ElSubMenu, a6 as ElDivider, a7 as ElScrollbar, a8 as ElBreadcrumbItem, a9 as ElBreadcrumb, aa as withDirectives, R as withModifiers, ab as vShow, ac as normalizeStyle, g as ElButton, ad as ElIcon, h as unref, ae as document_default, af as Transition, B as resolveComponent, ag as KeepAlive, ah as resolveDynamicComponent } from "./vendor-_9UVkM6-.js";
import { u as useUserStore, b as useNotificationStore, _ as _export_sfc, g as generateMenuFromRoutes, c as getBreadcrumbs, d as useSettingsStore } from "./index.js";
import { D as DocumentPreview } from "./DocumentPreview-kARaYjYY.js";
import { u as useProjectStore } from "./project-COt-HjGx.js";
/* empty css                                                                         */
import "./tender-DvsgeLWX.js";
const _hoisted_1$6 = { class: "navbar-left" };
const _hoisted_2$4 = ["title"];
const _hoisted_3$3 = {
  key: 0,
  class: "bi bi-lightbulb-fill brand-icon"
};
const _hoisted_4$3 = { class: "navbar-right" };
const _hoisted_5$2 = { class: "model-option" };
const _hoisted_6$2 = { class: "user-info" };
const _hoisted_7$2 = {
  key: 0,
  class: "user-name"
};
const _hoisted_8$1 = {
  key: 1,
  class: "bi bi-chevron-down dropdown-icon"
};
const _sfc_main$6 = /* @__PURE__ */ defineComponent({
  __name: "Navbar",
  props: {
    collapsed: { type: Boolean, default: false }
  },
  emits: ["toggle-sidebar"],
  setup(__props, { emit: __emit }) {
    const emit = __emit;
    const router = useRouter();
    const userStore = useUserStore();
    const notificationStore = useNotificationStore();
    const isMobile = ref(false);
    const isFullscreen = ref(false);
    const navbarClasses = computed(() => ({
      "navbar--mobile": isMobile.value,
      "navbar--fixed": true
    }));
    const username = computed(() => userStore.username || "未登录");
    const userAvatar = computed(() => userStore.avatar || "");
    const availableModels = computed(() => {
      return [
        // 始皇API模型（新增）
        {
          value: "shihuang-gpt5",
          label: "GPT5（最强推理）",
          icon: "bi-stars",
          recommended: false,
          provider: "shihuang"
        },
        {
          value: "shihuang-claude-sonnet-45",
          label: "Claude Sonnet 4.5（标书专用）",
          icon: "bi-chat-square-text",
          recommended: true,
          provider: "shihuang"
        },
        {
          value: "shihuang-gpt4o-mini",
          label: "GPT4o Mini（推荐-默认）",
          icon: "bi-robot",
          recommended: true,
          provider: "shihuang"
        },
        // 联通元景模型（保留）
        {
          value: "yuanjing-deepseek-v3",
          label: "DeepSeek V3",
          icon: "bi-stars",
          recommended: false,
          provider: "unicom"
        },
        {
          value: "yuanjing-qwen3-235b",
          label: "Qwen 2.5 235B",
          icon: "bi-lightning",
          recommended: false,
          provider: "unicom"
        },
        {
          value: "yuanjing-glm-rumination",
          label: "GLM Rumination",
          icon: "bi-chat-dots",
          recommended: false,
          provider: "unicom"
        }
      ];
    });
    const selectedModel = computed({
      get: () => {
        return localStorage.getItem("selectedModel") || "shihuang-gpt4o-mini";
      },
      set: (value) => {
        localStorage.setItem("selectedModel", value);
      }
    });
    const unreadCount = computed(() => notificationStore.unreadCount);
    function handleToggleSidebar() {
      emit("toggle-sidebar");
    }
    function goHome() {
      router.push({ name: "Home" });
    }
    function handleModelChange(modelValue) {
      const model = availableModels.value.find((m) => m.value === modelValue);
      if (model) {
        ElMessage.success(`已切换到 ${model.label} 模型`);
        window.dispatchEvent(
          new CustomEvent("ai-model-changed", {
            detail: { model: modelValue }
          })
        );
      }
    }
    function toggleFullscreen() {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen();
        isFullscreen.value = true;
      } else {
        if (document.exitFullscreen) {
          document.exitFullscreen();
          isFullscreen.value = false;
        }
      }
    }
    function showNotifications() {
      ElMessage.info("通知中心功能开发中...");
    }
    async function handleCommand(command) {
      switch (command) {
        case "profile":
          router.push({ name: "UserProfile" });
          break;
        case "settings":
          router.push({ name: "Settings" });
          break;
        case "logout":
          try {
            await ElMessageBox.confirm("确定要退出登录吗？", "提示", {
              confirmButtonText: "确定",
              cancelButtonText: "取消",
              type: "warning"
            });
            await userStore.logout();
            ElMessage.success("已退出登录");
            router.push({ name: "Login" });
          } catch (error) {
          }
          break;
      }
    }
    function checkScreenSize() {
      isMobile.value = window.innerWidth < 768;
    }
    function handleFullscreenChange() {
      isFullscreen.value = !!document.fullscreenElement;
    }
    onMounted(() => {
      checkScreenSize();
      window.addEventListener("resize", checkScreenSize);
      document.addEventListener("fullscreenchange", handleFullscreenChange);
    });
    onBeforeUnmount(() => {
      window.removeEventListener("resize", checkScreenSize);
      document.removeEventListener("fullscreenchange", handleFullscreenChange);
    });
    return (_ctx, _cache) => {
      const _component_el_tag = ElTag;
      const _component_el_option = ElOption;
      const _component_el_select = ElSelect;
      const _component_el_tooltip = ElTooltip;
      const _component_el_badge = ElBadge;
      const _component_el_avatar = ElAvatar;
      const _component_el_dropdown_item = ElDropdownItem;
      const _component_el_dropdown_menu = ElDropdownMenu;
      const _component_el_dropdown = ElDropdown;
      return openBlock(), createElementBlock("header", {
        class: normalizeClass(["navbar", navbarClasses.value])
      }, [
        createBaseVNode("div", _hoisted_1$6, [
          createBaseVNode("button", {
            class: normalizeClass(["sidebar-toggle", { "is-active": !__props.collapsed }]),
            onClick: handleToggleSidebar,
            title: __props.collapsed ? "展开侧边栏" : "折叠侧边栏"
          }, [..._cache[1] || (_cache[1] = [
            createBaseVNode("i", { class: "bi bi-list" }, null, -1)
          ])], 10, _hoisted_2$4),
          createBaseVNode("div", {
            class: "navbar-brand",
            onClick: goHome
          }, [
            !isMobile.value ? (openBlock(), createElementBlock("i", _hoisted_3$3)) : createCommentVNode("", true),
            _cache[2] || (_cache[2] = createBaseVNode("span", { class: "brand-title" }, "元景AI标书生成平台", -1))
          ])
        ]),
        createBaseVNode("div", _hoisted_4$3, [
          !isMobile.value ? (openBlock(), createBlock(_component_el_select, {
            key: 0,
            modelValue: selectedModel.value,
            "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => selectedModel.value = $event),
            class: "model-selector",
            placeholder: "选择AI模型",
            size: "default",
            onChange: handleModelChange
          }, {
            prefix: withCtx(() => [..._cache[3] || (_cache[3] = [
              createBaseVNode("i", { class: "bi bi-robot" }, null, -1)
            ])]),
            default: withCtx(() => [
              (openBlock(true), createElementBlock(Fragment, null, renderList(availableModels.value, (model) => {
                return openBlock(), createBlock(_component_el_option, {
                  key: model.value,
                  label: model.label,
                  value: model.value
                }, {
                  default: withCtx(() => [
                    createBaseVNode("span", _hoisted_5$2, [
                      createBaseVNode("i", {
                        class: normalizeClass([model.icon, "model-icon"])
                      }, null, 2),
                      createBaseVNode("span", null, toDisplayString(model.label), 1),
                      model.recommended ? (openBlock(), createBlock(_component_el_tag, {
                        key: 0,
                        type: "success",
                        size: "small",
                        class: "model-tag"
                      }, {
                        default: withCtx(() => [..._cache[4] || (_cache[4] = [
                          createTextVNode(" 推荐 ", -1)
                        ])]),
                        _: 1
                      })) : createCommentVNode("", true)
                    ])
                  ]),
                  _: 2
                }, 1032, ["label", "value"]);
              }), 128))
            ]),
            _: 1
          }, 8, ["modelValue"])) : createCommentVNode("", true),
          !isMobile.value ? (openBlock(), createBlock(_component_el_tooltip, {
            key: 1,
            content: "全屏",
            placement: "bottom"
          }, {
            default: withCtx(() => [
              createBaseVNode("button", {
                class: "navbar-action",
                onClick: toggleFullscreen
              }, [
                createBaseVNode("i", {
                  class: normalizeClass([isFullscreen.value ? "bi-fullscreen-exit" : "bi-fullscreen", "bi"])
                }, null, 2)
              ])
            ]),
            _: 1
          })) : createCommentVNode("", true),
          createVNode(_component_el_badge, {
            value: unreadCount.value,
            hidden: unreadCount.value === 0,
            class: "navbar-badge"
          }, {
            default: withCtx(() => [
              createVNode(_component_el_tooltip, {
                content: "通知",
                placement: "bottom"
              }, {
                default: withCtx(() => [
                  createBaseVNode("button", {
                    class: "navbar-action",
                    onClick: showNotifications
                  }, [..._cache[5] || (_cache[5] = [
                    createBaseVNode("i", { class: "bi bi-bell" }, null, -1)
                  ])])
                ]),
                _: 1
              })
            ]),
            _: 1
          }, 8, ["value", "hidden"]),
          createVNode(_component_el_dropdown, {
            trigger: "click",
            onCommand: handleCommand
          }, {
            dropdown: withCtx(() => [
              createVNode(_component_el_dropdown_menu, null, {
                default: withCtx(() => [
                  createVNode(_component_el_dropdown_item, { command: "profile" }, {
                    default: withCtx(() => [..._cache[7] || (_cache[7] = [
                      createBaseVNode("i", { class: "bi bi-person" }, null, -1),
                      createBaseVNode("span", null, "个人信息", -1)
                    ])]),
                    _: 1
                  }),
                  createVNode(_component_el_dropdown_item, { command: "settings" }, {
                    default: withCtx(() => [..._cache[8] || (_cache[8] = [
                      createBaseVNode("i", { class: "bi bi-gear" }, null, -1),
                      createBaseVNode("span", null, "系统设置", -1)
                    ])]),
                    _: 1
                  }),
                  createVNode(_component_el_dropdown_item, {
                    divided: "",
                    command: "logout"
                  }, {
                    default: withCtx(() => [..._cache[9] || (_cache[9] = [
                      createBaseVNode("i", { class: "bi bi-box-arrow-right" }, null, -1),
                      createBaseVNode("span", null, "退出登录", -1)
                    ])]),
                    _: 1
                  })
                ]),
                _: 1
              })
            ]),
            default: withCtx(() => [
              createBaseVNode("div", _hoisted_6$2, [
                createVNode(_component_el_avatar, {
                  size: 32,
                  src: userAvatar.value
                }, {
                  default: withCtx(() => [..._cache[6] || (_cache[6] = [
                    createBaseVNode("i", { class: "bi bi-person-circle" }, null, -1)
                  ])]),
                  _: 1
                }, 8, ["src"]),
                !isMobile.value ? (openBlock(), createElementBlock("span", _hoisted_7$2, toDisplayString(username.value), 1)) : createCommentVNode("", true),
                !isMobile.value ? (openBlock(), createElementBlock("i", _hoisted_8$1)) : createCommentVNode("", true)
              ])
            ]),
            _: 1
          })
        ])
      ], 2);
    };
  }
});
const Navbar = /* @__PURE__ */ _export_sfc(_sfc_main$6, [["__scopeId", "data-v-75e8158b"]]);
const _hoisted_1$5 = {
  key: 0,
  class: "menu-group-title"
};
const _hoisted_2$3 = { class: "group-label" };
const _hoisted_3$2 = { class: "menu-title" };
const _hoisted_4$2 = { class: "menu-title" };
const _hoisted_5$1 = { class: "menu-title" };
const _hoisted_6$1 = { class: "menu-title" };
const _hoisted_7$1 = {
  key: 0,
  class: "sidebar-footer"
};
const _sfc_main$5 = /* @__PURE__ */ defineComponent({
  __name: "Sidebar",
  props: {
    collapsed: { type: Boolean, default: false },
    uniqueOpened: { type: Boolean, default: true },
    showCollapseButton: { type: Boolean, default: true }
  },
  emits: ["update:collapsed"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const route = useRoute();
    const router = useRouter();
    const userStore = useUserStore();
    const sidebarClasses = computed(() => ({
      "sidebar--collapsed": props.collapsed
    }));
    const menuCategories = computed(() => {
      const categories = [
        { key: "workspace", label: "工作台", icon: "bi-house-fill" },
        { key: "project", label: "项目管理", icon: "bi-folder-fill" },
        { key: "ai-tools", label: "AI核心工具", icon: "bi-robot" },
        { key: "knowledge", label: "知识中心", icon: "bi-book-fill" }
      ];
      if (userStore.username === "admin") {
        categories.push({ key: "abtest", label: "AB测试", icon: "bi-bug" });
      }
      return categories;
    });
    const menuItems = computed(() => {
      const allRoutes = router.getRoutes();
      const allMenus = generateMenuFromRoutes(allRoutes);
      return allMenus.filter((item) => {
        var _a, _b;
        if (((_a = item.meta) == null ? void 0 : _a.showInMenu) === false) return false;
        if (((_b = item.meta) == null ? void 0 : _b.category) === "abtest" && userStore.username !== "admin") {
          return false;
        }
        return true;
      });
    });
    const groupedMenuItems = computed(() => {
      const groups = {};
      menuItems.value.forEach((item) => {
        var _a, _b;
        if ((_a = item.meta) == null ? void 0 : _a.parent) {
          return;
        }
        const category = ((_b = item.meta) == null ? void 0 : _b.category) || "other";
        if (!groups[category]) {
          groups[category] = [];
        }
        groups[category].push(item);
      });
      Object.keys(groups).forEach((key) => {
        groups[key].sort((a, b) => (a.order || 99) - (b.order || 99));
      });
      return groups;
    });
    const activeMenu = computed(() => {
      const { path } = route;
      return path;
    });
    function handleMenuSelect(index) {
      if (index !== route.path) {
        router.push(index);
      }
    }
    function toggleCollapse() {
      emit("update:collapsed", !props.collapsed);
    }
    watch(
      () => route.path,
      () => {
      }
    );
    return (_ctx, _cache) => {
      const _component_el_menu_item = ElMenuItem;
      const _component_el_sub_menu = ElSubMenu;
      const _component_el_divider = ElDivider;
      const _component_el_menu = ElMenu;
      const _component_el_scrollbar = ElScrollbar;
      return openBlock(), createElementBlock("aside", {
        class: normalizeClass(["sidebar", sidebarClasses.value])
      }, [
        createVNode(_component_el_scrollbar, { class: "sidebar-scrollbar" }, {
          default: withCtx(() => [
            createVNode(_component_el_menu, {
              "default-active": activeMenu.value,
              collapse: __props.collapsed,
              "unique-opened": __props.uniqueOpened,
              "collapse-transition": false,
              class: "sidebar-menu",
              onSelect: handleMenuSelect
            }, {
              default: withCtx(() => [
                (openBlock(true), createElementBlock(Fragment, null, renderList(menuCategories.value, (category) => {
                  return openBlock(), createElementBlock(Fragment, {
                    key: category.key
                  }, [
                    groupedMenuItems.value[category.key] && groupedMenuItems.value[category.key].length > 0 ? (openBlock(), createElementBlock(Fragment, { key: 0 }, [
                      !__props.collapsed ? (openBlock(), createElementBlock("div", _hoisted_1$5, [
                        createBaseVNode("i", {
                          class: normalizeClass(["bi group-icon", category.icon])
                        }, null, 2),
                        createBaseVNode("span", _hoisted_2$3, toDisplayString(category.label), 1)
                      ])) : createCommentVNode("", true),
                      (openBlock(true), createElementBlock(Fragment, null, renderList(groupedMenuItems.value[category.key], (item) => {
                        return openBlock(), createElementBlock(Fragment, {
                          key: item.path
                        }, [
                          !item.children || item.children.length === 0 ? (openBlock(), createBlock(_component_el_menu_item, {
                            key: 0,
                            index: item.path
                          }, {
                            title: withCtx(() => [
                              item.icon ? (openBlock(), createElementBlock("i", {
                                key: 0,
                                class: normalizeClass(["bi menu-icon", item.icon])
                              }, null, 2)) : createCommentVNode("", true),
                              createBaseVNode("span", _hoisted_3$2, toDisplayString(item.title), 1)
                            ]),
                            _: 2
                          }, 1032, ["index"])) : (openBlock(), createBlock(_component_el_sub_menu, {
                            key: 1,
                            index: item.path
                          }, {
                            title: withCtx(() => [
                              item.icon ? (openBlock(), createElementBlock("i", {
                                key: 0,
                                class: normalizeClass(["bi menu-icon", item.icon])
                              }, null, 2)) : createCommentVNode("", true),
                              createBaseVNode("span", _hoisted_4$2, toDisplayString(item.title), 1)
                            ]),
                            default: withCtx(() => [
                              (openBlock(true), createElementBlock(Fragment, null, renderList(item.children, (subItem) => {
                                return openBlock(), createElementBlock(Fragment, {
                                  key: subItem.path
                                }, [
                                  !subItem.children || subItem.children.length === 0 ? (openBlock(), createBlock(_component_el_menu_item, {
                                    key: 0,
                                    index: subItem.path
                                  }, {
                                    title: withCtx(() => [
                                      subItem.icon ? (openBlock(), createElementBlock("i", {
                                        key: 0,
                                        class: normalizeClass(["bi submenu-icon", subItem.icon])
                                      }, null, 2)) : createCommentVNode("", true),
                                      createBaseVNode("span", null, toDisplayString(subItem.title), 1)
                                    ]),
                                    _: 2
                                  }, 1032, ["index"])) : (openBlock(), createBlock(_component_el_sub_menu, {
                                    key: 1,
                                    index: subItem.path
                                  }, {
                                    title: withCtx(() => [
                                      subItem.icon ? (openBlock(), createElementBlock("i", {
                                        key: 0,
                                        class: normalizeClass(["bi submenu-icon", subItem.icon])
                                      }, null, 2)) : createCommentVNode("", true),
                                      createBaseVNode("span", null, toDisplayString(subItem.title), 1)
                                    ]),
                                    default: withCtx(() => [
                                      (openBlock(true), createElementBlock(Fragment, null, renderList(subItem.children, (thirdItem) => {
                                        return openBlock(), createBlock(_component_el_menu_item, {
                                          key: thirdItem.path,
                                          index: thirdItem.path
                                        }, {
                                          title: withCtx(() => [
                                            thirdItem.icon ? (openBlock(), createElementBlock("i", {
                                              key: 0,
                                              class: normalizeClass(["bi submenu-icon", thirdItem.icon])
                                            }, null, 2)) : createCommentVNode("", true),
                                            createBaseVNode("span", null, toDisplayString(thirdItem.title), 1)
                                          ]),
                                          _: 2
                                        }, 1032, ["index"]);
                                      }), 128))
                                    ]),
                                    _: 2
                                  }, 1032, ["index"]))
                                ], 64);
                              }), 128))
                            ]),
                            _: 2
                          }, 1032, ["index"]))
                        ], 64);
                      }), 128)),
                      !__props.collapsed ? (openBlock(), createBlock(_component_el_divider, {
                        key: 1,
                        class: "menu-group-divider"
                      })) : createCommentVNode("", true)
                    ], 64)) : createCommentVNode("", true)
                  ], 64);
                }), 128)),
                groupedMenuItems.value["other"] && groupedMenuItems.value["other"].length > 0 ? (openBlock(true), createElementBlock(Fragment, { key: 0 }, renderList(groupedMenuItems.value["other"], (item) => {
                  return openBlock(), createElementBlock(Fragment, {
                    key: item.path
                  }, [
                    !item.children || item.children.length === 0 ? (openBlock(), createBlock(_component_el_menu_item, {
                      key: 0,
                      index: item.path
                    }, {
                      title: withCtx(() => [
                        item.icon ? (openBlock(), createElementBlock("i", {
                          key: 0,
                          class: normalizeClass(["bi menu-icon", item.icon])
                        }, null, 2)) : createCommentVNode("", true),
                        createBaseVNode("span", _hoisted_5$1, toDisplayString(item.title), 1)
                      ]),
                      _: 2
                    }, 1032, ["index"])) : (openBlock(), createBlock(_component_el_sub_menu, {
                      key: 1,
                      index: item.path
                    }, {
                      title: withCtx(() => [
                        item.icon ? (openBlock(), createElementBlock("i", {
                          key: 0,
                          class: normalizeClass(["bi menu-icon", item.icon])
                        }, null, 2)) : createCommentVNode("", true),
                        createBaseVNode("span", _hoisted_6$1, toDisplayString(item.title), 1)
                      ]),
                      default: withCtx(() => [
                        (openBlock(true), createElementBlock(Fragment, null, renderList(item.children, (subItem) => {
                          return openBlock(), createElementBlock(Fragment, {
                            key: subItem.path
                          }, [
                            !subItem.children || subItem.children.length === 0 ? (openBlock(), createBlock(_component_el_menu_item, {
                              key: 0,
                              index: subItem.path
                            }, {
                              title: withCtx(() => [
                                subItem.icon ? (openBlock(), createElementBlock("i", {
                                  key: 0,
                                  class: normalizeClass(["bi submenu-icon", subItem.icon])
                                }, null, 2)) : createCommentVNode("", true),
                                createBaseVNode("span", null, toDisplayString(subItem.title), 1)
                              ]),
                              _: 2
                            }, 1032, ["index"])) : (openBlock(), createBlock(_component_el_sub_menu, {
                              key: 1,
                              index: subItem.path
                            }, {
                              title: withCtx(() => [
                                subItem.icon ? (openBlock(), createElementBlock("i", {
                                  key: 0,
                                  class: normalizeClass(["bi submenu-icon", subItem.icon])
                                }, null, 2)) : createCommentVNode("", true),
                                createBaseVNode("span", null, toDisplayString(subItem.title), 1)
                              ]),
                              default: withCtx(() => [
                                (openBlock(true), createElementBlock(Fragment, null, renderList(subItem.children, (thirdItem) => {
                                  return openBlock(), createBlock(_component_el_menu_item, {
                                    key: thirdItem.path,
                                    index: thirdItem.path
                                  }, {
                                    title: withCtx(() => [
                                      thirdItem.icon ? (openBlock(), createElementBlock("i", {
                                        key: 0,
                                        class: normalizeClass(["bi submenu-icon", thirdItem.icon])
                                      }, null, 2)) : createCommentVNode("", true),
                                      createBaseVNode("span", null, toDisplayString(thirdItem.title), 1)
                                    ]),
                                    _: 2
                                  }, 1032, ["index"]);
                                }), 128))
                              ]),
                              _: 2
                            }, 1032, ["index"]))
                          ], 64);
                        }), 128))
                      ]),
                      _: 2
                    }, 1032, ["index"]))
                  ], 64);
                }), 128)) : createCommentVNode("", true)
              ]),
              _: 1
            }, 8, ["default-active", "collapse", "unique-opened"])
          ]),
          _: 1
        }),
        __props.showCollapseButton ? (openBlock(), createElementBlock("div", _hoisted_7$1, [
          createBaseVNode("button", {
            class: "collapse-button",
            onClick: toggleCollapse
          }, [
            createBaseVNode("i", {
              class: normalizeClass([__props.collapsed ? "bi-chevron-right" : "bi-chevron-left", "bi"])
            }, null, 2)
          ])
        ])) : createCommentVNode("", true)
      ], 2);
    };
  }
});
const Sidebar = /* @__PURE__ */ _export_sfc(_sfc_main$5, [["__scopeId", "data-v-5c83301f"]]);
const _hoisted_1$4 = {
  key: 0,
  class: "breadcrumb-wrapper"
};
const _hoisted_2$2 = { class: "breadcrumb-item" };
const _sfc_main$4 = /* @__PURE__ */ defineComponent({
  __name: "Breadcrumb",
  props: {
    showIcon: { type: Boolean, default: true }
  },
  setup(__props) {
    const route = useRoute();
    const breadcrumbs = computed(() => {
      return getBreadcrumbs(route);
    });
    return (_ctx, _cache) => {
      const _component_el_breadcrumb_item = ElBreadcrumbItem;
      const _component_el_breadcrumb = ElBreadcrumb;
      return breadcrumbs.value.length > 0 ? (openBlock(), createElementBlock("div", _hoisted_1$4, [
        createVNode(_component_el_breadcrumb, { separator: "/" }, {
          default: withCtx(() => [
            (openBlock(true), createElementBlock(Fragment, null, renderList(breadcrumbs.value, (crumb, index) => {
              return openBlock(), createBlock(_component_el_breadcrumb_item, {
                key: index,
                to: crumb.path ? { path: crumb.path } : void 0
              }, {
                default: withCtx(() => [
                  createBaseVNode("span", _hoisted_2$2, [
                    crumb.icon && __props.showIcon ? (openBlock(), createElementBlock("i", {
                      key: 0,
                      class: normalizeClass([crumb.icon, "breadcrumb-icon"])
                    }, null, 2)) : createCommentVNode("", true),
                    createBaseVNode("span", null, toDisplayString(crumb.title), 1)
                  ])
                ]),
                _: 2
              }, 1032, ["to"]);
            }), 128))
          ]),
          _: 1
        })
      ])) : createCommentVNode("", true);
    };
  }
});
const Breadcrumb = /* @__PURE__ */ _export_sfc(_sfc_main$4, [["__scopeId", "data-v-90d0759c"]]);
const _hoisted_1$3 = {
  key: 0,
  class: "tabs-view"
};
const _hoisted_2$1 = ["onClick", "onContextmenu"];
const _hoisted_3$1 = { class: "tab-title" };
const _hoisted_4$1 = ["onClick"];
const _sfc_main$3 = /* @__PURE__ */ defineComponent({
  __name: "TabsView",
  setup(__props) {
    const route = useRoute();
    const router = useRouter();
    const visitedViews = ref([]);
    const selectedTag = ref(null);
    const contextMenuVisible = ref(false);
    const contextMenuLeft = ref(0);
    const contextMenuTop = ref(0);
    const tabsContainerRef = ref();
    const contextMenuRef = ref();
    function isActive(tag) {
      return tag.path === route.path;
    }
    function addVisitedView(view) {
      var _a;
      if (view.name === "Login" || ((_a = view.meta) == null ? void 0 : _a.hideTabs)) {
        return;
      }
      const exists = visitedViews.value.some((v) => v.path === view.path);
      if (!exists) {
        visitedViews.value.push({
          name: view.name,
          path: view.path,
          fullPath: view.fullPath,
          query: view.query,
          params: view.params,
          meta: view.meta
        });
      }
      saveVisitedViews();
    }
    function closeTab(tag) {
      var _a;
      if ((_a = tag.meta) == null ? void 0 : _a.affix) {
        return;
      }
      const index = visitedViews.value.findIndex((v) => v.path === tag.path);
      if (index > -1) {
        visitedViews.value.splice(index, 1);
        saveVisitedViews();
        if (isActive(tag)) {
          const lastTag = visitedViews.value[visitedViews.value.length - 1];
          if (lastTag) {
            router.push(lastTag.path);
          } else {
            router.push("/");
          }
        }
      }
    }
    function handleTabClick(tag) {
      if (!isActive(tag)) {
        router.push(tag.path);
      }
    }
    function handleContextMenu(tag, event) {
      selectedTag.value = tag;
      contextMenuVisible.value = true;
      contextMenuLeft.value = event.clientX;
      contextMenuTop.value = event.clientY;
    }
    function refreshTab() {
      contextMenuVisible.value = false;
      if (selectedTag.value) {
        router.replace({
          path: selectedTag.value.path,
          query: { _t: Date.now() }
        });
      }
    }
    function closeOtherTabs() {
      contextMenuVisible.value = false;
      if (!selectedTag.value) return;
      visitedViews.value = visitedViews.value.filter(
        (v) => {
          var _a;
          return ((_a = v.meta) == null ? void 0 : _a.affix) || v.path === selectedTag.value.path;
        }
      );
      saveVisitedViews();
      if (route.path !== selectedTag.value.path) {
        router.push(selectedTag.value.path);
      }
    }
    function closeAllTabs() {
      contextMenuVisible.value = false;
      visitedViews.value = visitedViews.value.filter((v) => {
        var _a;
        return (_a = v.meta) == null ? void 0 : _a.affix;
      });
      saveVisitedViews();
      const affixTag = visitedViews.value.find((v) => {
        var _a;
        return (_a = v.meta) == null ? void 0 : _a.affix;
      });
      if (affixTag) {
        router.push(affixTag.path);
      } else {
        router.push("/");
      }
    }
    function saveVisitedViews() {
      const views = visitedViews.value.map((v) => ({
        name: v.name,
        path: v.path,
        fullPath: v.fullPath,
        query: v.query,
        params: v.params,
        meta: v.meta
      }));
      localStorage.setItem("visitedViews", JSON.stringify(views));
    }
    function restoreVisitedViews() {
      try {
        const saved = localStorage.getItem("visitedViews");
        if (saved) {
          const views = JSON.parse(saved);
          visitedViews.value = views;
        }
      } catch (error) {
        console.error("恢复访问记录失败:", error);
      }
    }
    function closeContextMenu() {
      contextMenuVisible.value = false;
    }
    function initAffixTags() {
      const affixTags = router.getRoutes().filter((route2) => {
        var _a;
        return (_a = route2.meta) == null ? void 0 : _a.affix;
      });
      for (const tag of affixTags) {
        if (tag.name) {
          addVisitedView(tag);
        }
      }
    }
    onMounted(() => {
      restoreVisitedViews();
      initAffixTags();
      addVisitedView(route);
      document.addEventListener("click", closeContextMenu);
    });
    onBeforeUnmount(() => {
      document.removeEventListener("click", closeContextMenu);
    });
    watch(
      () => route.path,
      () => {
        addVisitedView(route);
      }
    );
    return (_ctx, _cache) => {
      var _a, _b;
      const _component_el_scrollbar = ElScrollbar;
      return visitedViews.value.length > 0 ? (openBlock(), createElementBlock("div", _hoisted_1$3, [
        createVNode(_component_el_scrollbar, { class: "tabs-scrollbar" }, {
          default: withCtx(() => [
            createBaseVNode("div", {
              class: "tabs-container",
              ref_key: "tabsContainerRef",
              ref: tabsContainerRef
            }, [
              (openBlock(true), createElementBlock(Fragment, null, renderList(visitedViews.value, (tag) => {
                var _a2, _b2, _c, _d;
                return openBlock(), createElementBlock("div", {
                  key: tag.path,
                  class: normalizeClass(["tabs-item", {
                    "is-active": isActive(tag),
                    "is-affix": (_a2 = tag.meta) == null ? void 0 : _a2.affix
                  }]),
                  onClick: ($event) => handleTabClick(tag),
                  onContextmenu: withModifiers(($event) => handleContextMenu(tag, $event), ["prevent"])
                }, [
                  ((_b2 = tag.meta) == null ? void 0 : _b2.icon) ? (openBlock(), createElementBlock("i", {
                    key: 0,
                    class: normalizeClass([tag.meta.icon, "tab-icon"])
                  }, null, 2)) : createCommentVNode("", true),
                  createBaseVNode("span", _hoisted_3$1, toDisplayString(((_c = tag.meta) == null ? void 0 : _c.title) || tag.name), 1),
                  !((_d = tag.meta) == null ? void 0 : _d.affix) ? (openBlock(), createElementBlock("i", {
                    key: 1,
                    class: "bi bi-x tab-close",
                    onClick: withModifiers(($event) => closeTab(tag), ["stop"])
                  }, null, 8, _hoisted_4$1)) : createCommentVNode("", true)
                ], 42, _hoisted_2$1);
              }), 128))
            ], 512)
          ]),
          _: 1
        }),
        withDirectives(createBaseVNode("div", {
          class: "context-menu",
          style: normalizeStyle({ left: contextMenuLeft.value + "px", top: contextMenuTop.value + "px" }),
          ref_key: "contextMenuRef",
          ref: contextMenuRef
        }, [
          createBaseVNode("div", {
            class: "context-menu-item",
            onClick: refreshTab
          }, [..._cache[0] || (_cache[0] = [
            createBaseVNode("i", { class: "bi bi-arrow-clockwise" }, null, -1),
            createBaseVNode("span", null, "刷新", -1)
          ])]),
          _cache[3] || (_cache[3] = createBaseVNode("div", { class: "context-menu-divider" }, null, -1)),
          createBaseVNode("div", {
            class: normalizeClass(["context-menu-item", { "is-disabled": (_b = (_a = selectedTag.value) == null ? void 0 : _a.meta) == null ? void 0 : _b.affix }]),
            onClick: closeOtherTabs
          }, [..._cache[1] || (_cache[1] = [
            createBaseVNode("i", { class: "bi bi-x-circle" }, null, -1),
            createBaseVNode("span", null, "关闭其他", -1)
          ])], 2),
          createBaseVNode("div", {
            class: "context-menu-item",
            onClick: closeAllTabs
          }, [..._cache[2] || (_cache[2] = [
            createBaseVNode("i", { class: "bi bi-x-octagon" }, null, -1),
            createBaseVNode("span", null, "关闭所有", -1)
          ])])
        ], 4), [
          [vShow, contextMenuVisible.value]
        ])
      ])) : createCommentVNode("", true);
    };
  }
});
const TabsView = /* @__PURE__ */ _export_sfc(_sfc_main$3, [["__scopeId", "data-v-ec710d5a"]]);
const _hoisted_1$2 = { class: "footer-content" };
const _hoisted_2 = { class: "footer-section footer-copyright" };
const _hoisted_3 = {
  key: 0,
  class: "footer-divider"
};
const _hoisted_4 = {
  key: 1,
  class: "footer-section footer-version"
};
const _hoisted_5 = {
  key: 2,
  class: "footer-divider"
};
const _hoisted_6 = {
  key: 3,
  class: "footer-section footer-support"
};
const _hoisted_7 = {
  key: 4,
  class: "footer-divider"
};
const _hoisted_8 = {
  key: 5,
  class: "footer-section footer-beian"
};
const _hoisted_9 = ["href"];
const _sfc_main$2 = /* @__PURE__ */ defineComponent({
  __name: "Footer",
  props: {
    showVersion: { type: Boolean, default: true },
    showTechSupport: { type: Boolean, default: true },
    beian: { default: "" },
    beianLink: { default: "https://beian.miit.gov.cn/" }
  },
  setup(__props) {
    const isMobile = ref(false);
    const currentYear = computed(() => {
      return (/* @__PURE__ */ new Date()).getFullYear();
    });
    const version = computed(() => {
      return "2.0.0";
    });
    const footerClasses = computed(() => ({
      "footer--mobile": isMobile.value
    }));
    function checkScreenSize() {
      isMobile.value = window.innerWidth < 768;
    }
    onMounted(() => {
      checkScreenSize();
      window.addEventListener("resize", checkScreenSize);
    });
    onBeforeUnmount(() => {
      window.removeEventListener("resize", checkScreenSize);
    });
    return (_ctx, _cache) => {
      return openBlock(), createElementBlock("footer", {
        class: normalizeClass(["app-footer", footerClasses.value])
      }, [
        createBaseVNode("div", _hoisted_1$2, [
          createBaseVNode("div", _hoisted_2, [
            createBaseVNode("span", null, "© " + toDisplayString(currentYear.value) + " 元景AI. All rights reserved.", 1)
          ]),
          !isMobile.value ? (openBlock(), createElementBlock("div", _hoisted_3, "|")) : createCommentVNode("", true),
          __props.showVersion ? (openBlock(), createElementBlock("div", _hoisted_4, [
            createBaseVNode("span", null, "版本 " + toDisplayString(version.value), 1)
          ])) : createCommentVNode("", true),
          !isMobile.value && __props.showTechSupport ? (openBlock(), createElementBlock("div", _hoisted_5, "|")) : createCommentVNode("", true),
          __props.showTechSupport ? (openBlock(), createElementBlock("div", _hoisted_6, [..._cache[0] || (_cache[0] = [
            createBaseVNode("span", null, "技术支持：元景AI团队", -1)
          ])])) : createCommentVNode("", true),
          !isMobile.value && __props.beian ? (openBlock(), createElementBlock("div", _hoisted_7, "|")) : createCommentVNode("", true),
          __props.beian ? (openBlock(), createElementBlock("div", _hoisted_8, [
            createBaseVNode("a", {
              href: __props.beianLink,
              target: "_blank",
              rel: "noopener noreferrer"
            }, toDisplayString(__props.beian), 9, _hoisted_9)
          ])) : createCommentVNode("", true)
        ])
      ], 2);
    };
  }
});
const Footer = /* @__PURE__ */ _export_sfc(_sfc_main$2, [["__scopeId", "data-v-c7ce98ec"]]);
const _hoisted_1$1 = {
  key: 0,
  class: "tender-document-floating-button"
};
const _sfc_main$1 = /* @__PURE__ */ defineComponent({
  __name: "TenderDocumentFloatingButton",
  setup(__props) {
    const projectStore = useProjectStore();
    const previewVisible = ref(false);
    const loading = ref(false);
    const shouldShow = computed(() => {
      const hasProject = projectStore.hasCurrentProject;
      const currentProj = projectStore.currentProject;
      const hasTenderDoc = !!(currentProj == null ? void 0 : currentProj.tender_document_path);
      if (hasProject && !hasTenderDoc) {
        console.log("[悬浮按钮] 项目已选择但没有标书文档:", currentProj == null ? void 0 : currentProj.id, currentProj == null ? void 0 : currentProj.project_name);
      }
      return hasProject && hasTenderDoc;
    });
    const tenderDocumentPath = computed(() => {
      var _a;
      return ((_a = projectStore.currentProject) == null ? void 0 : _a.tender_document_path) || "";
    });
    const tenderDocumentName = computed(() => {
      var _a, _b;
      const projectName = ((_a = projectStore.currentProject) == null ? void 0 : _a.project_name) || ((_b = projectStore.currentProject) == null ? void 0 : _b.name) || "未命名项目";
      return `${projectName} - 招标文档`;
    });
    function handlePreview() {
      if (!tenderDocumentPath.value) {
        ElMessage.warning("当前项目没有招标文档");
        return;
      }
      previewVisible.value = true;
    }
    return (_ctx, _cache) => {
      const _component_el_icon = ElIcon;
      const _component_el_button = ElButton;
      const _component_el_tooltip = ElTooltip;
      return openBlock(), createBlock(Transition, { name: "fade-slide" }, {
        default: withCtx(() => [
          shouldShow.value ? (openBlock(), createElementBlock("div", _hoisted_1$1, [
            createVNode(_component_el_tooltip, {
              content: "点击预览当前项目的招标文档",
              placement: "left",
              "show-after": 500
            }, {
              default: withCtx(() => [
                createVNode(_component_el_button, {
                  type: "primary",
                  size: "large",
                  loading: loading.value,
                  onClick: handlePreview,
                  class: "floating-btn"
                }, {
                  default: withCtx(() => [
                    createVNode(_component_el_icon, { class: "btn-icon" }, {
                      default: withCtx(() => [
                        createVNode(unref(document_default))
                      ]),
                      _: 1
                    }),
                    _cache[1] || (_cache[1] = createBaseVNode("span", { class: "btn-text" }, "预览标书", -1))
                  ]),
                  _: 1
                }, 8, ["loading"])
              ]),
              _: 1
            }),
            createVNode(DocumentPreview, {
              modelValue: previewVisible.value,
              "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => previewVisible.value = $event),
              "file-url": tenderDocumentPath.value,
              "file-name": tenderDocumentName.value
            }, null, 8, ["modelValue", "file-url", "file-name"])
          ])) : createCommentVNode("", true)
        ]),
        _: 1
      });
    };
  }
});
const TenderDocumentFloatingButton = /* @__PURE__ */ _export_sfc(_sfc_main$1, [["__scopeId", "data-v-59d6aa8a"]]);
const _hoisted_1 = { class: "layout-container" };
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "MainLayout",
  setup(__props) {
    const route = useRoute();
    const settingsStore = useSettingsStore();
    const sidebarCollapsed = ref(false);
    const isMobile = ref(false);
    const isTablet = ref(false);
    const cachedViews = ref([]);
    const layoutClasses = computed(() => ({
      "layout--mobile": isMobile.value,
      "layout--tablet": isTablet.value,
      "layout--sidebar-collapsed": sidebarCollapsed.value,
      "layout--fixed-header": settingsStore.fixedHeader,
      "layout--sidebar-hidden": !showSidebar.value
    }));
    const contentClasses = computed(() => ({
      "content--with-sidebar": showSidebar.value,
      "content--sidebar-collapsed": sidebarCollapsed.value,
      "content--full-width": !showSidebar.value
    }));
    const pageContentClasses = computed(() => ({
      "page-content--with-tabs": showTabs.value,
      "page-content--with-breadcrumb": showBreadcrumb.value,
      "page-content--padding": !route.meta.noPadding
    }));
    const showSidebar = computed(() => {
      if (route.name === "Login") return false;
      if (route.meta.hideSidebar) return false;
      return settingsStore.showSidebar;
    });
    const showBreadcrumb = computed(() => {
      if (route.name === "Login") return false;
      if (route.meta.hideBreadcrumb) return false;
      return settingsStore.showBreadcrumb;
    });
    const showTabs = computed(() => {
      if (route.name === "Login") return false;
      if (route.meta.hideTabs) return false;
      return settingsStore.showTabs;
    });
    const showFooter = computed(() => {
      if (route.name === "Login") return false;
      if (route.meta.hideFooter) return false;
      return settingsStore.showFooter;
    });
    const transitionName = computed(() => {
      return settingsStore.pageTransition || "fade";
    });
    function toggleSidebar() {
      sidebarCollapsed.value = !sidebarCollapsed.value;
    }
    function setSidebarCollapsed(collapsed) {
      sidebarCollapsed.value = collapsed;
    }
    function checkScreenSize() {
      const width = window.innerWidth;
      isMobile.value = width < 768;
      isTablet.value = width >= 768 && width < 1024;
      if (isMobile.value && !sidebarCollapsed.value) {
        sidebarCollapsed.value = true;
      }
    }
    function updateCachedViews() {
      if (route.meta.keepAlive && route.name) {
        const viewName = route.name;
        if (!cachedViews.value.includes(viewName)) {
          cachedViews.value.push(viewName);
        }
      }
    }
    onMounted(() => {
      checkScreenSize();
      window.addEventListener("resize", checkScreenSize);
      const savedCollapsed = localStorage.getItem("sidebarCollapsed");
      if (savedCollapsed !== null) {
        sidebarCollapsed.value = savedCollapsed === "true";
      }
    });
    onBeforeUnmount(() => {
      window.removeEventListener("resize", checkScreenSize);
    });
    watch(sidebarCollapsed, (newValue) => {
      localStorage.setItem("sidebarCollapsed", String(newValue));
    });
    watch(
      () => route.path,
      () => {
        updateCachedViews();
        if (isMobile.value && !sidebarCollapsed.value) {
          sidebarCollapsed.value = true;
        }
      },
      { immediate: true }
    );
    return (_ctx, _cache) => {
      const _component_router_view = resolveComponent("router-view");
      return openBlock(), createElementBlock("div", {
        class: normalizeClass(["main-layout", layoutClasses.value])
      }, [
        createVNode(Navbar, {
          collapsed: sidebarCollapsed.value,
          onToggleSidebar: toggleSidebar
        }, null, 8, ["collapsed"]),
        createBaseVNode("div", _hoisted_1, [
          showSidebar.value ? (openBlock(), createBlock(Sidebar, {
            key: 0,
            collapsed: sidebarCollapsed.value,
            "onUpdate:collapsed": setSidebarCollapsed
          }, null, 8, ["collapsed"])) : createCommentVNode("", true),
          createBaseVNode("div", {
            class: normalizeClass(["main-content", contentClasses.value])
          }, [
            showBreadcrumb.value ? (openBlock(), createBlock(Breadcrumb, {
              key: 0,
              class: "breadcrumb-container"
            })) : createCommentVNode("", true),
            showTabs.value ? (openBlock(), createBlock(TabsView, {
              key: 1,
              class: "tabs-container"
            })) : createCommentVNode("", true),
            createBaseVNode("div", {
              class: normalizeClass(["page-content", pageContentClasses.value])
            }, [
              createVNode(_component_router_view, null, {
                default: withCtx(({ Component, route: route2 }) => [
                  createVNode(Transition, {
                    name: transitionName.value,
                    mode: "out-in"
                  }, {
                    default: withCtx(() => [
                      (openBlock(), createBlock(KeepAlive, { include: cachedViews.value }, [
                        (openBlock(), createBlock(resolveDynamicComponent(Component), {
                          key: route2.path
                        }))
                      ], 1032, ["include"]))
                    ]),
                    _: 2
                  }, 1032, ["name"])
                ]),
                _: 1
              })
            ], 2),
            showFooter.value ? (openBlock(), createBlock(Footer, {
              key: 2,
              class: "footer-container"
            })) : createCommentVNode("", true)
          ], 2)
        ]),
        isMobile.value && !sidebarCollapsed.value ? (openBlock(), createElementBlock("div", {
          key: 0,
          class: "sidebar-overlay",
          onClick: toggleSidebar
        })) : createCommentVNode("", true),
        createVNode(TenderDocumentFloatingButton)
      ], 2);
    };
  }
});
const MainLayout = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-ccf14112"]]);
export {
  MainLayout as default
};
