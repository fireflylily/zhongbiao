import { d as defineComponent, M as useRouter, r as ref, S as onMounted, e as createElementBlock, o as openBlock, f as createVNode, w as withCtx, ai as ElCol, h as unref, aj as ElStatistic, n as createBaseVNode, ak as ElRow, F as Fragment, V as renderList, ac as normalizeStyle, U as normalizeClass, t as toDisplayString, k as createBlock, g as ElButton, p as createTextVNode, al as ElTable, am as ElTableColumn, Q as ElLink, X as ElTag, an as ElPagination, ao as dayjs } from "./vendor-MtO928VE.js";
import { u as useProjectStore } from "./project-X4Kuz_iO.js";
import { a as useNotification, _ as _export_sfc } from "./index.js";
import { t as tenderApi } from "./tender-DvsgeLWX.js";
import { L as Loading } from "./Loading-75jVWA4c.js";
import { E as Empty } from "./Empty-B61dCWeQ.js";
/* empty css                                                                           */
import { C as Card } from "./Card-jLaN2c6R.js";
import { I as IconButton } from "./IconButton-CDqBOgvk.js";
/* empty css                                                                         */
const _hoisted_1 = { class: "dashboard-page" };
const _hoisted_2 = { class: "quick-actions" };
const _hoisted_3 = ["onClick"];
const _hoisted_4 = { class: "action-label" };
const _hoisted_5 = { class: "pagination-wrapper" };
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "Dashboard",
  setup(__props) {
    const router = useRouter();
    const projectStore = useProjectStore();
    const { success, error: showError, confirm } = useNotification();
    const loadingStats = ref(false);
    const loadingProjects = ref(false);
    const statistics = ref({
      totalProjects: 0,
      inProgressProjects: 0,
      wonThisMonth: 0,
      pendingTasks: 0
    });
    const projects = ref([]);
    const currentPage = ref(1);
    const pageSize = ref(10);
    const total = ref(0);
    const quickActions = [
      {
        name: "start-tender",
        label: "开始投标",
        icon: "bi bi-play-circle-fill",
        color: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        route: "/tender-management"
      },
      {
        name: "business-response",
        label: "商务应答",
        icon: "bi bi-briefcase-fill",
        color: "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
        route: "/business-response"
      },
      {
        name: "point-to-point",
        label: "点对点应答",
        icon: "bi bi-arrow-left-right",
        color: "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
        route: "/point-to-point"
      },
      {
        name: "tech-proposal",
        label: "技术方案",
        icon: "bi bi-file-code-fill",
        color: "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)",
        route: "/tech-proposal"
      },
      {
        name: "tender-scoring",
        label: "标书评分",
        icon: "bi bi-star-fill",
        color: "linear-gradient(135deg, #fa709a 0%, #fee140 100%)",
        route: "/tender-scoring"
      },
      {
        name: "knowledge",
        label: "知识中心",
        icon: "bi bi-book-fill",
        color: "linear-gradient(135deg, #30cfd0 0%, #330867 100%)",
        route: "/knowledge/company-library"
      }
    ];
    async function loadStatistics() {
      loadingStats.value = true;
      try {
        const response = await tenderApi.getDashboardStatistics();
        if (response.success && response.data) {
          statistics.value = {
            totalProjects: response.data.totalProjects,
            inProgressProjects: response.data.inProgressProjects,
            wonThisMonth: response.data.wonThisMonth,
            pendingTasks: response.data.pendingTasks
          };
        }
      } catch (err) {
        showError("加载统计数据失败: " + err.message);
      } finally {
        loadingStats.value = false;
      }
    }
    async function loadProjects() {
      loadingProjects.value = true;
      try {
        const response = await tenderApi.getProjects({
          page: currentPage.value,
          page_size: pageSize.value
        });
        if (response.success && response.data) {
          if (Array.isArray(response.data)) {
            projects.value = response.data;
            total.value = response.data.length;
          } else if (response.data.items) {
            projects.value = response.data.items;
            total.value = response.data.total || 0;
          }
        }
      } catch (err) {
        showError("加载项目列表失败: " + err.message);
      } finally {
        loadingProjects.value = false;
      }
    }
    async function refreshProjects() {
      await loadProjects();
      success("刷新成功");
    }
    function handleQuickAction(action) {
      router.push(action.route);
    }
    function handleCreateProject() {
      router.push("/tender-management");
    }
    function handleViewProject(project) {
      projectStore.setCurrentProject(project);
      router.push({
        name: "TenderManagementDetail",
        params: { id: project.id }
      });
    }
    function handleContinueProject(project) {
      projectStore.setCurrentProject(project);
      router.push({
        name: "TenderManagementDetail",
        params: { id: project.id }
      });
    }
    async function handleArchiveProject(project) {
      const confirmed = await confirm(
        `确定要归档项目"${project.project_name}"吗?`,
        "归档项目",
        "归档后项目将不再显示在进行中列表"
      );
      if (confirmed) {
        try {
          await projectStore.updateProject(project.id, { status: "archived" });
          success("项目已归档");
          await loadProjects();
        } catch (err) {
          showError("归档失败: " + err.message);
        }
      }
    }
    function handleSizeChange(size) {
      pageSize.value = size;
      currentPage.value = 1;
      loadProjects();
    }
    function handlePageChange(page) {
      currentPage.value = page;
      loadProjects();
    }
    function getStatusType(status) {
      const typeMap = {
        pending: "info",
        in_progress: "warning",
        completed: "success",
        won: "success",
        lost: "danger",
        archived: "info"
      };
      return typeMap[status] || "info";
    }
    function getStatusLabel(status) {
      const labelMap = {
        pending: "待处理",
        in_progress: "进行中",
        completed: "已完成",
        won: "已中标",
        lost: "未中标",
        archived: "已归档"
      };
      return labelMap[status] || status;
    }
    function formatDate(date) {
      if (!date) return "-";
      return dayjs(date).format("YYYY-MM-DD HH:mm");
    }
    onMounted(() => {
      loadStatistics();
      loadProjects();
    });
    return (_ctx, _cache) => {
      const _component_el_statistic = ElStatistic;
      const _component_el_col = ElCol;
      const _component_el_row = ElRow;
      const _component_el_button = ElButton;
      const _component_el_link = ElLink;
      const _component_el_table_column = ElTableColumn;
      const _component_el_tag = ElTag;
      const _component_el_table = ElTable;
      const _component_el_pagination = ElPagination;
      return openBlock(), createElementBlock("div", _hoisted_1, [
        createVNode(_component_el_row, {
          gutter: 16,
          class: "kpi-cards"
        }, {
          default: withCtx(() => [
            createVNode(_component_el_col, {
              xs: 12,
              sm: 12,
              md: 6,
              lg: 6
            }, {
              default: withCtx(() => [
                createVNode(unref(Card), {
                  shadow: "hover",
                  loading: loadingStats.value
                }, {
                  default: withCtx(() => [
                    createVNode(_component_el_statistic, {
                      title: "总项目数",
                      value: statistics.value.totalProjects
                    }, {
                      prefix: withCtx(() => [..._cache[2] || (_cache[2] = [
                        createBaseVNode("i", {
                          class: "bi bi-folder-fill statistic-icon",
                          style: { "color": "#409eff" }
                        }, null, -1)
                      ])]),
                      _: 1
                    }, 8, ["value"])
                  ]),
                  _: 1
                }, 8, ["loading"])
              ]),
              _: 1
            }),
            createVNode(_component_el_col, {
              xs: 12,
              sm: 12,
              md: 6,
              lg: 6
            }, {
              default: withCtx(() => [
                createVNode(unref(Card), {
                  shadow: "hover",
                  loading: loadingStats.value
                }, {
                  default: withCtx(() => [
                    createVNode(_component_el_statistic, {
                      title: "进行中项目",
                      value: statistics.value.inProgressProjects
                    }, {
                      prefix: withCtx(() => [..._cache[3] || (_cache[3] = [
                        createBaseVNode("i", {
                          class: "bi bi-clock-fill statistic-icon",
                          style: { "color": "#e6a23c" }
                        }, null, -1)
                      ])]),
                      _: 1
                    }, 8, ["value"])
                  ]),
                  _: 1
                }, 8, ["loading"])
              ]),
              _: 1
            }),
            createVNode(_component_el_col, {
              xs: 12,
              sm: 12,
              md: 6,
              lg: 6
            }, {
              default: withCtx(() => [
                createVNode(unref(Card), {
                  shadow: "hover",
                  loading: loadingStats.value
                }, {
                  default: withCtx(() => [
                    createVNode(_component_el_statistic, {
                      title: "本月中标",
                      value: statistics.value.wonThisMonth
                    }, {
                      prefix: withCtx(() => [..._cache[4] || (_cache[4] = [
                        createBaseVNode("i", {
                          class: "bi bi-trophy-fill statistic-icon",
                          style: { "color": "#67c23a" }
                        }, null, -1)
                      ])]),
                      _: 1
                    }, 8, ["value"])
                  ]),
                  _: 1
                }, 8, ["loading"])
              ]),
              _: 1
            }),
            createVNode(_component_el_col, {
              xs: 12,
              sm: 12,
              md: 6,
              lg: 6
            }, {
              default: withCtx(() => [
                createVNode(unref(Card), {
                  shadow: "hover",
                  loading: loadingStats.value
                }, {
                  default: withCtx(() => [
                    createVNode(_component_el_statistic, {
                      title: "待处理任务",
                      value: statistics.value.pendingTasks
                    }, {
                      prefix: withCtx(() => [..._cache[5] || (_cache[5] = [
                        createBaseVNode("i", {
                          class: "bi bi-list-task statistic-icon",
                          style: { "color": "#f56c6c" }
                        }, null, -1)
                      ])]),
                      _: 1
                    }, 8, ["value"])
                  ]),
                  _: 1
                }, 8, ["loading"])
              ]),
              _: 1
            })
          ]),
          _: 1
        }),
        createVNode(unref(Card), {
          title: "快捷入口",
          class: "quick-actions-card"
        }, {
          default: withCtx(() => [
            createBaseVNode("div", _hoisted_2, [
              (openBlock(), createElementBlock(Fragment, null, renderList(quickActions, (action) => {
                return createBaseVNode("div", {
                  key: action.name,
                  class: "action-item",
                  onClick: ($event) => handleQuickAction(action)
                }, [
                  createBaseVNode("div", {
                    class: "action-icon",
                    style: normalizeStyle({ background: action.color })
                  }, [
                    createBaseVNode("i", {
                      class: normalizeClass(action.icon)
                    }, null, 2)
                  ], 4),
                  createBaseVNode("div", _hoisted_4, toDisplayString(action.label), 1)
                ], 8, _hoisted_3);
              }), 64))
            ])
          ]),
          _: 1
        }),
        createVNode(unref(Card), {
          title: "进行中的项目",
          class: "projects-card"
        }, {
          actions: withCtx(() => [
            createVNode(unref(IconButton), {
              icon: "bi-arrow-clockwise",
              tooltip: "刷新",
              onClick: refreshProjects
            })
          ]),
          default: withCtx(() => [
            loadingProjects.value ? (openBlock(), createBlock(unref(Loading), {
              key: 0,
              visible: true,
              fullscreen: false,
              text: "加载项目列表..."
            })) : projects.value.length === 0 ? (openBlock(), createBlock(unref(Empty), {
              key: 1,
              type: "no-data",
              description: "暂无进行中的项目"
            }, {
              action: withCtx(() => [
                createVNode(_component_el_button, {
                  type: "primary",
                  onClick: handleCreateProject
                }, {
                  default: withCtx(() => [..._cache[6] || (_cache[6] = [
                    createTextVNode("创建第一个项目", -1)
                  ])]),
                  _: 1
                })
              ]),
              _: 1
            })) : (openBlock(), createElementBlock(Fragment, { key: 2 }, [
              createVNode(_component_el_table, {
                data: projects.value,
                stripe: "",
                style: { "width": "100%" }
              }, {
                default: withCtx(() => [
                  createVNode(_component_el_table_column, {
                    prop: "project_name",
                    label: "项目名称",
                    "min-width": "200"
                  }, {
                    default: withCtx(({ row }) => [
                      createVNode(_component_el_link, {
                        type: "primary",
                        onClick: ($event) => handleViewProject(row)
                      }, {
                        default: withCtx(() => [
                          createTextVNode(toDisplayString(row.project_name), 1)
                        ]),
                        _: 2
                      }, 1032, ["onClick"])
                    ]),
                    _: 1
                  }),
                  createVNode(_component_el_table_column, {
                    prop: "project_number",
                    label: "项目编号",
                    width: "150"
                  }),
                  createVNode(_component_el_table_column, {
                    prop: "status",
                    label: "状态",
                    width: "120"
                  }, {
                    default: withCtx(({ row }) => [
                      createVNode(_component_el_tag, {
                        type: getStatusType(row.status)
                      }, {
                        default: withCtx(() => [
                          createTextVNode(toDisplayString(getStatusLabel(row.status)), 1)
                        ]),
                        _: 2
                      }, 1032, ["type"])
                    ]),
                    _: 1
                  }),
                  createVNode(_component_el_table_column, {
                    prop: "company_name",
                    label: "关联企业",
                    width: "200"
                  }),
                  createVNode(_component_el_table_column, {
                    prop: "created_at",
                    label: "创建时间",
                    width: "180"
                  }, {
                    default: withCtx(({ row }) => [
                      createTextVNode(toDisplayString(formatDate(row.created_at)), 1)
                    ]),
                    _: 1
                  }),
                  createVNode(_component_el_table_column, {
                    label: "操作",
                    width: "200",
                    fixed: "right"
                  }, {
                    default: withCtx(({ row }) => [
                      createVNode(unref(IconButton), {
                        icon: "bi-eye",
                        type: "primary",
                        tooltip: "查看详情",
                        onClick: ($event) => handleViewProject(row)
                      }, null, 8, ["onClick"]),
                      createVNode(unref(IconButton), {
                        icon: "bi-play-circle",
                        type: "success",
                        tooltip: "继续处理",
                        onClick: ($event) => handleContinueProject(row)
                      }, null, 8, ["onClick"]),
                      createVNode(unref(IconButton), {
                        icon: "bi-archive",
                        type: "warning",
                        tooltip: "归档",
                        onClick: ($event) => handleArchiveProject(row)
                      }, null, 8, ["onClick"])
                    ]),
                    _: 1
                  })
                ]),
                _: 1
              }, 8, ["data"]),
              createBaseVNode("div", _hoisted_5, [
                createVNode(_component_el_pagination, {
                  "current-page": currentPage.value,
                  "onUpdate:currentPage": _cache[0] || (_cache[0] = ($event) => currentPage.value = $event),
                  "page-size": pageSize.value,
                  "onUpdate:pageSize": _cache[1] || (_cache[1] = ($event) => pageSize.value = $event),
                  total: total.value,
                  "page-sizes": [10, 20, 50, 100],
                  layout: "total, sizes, prev, pager, next, jumper",
                  onSizeChange: handleSizeChange,
                  onCurrentChange: handlePageChange
                }, null, 8, ["current-page", "page-size", "total"])
              ])
            ], 64))
          ]),
          _: 1
        })
      ]);
    };
  }
});
const Dashboard = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-6925dc07"]]);
export {
  Dashboard as default
};
