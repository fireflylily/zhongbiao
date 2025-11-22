import { d as defineComponent, M as useRouter, r as ref, c as computed, S as onMounted, e as createElementBlock, o as openBlock, n as createBaseVNode, f as createVNode, w as withCtx, ad as ElIcon, h as unref, bf as user_default, t as toDisplayString, as as ElCard, aO as circle_check_default, bn as trophy_base_default, k as createBlock, q as ElForm, s as ElFormItem, y as ElInput, aZ as search_default, Y as ElSelect, W as ElOption, g as ElButton, p as createTextVNode, b8 as refresh_left_default, al as ElTable, am as ElTableColumn, X as ElTag, bd as plus_default, aF as upload_default, a6 as ElDivider, ak as ElRow, ai as ElCol, v as ElRadioGroup, x as ElRadio, aA as ElInputNumber, j as ElDialog, m as ElAlert, at as ElUpload, aR as upload_filled_default } from "./vendor-MtO928VE.js";
import { L as Loading } from "./Loading-75jVWA4c.js";
import { E as Empty } from "./Empty-B61dCWeQ.js";
/* empty css                                                                           */
import { C as Card } from "./Card-jLaN2c6R.js";
/* empty css                                                                         */
import { a as useNotification, _ as _export_sfc } from "./index.js";
import { k as knowledgeApi, f as formatDate } from "./formatters-DrGE7noj.js";
import { v as validateEmail, a as validatePhone } from "./validators-CS_37Iha.js";
const _hoisted_1 = { class: "resume-library" };
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
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "ResumeLibrary",
  setup(__props) {
    const router = useRouter();
    const { success, error } = useNotification();
    const loading = ref(false);
    const allResumes = ref([]);
    const filters = ref({
      keyword: "",
      educationLevel: "",
      position: "",
      status: ""
    });
    const createDialogVisible = ref(false);
    const creating = ref(false);
    const createFormRef = ref();
    const createForm = ref({
      name: "",
      gender: "",
      phone: "",
      email: "",
      education_level: "",
      degree: "",
      university: "",
      major: "",
      current_position: "",
      professional_title: "",
      work_years: void 0,
      current_company: "",
      introduction: ""
    });
    const createFormRules = {
      name: [
        { required: true, message: "请输入姓名", trigger: "blur" },
        { min: 2, max: 50, message: "姓名长度在 2 到 50 个字符", trigger: "blur" }
      ],
      phone: [
        { validator: validatePhone, trigger: "blur" }
      ],
      email: [
        { validator: validateEmail, trigger: "blur" }
      ]
    };
    const uploadDialogVisible = ref(false);
    const parsing = ref(false);
    const uploadRef = ref();
    const uploadFileList = ref([]);
    const currentUploadFile = ref(null);
    const filteredResumes = computed(() => {
      let result = [...allResumes.value];
      if (filters.value.keyword) {
        const keyword = filters.value.keyword.toLowerCase();
        result = result.filter((r) => {
          var _a, _b, _c, _d;
          return ((_a = r.name) == null ? void 0 : _a.toLowerCase().includes(keyword)) || ((_b = r.current_position) == null ? void 0 : _b.toLowerCase().includes(keyword)) || ((_c = r.skills) == null ? void 0 : _c.toLowerCase().includes(keyword)) || ((_d = r.major) == null ? void 0 : _d.toLowerCase().includes(keyword));
        });
      }
      if (filters.value.educationLevel) {
        result = result.filter((r) => r.education_level === filters.value.educationLevel);
      }
      if (filters.value.position) {
        const position = filters.value.position.toLowerCase();
        result = result.filter((r) => {
          var _a;
          return (_a = r.current_position) == null ? void 0 : _a.toLowerCase().includes(position);
        });
      }
      if (filters.value.status) {
        result = result.filter((r) => r.status === filters.value.status);
      }
      return result;
    });
    const activeResumesCount = computed(() => {
      return allResumes.value.filter((r) => r.status === "active").length;
    });
    const averageWorkYears = computed(() => {
      const resumes = allResumes.value.filter((r) => r.work_years && r.work_years > 0);
      if (resumes.length === 0) return 0;
      const total = resumes.reduce((sum, r) => sum + (r.work_years || 0), 0);
      return (total / resumes.length).toFixed(1);
    });
    const loadResumes = async () => {
      loading.value = true;
      try {
        const response = await knowledgeApi.getResumes();
        if (response.success && response.data) {
          const resumeList = response.data.resumes || response.data;
          allResumes.value = resumeList.map((r) => ({
            ...r,
            created_at: r.created_at ? formatDate(r.created_at) : "-",
            updated_at: r.updated_at ? formatDate(r.updated_at) : "-"
          }));
        }
      } catch (err) {
        console.error("加载简历列表失败:", err);
        error("加载失败", err instanceof Error ? err.message : "未知错误");
      } finally {
        loading.value = false;
      }
    };
    const handleSearch = () => {
    };
    const handleResetFilters = () => {
      filters.value.keyword = "";
      filters.value.educationLevel = "";
      filters.value.position = "";
      filters.value.status = "";
    };
    const getEducationTagType = (education) => {
      if (!education) return "info";
      if (education === "博士") return "danger";
      if (education === "硕士") return "warning";
      if (education === "本科") return "success";
      return "info";
    };
    const getStatusTagType = (status) => {
      switch (status) {
        case "active":
          return "success";
        case "inactive":
          return "warning";
        case "archived":
          return "info";
        default:
          return "info";
      }
    };
    const getStatusLabel = (status) => {
      switch (status) {
        case "active":
          return "活跃";
        case "inactive":
          return "离职";
        case "archived":
          return "已归档";
        default:
          return "-";
      }
    };
    const handleCreate = () => {
      createDialogVisible.value = true;
    };
    const handleConfirmCreate = async () => {
      if (!createFormRef.value) return;
      await createFormRef.value.validate(async (valid) => {
        if (!valid) return;
        creating.value = true;
        try {
          const response = await knowledgeApi.createResume({
            name: createForm.value.name,
            gender: createForm.value.gender || void 0,
            phone: createForm.value.phone || void 0,
            email: createForm.value.email || void 0,
            education_level: createForm.value.education_level || void 0,
            degree: createForm.value.degree || void 0,
            university: createForm.value.university || void 0,
            major: createForm.value.major || void 0,
            current_position: createForm.value.current_position || void 0,
            professional_title: createForm.value.professional_title || void 0,
            work_years: createForm.value.work_years,
            current_company: createForm.value.current_company || void 0,
            introduction: createForm.value.introduction || void 0,
            status: "active"
          });
          if (response.success) {
            success("创建成功", "简历创建成功");
            createDialogVisible.value = false;
            await loadResumes();
          } else {
            error("创建失败", response.error || "未知错误");
          }
        } catch (err) {
          console.error("创建简历失败:", err);
          error("创建失败", err instanceof Error ? err.message : "未知错误");
        } finally {
          creating.value = false;
        }
      });
    };
    const handleUploadResume = () => {
      uploadDialogVisible.value = true;
    };
    const handleFileChange = (uploadFile) => {
      console.log("文件变化:", uploadFile);
      if (uploadFile.raw) {
        const maxSize = 10 * 1024 * 1024;
        if (uploadFile.raw.size > maxSize) {
          error("文件过大", "文件大小不能超过10MB");
          uploadFileList.value = [];
          currentUploadFile.value = null;
          return;
        }
        currentUploadFile.value = uploadFile.raw;
      }
    };
    const handleFileRemove = () => {
      currentUploadFile.value = null;
    };
    const handleConfirmUpload = async () => {
      if (!currentUploadFile.value) {
        error("请选择文件", "请先选择要上传的简历文件");
        return;
      }
      parsing.value = true;
      try {
        const response = await knowledgeApi.parseResumeFile(currentUploadFile.value, true);
        if (response.success) {
          success("导入成功", "简历已自动解析并创建");
          uploadDialogVisible.value = false;
          await loadResumes();
        } else {
          error("导入失败", response.error || "解析失败");
        }
      } catch (err) {
        console.error("智能导入失败:", err);
        error("导入失败", err instanceof Error ? err.message : "未知错误");
      } finally {
        parsing.value = false;
      }
    };
    const handleUploadDialogClose = () => {
      uploadFileList.value = [];
      currentUploadFile.value = null;
    };
    const handleDialogClose = () => {
      var _a;
      createForm.value = {
        name: "",
        gender: "",
        phone: "",
        email: "",
        education_level: "",
        degree: "",
        university: "",
        major: "",
        current_position: "",
        professional_title: "",
        work_years: void 0,
        current_company: "",
        introduction: ""
      };
      (_a = createFormRef.value) == null ? void 0 : _a.resetFields();
    };
    const handleView = (row) => {
      router.push(`/knowledge/resume/${row.resume_id}`);
    };
    const handleEdit = (row) => {
      router.push(`/knowledge/resume/${row.resume_id}`);
    };
    const handleDelete = async (row) => {
      try {
        if (!confirm(`确定要删除简历 "${row.name}" 吗？此操作不可恢复。`)) {
          return;
        }
        const response = await knowledgeApi.deleteResume(row.resume_id);
        if (response.success) {
          success("删除成功", `已删除简历: ${row.name}`);
          await loadResumes();
        } else {
          error("删除失败", response.error || "未知错误");
        }
      } catch (err) {
        console.error("删除简历失败:", err);
        error("删除失败", err instanceof Error ? err.message : "未知错误");
      }
    };
    onMounted(() => {
      loadResumes();
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
      const _component_el_divider = ElDivider;
      const _component_el_col = ElCol;
      const _component_el_radio = ElRadio;
      const _component_el_radio_group = ElRadioGroup;
      const _component_el_row = ElRow;
      const _component_el_input_number = ElInputNumber;
      const _component_el_dialog = ElDialog;
      const _component_el_alert = ElAlert;
      const _component_el_upload = ElUpload;
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
                      createVNode(unref(user_default))
                    ]),
                    _: 1
                  })
                ]),
                createBaseVNode("div", _hoisted_5, [
                  _cache[22] || (_cache[22] = createBaseVNode("div", { class: "stat-label" }, "总简历数", -1)),
                  createBaseVNode("div", _hoisted_6, toDisplayString(allResumes.value.length), 1)
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
                      createVNode(unref(circle_check_default))
                    ]),
                    _: 1
                  })
                ]),
                createBaseVNode("div", _hoisted_9, [
                  _cache[23] || (_cache[23] = createBaseVNode("div", { class: "stat-label" }, "活跃简历", -1)),
                  createBaseVNode("div", _hoisted_10, toDisplayString(activeResumesCount.value), 1)
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
                      createVNode(unref(trophy_base_default))
                    ]),
                    _: 1
                  })
                ]),
                createBaseVNode("div", _hoisted_13, [
                  _cache[24] || (_cache[24] = createBaseVNode("div", { class: "stat-label" }, "平均工龄", -1)),
                  createBaseVNode("div", _hoisted_14, toDisplayString(averageWorkYears.value) + "年", 1)
                ])
              ])
            ]),
            _: 1
          })
        ]),
        createVNode(unref(Card), { title: "简历列表" }, {
          actions: withCtx(() => [
            createVNode(_component_el_button, {
              type: "primary",
              onClick: handleCreate
            }, {
              default: withCtx(() => [
                createVNode(_component_el_icon, null, {
                  default: withCtx(() => [
                    createVNode(unref(plus_default))
                  ]),
                  _: 1
                }),
                _cache[25] || (_cache[25] = createTextVNode(" 新建简历 ", -1))
              ]),
              _: 1
            }),
            createVNode(_component_el_button, {
              type: "success",
              onClick: handleUploadResume
            }, {
              default: withCtx(() => [
                createVNode(_component_el_icon, null, {
                  default: withCtx(() => [
                    createVNode(unref(upload_default))
                  ]),
                  _: 1
                }),
                _cache[26] || (_cache[26] = createTextVNode(" 智能导入 ", -1))
              ]),
              _: 1
            })
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
                        placeholder: "搜索姓名、职位、技能...",
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
                  createVNode(_component_el_form_item, { label: "学历" }, {
                    default: withCtx(() => [
                      createVNode(_component_el_select, {
                        modelValue: filters.value.educationLevel,
                        "onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => filters.value.educationLevel = $event),
                        placeholder: "全部学历",
                        clearable: "",
                        style: { "width": "120px" },
                        onChange: handleSearch
                      }, {
                        default: withCtx(() => [
                          createVNode(_component_el_option, {
                            label: "全部学历",
                            value: ""
                          }),
                          createVNode(_component_el_option, {
                            label: "博士",
                            value: "博士"
                          }),
                          createVNode(_component_el_option, {
                            label: "硕士",
                            value: "硕士"
                          }),
                          createVNode(_component_el_option, {
                            label: "本科",
                            value: "本科"
                          }),
                          createVNode(_component_el_option, {
                            label: "大专",
                            value: "大专"
                          }),
                          createVNode(_component_el_option, {
                            label: "高中",
                            value: "高中"
                          })
                        ]),
                        _: 1
                      }, 8, ["modelValue"])
                    ]),
                    _: 1
                  }),
                  createVNode(_component_el_form_item, { label: "职位" }, {
                    default: withCtx(() => [
                      createVNode(_component_el_input, {
                        modelValue: filters.value.position,
                        "onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => filters.value.position = $event),
                        placeholder: "职位关键词",
                        clearable: "",
                        style: { "width": "150px" },
                        onInput: handleSearch
                      }, null, 8, ["modelValue"])
                    ]),
                    _: 1
                  }),
                  createVNode(_component_el_form_item, { label: "状态" }, {
                    default: withCtx(() => [
                      createVNode(_component_el_select, {
                        modelValue: filters.value.status,
                        "onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => filters.value.status = $event),
                        placeholder: "全部状态",
                        clearable: "",
                        style: { "width": "120px" },
                        onChange: handleSearch
                      }, {
                        default: withCtx(() => [
                          createVNode(_component_el_option, {
                            label: "全部状态",
                            value: ""
                          }),
                          createVNode(_component_el_option, {
                            label: "活跃",
                            value: "active"
                          }),
                          createVNode(_component_el_option, {
                            label: "离职",
                            value: "inactive"
                          }),
                          createVNode(_component_el_option, {
                            label: "已归档",
                            value: "archived"
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
                          _cache[27] || (_cache[27] = createTextVNode(" 重置 ", -1))
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
            })) : !filteredResumes.value.length ? (openBlock(), createBlock(unref(Empty), {
              key: 1,
              type: "no-data",
              description: "暂无简历数据"
            })) : (openBlock(), createBlock(_component_el_table, {
              key: 2,
              data: filteredResumes.value,
              stripe: "",
              style: { "width": "100%" }
            }, {
              default: withCtx(() => [
                createVNode(_component_el_table_column, {
                  prop: "resume_id",
                  label: "ID",
                  width: "70",
                  fixed: ""
                }),
                createVNode(_component_el_table_column, {
                  prop: "name",
                  label: "姓名",
                  width: "100",
                  fixed: ""
                }),
                createVNode(_component_el_table_column, {
                  prop: "gender",
                  label: "性别",
                  width: "60",
                  align: "center"
                }, {
                  default: withCtx(({ row }) => [
                    createTextVNode(toDisplayString(row.gender || "-"), 1)
                  ]),
                  _: 1
                }),
                createVNode(_component_el_table_column, {
                  prop: "education_level",
                  label: "学历",
                  width: "80"
                }, {
                  default: withCtx(({ row }) => [
                    createVNode(_component_el_tag, {
                      type: getEducationTagType(row.education_level),
                      size: "small"
                    }, {
                      default: withCtx(() => [
                        createTextVNode(toDisplayString(row.education_level || "-"), 1)
                      ]),
                      _: 2
                    }, 1032, ["type"])
                  ]),
                  _: 1
                }),
                createVNode(_component_el_table_column, {
                  prop: "university",
                  label: "毕业院校",
                  width: "140",
                  "show-overflow-tooltip": ""
                }),
                createVNode(_component_el_table_column, {
                  prop: "major",
                  label: "专业",
                  width: "120",
                  "show-overflow-tooltip": ""
                }),
                createVNode(_component_el_table_column, {
                  prop: "current_position",
                  label: "当前职位",
                  width: "140",
                  "show-overflow-tooltip": ""
                }),
                createVNode(_component_el_table_column, {
                  prop: "professional_title",
                  label: "职称",
                  width: "100"
                }),
                createVNode(_component_el_table_column, {
                  prop: "work_years",
                  label: "工作年限",
                  width: "90",
                  align: "center"
                }, {
                  default: withCtx(({ row }) => [
                    createTextVNode(toDisplayString(row.work_years ? `${row.work_years}年` : "-"), 1)
                  ]),
                  _: 1
                }),
                createVNode(_component_el_table_column, {
                  prop: "current_company",
                  label: "当前单位",
                  width: "160",
                  "show-overflow-tooltip": ""
                }),
                createVNode(_component_el_table_column, {
                  prop: "phone",
                  label: "联系电话",
                  width: "120"
                }),
                createVNode(_component_el_table_column, {
                  prop: "email",
                  label: "邮箱",
                  width: "180",
                  "show-overflow-tooltip": ""
                }),
                createVNode(_component_el_table_column, {
                  prop: "status",
                  label: "状态",
                  width: "80",
                  align: "center"
                }, {
                  default: withCtx(({ row }) => [
                    createVNode(_component_el_tag, {
                      type: getStatusTagType(row.status),
                      size: "small"
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
                      default: withCtx(() => [..._cache[28] || (_cache[28] = [
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
                      default: withCtx(() => [..._cache[29] || (_cache[29] = [
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
                      default: withCtx(() => [..._cache[30] || (_cache[30] = [
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
          "onUpdate:modelValue": _cache[18] || (_cache[18] = ($event) => createDialogVisible.value = $event),
          title: "新建简历",
          width: "700px",
          onClose: handleDialogClose
        }, {
          footer: withCtx(() => [
            createVNode(_component_el_button, {
              onClick: _cache[17] || (_cache[17] = ($event) => createDialogVisible.value = false)
            }, {
              default: withCtx(() => [..._cache[36] || (_cache[36] = [
                createTextVNode("取消", -1)
              ])]),
              _: 1
            }),
            createVNode(_component_el_button, {
              type: "primary",
              loading: creating.value,
              onClick: handleConfirmCreate
            }, {
              default: withCtx(() => [..._cache[37] || (_cache[37] = [
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
                createVNode(_component_el_divider, { "content-position": "left" }, {
                  default: withCtx(() => [..._cache[31] || (_cache[31] = [
                    createTextVNode("基本信息", -1)
                  ])]),
                  _: 1
                }),
                createVNode(_component_el_row, { gutter: 20 }, {
                  default: withCtx(() => [
                    createVNode(_component_el_col, { span: 12 }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, {
                          label: "姓名",
                          prop: "name"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: createForm.value.name,
                              "onUpdate:modelValue": _cache[4] || (_cache[4] = ($event) => createForm.value.name = $event),
                              placeholder: "请输入姓名"
                            }, null, 8, ["modelValue"])
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    createVNode(_component_el_col, { span: 12 }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, {
                          label: "性别",
                          prop: "gender"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_radio_group, {
                              modelValue: createForm.value.gender,
                              "onUpdate:modelValue": _cache[5] || (_cache[5] = ($event) => createForm.value.gender = $event)
                            }, {
                              default: withCtx(() => [
                                createVNode(_component_el_radio, { label: "男" }, {
                                  default: withCtx(() => [..._cache[32] || (_cache[32] = [
                                    createTextVNode("男", -1)
                                  ])]),
                                  _: 1
                                }),
                                createVNode(_component_el_radio, { label: "女" }, {
                                  default: withCtx(() => [..._cache[33] || (_cache[33] = [
                                    createTextVNode("女", -1)
                                  ])]),
                                  _: 1
                                })
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
                }),
                createVNode(_component_el_row, { gutter: 20 }, {
                  default: withCtx(() => [
                    createVNode(_component_el_col, { span: 12 }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, {
                          label: "联系电话",
                          prop: "phone"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: createForm.value.phone,
                              "onUpdate:modelValue": _cache[6] || (_cache[6] = ($event) => createForm.value.phone = $event),
                              placeholder: "请输入手机号"
                            }, null, 8, ["modelValue"])
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    createVNode(_component_el_col, { span: 12 }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, {
                          label: "邮箱",
                          prop: "email"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: createForm.value.email,
                              "onUpdate:modelValue": _cache[7] || (_cache[7] = ($event) => createForm.value.email = $event),
                              placeholder: "请输入邮箱"
                            }, null, 8, ["modelValue"])
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                }),
                createVNode(_component_el_divider, { "content-position": "left" }, {
                  default: withCtx(() => [..._cache[34] || (_cache[34] = [
                    createTextVNode("教育信息", -1)
                  ])]),
                  _: 1
                }),
                createVNode(_component_el_row, { gutter: 20 }, {
                  default: withCtx(() => [
                    createVNode(_component_el_col, { span: 12 }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, {
                          label: "学历",
                          prop: "education_level"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_select, {
                              modelValue: createForm.value.education_level,
                              "onUpdate:modelValue": _cache[8] || (_cache[8] = ($event) => createForm.value.education_level = $event),
                              placeholder: "请选择学历",
                              style: { "width": "100%" }
                            }, {
                              default: withCtx(() => [
                                createVNode(_component_el_option, {
                                  label: "博士",
                                  value: "博士"
                                }),
                                createVNode(_component_el_option, {
                                  label: "硕士",
                                  value: "硕士"
                                }),
                                createVNode(_component_el_option, {
                                  label: "本科",
                                  value: "本科"
                                }),
                                createVNode(_component_el_option, {
                                  label: "大专",
                                  value: "大专"
                                }),
                                createVNode(_component_el_option, {
                                  label: "高中",
                                  value: "高中"
                                }),
                                createVNode(_component_el_option, {
                                  label: "中专",
                                  value: "中专"
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
                        })
                      ]),
                      _: 1
                    }),
                    createVNode(_component_el_col, { span: 12 }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, {
                          label: "学位",
                          prop: "degree"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_select, {
                              modelValue: createForm.value.degree,
                              "onUpdate:modelValue": _cache[9] || (_cache[9] = ($event) => createForm.value.degree = $event),
                              placeholder: "请选择学位",
                              style: { "width": "100%" }
                            }, {
                              default: withCtx(() => [
                                createVNode(_component_el_option, {
                                  label: "博士学位",
                                  value: "博士"
                                }),
                                createVNode(_component_el_option, {
                                  label: "硕士学位",
                                  value: "硕士"
                                }),
                                createVNode(_component_el_option, {
                                  label: "学士学位",
                                  value: "学士"
                                }),
                                createVNode(_component_el_option, {
                                  label: "无学位",
                                  value: "无"
                                })
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
                }),
                createVNode(_component_el_row, { gutter: 20 }, {
                  default: withCtx(() => [
                    createVNode(_component_el_col, { span: 12 }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, {
                          label: "毕业院校",
                          prop: "university"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: createForm.value.university,
                              "onUpdate:modelValue": _cache[10] || (_cache[10] = ($event) => createForm.value.university = $event),
                              placeholder: "请输入毕业院校"
                            }, null, 8, ["modelValue"])
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    createVNode(_component_el_col, { span: 12 }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, {
                          label: "专业",
                          prop: "major"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: createForm.value.major,
                              "onUpdate:modelValue": _cache[11] || (_cache[11] = ($event) => createForm.value.major = $event),
                              placeholder: "请输入专业"
                            }, null, 8, ["modelValue"])
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                }),
                createVNode(_component_el_divider, { "content-position": "left" }, {
                  default: withCtx(() => [..._cache[35] || (_cache[35] = [
                    createTextVNode("工作信息", -1)
                  ])]),
                  _: 1
                }),
                createVNode(_component_el_row, { gutter: 20 }, {
                  default: withCtx(() => [
                    createVNode(_component_el_col, { span: 12 }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, {
                          label: "当前职位",
                          prop: "current_position"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: createForm.value.current_position,
                              "onUpdate:modelValue": _cache[12] || (_cache[12] = ($event) => createForm.value.current_position = $event),
                              placeholder: "如：项目经理"
                            }, null, 8, ["modelValue"])
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    createVNode(_component_el_col, { span: 12 }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, {
                          label: "职称",
                          prop: "professional_title"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: createForm.value.professional_title,
                              "onUpdate:modelValue": _cache[13] || (_cache[13] = ($event) => createForm.value.professional_title = $event),
                              placeholder: "如：高级工程师"
                            }, null, 8, ["modelValue"])
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                }),
                createVNode(_component_el_row, { gutter: 20 }, {
                  default: withCtx(() => [
                    createVNode(_component_el_col, { span: 12 }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, {
                          label: "工作年限",
                          prop: "work_years"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input_number, {
                              modelValue: createForm.value.work_years,
                              "onUpdate:modelValue": _cache[14] || (_cache[14] = ($event) => createForm.value.work_years = $event),
                              min: 0,
                              max: 50,
                              placeholder: "年",
                              style: { "width": "100%" }
                            }, null, 8, ["modelValue"])
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    createVNode(_component_el_col, { span: 12 }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, {
                          label: "当前单位",
                          prop: "current_company"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: createForm.value.current_company,
                              "onUpdate:modelValue": _cache[15] || (_cache[15] = ($event) => createForm.value.current_company = $event),
                              placeholder: "请输入当前工作单位"
                            }, null, 8, ["modelValue"])
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                }),
                createVNode(_component_el_form_item, {
                  label: "个人简介",
                  prop: "introduction"
                }, {
                  default: withCtx(() => [
                    createVNode(_component_el_input, {
                      modelValue: createForm.value.introduction,
                      "onUpdate:modelValue": _cache[16] || (_cache[16] = ($event) => createForm.value.introduction = $event),
                      type: "textarea",
                      rows: 3,
                      placeholder: "请简要介绍个人经历、专长等"
                    }, null, 8, ["modelValue"])
                  ]),
                  _: 1
                })
              ]),
              _: 1
            }, 8, ["model"])
          ]),
          _: 1
        }, 8, ["modelValue"]),
        createVNode(_component_el_dialog, {
          modelValue: uploadDialogVisible.value,
          "onUpdate:modelValue": _cache[21] || (_cache[21] = ($event) => uploadDialogVisible.value = $event),
          title: "智能导入简历",
          width: "500px",
          onClose: handleUploadDialogClose
        }, {
          footer: withCtx(() => [
            createVNode(_component_el_button, {
              onClick: _cache[20] || (_cache[20] = ($event) => uploadDialogVisible.value = false)
            }, {
              default: withCtx(() => [..._cache[40] || (_cache[40] = [
                createTextVNode("取消", -1)
              ])]),
              _: 1
            }),
            createVNode(_component_el_button, {
              type: "primary",
              loading: parsing.value,
              onClick: handleConfirmUpload
            }, {
              default: withCtx(() => [..._cache[41] || (_cache[41] = [
                createTextVNode(" 开始解析 ", -1)
              ])]),
              _: 1
            }, 8, ["loading"])
          ]),
          default: withCtx(() => [
            createVNode(_component_el_alert, {
              title: "智能解析",
              type: "info",
              description: "上传PDF/DOC/DOCX格式的简历文件，系统将自动提取信息并创建简历记录",
              closable: false,
              style: { "margin-bottom": "20px" }
            }),
            createVNode(_component_el_upload, {
              ref_key: "uploadRef",
              ref: uploadRef,
              "file-list": uploadFileList.value,
              "onUpdate:fileList": _cache[19] || (_cache[19] = ($event) => uploadFileList.value = $event),
              "auto-upload": false,
              limit: 1,
              accept: ".pdf,.doc,.docx",
              drag: "",
              "on-change": handleFileChange,
              "on-remove": handleFileRemove
            }, {
              tip: withCtx(() => [..._cache[38] || (_cache[38] = [
                createBaseVNode("div", { class: "el-upload__tip" }, " 支持PDF、DOC、DOCX格式，文件大小不超过10MB ", -1)
              ])]),
              default: withCtx(() => [
                createVNode(_component_el_icon, { class: "el-icon--upload" }, {
                  default: withCtx(() => [
                    createVNode(unref(upload_filled_default))
                  ]),
                  _: 1
                }),
                _cache[39] || (_cache[39] = createBaseVNode("div", { class: "el-upload__text" }, [
                  createTextVNode(" 拖拽文件到这里 或 "),
                  createBaseVNode("em", null, "点击上传")
                ], -1))
              ]),
              _: 1
            }, 8, ["file-list"])
          ]),
          _: 1
        }, 8, ["modelValue"])
      ]);
    };
  }
});
const ResumeLibrary = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-d80ddb3a"]]);
export {
  ResumeLibrary as default
};
