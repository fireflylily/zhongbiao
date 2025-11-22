import { d as defineComponent, r as ref, D as watch, e as createElementBlock, o as openBlock, f as createVNode, as as ElCard, w as withCtx, q as ElForm, ak as ElRow, ai as ElCol, s as ElFormItem, y as ElInput, v as ElRadioGroup, x as ElRadio, p as createTextVNode, b9 as ElDatePicker, Y as ElSelect, W as ElOption, g as ElButton, n as createBaseVNode, aA as ElInputNumber, S as onMounted, k as createBlock, h as unref, F as Fragment, V as renderList, ad as ElIcon, aF as upload_default, j as ElDialog, at as ElUpload, aR as upload_filled_default, ah as resolveDynamicComponent, X as ElTag, t as toDisplayString, l as createCommentVNode, aE as download_default, bc as delete_default, bb as files_default, bn as trophy_base_default, bi as medal_default, bh as tickets_default, bo as postcard_default, ae as document_default, u as useRoute, M as useRouter, ax as ElTabPane, bf as user_default, bp as reading_default, bq as briefcase_default, b3 as folder_default, aw as ElTabs } from "./vendor-MtO928VE.js";
import { L as Loading } from "./Loading-D6Ei-uTU.js";
/* empty css                                                                           */
/* empty css                                                                         */
import { a as useNotification, _ as _export_sfc } from "./index.js";
import { k as knowledgeApi, a as formatFileSize, f as formatDate } from "./formatters-DrGE7noj.js";
import { b as validateIdCard, v as validateEmail, a as validatePhone } from "./validators-CS_37Iha.js";
import { E as Empty } from "./Empty-CMm3i0ir.js";
import { s as smartCompressImage } from "./imageCompressor-DC3BCfPz.js";
const _hoisted_1$4 = { class: "resume-basic-info-tab" };
const _sfc_main$4 = /* @__PURE__ */ defineComponent({
  __name: "ResumeBasicInfoTab",
  props: {
    resumeId: {},
    resumeData: {}
  },
  emits: ["update"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const { success, error } = useNotification();
    const formRef = ref();
    const saving = ref(false);
    const formData = ref({
      name: "",
      gender: "",
      birth_date: "",
      nationality: "",
      native_place: "",
      political_status: "",
      id_number: "",
      phone: "",
      email: "",
      address: "",
      introduction: ""
    });
    const formRules = {
      name: [
        { required: true, message: "请输入姓名", trigger: "blur" }
      ],
      phone: [
        { validator: validatePhone, trigger: "blur" }
      ],
      email: [
        { validator: validateEmail, trigger: "blur" }
      ],
      id_number: [
        { validator: validateIdCard, trigger: "blur" }
      ]
    };
    watch(
      () => props.resumeData,
      (newData) => {
        if (newData) {
          formData.value = {
            name: newData.name || "",
            gender: newData.gender || "",
            birth_date: newData.birth_date || "",
            nationality: newData.nationality || "",
            native_place: newData.native_place || "",
            political_status: newData.political_status || "",
            id_number: newData.id_number || "",
            phone: newData.phone || "",
            email: newData.email || "",
            address: newData.address || "",
            introduction: newData.introduction || ""
          };
        }
      },
      { immediate: true, deep: true }
    );
    const handleSave = async () => {
      if (!formRef.value) return;
      await formRef.value.validate(async (valid) => {
        if (!valid) return;
        saving.value = true;
        try {
          const response = await knowledgeApi.updateResume(props.resumeId, formData.value);
          if (response.success) {
            success("保存成功", "基本信息已更新");
            emit("update");
          } else {
            error("保存失败", response.error || "未知错误");
          }
        } catch (err) {
          console.error("保存基本信息失败:", err);
          error("保存失败", err instanceof Error ? err.message : "未知错误");
        } finally {
          saving.value = false;
        }
      });
    };
    const handleReset = () => {
      var _a;
      (_a = formRef.value) == null ? void 0 : _a.resetFields();
    };
    return (_ctx, _cache) => {
      const _component_el_input = ElInput;
      const _component_el_form_item = ElFormItem;
      const _component_el_col = ElCol;
      const _component_el_radio = ElRadio;
      const _component_el_radio_group = ElRadioGroup;
      const _component_el_date_picker = ElDatePicker;
      const _component_el_row = ElRow;
      const _component_el_option = ElOption;
      const _component_el_select = ElSelect;
      const _component_el_button = ElButton;
      const _component_el_form = ElForm;
      const _component_el_card = ElCard;
      return openBlock(), createElementBlock("div", _hoisted_1$4, [
        createVNode(_component_el_card, null, {
          header: withCtx(() => [..._cache[11] || (_cache[11] = [
            createBaseVNode("span", null, "基本信息", -1)
          ])]),
          default: withCtx(() => [
            createVNode(_component_el_form, {
              ref_key: "formRef",
              ref: formRef,
              model: formData.value,
              rules: formRules,
              "label-width": "120px"
            }, {
              default: withCtx(() => [
                createVNode(_component_el_row, { gutter: 20 }, {
                  default: withCtx(() => [
                    createVNode(_component_el_col, { span: 8 }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, {
                          label: "姓名",
                          prop: "name"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: formData.value.name,
                              "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => formData.value.name = $event),
                              placeholder: "请输入姓名"
                            }, null, 8, ["modelValue"])
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    createVNode(_component_el_col, { span: 8 }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, {
                          label: "性别",
                          prop: "gender"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_radio_group, {
                              modelValue: formData.value.gender,
                              "onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => formData.value.gender = $event)
                            }, {
                              default: withCtx(() => [
                                createVNode(_component_el_radio, { label: "男" }, {
                                  default: withCtx(() => [..._cache[12] || (_cache[12] = [
                                    createTextVNode("男", -1)
                                  ])]),
                                  _: 1
                                }),
                                createVNode(_component_el_radio, { label: "女" }, {
                                  default: withCtx(() => [..._cache[13] || (_cache[13] = [
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
                    }),
                    createVNode(_component_el_col, { span: 8 }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, {
                          label: "出生日期",
                          prop: "birth_date"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_date_picker, {
                              modelValue: formData.value.birth_date,
                              "onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => formData.value.birth_date = $event),
                              type: "date",
                              placeholder: "选择日期",
                              "value-format": "YYYY-MM-DD",
                              style: { "width": "100%" }
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
                    createVNode(_component_el_col, { span: 8 }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, {
                          label: "民族",
                          prop: "nationality"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: formData.value.nationality,
                              "onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => formData.value.nationality = $event),
                              placeholder: "如：汉族"
                            }, null, 8, ["modelValue"])
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    createVNode(_component_el_col, { span: 8 }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, {
                          label: "籍贯",
                          prop: "native_place"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: formData.value.native_place,
                              "onUpdate:modelValue": _cache[4] || (_cache[4] = ($event) => formData.value.native_place = $event),
                              placeholder: "如：北京市"
                            }, null, 8, ["modelValue"])
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    createVNode(_component_el_col, { span: 8 }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, {
                          label: "政治面貌",
                          prop: "political_status"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_select, {
                              modelValue: formData.value.political_status,
                              "onUpdate:modelValue": _cache[5] || (_cache[5] = ($event) => formData.value.political_status = $event),
                              placeholder: "请选择",
                              style: { "width": "100%" }
                            }, {
                              default: withCtx(() => [
                                createVNode(_component_el_option, {
                                  label: "中共党员",
                                  value: "中共党员"
                                }),
                                createVNode(_component_el_option, {
                                  label: "共青团员",
                                  value: "共青团员"
                                }),
                                createVNode(_component_el_option, {
                                  label: "民主党派",
                                  value: "民主党派"
                                }),
                                createVNode(_component_el_option, {
                                  label: "群众",
                                  value: "群众"
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
                          label: "身份证号",
                          prop: "id_number"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: formData.value.id_number,
                              "onUpdate:modelValue": _cache[6] || (_cache[6] = ($event) => formData.value.id_number = $event),
                              placeholder: "18位身份证号",
                              maxlength: "18"
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
                          label: "联系电话",
                          prop: "phone"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: formData.value.phone,
                              "onUpdate:modelValue": _cache[7] || (_cache[7] = ($event) => formData.value.phone = $event),
                              placeholder: "手机号码",
                              maxlength: "11"
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
                          label: "电子邮箱",
                          prop: "email"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: formData.value.email,
                              "onUpdate:modelValue": _cache[8] || (_cache[8] = ($event) => formData.value.email = $event),
                              placeholder: "邮箱地址"
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
                          label: "联系地址",
                          prop: "address"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: formData.value.address,
                              "onUpdate:modelValue": _cache[9] || (_cache[9] = ($event) => formData.value.address = $event),
                              placeholder: "详细地址"
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
                      modelValue: formData.value.introduction,
                      "onUpdate:modelValue": _cache[10] || (_cache[10] = ($event) => formData.value.introduction = $event),
                      type: "textarea",
                      rows: 4,
                      placeholder: "请简要介绍个人经历、专长、优势等"
                    }, null, 8, ["modelValue"])
                  ]),
                  _: 1
                }),
                createVNode(_component_el_form_item, null, {
                  default: withCtx(() => [
                    createVNode(_component_el_button, {
                      type: "primary",
                      loading: saving.value,
                      onClick: handleSave
                    }, {
                      default: withCtx(() => [..._cache[14] || (_cache[14] = [
                        createTextVNode(" 保存 ", -1)
                      ])]),
                      _: 1
                    }, 8, ["loading"]),
                    createVNode(_component_el_button, { onClick: handleReset }, {
                      default: withCtx(() => [..._cache[15] || (_cache[15] = [
                        createTextVNode("重置", -1)
                      ])]),
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
        })
      ]);
    };
  }
});
const ResumeBasicInfoTab = /* @__PURE__ */ _export_sfc(_sfc_main$4, [["__scopeId", "data-v-9eb5d3ea"]]);
const _hoisted_1$3 = { class: "resume-education-tab" };
const _sfc_main$3 = /* @__PURE__ */ defineComponent({
  __name: "ResumeEducationTab",
  props: {
    resumeId: {},
    resumeData: {}
  },
  emits: ["update"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const { success, error } = useNotification();
    const formRef = ref();
    const saving = ref(false);
    const formData = ref({
      education_level: "",
      degree: "",
      university: "",
      major: "",
      graduation_date: ""
    });
    watch(
      () => props.resumeData,
      (newData) => {
        if (newData) {
          formData.value = {
            education_level: newData.education_level || "",
            degree: newData.degree || "",
            university: newData.university || "",
            major: newData.major || "",
            graduation_date: newData.graduation_date || ""
          };
        }
      },
      { immediate: true, deep: true }
    );
    const handleSave = async () => {
      if (!formRef.value) return;
      saving.value = true;
      try {
        const response = await knowledgeApi.updateResume(props.resumeId, formData.value);
        if (response.success) {
          success("保存成功", "教育信息已更新");
          emit("update");
        } else {
          error("保存失败", response.error || "未知错误");
        }
      } catch (err) {
        console.error("保存教育信息失败:", err);
        error("保存失败", err instanceof Error ? err.message : "未知错误");
      } finally {
        saving.value = false;
      }
    };
    const handleReset = () => {
      var _a;
      (_a = formRef.value) == null ? void 0 : _a.resetFields();
    };
    return (_ctx, _cache) => {
      const _component_el_option = ElOption;
      const _component_el_select = ElSelect;
      const _component_el_form_item = ElFormItem;
      const _component_el_col = ElCol;
      const _component_el_row = ElRow;
      const _component_el_input = ElInput;
      const _component_el_date_picker = ElDatePicker;
      const _component_el_button = ElButton;
      const _component_el_form = ElForm;
      const _component_el_card = ElCard;
      return openBlock(), createElementBlock("div", _hoisted_1$3, [
        createVNode(_component_el_card, null, {
          header: withCtx(() => [..._cache[5] || (_cache[5] = [
            createBaseVNode("span", null, "教育信息", -1)
          ])]),
          default: withCtx(() => [
            createVNode(_component_el_form, {
              ref_key: "formRef",
              ref: formRef,
              model: formData.value,
              "label-width": "120px"
            }, {
              default: withCtx(() => [
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
                              modelValue: formData.value.education_level,
                              "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => formData.value.education_level = $event),
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
                              modelValue: formData.value.degree,
                              "onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => formData.value.degree = $event),
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
                              modelValue: formData.value.university,
                              "onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => formData.value.university = $event),
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
                              modelValue: formData.value.major,
                              "onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => formData.value.major = $event),
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
                createVNode(_component_el_row, { gutter: 20 }, {
                  default: withCtx(() => [
                    createVNode(_component_el_col, { span: 12 }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, {
                          label: "毕业时间",
                          prop: "graduation_date"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_date_picker, {
                              modelValue: formData.value.graduation_date,
                              "onUpdate:modelValue": _cache[4] || (_cache[4] = ($event) => formData.value.graduation_date = $event),
                              type: "date",
                              placeholder: "选择毕业日期",
                              "value-format": "YYYY-MM-DD",
                              style: { "width": "100%" }
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
                createVNode(_component_el_form_item, null, {
                  default: withCtx(() => [
                    createVNode(_component_el_button, {
                      type: "primary",
                      loading: saving.value,
                      onClick: handleSave
                    }, {
                      default: withCtx(() => [..._cache[6] || (_cache[6] = [
                        createTextVNode(" 保存 ", -1)
                      ])]),
                      _: 1
                    }, 8, ["loading"]),
                    createVNode(_component_el_button, { onClick: handleReset }, {
                      default: withCtx(() => [..._cache[7] || (_cache[7] = [
                        createTextVNode("重置", -1)
                      ])]),
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
        })
      ]);
    };
  }
});
const ResumeEducationTab = /* @__PURE__ */ _export_sfc(_sfc_main$3, [["__scopeId", "data-v-15f0e911"]]);
const _hoisted_1$2 = { class: "resume-work-tab" };
const _sfc_main$2 = /* @__PURE__ */ defineComponent({
  __name: "ResumeWorkTab",
  props: {
    resumeId: {},
    resumeData: {}
  },
  emits: ["update"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const { success, error } = useNotification();
    const formRef = ref();
    const saving = ref(false);
    const formData = ref({
      current_position: "",
      professional_title: "",
      work_years: void 0,
      current_company: "",
      department: "",
      work_location: "",
      skills: "",
      certificates: "",
      awards: ""
    });
    watch(
      () => props.resumeData,
      (newData) => {
        if (newData) {
          formData.value = {
            current_position: newData.current_position || "",
            professional_title: newData.professional_title || "",
            work_years: newData.work_years,
            current_company: newData.current_company || "",
            department: newData.department || "",
            work_location: newData.work_location || "",
            skills: newData.skills || "",
            certificates: newData.certificates || "",
            awards: newData.awards || ""
          };
        }
      },
      { immediate: true, deep: true }
    );
    const handleSave = async () => {
      if (!formRef.value) return;
      saving.value = true;
      try {
        const response = await knowledgeApi.updateResume(props.resumeId, formData.value);
        if (response.success) {
          success("保存成功", "工作信息已更新");
          emit("update");
        } else {
          error("保存失败", response.error || "未知错误");
        }
      } catch (err) {
        console.error("保存工作信息失败:", err);
        error("保存失败", err instanceof Error ? err.message : "未知错误");
      } finally {
        saving.value = false;
      }
    };
    const handleReset = () => {
      var _a;
      (_a = formRef.value) == null ? void 0 : _a.resetFields();
    };
    return (_ctx, _cache) => {
      const _component_el_input = ElInput;
      const _component_el_form_item = ElFormItem;
      const _component_el_col = ElCol;
      const _component_el_row = ElRow;
      const _component_el_input_number = ElInputNumber;
      const _component_el_button = ElButton;
      const _component_el_form = ElForm;
      const _component_el_card = ElCard;
      return openBlock(), createElementBlock("div", _hoisted_1$2, [
        createVNode(_component_el_card, null, {
          header: withCtx(() => [..._cache[9] || (_cache[9] = [
            createBaseVNode("span", null, "工作信息", -1)
          ])]),
          default: withCtx(() => [
            createVNode(_component_el_form, {
              ref_key: "formRef",
              ref: formRef,
              model: formData.value,
              "label-width": "120px"
            }, {
              default: withCtx(() => [
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
                              modelValue: formData.value.current_position,
                              "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => formData.value.current_position = $event),
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
                              modelValue: formData.value.professional_title,
                              "onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => formData.value.professional_title = $event),
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
                              modelValue: formData.value.work_years,
                              "onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => formData.value.work_years = $event),
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
                              modelValue: formData.value.current_company,
                              "onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => formData.value.current_company = $event),
                              placeholder: "当前工作单位"
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
                          label: "所在部门",
                          prop: "department"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: formData.value.department,
                              "onUpdate:modelValue": _cache[4] || (_cache[4] = ($event) => formData.value.department = $event),
                              placeholder: "部门名称"
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
                          label: "工作地点",
                          prop: "work_location"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: formData.value.work_location,
                              "onUpdate:modelValue": _cache[5] || (_cache[5] = ($event) => formData.value.work_location = $event),
                              placeholder: "工作城市"
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
                  label: "技能特长",
                  prop: "skills"
                }, {
                  default: withCtx(() => [
                    createVNode(_component_el_input, {
                      modelValue: formData.value.skills,
                      "onUpdate:modelValue": _cache[6] || (_cache[6] = ($event) => formData.value.skills = $event),
                      type: "textarea",
                      rows: 3,
                      placeholder: "请输入技能特长，多个技能用逗号分隔，如：项目管理,需求分析,Java开发"
                    }, null, 8, ["modelValue"])
                  ]),
                  _: 1
                }),
                createVNode(_component_el_form_item, {
                  label: "证书列表",
                  prop: "certificates"
                }, {
                  default: withCtx(() => [
                    createVNode(_component_el_input, {
                      modelValue: formData.value.certificates,
                      "onUpdate:modelValue": _cache[7] || (_cache[7] = ($event) => formData.value.certificates = $event),
                      type: "textarea",
                      rows: 2,
                      placeholder: "请输入证书名称，多个证书用逗号分隔，如：PMP,软考高级"
                    }, null, 8, ["modelValue"])
                  ]),
                  _: 1
                }),
                createVNode(_component_el_form_item, {
                  label: "获奖情况",
                  prop: "awards"
                }, {
                  default: withCtx(() => [
                    createVNode(_component_el_input, {
                      modelValue: formData.value.awards,
                      "onUpdate:modelValue": _cache[8] || (_cache[8] = ($event) => formData.value.awards = $event),
                      type: "textarea",
                      rows: 2,
                      placeholder: "请输入获奖情况"
                    }, null, 8, ["modelValue"])
                  ]),
                  _: 1
                }),
                createVNode(_component_el_form_item, null, {
                  default: withCtx(() => [
                    createVNode(_component_el_button, {
                      type: "primary",
                      loading: saving.value,
                      onClick: handleSave
                    }, {
                      default: withCtx(() => [..._cache[10] || (_cache[10] = [
                        createTextVNode(" 保存 ", -1)
                      ])]),
                      _: 1
                    }, 8, ["loading"]),
                    createVNode(_component_el_button, { onClick: handleReset }, {
                      default: withCtx(() => [..._cache[11] || (_cache[11] = [
                        createTextVNode("重置", -1)
                      ])]),
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
        })
      ]);
    };
  }
});
const ResumeWorkTab = /* @__PURE__ */ _export_sfc(_sfc_main$2, [["__scopeId", "data-v-00b6bb2c"]]);
const _hoisted_1$1 = { class: "resume-attachments-tab" };
const _hoisted_2$1 = { class: "card-header" };
const _hoisted_3$1 = {
  key: 2,
  class: "attachments-grid"
};
const _hoisted_4$1 = { class: "attachment-header" };
const _hoisted_5$1 = { class: "attachment-body" };
const _hoisted_6$1 = ["title"];
const _hoisted_7$1 = { class: "file-info" };
const _hoisted_8$1 = { class: "file-size" };
const _hoisted_9 = { class: "file-date" };
const _hoisted_10 = {
  key: 0,
  class: "file-desc"
};
const _hoisted_11 = { class: "attachment-actions" };
const _sfc_main$1 = /* @__PURE__ */ defineComponent({
  __name: "ResumeAttachmentsTab",
  props: {
    resumeId: {},
    resumeData: {}
  },
  emits: ["update"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const { success, error } = useNotification();
    const loading = ref(false);
    const attachments = ref([]);
    const uploadDialogVisible = ref(false);
    const uploading = ref(false);
    const uploadFormRef = ref();
    const uploadRef = ref();
    const uploadForm = ref({
      attachment_category: "resume",
      description: "",
      file: null
    });
    const uploadFormRules = {
      attachment_category: [
        { required: true, message: "请选择附件类型", trigger: "change" }
      ]
    };
    const getAttachmentIcon = (category) => {
      switch (category) {
        case "resume":
          return document_default;
        case "id_card":
          return postcard_default;
        case "education":
          return tickets_default;
        case "degree":
          return tickets_default;
        case "qualification":
          return medal_default;
        case "award":
          return trophy_base_default;
        default:
          return files_default;
      }
    };
    const getAttachmentColor = (category) => {
      switch (category) {
        case "resume":
          return "#409eff";
        case "id_card":
          return "#f56c6c";
        case "education":
          return "#67c23a";
        case "degree":
          return "#e6a23c";
        case "qualification":
          return "#909399";
        case "award":
          return "#ff9800";
        default:
          return "#909399";
      }
    };
    const getAttachmentTagType = (category) => {
      switch (category) {
        case "resume":
          return "primary";
        case "id_card":
          return "danger";
        case "education":
          return "success";
        case "degree":
          return "warning";
        case "qualification":
          return "info";
        case "award":
          return "warning";
        default:
          return "info";
      }
    };
    const getAttachmentLabel = (category) => {
      switch (category) {
        case "resume":
          return "简历文件";
        case "id_card":
          return "身份证";
        case "education":
          return "学历证书";
        case "degree":
          return "学位证书";
        case "qualification":
          return "资质证书";
        case "award":
          return "获奖证书";
        default:
          return "其他材料";
      }
    };
    const loadAttachments = async () => {
      loading.value = true;
      try {
        const response = await knowledgeApi.getResumeAttachments(props.resumeId);
        if (response.success && response.data) {
          attachments.value = response.data;
        }
      } catch (err) {
        console.error("加载附件列表失败:", err);
        error("加载失败", err instanceof Error ? err.message : "未知错误");
      } finally {
        loading.value = false;
      }
    };
    const handleFileChange = (uploadFile) => {
      if (uploadFile.raw) {
        uploadForm.value.file = uploadFile.raw;
      }
    };
    const handleUpload = () => {
      uploadDialogVisible.value = true;
    };
    const handleConfirmUpload = async () => {
      if (!uploadFormRef.value) return;
      await uploadFormRef.value.validate(async (valid) => {
        var _a;
        if (!valid) return;
        if (!uploadForm.value.file) {
          error("请选择文件", "请先选择要上传的文件");
          return;
        }
        uploading.value = true;
        try {
          let fileToUpload = uploadForm.value.file;
          if (fileToUpload.type.startsWith("image/")) {
            const imageType = uploadForm.value.attachment_category === "id_card" ? "id_card" : "photo";
            fileToUpload = await smartCompressImage(fileToUpload, imageType);
            console.log("[ResumeAttachments] 图片已压缩");
          }
          const response = await knowledgeApi.uploadResumeAttachment(
            props.resumeId,
            fileToUpload,
            uploadForm.value.attachment_category,
            uploadForm.value.description || void 0
          );
          if (response.success) {
            success("上传成功", "附件已上传");
            uploadDialogVisible.value = false;
            (_a = uploadRef.value) == null ? void 0 : _a.clearFiles();
            uploadForm.value = {
              attachment_category: "resume",
              description: "",
              file: null
            };
            await loadAttachments();
            emit("update");
          } else {
            error("上传失败", response.error || "未知错误");
          }
        } catch (err) {
          console.error("上传附件失败:", err);
          error("上传失败", err instanceof Error ? err.message : "未知错误");
        } finally {
          uploading.value = false;
        }
      });
    };
    const handleDownload = (attachment) => {
      const url = knowledgeApi.downloadResumeAttachment(attachment.attachment_id);
      window.open(url, "_blank");
    };
    const handleDelete = async (attachment) => {
      try {
        if (!confirm(`确定要删除附件 "${attachment.original_filename}" 吗？`)) {
          return;
        }
        const response = await knowledgeApi.deleteResumeAttachment(attachment.attachment_id);
        if (response.success) {
          success("删除成功", "附件已删除");
          await loadAttachments();
          emit("update");
        } else {
          error("删除失败", response.error || "未知错误");
        }
      } catch (err) {
        console.error("删除附件失败:", err);
        error("删除失败", err instanceof Error ? err.message : "未知错误");
      }
    };
    onMounted(() => {
      loadAttachments();
    });
    return (_ctx, _cache) => {
      const _component_el_icon = ElIcon;
      const _component_el_button = ElButton;
      const _component_el_tag = ElTag;
      const _component_el_card = ElCard;
      const _component_el_option = ElOption;
      const _component_el_select = ElSelect;
      const _component_el_form_item = ElFormItem;
      const _component_el_input = ElInput;
      const _component_el_upload = ElUpload;
      const _component_el_form = ElForm;
      const _component_el_dialog = ElDialog;
      return openBlock(), createElementBlock("div", _hoisted_1$1, [
        createVNode(_component_el_card, null, {
          header: withCtx(() => [
            createBaseVNode("div", _hoisted_2$1, [
              _cache[5] || (_cache[5] = createBaseVNode("span", null, "简历附件", -1)),
              createVNode(_component_el_button, {
                type: "primary",
                size: "small",
                onClick: handleUpload
              }, {
                default: withCtx(() => [
                  createVNode(_component_el_icon, null, {
                    default: withCtx(() => [
                      createVNode(unref(upload_default))
                    ]),
                    _: 1
                  }),
                  _cache[4] || (_cache[4] = createTextVNode(" 上传附件 ", -1))
                ]),
                _: 1
              })
            ])
          ]),
          default: withCtx(() => [
            loading.value ? (openBlock(), createBlock(unref(Loading), {
              key: 0,
              text: "加载附件中..."
            })) : !attachments.value.length ? (openBlock(), createBlock(unref(Empty), {
              key: 1,
              type: "no-data",
              description: "暂无附件"
            })) : (openBlock(), createElementBlock("div", _hoisted_3$1, [
              (openBlock(true), createElementBlock(Fragment, null, renderList(attachments.value, (attachment) => {
                return openBlock(), createElementBlock("div", {
                  key: attachment.attachment_id,
                  class: "attachment-card"
                }, [
                  createBaseVNode("div", _hoisted_4$1, [
                    createVNode(_component_el_icon, {
                      size: 32,
                      color: getAttachmentColor(attachment.attachment_category)
                    }, {
                      default: withCtx(() => [
                        (openBlock(), createBlock(resolveDynamicComponent(getAttachmentIcon(attachment.attachment_category))))
                      ]),
                      _: 2
                    }, 1032, ["color"]),
                    createVNode(_component_el_tag, {
                      type: getAttachmentTagType(attachment.attachment_category),
                      size: "small"
                    }, {
                      default: withCtx(() => [
                        createTextVNode(toDisplayString(getAttachmentLabel(attachment.attachment_category)), 1)
                      ]),
                      _: 2
                    }, 1032, ["type"])
                  ]),
                  createBaseVNode("div", _hoisted_5$1, [
                    createBaseVNode("div", {
                      class: "file-name",
                      title: attachment.original_filename
                    }, toDisplayString(attachment.original_filename), 9, _hoisted_6$1),
                    createBaseVNode("div", _hoisted_7$1, [
                      createBaseVNode("span", _hoisted_8$1, toDisplayString(unref(formatFileSize)(attachment.file_size)), 1),
                      createBaseVNode("span", _hoisted_9, toDisplayString(unref(formatDate)(attachment.uploaded_at, "date")), 1)
                    ]),
                    attachment.attachment_description ? (openBlock(), createElementBlock("div", _hoisted_10, toDisplayString(attachment.attachment_description), 1)) : createCommentVNode("", true)
                  ]),
                  createBaseVNode("div", _hoisted_11, [
                    createVNode(_component_el_button, {
                      size: "small",
                      onClick: ($event) => handleDownload(attachment)
                    }, {
                      default: withCtx(() => [
                        createVNode(_component_el_icon, null, {
                          default: withCtx(() => [
                            createVNode(unref(download_default))
                          ]),
                          _: 1
                        }),
                        _cache[6] || (_cache[6] = createTextVNode(" 下载 ", -1))
                      ]),
                      _: 1
                    }, 8, ["onClick"]),
                    createVNode(_component_el_button, {
                      size: "small",
                      type: "danger",
                      onClick: ($event) => handleDelete(attachment)
                    }, {
                      default: withCtx(() => [
                        createVNode(_component_el_icon, null, {
                          default: withCtx(() => [
                            createVNode(unref(delete_default))
                          ]),
                          _: 1
                        }),
                        _cache[7] || (_cache[7] = createTextVNode(" 删除 ", -1))
                      ]),
                      _: 1
                    }, 8, ["onClick"])
                  ])
                ]);
              }), 128))
            ]))
          ]),
          _: 1
        }),
        createVNode(_component_el_dialog, {
          modelValue: uploadDialogVisible.value,
          "onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => uploadDialogVisible.value = $event),
          title: "上传简历附件",
          width: "500px"
        }, {
          footer: withCtx(() => [
            createVNode(_component_el_button, {
              onClick: _cache[2] || (_cache[2] = ($event) => uploadDialogVisible.value = false)
            }, {
              default: withCtx(() => [..._cache[10] || (_cache[10] = [
                createTextVNode("取消", -1)
              ])]),
              _: 1
            }),
            createVNode(_component_el_button, {
              type: "primary",
              loading: uploading.value,
              onClick: handleConfirmUpload
            }, {
              default: withCtx(() => [..._cache[11] || (_cache[11] = [
                createTextVNode(" 确定上传 ", -1)
              ])]),
              _: 1
            }, 8, ["loading"])
          ]),
          default: withCtx(() => [
            createVNode(_component_el_form, {
              ref_key: "uploadFormRef",
              ref: uploadFormRef,
              model: uploadForm.value,
              rules: uploadFormRules,
              "label-width": "120px"
            }, {
              default: withCtx(() => [
                createVNode(_component_el_form_item, {
                  label: "附件类型",
                  prop: "attachment_category"
                }, {
                  default: withCtx(() => [
                    createVNode(_component_el_select, {
                      modelValue: uploadForm.value.attachment_category,
                      "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => uploadForm.value.attachment_category = $event),
                      placeholder: "请选择附件类型",
                      style: { "width": "100%" }
                    }, {
                      default: withCtx(() => [
                        createVNode(_component_el_option, {
                          label: "简历文件",
                          value: "resume"
                        }),
                        createVNode(_component_el_option, {
                          label: "身份证",
                          value: "id_card"
                        }),
                        createVNode(_component_el_option, {
                          label: "学历证书",
                          value: "education"
                        }),
                        createVNode(_component_el_option, {
                          label: "学位证书",
                          value: "degree"
                        }),
                        createVNode(_component_el_option, {
                          label: "资质证书",
                          value: "qualification"
                        }),
                        createVNode(_component_el_option, {
                          label: "获奖证书",
                          value: "award"
                        }),
                        createVNode(_component_el_option, {
                          label: "其他材料",
                          value: "other"
                        })
                      ]),
                      _: 1
                    }, 8, ["modelValue"])
                  ]),
                  _: 1
                }),
                createVNode(_component_el_form_item, {
                  label: "附件说明",
                  prop: "description"
                }, {
                  default: withCtx(() => [
                    createVNode(_component_el_input, {
                      modelValue: uploadForm.value.description,
                      "onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => uploadForm.value.description = $event),
                      type: "textarea",
                      rows: 2,
                      placeholder: "请简要说明附件内容（可选）"
                    }, null, 8, ["modelValue"])
                  ]),
                  _: 1
                }),
                createVNode(_component_el_form_item, {
                  label: "选择文件",
                  prop: "file"
                }, {
                  default: withCtx(() => [
                    createVNode(_component_el_upload, {
                      ref_key: "uploadRef",
                      ref: uploadRef,
                      "auto-upload": false,
                      limit: 1,
                      "on-change": handleFileChange,
                      accept: ".pdf,.doc,.docx,.jpg,.jpeg,.png",
                      drag: ""
                    }, {
                      tip: withCtx(() => [..._cache[8] || (_cache[8] = [
                        createBaseVNode("div", { class: "el-upload__tip" }, " 支持PDF、DOC、DOCX、JPG、PNG格式，文件大小不超过20MB ", -1)
                      ])]),
                      default: withCtx(() => [
                        createVNode(_component_el_icon, { class: "el-icon--upload" }, {
                          default: withCtx(() => [
                            createVNode(unref(upload_filled_default))
                          ]),
                          _: 1
                        }),
                        _cache[9] || (_cache[9] = createBaseVNode("div", { class: "el-upload__text" }, [
                          createTextVNode(" 拖拽文件到这里 或 "),
                          createBaseVNode("em", null, "点击上传")
                        ], -1))
                      ]),
                      _: 1
                    }, 512)
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
const ResumeAttachmentsTab = /* @__PURE__ */ _export_sfc(_sfc_main$1, [["__scopeId", "data-v-686973bc"]]);
const _hoisted_1 = { class: "resume-detail" };
const _hoisted_2 = { class: "detail-header" };
const _hoisted_3 = { class: "header-title" };
const _hoisted_4 = {
  key: 1,
  class: "detail-content"
};
const _hoisted_5 = { class: "tab-label" };
const _hoisted_6 = { class: "tab-label" };
const _hoisted_7 = { class: "tab-label" };
const _hoisted_8 = { class: "tab-label" };
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "ResumeDetail",
  setup(__props) {
    const route = useRoute();
    const router = useRouter();
    const { error } = useNotification();
    const loading = ref(false);
    const activeTab = ref("basic");
    const resumeId = ref(0);
    const resumeData = ref({});
    const getEducationTagType = (education) => {
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
          return status;
      }
    };
    const loadResumeData = async () => {
      loading.value = true;
      try {
        const response = await knowledgeApi.getResume(resumeId.value);
        if (response.success && response.data) {
          resumeData.value = response.data;
        } else {
          error("加载失败", "无法获取简历信息");
          handleBack();
        }
      } catch (err) {
        console.error("加载简历数据失败:", err);
        error("加载失败", err instanceof Error ? err.message : "未知错误");
        handleBack();
      } finally {
        loading.value = false;
      }
    };
    const handleTabChange = (tabName) => {
      console.log("切换到Tab:", tabName);
    };
    const handleDataUpdate = async () => {
      await loadResumeData();
    };
    const handleBack = () => {
      router.push("/knowledge/resume-library");
    };
    onMounted(() => {
      const id = route.params.id;
      if (id) {
        resumeId.value = parseInt(id, 10);
        if (isNaN(resumeId.value)) {
          error("参数错误", "无效的简历ID");
          handleBack();
          return;
        }
        loadResumeData();
      } else {
        error("参数错误", "缺少简历ID");
        handleBack();
      }
    });
    return (_ctx, _cache) => {
      const _component_el_button = ElButton;
      const _component_el_tag = ElTag;
      const _component_el_icon = ElIcon;
      const _component_el_tab_pane = ElTabPane;
      const _component_el_tabs = ElTabs;
      return openBlock(), createElementBlock("div", _hoisted_1, [
        createBaseVNode("div", _hoisted_2, [
          createVNode(_component_el_button, {
            onClick: handleBack,
            icon: "ArrowLeft"
          }, {
            default: withCtx(() => [..._cache[1] || (_cache[1] = [
              createTextVNode("返回列表", -1)
            ])]),
            _: 1
          }),
          createBaseVNode("div", _hoisted_3, [
            createBaseVNode("h2", null, toDisplayString(resumeData.value.name || "简历详情"), 1),
            resumeData.value.education_level ? (openBlock(), createBlock(_component_el_tag, {
              key: 0,
              type: getEducationTagType(resumeData.value.education_level)
            }, {
              default: withCtx(() => [
                createTextVNode(toDisplayString(resumeData.value.education_level), 1)
              ]),
              _: 1
            }, 8, ["type"])) : createCommentVNode("", true),
            resumeData.value.current_position ? (openBlock(), createBlock(_component_el_tag, {
              key: 1,
              type: "info"
            }, {
              default: withCtx(() => [
                createTextVNode(toDisplayString(resumeData.value.current_position), 1)
              ]),
              _: 1
            })) : createCommentVNode("", true),
            resumeData.value.status ? (openBlock(), createBlock(_component_el_tag, {
              key: 2,
              type: getStatusTagType(resumeData.value.status)
            }, {
              default: withCtx(() => [
                createTextVNode(toDisplayString(getStatusLabel(resumeData.value.status)), 1)
              ]),
              _: 1
            }, 8, ["type"])) : createCommentVNode("", true)
          ])
        ]),
        loading.value ? (openBlock(), createBlock(unref(Loading), {
          key: 0,
          text: "加载简历信息中..."
        })) : (openBlock(), createElementBlock("div", _hoisted_4, [
          createVNode(_component_el_tabs, {
            modelValue: activeTab.value,
            "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => activeTab.value = $event),
            class: "resume-tabs",
            onTabChange: handleTabChange
          }, {
            default: withCtx(() => [
              createVNode(_component_el_tab_pane, { name: "basic" }, {
                label: withCtx(() => [
                  createBaseVNode("span", _hoisted_5, [
                    createVNode(_component_el_icon, null, {
                      default: withCtx(() => [
                        createVNode(unref(user_default))
                      ]),
                      _: 1
                    }),
                    _cache[2] || (_cache[2] = createTextVNode(" 基本信息 ", -1))
                  ])
                ]),
                default: withCtx(() => [
                  createVNode(ResumeBasicInfoTab, {
                    "resume-id": resumeId.value,
                    "resume-data": resumeData.value,
                    onUpdate: handleDataUpdate
                  }, null, 8, ["resume-id", "resume-data"])
                ]),
                _: 1
              }),
              createVNode(_component_el_tab_pane, { name: "education" }, {
                label: withCtx(() => [
                  createBaseVNode("span", _hoisted_6, [
                    createVNode(_component_el_icon, null, {
                      default: withCtx(() => [
                        createVNode(unref(reading_default))
                      ]),
                      _: 1
                    }),
                    _cache[3] || (_cache[3] = createTextVNode(" 教育信息 ", -1))
                  ])
                ]),
                default: withCtx(() => [
                  createVNode(ResumeEducationTab, {
                    "resume-id": resumeId.value,
                    "resume-data": resumeData.value,
                    onUpdate: handleDataUpdate
                  }, null, 8, ["resume-id", "resume-data"])
                ]),
                _: 1
              }),
              createVNode(_component_el_tab_pane, { name: "work" }, {
                label: withCtx(() => [
                  createBaseVNode("span", _hoisted_7, [
                    createVNode(_component_el_icon, null, {
                      default: withCtx(() => [
                        createVNode(unref(briefcase_default))
                      ]),
                      _: 1
                    }),
                    _cache[4] || (_cache[4] = createTextVNode(" 工作信息 ", -1))
                  ])
                ]),
                default: withCtx(() => [
                  createVNode(ResumeWorkTab, {
                    "resume-id": resumeId.value,
                    "resume-data": resumeData.value,
                    onUpdate: handleDataUpdate
                  }, null, 8, ["resume-id", "resume-data"])
                ]),
                _: 1
              }),
              createVNode(_component_el_tab_pane, { name: "attachments" }, {
                label: withCtx(() => [
                  createBaseVNode("span", _hoisted_8, [
                    createVNode(_component_el_icon, null, {
                      default: withCtx(() => [
                        createVNode(unref(folder_default))
                      ]),
                      _: 1
                    }),
                    _cache[5] || (_cache[5] = createTextVNode(" 附件管理 ", -1))
                  ])
                ]),
                default: withCtx(() => [
                  createVNode(ResumeAttachmentsTab, {
                    "resume-id": resumeId.value,
                    "resume-data": resumeData.value,
                    onUpdate: handleDataUpdate
                  }, null, 8, ["resume-id", "resume-data"])
                ]),
                _: 1
              })
            ]),
            _: 1
          }, 8, ["modelValue"])
        ]))
      ]);
    };
  }
});
const ResumeDetail = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-2d29e80e"]]);
export {
  ResumeDetail as default
};
