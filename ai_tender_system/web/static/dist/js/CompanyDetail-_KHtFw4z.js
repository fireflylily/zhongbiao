import { d as defineComponent, r as ref, D as watch, e as createElementBlock, o as openBlock, f as createVNode, h as unref, w as withCtx, q as ElForm, ak as ElRow, ai as ElCol, s as ElFormItem, y as ElInput, b9 as ElDatePicker, Y as ElSelect, W as ElOption, aA as ElInputNumber, g as ElButton, p as createTextVNode, ad as ElIcon, ba as select_default, c as computed, k as createBlock, n as createBaseVNode, ah as resolveDynamicComponent, t as toDisplayString, l as createCommentVNode, X as ElTag, bb as files_default, ae as document_default, aE as download_default, bc as delete_default, F as Fragment, V as renderList, aB as ElText, aF as upload_default, U as normalizeClass, as as ElCard, S as onMounted, bd as plus_default, j as ElDialog, b3 as folder_default, be as credit_card_default, bf as user_default, bg as document_checked_default, am as ElTableColumn, x as ElRadio, al as ElTable, ar as ElEmpty, bh as tickets_default, u as useRoute, M as useRouter, ax as ElTabPane, b6 as office_building_default, bi as medal_default, bj as wallet_default, aw as ElTabs } from "./vendor-MtO928VE.js";
import { L as Loading } from "./Loading-75jVWA4c.js";
/* empty css                                                                           */
/* empty css                                                                         */
import { a as useNotification, _ as _export_sfc } from "./index.js";
import { c as companyApi } from "./company-z4Xg082l.js";
import { C as Card } from "./Card-jLaN2c6R.js";
import { D as DocumentUploader } from "./DocumentUploader-D4BCHi8H.js";
import "./imageCompressor-DC3BCfPz.js";
const _hoisted_1$5 = { class: "basic-info-tab" };
const _sfc_main$5 = /* @__PURE__ */ defineComponent({
  __name: "BasicInfoTab",
  props: {
    companyId: {},
    companyData: {}
  },
  emits: ["update"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const { success, error } = useNotification();
    const formRef = ref();
    const saving = ref(false);
    const formData = ref({
      company_name: "",
      establish_date: "",
      legal_representative: "",
      legal_representative_position: "",
      legal_representative_gender: "",
      legal_representative_age: void 0,
      social_credit_code: "",
      registered_capital: "",
      company_type: "",
      registered_address: "",
      fixed_phone: "",
      fax: "",
      postal_code: "",
      email: "",
      business_scope: "",
      description: ""
    });
    const formRules = {
      company_name: [
        { required: true, message: "请输入企业名称", trigger: "blur" }
      ],
      email: [
        { type: "email", message: "请输入正确的邮箱地址", trigger: "blur" }
      ],
      postal_code: [
        { pattern: /^\d{6}$/, message: "邮政编码必须是6位数字", trigger: "blur" }
      ]
    };
    watch(
      () => props.companyData,
      (newData) => {
        if (newData) {
          formData.value = {
            company_name: newData.company_name || "",
            establish_date: newData.establish_date || "",
            legal_representative: newData.legal_representative || "",
            legal_representative_position: newData.legal_representative_position || "",
            legal_representative_gender: newData.legal_representative_gender || "",
            legal_representative_age: newData.legal_representative_age || void 0,
            social_credit_code: newData.social_credit_code || "",
            registered_capital: newData.registered_capital || "",
            company_type: newData.company_type || "",
            registered_address: newData.registered_address || "",
            fixed_phone: newData.fixed_phone || "",
            fax: newData.fax || "",
            postal_code: newData.postal_code || "",
            email: newData.email || "",
            business_scope: newData.business_scope || "",
            description: newData.description || ""
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
          const response = await companyApi.updateCompany(props.companyId, {
            companyName: formData.value.company_name,
            establishDate: formData.value.establish_date,
            legalRepresentative: formData.value.legal_representative,
            legalRepresentativePosition: formData.value.legal_representative_position,
            legalRepresentativeGender: formData.value.legal_representative_gender,
            legalRepresentativeAge: formData.value.legal_representative_age,
            socialCreditCode: formData.value.social_credit_code,
            registeredCapital: formData.value.registered_capital,
            companyType: formData.value.company_type,
            registeredAddress: formData.value.registered_address,
            fixedPhone: formData.value.fixed_phone,
            fax: formData.value.fax,
            postalCode: formData.value.postal_code,
            email: formData.value.email,
            businessScope: formData.value.business_scope,
            companyDescription: formData.value.description
          });
          if (response.success) {
            success("保存成功", "基础信息已更新");
            emit("update");
          }
        } catch (err) {
          console.error("保存基础信息失败:", err);
          error("保存失败", err instanceof Error ? err.message : "未知错误");
        } finally {
          saving.value = false;
        }
      });
    };
    return (_ctx, _cache) => {
      const _component_el_input = ElInput;
      const _component_el_form_item = ElFormItem;
      const _component_el_col = ElCol;
      const _component_el_date_picker = ElDatePicker;
      const _component_el_row = ElRow;
      const _component_el_option = ElOption;
      const _component_el_select = ElSelect;
      const _component_el_input_number = ElInputNumber;
      const _component_el_icon = ElIcon;
      const _component_el_button = ElButton;
      const _component_el_form = ElForm;
      return openBlock(), createElementBlock("div", _hoisted_1$5, [
        createVNode(unref(Card), { title: "基础信息" }, {
          default: withCtx(() => [
            createVNode(_component_el_form, {
              ref_key: "formRef",
              ref: formRef,
              model: formData.value,
              rules: formRules,
              "label-width": "140px",
              class: "basic-form"
            }, {
              default: withCtx(() => [
                createVNode(_component_el_row, { gutter: 20 }, {
                  default: withCtx(() => [
                    createVNode(_component_el_col, { span: 12 }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, {
                          label: "企业名称",
                          prop: "company_name"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: formData.value.company_name,
                              "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => formData.value.company_name = $event),
                              placeholder: "请输入企业名称"
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
                          label: "成立日期",
                          prop: "establish_date"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_date_picker, {
                              modelValue: formData.value.establish_date,
                              "onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => formData.value.establish_date = $event),
                              type: "date",
                              placeholder: "选择日期",
                              style: { "width": "100%" },
                              "value-format": "YYYY-MM-DD"
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
                          label: "法定代表人",
                          prop: "legal_representative"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: formData.value.legal_representative,
                              "onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => formData.value.legal_representative = $event),
                              placeholder: "请输入法定代表人"
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
                          label: "法定代表人职务",
                          prop: "legal_representative_position"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: formData.value.legal_representative_position,
                              "onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => formData.value.legal_representative_position = $event),
                              placeholder: "请输入职务"
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
                          label: "法定代表人性别",
                          prop: "legal_representative_gender"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_select, {
                              modelValue: formData.value.legal_representative_gender,
                              "onUpdate:modelValue": _cache[4] || (_cache[4] = ($event) => formData.value.legal_representative_gender = $event),
                              placeholder: "请选择性别",
                              style: { "width": "100%" }
                            }, {
                              default: withCtx(() => [
                                createVNode(_component_el_option, {
                                  label: "男",
                                  value: "男"
                                }),
                                createVNode(_component_el_option, {
                                  label: "女",
                                  value: "女"
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
                          label: "法定代表人年龄",
                          prop: "legal_representative_age"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input_number, {
                              modelValue: formData.value.legal_representative_age,
                              "onUpdate:modelValue": _cache[5] || (_cache[5] = ($event) => formData.value.legal_representative_age = $event),
                              min: 18,
                              max: 100,
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
                    createVNode(_component_el_col, { span: 12 }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, {
                          label: "统一社会信用代码",
                          prop: "social_credit_code"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: formData.value.social_credit_code,
                              "onUpdate:modelValue": _cache[6] || (_cache[6] = ($event) => formData.value.social_credit_code = $event),
                              placeholder: "请输入统一社会信用代码"
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
                          label: "注册资本",
                          prop: "registered_capital"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: formData.value.registered_capital,
                              "onUpdate:modelValue": _cache[7] || (_cache[7] = ($event) => formData.value.registered_capital = $event),
                              placeholder: "如：1000万元"
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
                          label: "企业类型",
                          prop: "company_type"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: formData.value.company_type,
                              "onUpdate:modelValue": _cache[8] || (_cache[8] = ($event) => formData.value.company_type = $event),
                              placeholder: "如：有限责任公司"
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
                          label: "注册地址",
                          prop: "registered_address"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: formData.value.registered_address,
                              "onUpdate:modelValue": _cache[9] || (_cache[9] = ($event) => formData.value.registered_address = $event),
                              placeholder: "请输入注册地址"
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
                          label: "联系电话",
                          prop: "fixed_phone"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: formData.value.fixed_phone,
                              "onUpdate:modelValue": _cache[10] || (_cache[10] = ($event) => formData.value.fixed_phone = $event),
                              placeholder: "请输入联系电话"
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
                          label: "传真",
                          prop: "fax"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: formData.value.fax,
                              "onUpdate:modelValue": _cache[11] || (_cache[11] = ($event) => formData.value.fax = $event),
                              placeholder: "请输入传真"
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
                          label: "邮政编码",
                          prop: "postal_code"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: formData.value.postal_code,
                              "onUpdate:modelValue": _cache[12] || (_cache[12] = ($event) => formData.value.postal_code = $event),
                              placeholder: "请输入邮政编码",
                              maxlength: "6"
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
                          label: "电子邮箱",
                          prop: "email"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: formData.value.email,
                              "onUpdate:modelValue": _cache[13] || (_cache[13] = ($event) => formData.value.email = $event),
                              placeholder: "请输入电子邮箱"
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
                createVNode(_component_el_row, null, {
                  default: withCtx(() => [
                    createVNode(_component_el_col, { span: 24 }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, {
                          label: "经营范围",
                          prop: "business_scope"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: formData.value.business_scope,
                              "onUpdate:modelValue": _cache[14] || (_cache[14] = ($event) => formData.value.business_scope = $event),
                              type: "textarea",
                              rows: 5,
                              placeholder: "请输入经营范围"
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
                createVNode(_component_el_row, null, {
                  default: withCtx(() => [
                    createVNode(_component_el_col, { span: 24 }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, {
                          label: "企业简介",
                          prop: "description"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: formData.value.description,
                              "onUpdate:modelValue": _cache[15] || (_cache[15] = ($event) => formData.value.description = $event),
                              type: "textarea",
                              rows: 5,
                              placeholder: "请输入企业简介"
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
                createVNode(_component_el_row, null, {
                  default: withCtx(() => [
                    createVNode(_component_el_col, { span: 24 }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, null, {
                          default: withCtx(() => [
                            createVNode(_component_el_button, {
                              type: "primary",
                              loading: saving.value,
                              onClick: handleSave
                            }, {
                              default: withCtx(() => [
                                createVNode(_component_el_icon, null, {
                                  default: withCtx(() => [
                                    createVNode(unref(select_default))
                                  ]),
                                  _: 1
                                }),
                                _cache[16] || (_cache[16] = createTextVNode(" 保存基础信息 ", -1))
                              ]),
                              _: 1
                            }, 8, ["loading"])
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
            }, 8, ["model"])
          ]),
          _: 1
        })
      ]);
    };
  }
});
const BasicInfoTab = /* @__PURE__ */ _export_sfc(_sfc_main$5, [["__scopeId", "data-v-cf1705e1"]]);
const _hoisted_1$4 = { class: "card-header" };
const _hoisted_2$4 = { class: "qual-info" };
const _hoisted_3$4 = { class: "qual-name" };
const _hoisted_4$4 = { class: "badges" };
const _hoisted_5$2 = {
  key: 0,
  class: "file-status"
};
const _hoisted_6$2 = {
  key: 0,
  class: "single-file"
};
const _hoisted_7$2 = { class: "file-item" };
const _hoisted_8$2 = { class: "file-details" };
const _hoisted_9$1 = { class: "file-name" };
const _hoisted_10$1 = { class: "file-meta" };
const _hoisted_11$1 = { class: "file-actions" };
const _hoisted_12$1 = {
  key: 1,
  class: "multiple-files"
};
const _hoisted_13$1 = { class: "file-details" };
const _hoisted_14$1 = { class: "file-name" };
const _hoisted_15$1 = { class: "file-meta" };
const _hoisted_16$1 = { class: "file-actions" };
const _hoisted_17$1 = {
  key: 1,
  class: "no-file"
};
const _hoisted_18$1 = { class: "card-footer" };
const _hoisted_19$1 = { class: "upload-section" };
const _hoisted_20$1 = { class: "upload-tips" };
const _sfc_main$4 = /* @__PURE__ */ defineComponent({
  __name: "QualificationCard",
  props: {
    qualification: {},
    fileInfo: {},
    isCustom: { type: Boolean },
    onUpload: { type: Function }
  },
  emits: ["upload", "download", "delete", "remove-custom"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const uploaderRef = ref();
    const hasFile = computed(() => {
      if (!props.fileInfo) return false;
      if (props.fileInfo.allow_multiple_files) {
        return props.fileInfo.files && props.fileInfo.files.length > 0;
      }
      return !!props.fileInfo.original_filename;
    });
    const isMultipleFiles = computed(() => {
      var _a, _b;
      return ((_a = props.fileInfo) == null ? void 0 : _a.allow_multiple_files) && ((_b = props.fileInfo) == null ? void 0 : _b.files);
    });
    const acceptTypes = computed(() => {
      if (props.qualification.key === "financial_audit_report") {
        return ".pdf,.xls,.xlsx,.jpg,.jpeg,.png";
      }
      return ".pdf,.jpg,.jpeg,.png";
    });
    const imageType = computed(() => {
      const key = props.qualification.key;
      if (key === "business_license") {
        return "license";
      }
      if (key.includes("id") || key === "legal_id_front" || key === "legal_id_back") {
        return "id_card";
      }
      if (key.includes("seal")) {
        return "seal";
      }
      if (key.includes("iso") || key.includes("cmmi") || key.includes("certificate") || key.includes("qualification") || key.includes("认证")) {
        return "qualification";
      }
      return "default";
    });
    const handleCustomUpload = async (options) => {
      const { file, onSuccess, onError } = options;
      try {
        if (props.onUpload) {
          await props.onUpload(file);
        } else {
          emit("upload", file);
        }
        onSuccess({ success: true });
      } catch (error) {
        onError(error);
      }
    };
    const handleDownload = () => {
      emit("download", props.qualification.key);
    };
    const handleDownloadById = (qualId) => {
      emit("download", props.qualification.key, qualId);
    };
    const handleDelete = () => {
      emit("delete", props.qualification.key);
    };
    const handleDeleteById = (qualId) => {
      emit("delete", props.qualification.key, qualId);
    };
    const formatFileSize = (bytes) => {
      if (!bytes) return "0 B";
      const k = 1024;
      const sizes = ["B", "KB", "MB", "GB"];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return Math.round(bytes / Math.pow(k, i) * 100) / 100 + " " + sizes[i];
    };
    const formatDate = (dateStr) => {
      if (!dateStr) return "";
      const date = new Date(dateStr);
      return date.toLocaleString("zh-CN", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit"
      });
    };
    return (_ctx, _cache) => {
      const _component_el_icon = ElIcon;
      const _component_el_tag = ElTag;
      const _component_el_button = ElButton;
      const _component_el_text = ElText;
      const _component_el_card = ElCard;
      return openBlock(), createBlock(_component_el_card, {
        class: normalizeClass(["qualification-card", { "required": __props.qualification.required, "has-file": hasFile.value }])
      }, {
        default: withCtx(() => [
          createBaseVNode("div", _hoisted_1$4, [
            createBaseVNode("div", _hoisted_2$4, [
              createVNode(_component_el_icon, {
                class: "qual-icon",
                size: 20
              }, {
                default: withCtx(() => [
                  (openBlock(), createBlock(resolveDynamicComponent(__props.qualification.icon)))
                ]),
                _: 1
              }),
              createBaseVNode("span", _hoisted_3$4, toDisplayString(__props.qualification.name), 1)
            ]),
            createBaseVNode("div", _hoisted_4$4, [
              __props.qualification.required ? (openBlock(), createBlock(_component_el_tag, {
                key: 0,
                type: "warning",
                size: "small"
              }, {
                default: withCtx(() => [..._cache[1] || (_cache[1] = [
                  createTextVNode("必需", -1)
                ])]),
                _: 1
              })) : createCommentVNode("", true),
              __props.qualification.allowMultiple ? (openBlock(), createBlock(_component_el_tag, {
                key: 1,
                type: "info",
                size: "small"
              }, {
                default: withCtx(() => [
                  createVNode(_component_el_icon, null, {
                    default: withCtx(() => [
                      createVNode(unref(files_default))
                    ]),
                    _: 1
                  }),
                  _cache[2] || (_cache[2] = createTextVNode(" 多文件 ", -1))
                ]),
                _: 1
              })) : createCommentVNode("", true)
            ])
          ]),
          hasFile.value ? (openBlock(), createElementBlock("div", _hoisted_5$2, [
            !isMultipleFiles.value ? (openBlock(), createElementBlock("div", _hoisted_6$2, [
              createBaseVNode("div", _hoisted_7$2, [
                createVNode(_component_el_icon, { class: "file-icon" }, {
                  default: withCtx(() => [
                    createVNode(unref(document_default))
                  ]),
                  _: 1
                }),
                createBaseVNode("div", _hoisted_8$2, [
                  createBaseVNode("div", _hoisted_9$1, toDisplayString(__props.fileInfo.original_filename), 1),
                  createBaseVNode("div", _hoisted_10$1, [
                    createBaseVNode("span", null, toDisplayString(formatFileSize(__props.fileInfo.file_size)), 1),
                    _cache[3] || (_cache[3] = createBaseVNode("span", { class: "divider" }, "•", -1)),
                    createBaseVNode("span", null, toDisplayString(formatDate(__props.fileInfo.upload_time)), 1)
                  ])
                ]),
                createBaseVNode("div", _hoisted_11$1, [
                  createVNode(_component_el_button, {
                    text: "",
                    type: "primary",
                    size: "small",
                    onClick: handleDownload
                  }, {
                    default: withCtx(() => [
                      createVNode(_component_el_icon, null, {
                        default: withCtx(() => [
                          createVNode(unref(download_default))
                        ]),
                        _: 1
                      })
                    ]),
                    _: 1
                  }),
                  createVNode(_component_el_button, {
                    text: "",
                    type: "danger",
                    size: "small",
                    onClick: handleDelete
                  }, {
                    default: withCtx(() => [
                      createVNode(_component_el_icon, null, {
                        default: withCtx(() => [
                          createVNode(unref(delete_default))
                        ]),
                        _: 1
                      })
                    ]),
                    _: 1
                  })
                ])
              ])
            ])) : (openBlock(), createElementBlock("div", _hoisted_12$1, [
              (openBlock(true), createElementBlock(Fragment, null, renderList(__props.fileInfo.files, (file) => {
                return openBlock(), createElementBlock("div", {
                  key: file.qualification_id,
                  class: "file-item"
                }, [
                  createVNode(_component_el_icon, { class: "file-icon" }, {
                    default: withCtx(() => [
                      createVNode(unref(document_default))
                    ]),
                    _: 1
                  }),
                  createBaseVNode("div", _hoisted_13$1, [
                    createBaseVNode("div", _hoisted_14$1, toDisplayString(file.original_filename), 1),
                    createBaseVNode("div", _hoisted_15$1, [
                      createBaseVNode("span", null, toDisplayString(formatFileSize(file.file_size)), 1),
                      _cache[4] || (_cache[4] = createBaseVNode("span", { class: "divider" }, "•", -1)),
                      createBaseVNode("span", null, toDisplayString(formatDate(file.upload_time)), 1)
                    ])
                  ]),
                  createBaseVNode("div", _hoisted_16$1, [
                    createVNode(_component_el_button, {
                      text: "",
                      type: "primary",
                      size: "small",
                      onClick: ($event) => handleDownloadById(file.qualification_id)
                    }, {
                      default: withCtx(() => [
                        createVNode(_component_el_icon, null, {
                          default: withCtx(() => [
                            createVNode(unref(download_default))
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }, 8, ["onClick"]),
                    createVNode(_component_el_button, {
                      text: "",
                      type: "danger",
                      size: "small",
                      onClick: ($event) => handleDeleteById(file.qualification_id)
                    }, {
                      default: withCtx(() => [
                        createVNode(_component_el_icon, null, {
                          default: withCtx(() => [
                            createVNode(unref(delete_default))
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }, 8, ["onClick"])
                  ])
                ]);
              }), 128))
            ]))
          ])) : (openBlock(), createElementBlock("div", _hoisted_17$1, [
            createVNode(_component_el_text, {
              type: "info",
              size: "small"
            }, {
              default: withCtx(() => [..._cache[5] || (_cache[5] = [
                createTextVNode("未上传文件", -1)
              ])]),
              _: 1
            })
          ])),
          createBaseVNode("div", _hoisted_18$1, [
            createBaseVNode("div", _hoisted_19$1, [
              createVNode(unref(DocumentUploader), {
                ref_key: "uploaderRef",
                ref: uploaderRef,
                accept: acceptTypes.value,
                multiple: __props.qualification.allowMultiple,
                "show-file-list": false,
                "http-request": handleCustomUpload,
                "max-size": 20,
                "auto-compress-image": true,
                "image-type": imageType.value
              }, {
                trigger: withCtx(() => [
                  createVNode(_component_el_button, {
                    type: "primary",
                    size: "small"
                  }, {
                    default: withCtx(() => [
                      createVNode(_component_el_icon, null, {
                        default: withCtx(() => [
                          createVNode(unref(upload_default))
                        ]),
                        _: 1
                      }),
                      createTextVNode(" " + toDisplayString(__props.qualification.allowMultiple ? "批量上传" : "上传文件"), 1)
                    ]),
                    _: 1
                  })
                ]),
                _: 1
              }, 8, ["accept", "multiple", "image-type"]),
              __props.isCustom ? (openBlock(), createBlock(_component_el_button, {
                key: 0,
                type: "danger",
                size: "small",
                onClick: _cache[0] || (_cache[0] = ($event) => _ctx.$emit("remove-custom"))
              }, {
                default: withCtx(() => [
                  createVNode(_component_el_icon, null, {
                    default: withCtx(() => [
                      createVNode(unref(delete_default))
                    ]),
                    _: 1
                  }),
                  _cache[6] || (_cache[6] = createTextVNode(" 移除 ", -1))
                ]),
                _: 1
              })) : createCommentVNode("", true)
            ]),
            createBaseVNode("div", _hoisted_20$1, [
              createVNode(_component_el_text, {
                type: "info",
                size: "small"
              }, {
                default: withCtx(() => [..._cache[7] || (_cache[7] = [
                  createTextVNode(" 支持JPG、PNG、PDF格式 ", -1),
                  createBaseVNode("span", { class: "pdf-tip" }, "（PDF将自动转换为图片）", -1)
                ])]),
                _: 1
              })
            ])
          ])
        ]),
        _: 1
      }, 8, ["class"]);
    };
  }
});
const QualificationCard = /* @__PURE__ */ _export_sfc(_sfc_main$4, [["__scopeId", "data-v-1923de96"]]);
const _hoisted_1$3 = { class: "qualification-tab" };
const _hoisted_2$3 = { key: 1 };
const _hoisted_3$3 = { class: "qualification-category" };
const _hoisted_4$3 = { class: "category-title text-secondary" };
const _sfc_main$3 = /* @__PURE__ */ defineComponent({
  __name: "QualificationTab",
  props: {
    companyId: {},
    companyData: {}
  },
  emits: ["update"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const { success, error } = useNotification();
    const loading = ref(false);
    const qualificationFiles = ref({});
    const customQualifications = ref([]);
    const customDialogVisible = ref(false);
    const customForm = ref({ name: "" });
    const categories = [
      { key: "basic", name: "基本证件资质", color: "primary" },
      { key: "iso", name: "ISO体系认证", color: "success" },
      { key: "credit", name: "信用资质证明", color: "info" },
      { key: "industry", name: "行业专业资质", color: "danger" }
    ];
    const standardQualifications = [
      // 基本证件 (5项)
      { key: "business_license", name: "营业执照", icon: "Document", category: "basic", required: true },
      { key: "legal_id_front", name: "法人身份证(正面)", icon: "CreditCard", category: "basic", required: true },
      { key: "legal_id_back", name: "法人身份证(反面)", icon: "CreditCard", category: "basic", required: true },
      { key: "bank_account_permit", name: "银行开户许可证", icon: "CreditCard", category: "basic" },
      { key: "tax_registration", name: "税务登记证", icon: "DocumentChecked", category: "basic" },
      // ISO认证 (4项)
      { key: "iso9001", name: "ISO 9001质量管理体系认证", icon: "Medal", category: "iso" },
      { key: "iso14001", name: "ISO 14001环境管理体系认证", icon: "Medal", category: "iso" },
      { key: "iso27001", name: "ISO 27001信息安全管理体系认证", icon: "Lock", category: "iso" },
      { key: "iso20000", name: "ISO 20000 IT服务管理体系认证", icon: "Monitor", category: "iso" },
      // 信用资质 (4项)
      { key: "dishonest_executor", name: "失信被执行人名单（信用中国）", icon: "WarningFilled", category: "credit" },
      { key: "tax_violation_check", name: "重大税收违法案件当事人名单（信用中国）", icon: "WarningFilled", category: "credit" },
      { key: "gov_procurement_creditchina", name: "政府采购严重违法失信（信用中国）", icon: "Flag", category: "credit" },
      { key: "gov_procurement_ccgp", name: "政府采购严重违法失信行为信息记录（政府采购网）", icon: "CircleCheck", category: "credit" },
      // 行业资质 (6项)
      { key: "basic_telecom_permit", name: "基础电信业务许可证", icon: "PhoneFilled", category: "industry" },
      { key: "value_added_telecom_permit", name: "增值电信业务许可证", icon: "PhoneFilled", category: "industry" },
      { key: "software_copyright", name: "软件著作权登记证书", icon: "Document", category: "industry", allowMultiple: true },
      { key: "patent_certificate", name: "专利证书", icon: "TrophyBase", category: "industry", allowMultiple: true },
      { key: "high_tech", name: "高新技术企业证书", icon: "Star", category: "industry" },
      { key: "software_enterprise", name: "软件企业认定证书", icon: "Monitor", category: "industry" },
      { key: "cmmi", name: "CMMI成熟度等级证书", icon: "Trophy", category: "industry" }
    ];
    const getQualificationsByCategory = (categoryKey) => {
      return standardQualifications.filter((q) => q.category === categoryKey);
    };
    const loadQualifications = async () => {
      loading.value = true;
      try {
        const response = await companyApi.getCompanyQualifications(props.companyId);
        if (response.success && response.data) {
          qualificationFiles.value = response.data;
          console.log("加载资质文件:", qualificationFiles.value);
        }
      } catch (err) {
        console.error("加载资质文件失败:", err);
        error("加载失败", err instanceof Error ? err.message : "未知错误");
      } finally {
        loading.value = false;
      }
    };
    const handleUpload = async (qualKey, file) => {
      const qual = standardQualifications.find((q) => q.key === qualKey) || customQualifications.value.find((q) => q.key === qualKey);
      try {
        const response = await companyApi.uploadQualification(
          props.companyId,
          qualKey,
          file,
          {}
        );
        if (response.success) {
          success("上传成功", `${(qual == null ? void 0 : qual.name) || "资质文件"}上传成功`);
          await loadQualifications();
          emit("update");
        } else {
          throw new Error(response.message || "上传失败");
        }
      } catch (err) {
        console.error("上传资质文件失败:", err);
        const errorMsg = err instanceof Error ? err.message : "未知错误";
        error("上传失败", errorMsg);
        throw err;
      }
    };
    const createUploadHandler = (qualKey) => {
      return (file) => handleUpload(qualKey, file);
    };
    const handleDownload = async (qualKey, qualId) => {
      try {
        if (qualId) {
          await companyApi.downloadQualification(qualId, "");
        } else {
          window.open(`/api/companies/${props.companyId}/qualifications/${qualKey}/download`);
        }
      } catch (err) {
        console.error("下载资质文件失败:", err);
        error("下载失败", err instanceof Error ? err.message : "未知错误");
      }
    };
    const handleDelete = async (qualKey, qualId) => {
      try {
        if (!confirm("确定要删除此资质文件吗？")) {
          return;
        }
        if (qualId) {
          await companyApi.deleteQualification(qualId);
        } else {
          const response = await fetch(`/api/companies/${props.companyId}/qualifications/${qualKey}`, {
            method: "DELETE"
          });
          if (!response.ok) throw new Error("删除失败");
        }
        success("删除成功", "资质文件已删除");
        await loadQualifications();
        emit("update");
      } catch (err) {
        console.error("删除资质文件失败:", err);
        error("删除失败", err instanceof Error ? err.message : "未知错误");
      }
    };
    const showAddCustomDialog = () => {
      customForm.value.name = "";
      customDialogVisible.value = true;
    };
    const handleAddCustom = () => {
      if (!customForm.value.name.trim()) {
        error("错误", "请输入资质名称");
        return;
      }
      const customKey = `custom_${Date.now()}`;
      customQualifications.value.push({
        key: customKey,
        name: customForm.value.name.trim(),
        icon: "Document",
        category: "custom"
      });
      customDialogVisible.value = false;
      success("添加成功", "自定义资质已添加");
    };
    const removeCustomQualification = (index) => {
      if (confirm("确定要移除此自定义资质吗？")) {
        customQualifications.value.splice(index, 1);
        success("移除成功", "自定义资质已移除");
      }
    };
    onMounted(() => {
      loadQualifications();
    });
    return (_ctx, _cache) => {
      const _component_el_icon = ElIcon;
      const _component_el_col = ElCol;
      const _component_el_row = ElRow;
      const _component_el_button = ElButton;
      const _component_el_input = ElInput;
      const _component_el_form_item = ElFormItem;
      const _component_el_form = ElForm;
      const _component_el_dialog = ElDialog;
      return openBlock(), createElementBlock("div", _hoisted_1$3, [
        createVNode(unref(Card), { title: "资质信息管理" }, {
          default: withCtx(() => [
            loading.value ? (openBlock(), createBlock(unref(Loading), {
              key: 0,
              text: "加载资质信息..."
            })) : (openBlock(), createElementBlock("div", _hoisted_2$3, [
              (openBlock(), createElementBlock(Fragment, null, renderList(categories, (category) => {
                return createBaseVNode("div", {
                  key: category.key,
                  class: "qualification-category"
                }, [
                  createBaseVNode("h6", {
                    class: normalizeClass(["category-title", `text-${category.color}`])
                  }, [
                    createVNode(_component_el_icon, null, {
                      default: withCtx(() => [
                        createVNode(unref(folder_default))
                      ]),
                      _: 1
                    }),
                    createTextVNode(" " + toDisplayString(category.name), 1)
                  ], 2),
                  createVNode(_component_el_row, { gutter: 16 }, {
                    default: withCtx(() => [
                      (openBlock(true), createElementBlock(Fragment, null, renderList(getQualificationsByCategory(category.key), (qual) => {
                        return openBlock(), createBlock(_component_el_col, {
                          key: qual.key,
                          span: 12
                        }, {
                          default: withCtx(() => [
                            createVNode(QualificationCard, {
                              qualification: qual,
                              "file-info": qualificationFiles.value[qual.key],
                              "on-upload": createUploadHandler(qual.key),
                              onDownload: handleDownload,
                              onDelete: handleDelete
                            }, null, 8, ["qualification", "file-info", "on-upload"])
                          ]),
                          _: 2
                        }, 1024);
                      }), 128))
                    ]),
                    _: 2
                  }, 1024)
                ]);
              }), 64)),
              createBaseVNode("div", _hoisted_3$3, [
                createBaseVNode("h6", _hoisted_4$3, [
                  createVNode(_component_el_icon, null, {
                    default: withCtx(() => [
                      createVNode(unref(plus_default))
                    ]),
                    _: 1
                  }),
                  _cache[3] || (_cache[3] = createTextVNode(" 自定义资质 ", -1))
                ]),
                createVNode(_component_el_button, {
                  type: "primary",
                  onClick: showAddCustomDialog
                }, {
                  default: withCtx(() => [
                    createVNode(_component_el_icon, null, {
                      default: withCtx(() => [
                        createVNode(unref(plus_default))
                      ]),
                      _: 1
                    }),
                    _cache[4] || (_cache[4] = createTextVNode(" 添加自定义资质 ", -1))
                  ]),
                  _: 1
                }),
                customQualifications.value.length > 0 ? (openBlock(), createBlock(_component_el_row, {
                  key: 0,
                  gutter: 16,
                  class: "mt-3"
                }, {
                  default: withCtx(() => [
                    (openBlock(true), createElementBlock(Fragment, null, renderList(customQualifications.value, (qual, index) => {
                      return openBlock(), createBlock(_component_el_col, {
                        key: qual.key,
                        span: 12
                      }, {
                        default: withCtx(() => [
                          createVNode(QualificationCard, {
                            qualification: qual,
                            "file-info": qualificationFiles.value[qual.key],
                            "is-custom": true,
                            "on-upload": createUploadHandler(qual.key),
                            onDownload: handleDownload,
                            onDelete: handleDelete,
                            onRemoveCustom: ($event) => removeCustomQualification(index)
                          }, null, 8, ["qualification", "file-info", "on-upload", "onRemoveCustom"])
                        ]),
                        _: 2
                      }, 1024);
                    }), 128))
                  ]),
                  _: 1
                })) : createCommentVNode("", true)
              ])
            ]))
          ]),
          _: 1
        }),
        createVNode(_component_el_dialog, {
          modelValue: customDialogVisible.value,
          "onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => customDialogVisible.value = $event),
          title: "添加自定义资质",
          width: "400px"
        }, {
          footer: withCtx(() => [
            createVNode(_component_el_button, {
              onClick: _cache[1] || (_cache[1] = ($event) => customDialogVisible.value = false)
            }, {
              default: withCtx(() => [..._cache[5] || (_cache[5] = [
                createTextVNode("取消", -1)
              ])]),
              _: 1
            }),
            createVNode(_component_el_button, {
              type: "primary",
              onClick: handleAddCustom
            }, {
              default: withCtx(() => [..._cache[6] || (_cache[6] = [
                createTextVNode("确定", -1)
              ])]),
              _: 1
            })
          ]),
          default: withCtx(() => [
            createVNode(_component_el_form, {
              model: customForm.value,
              "label-width": "100px"
            }, {
              default: withCtx(() => [
                createVNode(_component_el_form_item, { label: "资质名称" }, {
                  default: withCtx(() => [
                    createVNode(_component_el_input, {
                      modelValue: customForm.value.name,
                      "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => customForm.value.name = $event),
                      placeholder: "请输入资质名称",
                      maxlength: "50"
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
const QualificationTab = /* @__PURE__ */ _export_sfc(_sfc_main$3, [["__scopeId", "data-v-d0a8e1b6"]]);
const _hoisted_1$2 = { class: "personnel-tab" };
const _hoisted_2$2 = { class: "attachments-grid" };
const _hoisted_3$2 = { class: "attachment-item" };
const _hoisted_4$2 = { class: "attachment-header" };
const _hoisted_5$1 = {
  key: 0,
  class: "file-info"
};
const _hoisted_6$1 = { class: "file-name" };
const _hoisted_7$1 = { class: "file-actions" };
const _hoisted_8$1 = {
  key: 1,
  class: "no-file"
};
const _hoisted_9 = { class: "attachment-item" };
const _hoisted_10 = { class: "attachment-header" };
const _hoisted_11 = {
  key: 0,
  class: "file-info"
};
const _hoisted_12 = { class: "file-name" };
const _hoisted_13 = { class: "file-actions" };
const _hoisted_14 = {
  key: 1,
  class: "no-file"
};
const _hoisted_15 = { class: "attachment-item" };
const _hoisted_16 = { class: "attachment-header" };
const _hoisted_17 = {
  key: 0,
  class: "file-info"
};
const _hoisted_18 = { class: "file-name" };
const _hoisted_19 = { class: "file-actions" };
const _hoisted_20 = {
  key: 1,
  class: "no-file"
};
const _hoisted_21 = { class: "attachment-item" };
const _hoisted_22 = { class: "attachment-header" };
const _hoisted_23 = {
  key: 0,
  class: "file-info"
};
const _hoisted_24 = { class: "file-name" };
const _hoisted_25 = { class: "file-actions" };
const _hoisted_26 = {
  key: 1,
  class: "no-file"
};
const _sfc_main$2 = /* @__PURE__ */ defineComponent({
  __name: "PersonnelTab",
  props: {
    companyId: {},
    companyData: {}
  },
  emits: ["update"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const { success, error } = useNotification();
    const formRef = ref();
    const saving = ref(false);
    const formData = ref({
      authorized_person_name: "",
      authorized_person_id: "",
      authorized_person_gender: "",
      authorized_person_age: void 0,
      authorized_person_position: "",
      authorized_person_title: ""
    });
    const attachments = ref({
      auth_id_front: null,
      auth_id_back: null,
      manager_resume: null,
      social_security: null
    });
    const formRules = {
      authorized_person_id: [
        { pattern: /^[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]$/, message: "请输入正确的身份证号", trigger: "blur" }
      ]
    };
    watch(
      () => props.companyData,
      (newData) => {
        if (newData) {
          formData.value = {
            authorized_person_name: newData.authorized_person_name || "",
            authorized_person_id: newData.authorized_person_id || "",
            authorized_person_gender: newData.authorized_person_gender || "",
            authorized_person_age: newData.authorized_person_age || void 0,
            authorized_person_position: newData.authorized_person_position || "",
            authorized_person_title: newData.authorized_person_title || ""
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
          const response = await companyApi.updateCompany(props.companyId, {
            authorizedPersonName: formData.value.authorized_person_name,
            authorizedPersonId: formData.value.authorized_person_id,
            authorizedPersonGender: formData.value.authorized_person_gender,
            authorizedPersonAge: formData.value.authorized_person_age,
            authorizedPersonPosition: formData.value.authorized_person_position,
            authorizedPersonTitle: formData.value.authorized_person_title
          });
          if (response.success) {
            success("保存成功", "被授权人信息已更新");
            emit("update");
          }
        } catch (err) {
          console.error("保存被授权人信息失败:", JSON.stringify(err, null, 2));
          const errorMessage = (err == null ? void 0 : err.message) || (err instanceof Error ? err.message : "未知错误");
          error("保存失败", errorMessage);
        } finally {
          saving.value = false;
        }
      });
    };
    const createUploadHandler = (qualKey) => {
      return async (options) => {
        const { file, onSuccess, onError } = options;
        try {
          const response = await companyApi.uploadQualification(
            props.companyId,
            qualKey,
            file,
            {}
          );
          if (response.success) {
            success("上传成功", "附件上传成功");
            loadAttachments();
            emit("update");
            onSuccess(response);
          } else {
            throw new Error(response.error || "上传失败");
          }
        } catch (err) {
          console.error("上传附件失败:", JSON.stringify(err, null, 2));
          const errorMsg = (err == null ? void 0 : err.message) || (err instanceof Error ? err.message : "未知错误");
          error("上传失败", errorMsg);
          onError(err);
        }
      };
    };
    const downloadAttachment = (type) => {
      window.open(`/api/companies/${props.companyId}/qualifications/${type}/download`);
    };
    const deleteAttachment = async (type) => {
      if (!confirm("确定要删除此附件吗？")) return;
      try {
        const response = await fetch(`/api/companies/${props.companyId}/qualifications/${type}`, {
          method: "DELETE"
        });
        if (!response.ok) throw new Error("删除失败");
        success("删除成功", "附件已删除");
        loadAttachments();
        emit("update");
      } catch (err) {
        console.error("删除附件失败:", JSON.stringify(err, null, 2));
        const errorMsg = (err == null ? void 0 : err.message) || (err instanceof Error ? err.message : "未知错误");
        error("删除失败", errorMsg);
      }
    };
    const loadAttachments = async () => {
      try {
        const response = await companyApi.getCompanyQualifications(props.companyId);
        if (response.success && response.data) {
          const data = response.data;
          attachments.value = {
            auth_id_front: data.auth_id_front ? { name: data.auth_id_front.original_filename } : null,
            auth_id_back: data.auth_id_back ? { name: data.auth_id_back.original_filename } : null,
            manager_resume: data.manager_resume ? { name: data.manager_resume.original_filename } : null,
            social_security: data.social_security ? { name: data.social_security.original_filename } : null
          };
        }
      } catch (err) {
        console.error("加载附件失败:", JSON.stringify(err, null, 2));
      }
    };
    onMounted(() => {
      loadAttachments();
    });
    return (_ctx, _cache) => {
      const _component_el_input = ElInput;
      const _component_el_form_item = ElFormItem;
      const _component_el_col = ElCol;
      const _component_el_row = ElRow;
      const _component_el_option = ElOption;
      const _component_el_select = ElSelect;
      const _component_el_input_number = ElInputNumber;
      const _component_el_icon = ElIcon;
      const _component_el_button = ElButton;
      const _component_el_form = ElForm;
      return openBlock(), createElementBlock("div", _hoisted_1$2, [
        createVNode(unref(Card), { title: "被授权人基本信息" }, {
          default: withCtx(() => [
            createVNode(_component_el_form, {
              ref_key: "formRef",
              ref: formRef,
              model: formData.value,
              rules: formRules,
              "label-width": "140px",
              class: "personnel-form"
            }, {
              default: withCtx(() => [
                createVNode(_component_el_row, { gutter: 20 }, {
                  default: withCtx(() => [
                    createVNode(_component_el_col, { span: 12 }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, {
                          label: "姓名",
                          prop: "authorized_person_name"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: formData.value.authorized_person_name,
                              "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => formData.value.authorized_person_name = $event),
                              placeholder: "请输入被授权人姓名"
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
                          label: "身份证号",
                          prop: "authorized_person_id"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: formData.value.authorized_person_id,
                              "onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => formData.value.authorized_person_id = $event),
                              placeholder: "请输入身份证号",
                              maxlength: "18"
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
                          label: "性别",
                          prop: "authorized_person_gender"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_select, {
                              modelValue: formData.value.authorized_person_gender,
                              "onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => formData.value.authorized_person_gender = $event),
                              placeholder: "请选择性别",
                              style: { "width": "100%" }
                            }, {
                              default: withCtx(() => [
                                createVNode(_component_el_option, {
                                  label: "男",
                                  value: "男"
                                }),
                                createVNode(_component_el_option, {
                                  label: "女",
                                  value: "女"
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
                          label: "年龄",
                          prop: "authorized_person_age"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input_number, {
                              modelValue: formData.value.authorized_person_age,
                              "onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => formData.value.authorized_person_age = $event),
                              min: 18,
                              max: 100,
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
                    createVNode(_component_el_col, { span: 12 }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, {
                          label: "职位",
                          prop: "authorized_person_position"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: formData.value.authorized_person_position,
                              "onUpdate:modelValue": _cache[4] || (_cache[4] = ($event) => formData.value.authorized_person_position = $event),
                              placeholder: "请输入职位"
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
                          prop: "authorized_person_title"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: formData.value.authorized_person_title,
                              "onUpdate:modelValue": _cache[5] || (_cache[5] = ($event) => formData.value.authorized_person_title = $event),
                              placeholder: "请输入职称"
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
                createVNode(_component_el_row, null, {
                  default: withCtx(() => [
                    createVNode(_component_el_col, { span: 24 }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, null, {
                          default: withCtx(() => [
                            createVNode(_component_el_button, {
                              type: "primary",
                              loading: saving.value,
                              onClick: handleSave
                            }, {
                              default: withCtx(() => [
                                createVNode(_component_el_icon, null, {
                                  default: withCtx(() => [
                                    createVNode(unref(select_default))
                                  ]),
                                  _: 1
                                }),
                                _cache[14] || (_cache[14] = createTextVNode(" 保存被授权人信息 ", -1))
                              ]),
                              _: 1
                            }, 8, ["loading"])
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
            }, 8, ["model"])
          ]),
          _: 1
        }),
        createVNode(unref(Card), {
          title: "相关附件",
          class: "mt-4"
        }, {
          default: withCtx(() => [
            createBaseVNode("div", _hoisted_2$2, [
              createBaseVNode("div", _hoisted_3$2, [
                createBaseVNode("div", _hoisted_4$2, [
                  createVNode(_component_el_icon, { class: "icon" }, {
                    default: withCtx(() => [
                      createVNode(unref(credit_card_default))
                    ]),
                    _: 1
                  }),
                  _cache[15] || (_cache[15] = createBaseVNode("span", { class: "title" }, "被授权人身份证（正面）", -1))
                ]),
                attachments.value.auth_id_front ? (openBlock(), createElementBlock("div", _hoisted_5$1, [
                  createVNode(_component_el_icon, { class: "file-icon" }, {
                    default: withCtx(() => [
                      createVNode(unref(document_default))
                    ]),
                    _: 1
                  }),
                  createBaseVNode("span", _hoisted_6$1, toDisplayString(attachments.value.auth_id_front.name), 1),
                  createBaseVNode("div", _hoisted_7$1, [
                    createVNode(_component_el_button, {
                      text: "",
                      type: "primary",
                      size: "small",
                      onClick: _cache[6] || (_cache[6] = ($event) => downloadAttachment("auth_id_front"))
                    }, {
                      default: withCtx(() => [
                        createVNode(_component_el_icon, null, {
                          default: withCtx(() => [
                            createVNode(unref(download_default))
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    createVNode(_component_el_button, {
                      text: "",
                      type: "danger",
                      size: "small",
                      onClick: _cache[7] || (_cache[7] = ($event) => deleteAttachment("auth_id_front"))
                    }, {
                      default: withCtx(() => [
                        createVNode(_component_el_icon, null, {
                          default: withCtx(() => [
                            createVNode(unref(delete_default))
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    })
                  ])
                ])) : (openBlock(), createElementBlock("div", _hoisted_8$1, "未上传")),
                createVNode(unref(DocumentUploader), {
                  accept: ".jpg,.jpeg,.png,.pdf",
                  "show-file-list": false,
                  "http-request": createUploadHandler("auth_id_front"),
                  "auto-compress-image": true,
                  "image-type": "id_card",
                  "max-size": 10
                }, {
                  trigger: withCtx(() => [
                    createVNode(_component_el_button, { size: "small" }, {
                      default: withCtx(() => [
                        createVNode(_component_el_icon, null, {
                          default: withCtx(() => [
                            createVNode(unref(upload_default))
                          ]),
                          _: 1
                        }),
                        _cache[16] || (_cache[16] = createTextVNode(" 上传文件 ", -1))
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                }, 8, ["http-request"])
              ]),
              createBaseVNode("div", _hoisted_9, [
                createBaseVNode("div", _hoisted_10, [
                  createVNode(_component_el_icon, { class: "icon" }, {
                    default: withCtx(() => [
                      createVNode(unref(credit_card_default))
                    ]),
                    _: 1
                  }),
                  _cache[17] || (_cache[17] = createBaseVNode("span", { class: "title" }, "被授权人身份证（反面）", -1))
                ]),
                attachments.value.auth_id_back ? (openBlock(), createElementBlock("div", _hoisted_11, [
                  createVNode(_component_el_icon, { class: "file-icon" }, {
                    default: withCtx(() => [
                      createVNode(unref(document_default))
                    ]),
                    _: 1
                  }),
                  createBaseVNode("span", _hoisted_12, toDisplayString(attachments.value.auth_id_back.name), 1),
                  createBaseVNode("div", _hoisted_13, [
                    createVNode(_component_el_button, {
                      text: "",
                      type: "primary",
                      size: "small",
                      onClick: _cache[8] || (_cache[8] = ($event) => downloadAttachment("auth_id_back"))
                    }, {
                      default: withCtx(() => [
                        createVNode(_component_el_icon, null, {
                          default: withCtx(() => [
                            createVNode(unref(download_default))
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    createVNode(_component_el_button, {
                      text: "",
                      type: "danger",
                      size: "small",
                      onClick: _cache[9] || (_cache[9] = ($event) => deleteAttachment("auth_id_back"))
                    }, {
                      default: withCtx(() => [
                        createVNode(_component_el_icon, null, {
                          default: withCtx(() => [
                            createVNode(unref(delete_default))
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    })
                  ])
                ])) : (openBlock(), createElementBlock("div", _hoisted_14, "未上传")),
                createVNode(unref(DocumentUploader), {
                  accept: ".jpg,.jpeg,.png,.pdf",
                  "show-file-list": false,
                  "http-request": createUploadHandler("auth_id_back"),
                  "auto-compress-image": true,
                  "image-type": "id_card",
                  "max-size": 10
                }, {
                  trigger: withCtx(() => [
                    createVNode(_component_el_button, { size: "small" }, {
                      default: withCtx(() => [
                        createVNode(_component_el_icon, null, {
                          default: withCtx(() => [
                            createVNode(unref(upload_default))
                          ]),
                          _: 1
                        }),
                        _cache[18] || (_cache[18] = createTextVNode(" 上传文件 ", -1))
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                }, 8, ["http-request"])
              ]),
              createBaseVNode("div", _hoisted_15, [
                createBaseVNode("div", _hoisted_16, [
                  createVNode(_component_el_icon, { class: "icon" }, {
                    default: withCtx(() => [
                      createVNode(unref(user_default))
                    ]),
                    _: 1
                  }),
                  _cache[19] || (_cache[19] = createBaseVNode("span", { class: "title" }, "项目经理简历", -1))
                ]),
                attachments.value.manager_resume ? (openBlock(), createElementBlock("div", _hoisted_17, [
                  createVNode(_component_el_icon, { class: "file-icon" }, {
                    default: withCtx(() => [
                      createVNode(unref(document_default))
                    ]),
                    _: 1
                  }),
                  createBaseVNode("span", _hoisted_18, toDisplayString(attachments.value.manager_resume.name), 1),
                  createBaseVNode("div", _hoisted_19, [
                    createVNode(_component_el_button, {
                      text: "",
                      type: "primary",
                      size: "small",
                      onClick: _cache[10] || (_cache[10] = ($event) => downloadAttachment("manager_resume"))
                    }, {
                      default: withCtx(() => [
                        createVNode(_component_el_icon, null, {
                          default: withCtx(() => [
                            createVNode(unref(download_default))
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    createVNode(_component_el_button, {
                      text: "",
                      type: "danger",
                      size: "small",
                      onClick: _cache[11] || (_cache[11] = ($event) => deleteAttachment("manager_resume"))
                    }, {
                      default: withCtx(() => [
                        createVNode(_component_el_icon, null, {
                          default: withCtx(() => [
                            createVNode(unref(delete_default))
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    })
                  ])
                ])) : (openBlock(), createElementBlock("div", _hoisted_20, "未上传")),
                createVNode(unref(DocumentUploader), {
                  accept: ".pdf,.doc,.docx",
                  "show-file-list": false,
                  "http-request": createUploadHandler("manager_resume"),
                  "auto-compress-image": false,
                  "max-size": 20
                }, {
                  trigger: withCtx(() => [
                    createVNode(_component_el_button, { size: "small" }, {
                      default: withCtx(() => [
                        createVNode(_component_el_icon, null, {
                          default: withCtx(() => [
                            createVNode(unref(upload_default))
                          ]),
                          _: 1
                        }),
                        _cache[20] || (_cache[20] = createTextVNode(" 上传文件 ", -1))
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                }, 8, ["http-request"])
              ]),
              createBaseVNode("div", _hoisted_21, [
                createBaseVNode("div", _hoisted_22, [
                  createVNode(_component_el_icon, { class: "icon" }, {
                    default: withCtx(() => [
                      createVNode(unref(document_checked_default))
                    ]),
                    _: 1
                  }),
                  _cache[21] || (_cache[21] = createBaseVNode("span", { class: "title" }, "社保证明", -1))
                ]),
                attachments.value.social_security ? (openBlock(), createElementBlock("div", _hoisted_23, [
                  createVNode(_component_el_icon, { class: "file-icon" }, {
                    default: withCtx(() => [
                      createVNode(unref(document_default))
                    ]),
                    _: 1
                  }),
                  createBaseVNode("span", _hoisted_24, toDisplayString(attachments.value.social_security.name), 1),
                  createBaseVNode("div", _hoisted_25, [
                    createVNode(_component_el_button, {
                      text: "",
                      type: "primary",
                      size: "small",
                      onClick: _cache[12] || (_cache[12] = ($event) => downloadAttachment("social_security"))
                    }, {
                      default: withCtx(() => [
                        createVNode(_component_el_icon, null, {
                          default: withCtx(() => [
                            createVNode(unref(download_default))
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    createVNode(_component_el_button, {
                      text: "",
                      type: "danger",
                      size: "small",
                      onClick: _cache[13] || (_cache[13] = ($event) => deleteAttachment("social_security"))
                    }, {
                      default: withCtx(() => [
                        createVNode(_component_el_icon, null, {
                          default: withCtx(() => [
                            createVNode(unref(delete_default))
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    })
                  ])
                ])) : (openBlock(), createElementBlock("div", _hoisted_26, "未上传")),
                createVNode(unref(DocumentUploader), {
                  accept: ".pdf,.jpg,.jpeg,.png",
                  "show-file-list": false,
                  "http-request": createUploadHandler("social_security"),
                  "auto-compress-image": true,
                  "image-type": "default",
                  "max-size": 20
                }, {
                  trigger: withCtx(() => [
                    createVNode(_component_el_button, { size: "small" }, {
                      default: withCtx(() => [
                        createVNode(_component_el_icon, null, {
                          default: withCtx(() => [
                            createVNode(unref(upload_default))
                          ]),
                          _: 1
                        }),
                        _cache[22] || (_cache[22] = createTextVNode(" 上传文件 ", -1))
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                }, 8, ["http-request"])
              ])
            ])
          ]),
          _: 1
        })
      ]);
    };
  }
});
const PersonnelTab = /* @__PURE__ */ _export_sfc(_sfc_main$2, [["__scopeId", "data-v-bc10a0da"]]);
const _hoisted_1$1 = { class: "financial-tab" };
const _hoisted_2$1 = { class: "shareholders-section" };
const _hoisted_3$1 = { class: "section-header" };
const _hoisted_4$1 = { class: "save-section" };
const _sfc_main$1 = /* @__PURE__ */ defineComponent({
  __name: "FinancialTab",
  props: {
    companyId: {},
    companyData: {}
  },
  emits: ["update"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const { success, error } = useNotification();
    const bankFormRef = ref();
    const equityFormRef = ref();
    const managementFormRef = ref();
    const shareholderFormRef = ref();
    const saving = ref(false);
    const loading = ref(false);
    const financialQualifications = ref([
      {
        key: "audit_report",
        name: "财务审计报告",
        icon: document_default,
        required: false,
        allowMultiple: true
      },
      {
        key: "taxpayer_certificate",
        name: "纳税人资格证明",
        icon: tickets_default,
        required: false,
        allowMultiple: false
      }
    ]);
    const qualificationFiles = ref({});
    const bankForm = ref({
      bank_name: "",
      bank_account: ""
    });
    const equityForm = ref({
      actual_controller: "",
      controlling_shareholder: ""
    });
    const managementForm = ref({
      managing_unit_name: "",
      managed_unit_name: ""
    });
    const shareholders = ref([]);
    const controllingShareholderIndex = ref(-1);
    const actualControllerIndex = ref(-1);
    const shareholderDialogVisible = ref(false);
    const editingIndex = ref(-1);
    const shareholderForm = ref({
      name: "",
      type: "",
      ratio: ""
    });
    const shareholderRules = {
      name: [{ required: true, message: "请输入股东名称", trigger: "blur" }],
      type: [{ required: true, message: "请选择类型", trigger: "change" }],
      ratio: [{ required: true, message: "请输入出资比例", trigger: "blur" }]
    };
    watch(
      () => props.companyData,
      (newData) => {
        if (newData) {
          bankForm.value = {
            bank_name: newData.bank_name || "",
            bank_account: newData.bank_account || ""
          };
          equityForm.value = {
            actual_controller: newData.actual_controller || "",
            controlling_shareholder: newData.controlling_shareholder || ""
          };
          managementForm.value = {
            managing_unit_name: newData.managing_unit_name || "",
            managed_unit_name: newData.managed_unit_name || ""
          };
          try {
            const shareholdersInfo = newData.shareholders_info;
            if (shareholdersInfo) {
              shareholders.value = typeof shareholdersInfo === "string" ? JSON.parse(shareholdersInfo) : shareholdersInfo;
              controllingShareholderIndex.value = shareholders.value.findIndex(
                (s) => s.is_controlling === true
              );
              actualControllerIndex.value = shareholders.value.findIndex(
                (s) => s.is_actual_controller === true
              );
            } else {
              shareholders.value = [];
              controllingShareholderIndex.value = -1;
              actualControllerIndex.value = -1;
            }
          } catch (err) {
            console.error("解析股东信息失败:", err);
            shareholders.value = [];
            controllingShareholderIndex.value = -1;
            actualControllerIndex.value = -1;
          }
        }
      },
      { immediate: true, deep: true }
    );
    const showAddShareholderDialog = () => {
      editingIndex.value = -1;
      shareholderForm.value = {
        name: "",
        type: "",
        ratio: ""
      };
      shareholderDialogVisible.value = true;
    };
    const handleEditShareholder = (index) => {
      editingIndex.value = index;
      const shareholder = shareholders.value[index];
      shareholderForm.value = {
        name: shareholder.name,
        type: shareholder.type,
        ratio: shareholder.ratio
      };
      shareholderDialogVisible.value = true;
    };
    const handleDeleteShareholder = (index) => {
      if (confirm("确定要删除此股东吗？")) {
        if (index === controllingShareholderIndex.value) {
          controllingShareholderIndex.value = -1;
        }
        if (index === actualControllerIndex.value) {
          actualControllerIndex.value = -1;
        }
        shareholders.value.splice(index, 1);
        if (index < controllingShareholderIndex.value) {
          controllingShareholderIndex.value--;
        }
        if (index < actualControllerIndex.value) {
          actualControllerIndex.value--;
        }
        success("删除成功", "股东已删除，请点击保存按钮保存更改");
      }
    };
    const handleControllingShareholderChange = () => {
      shareholders.value.forEach((s) => {
        s.is_controlling = false;
      });
      if (controllingShareholderIndex.value !== -1) {
        shareholders.value[controllingShareholderIndex.value].is_controlling = true;
      }
    };
    const handleActualControllerChange = () => {
      shareholders.value.forEach((s) => {
        s.is_actual_controller = false;
      });
      if (actualControllerIndex.value !== -1) {
        shareholders.value[actualControllerIndex.value].is_actual_controller = true;
      }
    };
    const handleConfirmShareholder = async () => {
      if (!shareholderFormRef.value) return;
      await shareholderFormRef.value.validate((valid) => {
        if (!valid) return;
        if (editingIndex.value === -1) {
          shareholders.value.push({
            ...shareholderForm.value,
            is_controlling: false,
            // 🆕 默认不是控股股东
            is_actual_controller: false
            // 🆕 默认不是实际控制人
          });
          success("添加成功", "股东已添加，请点击保存按钮保存更改");
        } else {
          const existingShareholder = shareholders.value[editingIndex.value];
          shareholders.value[editingIndex.value] = {
            ...shareholderForm.value,
            is_controlling: existingShareholder.is_controlling || false,
            is_actual_controller: existingShareholder.is_actual_controller || false
          };
          success("编辑成功", "股东信息已更新，请点击保存按钮保存更改");
        }
        shareholderDialogVisible.value = false;
      });
    };
    const loadQualifications = async () => {
      try {
        loading.value = true;
        const response = await companyApi.getCompanyQualifications(props.companyId);
        if (response.success) {
          qualificationFiles.value = response.data || {};
        }
      } catch (err) {
        console.error("加载资质文件失败:", err);
      } finally {
        loading.value = false;
      }
    };
    const handleUploadFile = async (qualKey, file) => {
      try {
        const qualification = financialQualifications.value.find((q) => q.key === qualKey);
        let fileVersion = null;
        if (qualification == null ? void 0 : qualification.allowMultiple) {
          fileVersion = prompt(`请输入 "${file.name}" 的年份:
例如：2023、2024`);
          if (fileVersion === null) {
            return;
          }
          if (!fileVersion.trim()) {
            error("上传失败", "年份不能为空");
            return;
          }
        }
        const formData = new FormData();
        formData.append(`qualifications[${qualKey}]`, file);
        formData.append("qualification_names", JSON.stringify({ [qualKey]: (qualification == null ? void 0 : qualification.name) || qualKey }));
        if (fileVersion) {
          formData.append("file_versions", JSON.stringify({ [qualKey]: fileVersion.trim() }));
        }
        const response = await fetch(`/api/companies/${props.companyId}/qualifications/upload`, {
          method: "POST",
          body: formData,
          credentials: "include",
          // 包含cookies进行认证
          headers: {
            // 注意：不要设置 Content-Type，让浏览器自动设置multipart/form-data边界
          }
        });
        if (!response.ok) {
          const contentType = response.headers.get("content-type");
          if (contentType && contentType.includes("application/json")) {
            const errorData = await response.json();
            throw new Error(errorData.error || `服务器错误: ${response.status}`);
          } else {
            throw new Error(`上传失败: 服务器返回错误 ${response.status}`);
          }
        }
        const result = await response.json();
        if (result.success) {
          success("上传成功", `${(qualification == null ? void 0 : qualification.name) || "资质文件"}上传成功`);
          await loadQualifications();
          emit("update");
        } else {
          throw new Error(result.error || "上传失败");
        }
      } catch (err) {
        console.error("上传资质文件失败:", err);
        error("上传失败", err instanceof Error ? err.message : "未知错误");
      }
    };
    const handleDownloadFile = async (qualKey, qualId) => {
      try {
        let url;
        if (qualId) {
          url = `/api/qualifications/${qualId}/download`;
        } else {
          url = `/api/companies/${props.companyId}/qualifications/${qualKey}/download`;
        }
        window.open(url, "_blank");
      } catch (err) {
        console.error("下载资质文件失败:", err);
        error("下载失败", err instanceof Error ? err.message : "未知错误");
      }
    };
    const handleDeleteFile = async (qualKey, qualId) => {
      try {
        if (!confirm("确定要删除此资质文件吗？")) {
          return;
        }
        if (qualId) {
          await companyApi.deleteQualification(qualId);
        } else {
          const response = await fetch(`/api/companies/${props.companyId}/qualifications/${qualKey}`, {
            method: "DELETE",
            credentials: "include"
            // 包含cookies进行认证
          });
          if (!response.ok) throw new Error("删除失败");
        }
        success("删除成功", "资质文件已删除");
        await loadQualifications();
        emit("update");
      } catch (err) {
        console.error("删除资质文件失败:", err);
        error("删除失败", err instanceof Error ? err.message : "未知错误");
      }
    };
    const handleSaveAll = async () => {
      saving.value = true;
      try {
        const response = await companyApi.updateCompany(props.companyId, {
          // 银行信息
          bank_name: bankForm.value.bank_name,
          bank_account: bankForm.value.bank_account,
          // 股权结构
          actual_controller: equityForm.value.actual_controller,
          controlling_shareholder: equityForm.value.controlling_shareholder,
          shareholders_info: JSON.stringify(shareholders.value),
          // 管理关系
          managing_unit_name: managementForm.value.managing_unit_name,
          managed_unit_name: managementForm.value.managed_unit_name
        });
        if (response.success) {
          success("保存成功", "财务信息已更新");
          emit("update");
        }
      } catch (err) {
        console.error("保存财务信息失败:", err);
        error("保存失败", err instanceof Error ? err.message : "未知错误");
      } finally {
        saving.value = false;
      }
    };
    onMounted(() => {
      loadQualifications();
    });
    return (_ctx, _cache) => {
      const _component_el_col = ElCol;
      const _component_el_row = ElRow;
      const _component_el_input = ElInput;
      const _component_el_form_item = ElFormItem;
      const _component_el_form = ElForm;
      const _component_el_icon = ElIcon;
      const _component_el_button = ElButton;
      const _component_el_table_column = ElTableColumn;
      const _component_el_radio = ElRadio;
      const _component_el_table = ElTable;
      const _component_el_empty = ElEmpty;
      const _component_el_option = ElOption;
      const _component_el_select = ElSelect;
      const _component_el_dialog = ElDialog;
      return openBlock(), createElementBlock("div", _hoisted_1$1, [
        createVNode(unref(Card), {
          title: "财务资质文件",
          class: "mb-4"
        }, {
          default: withCtx(() => [
            createVNode(_component_el_row, { gutter: 20 }, {
              default: withCtx(() => [
                (openBlock(true), createElementBlock(Fragment, null, renderList(financialQualifications.value, (qualification) => {
                  return openBlock(), createBlock(_component_el_col, {
                    key: qualification.key,
                    span: 12
                  }, {
                    default: withCtx(() => [
                      createVNode(QualificationCard, {
                        qualification,
                        "file-info": qualificationFiles.value[qualification.key],
                        onUpload: ($event) => handleUploadFile(qualification.key, $event),
                        onDownload: handleDownloadFile,
                        onDelete: handleDeleteFile
                      }, null, 8, ["qualification", "file-info", "onUpload"])
                    ]),
                    _: 2
                  }, 1024);
                }), 128))
              ]),
              _: 1
            })
          ]),
          _: 1
        }),
        createVNode(unref(Card), { title: "银行账户信息" }, {
          default: withCtx(() => [
            createVNode(_component_el_form, {
              ref_key: "bankFormRef",
              ref: bankFormRef,
              model: bankForm.value,
              "label-width": "140px",
              class: "bank-form"
            }, {
              default: withCtx(() => [
                createVNode(_component_el_row, { gutter: 20 }, {
                  default: withCtx(() => [
                    createVNode(_component_el_col, { span: 12 }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, { label: "开户行全称" }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: bankForm.value.bank_name,
                              "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => bankForm.value.bank_name = $event),
                              placeholder: "请输入开户行全称"
                            }, null, 8, ["modelValue"])
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    createVNode(_component_el_col, { span: 12 }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, { label: "银行账号" }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: bankForm.value.bank_account,
                              "onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => bankForm.value.bank_account = $event),
                              placeholder: "请输入银行账号"
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
            }, 8, ["model"])
          ]),
          _: 1
        }),
        createVNode(unref(Card), {
          title: "股权结构信息",
          class: "mt-4"
        }, {
          default: withCtx(() => [
            createVNode(_component_el_form, {
              ref_key: "equityFormRef",
              ref: equityFormRef,
              model: equityForm.value,
              "label-width": "140px",
              class: "equity-form"
            }, {
              default: withCtx(() => [
                createVNode(_component_el_row, { gutter: 20 }, {
                  default: withCtx(() => [
                    createVNode(_component_el_col, { span: 12 }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, { label: "实际控制人" }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: equityForm.value.actual_controller,
                              "onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => equityForm.value.actual_controller = $event),
                              placeholder: "请输入实际控制人"
                            }, null, 8, ["modelValue"])
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    createVNode(_component_el_col, { span: 12 }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, { label: "控股股东" }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: equityForm.value.controlling_shareholder,
                              "onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => equityForm.value.controlling_shareholder = $event),
                              placeholder: "请输入控股股东"
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
            }, 8, ["model"]),
            createBaseVNode("div", _hoisted_2$1, [
              createBaseVNode("div", _hoisted_3$1, [
                _cache[14] || (_cache[14] = createBaseVNode("h6", null, "股东/投资人列表", -1)),
                createVNode(_component_el_button, {
                  type: "primary",
                  size: "small",
                  onClick: showAddShareholderDialog
                }, {
                  default: withCtx(() => [
                    createVNode(_component_el_icon, null, {
                      default: withCtx(() => [
                        createVNode(unref(plus_default))
                      ]),
                      _: 1
                    }),
                    _cache[13] || (_cache[13] = createTextVNode(" 添加股东 ", -1))
                  ]),
                  _: 1
                })
              ]),
              shareholders.value.length > 0 ? (openBlock(), createBlock(_component_el_table, {
                key: 0,
                data: shareholders.value,
                stripe: ""
              }, {
                default: withCtx(() => [
                  createVNode(_component_el_table_column, {
                    prop: "name",
                    label: "股东名称",
                    "min-width": "150"
                  }),
                  createVNode(_component_el_table_column, {
                    prop: "type",
                    label: "类型",
                    width: "100"
                  }),
                  createVNode(_component_el_table_column, {
                    prop: "ratio",
                    label: "出资比例",
                    width: "120"
                  }),
                  createVNode(_component_el_table_column, {
                    label: "控股股东",
                    width: "100",
                    align: "center"
                  }, {
                    default: withCtx(({ $index }) => [
                      createVNode(_component_el_radio, {
                        modelValue: controllingShareholderIndex.value,
                        "onUpdate:modelValue": _cache[4] || (_cache[4] = ($event) => controllingShareholderIndex.value = $event),
                        label: $index,
                        onChange: handleControllingShareholderChange
                      }, {
                        default: withCtx(() => [..._cache[15] || (_cache[15] = [
                          createBaseVNode("span", null, null, -1)
                        ])]),
                        _: 1
                      }, 8, ["modelValue", "label"])
                    ]),
                    _: 1
                  }),
                  createVNode(_component_el_table_column, {
                    label: "实际控制人",
                    width: "110",
                    align: "center"
                  }, {
                    default: withCtx(({ $index }) => [
                      createVNode(_component_el_radio, {
                        modelValue: actualControllerIndex.value,
                        "onUpdate:modelValue": _cache[5] || (_cache[5] = ($event) => actualControllerIndex.value = $event),
                        label: $index,
                        onChange: handleActualControllerChange
                      }, {
                        default: withCtx(() => [..._cache[16] || (_cache[16] = [
                          createBaseVNode("span", null, null, -1)
                        ])]),
                        _: 1
                      }, 8, ["modelValue", "label"])
                    ]),
                    _: 1
                  }),
                  createVNode(_component_el_table_column, {
                    label: "操作",
                    width: "150"
                  }, {
                    default: withCtx(({ row, $index }) => [
                      createVNode(_component_el_button, {
                        text: "",
                        type: "primary",
                        size: "small",
                        onClick: ($event) => handleEditShareholder($index)
                      }, {
                        default: withCtx(() => [..._cache[17] || (_cache[17] = [
                          createTextVNode(" 编辑 ", -1)
                        ])]),
                        _: 1
                      }, 8, ["onClick"]),
                      createVNode(_component_el_button, {
                        text: "",
                        type: "danger",
                        size: "small",
                        onClick: ($event) => handleDeleteShareholder($index)
                      }, {
                        default: withCtx(() => [..._cache[18] || (_cache[18] = [
                          createTextVNode(" 删除 ", -1)
                        ])]),
                        _: 1
                      }, 8, ["onClick"])
                    ]),
                    _: 1
                  })
                ]),
                _: 1
              }, 8, ["data"])) : (openBlock(), createBlock(_component_el_empty, {
                key: 1,
                description: "暂无股东信息",
                "image-size": 100
              }))
            ])
          ]),
          _: 1
        }),
        createVNode(unref(Card), {
          title: "管理关系信息",
          class: "mt-4"
        }, {
          default: withCtx(() => [
            createVNode(_component_el_form, {
              ref_key: "managementFormRef",
              ref: managementFormRef,
              model: managementForm.value,
              "label-width": "140px",
              class: "management-form"
            }, {
              default: withCtx(() => [
                createVNode(_component_el_row, { gutter: 20 }, {
                  default: withCtx(() => [
                    createVNode(_component_el_col, { span: 12 }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, { label: "管理单位名称" }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: managementForm.value.managing_unit_name,
                              "onUpdate:modelValue": _cache[6] || (_cache[6] = ($event) => managementForm.value.managing_unit_name = $event),
                              placeholder: "如有管理单位请输入"
                            }, null, 8, ["modelValue"])
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    createVNode(_component_el_col, { span: 12 }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, { label: "被管理单位名称" }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: managementForm.value.managed_unit_name,
                              "onUpdate:modelValue": _cache[7] || (_cache[7] = ($event) => managementForm.value.managed_unit_name = $event),
                              placeholder: "如有被管理单位请输入"
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
            }, 8, ["model"])
          ]),
          _: 1
        }),
        createBaseVNode("div", _hoisted_4$1, [
          createVNode(_component_el_button, {
            type: "primary",
            size: "large",
            loading: saving.value,
            onClick: handleSaveAll
          }, {
            default: withCtx(() => [
              createVNode(_component_el_icon, null, {
                default: withCtx(() => [
                  createVNode(unref(select_default))
                ]),
                _: 1
              }),
              _cache[19] || (_cache[19] = createTextVNode(" 保存财务信息 ", -1))
            ]),
            _: 1
          }, 8, ["loading"])
        ]),
        createVNode(_component_el_dialog, {
          modelValue: shareholderDialogVisible.value,
          "onUpdate:modelValue": _cache[12] || (_cache[12] = ($event) => shareholderDialogVisible.value = $event),
          title: editingIndex.value === -1 ? "添加股东" : "编辑股东",
          width: "500px"
        }, {
          footer: withCtx(() => [
            createVNode(_component_el_button, {
              onClick: _cache[11] || (_cache[11] = ($event) => shareholderDialogVisible.value = false)
            }, {
              default: withCtx(() => [..._cache[20] || (_cache[20] = [
                createTextVNode("取消", -1)
              ])]),
              _: 1
            }),
            createVNode(_component_el_button, {
              type: "primary",
              onClick: handleConfirmShareholder
            }, {
              default: withCtx(() => [..._cache[21] || (_cache[21] = [
                createTextVNode("确定", -1)
              ])]),
              _: 1
            })
          ]),
          default: withCtx(() => [
            createVNode(_component_el_form, {
              ref_key: "shareholderFormRef",
              ref: shareholderFormRef,
              model: shareholderForm.value,
              rules: shareholderRules,
              "label-width": "100px"
            }, {
              default: withCtx(() => [
                createVNode(_component_el_form_item, {
                  label: "股东名称",
                  prop: "name"
                }, {
                  default: withCtx(() => [
                    createVNode(_component_el_input, {
                      modelValue: shareholderForm.value.name,
                      "onUpdate:modelValue": _cache[8] || (_cache[8] = ($event) => shareholderForm.value.name = $event),
                      placeholder: "请输入股东名称"
                    }, null, 8, ["modelValue"])
                  ]),
                  _: 1
                }),
                createVNode(_component_el_form_item, {
                  label: "类型",
                  prop: "type"
                }, {
                  default: withCtx(() => [
                    createVNode(_component_el_select, {
                      modelValue: shareholderForm.value.type,
                      "onUpdate:modelValue": _cache[9] || (_cache[9] = ($event) => shareholderForm.value.type = $event),
                      placeholder: "请选择类型",
                      style: { "width": "100%" }
                    }, {
                      default: withCtx(() => [
                        createVNode(_component_el_option, {
                          label: "企业",
                          value: "企业"
                        }),
                        createVNode(_component_el_option, {
                          label: "自然人",
                          value: "自然人"
                        })
                      ]),
                      _: 1
                    }, 8, ["modelValue"])
                  ]),
                  _: 1
                }),
                createVNode(_component_el_form_item, {
                  label: "出资比例",
                  prop: "ratio"
                }, {
                  default: withCtx(() => [
                    createVNode(_component_el_input, {
                      modelValue: shareholderForm.value.ratio,
                      "onUpdate:modelValue": _cache[10] || (_cache[10] = ($event) => shareholderForm.value.ratio = $event),
                      placeholder: "如：30%"
                    }, null, 8, ["modelValue"])
                  ]),
                  _: 1
                })
              ]),
              _: 1
            }, 8, ["model"])
          ]),
          _: 1
        }, 8, ["modelValue", "title"])
      ]);
    };
  }
});
const FinancialTab = /* @__PURE__ */ _export_sfc(_sfc_main$1, [["__scopeId", "data-v-5b1f60f2"]]);
const _hoisted_1 = { class: "company-detail" };
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
  __name: "CompanyDetail",
  setup(__props) {
    const route = useRoute();
    const router = useRouter();
    const { error } = useNotification();
    const loading = ref(false);
    const activeTab = ref("basic");
    const companyId = ref(0);
    const companyData = ref({});
    const industryMap = {
      technology: "科技",
      manufacturing: "制造业",
      finance: "金融",
      education: "教育",
      healthcare: "医疗",
      retail: "零售",
      construction: "建筑",
      other: "其他"
    };
    const getIndustryLabel = (industryType) => {
      return industryMap[industryType] || industryType;
    };
    const loadCompanyData = async () => {
      loading.value = true;
      try {
        const response = await companyApi.getCompany(companyId.value);
        if (response.success && response.data) {
          companyData.value = response.data;
        } else {
          error("加载失败", "无法获取企业信息");
          handleBack();
        }
      } catch (err) {
        console.error("加载企业数据失败:", err);
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
      await loadCompanyData();
    };
    const handleBack = () => {
      router.push("/knowledge/company-library");
    };
    onMounted(() => {
      const id = route.params.id;
      if (id) {
        companyId.value = parseInt(id, 10);
        if (isNaN(companyId.value)) {
          error("参数错误", "无效的企业ID");
          handleBack();
          return;
        }
        loadCompanyData();
      } else {
        error("参数错误", "缺少企业ID");
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
            createBaseVNode("h2", null, toDisplayString(companyData.value.company_name || "企业详情"), 1),
            companyData.value.industry_type ? (openBlock(), createBlock(_component_el_tag, {
              key: 0,
              type: "info"
            }, {
              default: withCtx(() => [
                createTextVNode(toDisplayString(getIndustryLabel(companyData.value.industry_type)), 1)
              ]),
              _: 1
            })) : createCommentVNode("", true)
          ])
        ]),
        loading.value ? (openBlock(), createBlock(unref(Loading), {
          key: 0,
          text: "加载企业信息中..."
        })) : (openBlock(), createElementBlock("div", _hoisted_4, [
          createVNode(_component_el_tabs, {
            modelValue: activeTab.value,
            "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => activeTab.value = $event),
            class: "company-tabs",
            onTabChange: handleTabChange
          }, {
            default: withCtx(() => [
              createVNode(_component_el_tab_pane, { name: "basic" }, {
                label: withCtx(() => [
                  createBaseVNode("span", _hoisted_5, [
                    createVNode(_component_el_icon, null, {
                      default: withCtx(() => [
                        createVNode(unref(office_building_default))
                      ]),
                      _: 1
                    }),
                    _cache[2] || (_cache[2] = createTextVNode(" 基础信息 ", -1))
                  ])
                ]),
                default: withCtx(() => [
                  createVNode(BasicInfoTab, {
                    "company-id": companyId.value,
                    "company-data": companyData.value,
                    onUpdate: handleDataUpdate
                  }, null, 8, ["company-id", "company-data"])
                ]),
                _: 1
              }),
              createVNode(_component_el_tab_pane, { name: "qualification" }, {
                label: withCtx(() => [
                  createBaseVNode("span", _hoisted_6, [
                    createVNode(_component_el_icon, null, {
                      default: withCtx(() => [
                        createVNode(unref(medal_default))
                      ]),
                      _: 1
                    }),
                    _cache[3] || (_cache[3] = createTextVNode(" 资质信息 ", -1))
                  ])
                ]),
                default: withCtx(() => [
                  createVNode(QualificationTab, {
                    "company-id": companyId.value,
                    "company-data": companyData.value,
                    onUpdate: handleDataUpdate
                  }, null, 8, ["company-id", "company-data"])
                ]),
                _: 1
              }),
              createVNode(_component_el_tab_pane, { name: "personnel" }, {
                label: withCtx(() => [
                  createBaseVNode("span", _hoisted_7, [
                    createVNode(_component_el_icon, null, {
                      default: withCtx(() => [
                        createVNode(unref(user_default))
                      ]),
                      _: 1
                    }),
                    _cache[4] || (_cache[4] = createTextVNode(" 被授权人信息 ", -1))
                  ])
                ]),
                default: withCtx(() => [
                  createVNode(PersonnelTab, {
                    "company-id": companyId.value,
                    "company-data": companyData.value,
                    onUpdate: handleDataUpdate
                  }, null, 8, ["company-id", "company-data"])
                ]),
                _: 1
              }),
              createVNode(_component_el_tab_pane, { name: "financial" }, {
                label: withCtx(() => [
                  createBaseVNode("span", _hoisted_8, [
                    createVNode(_component_el_icon, null, {
                      default: withCtx(() => [
                        createVNode(unref(wallet_default))
                      ]),
                      _: 1
                    }),
                    _cache[5] || (_cache[5] = createTextVNode(" 财务信息 ", -1))
                  ])
                ]),
                default: withCtx(() => [
                  createVNode(FinancialTab, {
                    "company-id": companyId.value,
                    "company-data": companyData.value,
                    onUpdate: handleDataUpdate
                  }, null, 8, ["company-id", "company-data"])
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
const CompanyDetail = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-8d9df7e4"]]);
export {
  CompanyDetail as default
};
