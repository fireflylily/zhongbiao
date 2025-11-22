import { d as defineComponent, r as ref, c as computed, D as watch, S as onMounted, T as onBeforeUnmount, e as createElementBlock, o as openBlock, U as normalizeClass, n as createBaseVNode, k as createBlock, t as toDisplayString, X as ElTag, w as withCtx, f as createVNode, p as createTextVNode, h as unref, ap as loading_default, ad as ElIcon, aS as full_screen_default, g as ElButton, aD as view_default, aE as download_default, l as createCommentVNode, aT as refresh_default, F as Fragment, V as renderList, ar as ElEmpty, aU as d_arrow_left_default, aV as d_arrow_right_default, aN as mergeProps, aI as mC, aK as nextTick, A as ElMessage } from "./vendor-MtO928VE.js";
/* empty css                                                                           */
import { _ as _export_sfc } from "./index.js";
const _hoisted_1 = { class: "editor-header" };
const _hoisted_2 = { class: "header-left" };
const _hoisted_3 = { class: "header-actions" };
const _hoisted_4 = { class: "editor-body" };
const _hoisted_5 = {
  key: 0,
  class: "outline-sidebar"
};
const _hoisted_6 = { class: "outline-header" };
const _hoisted_7 = { class: "outline-list" };
const _hoisted_8 = ["onClick"];
const _hoisted_9 = { class: "outline-text" };
const _hoisted_10 = { class: "outline-footer" };
const _hoisted_11 = { class: "editor-main" };
const _hoisted_12 = {
  key: 0,
  class: "streaming-indicator"
};
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "RichTextEditor",
  props: {
    modelValue: {},
    title: { default: "文档编辑" },
    height: { default: 600 },
    readonly: { type: Boolean, default: false },
    streaming: { type: Boolean, default: false },
    showOutline: { type: Boolean, default: true }
  },
  emits: ["update:modelValue", "save", "preview", "export", "ready"],
  setup(__props, { expose: __expose, emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const umoEditorRef = ref(null);
    const content = ref(props.modelValue);
    const isDirty = ref(false);
    const saving = ref(false);
    const isFullscreen = ref(false);
    const isStreaming = computed(() => props.streaming);
    const hasContent = computed(() => !!content.value && content.value !== "<p></p>");
    const needsSwitchToPageLayout = ref(false);
    const editorOptions = computed(() => ({
      // 工具栏配置
      toolbar: {
        defaultMode: "ribbon"
      },
      // 页面配置（使用官方文档的完整配置）
      page: {
        layouts: ["page", "web"],
        // 🔥 两种布局都支持（官方默认）
        defaultMargin: {
          left: 3.18,
          right: 3.18,
          top: 2.54,
          bottom: 2.54
        },
        defaultOrientation: "portrait",
        defaultBackground: "#ffffff",
        showBreakMarks: true,
        showLineNumber: false,
        showToc: false,
        watermark: {
          type: "compact",
          alpha: 0.2,
          fontColor: "#000",
          fontSize: 16,
          fontFamily: "SimSun",
          fontWeight: "normal",
          text: ""
        }
      },
      // 文档配置
      document: {
        enableSpellcheck: false,
        readOnly: props.readonly
      },
      // 文件配置 (FileOptions)
      file: {
        maxSize: 10 * 1024 * 1024,
        // 最大 10MB
        allowedMimeTypes: [
          // 允许的文件类型
          "image/jpeg",
          "image/png",
          "image/gif",
          "image/webp"
        ]
      },
      // 文件上传回调（顶级配置）- 必须是 async 函数
      onFileUpload: async (file) => {
        console.log("[RichTextEditor] 文件上传:", file.name, file.type);
        return new Promise((resolve, reject) => {
          const reader = new FileReader();
          reader.onload = (e) => {
            var _a;
            const url = (_a = e.target) == null ? void 0 : _a.result;
            resolve({
              id: `img-${Date.now()}`,
              url
            });
          };
          reader.onerror = () => reject(new Error("读取失败"));
          reader.readAsDataURL(file);
        });
      },
      // 文件删除回调（顶级配置）- 必须是普通函数（非 async）
      onFileDelete: (file) => {
        if (file) {
          console.log("[RichTextEditor] 文件删除:", file);
        }
        return true;
      }
    }));
    const outline = ref([]);
    const outlineCollapsed = ref(false);
    const activeHeadingId = ref("");
    const refreshingOutline = ref(false);
    computed(() => {
      if (isFullscreen.value) {
        return "calc(100vh - 120px)";
      }
      return typeof props.height === "number" ? `${props.height}px` : props.height;
    });
    watch(() => props.modelValue, (newValue) => {
      if (newValue && newValue !== content.value) {
        content.value = newValue;
        isDirty.value = false;
        if (umoEditorRef.value) {
          setEditorContent(newValue);
        }
      }
    });
    watch(isStreaming, (streaming) => {
      console.log("[RichTextEditor] 流式状态变化:", streaming);
      if (umoEditorRef.value && typeof umoEditorRef.value.setReadOnly === "function") {
        umoEditorRef.value.setReadOnly(streaming || props.readonly);
      }
    });
    const handleEditorCreated = () => {
      console.log("[RichTextEditor] ✅ 编辑器创建完成 (@created事件)");
      setTimeout(() => {
        switchToPageLayout();
      }, 300);
      if (props.modelValue) {
        setTimeout(() => {
          setEditorContent(props.modelValue);
        }, 100);
      }
      if (props.readonly || props.streaming) {
        if (umoEditorRef.value && typeof umoEditorRef.value.setReadOnly === "function") {
          umoEditorRef.value.setReadOnly(true);
        }
      }
      emit("ready");
      console.log("[RichTextEditor] 编辑器就绪");
      setTimeout(() => {
        refreshOutline();
      }, 800);
    };
    const switchToPageLayout = () => {
      if (!umoEditorRef.value) return;
      try {
        if (typeof umoEditorRef.value.setLayout === "function") {
          umoEditorRef.value.setLayout("page");
          console.log("[RichTextEditor] ✅ 已切换到分页模式");
          needsSwitchToPageLayout.value = false;
          setTimeout(() => {
            const container = document.querySelector(".umo-editor-container");
            if (container) {
              container.classList.add("umo-page-mode");
              container.classList.remove("umo-continuous-mode");
              console.log("[RichTextEditor] 已添加 umo-page-mode 类");
            }
            console.log("[RichTextEditor] 分页模式DOM应该已更新");
          }, 500);
        } else {
          console.warn("[RichTextEditor] setLayout方法不可用");
        }
      } catch (error) {
        console.error("[RichTextEditor] 切换分页模式失败:", error);
      }
    };
    const handleContentChange = () => {
      console.log("[RichTextEditor] ✨ 内容变化 (@changed事件)");
      if (!umoEditorRef.value) return;
      try {
        const html = umoEditorRef.value.getHTML();
        console.log("[RichTextEditor] 当前内容长度:", html.length);
        console.log("[RichTextEditor] 之前内容长度:", content.value.length);
        if (html !== content.value) {
          content.value = html;
          isDirty.value = true;
          console.log("[RichTextEditor] ✅ isDirty设置为true");
          emit("update:modelValue", html);
          debouncedRefreshOutline();
        } else {
          console.log("[RichTextEditor] ⚠️ 内容未变化，不更新isDirty");
        }
      } catch (error) {
        console.error("[RichTextEditor] 处理内容变化失败:", error);
      }
    };
    const setEditorContent = (html) => {
      if (!umoEditorRef.value) {
        console.warn("[RichTextEditor] 编辑器未就绪");
        return;
      }
      try {
        cleanupLocalStorage();
        if (typeof umoEditorRef.value.setContent === "function") {
          umoEditorRef.value.setContent(html);
          console.log("[RichTextEditor] 内容已更新，长度:", html.length);
          setTimeout(() => {
            cleanupLocalStorage();
          }, 100);
        } else {
          console.error("[RichTextEditor] setContent方法不存在");
        }
      } catch (error) {
        console.error("[RichTextEditor] 设置内容失败:", error);
        if (error.name === "QuotaExceededError") {
          console.warn("[RichTextEditor] localStorage超限，清理后重试");
          cleanupLocalStorage();
          try {
            umoEditorRef.value.setContent(html);
          } catch (retryError) {
            console.error("[RichTextEditor] 重试仍然失败:", retryError);
          }
        }
      }
    };
    const appendContent = (html) => {
      if (!umoEditorRef.value) {
        console.warn("[RichTextEditor] 编辑器未就绪，内容已缓存");
        content.value += html;
        return;
      }
      try {
        const currentHtml = umoEditorRef.value.getHTML();
        const newHtml = currentHtml + html;
        umoEditorRef.value.setContent(newHtml);
        content.value = newHtml;
        console.log("[RichTextEditor] 内容已追加，当前长度:", newHtml.length);
        nextTick(() => {
          scrollToBottom();
        });
        debouncedRefreshOutline();
      } catch (error) {
        console.error("[RichTextEditor] 追加内容失败:", error);
      }
    };
    const scrollToBottom = () => {
      var _a;
      try {
        const editor = (_a = umoEditorRef.value) == null ? void 0 : _a.getEditor();
        if (editor && editor.view) {
          const { dom } = editor.view;
          dom.scrollTop = dom.scrollHeight;
        }
      } catch (error) {
        console.error("[RichTextEditor] 滚动失败:", error);
      }
    };
    let refreshTimer = null;
    const debouncedRefreshOutline = () => {
      if (refreshTimer) clearTimeout(refreshTimer);
      refreshTimer = window.setTimeout(() => {
        refreshOutline();
      }, 500);
    };
    const refreshOutline = async () => {
      if (!umoEditorRef.value) return;
      if (!props.showOutline) return;
      refreshingOutline.value = true;
      try {
        if (typeof umoEditorRef.value.getTableOfContents === "function") {
          const toc = umoEditorRef.value.getTableOfContents();
          outline.value = toc || [];
          console.log("[RichTextEditor] 目录更新:", outline.value.length, "项", toc);
        } else {
          console.warn("[RichTextEditor] getTableOfContents方法不可用");
          outline.value = [];
        }
      } catch (error) {
        console.error("[RichTextEditor] 获取目录失败:", error);
        outline.value = [];
      } finally {
        refreshingOutline.value = false;
      }
    };
    const scrollToHeading = (item) => {
      if (!item) return;
      try {
        if (item.dom && typeof item.dom.scrollIntoView === "function") {
          item.dom.scrollIntoView({
            behavior: "smooth",
            block: "start"
          });
          activeHeadingId.value = item.id;
          return;
        }
        if (item.id) {
          const element = document.getElementById(item.id);
          if (element) {
            element.scrollIntoView({
              behavior: "smooth",
              block: "start"
            });
            activeHeadingId.value = item.id;
            return;
          }
        }
        console.warn("[RichTextEditor] 无法滚动到标题:", item);
      } catch (error) {
        console.error("[RichTextEditor] 滚动失败:", error);
      }
    };
    const handleSave = async () => {
      if (!isDirty.value || isStreaming.value) return;
      saving.value = true;
      try {
        emit("save", content.value);
        await nextTick();
        isDirty.value = false;
      } catch (error) {
        console.error("[RichTextEditor] 保存失败:", error);
        ElMessage.error("保存失败");
      } finally {
        saving.value = false;
      }
    };
    const toggleFullscreen = () => {
      isFullscreen.value = !isFullscreen.value;
      if (isFullscreen.value) {
        document.body.style.overflow = "hidden";
      } else {
        document.body.style.overflow = "";
      }
    };
    const clear = () => {
      content.value = "";
      setEditorContent("");
      outline.value = [];
      isDirty.value = false;
    };
    const getContent = () => {
      try {
        if (umoEditorRef.value && typeof umoEditorRef.value.getHTML === "function") {
          return umoEditorRef.value.getHTML();
        }
      } catch (error) {
        console.error("[RichTextEditor] 获取内容失败:", error);
      }
      return content.value;
    };
    const setContent = (html) => {
      content.value = html;
      setEditorContent(html);
      isDirty.value = false;
      setTimeout(() => {
        refreshOutline();
      }, 300);
    };
    const setStreaming = (streaming) => {
      console.log("[RichTextEditor] 设置流式状态:", streaming);
    };
    const getEditor = () => {
      var _a, _b;
      return (_b = (_a = umoEditorRef.value) == null ? void 0 : _a.getEditor) == null ? void 0 : _b.call(_a);
    };
    const insertPageBreak = () => {
      try {
        let editor = getEditor();
        if (editor && editor.__v_isRef) {
          editor = editor.value;
        }
        if (editor && editor.commands && editor.commands.setPageBreak) {
          editor.commands.setPageBreak();
          console.log("[RichTextEditor] 已插入原生分页符");
          return true;
        } else {
          console.warn("[RichTextEditor] setPageBreak 命令不可用");
          return false;
        }
      } catch (error) {
        console.error("[RichTextEditor] 插入分页符失败:", error);
        return false;
      }
    };
    __expose({
      getContent,
      setContent,
      appendContent,
      clear,
      refreshOutline,
      setStreaming,
      getEditor,
      // 暴露底层编辑器实例
      insertPageBreak
      // 新增：插入原生分页符
    });
    const cleanupLocalStorage = () => {
      try {
        const keys = Object.keys(localStorage);
        for (const key of keys) {
          if (key.startsWith("umo-editor:")) {
            localStorage.removeItem(key);
          }
        }
      } catch (error) {
        console.error("[RichTextEditor] 清理localStorage失败:", error);
      }
    };
    const originalSetItem = localStorage.setItem;
    let hasWarnedAboutStorage = false;
    const blockUmoEditorStorage = () => {
      localStorage.setItem = function(key, value) {
        if (key.startsWith("umo-editor:")) {
          if (!hasWarnedAboutStorage) {
            console.warn("[RichTextEditor] 已阻止 Umo Editor 写入 localStorage（大小:", value.length, "字节），后续将静默阻止");
            hasWarnedAboutStorage = true;
          }
          return;
        }
        return originalSetItem.call(localStorage, key, value);
      };
      console.log("[RichTextEditor] localStorage 保护已启用");
    };
    const restoreLocalStorage = () => {
      localStorage.setItem = originalSetItem;
      console.log("[RichTextEditor] localStorage拦截器已移除");
    };
    onMounted(() => {
      blockUmoEditorStorage();
      cleanupLocalStorage();
    });
    onBeforeUnmount(() => {
      if (isFullscreen.value) {
        document.body.style.overflow = "";
      }
      if (refreshTimer) {
        clearTimeout(refreshTimer);
      }
      restoreLocalStorage();
      cleanupLocalStorage();
    });
    return (_ctx, _cache) => {
      const _component_el_icon = ElIcon;
      const _component_el_tag = ElTag;
      const _component_el_button = ElButton;
      const _component_el_empty = ElEmpty;
      return openBlock(), createElementBlock("div", {
        class: normalizeClass(["rich-text-editor", { fullscreen: isFullscreen.value, streaming: isStreaming.value }])
      }, [
        createBaseVNode("div", _hoisted_1, [
          createBaseVNode("div", _hoisted_2, [
            createBaseVNode("h3", null, "✏️ " + toDisplayString(__props.title), 1),
            isStreaming.value ? (openBlock(), createBlock(_component_el_tag, {
              key: 0,
              type: "primary",
              effect: "plain"
            }, {
              default: withCtx(() => [
                createVNode(_component_el_icon, { class: "is-loading" }, {
                  default: withCtx(() => [
                    createVNode(unref(loading_default))
                  ]),
                  _: 1
                }),
                _cache[4] || (_cache[4] = createTextVNode(" AI生成中... ", -1))
              ]),
              _: 1
            })) : isDirty.value ? (openBlock(), createBlock(_component_el_tag, {
              key: 1,
              type: "warning"
            }, {
              default: withCtx(() => [..._cache[5] || (_cache[5] = [
                createTextVNode("有未保存的修改", -1)
              ])]),
              _: 1
            })) : (openBlock(), createBlock(_component_el_tag, {
              key: 2,
              type: "success"
            }, {
              default: withCtx(() => [..._cache[6] || (_cache[6] = [
                createTextVNode("已保存", -1)
              ])]),
              _: 1
            }))
          ]),
          createBaseVNode("div", _hoisted_3, [
            createVNode(_component_el_button, {
              onClick: toggleFullscreen,
              size: "small"
            }, {
              default: withCtx(() => [
                createVNode(_component_el_icon, null, {
                  default: withCtx(() => [
                    createVNode(unref(full_screen_default))
                  ]),
                  _: 1
                }),
                createTextVNode(" " + toDisplayString(isFullscreen.value ? "退出全屏" : "全屏编辑"), 1)
              ]),
              _: 1
            }),
            createVNode(_component_el_button, {
              type: "primary",
              onClick: _cache[0] || (_cache[0] = ($event) => emit("preview")),
              size: "small",
              disabled: !hasContent.value || isStreaming.value
            }, {
              default: withCtx(() => [
                createVNode(_component_el_icon, null, {
                  default: withCtx(() => [
                    createVNode(unref(view_default))
                  ]),
                  _: 1
                }),
                _cache[7] || (_cache[7] = createTextVNode(" 预览Word ", -1))
              ]),
              _: 1
            }, 8, ["disabled"]),
            createVNode(_component_el_button, {
              type: "success",
              onClick: _cache[1] || (_cache[1] = ($event) => emit("export")),
              size: "small",
              disabled: !hasContent.value || isStreaming.value
            }, {
              default: withCtx(() => [
                createVNode(_component_el_icon, null, {
                  default: withCtx(() => [
                    createVNode(unref(download_default))
                  ]),
                  _: 1
                }),
                _cache[8] || (_cache[8] = createTextVNode(" 导出Word ", -1))
              ]),
              _: 1
            }, 8, ["disabled"]),
            createVNode(_component_el_button, {
              type: "primary",
              loading: saving.value,
              disabled: !hasContent.value || isStreaming.value,
              onClick: handleSave,
              size: "small"
            }, {
              default: withCtx(() => [..._cache[9] || (_cache[9] = [
                createTextVNode(" 保存 ", -1)
              ])]),
              _: 1
            }, 8, ["loading", "disabled"])
          ])
        ]),
        createBaseVNode("div", _hoisted_4, [
          __props.showOutline && !outlineCollapsed.value ? (openBlock(), createElementBlock("div", _hoisted_5, [
            createBaseVNode("div", _hoisted_6, [
              _cache[10] || (_cache[10] = createBaseVNode("h4", null, "📑 目录", -1)),
              createVNode(_component_el_button, {
                text: "",
                size: "small",
                onClick: refreshOutline,
                loading: refreshingOutline.value
              }, {
                default: withCtx(() => [
                  createVNode(_component_el_icon, null, {
                    default: withCtx(() => [
                      createVNode(unref(refresh_default))
                    ]),
                    _: 1
                  })
                ]),
                _: 1
              }, 8, ["loading"])
            ]),
            createBaseVNode("div", _hoisted_7, [
              (openBlock(true), createElementBlock(Fragment, null, renderList(outline.value, (item, index) => {
                return openBlock(), createElementBlock("div", {
                  key: item.id || index,
                  class: normalizeClass(["outline-item", `level-${item.level}`, { active: activeHeadingId.value === item.id }]),
                  onClick: ($event) => scrollToHeading(item)
                }, [
                  createBaseVNode("span", _hoisted_9, toDisplayString(item.textContent), 1)
                ], 10, _hoisted_8);
              }), 128)),
              outline.value.length === 0 && !isStreaming.value ? (openBlock(), createBlock(_component_el_empty, {
                key: 0,
                description: "暂无标题",
                "image-size": 60
              })) : createCommentVNode("", true)
            ]),
            createBaseVNode("div", _hoisted_10, [
              createVNode(_component_el_button, {
                text: "",
                size: "small",
                onClick: _cache[2] || (_cache[2] = ($event) => outlineCollapsed.value = true)
              }, {
                default: withCtx(() => [
                  createVNode(_component_el_icon, null, {
                    default: withCtx(() => [
                      createVNode(unref(d_arrow_left_default))
                    ]),
                    _: 1
                  }),
                  _cache[11] || (_cache[11] = createTextVNode(" 折叠目录 ", -1))
                ]),
                _: 1
              })
            ])
          ])) : createCommentVNode("", true),
          __props.showOutline && outlineCollapsed.value ? (openBlock(), createElementBlock("div", {
            key: 1,
            class: "outline-toggle",
            onClick: _cache[3] || (_cache[3] = ($event) => outlineCollapsed.value = false)
          }, [
            createVNode(_component_el_icon, null, {
              default: withCtx(() => [
                createVNode(unref(d_arrow_right_default))
              ]),
              _: 1
            }),
            _cache[12] || (_cache[12] = createBaseVNode("span", { class: "toggle-text" }, "展开目录", -1))
          ])) : createCommentVNode("", true),
          createBaseVNode("div", _hoisted_11, [
            isStreaming.value ? (openBlock(), createElementBlock("div", _hoisted_12, [
              createVNode(_component_el_icon, { class: "is-loading" }, {
                default: withCtx(() => [
                  createVNode(unref(loading_default))
                ]),
                _: 1
              }),
              _cache[13] || (_cache[13] = createBaseVNode("span", null, "AI 正在生成内容，请稍候...", -1))
            ])) : createCommentVNode("", true),
            createVNode(unref(mC), mergeProps({
              ref_key: "umoEditorRef",
              ref: umoEditorRef
            }, editorOptions.value, {
              onChanged: handleContentChange,
              onCreated: handleEditorCreated
            }), null, 16)
          ])
        ])
      ], 2);
    };
  }
});
const RichTextEditor = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-347c6fc4"]]);
export {
  RichTextEditor as R
};
