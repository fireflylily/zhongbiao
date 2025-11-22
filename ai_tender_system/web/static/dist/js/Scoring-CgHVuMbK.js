import { d as defineComponent, r as ref, c as computed, S as onMounted, e as createElementBlock, o as openBlock, f as createVNode, k as createBlock, l as createCommentVNode, w as withCtx, q as ElForm, ak as ElRow, ai as ElCol, s as ElFormItem, Y as ElSelect, F as Fragment, V as renderList, W as ElOption, y as ElInput, n as createBaseVNode, as as ElCard, al as ElTable, am as ElTableColumn, aA as ElInputNumber, g as ElButton, p as createTextVNode, U as normalizeClass, t as toDisplayString, X as ElTag, h as unref, aE as download_default, A as ElMessage, a_ as k } from "./vendor-MtO928VE.js";
/* empty css                                                                           */
import { S as SSEStreamViewer } from "./SSEStreamViewer-ChA9d39N.js";
/* empty css                                                                         */
import { _ as _export_sfc } from "./index.js";
import { t as tenderApi } from "./tender-DvsgeLWX.js";
const _hoisted_1 = { class: "tender-scoring" };
const _hoisted_2 = { class: "card-header" };
const _hoisted_3 = { class: "scoring-actions" };
const _hoisted_4 = { class: "weight-summary" };
const _hoisted_5 = {
  key: 0,
  class: "weight-tip"
};
const _hoisted_6 = { class: "card-header" };
const _hoisted_7 = { class: "header-actions" };
const _hoisted_8 = { class: "dimension-scores" };
const _hoisted_9 = ["innerHTML"];
const _hoisted_10 = { class: "risk-analysis" };
const _hoisted_11 = { class: "improvement-suggestions" };
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "Scoring",
  setup(__props) {
    const form = ref({
      projectId: null
    });
    const projects = ref([]);
    const selectedProject = computed(
      () => projects.value.find((p) => p.id === form.value.projectId)
    );
    const scoringDimensions = ref([
      { name: "技术方案完整性", weight: 30, description: "技术方案的完整性和可行性" },
      { name: "商务响应度", weight: 25, description: "商务条款的响应程度" },
      { name: "资质匹配度", weight: 20, description: "公司资质与项目要求的匹配程度" },
      { name: "成本合理性", weight: 15, description: "报价的合理性和竞争力" },
      { name: "风险控制", weight: 10, description: "项目风险的识别和控制措施" }
    ]);
    const totalWeight = computed(
      () => scoringDimensions.value.reduce((sum, dim) => sum + dim.weight, 0)
    );
    const canStartScoring = computed(
      () => form.value.projectId && totalWeight.value === 100 && scoringDimensions.value.length > 0
    );
    const scoringLoading = ref(false);
    const streamContent = ref("");
    const scoringResult = ref(null);
    const loadProjects = async () => {
      var _a;
      try {
        const response = await tenderApi.getProjects({ page: 1, page_size: 100 });
        projects.value = ((_a = response.data) == null ? void 0 : _a.items) || [];
      } catch (error) {
        console.error("加载项目列表失败:", error);
        ElMessage.error("加载项目列表失败");
      }
    };
    const handleProjectChange = () => {
      scoringResult.value = null;
      streamContent.value = "";
    };
    const addDimension = () => {
      scoringDimensions.value.push({
        name: "",
        weight: 0,
        description: ""
      });
    };
    const removeDimension = (index) => {
      scoringDimensions.value.splice(index, 1);
    };
    const startScoring = async () => {
      if (!form.value.projectId) {
        ElMessage.warning("请先选择项目");
        return;
      }
      if (totalWeight.value !== 100) {
        ElMessage.warning("评分维度权重总和必须为100%");
        return;
      }
      scoringLoading.value = true;
      streamContent.value = "";
      scoringResult.value = null;
      try {
        await simulateAIScoring();
        ElMessage.success("评分完成");
      } catch (error) {
        console.error("评分失败:", error);
        ElMessage.error("评分失败，请重试");
      } finally {
        scoringLoading.value = false;
      }
    };
    const simulateAIScoring = async () => {
      return new Promise((resolve) => {
        let progress = 0;
        const interval = setInterval(() => {
          progress += 10;
          streamContent.value += `
正在分析第 ${progress / 10} 个维度...`;
          if (progress >= 100) {
            clearInterval(interval);
            const dimensions = scoringDimensions.value.map((dim) => {
              const score = Math.random() * 30 + 70;
              return {
                ...dim,
                score: Math.round(score),
                weightedScore: score * dim.weight / 100,
                analysis: `该维度表现${score >= 85 ? "优秀" : score >= 70 ? "良好" : "一般"}，${score >= 85 ? "完全满足招标要求，具有明显竞争优势。" : score >= 70 ? "基本满足招标要求，但仍有改进空间。" : "存在一定差距，需要重点改进。"}

**优势：**
- 方案设计合理
- 团队经验丰富

**不足：**
- 部分细节需要完善`
              };
            });
            const totalScore = dimensions.reduce((sum, dim) => sum + dim.weightedScore, 0);
            scoringResult.value = {
              totalScore: Math.round(totalScore),
              dimensions,
              riskAnalysis: `# 风险评估

## 技术风险
- **中等风险**: 部分技术方案需要进一步细化
- 建议加强技术团队的配置

## 商务风险
- **低风险**: 商务条款基本符合要求
- 价格竞争力较强

## 执行风险
- **中等风险**: 项目周期较紧
- 需要合理安排资源和进度`,
              suggestions: `# 改进建议

## 技术方案优化
1. 完善系统架构设计文档
2. 补充性能测试方案
3. 加强数据安全保障措施

## 商务条款完善
1. 明确验收标准
2. 补充售后服务承诺

## 团队能力提升
1. 增加项目相关经验人员
2. 提供更详细的团队简历`
            };
            resolve();
          }
        }, 300);
      });
    };
    const stopScoring = () => {
      scoringLoading.value = false;
      ElMessage.info("已停止评分");
    };
    const getScoreType = (score) => {
      if (score >= 90) return "success";
      if (score >= 80) return "";
      if (score >= 70) return "warning";
      return "danger";
    };
    const formatMarkdown = (text) => {
      try {
        return k.parse(text);
      } catch (error) {
        return text;
      }
    };
    const exportReport = () => {
      var _a;
      if (!scoringResult.value) return;
      const report = generateReport();
      const blob = new Blob([report], { type: "text/plain;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `标书评分报告-${((_a = selectedProject.value) == null ? void 0 : _a.project_name) || "report"}-${Date.now()}.txt`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      ElMessage.success("报告导出成功");
    };
    const generateReport = () => {
      var _a, _b, _c;
      if (!scoringResult.value) return "";
      let report = `# 标书评分报告

`;
      report += `## 项目信息
`;
      report += `- 项目名称: ${(_a = selectedProject.value) == null ? void 0 : _a.project_name}
`;
      report += `- 项目编号: ${(_b = selectedProject.value) == null ? void 0 : _b.project_number}
`;
      report += `- 公司名称: ${(_c = selectedProject.value) == null ? void 0 : _c.company_name}
`;
      report += `- 评分时间: ${(/* @__PURE__ */ new Date()).toLocaleString()}

`;
      report += `## 总体评分
`;
      report += `**总分: ${scoringResult.value.totalScore} / 100**

`;
      report += `## 各维度评分

`;
      scoringResult.value.dimensions.forEach((dim, index) => {
        report += `### ${index + 1}. ${dim.name} (权重: ${dim.weight}%)
`;
        report += `- 得分: ${dim.score}
`;
        report += `- 加权得分: ${dim.weightedScore.toFixed(2)}
`;
        report += `- 分析:
${dim.analysis}

`;
      });
      report += `## ${scoringResult.value.riskAnalysis}

`;
      report += `## ${scoringResult.value.suggestions}
`;
      return report;
    };
    onMounted(() => {
      loadProjects();
    });
    return (_ctx, _cache) => {
      const _component_el_option = ElOption;
      const _component_el_select = ElSelect;
      const _component_el_form_item = ElFormItem;
      const _component_el_col = ElCol;
      const _component_el_input = ElInput;
      const _component_el_row = ElRow;
      const _component_el_form = ElForm;
      const _component_el_card = ElCard;
      const _component_el_button = ElButton;
      const _component_el_table_column = ElTableColumn;
      const _component_el_input_number = ElInputNumber;
      const _component_el_table = ElTable;
      const _component_el_tag = ElTag;
      return openBlock(), createElementBlock("div", _hoisted_1, [
        createVNode(_component_el_card, {
          class: "project-selector",
          shadow: "never"
        }, {
          header: withCtx(() => [..._cache[1] || (_cache[1] = [
            createBaseVNode("div", { class: "card-header" }, [
              createBaseVNode("span", null, "选择项目")
            ], -1)
          ])]),
          default: withCtx(() => [
            createVNode(_component_el_form, {
              model: form.value,
              "label-width": "100px"
            }, {
              default: withCtx(() => [
                createVNode(_component_el_row, { gutter: 20 }, {
                  default: withCtx(() => [
                    createVNode(_component_el_col, { span: 12 }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, { label: "项目" }, {
                          default: withCtx(() => [
                            createVNode(_component_el_select, {
                              modelValue: form.value.projectId,
                              "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => form.value.projectId = $event),
                              placeholder: "请选择项目",
                              filterable: "",
                              onChange: handleProjectChange,
                              style: { "width": "100%" }
                            }, {
                              default: withCtx(() => [
                                (openBlock(true), createElementBlock(Fragment, null, renderList(projects.value, (project) => {
                                  return openBlock(), createBlock(_component_el_option, {
                                    key: project.id,
                                    label: `${project.project_name} (${project.project_number})`,
                                    value: project.id
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
                    }),
                    createVNode(_component_el_col, { span: 12 }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, { label: "公司" }, {
                          default: withCtx(() => {
                            var _a;
                            return [
                              createVNode(_component_el_input, {
                                value: ((_a = selectedProject.value) == null ? void 0 : _a.company_name) || "-",
                                disabled: ""
                              }, null, 8, ["value"])
                            ];
                          }),
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
            }, 8, ["model"])
          ]),
          _: 1
        }),
        form.value.projectId ? (openBlock(), createBlock(_component_el_card, {
          key: 0,
          class: "scoring-config",
          shadow: "never"
        }, {
          header: withCtx(() => [
            createBaseVNode("div", _hoisted_2, [
              _cache[3] || (_cache[3] = createBaseVNode("span", null, "评分维度配置", -1)),
              createVNode(_component_el_button, {
                type: "primary",
                size: "small",
                onClick: addDimension
              }, {
                default: withCtx(() => [..._cache[2] || (_cache[2] = [
                  createTextVNode(" 添加维度 ", -1)
                ])]),
                _: 1
              })
            ])
          ]),
          default: withCtx(() => [
            createVNode(_component_el_table, {
              data: scoringDimensions.value,
              border: ""
            }, {
              default: withCtx(() => [
                createVNode(_component_el_table_column, {
                  type: "index",
                  label: "序号",
                  width: "60"
                }),
                createVNode(_component_el_table_column, {
                  prop: "name",
                  label: "评分维度",
                  "min-width": "150"
                }, {
                  default: withCtx(({ row }) => [
                    createVNode(_component_el_input, {
                      modelValue: row.name,
                      "onUpdate:modelValue": ($event) => row.name = $event,
                      placeholder: "请输入评分维度"
                    }, null, 8, ["modelValue", "onUpdate:modelValue"])
                  ]),
                  _: 1
                }),
                createVNode(_component_el_table_column, {
                  prop: "weight",
                  label: "权重 (%)",
                  width: "120"
                }, {
                  default: withCtx(({ row }) => [
                    createVNode(_component_el_input_number, {
                      modelValue: row.weight,
                      "onUpdate:modelValue": ($event) => row.weight = $event,
                      min: 0,
                      max: 100,
                      step: 5,
                      "controls-position": "right",
                      style: { "width": "100%" }
                    }, null, 8, ["modelValue", "onUpdate:modelValue"])
                  ]),
                  _: 1
                }),
                createVNode(_component_el_table_column, {
                  prop: "description",
                  label: "评分说明",
                  "min-width": "200"
                }, {
                  default: withCtx(({ row }) => [
                    createVNode(_component_el_input, {
                      modelValue: row.description,
                      "onUpdate:modelValue": ($event) => row.description = $event,
                      type: "textarea",
                      rows: 2,
                      placeholder: "请输入评分说明"
                    }, null, 8, ["modelValue", "onUpdate:modelValue"])
                  ]),
                  _: 1
                }),
                createVNode(_component_el_table_column, {
                  label: "操作",
                  width: "100",
                  fixed: "right"
                }, {
                  default: withCtx(({ $index }) => [
                    createVNode(_component_el_button, {
                      type: "danger",
                      size: "small",
                      text: "",
                      onClick: ($event) => removeDimension($index)
                    }, {
                      default: withCtx(() => [..._cache[4] || (_cache[4] = [
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
            createBaseVNode("div", _hoisted_3, [
              createBaseVNode("div", _hoisted_4, [
                _cache[5] || (_cache[5] = createTextVNode(" 总权重: ", -1)),
                createBaseVNode("strong", {
                  class: normalizeClass({ "error": totalWeight.value !== 100 })
                }, toDisplayString(totalWeight.value) + "%", 3),
                totalWeight.value !== 100 ? (openBlock(), createElementBlock("span", _hoisted_5, " (权重总和应为 100%) ")) : createCommentVNode("", true)
              ]),
              createVNode(_component_el_button, {
                type: "primary",
                disabled: !canStartScoring.value,
                loading: scoringLoading.value,
                onClick: startScoring
              }, {
                default: withCtx(() => [..._cache[6] || (_cache[6] = [
                  createTextVNode(" 开始AI评分 ", -1)
                ])]),
                _: 1
              }, 8, ["disabled", "loading"])
            ])
          ]),
          _: 1
        })) : createCommentVNode("", true),
        scoringResult.value ? (openBlock(), createBlock(_component_el_card, {
          key: 1,
          class: "scoring-result",
          shadow: "never"
        }, {
          header: withCtx(() => [
            createBaseVNode("div", _hoisted_6, [
              _cache[8] || (_cache[8] = createBaseVNode("span", null, "评分结果", -1)),
              createBaseVNode("div", _hoisted_7, [
                createVNode(_component_el_tag, {
                  type: getScoreType(scoringResult.value.totalScore),
                  size: "large"
                }, {
                  default: withCtx(() => [
                    createTextVNode(" 总分: " + toDisplayString(scoringResult.value.totalScore) + " / 100 ", 1)
                  ]),
                  _: 1
                }, 8, ["type"]),
                createVNode(_component_el_button, {
                  type: "success",
                  size: "small",
                  icon: unref(download_default),
                  onClick: exportReport
                }, {
                  default: withCtx(() => [..._cache[7] || (_cache[7] = [
                    createTextVNode(" 导出报告 ", -1)
                  ])]),
                  _: 1
                }, 8, ["icon"])
              ])
            ])
          ]),
          default: withCtx(() => [
            createBaseVNode("div", _hoisted_8, [
              _cache[9] || (_cache[9] = createBaseVNode("h4", null, "各维度评分详情", -1)),
              createVNode(_component_el_table, {
                data: scoringResult.value.dimensions,
                border: ""
              }, {
                default: withCtx(() => [
                  createVNode(_component_el_table_column, {
                    type: "index",
                    label: "序号",
                    width: "60"
                  }),
                  createVNode(_component_el_table_column, {
                    prop: "name",
                    label: "评分维度",
                    "min-width": "150"
                  }),
                  createVNode(_component_el_table_column, {
                    prop: "weight",
                    label: "权重",
                    width: "100"
                  }, {
                    default: withCtx(({ row }) => [
                      createTextVNode(toDisplayString(row.weight) + "% ", 1)
                    ]),
                    _: 1
                  }),
                  createVNode(_component_el_table_column, {
                    prop: "score",
                    label: "得分",
                    width: "100"
                  }, {
                    default: withCtx(({ row }) => [
                      createVNode(_component_el_tag, {
                        type: getScoreType(row.score)
                      }, {
                        default: withCtx(() => [
                          createTextVNode(toDisplayString(row.score), 1)
                        ]),
                        _: 2
                      }, 1032, ["type"])
                    ]),
                    _: 1
                  }),
                  createVNode(_component_el_table_column, {
                    prop: "weightedScore",
                    label: "加权得分",
                    width: "120"
                  }, {
                    default: withCtx(({ row }) => [
                      createTextVNode(toDisplayString(row.weightedScore.toFixed(2)), 1)
                    ]),
                    _: 1
                  }),
                  createVNode(_component_el_table_column, {
                    prop: "analysis",
                    label: "AI分析",
                    "min-width": "300"
                  }, {
                    default: withCtx(({ row }) => [
                      createBaseVNode("div", {
                        class: "analysis-content",
                        innerHTML: formatMarkdown(row.analysis)
                      }, null, 8, _hoisted_9)
                    ]),
                    _: 1
                  })
                ]),
                _: 1
              }, 8, ["data"])
            ]),
            createBaseVNode("div", _hoisted_10, [
              _cache[10] || (_cache[10] = createBaseVNode("h4", null, "风险分析", -1)),
              createVNode(unref(SSEStreamViewer), {
                content: scoringResult.value.riskAnalysis,
                "is-streaming": false,
                "enable-markdown": true
              }, null, 8, ["content"])
            ]),
            createBaseVNode("div", _hoisted_11, [
              _cache[11] || (_cache[11] = createBaseVNode("h4", null, "改进建议", -1)),
              createVNode(unref(SSEStreamViewer), {
                content: scoringResult.value.suggestions,
                "is-streaming": false,
                "enable-markdown": true
              }, null, 8, ["content"])
            ])
          ]),
          _: 1
        })) : createCommentVNode("", true),
        scoringLoading.value ? (openBlock(), createBlock(_component_el_card, {
          key: 2,
          class: "streaming-output",
          shadow: "never"
        }, {
          header: withCtx(() => [..._cache[12] || (_cache[12] = [
            createBaseVNode("div", { class: "card-header" }, [
              createBaseVNode("span", null, "AI正在评分...")
            ], -1)
          ])]),
          default: withCtx(() => [
            createVNode(unref(SSEStreamViewer), {
              content: streamContent.value,
              "is-streaming": scoringLoading.value,
              onStop: stopScoring
            }, null, 8, ["content", "is-streaming"])
          ]),
          _: 1
        })) : createCommentVNode("", true)
      ]);
    };
  }
});
const Scoring = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-f1b01cc5"]]);
export {
  Scoring as default
};
