import { d as defineComponent, r as ref, M as useRouter, S as onMounted, e as createElementBlock, o as openBlock, f as createVNode, w as withCtx, k as createBlock, l as createCommentVNode, h as unref, al as ElTable, am as ElTableColumn, Q as ElLink, p as createTextVNode, t as toDisplayString, X as ElTag, n as createBaseVNode, an as ElPagination, g as ElButton, ao as dayjs } from "./vendor-MtO928VE.js";
import { L as Loading } from "./Loading-75jVWA4c.js";
import { E as Empty } from "./Empty-B61dCWeQ.js";
/* empty css                                                                           */
import { C as Card } from "./Card-jLaN2c6R.js";
import { I as IconButton } from "./IconButton-CDqBOgvk.js";
/* empty css                                                                         */
import { a as useNotification, _ as _export_sfc } from "./index.js";
import { t as tenderApi } from "./tender-DvsgeLWX.js";
import { c as companyApi } from "./company-z4Xg082l.js";
const _hoisted_1 = { class: "tender-management" };
const _hoisted_2 = {
  key: 3,
  class: "pagination-wrapper"
};
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "Management",
  setup(__props) {
    const loading = ref(false);
    const creating = ref(false);
    const projects = ref([]);
    const currentPage = ref(1);
    const pageSize = ref(10);
    const total = ref(0);
    const router = useRouter();
    const { success, error } = useNotification();
    const loadProjects = async () => {
      var _a, _b;
      loading.value = true;
      try {
        const response = await tenderApi.getProjects({
          page: currentPage.value,
          page_size: pageSize.value
        });
        const rawData = ((_a = response.data) == null ? void 0 : _a.items) || response.data || [];
        projects.value = rawData.map((project) => ({
          id: project.project_id,
          name: project.project_name,
          number: project.project_number,
          company_name: project.company_name,
          status: project.status,
          created_at: project.created_at,
          ...project
        }));
        total.value = ((_b = response.data) == null ? void 0 : _b.total) || projects.value.length;
      } catch (err) {
        console.error("加载项目列表失败:", err);
        error("加载失败", err instanceof Error ? err.message : "未知错误");
      } finally {
        loading.value = false;
      }
    };
    const hasBusinessResponse = (project) => {
      return project.business_response_file || project.business_response_status === "completed";
    };
    const hasPointToPoint = (project) => {
      return project.point_to_point_file || project.point_to_point_status === "completed";
    };
    const hasTechProposal = (project) => {
      return project.tech_proposal_file || project.tech_proposal_status === "completed" || !!project.technical_data;
    };
    const hasFinalMerge = (project) => {
      return project.final_merge_file || project.merge_status === "completed";
    };
    const handleView = (row) => {
      router.push({
        name: "TenderManagementDetail",
        params: { id: row.id }
      });
    };
    const handleDelete = async (row) => {
      try {
        if (!confirm(`确定要删除项目 "${row.name}" 吗？此操作将同时删除项目的所有文档，且不可恢复。`)) {
          return;
        }
        await tenderApi.deleteProject(row.id);
        success("删除成功", `已删除项目: ${row.name}`);
        await loadProjects();
      } catch (err) {
        console.error("删除项目失败:", err);
        error("删除失败", err instanceof Error ? err.message : "未知错误");
      }
    };
    const handleCreate = async () => {
      creating.value = true;
      try {
        const companiesResponse = await companyApi.getCompanies();
        const companies = companiesResponse.data || [];
        if (companies.length === 0) {
          error("无法创建项目：请先添加公司信息");
          return;
        }
        const response = await tenderApi.createProject({
          project_name: "新项目",
          project_number: `PRJ-${Date.now()}`,
          company_id: companies[0].company_id
        });
        const projectId = response.project_id;
        success("创建成功");
        router.push({
          name: "TenderManagementDetail",
          params: { id: projectId }
        });
      } catch (err) {
        console.error("创建项目失败:", err);
        const errorMessage = err instanceof Error ? err.message : "未知错误";
        error(`创建项目失败：${errorMessage}`);
      } finally {
        creating.value = false;
      }
    };
    const handleSizeChange = (size) => {
      pageSize.value = size;
      currentPage.value = 1;
      loadProjects();
    };
    const handlePageChange = (page) => {
      currentPage.value = page;
      loadProjects();
    };
    const formatDate = (date) => {
      if (!date) return "-";
      return dayjs(date).format("YYYY-MM-DD HH:mm");
    };
    onMounted(() => {
      loadProjects();
    });
    return (_ctx, _cache) => {
      const _component_el_button = ElButton;
      const _component_el_table_column = ElTableColumn;
      const _component_el_link = ElLink;
      const _component_el_tag = ElTag;
      const _component_el_table = ElTable;
      const _component_el_pagination = ElPagination;
      return openBlock(), createElementBlock("div", _hoisted_1, [
        createVNode(unref(Card), { title: "项目列表" }, {
          actions: withCtx(() => [
            createVNode(_component_el_button, {
              type: "primary",
              loading: creating.value,
              onClick: handleCreate
            }, {
              default: withCtx(() => [..._cache[2] || (_cache[2] = [
                createBaseVNode("i", { class: "bi bi-plus-lg" }, null, -1),
                createTextVNode(" 新建项目 ", -1)
              ])]),
              _: 1
            }, 8, ["loading"])
          ]),
          default: withCtx(() => [
            loading.value ? (openBlock(), createBlock(unref(Loading), {
              key: 0,
              text: "加载中..."
            })) : !projects.value.length ? (openBlock(), createBlock(unref(Empty), {
              key: 1,
              type: "no-data",
              description: "暂无项目"
            })) : (openBlock(), createBlock(_component_el_table, {
              key: 2,
              data: projects.value,
              stripe: "",
              style: { "width": "100%" }
            }, {
              default: withCtx(() => [
                createVNode(_component_el_table_column, {
                  prop: "id",
                  label: "ID",
                  width: "70",
                  fixed: ""
                }),
                createVNode(_component_el_table_column, {
                  prop: "name",
                  label: "项目名称",
                  "min-width": "200",
                  fixed: ""
                }, {
                  default: withCtx(({ row }) => [
                    createVNode(_component_el_link, {
                      type: "primary",
                      onClick: ($event) => handleView(row)
                    }, {
                      default: withCtx(() => [
                        createTextVNode(toDisplayString(row.name), 1)
                      ]),
                      _: 2
                    }, 1032, ["onClick"])
                  ]),
                  _: 1
                }),
                createVNode(_component_el_table_column, {
                  prop: "company_name",
                  label: "公司名称",
                  "min-width": "180",
                  "show-overflow-tooltip": ""
                }),
                createVNode(_component_el_table_column, {
                  prop: "authorized_person_name",
                  label: "被授权人",
                  width: "100"
                }),
                createVNode(_component_el_table_column, {
                  label: "商务应答",
                  width: "100",
                  align: "center"
                }, {
                  default: withCtx(({ row }) => [
                    hasBusinessResponse(row) ? (openBlock(), createBlock(_component_el_tag, {
                      key: 0,
                      type: "success",
                      size: "small"
                    }, {
                      default: withCtx(() => [..._cache[3] || (_cache[3] = [
                        createBaseVNode("i", { class: "bi bi-check-circle-fill" }, null, -1),
                        createTextVNode(" 已生成 ", -1)
                      ])]),
                      _: 1
                    })) : (openBlock(), createBlock(_component_el_tag, {
                      key: 1,
                      type: "info",
                      size: "small"
                    }, {
                      default: withCtx(() => [..._cache[4] || (_cache[4] = [
                        createBaseVNode("i", { class: "bi bi-dash-circle" }, null, -1),
                        createTextVNode(" 未生成 ", -1)
                      ])]),
                      _: 1
                    }))
                  ]),
                  _: 1
                }),
                createVNode(_component_el_table_column, {
                  label: "技术点对点",
                  width: "110",
                  align: "center"
                }, {
                  default: withCtx(({ row }) => [
                    hasPointToPoint(row) ? (openBlock(), createBlock(_component_el_tag, {
                      key: 0,
                      type: "success",
                      size: "small"
                    }, {
                      default: withCtx(() => [..._cache[5] || (_cache[5] = [
                        createBaseVNode("i", { class: "bi bi-check-circle-fill" }, null, -1),
                        createTextVNode(" 已生成 ", -1)
                      ])]),
                      _: 1
                    })) : (openBlock(), createBlock(_component_el_tag, {
                      key: 1,
                      type: "info",
                      size: "small"
                    }, {
                      default: withCtx(() => [..._cache[6] || (_cache[6] = [
                        createBaseVNode("i", { class: "bi bi-dash-circle" }, null, -1),
                        createTextVNode(" 未生成 ", -1)
                      ])]),
                      _: 1
                    }))
                  ]),
                  _: 1
                }),
                createVNode(_component_el_table_column, {
                  label: "技术方案",
                  width: "100",
                  align: "center"
                }, {
                  default: withCtx(({ row }) => [
                    hasTechProposal(row) ? (openBlock(), createBlock(_component_el_tag, {
                      key: 0,
                      type: "success",
                      size: "small"
                    }, {
                      default: withCtx(() => [..._cache[7] || (_cache[7] = [
                        createBaseVNode("i", { class: "bi bi-check-circle-fill" }, null, -1),
                        createTextVNode(" 已生成 ", -1)
                      ])]),
                      _: 1
                    })) : (openBlock(), createBlock(_component_el_tag, {
                      key: 1,
                      type: "info",
                      size: "small"
                    }, {
                      default: withCtx(() => [..._cache[8] || (_cache[8] = [
                        createBaseVNode("i", { class: "bi bi-dash-circle" }, null, -1),
                        createTextVNode(" 未生成 ", -1)
                      ])]),
                      _: 1
                    }))
                  ]),
                  _: 1
                }),
                createVNode(_component_el_table_column, {
                  label: "最后融合",
                  width: "100",
                  align: "center"
                }, {
                  default: withCtx(({ row }) => [
                    hasFinalMerge(row) ? (openBlock(), createBlock(_component_el_tag, {
                      key: 0,
                      type: "success",
                      size: "small"
                    }, {
                      default: withCtx(() => [..._cache[9] || (_cache[9] = [
                        createBaseVNode("i", { class: "bi bi-check-circle-fill" }, null, -1),
                        createTextVNode(" 已融合 ", -1)
                      ])]),
                      _: 1
                    })) : (openBlock(), createBlock(_component_el_tag, {
                      key: 1,
                      type: "info",
                      size: "small"
                    }, {
                      default: withCtx(() => [..._cache[10] || (_cache[10] = [
                        createBaseVNode("i", { class: "bi bi-dash-circle" }, null, -1),
                        createTextVNode(" 未融合 ", -1)
                      ])]),
                      _: 1
                    }))
                  ]),
                  _: 1
                }),
                createVNode(_component_el_table_column, {
                  prop: "status",
                  label: "项目状态",
                  width: "100",
                  align: "center"
                }, {
                  default: withCtx(({ row }) => [
                    row.status === "active" ? (openBlock(), createBlock(_component_el_tag, {
                      key: 0,
                      type: "success"
                    }, {
                      default: withCtx(() => [..._cache[11] || (_cache[11] = [
                        createTextVNode("进行中", -1)
                      ])]),
                      _: 1
                    })) : row.status === "completed" ? (openBlock(), createBlock(_component_el_tag, {
                      key: 1,
                      type: "primary"
                    }, {
                      default: withCtx(() => [..._cache[12] || (_cache[12] = [
                        createTextVNode("已完成", -1)
                      ])]),
                      _: 1
                    })) : (openBlock(), createBlock(_component_el_tag, {
                      key: 2,
                      type: "info"
                    }, {
                      default: withCtx(() => [..._cache[13] || (_cache[13] = [
                        createTextVNode("草稿", -1)
                      ])]),
                      _: 1
                    }))
                  ]),
                  _: 1
                }),
                createVNode(_component_el_table_column, {
                  prop: "created_at",
                  label: "创建时间",
                  width: "160"
                }, {
                  default: withCtx(({ row }) => [
                    createTextVNode(toDisplayString(formatDate(row.created_at)), 1)
                  ]),
                  _: 1
                }),
                createVNode(_component_el_table_column, {
                  label: "操作",
                  width: "120",
                  fixed: "right"
                }, {
                  default: withCtx(({ row }) => [
                    createVNode(unref(IconButton), {
                      icon: "bi-eye",
                      type: "primary",
                      tooltip: "查看详情",
                      onClick: ($event) => handleView(row)
                    }, null, 8, ["onClick"]),
                    createVNode(unref(IconButton), {
                      icon: "bi-trash",
                      type: "danger",
                      tooltip: "删除项目",
                      onClick: ($event) => handleDelete(row)
                    }, null, 8, ["onClick"])
                  ]),
                  _: 1
                })
              ]),
              _: 1
            }, 8, ["data"])),
            projects.value.length > 0 ? (openBlock(), createElementBlock("div", _hoisted_2, [
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
            ])) : createCommentVNode("", true)
          ]),
          _: 1
        })
      ]);
    };
  }
});
const Management = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-aca97e9b"]]);
export {
  Management as default
};
