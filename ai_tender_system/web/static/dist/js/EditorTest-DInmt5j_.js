import { d as defineComponent, r as ref, e as createElementBlock, o as openBlock, f as createVNode, k as createBlock, l as createCommentVNode, w as withCtx, aw as ElTabs, ax as ElTabPane, m as ElAlert, p as createTextVNode, at as ElUpload, n as createBaseVNode, ad as ElIcon, h as unref, aR as upload_filled_default, g as ElButton, as as ElCard, t as toDisplayString, A as ElMessage } from "./vendor-MtO928VE.js";
/* empty css                                                                           */
/* empty css                                                                         */
import { R as RichTextEditor } from "./RichTextEditor-Clg90zh2.js";
import { _ as _export_sfc } from "./index.js";
const _hoisted_1 = { class: "editor-test-page" };
const _hoisted_2 = { style: { "white-space": "pre-wrap", "font-size": "12px" } };
const _hoisted_3 = { class: "editor-container" };
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "EditorTest",
  setup(__props) {
    const editorRef = ref(null);
    const editorContent = ref("");
    const activeTab = ref("word");
    const selectedFile = ref(null);
    const converting = ref(false);
    const conversionLog = ref("");
    const handleFileChange = (file) => {
      if (file.raw) {
        selectedFile.value = file.raw;
        ElMessage.success(`已选择文件: ${file.name}`);
      }
    };
    const convertWordToHtml = async () => {
      if (!selectedFile.value) {
        ElMessage.warning("请先选择Word文档");
        return;
      }
      converting.value = true;
      conversionLog.value = "正在转换Word文档...\n";
      try {
        const formData = new FormData();
        formData.append("file", selectedFile.value);
        const uploadResponse = await fetch("/api/editor/upload-temp", {
          method: "POST",
          body: formData
        });
        if (!uploadResponse.ok) {
          throw new Error("文件上传失败");
        }
        const uploadResult = await uploadResponse.json();
        const filePath = uploadResult.file_path;
        conversionLog.value += `✓ 文件已上传: ${filePath}
`;
        conversionLog.value += "正在转换为HTML...\n";
        const convertResponse = await fetch("/api/editor/convert-word-to-html", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ file_path: filePath })
        });
        const result = await convertResponse.json();
        if (result.success && result.html_content) {
          conversionLog.value += `✓ 转换成功！HTML长度: ${result.html_content.length}
`;
          const pageBreakCount = (result.html_content.match(/page-break/g) || []).length;
          conversionLog.value += `✓ 检测到 ${pageBreakCount} 个分页符
`;
          editorContent.value = result.html_content;
          if (editorRef.value) {
            editorRef.value.setContent(result.html_content);
          }
          ElMessage.success("Word文档已加载到编辑器");
        } else {
          throw new Error(result.error || "转换失败");
        }
      } catch (error) {
        conversionLog.value += `❌ 错误: ${error.message}
`;
        ElMessage.error("转换失败: " + error.message);
      } finally {
        converting.value = false;
      }
    };
    const loadTestContentWithBreaks = () => {
      const testContent = `
<h1>第一章 项目概述</h1>
<p>这是第一章的内容。我们将在这里介绍项目的基本情况和背景。</p>
<p>项目名称：智能标书管理系统</p>
<p>项目目标：提高标书编写效率，降低人工成本。</p>

<hr data-type="page-break" />

<h1>第二章 技术方案</h1>
<p>本章介绍我们采用的技术方案和架构设计。</p>
<h2>2.1 系统架构</h2>
<p>系统采用前后端分离架构，前端使用Vue3 + TypeScript，后端使用Python Flask。</p>
<h2>2.2 技术栈</h2>
<ul>
  <li>前端：Vue3 + Element Plus + UmoEditor</li>
  <li>后端：Python Flask + SQLAlchemy</li>
  <li>数据库：SQLite / MySQL</li>
</ul>

<hr data-type="page-break" />

<h1>第三章 实施计划</h1>
<p>本章描述项目的实施计划和时间安排。</p>
<table>
  <tr>
    <th>阶段</th>
    <th>任务</th>
    <th>时间</th>
  </tr>
  <tr>
    <td>第一阶段</td>
    <td>需求分析</td>
    <td>2周</td>
  </tr>
  <tr>
    <td>第二阶段</td>
    <td>系统开发</td>
    <td>8周</td>
  </tr>
  <tr>
    <td>第三阶段</td>
    <td>测试上线</td>
    <td>2周</td>
  </tr>
</table>

<hr data-type="page-break" />

<h1>第四章 总结</h1>
<p>通过本项目的实施，将大幅提升标书编写效率。</p>
<p><strong>预期成果：</strong></p>
<ul>
  <li>标书编写时间缩短50%</li>
  <li>错误率降低80%</li>
  <li>用户满意度提升</li>
</ul>
  `;
      editorContent.value = testContent;
      if (editorRef.value) {
        editorRef.value.setContent(testContent);
      }
      ElMessage.success("测试内容已加载（包含3个分页符）");
    };
    const insertPageBreak = () => {
      if (!editorRef.value) {
        ElMessage.warning("编辑器未就绪");
        return;
      }
      const pageBreakHtml = '<hr data-type="page-break" />';
      const currentContent = editorRef.value.getContent();
      const newContent = currentContent + pageBreakHtml;
      editorRef.value.setContent(newContent);
      ElMessage.success("已插入分页符");
    };
    const clearEditor = () => {
      editorContent.value = "";
      if (editorRef.value) {
        editorRef.value.clear();
      }
      ElMessage.success("编辑器已清空");
    };
    const loadLongContent = () => {
      const longParagraph = "<p>" + "这是一个很长的段落内容。".repeat(50) + "</p>\n";
      const longContent = `
<h1>第一章 项目背景</h1>
${longParagraph.repeat(30)}

<div class="umo-page-break" data-line-number="false" data-content="分页符"></div>

<h1>第二章 需求分析</h1>
${longParagraph.repeat(30)}

<div class="umo-page-break" data-line-number="false" data-content="分页符"></div>

<h1>第三章 技术方案</h1>
${longParagraph.repeat(30)}

<div class="umo-page-break" data-line-number="false" data-content="分页符"></div>

<h1>第四章 实施计划</h1>
${longParagraph.repeat(30)}

<div class="umo-page-break" data-line-number="false" data-content="分页符"></div>

<h1>第五章 总结</h1>
${longParagraph.repeat(30)}
  `;
      editorContent.value = longContent;
      if (editorRef.value) {
        editorRef.value.setContent(longContent);
      }
      ElMessage.success("超长文档已加载（包含原生分页符）");
    };
    const insertNativePageBreak = () => {
      if (!editorRef.value) {
        ElMessage.warning("编辑器未就绪");
        return;
      }
      try {
        console.log("[EditorTest] 准备插入原生分页符...");
        const success = editorRef.value.insertPageBreak();
        console.log("[EditorTest] insertPageBreak 返回:", success);
        if (success) {
          ElMessage.success("✅ 已插入原生分页符");
          setTimeout(() => {
            const html = editorRef.value.getContent();
            console.log("[EditorTest] 当前HTML长度:", html.length);
            const pageBreaks = html.match(/<div class="umo-page-break"[^>]*>/g);
            console.log("[EditorTest] 找到分页符数量:", (pageBreaks == null ? void 0 : pageBreaks.length) || 0);
            if (pageBreaks && pageBreaks.length > 0) {
              console.log("[EditorTest] 分页符HTML:", pageBreaks);
            }
            const container = document.querySelector('[contenteditable="true"]');
            if (container) {
              const domBreaks = container.querySelectorAll(".umo-page-break");
              console.log("[EditorTest] DOM中的分页符数量:", domBreaks.length);
            }
          }, 200);
        } else {
          ElMessage.error("插入失败，返回false");
        }
      } catch (error) {
        console.error("插入原生分页符失败:", error);
        ElMessage.error("插入失败: " + error.message);
      }
    };
    const debugEditor = () => {
      var _a, _b, _c, _d;
      if (!editorRef.value) {
        ElMessage.warning("编辑器未就绪");
        return;
      }
      console.log("========== 编辑器调试信息 ==========");
      console.log("1. editorRef 方法:", Object.keys(editorRef.value).filter((k) => typeof editorRef.value[k] === "function"));
      let editor = editorRef.value.getEditor();
      if (editor && editor.__v_isRef) {
        console.log("2a. 检测到RefImpl，正在解包...");
        editor = editor.value;
      }
      if (editor) {
        console.log("2. 底层编辑器类型:", (_a = editor.constructor) == null ? void 0 : _a.name);
        console.log("3. 编辑器对象:", editor);
        console.log("4. 可用命令:", editor.commands ? Object.keys(editor.commands) : "无");
        if (editor.commands) {
          const pageCommands = Object.keys(editor.commands).filter(
            (k) => k.toLowerCase().includes("page") || k.toLowerCase().includes("break")
          );
          console.log("5. 分页相关命令:", pageCommands);
        }
        console.log("6. 编辑器属性:", Object.keys(editor));
        console.log("7. 当前布局:", (_d = (_c = (_b = editor.view) == null ? void 0 : _b.dom) == null ? void 0 : _c.closest(".umo-editor-container")) == null ? void 0 : _d.classList);
      } else {
        console.log("2. 底层编辑器未找到");
      }
      console.log("================================");
      ElMessage.success("调试信息已输出到Console，请查看");
    };
    const forcePageMode = () => {
      var _a, _b, _c;
      if (!editorRef.value) {
        ElMessage.warning("编辑器未就绪");
        return;
      }
      try {
        let editor = editorRef.value.getEditor();
        if (editor && editor.__v_isRef) {
          editor = editor.value;
        }
        console.log("[EditorTest] 当前布局:", (_b = (_a = editor.extensionStorage) == null ? void 0 : _a.page) == null ? void 0 : _b.layout);
        if (editorRef.value.setLayout) {
          editorRef.value.setLayout("page");
          console.log('[EditorTest] ✓ 调用了 setLayout("page")');
        }
        if ((_c = editor.extensionStorage) == null ? void 0 : _c.page) {
          editor.extensionStorage.page.layout = "page";
          console.log('[EditorTest] ✓ 直接设置 extensionStorage.page.layout = "page"');
        }
        const container = document.querySelector(".umo-editor-container");
        if (container) {
          container.classList.add("page-layout");
          container.classList.remove("continuous-layout");
          console.log("[EditorTest] ✓ 添加了 page-layout 类");
        }
        const allButtons = document.querySelectorAll('.umo-editor-container button, .umo-toolbar button, [role="button"]');
        console.log("[EditorTest] 工具栏按钮总数:", allButtons.length);
        const layoutButtons = Array.from(allButtons).filter((btn) => {
          const text = btn.textContent || "";
          const title = btn.getAttribute("title") || "";
          const ariaLabel = btn.getAttribute("aria-label") || "";
          return text.includes("页面") || text.includes("布局") || title.includes("页面") || title.includes("布局") || title.toLowerCase().includes("layout") || ariaLabel.includes("页面") || ariaLabel.includes("布局");
        });
        console.log("[EditorTest] 找到可能的布局按钮:", layoutButtons.length);
        layoutButtons.forEach((btn, i) => {
          console.log(`  ${i + 1}. ${btn.textContent || btn.getAttribute("title")}`, btn);
        });
        if (layoutButtons.length > 0) {
          console.log("[EditorTest] 尝试点击第一个布局按钮...");
          layoutButtons[0].click();
        }
        setTimeout(() => {
          var _a2, _b2;
          console.log("[EditorTest] 300ms后布局:", (_b2 = (_a2 = editor.extensionStorage) == null ? void 0 : _a2.page) == null ? void 0 : _b2.layout);
          const pages = document.querySelectorAll(".umo-page, [data-page-number]");
          console.log("[EditorTest] 页面元素数量:", pages.length);
        }, 300);
        ElMessage.success("已尝试强制启用分页模式，请查看Console");
      } catch (error) {
        console.error("[EditorTest] 强制启用失败:", error);
        ElMessage.error("操作失败: " + error.message);
      }
    };
    const handleEditorReady = () => {
      console.log("[EditorTest] 编辑器已就绪");
      setTimeout(() => {
        debugEditor();
      }, 500);
    };
    return (_ctx, _cache) => {
      const _component_el_alert = ElAlert;
      const _component_el_icon = ElIcon;
      const _component_el_upload = ElUpload;
      const _component_el_button = ElButton;
      const _component_el_tab_pane = ElTabPane;
      const _component_el_tabs = ElTabs;
      const _component_el_card = ElCard;
      return openBlock(), createElementBlock("div", _hoisted_1, [
        createVNode(_component_el_card, { shadow: "never" }, {
          header: withCtx(() => [..._cache[2] || (_cache[2] = [
            createBaseVNode("h2", null, "📝 编辑器 & 分页符测试", -1)
          ])]),
          default: withCtx(() => [
            createVNode(_component_el_tabs, {
              modelValue: activeTab.value,
              "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => activeTab.value = $event),
              type: "card"
            }, {
              default: withCtx(() => [
                createVNode(_component_el_tab_pane, {
                  label: "Word文档测试",
                  name: "word"
                }, {
                  default: withCtx(() => [
                    createVNode(_component_el_alert, {
                      type: "info",
                      closable: false,
                      style: { "margin-bottom": "16px" }
                    }, {
                      default: withCtx(() => [..._cache[3] || (_cache[3] = [
                        createTextVNode(" 💡 上传一个包含分页符的Word文档，测试分页符是否正确显示 ", -1)
                      ])]),
                      _: 1
                    }),
                    createVNode(_component_el_upload, {
                      class: "upload-demo",
                      drag: "",
                      "auto-upload": false,
                      limit: 1,
                      accept: ".doc,.docx",
                      "on-change": handleFileChange
                    }, {
                      tip: withCtx(() => [..._cache[4] || (_cache[4] = [
                        createBaseVNode("div", { class: "el-upload__tip" }, " 仅支持 .doc / .docx 格式文件 ", -1)
                      ])]),
                      default: withCtx(() => [
                        createVNode(_component_el_icon, { class: "el-icon--upload" }, {
                          default: withCtx(() => [
                            createVNode(unref(upload_filled_default))
                          ]),
                          _: 1
                        }),
                        _cache[5] || (_cache[5] = createBaseVNode("div", { class: "el-upload__text" }, [
                          createTextVNode(" 拖拽Word文档到此处或 "),
                          createBaseVNode("em", null, "点击上传")
                        ], -1))
                      ]),
                      _: 1
                    }),
                    selectedFile.value ? (openBlock(), createBlock(_component_el_button, {
                      key: 0,
                      type: "primary",
                      loading: converting.value,
                      onClick: convertWordToHtml,
                      style: { "margin-top": "16px" }
                    }, {
                      default: withCtx(() => [..._cache[6] || (_cache[6] = [
                        createTextVNode(" 转换并加载到编辑器 ", -1)
                      ])]),
                      _: 1
                    }, 8, ["loading"])) : createCommentVNode("", true)
                  ]),
                  _: 1
                }),
                createVNode(_component_el_tab_pane, {
                  label: "手动分页符测试",
                  name: "manual"
                }, {
                  default: withCtx(() => [
                    createVNode(_component_el_alert, {
                      type: "info",
                      closable: false,
                      style: { "margin-bottom": "16px" }
                    }, {
                      default: withCtx(() => [..._cache[7] || (_cache[7] = [
                        createTextVNode(" 💡 点击下方按钮加载包含分页符的测试内容 ", -1)
                      ])]),
                      _: 1
                    }),
                    createVNode(_component_el_button, {
                      type: "primary",
                      onClick: loadTestContentWithBreaks
                    }, {
                      default: withCtx(() => [..._cache[8] || (_cache[8] = [
                        createTextVNode(" 加载测试内容（带分页符） ", -1)
                      ])]),
                      _: 1
                    }),
                    createVNode(_component_el_button, {
                      onClick: insertPageBreak,
                      disabled: !editorRef.value
                    }, {
                      default: withCtx(() => [..._cache[9] || (_cache[9] = [
                        createTextVNode(" 插入HR分页符 ", -1)
                      ])]),
                      _: 1
                    }, 8, ["disabled"]),
                    createVNode(_component_el_button, {
                      onClick: insertNativePageBreak,
                      disabled: !editorRef.value,
                      type: "success"
                    }, {
                      default: withCtx(() => [..._cache[10] || (_cache[10] = [
                        createTextVNode(" 插入原生分页符（实验） ", -1)
                      ])]),
                      _: 1
                    }, 8, ["disabled"]),
                    createVNode(_component_el_button, {
                      onClick: debugEditor,
                      disabled: !editorRef.value,
                      type: "warning"
                    }, {
                      default: withCtx(() => [..._cache[11] || (_cache[11] = [
                        createTextVNode(" 调试编辑器API ", -1)
                      ])]),
                      _: 1
                    }, 8, ["disabled"]),
                    createVNode(_component_el_button, {
                      onClick: forcePageMode,
                      disabled: !editorRef.value,
                      type: "danger"
                    }, {
                      default: withCtx(() => [..._cache[12] || (_cache[12] = [
                        createTextVNode(" 强制启用分页模式 ", -1)
                      ])]),
                      _: 1
                    }, 8, ["disabled"]),
                    createVNode(_component_el_button, {
                      onClick: clearEditor,
                      disabled: !editorRef.value
                    }, {
                      default: withCtx(() => [..._cache[13] || (_cache[13] = [
                        createTextVNode(" 清空编辑器 ", -1)
                      ])]),
                      _: 1
                    }, 8, ["disabled"])
                  ]),
                  _: 1
                }),
                createVNode(_component_el_tab_pane, {
                  label: "长文档测试",
                  name: "long"
                }, {
                  default: withCtx(() => [
                    createVNode(_component_el_alert, {
                      type: "info",
                      closable: false,
                      style: { "margin-bottom": "16px" }
                    }, {
                      default: withCtx(() => [..._cache[14] || (_cache[14] = [
                        createTextVNode(" 💡 加载超长文档，测试编辑器性能和分页布局 ", -1)
                      ])]),
                      _: 1
                    }),
                    createVNode(_component_el_button, {
                      type: "primary",
                      onClick: loadLongContent
                    }, {
                      default: withCtx(() => [..._cache[15] || (_cache[15] = [
                        createTextVNode(" 加载长文档（4章节） ", -1)
                      ])]),
                      _: 1
                    })
                  ]),
                  _: 1
                })
              ]),
              _: 1
            }, 8, ["modelValue"])
          ]),
          _: 1
        }),
        conversionLog.value ? (openBlock(), createBlock(_component_el_card, {
          key: 0,
          shadow: "never",
          style: { "margin-top": "16px" }
        }, {
          header: withCtx(() => [..._cache[16] || (_cache[16] = [
            createBaseVNode("h3", null, "转换日志", -1)
          ])]),
          default: withCtx(() => [
            createBaseVNode("pre", _hoisted_2, toDisplayString(conversionLog.value), 1)
          ]),
          _: 1
        })) : createCommentVNode("", true),
        createVNode(_component_el_card, {
          shadow: "never",
          style: { "margin-top": "16px" }
        }, {
          header: withCtx(() => [..._cache[17] || (_cache[17] = [
            createBaseVNode("h3", null, "富文本编辑器", -1)
          ])]),
          default: withCtx(() => [
            createBaseVNode("div", _hoisted_3, [
              createVNode(unref(RichTextEditor), {
                ref_key: "editorRef",
                ref: editorRef,
                modelValue: editorContent.value,
                "onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => editorContent.value = $event),
                title: "测试文档",
                height: 800,
                onReady: handleEditorReady
              }, null, 8, ["modelValue"])
            ])
          ]),
          _: 1
        })
      ]);
    };
  }
});
const EditorTest = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-e5c086fb"]]);
export {
  EditorTest as default
};
