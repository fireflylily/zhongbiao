import { d as defineComponent, r as ref, c as computed, S as onMounted, e as createElementBlock, o as openBlock, N as createStaticVNode, n as createBaseVNode, f as createVNode, k as createBlock, l as createCommentVNode, w as withCtx, ak as ElRow, ai as ElCol, s as ElFormItem, Y as ElSelect, F as Fragment, V as renderList, h as unref, W as ElOption, t as toDisplayString, as as ElCard, ad as ElIcon, ae as document_default, X as ElTag, p as createTextVNode, aB as ElText, g as ElButton, aD as view_default, q as ElForm, y as ElInput, aa as withDirectives, aJ as vLoading, bs as video_play_default, aT as refresh_default, a7 as ElScrollbar, ar as ElEmpty, aE as download_default, A as ElMessage } from "./vendor-MtO928VE.js";
import { _ as _export_sfc } from "./index.js";
import { u as useProjectDocuments } from "./useProjectDocuments-CobiuthK.js";
import { t as tenderApi } from "./tender-DvsgeLWX.js";
/* empty css                                                                           */
import { D as DocumentPreview } from "./DocumentPreview-9ke4Yi2d.js";
import { c as companyApi } from "./company-z4Xg082l.js";
import "./project-X4Kuz_iO.js";
/* empty css                                                                         */
const _hoisted_1 = { class: "outline-comparison-wrapper" };
const _hoisted_2 = { class: "main-content" };
const _hoisted_3 = { style: { "color": "var(--text-secondary)", "font-size": "12px", "margin-left": "8px" } };
const _hoisted_4 = { class: "document-item" };
const _hoisted_5 = { class: "document-header" };
const _hoisted_6 = { class: "document-info" };
const _hoisted_7 = { class: "document-item" };
const _hoisted_8 = { class: "document-header" };
const _hoisted_9 = { class: "document-info" };
const _hoisted_10 = { class: "card-header" };
const _hoisted_11 = { class: "card-title" };
const _hoisted_12 = { class: "card-header" };
const _hoisted_13 = { class: "card-title" };
const _hoisted_14 = { class: "action-section" };
const _hoisted_15 = { class: "card-header" };
const _hoisted_16 = { class: "result-section" };
const _hoisted_17 = { class: "result-title" };
const _hoisted_18 = { class: "outline-content" };
const _hoisted_19 = {
  key: 0,
  class: "outline-text"
};
const _hoisted_20 = { class: "result-meta" };
const _hoisted_21 = { class: "result-section" };
const _hoisted_22 = { class: "result-title" };
const _hoisted_23 = { class: "outline-content" };
const _hoisted_24 = {
  key: 0,
  class: "outline-text"
};
const _hoisted_25 = { class: "result-meta" };
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "OutlineComparison",
  setup(__props) {
    const {
      projects: projectsFromComposable,
      currentDocuments,
      loadProjects: loadProjectsFromComposable,
      handleProjectChange: handleProjectChangeComposable
    } = useProjectDocuments();
    const projects = projectsFromComposable;
    const companies = ref([]);
    const selectedProjectId = ref(null);
    const selectedCompanyId = ref(null);
    const showTenderFile = ref(false);
    const showTechnicalFile = ref(false);
    const previewVisible = ref(false);
    const previewFileUrl = ref("");
    const previewFileName = ref("");
    const group1Prompt = ref("正在加载提示词配置...");
    const promptLoading = ref(true);
    const group2Model = ref("");
    const group2Prompt = ref("");
    const generating = ref(false);
    const hasResults = ref(false);
    const group1Result = ref("");
    const group2Result = ref("");
    const group1Time = ref("");
    const group2Time = ref("");
    const canGenerate = computed(() => {
      return selectedProjectId.value && selectedCompanyId.value && group2Model.value && group2Prompt.value;
    });
    function formatFileSize(bytes) {
      if (bytes === 0) return "未知大小";
      const k = 1024;
      const sizes = ["B", "KB", "MB", "GB"];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return Math.round(bytes / Math.pow(k, i) * 100) / 100 + " " + sizes[i];
    }
    async function loadProjects() {
      await loadProjectsFromComposable();
    }
    async function loadCompanies() {
      try {
        const response = await companyApi.getCompanies();
        if (response.success && response.data) {
          companies.value = response.data;
        }
      } catch (error) {
        console.error("加载公司列表失败:", error);
        ElMessage.error("加载公司列表失败");
      }
    }
    async function loadPrompts() {
      promptLoading.value = true;
      try {
        const response = await tenderApi.getOutlineGenerationPrompts();
        console.log("提示词API响应:", response);
        if (response.success && response.data) {
          const promptData = response.data.prompts || response.data;
          group1Prompt.value = promptData.generate_outline || "未找到提示词配置";
          console.log("✓ 提示词已加载，长度:", group1Prompt.value.length);
        } else {
          group1Prompt.value = "未找到提示词配置";
        }
      } catch (error) {
        console.error("加载提示词配置失败:", error);
        ElMessage.error("加载提示词配置失败");
        group1Prompt.value = "加载失败，请刷新页面重试";
      } finally {
        promptLoading.value = false;
      }
    }
    async function handleProjectChange(projectId) {
      showTenderFile.value = false;
      showTechnicalFile.value = false;
      if (!projectId) {
        selectedCompanyId.value = null;
        await handleProjectChangeComposable(null);
        return;
      }
      await handleProjectChangeComposable(projectId, {
        onClear: () => {
          showTenderFile.value = false;
          showTechnicalFile.value = false;
        },
        onDocumentsLoaded: (docs) => {
          if (docs.tenderFile) {
            showTenderFile.value = true;
            console.log("✅ 标书文件已加载:", docs.tenderFile.name);
          }
          if (docs.technicalFile) {
            showTechnicalFile.value = true;
            console.log("✅ 技术文件已加载:", docs.technicalFile.name);
          }
        }
      });
      const project = projects.value.find((p) => p.id === projectId);
      if (project && project.company_id) {
        selectedCompanyId.value = project.company_id;
      }
    }
    async function handleGenerate() {
      if (!canGenerate.value) {
        ElMessage.warning("请完整填写所有配置项");
        return;
      }
      generating.value = true;
      hasResults.value = false;
      try {
        ElMessage.info("大纲生成功能开发中...");
        setTimeout(() => {
          group1Result.value = "第一章 项目概述\n1.1 项目背景\n1.2 项目目标\n第二章 技术方案\n2.1 系统架构\n2.2 技术选型";
          group2Result.value = "第一章 项目介绍\n1.1 背景分析\n1.2 目标设定\n第二章 解决方案\n2.1 架构设计\n2.2 技术栈";
          group1Time.value = "2.3秒";
          group2Time.value = "3.1秒";
          hasResults.value = true;
          generating.value = false;
        }, 2e3);
      } catch (error) {
        console.error("生成失败:", error);
        ElMessage.error("生成失败");
        generating.value = false;
      }
    }
    function handleReset() {
      selectedProjectId.value = null;
      selectedCompanyId.value = null;
      group2Model.value = "";
      group2Prompt.value = "";
      hasResults.value = false;
      group1Result.value = "";
      group2Result.value = "";
      group1Time.value = "";
      group2Time.value = "";
    }
    function previewTechnicalFile() {
      if (!currentDocuments.value.technicalFile) {
        ElMessage.warning("技术文件不存在");
        return;
      }
      previewFileUrl.value = currentDocuments.value.technicalFile.url;
      previewFileName.value = currentDocuments.value.technicalFile.name;
      previewVisible.value = true;
    }
    onMounted(() => {
      loadProjects();
      loadCompanies();
      loadPrompts();
    });
    return (_ctx, _cache) => {
      const _component_el_option = ElOption;
      const _component_el_select = ElSelect;
      const _component_el_form_item = ElFormItem;
      const _component_el_col = ElCol;
      const _component_el_row = ElRow;
      const _component_el_card = ElCard;
      const _component_el_icon = ElIcon;
      const _component_el_tag = ElTag;
      const _component_el_text = ElText;
      const _component_el_button = ElButton;
      const _component_el_input = ElInput;
      const _component_el_form = ElForm;
      const _component_el_empty = ElEmpty;
      const _component_el_scrollbar = ElScrollbar;
      const _directive_loading = vLoading;
      return openBlock(), createElementBlock("div", _hoisted_1, [
        _cache[25] || (_cache[25] = createStaticVNode('<div class="page-header" data-v-97b6cc04><div class="header-content" data-v-97b6cc04><div class="title-section" data-v-97b6cc04><i class="bi-diagram-3 header-icon" data-v-97b6cc04></i><div class="title-group" data-v-97b6cc04><h1 class="page-title" data-v-97b6cc04>大纲生成对比</h1><p class="page-description" data-v-97b6cc04>对比不同模型和提示词生成的技术方案大纲效果</p></div></div></div></div>', 1)),
        createBaseVNode("div", _hoisted_2, [
          createVNode(_component_el_card, { class: "selection-card" }, {
            default: withCtx(() => [
              createVNode(_component_el_row, { gutter: 16 }, {
                default: withCtx(() => [
                  createVNode(_component_el_col, {
                    xs: 24,
                    sm: 12
                  }, {
                    default: withCtx(() => [
                      createVNode(_component_el_form_item, { label: "选择项目" }, {
                        default: withCtx(() => [
                          createVNode(_component_el_select, {
                            modelValue: selectedProjectId.value,
                            "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => selectedProjectId.value = $event),
                            placeholder: "请选择项目",
                            filterable: "",
                            clearable: "",
                            onChange: handleProjectChange
                          }, {
                            default: withCtx(() => [
                              (openBlock(true), createElementBlock(Fragment, null, renderList(unref(projects), (project) => {
                                return openBlock(), createBlock(_component_el_option, {
                                  key: project.id,
                                  label: project.project_name,
                                  value: project.id
                                }, {
                                  default: withCtx(() => [
                                    createBaseVNode("span", null, toDisplayString(project.project_name), 1),
                                    createBaseVNode("span", _hoisted_3, toDisplayString(project.company_name), 1)
                                  ]),
                                  _: 2
                                }, 1032, ["label", "value"]);
                              }), 128))
                            ]),
                            _: 1
                          }, 8, ["modelValue"])
                        ]),
                        _: 1
                      })
                    ]),
                    _: 1
                  }),
                  createVNode(_component_el_col, {
                    xs: 24,
                    sm: 12
                  }, {
                    default: withCtx(() => [
                      createVNode(_component_el_form_item, { label: "应答公司" }, {
                        default: withCtx(() => [
                          createVNode(_component_el_select, {
                            modelValue: selectedCompanyId.value,
                            "onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => selectedCompanyId.value = $event),
                            placeholder: "请选择应答公司",
                            filterable: "",
                            clearable: ""
                          }, {
                            default: withCtx(() => [
                              (openBlock(true), createElementBlock(Fragment, null, renderList(companies.value, (company) => {
                                return openBlock(), createBlock(_component_el_option, {
                                  key: company.company_id,
                                  label: company.company_name || company.name,
                                  value: company.company_id
                                }, null, 8, ["label", "value"]);
                              }), 128))
                            ]),
                            _: 1
                          }, 8, ["modelValue"])
                        ]),
                        _: 1
                      })
                    ]),
                    _: 1
                  })
                ]),
                _: 1
              })
            ]),
            _: 1
          }),
          selectedProjectId.value && (showTenderFile.value || showTechnicalFile.value) ? (openBlock(), createBlock(_component_el_card, {
            key: 0,
            class: "documents-card"
          }, {
            header: withCtx(() => [..._cache[6] || (_cache[6] = [
              createBaseVNode("div", { class: "card-header" }, [
                createBaseVNode("span", { class: "card-title" }, [
                  createBaseVNode("i", { class: "bi-folder2-open" }),
                  createTextVNode(" 项目文档 ")
                ])
              ], -1)
            ])]),
            default: withCtx(() => [
              createVNode(_component_el_row, { gutter: 16 }, {
                default: withCtx(() => [
                  showTenderFile.value && unref(currentDocuments).tenderFile ? (openBlock(), createBlock(_component_el_col, {
                    key: 0,
                    xs: 24,
                    sm: 12
                  }, {
                    default: withCtx(() => [
                      createBaseVNode("div", _hoisted_4, [
                        createBaseVNode("div", _hoisted_5, [
                          createVNode(_component_el_icon, {
                            class: "document-icon",
                            color: "#409EFF"
                          }, {
                            default: withCtx(() => [
                              createVNode(unref(document_default))
                            ]),
                            _: 1
                          }),
                          _cache[7] || (_cache[7] = createBaseVNode("span", { class: "document-label" }, "招标文档：", -1))
                        ]),
                        createBaseVNode("div", _hoisted_6, [
                          createVNode(_component_el_tag, {
                            type: "info",
                            size: "large"
                          }, {
                            default: withCtx(() => [
                              createTextVNode(toDisplayString(unref(currentDocuments).tenderFile.name), 1)
                            ]),
                            _: 1
                          }),
                          createVNode(_component_el_text, {
                            size: "small",
                            type: "info",
                            style: { "margin-left": "8px" }
                          }, {
                            default: withCtx(() => [
                              createTextVNode(toDisplayString(formatFileSize(unref(currentDocuments).tenderFile.size)), 1)
                            ]),
                            _: 1
                          })
                        ])
                      ])
                    ]),
                    _: 1
                  })) : createCommentVNode("", true),
                  showTechnicalFile.value && unref(currentDocuments).technicalFile ? (openBlock(), createBlock(_component_el_col, {
                    key: 1,
                    xs: 24,
                    sm: 12
                  }, {
                    default: withCtx(() => [
                      createBaseVNode("div", _hoisted_7, [
                        createBaseVNode("div", _hoisted_8, [
                          createVNode(_component_el_icon, {
                            class: "document-icon",
                            color: "#67C23A"
                          }, {
                            default: withCtx(() => [
                              createVNode(unref(document_default))
                            ]),
                            _: 1
                          }),
                          _cache[8] || (_cache[8] = createBaseVNode("span", { class: "document-label" }, "技术需求文档：", -1))
                        ]),
                        createBaseVNode("div", _hoisted_9, [
                          createVNode(_component_el_tag, {
                            type: "success",
                            size: "large"
                          }, {
                            default: withCtx(() => [
                              createTextVNode(toDisplayString(unref(currentDocuments).technicalFile.name), 1)
                            ]),
                            _: 1
                          }),
                          createVNode(_component_el_text, {
                            size: "small",
                            type: "info",
                            style: { "margin-left": "8px" }
                          }, {
                            default: withCtx(() => [
                              createTextVNode(toDisplayString(formatFileSize(unref(currentDocuments).technicalFile.size)), 1)
                            ]),
                            _: 1
                          }),
                          createVNode(_component_el_button, {
                            type: "primary",
                            size: "small",
                            plain: "",
                            style: { "margin-left": "12px" },
                            onClick: previewTechnicalFile
                          }, {
                            default: withCtx(() => [
                              createVNode(_component_el_icon, { style: { "margin-right": "4px" } }, {
                                default: withCtx(() => [
                                  createVNode(unref(view_default))
                                ]),
                                _: 1
                              }),
                              _cache[9] || (_cache[9] = createTextVNode(" 预览 ", -1))
                            ]),
                            _: 1
                          })
                        ])
                      ])
                    ]),
                    _: 1
                  })) : createCommentVNode("", true)
                ]),
                _: 1
              })
            ]),
            _: 1
          })) : createCommentVNode("", true),
          createVNode(_component_el_row, {
            gutter: 16,
            style: { "margin-top": "16px" }
          }, {
            default: withCtx(() => [
              createVNode(_component_el_col, {
                xs: 24,
                lg: 12
              }, {
                default: withCtx(() => [
                  createVNode(_component_el_card, { class: "config-card" }, {
                    header: withCtx(() => [
                      createBaseVNode("div", _hoisted_10, [
                        createBaseVNode("span", _hoisted_11, [
                          createVNode(_component_el_tag, {
                            type: "success",
                            size: "small"
                          }, {
                            default: withCtx(() => [..._cache[10] || (_cache[10] = [
                              createTextVNode("基准组", -1)
                            ])]),
                            _: 1
                          }),
                          _cache[11] || (_cache[11] = createBaseVNode("span", { style: { "margin-left": "8px" } }, "当前配置", -1))
                        ])
                      ])
                    ]),
                    default: withCtx(() => [
                      createVNode(_component_el_form, { "label-position": "top" }, {
                        default: withCtx(() => [
                          createVNode(_component_el_form_item, { label: "模型" }, {
                            default: withCtx(() => [
                              createVNode(_component_el_input, {
                                value: "gpt-4o-mini",
                                disabled: ""
                              }, {
                                prepend: withCtx(() => [..._cache[12] || (_cache[12] = [
                                  createBaseVNode("i", { class: "bi-robot" }, null, -1)
                                ])]),
                                _: 1
                              })
                            ]),
                            _: 1
                          }),
                          createVNode(_component_el_form_item, { label: "提示词" }, {
                            extra: withCtx(() => [
                              promptLoading.value ? (openBlock(), createBlock(_component_el_text, {
                                key: 0,
                                size: "small",
                                type: "warning"
                              }, {
                                default: withCtx(() => [..._cache[13] || (_cache[13] = [
                                  createTextVNode(" 正在从后端加载真实提示词配置... ", -1)
                                ])]),
                                _: 1
                              })) : (openBlock(), createBlock(_component_el_text, {
                                key: 1,
                                size: "small",
                                type: "success"
                              }, {
                                default: withCtx(() => [..._cache[14] || (_cache[14] = [
                                  createTextVNode(" ✓ 已加载系统提示词模板。实际使用时，{analysis} 占位符会被替换为标书的具体需求分析结果，确保每个标书的大纲都是个性化的。 ", -1)
                                ])]),
                                _: 1
                              }))
                            ]),
                            default: withCtx(() => [
                              withDirectives(createVNode(_component_el_input, {
                                modelValue: group1Prompt.value,
                                "onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => group1Prompt.value = $event),
                                type: "textarea",
                                rows: 12,
                                placeholder: "当前使用的大纲生成提示词",
                                disabled: ""
                              }, null, 8, ["modelValue"]), [
                                [_directive_loading, promptLoading.value]
                              ])
                            ]),
                            _: 1
                          })
                        ]),
                        _: 1
                      })
                    ]),
                    _: 1
                  })
                ]),
                _: 1
              }),
              createVNode(_component_el_col, {
                xs: 24,
                lg: 12
              }, {
                default: withCtx(() => [
                  createVNode(_component_el_card, { class: "config-card" }, {
                    header: withCtx(() => [
                      createBaseVNode("div", _hoisted_12, [
                        createBaseVNode("span", _hoisted_13, [
                          createVNode(_component_el_tag, {
                            type: "warning",
                            size: "small"
                          }, {
                            default: withCtx(() => [..._cache[15] || (_cache[15] = [
                              createTextVNode("对比组", -1)
                            ])]),
                            _: 1
                          }),
                          _cache[16] || (_cache[16] = createBaseVNode("span", { style: { "margin-left": "8px" } }, "自定义配置", -1))
                        ])
                      ])
                    ]),
                    default: withCtx(() => [
                      createVNode(_component_el_form, { "label-position": "top" }, {
                        default: withCtx(() => [
                          createVNode(_component_el_form_item, { label: "模型" }, {
                            default: withCtx(() => [
                              createVNode(_component_el_select, {
                                modelValue: group2Model.value,
                                "onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => group2Model.value = $event),
                                placeholder: "选择模型"
                              }, {
                                default: withCtx(() => [
                                  createVNode(_component_el_option, {
                                    label: "GPT5（最强推理）",
                                    value: "shihuang-gpt5"
                                  }),
                                  createVNode(_component_el_option, {
                                    label: "Claude Sonnet 4.5（标书专用）",
                                    value: "shihuang-claude-sonnet-45"
                                  }),
                                  createVNode(_component_el_option, {
                                    label: "GPT4o Mini（推荐）",
                                    value: "shihuang-gpt4o-mini"
                                  })
                                ]),
                                _: 1
                              }, 8, ["modelValue"])
                            ]),
                            _: 1
                          }),
                          createVNode(_component_el_form_item, { label: "提示词" }, {
                            extra: withCtx(() => [
                              createVNode(_component_el_text, {
                                size: "small",
                                type: "info"
                              }, {
                                default: withCtx(() => [..._cache[17] || (_cache[17] = [
                                  createTextVNode(" 自定义提示词，用于对比测试 ", -1)
                                ])]),
                                _: 1
                              })
                            ]),
                            default: withCtx(() => [
                              createVNode(_component_el_input, {
                                modelValue: group2Prompt.value,
                                "onUpdate:modelValue": _cache[4] || (_cache[4] = ($event) => group2Prompt.value = $event),
                                type: "textarea",
                                rows: 12,
                                placeholder: "输入自定义提示词..."
                              }, null, 8, ["modelValue"])
                            ]),
                            _: 1
                          })
                        ]),
                        _: 1
                      })
                    ]),
                    _: 1
                  })
                ]),
                _: 1
              })
            ]),
            _: 1
          }),
          createBaseVNode("div", _hoisted_14, [
            createVNode(_component_el_button, {
              type: "primary",
              size: "large",
              icon: unref(video_play_default),
              loading: generating.value,
              disabled: !canGenerate.value,
              onClick: handleGenerate
            }, {
              default: withCtx(() => [..._cache[18] || (_cache[18] = [
                createTextVNode(" 开始生成对比 ", -1)
              ])]),
              _: 1
            }, 8, ["icon", "loading", "disabled"]),
            createVNode(_component_el_button, {
              size: "large",
              icon: unref(refresh_default),
              onClick: handleReset
            }, {
              default: withCtx(() => [..._cache[19] || (_cache[19] = [
                createTextVNode(" 重置 ", -1)
              ])]),
              _: 1
            }, 8, ["icon"])
          ]),
          hasResults.value ? (openBlock(), createBlock(_component_el_card, {
            key: 1,
            class: "result-card"
          }, {
            header: withCtx(() => [
              createBaseVNode("div", _hoisted_15, [
                _cache[21] || (_cache[21] = createBaseVNode("span", { class: "card-title" }, [
                  createBaseVNode("i", { class: "bi-bar-chart" }),
                  createTextVNode(" 生成结果对比 ")
                ], -1)),
                createVNode(_component_el_button, {
                  text: "",
                  icon: unref(download_default)
                }, {
                  default: withCtx(() => [..._cache[20] || (_cache[20] = [
                    createTextVNode("导出报告", -1)
                  ])]),
                  _: 1
                }, 8, ["icon"])
              ])
            ]),
            default: withCtx(() => [
              createVNode(_component_el_row, { gutter: 16 }, {
                default: withCtx(() => [
                  createVNode(_component_el_col, {
                    xs: 24,
                    lg: 12
                  }, {
                    default: withCtx(() => [
                      createBaseVNode("div", _hoisted_16, [
                        createBaseVNode("h3", _hoisted_17, [
                          createVNode(_component_el_tag, {
                            type: "success",
                            size: "small"
                          }, {
                            default: withCtx(() => [..._cache[22] || (_cache[22] = [
                              createTextVNode("基准组", -1)
                            ])]),
                            _: 1
                          }),
                          _cache[23] || (_cache[23] = createTextVNode(" GPT-4o-mini ", -1))
                        ]),
                        createBaseVNode("div", _hoisted_18, [
                          createVNode(_component_el_scrollbar, { "max-height": "600px" }, {
                            default: withCtx(() => [
                              group1Result.value ? (openBlock(), createElementBlock("div", _hoisted_19, toDisplayString(group1Result.value), 1)) : (openBlock(), createBlock(_component_el_empty, {
                                key: 1,
                                description: "暂无结果"
                              }))
                            ]),
                            _: 1
                          })
                        ]),
                        createBaseVNode("div", _hoisted_20, [
                          createVNode(_component_el_text, {
                            size: "small",
                            type: "info"
                          }, {
                            default: withCtx(() => [
                              createTextVNode(" 生成时间: " + toDisplayString(group1Time.value || "-"), 1)
                            ]),
                            _: 1
                          })
                        ])
                      ])
                    ]),
                    _: 1
                  }),
                  createVNode(_component_el_col, {
                    xs: 24,
                    lg: 12
                  }, {
                    default: withCtx(() => [
                      createBaseVNode("div", _hoisted_21, [
                        createBaseVNode("h3", _hoisted_22, [
                          createVNode(_component_el_tag, {
                            type: "warning",
                            size: "small"
                          }, {
                            default: withCtx(() => [..._cache[24] || (_cache[24] = [
                              createTextVNode("对比组", -1)
                            ])]),
                            _: 1
                          }),
                          createTextVNode(" " + toDisplayString(group2Model.value || "未选择"), 1)
                        ]),
                        createBaseVNode("div", _hoisted_23, [
                          createVNode(_component_el_scrollbar, { "max-height": "600px" }, {
                            default: withCtx(() => [
                              group2Result.value ? (openBlock(), createElementBlock("div", _hoisted_24, toDisplayString(group2Result.value), 1)) : (openBlock(), createBlock(_component_el_empty, {
                                key: 1,
                                description: "暂无结果"
                              }))
                            ]),
                            _: 1
                          })
                        ]),
                        createBaseVNode("div", _hoisted_25, [
                          createVNode(_component_el_text, {
                            size: "small",
                            type: "info"
                          }, {
                            default: withCtx(() => [
                              createTextVNode(" 生成时间: " + toDisplayString(group2Time.value || "-"), 1)
                            ]),
                            _: 1
                          })
                        ])
                      ])
                    ]),
                    _: 1
                  })
                ]),
                _: 1
              })
            ]),
            _: 1
          })) : createCommentVNode("", true)
        ]),
        createVNode(unref(DocumentPreview), {
          modelValue: previewVisible.value,
          "onUpdate:modelValue": _cache[5] || (_cache[5] = ($event) => previewVisible.value = $event),
          "file-url": previewFileUrl.value,
          "file-name": previewFileName.value
        }, null, 8, ["modelValue", "file-url", "file-name"])
      ]);
    };
  }
});
const OutlineComparison = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-97b6cc04"]]);
export {
  OutlineComparison as default
};
