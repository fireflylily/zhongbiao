import { d as defineComponent, r as ref, c as computed, e as createElementBlock, o as openBlock, f as createVNode, w as withCtx, F as Fragment, V as renderList, k as createBlock, ai as ElCol, as as ElCard, n as createBaseVNode, ad as ElIcon, U as normalizeClass, ah as resolveDynamicComponent, t as toDisplayString, ak as ElRow, al as ElTable, am as ElTableColumn, X as ElTag, p as createTextVNode, aL as ElProgress, g as ElButton, h as unref, aT as refresh_default, ay as ElDescriptions, az as ElDescriptionsItem, Y as ElSelect, W as ElOption, bu as timer_default, bv as cpu_default, bw as data_analysis_default, ae as document_default } from "./vendor-_9UVkM6-.js";
import { _ as _export_sfc } from "./index.js";
const _hoisted_1 = { class: "system-status" };
const _hoisted_2 = { class: "overview-content" };
const _hoisted_3 = { class: "overview-info" };
const _hoisted_4 = { class: "overview-label" };
const _hoisted_5 = { class: "overview-value" };
const _hoisted_6 = { style: { "display": "flex", "justify-content": "space-between", "align-items": "center" } };
const _hoisted_7 = { style: { "padding": "20px" } };
const _hoisted_8 = { style: { "font-size": "14px" } };
const _hoisted_9 = { style: { "margin-top": "20px", "text-align": "center" } };
const _hoisted_10 = { style: { "display": "flex", "justify-content": "space-between", "align-items": "center" } };
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "Status",
  setup(__props) {
    const overviewData = ref([
      {
        label: "系统运行时长",
        value: "15天 8小时",
        icon: timer_default,
        iconClass: "icon-primary"
      },
      {
        label: "CPU使用率",
        value: "45%",
        icon: cpu_default,
        iconClass: "icon-success"
      },
      {
        label: "内存使用",
        value: "8.2 GB / 16 GB",
        icon: data_analysis_default,
        iconClass: "icon-warning"
      },
      {
        label: "今日处理文档",
        value: "1,234",
        icon: document_default,
        iconClass: "icon-info"
      }
    ]);
    const services = ref([
      {
        name: "Web服务",
        status: "running",
        uptime: "15天 8小时",
        cpu: 35,
        memory: 52,
        requests: 1234,
        avgResponseTime: "45ms"
      },
      {
        name: "AI服务",
        status: "running",
        uptime: "15天 8小时",
        cpu: 78,
        memory: 68,
        requests: 567,
        avgResponseTime: "1.2s"
      },
      {
        name: "文档处理服务",
        status: "running",
        uptime: "15天 8小时",
        cpu: 42,
        memory: 45,
        requests: 234,
        avgResponseTime: "380ms"
      },
      {
        name: "知识库服务",
        status: "running",
        uptime: "15天 8小时",
        cpu: 28,
        memory: 38,
        requests: 890,
        avgResponseTime: "120ms"
      }
    ]);
    const dbInfo = ref({
      type: "PostgreSQL",
      version: "14.5",
      connected: true,
      activeConnections: 12,
      idleConnections: 8,
      maxConnections: 100,
      size: "2.5 GB",
      tables: 45,
      slowQueries: 3
    });
    const diskUsage = ref({
      percentage: 68,
      used: "340 GB",
      total: "500 GB"
    });
    const logLevel = ref("all");
    const logs = ref([
      {
        time: "2025-01-15 10:23:45",
        level: "info",
        module: "Web服务",
        message: "用户登录成功: admin"
      },
      {
        time: "2025-01-15 10:22:30",
        level: "info",
        module: "AI服务",
        message: "文档处理任务完成: task_12345"
      },
      {
        time: "2025-01-15 10:21:15",
        level: "warning",
        module: "数据库",
        message: "慢查询检测: 查询耗时3.2秒"
      },
      {
        time: "2025-01-15 10:20:00",
        level: "error",
        module: "AI服务",
        message: "API调用失败: 超时"
      },
      {
        time: "2025-01-15 10:18:45",
        level: "info",
        module: "知识库",
        message: "文档索引更新完成"
      }
    ]);
    const filteredLogs = computed(() => {
      if (logLevel.value === "all") {
        return logs.value;
      }
      return logs.value.filter((log) => log.level === logLevel.value);
    });
    const refreshStatus = () => {
      console.log("刷新状态");
    };
    const getProgressColor = (percentage) => {
      if (percentage >= 80) return "#f56c6c";
      if (percentage >= 60) return "#e6a23c";
      return "#67c23a";
    };
    const getLogLevelType = (level) => {
      const types = {
        error: "danger",
        warning: "warning",
        info: "info"
      };
      return types[level] || "info";
    };
    return (_ctx, _cache) => {
      const _component_el_icon = ElIcon;
      const _component_el_card = ElCard;
      const _component_el_col = ElCol;
      const _component_el_row = ElRow;
      const _component_el_button = ElButton;
      const _component_el_table_column = ElTableColumn;
      const _component_el_tag = ElTag;
      const _component_el_progress = ElProgress;
      const _component_el_table = ElTable;
      const _component_el_descriptions_item = ElDescriptionsItem;
      const _component_el_descriptions = ElDescriptions;
      const _component_el_option = ElOption;
      const _component_el_select = ElSelect;
      return openBlock(), createElementBlock("div", _hoisted_1, [
        createVNode(_component_el_row, { gutter: 20 }, {
          default: withCtx(() => [
            (openBlock(true), createElementBlock(Fragment, null, renderList(overviewData.value, (item) => {
              return openBlock(), createBlock(_component_el_col, {
                span: 6,
                key: item.label
              }, {
                default: withCtx(() => [
                  createVNode(_component_el_card, {
                    shadow: "hover",
                    class: "overview-card"
                  }, {
                    default: withCtx(() => [
                      createBaseVNode("div", _hoisted_2, [
                        createVNode(_component_el_icon, {
                          class: normalizeClass(["overview-icon", item.iconClass])
                        }, {
                          default: withCtx(() => [
                            (openBlock(), createBlock(resolveDynamicComponent(item.icon)))
                          ]),
                          _: 2
                        }, 1032, ["class"]),
                        createBaseVNode("div", _hoisted_3, [
                          createBaseVNode("div", _hoisted_4, toDisplayString(item.label), 1),
                          createBaseVNode("div", _hoisted_5, toDisplayString(item.value), 1)
                        ])
                      ])
                    ]),
                    _: 2
                  }, 1024)
                ]),
                _: 2
              }, 1024);
            }), 128))
          ]),
          _: 1
        }),
        createVNode(_component_el_card, {
          shadow: "never",
          style: { "margin-top": "20px" }
        }, {
          header: withCtx(() => [
            createBaseVNode("div", _hoisted_6, [
              _cache[2] || (_cache[2] = createBaseVNode("span", null, "服务状态", -1)),
              createVNode(_component_el_button, {
                size: "small",
                icon: unref(refresh_default),
                onClick: refreshStatus
              }, {
                default: withCtx(() => [..._cache[1] || (_cache[1] = [
                  createTextVNode("刷新", -1)
                ])]),
                _: 1
              }, 8, ["icon"])
            ])
          ]),
          default: withCtx(() => [
            createVNode(_component_el_table, {
              data: services.value,
              border: ""
            }, {
              default: withCtx(() => [
                createVNode(_component_el_table_column, {
                  prop: "name",
                  label: "服务名称",
                  "min-width": "150"
                }),
                createVNode(_component_el_table_column, {
                  prop: "status",
                  label: "状态",
                  width: "100"
                }, {
                  default: withCtx(({ row }) => [
                    createVNode(_component_el_tag, {
                      type: row.status === "running" ? "success" : "danger"
                    }, {
                      default: withCtx(() => [
                        createTextVNode(toDisplayString(row.status === "running" ? "运行中" : "已停止"), 1)
                      ]),
                      _: 2
                    }, 1032, ["type"])
                  ]),
                  _: 1
                }),
                createVNode(_component_el_table_column, {
                  prop: "uptime",
                  label: "运行时长",
                  width: "150"
                }),
                createVNode(_component_el_table_column, {
                  prop: "cpu",
                  label: "CPU使用率",
                  width: "120"
                }, {
                  default: withCtx(({ row }) => [
                    createVNode(_component_el_progress, {
                      percentage: row.cpu,
                      color: getProgressColor(row.cpu)
                    }, null, 8, ["percentage", "color"])
                  ]),
                  _: 1
                }),
                createVNode(_component_el_table_column, {
                  prop: "memory",
                  label: "内存使用率",
                  width: "120"
                }, {
                  default: withCtx(({ row }) => [
                    createVNode(_component_el_progress, {
                      percentage: row.memory,
                      color: getProgressColor(row.memory)
                    }, null, 8, ["percentage", "color"])
                  ]),
                  _: 1
                }),
                createVNode(_component_el_table_column, {
                  prop: "requests",
                  label: "请求数/分钟",
                  width: "130"
                }),
                createVNode(_component_el_table_column, {
                  prop: "avgResponseTime",
                  label: "平均响应时间",
                  width: "130"
                })
              ]),
              _: 1
            }, 8, ["data"])
          ]),
          _: 1
        }),
        createVNode(_component_el_card, {
          shadow: "never",
          style: { "margin-top": "20px" }
        }, {
          header: withCtx(() => [..._cache[3] || (_cache[3] = [
            createBaseVNode("span", null, "数据库状态", -1)
          ])]),
          default: withCtx(() => [
            createVNode(_component_el_descriptions, {
              column: 3,
              border: ""
            }, {
              default: withCtx(() => [
                createVNode(_component_el_descriptions_item, { label: "数据库类型" }, {
                  default: withCtx(() => [
                    createTextVNode(toDisplayString(dbInfo.value.type), 1)
                  ]),
                  _: 1
                }),
                createVNode(_component_el_descriptions_item, { label: "版本" }, {
                  default: withCtx(() => [
                    createTextVNode(toDisplayString(dbInfo.value.version), 1)
                  ]),
                  _: 1
                }),
                createVNode(_component_el_descriptions_item, { label: "连接状态" }, {
                  default: withCtx(() => [
                    createVNode(_component_el_tag, {
                      type: dbInfo.value.connected ? "success" : "danger"
                    }, {
                      default: withCtx(() => [
                        createTextVNode(toDisplayString(dbInfo.value.connected ? "已连接" : "未连接"), 1)
                      ]),
                      _: 1
                    }, 8, ["type"])
                  ]),
                  _: 1
                }),
                createVNode(_component_el_descriptions_item, { label: "活动连接数" }, {
                  default: withCtx(() => [
                    createTextVNode(toDisplayString(dbInfo.value.activeConnections), 1)
                  ]),
                  _: 1
                }),
                createVNode(_component_el_descriptions_item, { label: "空闲连接数" }, {
                  default: withCtx(() => [
                    createTextVNode(toDisplayString(dbInfo.value.idleConnections), 1)
                  ]),
                  _: 1
                }),
                createVNode(_component_el_descriptions_item, { label: "最大连接数" }, {
                  default: withCtx(() => [
                    createTextVNode(toDisplayString(dbInfo.value.maxConnections), 1)
                  ]),
                  _: 1
                }),
                createVNode(_component_el_descriptions_item, { label: "数据库大小" }, {
                  default: withCtx(() => [
                    createTextVNode(toDisplayString(dbInfo.value.size), 1)
                  ]),
                  _: 1
                }),
                createVNode(_component_el_descriptions_item, { label: "表数量" }, {
                  default: withCtx(() => [
                    createTextVNode(toDisplayString(dbInfo.value.tables), 1)
                  ]),
                  _: 1
                }),
                createVNode(_component_el_descriptions_item, { label: "慢查询数" }, {
                  default: withCtx(() => [
                    createTextVNode(toDisplayString(dbInfo.value.slowQueries), 1)
                  ]),
                  _: 1
                })
              ]),
              _: 1
            })
          ]),
          _: 1
        }),
        createVNode(_component_el_row, {
          gutter: 20,
          style: { "margin-top": "20px" }
        }, {
          default: withCtx(() => [
            createVNode(_component_el_col, { span: 12 }, {
              default: withCtx(() => [
                createVNode(_component_el_card, { shadow: "never" }, {
                  header: withCtx(() => [..._cache[4] || (_cache[4] = [
                    createBaseVNode("span", null, "磁盘使用情况", -1)
                  ])]),
                  default: withCtx(() => [
                    createBaseVNode("div", _hoisted_7, [
                      createVNode(_component_el_progress, {
                        type: "circle",
                        percentage: diskUsage.value.percentage,
                        width: 150,
                        color: getProgressColor(diskUsage.value.percentage)
                      }, {
                        default: withCtx(() => [
                          createBaseVNode("span", _hoisted_8, toDisplayString(diskUsage.value.percentage) + "%", 1)
                        ]),
                        _: 1
                      }, 8, ["percentage", "color"]),
                      createBaseVNode("div", _hoisted_9, [
                        createBaseVNode("div", null, "已使用: " + toDisplayString(diskUsage.value.used), 1),
                        createBaseVNode("div", null, "总容量: " + toDisplayString(diskUsage.value.total), 1)
                      ])
                    ])
                  ]),
                  _: 1
                })
              ]),
              _: 1
            }),
            createVNode(_component_el_col, { span: 12 }, {
              default: withCtx(() => [
                createVNode(_component_el_card, { shadow: "never" }, {
                  header: withCtx(() => [..._cache[5] || (_cache[5] = [
                    createBaseVNode("span", null, "缓存状态", -1)
                  ])]),
                  default: withCtx(() => [
                    createVNode(_component_el_descriptions, {
                      column: 1,
                      border: ""
                    }, {
                      default: withCtx(() => [
                        createVNode(_component_el_descriptions_item, { label: "缓存类型" }, {
                          default: withCtx(() => [..._cache[6] || (_cache[6] = [
                            createTextVNode("Redis", -1)
                          ])]),
                          _: 1
                        }),
                        createVNode(_component_el_descriptions_item, { label: "连接状态" }, {
                          default: withCtx(() => [
                            createVNode(_component_el_tag, { type: "success" }, {
                              default: withCtx(() => [..._cache[7] || (_cache[7] = [
                                createTextVNode("已连接", -1)
                              ])]),
                              _: 1
                            })
                          ]),
                          _: 1
                        }),
                        createVNode(_component_el_descriptions_item, { label: "使用内存" }, {
                          default: withCtx(() => [..._cache[8] || (_cache[8] = [
                            createTextVNode("256 MB", -1)
                          ])]),
                          _: 1
                        }),
                        createVNode(_component_el_descriptions_item, { label: "键数量" }, {
                          default: withCtx(() => [..._cache[9] || (_cache[9] = [
                            createTextVNode("1,234", -1)
                          ])]),
                          _: 1
                        }),
                        createVNode(_component_el_descriptions_item, { label: "命中率" }, {
                          default: withCtx(() => [..._cache[10] || (_cache[10] = [
                            createTextVNode("98.5%", -1)
                          ])]),
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
        createVNode(_component_el_card, {
          shadow: "never",
          style: { "margin-top": "20px" }
        }, {
          header: withCtx(() => [
            createBaseVNode("div", _hoisted_10, [
              _cache[11] || (_cache[11] = createBaseVNode("span", null, "最近日志", -1)),
              createVNode(_component_el_select, {
                modelValue: logLevel.value,
                "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => logLevel.value = $event),
                size: "small",
                style: { "width": "120px" }
              }, {
                default: withCtx(() => [
                  createVNode(_component_el_option, {
                    label: "全部",
                    value: "all"
                  }),
                  createVNode(_component_el_option, {
                    label: "错误",
                    value: "error"
                  }),
                  createVNode(_component_el_option, {
                    label: "警告",
                    value: "warning"
                  }),
                  createVNode(_component_el_option, {
                    label: "信息",
                    value: "info"
                  })
                ]),
                _: 1
              }, 8, ["modelValue"])
            ])
          ]),
          default: withCtx(() => [
            createVNode(_component_el_table, {
              data: filteredLogs.value,
              "max-height": "400"
            }, {
              default: withCtx(() => [
                createVNode(_component_el_table_column, {
                  prop: "time",
                  label: "时间",
                  width: "180"
                }),
                createVNode(_component_el_table_column, {
                  prop: "level",
                  label: "级别",
                  width: "100"
                }, {
                  default: withCtx(({ row }) => [
                    createVNode(_component_el_tag, {
                      type: getLogLevelType(row.level),
                      size: "small"
                    }, {
                      default: withCtx(() => [
                        createTextVNode(toDisplayString(row.level), 1)
                      ]),
                      _: 2
                    }, 1032, ["type"])
                  ]),
                  _: 1
                }),
                createVNode(_component_el_table_column, {
                  prop: "module",
                  label: "模块",
                  width: "150"
                }),
                createVNode(_component_el_table_column, {
                  prop: "message",
                  label: "消息",
                  "min-width": "300"
                })
              ]),
              _: 1
            }, 8, ["data"])
          ]),
          _: 1
        })
      ]);
    };
  }
});
const Status = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-2645e107"]]);
export {
  Status as default
};
