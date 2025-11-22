import { d as defineComponent, M as useRouter, r as ref, c as computed, S as onMounted, e as createElementBlock, o as openBlock, n as createBaseVNode, f as createVNode, w as withCtx, ad as ElIcon, h as unref, b6 as office_building_default, t as toDisplayString, as as ElCard, b7 as filter_default, k as createBlock, q as ElForm, s as ElFormItem, y as ElInput, aZ as search_default, Y as ElSelect, W as ElOption, g as ElButton, p as createTextVNode, b8 as refresh_left_default, al as ElTable, am as ElTableColumn, aL as ElProgress, X as ElTag, j as ElDialog } from "./vendor-MtO928VE.js";
import { L as Loading } from "./Loading-75jVWA4c.js";
import { E as Empty } from "./Empty-B61dCWeQ.js";
/* empty css                                                                           */
import { C as Card } from "./Card-jLaN2c6R.js";
/* empty css                                                                         */
import { a as useNotification, _ as _export_sfc } from "./index.js";
import { c as companyApi } from "./company-z4Xg082l.js";
const _hoisted_1 = { class: "company-library" };
const _hoisted_2 = { class: "stats-bar" };
const _hoisted_3 = { class: "stat-content" };
const _hoisted_4 = { class: "stat-icon" };
const _hoisted_5 = { class: "stat-info" };
const _hoisted_6 = { class: "stat-value" };
const _hoisted_7 = { class: "stat-content" };
const _hoisted_8 = { class: "stat-icon" };
const _hoisted_9 = { class: "stat-info" };
const _hoisted_10 = { class: "stat-value" };
const _hoisted_11 = { class: "filter-section" };
const _hoisted_12 = { class: "qualification-progress" };
const _hoisted_13 = { class: "progress-text" };
const STANDARD_QUALIFICATION_TOTAL = 17;
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "CompanyLibrary",
  setup(__props) {
    const router = useRouter();
    const { success, error } = useNotification();
    const loading = ref(false);
    const allCompanies = ref([]);
    const filters = ref({
      keyword: "",
      industry: ""
    });
    const createDialogVisible = ref(false);
    const creating = ref(false);
    const createFormRef = ref();
    const createForm = ref({
      companyName: "",
      companyCode: "",
      industryType: "",
      companyDescription: ""
    });
    const createFormRules = {
      companyName: [
        { required: true, message: "请输入企业名称", trigger: "blur" },
        { min: 2, max: 100, message: "企业名称长度在 2 到 100 个字符", trigger: "blur" }
      ]
    };
    const filteredCompanies = computed(() => {
      let result = [...allCompanies.value];
      if (filters.value.keyword) {
        const keyword = filters.value.keyword.toLowerCase();
        result = result.filter((company) => {
          var _a, _b, _c;
          return ((_a = company.company_name) == null ? void 0 : _a.toLowerCase().includes(keyword)) || ((_b = company.social_credit_code) == null ? void 0 : _b.toLowerCase().includes(keyword)) || ((_c = company.company_code) == null ? void 0 : _c.toLowerCase().includes(keyword));
        });
      }
      if (filters.value.industry) {
        result = result.filter((company) => company.industry_type === filters.value.industry);
      }
      return result;
    });
    const loadCompanies = async () => {
      loading.value = true;
      try {
        const response = await companyApi.getCompanies();
        const rawData = response.data || [];
        const companiesWithQualifications = await Promise.all(
          rawData.map(async (company) => {
            let qualificationCompleted = 0;
            try {
              const qualResponse = await companyApi.getCompanyQualifications(company.company_id);
              if (qualResponse.data) {
                qualificationCompleted = Object.keys(qualResponse.data).length;
              }
            } catch (err) {
              console.error(`加载企业${company.company_id}资质信息失败:`, err);
            }
            const qualificationTotal = STANDARD_QUALIFICATION_TOTAL;
            const qualificationProgress = qualificationTotal > 0 ? Math.round(qualificationCompleted / qualificationTotal * 100) : 0;
            return {
              company_id: company.company_id,
              company_name: company.company_name || "未命名",
              company_code: company.company_code || "",
              social_credit_code: company.social_credit_code || "-",
              legal_representative: company.legal_representative || "-",
              registered_capital: company.registered_capital || "-",
              employee_count: company.employee_count || "-",
              industry_type: company.industry_type || "",
              product_count: company.product_count || 0,
              document_count: company.document_count || 0,
              qualification_completed: qualificationCompleted,
              qualification_total: qualificationTotal,
              qualification_progress: qualificationProgress,
              created_at: company.created_at || "-",
              updated_at: company.updated_at || "-",
              ...company
            };
          })
        );
        allCompanies.value = companiesWithQualifications;
      } catch (err) {
        console.error("加载企业列表失败:", err);
        error("加载失败", err instanceof Error ? err.message : "未知错误");
      } finally {
        loading.value = false;
      }
    };
    const handleSearch = () => {
    };
    const handleResetFilters = () => {
      filters.value.keyword = "";
      filters.value.industry = "";
    };
    const getProgressColor = (percentage) => {
      if (percentage < 30) return "#f56c6c";
      if (percentage < 70) return "#e6a23c";
      return "#67c23a";
    };
    const handleConfirmCreate = async () => {
      if (!createFormRef.value) return;
      await createFormRef.value.validate(async (valid) => {
        if (!valid) return;
        creating.value = true;
        try {
          const response = await companyApi.createCompany({
            name: createForm.value.companyName,
            code: createForm.value.companyCode || void 0,
            description: createForm.value.companyDescription || void 0
          });
          if (response.success) {
            success("创建成功", "企业创建成功");
            createDialogVisible.value = false;
            await loadCompanies();
          }
        } catch (err) {
          console.error("创建企业失败:", err);
          error("创建失败", err instanceof Error ? err.message : "未知错误");
        } finally {
          creating.value = false;
        }
      });
    };
    const handleDialogClose = () => {
      var _a;
      createForm.value = {
        companyName: "",
        companyCode: "",
        industryType: "",
        companyDescription: ""
      };
      (_a = createFormRef.value) == null ? void 0 : _a.resetFields();
    };
    const handleView = (row) => {
      router.push(`/knowledge/company/${row.company_id}`);
    };
    const handleEdit = (row) => {
      router.push(`/knowledge/company/${row.company_id}`);
    };
    const handleDelete = async (row) => {
      try {
        if (!confirm(`确定要删除企业 "${row.company_name}" 吗？此操作将同时删除企业的所有产品和文档，且不可恢复。`)) {
          return;
        }
        await companyApi.deleteCompany(row.company_id);
        success("删除成功", `已删除企业: ${row.company_name}`);
        await loadCompanies();
      } catch (err) {
        console.error("删除企业失败:", err);
        error("删除失败", err instanceof Error ? err.message : "未知错误");
      }
    };
    onMounted(() => {
      loadCompanies();
    });
    return (_ctx, _cache) => {
      const _component_el_icon = ElIcon;
      const _component_el_card = ElCard;
      const _component_el_input = ElInput;
      const _component_el_form_item = ElFormItem;
      const _component_el_option = ElOption;
      const _component_el_select = ElSelect;
      const _component_el_button = ElButton;
      const _component_el_form = ElForm;
      const _component_el_table_column = ElTableColumn;
      const _component_el_progress = ElProgress;
      const _component_el_tag = ElTag;
      const _component_el_table = ElTable;
      const _component_el_dialog = ElDialog;
      return openBlock(), createElementBlock("div", _hoisted_1, [
        createBaseVNode("div", _hoisted_2, [
          createVNode(_component_el_card, { class: "stat-card" }, {
            default: withCtx(() => [
              createBaseVNode("div", _hoisted_3, [
                createBaseVNode("div", _hoisted_4, [
                  createVNode(_component_el_icon, {
                    size: 32,
                    color: "#409eff"
                  }, {
                    default: withCtx(() => [
                      createVNode(unref(office_building_default))
                    ]),
                    _: 1
                  })
                ]),
                createBaseVNode("div", _hoisted_5, [
                  _cache[8] || (_cache[8] = createBaseVNode("div", { class: "stat-label" }, "总企业数", -1)),
                  createBaseVNode("div", _hoisted_6, toDisplayString(allCompanies.value.length), 1)
                ])
              ])
            ]),
            _: 1
          }),
          createVNode(_component_el_card, { class: "stat-card" }, {
            default: withCtx(() => [
              createBaseVNode("div", _hoisted_7, [
                createBaseVNode("div", _hoisted_8, [
                  createVNode(_component_el_icon, {
                    size: 32,
                    color: "#67c23a"
                  }, {
                    default: withCtx(() => [
                      createVNode(unref(filter_default))
                    ]),
                    _: 1
                  })
                ]),
                createBaseVNode("div", _hoisted_9, [
                  _cache[9] || (_cache[9] = createBaseVNode("div", { class: "stat-label" }, "筛选结果", -1)),
                  createBaseVNode("div", _hoisted_10, toDisplayString(filteredCompanies.value.length), 1)
                ])
              ])
            ]),
            _: 1
          })
        ]),
        createVNode(unref(Card), { title: "企业列表" }, {
          default: withCtx(() => [
            createBaseVNode("div", _hoisted_11, [
              createVNode(_component_el_form, {
                inline: true,
                model: filters.value
              }, {
                default: withCtx(() => [
                  createVNode(_component_el_form_item, { label: "搜索" }, {
                    default: withCtx(() => [
                      createVNode(_component_el_input, {
                        modelValue: filters.value.keyword,
                        "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => filters.value.keyword = $event),
                        placeholder: "搜索企业名称、社会信用代码...",
                        clearable: "",
                        style: { "width": "300px" },
                        onInput: handleSearch
                      }, {
                        prefix: withCtx(() => [
                          createVNode(_component_el_icon, null, {
                            default: withCtx(() => [
                              createVNode(unref(search_default))
                            ]),
                            _: 1
                          })
                        ]),
                        _: 1
                      }, 8, ["modelValue"])
                    ]),
                    _: 1
                  }),
                  createVNode(_component_el_form_item, { label: "行业类型" }, {
                    default: withCtx(() => [
                      createVNode(_component_el_select, {
                        modelValue: filters.value.industry,
                        "onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => filters.value.industry = $event),
                        placeholder: "全部行业",
                        clearable: "",
                        style: { "width": "150px" },
                        onChange: handleSearch
                      }, {
                        default: withCtx(() => [
                          createVNode(_component_el_option, {
                            label: "全部行业",
                            value: ""
                          }),
                          createVNode(_component_el_option, {
                            label: "科技",
                            value: "technology"
                          }),
                          createVNode(_component_el_option, {
                            label: "制造业",
                            value: "manufacturing"
                          }),
                          createVNode(_component_el_option, {
                            label: "金融",
                            value: "finance"
                          }),
                          createVNode(_component_el_option, {
                            label: "教育",
                            value: "education"
                          }),
                          createVNode(_component_el_option, {
                            label: "医疗",
                            value: "healthcare"
                          }),
                          createVNode(_component_el_option, {
                            label: "零售",
                            value: "retail"
                          }),
                          createVNode(_component_el_option, {
                            label: "建筑",
                            value: "construction"
                          }),
                          createVNode(_component_el_option, {
                            label: "其他",
                            value: "other"
                          })
                        ]),
                        _: 1
                      }, 8, ["modelValue"])
                    ]),
                    _: 1
                  }),
                  createVNode(_component_el_form_item, null, {
                    default: withCtx(() => [
                      createVNode(_component_el_button, { onClick: handleResetFilters }, {
                        default: withCtx(() => [
                          createVNode(_component_el_icon, null, {
                            default: withCtx(() => [
                              createVNode(unref(refresh_left_default))
                            ]),
                            _: 1
                          }),
                          _cache[10] || (_cache[10] = createTextVNode(" 重置 ", -1))
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
            loading.value ? (openBlock(), createBlock(unref(Loading), {
              key: 0,
              text: "加载中..."
            })) : !filteredCompanies.value.length ? (openBlock(), createBlock(unref(Empty), {
              key: 1,
              type: "no-data",
              description: "暂无企业数据"
            })) : (openBlock(), createBlock(_component_el_table, {
              key: 2,
              data: filteredCompanies.value,
              stripe: "",
              style: { "width": "100%" }
            }, {
              default: withCtx(() => [
                createVNode(_component_el_table_column, {
                  prop: "company_id",
                  label: "ID",
                  width: "70",
                  fixed: ""
                }),
                createVNode(_component_el_table_column, {
                  prop: "company_name",
                  label: "企业名称",
                  "min-width": "200",
                  fixed: "",
                  "show-overflow-tooltip": ""
                }),
                createVNode(_component_el_table_column, {
                  prop: "social_credit_code",
                  label: "统一社会信用代码",
                  width: "180",
                  "show-overflow-tooltip": ""
                }),
                createVNode(_component_el_table_column, {
                  prop: "legal_representative",
                  label: "法定代表人",
                  width: "120"
                }),
                createVNode(_component_el_table_column, {
                  prop: "registered_capital",
                  label: "注册资本",
                  width: "120"
                }),
                createVNode(_component_el_table_column, {
                  prop: "employee_count",
                  label: "员工人数",
                  width: "100",
                  align: "center"
                }),
                createVNode(_component_el_table_column, {
                  label: "资质完成度",
                  width: "180",
                  align: "center"
                }, {
                  default: withCtx(({ row }) => [
                    createBaseVNode("div", _hoisted_12, [
                      createVNode(_component_el_progress, {
                        percentage: row.qualification_progress || 0,
                        color: getProgressColor(row.qualification_progress || 0),
                        "stroke-width": 8
                      }, null, 8, ["percentage", "color"]),
                      createBaseVNode("span", _hoisted_13, toDisplayString(row.qualification_completed || 0) + "/" + toDisplayString(row.qualification_total || 17), 1)
                    ])
                  ]),
                  _: 1
                }),
                createVNode(_component_el_table_column, {
                  prop: "product_count",
                  label: "产品数",
                  width: "90",
                  align: "center"
                }, {
                  default: withCtx(({ row }) => [
                    createVNode(_component_el_tag, {
                      size: "small",
                      type: "info"
                    }, {
                      default: withCtx(() => [
                        createTextVNode(toDisplayString(row.product_count || 0), 1)
                      ]),
                      _: 2
                    }, 1024)
                  ]),
                  _: 1
                }),
                createVNode(_component_el_table_column, {
                  prop: "document_count",
                  label: "文档数",
                  width: "90",
                  align: "center"
                }, {
                  default: withCtx(({ row }) => [
                    createVNode(_component_el_tag, {
                      size: "small",
                      type: "success"
                    }, {
                      default: withCtx(() => [
                        createTextVNode(toDisplayString(row.document_count || 0), 1)
                      ]),
                      _: 2
                    }, 1024)
                  ]),
                  _: 1
                }),
                createVNode(_component_el_table_column, {
                  prop: "created_at",
                  label: "创建时间",
                  width: "160",
                  "show-overflow-tooltip": ""
                }),
                createVNode(_component_el_table_column, {
                  prop: "updated_at",
                  label: "更新时间",
                  width: "160",
                  "show-overflow-tooltip": ""
                }),
                createVNode(_component_el_table_column, {
                  label: "操作",
                  width: "220",
                  fixed: "right"
                }, {
                  default: withCtx(({ row }) => [
                    createVNode(_component_el_button, {
                      text: "",
                      type: "primary",
                      size: "small",
                      onClick: ($event) => handleView(row)
                    }, {
                      default: withCtx(() => [..._cache[11] || (_cache[11] = [
                        createTextVNode(" 查看详情 ", -1)
                      ])]),
                      _: 1
                    }, 8, ["onClick"]),
                    createVNode(_component_el_button, {
                      text: "",
                      type: "warning",
                      size: "small",
                      onClick: ($event) => handleEdit(row)
                    }, {
                      default: withCtx(() => [..._cache[12] || (_cache[12] = [
                        createTextVNode(" 编辑 ", -1)
                      ])]),
                      _: 1
                    }, 8, ["onClick"]),
                    createVNode(_component_el_button, {
                      text: "",
                      type: "danger",
                      size: "small",
                      onClick: ($event) => handleDelete(row)
                    }, {
                      default: withCtx(() => [..._cache[13] || (_cache[13] = [
                        createTextVNode(" 删除 ", -1)
                      ])]),
                      _: 1
                    }, 8, ["onClick"])
                  ]),
                  _: 1
                })
              ]),
              _: 1
            }, 8, ["data"]))
          ]),
          _: 1
        }),
        createVNode(_component_el_dialog, {
          modelValue: createDialogVisible.value,
          "onUpdate:modelValue": _cache[7] || (_cache[7] = ($event) => createDialogVisible.value = $event),
          title: "新建企业",
          width: "500px",
          onClose: handleDialogClose
        }, {
          footer: withCtx(() => [
            createVNode(_component_el_button, {
              onClick: _cache[6] || (_cache[6] = ($event) => createDialogVisible.value = false)
            }, {
              default: withCtx(() => [..._cache[14] || (_cache[14] = [
                createTextVNode("取消", -1)
              ])]),
              _: 1
            }),
            createVNode(_component_el_button, {
              type: "primary",
              loading: creating.value,
              onClick: handleConfirmCreate
            }, {
              default: withCtx(() => [..._cache[15] || (_cache[15] = [
                createTextVNode(" 确定 ", -1)
              ])]),
              _: 1
            }, 8, ["loading"])
          ]),
          default: withCtx(() => [
            createVNode(_component_el_form, {
              ref_key: "createFormRef",
              ref: createFormRef,
              model: createForm.value,
              rules: createFormRules,
              "label-width": "120px"
            }, {
              default: withCtx(() => [
                createVNode(_component_el_form_item, {
                  label: "企业名称",
                  prop: "companyName"
                }, {
                  default: withCtx(() => [
                    createVNode(_component_el_input, {
                      modelValue: createForm.value.companyName,
                      "onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => createForm.value.companyName = $event),
                      placeholder: "请输入企业名称"
                    }, null, 8, ["modelValue"])
                  ]),
                  _: 1
                }),
                createVNode(_component_el_form_item, {
                  label: "企业代码",
                  prop: "companyCode"
                }, {
                  default: withCtx(() => [
                    createVNode(_component_el_input, {
                      modelValue: createForm.value.companyCode,
                      "onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => createForm.value.companyCode = $event),
                      placeholder: "请输入企业代码（可选）"
                    }, null, 8, ["modelValue"])
                  ]),
                  _: 1
                }),
                createVNode(_component_el_form_item, {
                  label: "行业类型",
                  prop: "industryType"
                }, {
                  default: withCtx(() => [
                    createVNode(_component_el_select, {
                      modelValue: createForm.value.industryType,
                      "onUpdate:modelValue": _cache[4] || (_cache[4] = ($event) => createForm.value.industryType = $event),
                      placeholder: "请选择行业类型",
                      style: { "width": "100%" }
                    }, {
                      default: withCtx(() => [
                        createVNode(_component_el_option, {
                          label: "科技",
                          value: "technology"
                        }),
                        createVNode(_component_el_option, {
                          label: "制造业",
                          value: "manufacturing"
                        }),
                        createVNode(_component_el_option, {
                          label: "金融",
                          value: "finance"
                        }),
                        createVNode(_component_el_option, {
                          label: "教育",
                          value: "education"
                        }),
                        createVNode(_component_el_option, {
                          label: "医疗",
                          value: "healthcare"
                        }),
                        createVNode(_component_el_option, {
                          label: "零售",
                          value: "retail"
                        }),
                        createVNode(_component_el_option, {
                          label: "建筑",
                          value: "construction"
                        }),
                        createVNode(_component_el_option, {
                          label: "其他",
                          value: "other"
                        })
                      ]),
                      _: 1
                    }, 8, ["modelValue"])
                  ]),
                  _: 1
                }),
                createVNode(_component_el_form_item, {
                  label: "企业简介",
                  prop: "companyDescription"
                }, {
                  default: withCtx(() => [
                    createVNode(_component_el_input, {
                      modelValue: createForm.value.companyDescription,
                      "onUpdate:modelValue": _cache[5] || (_cache[5] = ($event) => createForm.value.companyDescription = $event),
                      type: "textarea",
                      rows: 3,
                      placeholder: "请输入企业简介（可选）"
                    }, null, 8, ["modelValue"])
                  ]),
                  _: 1
                })
              ]),
              _: 1
            }, 8, ["model"])
          ]),
          _: 1
        }, 8, ["modelValue"])
      ]);
    };
  }
});
const CompanyLibrary = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-bc300562"]]);
export {
  CompanyLibrary as default
};
