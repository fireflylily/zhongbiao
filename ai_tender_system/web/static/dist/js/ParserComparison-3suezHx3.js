import { d as defineComponent, c as computed, B as resolveComponent, e as createElementBlock, o as openBlock, n as createBaseVNode, l as createCommentVNode, U as normalizeClass, t as toDisplayString, k as createBlock, ad as ElIcon, w as withCtx, f as createVNode, h as unref, aO as circle_check_default, aP as circle_close_default, bs as warning_default, F as Fragment, V as renderList, ac as normalizeStyle, r as ref, g as ElButton, p as createTextVNode, m as ElAlert, X as ElTag, as as ElCard, ar as ElEmpty, Y as ElSelect, W as ElOption, A as ElMessage, y as ElInput, S as onMounted, at as ElUpload, aF as upload_default, ay as ElDescriptions, az as ElDescriptionsItem, al as ElTable, am as ElTableColumn, z as ElMessageBox } from "./vendor-_9UVkM6-.js";
/* empty css                                                                           */
import { C as Card } from "./Card-C-BxBgcH.js";
/* empty css                                                                         */
import { e as apiClient, _ as _export_sfc } from "./index.js";
function uploadDocument(file) {
  const formData = new FormData();
  formData.append("file", file);
  return apiClient.post("/parser-debug/upload", formData, {
    headers: {
      "Content-Type": "multipart/form-data"
    }
  });
}
function getTestResult(documentId) {
  return apiClient.get(`/parser-debug/${documentId}`);
}
function saveGroundTruth(documentId, chapters, annotator = "user") {
  return apiClient.post(`/parser-debug/${documentId}/ground-truth`, {
    chapters,
    annotator
  });
}
function getHistory(params) {
  return apiClient.get("/parser-debug/history", {
    params
  });
}
function deleteTest(documentId) {
  return apiClient.delete(`/parser-debug/${documentId}/delete`);
}
function exportReport(documentId) {
  return apiClient.get(`/parser-debug/export/${documentId}`, {
    responseType: "blob"
  });
}
const parserDebugApi = {
  uploadDocument,
  getTestResult,
  saveGroundTruth,
  getHistory,
  deleteTest,
  exportReport
};
const _hoisted_1$3 = { class: "chapter-title" };
const _hoisted_2$3 = { class: "chapter-info" };
const _hoisted_3$3 = { class: "word-count" };
const _hoisted_4$3 = {
  key: 0,
  class: "children"
};
const _sfc_main$3 = /* @__PURE__ */ defineComponent({
  __name: "ChapterTreeItem",
  props: {
    chapter: {},
    groundTruth: {},
    level: {}
  },
  setup(__props) {
    const props = __props;
    const matchStatus = computed(() => {
      if (!props.groundTruth) return "unknown";
      const flattenChapters = (chapters) => {
        const result = [];
        for (const ch of chapters) {
          result.push(ch);
          if (ch.children && ch.children.length > 0) {
            result.push(...flattenChapters(ch.children));
          }
        }
        return result;
      };
      const truthFlat = flattenChapters(props.groundTruth);
      const normalizeTitle = (title) => {
        return title.replace(/^\d+\.\s*/, "").replace(/^\d+\.\d+\s*/, "").replace(/^第[一二三四五六七八九十\d]+[章节部分]\s*/, "").replace(/\s+/g, "").toLowerCase();
      };
      const normalizedCurrent = normalizeTitle(props.chapter.title);
      const isMatched = truthFlat.some(
        (ch) => normalizeTitle(ch.title) === normalizedCurrent
      );
      return isMatched ? "matched" : "false_positive";
    });
    const matchStatusClass = computed(() => {
      return {
        "status-matched": matchStatus.value === "matched",
        "status-false-positive": matchStatus.value === "false_positive",
        "status-unknown": matchStatus.value === "unknown"
      };
    });
    return (_ctx, _cache) => {
      const _component_el_icon = ElIcon;
      const _component_ChapterTreeItem = resolveComponent("ChapterTreeItem", true);
      return openBlock(), createElementBlock("div", {
        class: "chapter-tree-item",
        style: normalizeStyle({ paddingLeft: `${__props.level * 20}px` })
      }, [
        createBaseVNode("div", {
          class: normalizeClass(["chapter-row", matchStatusClass.value])
        }, [
          createBaseVNode("span", {
            class: normalizeClass(["level-badge", `level-${__props.chapter.level}`])
          }, " L" + toDisplayString(__props.chapter.level), 3),
          createBaseVNode("span", _hoisted_1$3, toDisplayString(__props.chapter.title), 1),
          createBaseVNode("span", _hoisted_2$3, [
            createBaseVNode("span", _hoisted_3$3, toDisplayString(__props.chapter.word_count) + "字", 1),
            matchStatus.value === "matched" ? (openBlock(), createBlock(_component_el_icon, {
              key: 0,
              class: "match-icon success"
            }, {
              default: withCtx(() => [
                createVNode(unref(circle_check_default))
              ]),
              _: 1
            })) : matchStatus.value === "missed" ? (openBlock(), createBlock(_component_el_icon, {
              key: 1,
              class: "match-icon error"
            }, {
              default: withCtx(() => [
                createVNode(unref(circle_close_default))
              ]),
              _: 1
            })) : matchStatus.value === "false_positive" ? (openBlock(), createBlock(_component_el_icon, {
              key: 2,
              class: "match-icon warning"
            }, {
              default: withCtx(() => [
                createVNode(unref(warning_default))
              ]),
              _: 1
            })) : createCommentVNode("", true)
          ])
        ], 2),
        __props.chapter.children && __props.chapter.children.length > 0 ? (openBlock(), createElementBlock("div", _hoisted_4$3, [
          (openBlock(true), createElementBlock(Fragment, null, renderList(__props.chapter.children, (child) => {
            return openBlock(), createBlock(_component_ChapterTreeItem, {
              key: child.id,
              chapter: child,
              "ground-truth": __props.groundTruth,
              level: __props.level + 1
            }, null, 8, ["chapter", "ground-truth", "level"]);
          }), 128))
        ])) : createCommentVNode("", true)
      ], 4);
    };
  }
});
const ChapterTreeItem = /* @__PURE__ */ _export_sfc(_sfc_main$3, [["__scopeId", "data-v-3e35c8e3"]]);
const _hoisted_1$2 = { class: "card-header" };
const _hoisted_2$2 = { class: "card-body" };
const _hoisted_3$2 = { class: "statistics" };
const _hoisted_4$2 = { class: "stat-item" };
const _hoisted_5$2 = { class: "value" };
const _hoisted_6$2 = { class: "stat-item" };
const _hoisted_7$2 = { class: "value" };
const _hoisted_8$2 = { class: "stat-item" };
const _hoisted_9$2 = { class: "value" };
const _hoisted_10$2 = {
  key: 0,
  class: "stat-item"
};
const _hoisted_11$1 = { class: "chapter-list" };
const _hoisted_12$1 = { class: "chapter-list-header" };
const _hoisted_13$1 = {
  key: 0,
  class: "error-message"
};
const _sfc_main$2 = /* @__PURE__ */ defineComponent({
  __name: "MethodCard",
  props: {
    title: {},
    result: {},
    groundTruth: {},
    accuracy: {},
    color: { default: "#409EFF" }
  },
  setup(__props) {
    const props = __props;
    const expanded = ref(false);
    const statusType = computed(() => {
      if (!props.result.success) return "danger";
      if (props.accuracy) {
        if (props.accuracy.f1_score >= 0.9) return "success";
        if (props.accuracy.f1_score >= 0.7) return "";
        if (props.accuracy.f1_score >= 0.5) return "warning";
        return "danger";
      }
      return "info";
    });
    const statusText = computed(() => {
      if (!props.result.success) return "失败";
      if (props.accuracy) {
        return `F1: ${(props.accuracy.f1_score * 100).toFixed(1)}%`;
      }
      return "成功";
    });
    const toggleExpanded = () => {
      expanded.value = !expanded.value;
    };
    const formatNumber = (num) => {
      if (num >= 1e4) return `${(num / 1e4).toFixed(1)}万`;
      return num.toString();
    };
    const getF1Class = (f1) => {
      if (f1 >= 0.9) return "excellent";
      if (f1 >= 0.7) return "good";
      if (f1 >= 0.5) return "fair";
      return "poor";
    };
    return (_ctx, _cache) => {
      const _component_el_tag = ElTag;
      const _component_el_button = ElButton;
      const _component_el_alert = ElAlert;
      const _component_el_card = ElCard;
      return openBlock(), createBlock(_component_el_card, {
        class: "method-card",
        "body-style": { padding: "0" }
      }, {
        header: withCtx(() => [
          createBaseVNode("div", _hoisted_1$2, [
            createBaseVNode("span", {
              class: "method-title",
              style: normalizeStyle({ color: __props.color })
            }, toDisplayString(__props.title), 5),
            createVNode(_component_el_tag, {
              type: statusType.value,
              size: "small"
            }, {
              default: withCtx(() => [
                createTextVNode(toDisplayString(statusText.value), 1)
              ]),
              _: 1
            }, 8, ["type"])
          ])
        ]),
        default: withCtx(() => {
          var _a, _b, _c;
          return [
            createBaseVNode("div", _hoisted_2$2, [
              createBaseVNode("div", _hoisted_3$2, [
                createBaseVNode("div", _hoisted_4$2, [
                  _cache[0] || (_cache[0] = createBaseVNode("span", { class: "label" }, "识别章节:", -1)),
                  createBaseVNode("span", _hoisted_5$2, toDisplayString(((_a = __props.result.chapters) == null ? void 0 : _a.length) || 0), 1)
                ]),
                createBaseVNode("div", _hoisted_6$2, [
                  _cache[1] || (_cache[1] = createBaseVNode("span", { class: "label" }, "总字数:", -1)),
                  createBaseVNode("span", _hoisted_7$2, toDisplayString(formatNumber(((_b = __props.result.statistics) == null ? void 0 : _b.total_words) || 0)), 1)
                ]),
                createBaseVNode("div", _hoisted_8$2, [
                  _cache[2] || (_cache[2] = createBaseVNode("span", { class: "label" }, "耗时:", -1)),
                  createBaseVNode("span", _hoisted_9$2, toDisplayString(((_c = __props.result.performance) == null ? void 0 : _c.elapsed_formatted) || "-"), 1)
                ]),
                __props.accuracy ? (openBlock(), createElementBlock("div", _hoisted_10$2, [
                  _cache[3] || (_cache[3] = createBaseVNode("span", { class: "label" }, "F1分数:", -1)),
                  createBaseVNode("span", {
                    class: normalizeClass(["value f1-score", getF1Class(__props.accuracy.f1_score)])
                  }, toDisplayString((__props.accuracy.f1_score * 100).toFixed(1)) + "% ", 3)
                ])) : createCommentVNode("", true)
              ]),
              createBaseVNode("div", _hoisted_11$1, [
                createBaseVNode("div", _hoisted_12$1, [
                  _cache[4] || (_cache[4] = createBaseVNode("span", null, "章节列表", -1)),
                  createVNode(_component_el_button, {
                    size: "small",
                    text: "",
                    onClick: toggleExpanded
                  }, {
                    default: withCtx(() => [
                      createTextVNode(toDisplayString(expanded.value ? "收起" : "展开全部"), 1)
                    ]),
                    _: 1
                  })
                ]),
                !__props.result.success ? (openBlock(), createElementBlock("div", _hoisted_13$1, [
                  createVNode(_component_el_alert, {
                    title: __props.result.error || "解析失败",
                    type: "error",
                    closable: false
                  }, null, 8, ["title"])
                ])) : (openBlock(), createElementBlock("div", {
                  key: 1,
                  class: normalizeClass(["chapters-container", { collapsed: !expanded.value }])
                }, [
                  (openBlock(true), createElementBlock(Fragment, null, renderList(__props.result.chapters, (chapter) => {
                    return openBlock(), createBlock(ChapterTreeItem, {
                      key: chapter.id,
                      chapter,
                      "ground-truth": __props.groundTruth,
                      level: 0
                    }, null, 8, ["chapter", "ground-truth"]);
                  }), 128))
                ], 2))
              ])
            ])
          ];
        }),
        _: 1
      });
    };
  }
});
const MethodCard = /* @__PURE__ */ _export_sfc(_sfc_main$2, [["__scopeId", "data-v-04b838bf"]]);
const _hoisted_1$1 = { class: "card-header" };
const _hoisted_2$1 = {
  key: 1,
  class: "action-buttons"
};
const _hoisted_3$1 = { class: "card-body" };
const _hoisted_4$1 = {
  key: 0,
  class: "empty-state"
};
const _hoisted_5$1 = {
  key: 1,
  class: "editing-area"
};
const _hoisted_6$1 = { class: "template-selector mb-3" };
const _hoisted_7$1 = { class: "editable-list" };
const _hoisted_8$1 = {
  key: 2,
  class: "display-area"
};
const _hoisted_9$1 = { class: "chapter-count" };
const _hoisted_10$1 = { class: "chapters-container" };
const _sfc_main$1 = /* @__PURE__ */ defineComponent({
  __name: "GroundTruthCard",
  props: {
    modelValue: {},
    documentId: {},
    availableResults: {}
  },
  emits: ["update:modelValue", "save"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const editing = ref(false);
    const editingChapters = ref([]);
    const selectedTemplate = ref("");
    const startEditing = () => {
      editing.value = true;
      if (props.modelValue) {
        editingChapters.value = flattenForEditing(props.modelValue);
      } else {
        editingChapters.value = [];
      }
    };
    const cancelEditing = () => {
      editing.value = false;
      editingChapters.value = [];
      selectedTemplate.value = "";
    };
    const saveEditing = () => {
      if (editingChapters.value.length === 0) {
        ElMessage.warning("请至少添加一个章节");
        return;
      }
      const chapters = editingChapters.value.map((ch, index) => ({
        id: `gt_${index}`,
        level: ch.level,
        title: ch.title,
        para_start_idx: 0,
        para_end_idx: 0,
        word_count: 0,
        preview_text: "",
        auto_selected: false,
        skip_recommended: false,
        children: []
      }));
      emit("update:modelValue", chapters);
      emit("save", chapters);
      editing.value = false;
    };
    const loadTemplate = (methodKey) => {
      if (methodKey === "manual") {
        editingChapters.value = [];
        return;
      }
      if (!props.availableResults || !props.availableResults[methodKey]) {
        ElMessage.warning("该方法的结果不可用");
        return;
      }
      const result = props.availableResults[methodKey];
      if (result.success && result.chapters) {
        editingChapters.value = flattenForEditing(result.chapters);
        ElMessage.success(`已加载${result.method_name}的结果`);
      } else {
        ElMessage.error("该方法解析失败");
      }
    };
    const addChapter = () => {
      editingChapters.value.push({
        title: "",
        level: 1
      });
    };
    const removeChapter = (index) => {
      editingChapters.value.splice(index, 1);
    };
    const flattenForEditing = (chapters) => {
      const result = [];
      const traverse = (chs) => {
        for (const ch of chs) {
          result.push({
            title: ch.title,
            level: ch.level
          });
          if (ch.children && ch.children.length > 0) {
            traverse(ch.children);
          }
        }
      };
      traverse(chapters);
      return result;
    };
    const getTotalChapters = (chapters) => {
      if (!chapters) return 0;
      let count = 0;
      const traverse = (chs) => {
        for (const ch of chs) {
          count++;
          if (ch.children && ch.children.length > 0) {
            traverse(ch.children);
          }
        }
      };
      traverse(chapters);
      return count;
    };
    return (_ctx, _cache) => {
      const _component_el_button = ElButton;
      const _component_el_empty = ElEmpty;
      const _component_el_alert = ElAlert;
      const _component_el_option = ElOption;
      const _component_el_select = ElSelect;
      const _component_el_input = ElInput;
      const _component_el_card = ElCard;
      return openBlock(), createBlock(_component_el_card, { class: "ground-truth-card" }, {
        header: withCtx(() => [
          createBaseVNode("div", _hoisted_1$1, [
            _cache[3] || (_cache[3] = createBaseVNode("span", { class: "title" }, "✅ 正确答案（人工标注）", -1)),
            !editing.value ? (openBlock(), createBlock(_component_el_button, {
              key: 0,
              size: "small",
              type: "primary",
              onClick: startEditing
            }, {
              default: withCtx(() => [
                createTextVNode(toDisplayString(__props.modelValue ? "编辑标注" : "开始标注"), 1)
              ]),
              _: 1
            })) : (openBlock(), createElementBlock("div", _hoisted_2$1, [
              createVNode(_component_el_button, {
                size: "small",
                onClick: cancelEditing
              }, {
                default: withCtx(() => [..._cache[1] || (_cache[1] = [
                  createTextVNode("取消", -1)
                ])]),
                _: 1
              }),
              createVNode(_component_el_button, {
                size: "small",
                type: "success",
                onClick: saveEditing
              }, {
                default: withCtx(() => [..._cache[2] || (_cache[2] = [
                  createTextVNode("保存", -1)
                ])]),
                _: 1
              })
            ]))
          ])
        ]),
        default: withCtx(() => [
          createBaseVNode("div", _hoisted_3$1, [
            !__props.modelValue && !editing.value ? (openBlock(), createElementBlock("div", _hoisted_4$1, [
              createVNode(_component_el_empty, { description: "尚未标注正确答案" }, {
                default: withCtx(() => [
                  createVNode(_component_el_button, {
                    type: "primary",
                    onClick: startEditing
                  }, {
                    default: withCtx(() => [..._cache[4] || (_cache[4] = [
                      createTextVNode("开始标注", -1)
                    ])]),
                    _: 1
                  })
                ]),
                _: 1
              })
            ])) : editing.value ? (openBlock(), createElementBlock("div", _hoisted_5$1, [
              createVNode(_component_el_alert, {
                title: "标注说明",
                type: "info",
                closable: false,
                class: "mb-3"
              }, {
                default: withCtx(() => [..._cache[5] || (_cache[5] = [
                  createBaseVNode("p", null, "请从左侧选择一个方法的结果作为基础，然后调整章节列表。", -1),
                  createBaseVNode("p", null, "您也可以手动添加、删除或修改章节。", -1)
                ])]),
                _: 1
              }),
              createBaseVNode("div", _hoisted_6$1, [
                _cache[6] || (_cache[6] = createBaseVNode("span", null, "基于方法结果:", -1)),
                createVNode(_component_el_select, {
                  modelValue: selectedTemplate.value,
                  "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => selectedTemplate.value = $event),
                  placeholder: "选择方法",
                  onChange: loadTemplate
                }, {
                  default: withCtx(() => {
                    var _a, _b;
                    return [
                      createVNode(_component_el_option, {
                        label: "语义锚点解析",
                        value: "semantic"
                      }),
                      createVNode(_component_el_option, {
                        label: "旧目录定位",
                        value: "old_toc"
                      }),
                      createVNode(_component_el_option, {
                        label: "样式识别",
                        value: "style"
                      }),
                      createVNode(_component_el_option, {
                        label: "大纲级别识别",
                        value: "outline"
                      }),
                      ((_b = (_a = __props.availableResults) == null ? void 0 : _a.azure) == null ? void 0 : _b.success) ? (openBlock(), createBlock(_component_el_option, {
                        key: 0,
                        label: "Azure Form Recognizer",
                        value: "azure"
                      })) : createCommentVNode("", true),
                      createVNode(_component_el_option, {
                        label: "手动创建",
                        value: "manual"
                      })
                    ];
                  }),
                  _: 1
                }, 8, ["modelValue"])
              ]),
              createBaseVNode("div", _hoisted_7$1, [
                createVNode(_component_el_button, {
                  size: "small",
                  onClick: addChapter,
                  class: "mb-2"
                }, {
                  default: withCtx(() => [..._cache[7] || (_cache[7] = [
                    createTextVNode(" + 添加章节 ", -1)
                  ])]),
                  _: 1
                }),
                (openBlock(true), createElementBlock(Fragment, null, renderList(editingChapters.value, (chapter, index) => {
                  return openBlock(), createElementBlock("div", {
                    key: index,
                    class: "editable-chapter"
                  }, [
                    createVNode(_component_el_input, {
                      modelValue: chapter.title,
                      "onUpdate:modelValue": ($event) => chapter.title = $event,
                      placeholder: "章节标题",
                      size: "small"
                    }, {
                      prepend: withCtx(() => [
                        createVNode(_component_el_select, {
                          modelValue: chapter.level,
                          "onUpdate:modelValue": ($event) => chapter.level = $event,
                          style: { "width": "80px" },
                          size: "small"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_option, {
                              label: "L1",
                              value: 1
                            }),
                            createVNode(_component_el_option, {
                              label: "L2",
                              value: 2
                            }),
                            createVNode(_component_el_option, {
                              label: "L3",
                              value: 3
                            })
                          ]),
                          _: 1
                        }, 8, ["modelValue", "onUpdate:modelValue"])
                      ]),
                      _: 2
                    }, 1032, ["modelValue", "onUpdate:modelValue"]),
                    createVNode(_component_el_button, {
                      size: "small",
                      type: "danger",
                      text: "",
                      onClick: ($event) => removeChapter(index)
                    }, {
                      default: withCtx(() => [..._cache[8] || (_cache[8] = [
                        createTextVNode(" 删除 ", -1)
                      ])]),
                      _: 1
                    }, 8, ["onClick"])
                  ]);
                }), 128))
              ])
            ])) : (openBlock(), createElementBlock("div", _hoisted_8$1, [
              createBaseVNode("div", _hoisted_9$1, " 共 " + toDisplayString(getTotalChapters(__props.modelValue)) + " 个章节 ", 1),
              createBaseVNode("div", _hoisted_10$1, [
                (openBlock(true), createElementBlock(Fragment, null, renderList(__props.modelValue, (chapter) => {
                  return openBlock(), createBlock(ChapterTreeItem, {
                    key: chapter.id,
                    chapter,
                    level: 0
                  }, null, 8, ["chapter"]);
                }), 128))
              ])
            ]))
          ])
        ]),
        _: 1
      });
    };
  }
});
const GroundTruthCard = /* @__PURE__ */ _export_sfc(_sfc_main$1, [["__scopeId", "data-v-d2bcdc40"]]);
const _hoisted_1 = { class: "parser-comparison" };
const _hoisted_2 = { class: "upload-section" };
const _hoisted_3 = {
  key: 0,
  class: "selected-file"
};
const _hoisted_4 = {
  key: 0,
  class: "doc-info"
};
const _hoisted_5 = {
  key: 1,
  class: "comparison-grid"
};
const _hoisted_6 = {
  key: 2,
  class: "accuracy-section"
};
const _hoisted_7 = { class: "best-method-summary" };
const _hoisted_8 = { class: "history-section" };
const _hoisted_9 = { class: "section-header" };
const _hoisted_10 = {
  key: 1,
  class: "text-muted"
};
const _hoisted_11 = {
  key: 1,
  class: "text-muted"
};
const _hoisted_12 = {
  key: 1,
  class: "text-muted"
};
const _hoisted_13 = {
  key: 1,
  class: "text-muted"
};
const _hoisted_14 = {
  key: 1,
  class: "text-muted"
};
const _hoisted_15 = { key: 0 };
const _hoisted_16 = { style: { "font-size": "12px", "margin-top": "4px", "color": "#606266" } };
const _hoisted_17 = {
  key: 1,
  class: "text-muted"
};
const _hoisted_18 = {
  key: 0,
  class: "empty-state"
};
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "ParserComparison",
  setup(__props) {
    const uploadRef = ref();
    const selectedFile = ref(null);
    const parsing = ref(false);
    const currentDocumentId = ref("");
    const documentInfo = ref(null);
    const results = ref(null);
    const groundTruth = ref(null);
    const accuracy = ref(null);
    const historyDialogVisible = ref(false);
    const historyList = ref([]);
    const handleFileSelect = (uploadFile) => {
      selectedFile.value = uploadFile.raw;
    };
    const startParsing = async () => {
      var _a, _b;
      if (!selectedFile.value) {
        ElMessage.warning("请先选择文件");
        return;
      }
      parsing.value = true;
      try {
        console.log("开始上传文件:", selectedFile.value.name);
        const response = await parserDebugApi.uploadDocument(selectedFile.value);
        console.log("API响应:", response);
        const data = response.data || response;
        if (data && data.success) {
          currentDocumentId.value = data.document_id;
          documentInfo.value = data.document_info;
          results.value = data.results;
          groundTruth.value = data.ground_truth || null;
          accuracy.value = data.accuracy || null;
          ElMessage.success("解析完成！");
        } else {
          console.error("解析失败，响应数据:", data);
          ElMessage.error((data == null ? void 0 : data.error) || "解析失败");
        }
      } catch (error) {
        console.error("解析异常:", error);
        console.error("错误详情:", error.response);
        ElMessage.error(((_b = (_a = error.response) == null ? void 0 : _a.data) == null ? void 0 : _b.error) || error.message || "解析失败");
      } finally {
        parsing.value = false;
      }
    };
    const handleSaveGroundTruth = async (chapters) => {
      if (!currentDocumentId.value) {
        ElMessage.error("没有当前文档");
        return;
      }
      try {
        const response = await parserDebugApi.saveGroundTruth(
          currentDocumentId.value,
          chapters,
          "user"
        );
        if (response.data.success) {
          accuracy.value = response.data.accuracy;
          ElMessage.success("标注已保存，准确率已计算");
        }
      } catch (error) {
        console.error("保存标注失败:", error);
        ElMessage.error("保存失败");
      }
    };
    const loadHistoryList = async () => {
      try {
        const response = await parserDebugApi.getHistory({ limit: 50 });
        historyList.value = response.data.tests;
      } catch (error) {
        console.error("加载历史记录失败:", error);
        ElMessage.error("加载历史记录失败");
      }
    };
    const showHistory = async () => {
      await loadHistoryList();
      historyDialogVisible.value = true;
    };
    const loadTest = async (documentId) => {
      try {
        const response = await parserDebugApi.getTestResult(documentId);
        if (response.data.success) {
          currentDocumentId.value = response.data.document_id;
          documentInfo.value = response.data.document_info;
          results.value = response.data.results;
          groundTruth.value = response.data.ground_truth || null;
          accuracy.value = response.data.accuracy || null;
          historyDialogVisible.value = false;
          ElMessage.success("测试结果已加载");
        }
      } catch (error) {
        ElMessage.error("加载失败");
      }
    };
    const handleDeleteTest = async (documentId) => {
      try {
        await ElMessageBox.confirm("确定要删除这条测试记录吗？", "确认删除", {
          type: "warning"
        });
        await parserDebugApi.deleteTest(documentId);
        ElMessage.success("已删除");
        showHistory();
      } catch (error) {
      }
    };
    const accuracyTableData = computed(() => {
      if (!accuracy.value || !results.value) return [];
      const methods = [
        { key: "semantic", name: "语义锚点解析" },
        { key: "style", name: "样式识别(增强)" },
        { key: "hybrid", name: "混合启发式识别" },
        { key: "azure", name: "Azure Form Recognizer" },
        { key: "docx_native", name: "Word大纲级别识别" }
      ];
      return methods.filter(({ key }) => results.value[key]).map(({ key, name }) => {
        var _a, _b, _c, _d, _e, _f, _g;
        return {
          method: name,
          precision: ((_a = accuracy.value[key]) == null ? void 0 : _a.precision) || 0,
          recall: ((_b = accuracy.value[key]) == null ? void 0 : _b.recall) || 0,
          f1: ((_c = accuracy.value[key]) == null ? void 0 : _c.f1_score) || 0,
          detected: ((_e = (_d = results.value[key]) == null ? void 0 : _d.chapters) == null ? void 0 : _e.length) || 0,
          elapsed: ((_g = (_f = results.value[key]) == null ? void 0 : _f.performance) == null ? void 0 : _g.elapsed_formatted) || "-",
          is_best: accuracy.value.best_method === key
        };
      });
    });
    const getScoreClass = (score) => {
      if (score >= 0.9) return "score-excellent";
      if (score >= 0.7) return "score-good";
      if (score >= 0.5) return "score-fair";
      return "score-poor";
    };
    const getF1TagType = (f1) => {
      if (f1 >= 0.9) return "success";
      if (f1 >= 0.7) return "";
      if (f1 >= 0.5) return "warning";
      return "danger";
    };
    const getBestMethodName = () => {
      var _a;
      const names = {
        semantic: "语义锚点解析",
        style: "样式识别(增强)",
        hybrid: "混合启发式识别",
        azure: "Azure Form Recognizer",
        docx_native: "Word大纲级别识别"
      };
      return names[(_a = accuracy.value) == null ? void 0 : _a.best_method] || "未知";
    };
    const getMethodDisplayName = (key) => {
      const names = {
        semantic: "语义锚点",
        style: "样式",
        hybrid: "混合启发式",
        azure: "Azure",
        docx_native: "Word大纲"
      };
      return names[key] || key;
    };
    onMounted(async () => {
      await loadHistoryList();
    });
    return (_ctx, _cache) => {
      const _component_el_button = ElButton;
      const _component_el_upload = ElUpload;
      const _component_el_descriptions_item = ElDescriptionsItem;
      const _component_el_tag = ElTag;
      const _component_el_descriptions = ElDescriptions;
      const _component_el_table_column = ElTableColumn;
      const _component_el_table = ElTable;
      const _component_el_alert = ElAlert;
      const _component_el_empty = ElEmpty;
      return openBlock(), createElementBlock("div", _hoisted_1, [
        createVNode(unref(Card), { title: "📊 目录解析方法对比工具" }, {
          extra: withCtx(() => [
            createVNode(_component_el_button, {
              onClick: showHistory,
              type: "text"
            }, {
              default: withCtx(() => [..._cache[1] || (_cache[1] = [
                createTextVNode("历史记录", -1)
              ])]),
              _: 1
            })
          ]),
          default: withCtx(() => {
            var _a, _b, _c, _d, _e;
            return [
              createBaseVNode("div", _hoisted_2, [
                createVNode(_component_el_upload, {
                  ref_key: "uploadRef",
                  ref: uploadRef,
                  "auto-upload": false,
                  "on-change": handleFileSelect,
                  "show-file-list": false,
                  accept: ".docx"
                }, {
                  default: withCtx(() => [
                    createVNode(_component_el_button, {
                      type: "primary",
                      icon: unref(upload_default)
                    }, {
                      default: withCtx(() => [..._cache[2] || (_cache[2] = [
                        createTextVNode("选择标书文档 (.docx)", -1)
                      ])]),
                      _: 1
                    }, 8, ["icon"])
                  ]),
                  _: 1
                }, 512),
                selectedFile.value ? (openBlock(), createElementBlock("span", _hoisted_3, " 已选择: " + toDisplayString(selectedFile.value.name), 1)) : createCommentVNode("", true),
                createVNode(_component_el_button, {
                  onClick: startParsing,
                  loading: parsing.value,
                  disabled: !selectedFile.value,
                  type: "success"
                }, {
                  default: withCtx(() => [..._cache[3] || (_cache[3] = [
                    createTextVNode(" 开始解析对比 ", -1)
                  ])]),
                  _: 1
                }, 8, ["loading", "disabled"])
              ]),
              documentInfo.value ? (openBlock(), createElementBlock("div", _hoisted_4, [
                createVNode(_component_el_descriptions, {
                  column: 4,
                  border: ""
                }, {
                  default: withCtx(() => [
                    createVNode(_component_el_descriptions_item, { label: "文件名" }, {
                      default: withCtx(() => [
                        createTextVNode(toDisplayString(documentInfo.value.filename), 1)
                      ]),
                      _: 1
                    }),
                    createVNode(_component_el_descriptions_item, { label: "总段落数" }, {
                      default: withCtx(() => [
                        createTextVNode(toDisplayString(documentInfo.value.total_paragraphs), 1)
                      ]),
                      _: 1
                    }),
                    createVNode(_component_el_descriptions_item, { label: "目录检测" }, {
                      default: withCtx(() => [
                        createVNode(_component_el_tag, {
                          type: documentInfo.value.has_toc ? "success" : "warning"
                        }, {
                          default: withCtx(() => [
                            createTextVNode(toDisplayString(documentInfo.value.has_toc ? `✓ 检测到 (${documentInfo.value.toc_items_count}项)` : "✗ 未检测到"), 1)
                          ]),
                          _: 1
                        }, 8, ["type"])
                      ]),
                      _: 1
                    }),
                    createVNode(_component_el_descriptions_item, { label: "上传时间" }, {
                      default: withCtx(() => [
                        createTextVNode(toDisplayString(documentInfo.value.upload_time || "-"), 1)
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                })
              ])) : createCommentVNode("", true),
              results.value ? (openBlock(), createElementBlock("div", _hoisted_5, [
                createVNode(MethodCard, {
                  title: "方法1: 语义锚点解析",
                  result: results.value.semantic,
                  "ground-truth": groundTruth.value,
                  accuracy: (_a = accuracy.value) == null ? void 0 : _a.semantic,
                  color: "#67C23A"
                }, null, 8, ["result", "ground-truth", "accuracy"]),
                createVNode(MethodCard, {
                  title: "方法2: 样式识别(增强)",
                  result: results.value.style,
                  "ground-truth": groundTruth.value,
                  accuracy: (_b = accuracy.value) == null ? void 0 : _b.style,
                  color: "#409EFF"
                }, null, 8, ["result", "ground-truth", "accuracy"]),
                createVNode(MethodCard, {
                  title: "方法3: 混合启发式识别",
                  result: results.value.hybrid,
                  "ground-truth": groundTruth.value,
                  accuracy: (_c = accuracy.value) == null ? void 0 : _c.hybrid,
                  color: "#E6A23C"
                }, null, 8, ["result", "ground-truth", "accuracy"]),
                results.value.azure ? (openBlock(), createBlock(MethodCard, {
                  key: 0,
                  title: "方法4: Azure Form Recognizer",
                  result: results.value.azure,
                  "ground-truth": groundTruth.value,
                  accuracy: (_d = accuracy.value) == null ? void 0 : _d.azure,
                  color: "#00B7C3"
                }, null, 8, ["result", "ground-truth", "accuracy"])) : createCommentVNode("", true),
                results.value.docx_native ? (openBlock(), createBlock(MethodCard, {
                  key: 1,
                  title: "方法5: Word大纲级别识别",
                  result: results.value.docx_native,
                  "ground-truth": groundTruth.value,
                  accuracy: (_e = accuracy.value) == null ? void 0 : _e.docx_native,
                  color: "#9C27B0"
                }, null, 8, ["result", "ground-truth", "accuracy"])) : createCommentVNode("", true),
                createVNode(GroundTruthCard, {
                  modelValue: groundTruth.value,
                  "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => groundTruth.value = $event),
                  "document-id": currentDocumentId.value,
                  "available-results": results.value,
                  onSave: handleSaveGroundTruth
                }, null, 8, ["modelValue", "document-id", "available-results"])
              ])) : createCommentVNode("", true),
              accuracy.value ? (openBlock(), createElementBlock("div", _hoisted_6, [
                _cache[5] || (_cache[5] = createBaseVNode("h3", null, "准确率对比", -1)),
                createVNode(_component_el_table, {
                  data: accuracyTableData.value,
                  border: "",
                  stripe: ""
                }, {
                  default: withCtx(() => [
                    createVNode(_component_el_table_column, {
                      prop: "method",
                      label: "解析方法",
                      width: "180"
                    }),
                    createVNode(_component_el_table_column, {
                      prop: "precision",
                      label: "精确率 (P)",
                      width: "120"
                    }, {
                      default: withCtx(({ row }) => [
                        createBaseVNode("span", {
                          class: normalizeClass(getScoreClass(row.precision))
                        }, toDisplayString((row.precision * 100).toFixed(1)) + "% ", 3)
                      ]),
                      _: 1
                    }),
                    createVNode(_component_el_table_column, {
                      prop: "recall",
                      label: "召回率 (R)",
                      width: "120"
                    }, {
                      default: withCtx(({ row }) => [
                        createBaseVNode("span", {
                          class: normalizeClass(getScoreClass(row.recall))
                        }, toDisplayString((row.recall * 100).toFixed(1)) + "% ", 3)
                      ]),
                      _: 1
                    }),
                    createVNode(_component_el_table_column, {
                      prop: "f1",
                      label: "F1分数",
                      width: "120"
                    }, {
                      default: withCtx(({ row }) => [
                        createVNode(_component_el_tag, {
                          type: getF1TagType(row.f1),
                          effect: "dark"
                        }, {
                          default: withCtx(() => [
                            createTextVNode(toDisplayString((row.f1 * 100).toFixed(1)) + "% ", 1)
                          ]),
                          _: 2
                        }, 1032, ["type"])
                      ]),
                      _: 1
                    }),
                    createVNode(_component_el_table_column, {
                      prop: "detected",
                      label: "识别数量",
                      width: "100"
                    }),
                    createVNode(_component_el_table_column, {
                      prop: "elapsed",
                      label: "耗时",
                      width: "100"
                    }),
                    createVNode(_component_el_table_column, {
                      label: "状态",
                      width: "100"
                    }, {
                      default: withCtx(({ row }) => [
                        row.is_best ? (openBlock(), createBlock(_component_el_tag, {
                          key: 0,
                          type: "success"
                        }, {
                          default: withCtx(() => [..._cache[4] || (_cache[4] = [
                            createTextVNode("最佳", -1)
                          ])]),
                          _: 1
                        })) : createCommentVNode("", true)
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                }, 8, ["data"]),
                createBaseVNode("div", _hoisted_7, [
                  createVNode(_component_el_alert, {
                    title: `最佳方法: ${getBestMethodName()} (F1分数: ${(accuracy.value.best_f1_score * 100).toFixed(1)}%)`,
                    type: "success",
                    closable: false
                  }, null, 8, ["title"])
                ])
              ])) : createCommentVNode("", true),
              createBaseVNode("div", _hoisted_8, [
                createBaseVNode("div", _hoisted_9, [
                  _cache[7] || (_cache[7] = createBaseVNode("h3", null, "📋 历史解析记录", -1)),
                  createVNode(_component_el_button, {
                    onClick: loadHistoryList,
                    icon: unref(upload_default),
                    size: "small"
                  }, {
                    default: withCtx(() => [..._cache[6] || (_cache[6] = [
                      createTextVNode(" 刷新列表 ", -1)
                    ])]),
                    _: 1
                  }, 8, ["icon"])
                ]),
                createVNode(_component_el_table, {
                  data: historyList.value,
                  border: "",
                  stripe: ""
                }, {
                  default: withCtx(() => [
                    createVNode(_component_el_table_column, {
                      prop: "filename",
                      label: "文件名",
                      "min-width": "200"
                    }),
                    createVNode(_component_el_table_column, {
                      prop: "upload_time",
                      label: "解析时间",
                      width: "180"
                    }),
                    createVNode(_component_el_table_column, {
                      label: "目录检测",
                      width: "100",
                      align: "center"
                    }, {
                      default: withCtx(({ row }) => [
                        createVNode(_component_el_tag, {
                          type: row.has_toc ? "success" : "info",
                          size: "small"
                        }, {
                          default: withCtx(() => [
                            createTextVNode(toDisplayString(row.has_toc ? `✓ (${row.toc_items_count})` : "✗"), 1)
                          ]),
                          _: 2
                        }, 1032, ["type"])
                      ]),
                      _: 1
                    }),
                    createVNode(_component_el_table_column, {
                      label: "语义锚点",
                      width: "100",
                      align: "center"
                    }, {
                      default: withCtx(({ row }) => [
                        row.semantic_f1 ? (openBlock(), createElementBlock("span", {
                          key: 0,
                          class: normalizeClass(getScoreClass(row.semantic_f1))
                        }, toDisplayString((row.semantic_f1 * 100).toFixed(1)) + "% ", 3)) : (openBlock(), createElementBlock("span", _hoisted_10, "-"))
                      ]),
                      _: 1
                    }),
                    createVNode(_component_el_table_column, {
                      label: "样式识别",
                      width: "100",
                      align: "center"
                    }, {
                      default: withCtx(({ row }) => [
                        row.style_f1 ? (openBlock(), createElementBlock("span", {
                          key: 0,
                          class: normalizeClass(getScoreClass(row.style_f1))
                        }, toDisplayString((row.style_f1 * 100).toFixed(1)) + "% ", 3)) : (openBlock(), createElementBlock("span", _hoisted_11, "-"))
                      ]),
                      _: 1
                    }),
                    createVNode(_component_el_table_column, {
                      label: "混合启发式",
                      width: "100",
                      align: "center"
                    }, {
                      default: withCtx(({ row }) => [
                        row.hybrid_f1 ? (openBlock(), createElementBlock("span", {
                          key: 0,
                          class: normalizeClass(getScoreClass(row.hybrid_f1))
                        }, toDisplayString((row.hybrid_f1 * 100).toFixed(1)) + "% ", 3)) : (openBlock(), createElementBlock("span", _hoisted_12, "-"))
                      ]),
                      _: 1
                    }),
                    createVNode(_component_el_table_column, {
                      label: "Azure",
                      width: "100",
                      align: "center"
                    }, {
                      default: withCtx(({ row }) => [
                        row.azure_f1 ? (openBlock(), createElementBlock("span", {
                          key: 0,
                          class: normalizeClass(getScoreClass(row.azure_f1))
                        }, toDisplayString((row.azure_f1 * 100).toFixed(1)) + "% ", 3)) : (openBlock(), createElementBlock("span", _hoisted_13, "-"))
                      ]),
                      _: 1
                    }),
                    createVNode(_component_el_table_column, {
                      label: "Word大纲",
                      width: "110",
                      align: "center"
                    }, {
                      default: withCtx(({ row }) => [
                        row.docx_native_f1 ? (openBlock(), createElementBlock("span", {
                          key: 0,
                          class: normalizeClass(getScoreClass(row.docx_native_f1))
                        }, toDisplayString((row.docx_native_f1 * 100).toFixed(1)) + "% ", 3)) : (openBlock(), createElementBlock("span", _hoisted_14, "-"))
                      ]),
                      _: 1
                    }),
                    createVNode(_component_el_table_column, {
                      label: "最佳方法",
                      width: "150",
                      align: "center"
                    }, {
                      default: withCtx(({ row }) => [
                        row.best_method ? (openBlock(), createElementBlock("div", _hoisted_15, [
                          createVNode(_component_el_tag, {
                            type: row.best_f1_score >= 0.9 ? "success" : "primary",
                            effect: "dark"
                          }, {
                            default: withCtx(() => [
                              createTextVNode(toDisplayString(getMethodDisplayName(row.best_method)), 1)
                            ]),
                            _: 2
                          }, 1032, ["type"]),
                          createBaseVNode("div", _hoisted_16, " F1: " + toDisplayString((row.best_f1_score * 100).toFixed(1)) + "% ", 1)
                        ])) : (openBlock(), createElementBlock("span", _hoisted_17, "未标注"))
                      ]),
                      _: 1
                    }),
                    createVNode(_component_el_table_column, {
                      label: "操作",
                      width: "150",
                      fixed: "right",
                      align: "center"
                    }, {
                      default: withCtx(({ row }) => [
                        createVNode(_component_el_button, {
                          size: "small",
                          type: "primary",
                          onClick: ($event) => loadTest(row.document_id)
                        }, {
                          default: withCtx(() => [..._cache[8] || (_cache[8] = [
                            createTextVNode(" 查看 ", -1)
                          ])]),
                          _: 1
                        }, 8, ["onClick"]),
                        createVNode(_component_el_button, {
                          size: "small",
                          type: "danger",
                          onClick: ($event) => handleDeleteTest(row.document_id)
                        }, {
                          default: withCtx(() => [..._cache[9] || (_cache[9] = [
                            createTextVNode(" 删除 ", -1)
                          ])]),
                          _: 1
                        }, 8, ["onClick"])
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                }, 8, ["data"]),
                historyList.value.length === 0 ? (openBlock(), createElementBlock("div", _hoisted_18, [
                  createVNode(_component_el_empty, { description: "暂无历史解析记录" })
                ])) : createCommentVNode("", true)
              ])
            ];
          }),
          _: 1
        })
      ]);
    };
  }
});
const ParserComparison = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-96d06aab"]]);
export {
  ParserComparison as default
};
