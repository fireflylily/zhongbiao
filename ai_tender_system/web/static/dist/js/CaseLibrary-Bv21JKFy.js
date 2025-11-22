import { d as defineComponent, M as useRouter, r as ref, c as computed, S as onMounted, e as createElementBlock, o as openBlock, n as createBaseVNode, f as createVNode, w as withCtx, ad as ElIcon, h as unref, ae as document_default, t as toDisplayString, as as ElCard, bk as success_filled_default, bl as money_default, k as createBlock, q as ElForm, s as ElFormItem, y as ElInput, aZ as search_default, Y as ElSelect, W as ElOption, g as ElButton, p as createTextVNode, b8 as refresh_left_default, al as ElTable, am as ElTableColumn, X as ElTag, bd as plus_default } from "./vendor-MtO928VE.js";
import { L as Loading } from "./Loading-D6Ei-uTU.js";
import { E as Empty } from "./Empty-CMm3i0ir.js";
/* empty css                                                                           */
import { C as Card } from "./Card-CPf5jQx8.js";
/* empty css                                                                         */
import { a as useNotification, _ as _export_sfc } from "./index.js";
import { k as knowledgeApi, f as formatDate } from "./formatters-DrGE7noj.js";
import { c as companyApi } from "./company-z4Xg082l.js";
const _hoisted_1 = { class: "case-library" };
const _hoisted_2 = { class: "stats-bar" };
const _hoisted_3 = { class: "stat-content" };
const _hoisted_4 = { class: "stat-icon" };
const _hoisted_5 = { class: "stat-info" };
const _hoisted_6 = { class: "stat-value" };
const _hoisted_7 = { class: "stat-content" };
const _hoisted_8 = { class: "stat-icon" };
const _hoisted_9 = { class: "stat-info" };
const _hoisted_10 = { class: "stat-value" };
const _hoisted_11 = { class: "stat-content" };
const _hoisted_12 = { class: "stat-icon" };
const _hoisted_13 = { class: "stat-info" };
const _hoisted_14 = { class: "stat-value" };
const _hoisted_15 = { class: "filter-section" };
const _hoisted_16 = {
  key: 1,
  style: { "color": "#909399" }
};
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "CaseLibrary",
  setup(__props) {
    const router = useRouter();
    const { success, error } = useNotification();
    const loading = ref(false);
    const creating = ref(false);
    const allCases = ref([]);
    const companies = ref([]);
    const currentCompanyId = ref();
    const filters = ref({
      keyword: "",
      productCategory: "",
      industry: "",
      contractType: ""
    });
    const filteredCases = computed(() => {
      let result = [...allCases.value];
      if (filters.value.keyword) {
        const keyword = filters.value.keyword.toLowerCase();
        result = result.filter((c) => {
          var _a, _b, _c;
          return ((_a = c.case_title) == null ? void 0 : _a.toLowerCase().includes(keyword)) || ((_b = c.customer_name) == null ? void 0 : _b.toLowerCase().includes(keyword)) || ((_c = c.case_number) == null ? void 0 : _c.toLowerCase().includes(keyword));
        });
      }
      if (filters.value.productCategory) {
        result = result.filter((c) => c.product_category === filters.value.productCategory);
      }
      if (filters.value.industry) {
        result = result.filter((c) => c.industry === filters.value.industry);
      }
      if (filters.value.contractType) {
        result = result.filter((c) => c.contract_type === filters.value.contractType);
      }
      return result;
    });
    const contractCasesCount = computed(() => {
      return allCases.value.filter((c) => c.contract_type === "合同").length;
    });
    const totalContractAmount = computed(() => {
      let total = 0;
      allCases.value.forEach((c) => {
        if (c.contract_amount) {
          const match = c.contract_amount.match(/[\d.]+/);
          if (match) {
            const num = parseFloat(match[0]);
            if (c.contract_amount.includes("万")) {
              total += num * 1e4;
            } else if (c.contract_amount.includes("亿")) {
              total += num * 1e8;
            } else {
              total += num;
            }
          }
        }
      });
      if (total >= 1e8) {
        return `${(total / 1e8).toFixed(2)}亿`;
      } else if (total >= 1e4) {
        return `${(total / 1e4).toFixed(2)}万`;
      }
      return total.toFixed(2);
    });
    const loadCases = async () => {
      loading.value = true;
      try {
        const response = await knowledgeApi.getCases({
          company_id: currentCompanyId.value
        });
        if (response.success && response.data) {
          allCases.value = response.data.map((c) => ({
            ...c,
            contract_start_date: c.contract_start_date ? formatDate(c.contract_start_date, "date") : "-",
            contract_end_date: c.contract_end_date ? formatDate(c.contract_end_date, "date") : "-",
            created_at: c.created_at ? formatDate(c.created_at) : "-"
          }));
        }
      } catch (err) {
        console.error("加载案例列表失败:", err);
        error("加载失败", err instanceof Error ? err.message : "未知错误");
      } finally {
        loading.value = false;
      }
    };
    const loadCompanies = async () => {
      try {
        const response = await companyApi.getCompanies();
        if (response.success && response.data) {
          companies.value = response.data;
          if (companies.value.length > 0 && !currentCompanyId.value) {
            currentCompanyId.value = companies.value[0].company_id;
            await loadCases();
          }
        }
      } catch (err) {
        console.error("加载企业列表失败:", err);
      }
    };
    const handleSearch = () => {
    };
    const handleResetFilters = () => {
      filters.value.keyword = "";
      filters.value.productCategory = "";
      filters.value.industry = "";
      filters.value.contractType = "";
    };
    const handleCreate = async () => {
      var _a;
      if (companies.value.length === 0) {
        error("无法创建", "请先添加企业信息");
        return;
      }
      creating.value = true;
      try {
        const companyId = currentCompanyId.value || ((_a = companies.value[0]) == null ? void 0 : _a.company_id);
        const response = await knowledgeApi.createCase({
          company_id: companyId,
          case_title: "新建案例",
          customer_name: "待完善",
          industry: "金融",
          contract_type: "合同"
        });
        if (response.success && response.data) {
          success("创建成功", "正在跳转到编辑页面...");
          router.push(`/knowledge/case/${response.data.case_id}`);
        } else {
          error("创建失败", response.error || "未知错误");
        }
      } catch (err) {
        console.error("创建案例失败:", err);
        error("创建失败", err instanceof Error ? err.message : "未知错误");
      } finally {
        creating.value = false;
      }
    };
    const handleView = (row) => {
      router.push(`/knowledge/case/${row.case_id}`);
    };
    const handleEdit = (row) => {
      router.push(`/knowledge/case/${row.case_id}`);
    };
    const handleDelete = async (row) => {
      try {
        if (!confirm(`确定要删除案例 "${row.case_title}" 吗？此操作不可恢复。`)) {
          return;
        }
        const response = await knowledgeApi.deleteCase(row.case_id);
        if (response.success) {
          success("删除成功", `已删除案例: ${row.case_title}`);
          await loadCases();
        } else {
          error("删除失败", response.error || "未知错误");
        }
      } catch (err) {
        console.error("删除案例失败:", err);
        error("删除失败", err instanceof Error ? err.message : "未知错误");
      }
    };
    onMounted(async () => {
      await loadCompanies();
    });
    return (_ctx, _cache) => {
      const _component_el_icon = ElIcon;
      const _component_el_card = ElCard;
      const _component_el_button = ElButton;
      const _component_el_input = ElInput;
      const _component_el_form_item = ElFormItem;
      const _component_el_option = ElOption;
      const _component_el_select = ElSelect;
      const _component_el_form = ElForm;
      const _component_el_table_column = ElTableColumn;
      const _component_el_tag = ElTag;
      const _component_el_table = ElTable;
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
                      createVNode(unref(document_default))
                    ]),
                    _: 1
                  })
                ]),
                createBaseVNode("div", _hoisted_5, [
                  _cache[4] || (_cache[4] = createBaseVNode("div", { class: "stat-label" }, "总案例数", -1)),
                  createBaseVNode("div", _hoisted_6, toDisplayString(allCases.value.length), 1)
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
                      createVNode(unref(success_filled_default))
                    ]),
                    _: 1
                  })
                ]),
                createBaseVNode("div", _hoisted_9, [
                  _cache[5] || (_cache[5] = createBaseVNode("div", { class: "stat-label" }, "合同案例", -1)),
                  createBaseVNode("div", _hoisted_10, toDisplayString(contractCasesCount.value), 1)
                ])
              ])
            ]),
            _: 1
          }),
          createVNode(_component_el_card, { class: "stat-card" }, {
            default: withCtx(() => [
              createBaseVNode("div", _hoisted_11, [
                createBaseVNode("div", _hoisted_12, [
                  createVNode(_component_el_icon, {
                    size: 32,
                    color: "#e6a23c"
                  }, {
                    default: withCtx(() => [
                      createVNode(unref(money_default))
                    ]),
                    _: 1
                  })
                ]),
                createBaseVNode("div", _hoisted_13, [
                  _cache[6] || (_cache[6] = createBaseVNode("div", { class: "stat-label" }, "合同总额", -1)),
                  createBaseVNode("div", _hoisted_14, toDisplayString(totalContractAmount.value), 1)
                ])
              ])
            ]),
            _: 1
          })
        ]),
        createVNode(unref(Card), { title: "案例列表" }, {
          actions: withCtx(() => [
            createVNode(_component_el_button, {
              type: "primary",
              loading: creating.value,
              onClick: handleCreate
            }, {
              default: withCtx(() => [
                createVNode(_component_el_icon, null, {
                  default: withCtx(() => [
                    createVNode(unref(plus_default))
                  ]),
                  _: 1
                }),
                _cache[7] || (_cache[7] = createTextVNode(" 新建案例 ", -1))
              ]),
              _: 1
            }, 8, ["loading"])
          ]),
          default: withCtx(() => [
            createBaseVNode("div", _hoisted_15, [
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
                        placeholder: "搜索案例标题、客户名称...",
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
                  createVNode(_component_el_form_item, { label: "产品分类" }, {
                    default: withCtx(() => [
                      createVNode(_component_el_select, {
                        modelValue: filters.value.productCategory,
                        "onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => filters.value.productCategory = $event),
                        placeholder: "全部产品",
                        clearable: "",
                        style: { "width": "130px" },
                        onChange: handleSearch
                      }, {
                        default: withCtx(() => [
                          createVNode(_component_el_option, {
                            label: "全部产品",
                            value: ""
                          }),
                          createVNode(_component_el_option, {
                            label: "风控产品",
                            value: "风控产品"
                          }),
                          createVNode(_component_el_option, {
                            label: "实修",
                            value: "实修"
                          }),
                          createVNode(_component_el_option, {
                            label: "免密",
                            value: "免密"
                          }),
                          createVNode(_component_el_option, {
                            label: "风控位置",
                            value: "风控位置"
                          })
                        ]),
                        _: 1
                      }, 8, ["modelValue"])
                    ]),
                    _: 1
                  }),
                  createVNode(_component_el_form_item, { label: "行业" }, {
                    default: withCtx(() => [
                      createVNode(_component_el_select, {
                        modelValue: filters.value.industry,
                        "onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => filters.value.industry = $event),
                        placeholder: "全部行业",
                        clearable: "",
                        style: { "width": "120px" },
                        onChange: handleSearch
                      }, {
                        default: withCtx(() => [
                          createVNode(_component_el_option, {
                            label: "全部行业",
                            value: ""
                          }),
                          createVNode(_component_el_option, {
                            label: "科技",
                            value: "科技"
                          }),
                          createVNode(_component_el_option, {
                            label: "制造业",
                            value: "制造业"
                          }),
                          createVNode(_component_el_option, {
                            label: "金融",
                            value: "金融"
                          }),
                          createVNode(_component_el_option, {
                            label: "教育",
                            value: "教育"
                          }),
                          createVNode(_component_el_option, {
                            label: "医疗",
                            value: "医疗"
                          }),
                          createVNode(_component_el_option, {
                            label: "建筑",
                            value: "建筑"
                          }),
                          createVNode(_component_el_option, {
                            label: "其他",
                            value: "其他"
                          })
                        ]),
                        _: 1
                      }, 8, ["modelValue"])
                    ]),
                    _: 1
                  }),
                  createVNode(_component_el_form_item, { label: "合同类型" }, {
                    default: withCtx(() => [
                      createVNode(_component_el_select, {
                        modelValue: filters.value.contractType,
                        "onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => filters.value.contractType = $event),
                        placeholder: "全部类型",
                        clearable: "",
                        style: { "width": "120px" },
                        onChange: handleSearch
                      }, {
                        default: withCtx(() => [
                          createVNode(_component_el_option, {
                            label: "全部类型",
                            value: ""
                          }),
                          createVNode(_component_el_option, {
                            label: "合同",
                            value: "合同"
                          }),
                          createVNode(_component_el_option, {
                            label: "订单",
                            value: "订单"
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
                          _cache[8] || (_cache[8] = createTextVNode(" 重置 ", -1))
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
            })) : !filteredCases.value.length ? (openBlock(), createBlock(unref(Empty), {
              key: 1,
              type: "no-data",
              description: "暂无案例数据"
            })) : (openBlock(), createBlock(_component_el_table, {
              key: 2,
              data: filteredCases.value,
              stripe: "",
              style: { "width": "100%" }
            }, {
              default: withCtx(() => [
                createVNode(_component_el_table_column, {
                  prop: "case_id",
                  label: "ID",
                  width: "70",
                  fixed: ""
                }),
                createVNode(_component_el_table_column, {
                  prop: "case_title",
                  label: "案例标题",
                  "min-width": "200",
                  fixed: "",
                  "show-overflow-tooltip": ""
                }),
                createVNode(_component_el_table_column, {
                  prop: "customer_name",
                  label: "客户名称",
                  width: "180",
                  "show-overflow-tooltip": ""
                }),
                createVNode(_component_el_table_column, {
                  prop: "product_category",
                  label: "产品分类",
                  width: "110",
                  align: "center"
                }, {
                  default: withCtx(({ row }) => [
                    row.product_category ? (openBlock(), createBlock(_component_el_tag, {
                      key: 0,
                      type: "primary",
                      size: "small"
                    }, {
                      default: withCtx(() => [
                        createTextVNode(toDisplayString(row.product_category), 1)
                      ]),
                      _: 2
                    }, 1024)) : (openBlock(), createElementBlock("span", _hoisted_16, "-"))
                  ]),
                  _: 1
                }),
                createVNode(_component_el_table_column, {
                  prop: "industry",
                  label: "所属行业",
                  width: "100"
                }),
                createVNode(_component_el_table_column, {
                  prop: "contract_type",
                  label: "合同类型",
                  width: "100",
                  align: "center"
                }, {
                  default: withCtx(({ row }) => [
                    createVNode(_component_el_tag, {
                      type: row.contract_type === "合同" ? "primary" : "success",
                      size: "small"
                    }, {
                      default: withCtx(() => [
                        createTextVNode(toDisplayString(row.contract_type), 1)
                      ]),
                      _: 2
                    }, 1032, ["type"])
                  ]),
                  _: 1
                }),
                createVNode(_component_el_table_column, {
                  prop: "contract_amount",
                  label: "合同金额",
                  width: "120",
                  align: "right"
                }),
                createVNode(_component_el_table_column, {
                  prop: "contract_start_date",
                  label: "合同开始日期",
                  width: "120"
                }),
                createVNode(_component_el_table_column, {
                  prop: "contract_end_date",
                  label: "合同结束日期",
                  width: "120"
                }),
                createVNode(_component_el_table_column, {
                  prop: "created_at",
                  label: "创建时间",
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
                      default: withCtx(() => [..._cache[9] || (_cache[9] = [
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
                      default: withCtx(() => [..._cache[10] || (_cache[10] = [
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
                      default: withCtx(() => [..._cache[11] || (_cache[11] = [
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
        })
      ]);
    };
  }
});
const CaseLibrary = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-f9e054aa"]]);
export {
  CaseLibrary as default
};
