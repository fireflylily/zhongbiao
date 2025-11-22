import { d as defineComponent, r as ref, D as watch, S as onMounted, e as createElementBlock, o as openBlock, f as createVNode, as as ElCard, w as withCtx, q as ElForm, ak as ElRow, ai as ElCol, s as ElFormItem, Y as ElSelect, F as Fragment, V as renderList, k as createBlock, W as ElOption, y as ElInput, v as ElRadioGroup, x as ElRadio, p as createTextVNode, b9 as ElDatePicker, a6 as ElDivider, g as ElButton, n as createBaseVNode, h as unref, ad as ElIcon, ah as resolveDynamicComponent, X as ElTag, t as toDisplayString, l as createCommentVNode, aE as download_default, bc as delete_default, aF as upload_default, j as ElDialog, at as ElUpload, aR as upload_filled_default, bb as files_default, bm as picture_default, bh as tickets_default, ba as select_default, ae as document_default, u as useRoute, M as useRouter } from "./vendor-MtO928VE.js";
import { L as Loading } from "./Loading-D6Ei-uTU.js";
/* empty css                                                                           */
/* empty css                                                                         */
import { a as useNotification, _ as _export_sfc } from "./index.js";
import { a as formatFileSize, f as formatDate, k as knowledgeApi } from "./formatters-DrGE7noj.js";
import { E as Empty } from "./Empty-CMm3i0ir.js";
import { s as smartCompressImage } from "./imageCompressor-DC3BCfPz.js";
import { c as companyApi } from "./company-z4Xg082l.js";
const _hoisted_1$1 = { class: "case-basic-info-tab" };
const _hoisted_2$1 = { class: "card-header" };
const _hoisted_3$1 = {
  key: 2,
  class: "attachments-grid"
};
const _hoisted_4$1 = { class: "attachment-header" };
const _hoisted_5 = { class: "attachment-body" };
const _hoisted_6 = ["title"];
const _hoisted_7 = { class: "file-info" };
const _hoisted_8 = { class: "file-size" };
const _hoisted_9 = { class: "file-date" };
const _hoisted_10 = {
  key: 0,
  class: "file-desc"
};
const _hoisted_11 = { class: "attachment-actions" };
const _sfc_main$1 = /* @__PURE__ */ defineComponent({
  __name: "CaseBasicInfoTab",
  props: {
    caseId: {},
    caseData: {}
  },
  emits: ["update"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const { success, error } = useNotification();
    const formRef = ref();
    const saving = ref(false);
    const companies = ref([]);
    const formData = ref({
      company_id: null,
      case_title: "",
      case_number: "",
      customer_name: "",
      product_category: "",
      industry: "金融",
      contract_type: "合同",
      final_customer_name: "",
      contract_amount: "",
      contract_start_date: "",
      contract_end_date: "",
      party_a_contact_name: "",
      party_a_contact_phone: "",
      party_a_contact_email: ""
    });
    const formRules = {
      company_id: [
        { required: true, message: "请选择所属企业", trigger: "change" }
      ],
      case_title: [
        { required: true, message: "请输入案例标题", trigger: "blur" }
      ],
      customer_name: [
        { required: true, message: "请输入客户名称", trigger: "blur" }
      ],
      contract_type: [
        { required: true, message: "请选择合同类型", trigger: "change" }
      ]
    };
    const loading = ref(false);
    const attachments = ref([]);
    const uploadDialogVisible = ref(false);
    const uploading = ref(false);
    const uploadFormRef = ref();
    const uploadRef = ref();
    const uploadFileList = ref([]);
    const uploadForm = ref({
      attachment_type: "contract",
      description: "",
      file: null
    });
    const uploadFormRules = {
      attachment_type: [
        { required: true, message: "请选择附件类型", trigger: "change" }
      ]
    };
    watch(
      () => props.caseData,
      (newData) => {
        if (newData) {
          formData.value = {
            company_id: newData.company_id || null,
            case_title: newData.case_title || "",
            case_number: newData.case_number || "",
            customer_name: newData.customer_name || "",
            product_category: newData.product_category || "",
            industry: newData.industry || "金融",
            contract_type: newData.contract_type || "合同",
            final_customer_name: newData.final_customer_name || "",
            contract_amount: newData.contract_amount || "",
            contract_start_date: newData.contract_start_date || "",
            contract_end_date: newData.contract_end_date || "",
            party_a_contact_name: newData.party_a_contact_name || "",
            party_a_contact_phone: newData.party_a_contact_phone || "",
            party_a_contact_email: newData.party_a_contact_email || ""
          };
        }
      },
      { immediate: true, deep: true }
    );
    const loadCompanies = async () => {
      try {
        const response = await companyApi.getCompanies();
        if (response.success && response.data) {
          companies.value = response.data;
        }
      } catch (err) {
        console.error("加载企业列表失败:", err);
      }
    };
    const handleSave = async () => {
      if (!formRef.value) return;
      await formRef.value.validate(async (valid) => {
        if (!valid) return;
        saving.value = true;
        try {
          const response = await knowledgeApi.updateCase(props.caseId, formData.value);
          if (response.success) {
            success("保存成功", "案例信息已更新");
            emit("update");
          } else {
            error("保存失败", response.error || "未知错误");
          }
        } catch (err) {
          console.error("保存案例信息失败:", err);
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
    const getAttachmentIcon = (type) => {
      switch (type) {
        case "contract":
          return document_default;
        case "acceptance":
          return select_default;
        case "testimony":
          return tickets_default;
        case "photo":
          return picture_default;
        default:
          return files_default;
      }
    };
    const getAttachmentColor = (type) => {
      switch (type) {
        case "contract":
          return "#409eff";
        case "acceptance":
          return "#67c23a";
        case "testimony":
          return "#e6a23c";
        case "photo":
          return "#f56c6c";
        default:
          return "#909399";
      }
    };
    const getAttachmentTagType = (type) => {
      switch (type) {
        case "contract":
          return "primary";
        case "acceptance":
          return "success";
        case "testimony":
          return "warning";
        case "photo":
          return "danger";
        default:
          return "info";
      }
    };
    const getAttachmentLabel = (type) => {
      switch (type) {
        case "contract":
          return "合同文件";
        case "acceptance":
          return "验收证明";
        case "testimony":
          return "客户证明";
        case "photo":
          return "项目照片";
        default:
          return "其他材料";
      }
    };
    const loadAttachments = async () => {
      loading.value = true;
      try {
        const response = await knowledgeApi.getCaseAttachments(props.caseId);
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
        const maxSize = 20 * 1024 * 1024;
        if (uploadFile.raw.size > maxSize) {
          error("文件过大", "文件大小不能超过20MB");
          uploadFileList.value = [];
          uploadForm.value.file = null;
          return;
        }
        uploadForm.value.file = uploadFile.raw;
      }
    };
    const handleFileRemove = () => {
      uploadForm.value.file = null;
    };
    const handleUpload = () => {
      uploadDialogVisible.value = true;
    };
    const handleConfirmUpload = async () => {
      if (!uploadFormRef.value) return;
      await uploadFormRef.value.validate(async (valid) => {
        if (!valid) return;
        if (!uploadForm.value.file) {
          error("请选择文件", "请先选择要上传的文件");
          return;
        }
        uploading.value = true;
        try {
          let fileToUpload = uploadForm.value.file;
          if (fileToUpload.type.startsWith("image/")) {
            const imageType = uploadForm.value.attachment_type === "photo" ? "photo" : "default";
            fileToUpload = await smartCompressImage(fileToUpload, imageType);
            console.log("[CaseBasicInfo] 图片已压缩");
          }
          const response = await knowledgeApi.uploadCaseAttachment(
            props.caseId,
            fileToUpload,
            uploadForm.value.attachment_type,
            uploadForm.value.description || void 0
          );
          if (response.success) {
            success("上传成功", "附件已上传");
            uploadDialogVisible.value = false;
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
    const handleUploadDialogClose = () => {
      var _a;
      uploadFileList.value = [];
      uploadForm.value = {
        attachment_type: "contract",
        description: "",
        file: null
      };
      (_a = uploadFormRef.value) == null ? void 0 : _a.resetFields();
    };
    const handleDownload = (attachment) => {
      const url = knowledgeApi.downloadCaseAttachment(attachment.attachment_id);
      window.open(url, "_blank");
    };
    const handleDelete = async (attachment) => {
      try {
        if (!confirm(`确定要删除附件 "${attachment.original_filename}" 吗？`)) {
          return;
        }
        const response = await knowledgeApi.deleteCaseAttachment(attachment.attachment_id);
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
      loadCompanies();
      loadAttachments();
    });
    return (_ctx, _cache) => {
      const _component_el_option = ElOption;
      const _component_el_select = ElSelect;
      const _component_el_form_item = ElFormItem;
      const _component_el_col = ElCol;
      const _component_el_row = ElRow;
      const _component_el_input = ElInput;
      const _component_el_radio = ElRadio;
      const _component_el_radio_group = ElRadioGroup;
      const _component_el_date_picker = ElDatePicker;
      const _component_el_divider = ElDivider;
      const _component_el_button = ElButton;
      const _component_el_form = ElForm;
      const _component_el_card = ElCard;
      const _component_el_icon = ElIcon;
      const _component_el_tag = ElTag;
      const _component_el_upload = ElUpload;
      const _component_el_dialog = ElDialog;
      return openBlock(), createElementBlock("div", _hoisted_1$1, [
        createVNode(_component_el_card, { style: { "margin-bottom": "20px" } }, {
          header: withCtx(() => [..._cache[19] || (_cache[19] = [
            createBaseVNode("span", null, "案例基本信息", -1)
          ])]),
          default: withCtx(() => [
            createVNode(_component_el_form, {
              ref_key: "formRef",
              ref: formRef,
              model: formData.value,
              rules: formRules,
              "label-width": "140px"
            }, {
              default: withCtx(() => [
                createVNode(_component_el_row, { gutter: 20 }, {
                  default: withCtx(() => [
                    createVNode(_component_el_col, { span: 12 }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, {
                          label: "所属企业",
                          prop: "company_id"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_select, {
                              modelValue: formData.value.company_id,
                              "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => formData.value.company_id = $event),
                              placeholder: "请选择企业",
                              filterable: "",
                              style: { "width": "100%" }
                            }, {
                              default: withCtx(() => [
                                (openBlock(true), createElementBlock(Fragment, null, renderList(companies.value, (company) => {
                                  return openBlock(), createBlock(_component_el_option, {
                                    key: company.company_id,
                                    label: company.company_name,
                                    value: company.company_id
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
                    })
                  ]),
                  _: 1
                }),
                createVNode(_component_el_row, { gutter: 20 }, {
                  default: withCtx(() => [
                    createVNode(_component_el_col, { span: 12 }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, {
                          label: "案例标题",
                          prop: "case_title"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: formData.value.case_title,
                              "onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => formData.value.case_title = $event),
                              placeholder: "请输入案例标题/合同名称"
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
                          label: "案例编号",
                          prop: "case_number"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: formData.value.case_number,
                              "onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => formData.value.case_number = $event),
                              placeholder: "请输入案例编号（可选）"
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
                          label: "客户名称",
                          prop: "customer_name"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: formData.value.customer_name,
                              "onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => formData.value.customer_name = $event),
                              placeholder: "请输入甲方客户名称"
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
                          label: "产品分类",
                          prop: "product_category"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_select, {
                              modelValue: formData.value.product_category,
                              "onUpdate:modelValue": _cache[4] || (_cache[4] = ($event) => formData.value.product_category = $event),
                              placeholder: "请选择产品分类",
                              clearable: "",
                              style: { "width": "100%" }
                            }, {
                              default: withCtx(() => [
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
                          label: "所属行业",
                          prop: "industry"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_select, {
                              modelValue: formData.value.industry,
                              "onUpdate:modelValue": _cache[5] || (_cache[5] = ($event) => formData.value.industry = $event),
                              placeholder: "请选择行业",
                              clearable: "",
                              style: { "width": "100%" }
                            }, {
                              default: withCtx(() => [
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
                        })
                      ]),
                      _: 1
                    }),
                    createVNode(_component_el_col, { span: 12 }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, {
                          label: "合同类型",
                          prop: "contract_type"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_radio_group, {
                              modelValue: formData.value.contract_type,
                              "onUpdate:modelValue": _cache[6] || (_cache[6] = ($event) => formData.value.contract_type = $event)
                            }, {
                              default: withCtx(() => [
                                createVNode(_component_el_radio, { label: "合同" }, {
                                  default: withCtx(() => [..._cache[20] || (_cache[20] = [
                                    createTextVNode("合同", -1)
                                  ])]),
                                  _: 1
                                }),
                                createVNode(_component_el_radio, { label: "订单" }, {
                                  default: withCtx(() => [..._cache[21] || (_cache[21] = [
                                    createTextVNode("订单", -1)
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
                          label: "合同金额",
                          prop: "contract_amount"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: formData.value.contract_amount,
                              "onUpdate:modelValue": _cache[7] || (_cache[7] = ($event) => formData.value.contract_amount = $event),
                              placeholder: "如：100万元、百万级"
                            }, {
                              append: withCtx(() => [..._cache[22] || (_cache[22] = [
                                createTextVNode("元", -1)
                              ])]),
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
                          label: "最终客户",
                          prop: "final_customer_name"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: formData.value.final_customer_name,
                              "onUpdate:modelValue": _cache[8] || (_cache[8] = ($event) => formData.value.final_customer_name = $event),
                              placeholder: "订单类型时填写最终客户",
                              disabled: formData.value.contract_type !== "订单"
                            }, null, 8, ["modelValue", "disabled"])
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    createVNode(_component_el_col, { span: 12 }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, {
                          label: "合同开始日期",
                          prop: "contract_start_date"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_date_picker, {
                              modelValue: formData.value.contract_start_date,
                              "onUpdate:modelValue": _cache[9] || (_cache[9] = ($event) => formData.value.contract_start_date = $event),
                              type: "date",
                              placeholder: "选择开始日期",
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
                    createVNode(_component_el_col, { span: 12 }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, {
                          label: "合同结束日期",
                          prop: "contract_end_date"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_date_picker, {
                              modelValue: formData.value.contract_end_date,
                              "onUpdate:modelValue": _cache[10] || (_cache[10] = ($event) => formData.value.contract_end_date = $event),
                              type: "date",
                              placeholder: "选择结束日期",
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
                createVNode(_component_el_divider, { "content-position": "left" }, {
                  default: withCtx(() => [..._cache[23] || (_cache[23] = [
                    createTextVNode("客户联系方式", -1)
                  ])]),
                  _: 1
                }),
                createVNode(_component_el_row, { gutter: 20 }, {
                  default: withCtx(() => [
                    createVNode(_component_el_col, { span: 8 }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, {
                          label: "联系人姓名",
                          prop: "party_a_contact_name"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: formData.value.party_a_contact_name,
                              "onUpdate:modelValue": _cache[11] || (_cache[11] = ($event) => formData.value.party_a_contact_name = $event),
                              placeholder: "联系人"
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
                          label: "联系电话",
                          prop: "party_a_contact_phone"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: formData.value.party_a_contact_phone,
                              "onUpdate:modelValue": _cache[12] || (_cache[12] = ($event) => formData.value.party_a_contact_phone = $event),
                              placeholder: "联系电话"
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
                          label: "联系邮箱",
                          prop: "party_a_contact_email"
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: formData.value.party_a_contact_email,
                              "onUpdate:modelValue": _cache[13] || (_cache[13] = ($event) => formData.value.party_a_contact_email = $event),
                              placeholder: "邮箱地址"
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
                      default: withCtx(() => [..._cache[24] || (_cache[24] = [
                        createTextVNode(" 保存 ", -1)
                      ])]),
                      _: 1
                    }, 8, ["loading"]),
                    createVNode(_component_el_button, { onClick: handleReset }, {
                      default: withCtx(() => [..._cache[25] || (_cache[25] = [
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
        }),
        createVNode(_component_el_card, null, {
          header: withCtx(() => [
            createBaseVNode("div", _hoisted_2$1, [
              _cache[27] || (_cache[27] = createBaseVNode("span", null, "案例附件", -1)),
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
                  _cache[26] || (_cache[26] = createTextVNode(" 上传附件 ", -1))
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
                      color: getAttachmentColor(attachment.attachment_type)
                    }, {
                      default: withCtx(() => [
                        (openBlock(), createBlock(resolveDynamicComponent(getAttachmentIcon(attachment.attachment_type))))
                      ]),
                      _: 2
                    }, 1032, ["color"]),
                    createVNode(_component_el_tag, {
                      type: getAttachmentTagType(attachment.attachment_type),
                      size: "small"
                    }, {
                      default: withCtx(() => [
                        createTextVNode(toDisplayString(getAttachmentLabel(attachment.attachment_type)), 1)
                      ]),
                      _: 2
                    }, 1032, ["type"])
                  ]),
                  createBaseVNode("div", _hoisted_5, [
                    createBaseVNode("div", {
                      class: "file-name",
                      title: attachment.original_filename
                    }, toDisplayString(attachment.original_filename), 9, _hoisted_6),
                    createBaseVNode("div", _hoisted_7, [
                      createBaseVNode("span", _hoisted_8, toDisplayString(unref(formatFileSize)(attachment.file_size)), 1),
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
                        _cache[28] || (_cache[28] = createTextVNode(" 下载 ", -1))
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
                        _cache[29] || (_cache[29] = createTextVNode(" 删除 ", -1))
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
          "onUpdate:modelValue": _cache[18] || (_cache[18] = ($event) => uploadDialogVisible.value = $event),
          title: "上传案例附件",
          width: "500px",
          onClose: handleUploadDialogClose
        }, {
          footer: withCtx(() => [
            createVNode(_component_el_button, {
              onClick: _cache[17] || (_cache[17] = ($event) => uploadDialogVisible.value = false)
            }, {
              default: withCtx(() => [..._cache[32] || (_cache[32] = [
                createTextVNode("取消", -1)
              ])]),
              _: 1
            }),
            createVNode(_component_el_button, {
              type: "primary",
              loading: uploading.value,
              onClick: handleConfirmUpload
            }, {
              default: withCtx(() => [..._cache[33] || (_cache[33] = [
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
                  prop: "attachment_type"
                }, {
                  default: withCtx(() => [
                    createVNode(_component_el_select, {
                      modelValue: uploadForm.value.attachment_type,
                      "onUpdate:modelValue": _cache[14] || (_cache[14] = ($event) => uploadForm.value.attachment_type = $event),
                      placeholder: "请选择附件类型",
                      style: { "width": "100%" }
                    }, {
                      default: withCtx(() => [
                        createVNode(_component_el_option, {
                          label: "合同文件",
                          value: "contract"
                        }),
                        createVNode(_component_el_option, {
                          label: "验收证明",
                          value: "acceptance"
                        }),
                        createVNode(_component_el_option, {
                          label: "客户证明",
                          value: "testimony"
                        }),
                        createVNode(_component_el_option, {
                          label: "项目照片",
                          value: "photo"
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
                      "onUpdate:modelValue": _cache[15] || (_cache[15] = ($event) => uploadForm.value.description = $event),
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
                      "file-list": uploadFileList.value,
                      "onUpdate:fileList": _cache[16] || (_cache[16] = ($event) => uploadFileList.value = $event),
                      "auto-upload": false,
                      limit: 1,
                      "on-change": handleFileChange,
                      "on-remove": handleFileRemove,
                      accept: ".pdf,.doc,.docx,.jpg,.jpeg,.png",
                      drag: ""
                    }, {
                      tip: withCtx(() => [..._cache[30] || (_cache[30] = [
                        createBaseVNode("div", { class: "el-upload__tip" }, " 支持PDF、DOC、DOCX、JPG、PNG格式，文件大小不超过20MB ", -1)
                      ])]),
                      default: withCtx(() => [
                        createVNode(_component_el_icon, { class: "el-icon--upload" }, {
                          default: withCtx(() => [
                            createVNode(unref(upload_filled_default))
                          ]),
                          _: 1
                        }),
                        _cache[31] || (_cache[31] = createBaseVNode("div", { class: "el-upload__text" }, [
                          createTextVNode(" 拖拽文件到这里 或 "),
                          createBaseVNode("em", null, "点击上传")
                        ], -1))
                      ]),
                      _: 1
                    }, 8, ["file-list"])
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
const CaseBasicInfoTab = /* @__PURE__ */ _export_sfc(_sfc_main$1, [["__scopeId", "data-v-e9280fb1"]]);
const _hoisted_1 = { class: "case-detail" };
const _hoisted_2 = { class: "detail-header" };
const _hoisted_3 = { class: "header-title" };
const _hoisted_4 = {
  key: 1,
  class: "detail-content"
};
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "CaseDetail",
  setup(__props) {
    const route = useRoute();
    const router = useRouter();
    const { error } = useNotification();
    const loading = ref(false);
    const caseId = ref(0);
    const caseData = ref({});
    const loadCaseData = async () => {
      loading.value = true;
      try {
        const response = await knowledgeApi.getCase(caseId.value);
        if (response.success && response.data) {
          caseData.value = response.data;
        } else {
          error("加载失败", "无法获取案例信息");
          handleBack();
        }
      } catch (err) {
        console.error("加载案例数据失败:", err);
        error("加载失败", err instanceof Error ? err.message : "未知错误");
        handleBack();
      } finally {
        loading.value = false;
      }
    };
    const handleDataUpdate = async () => {
      await loadCaseData();
    };
    const handleBack = () => {
      router.push("/knowledge/case-library");
    };
    onMounted(() => {
      const id = route.params.id;
      if (id) {
        caseId.value = parseInt(id, 10);
        if (isNaN(caseId.value)) {
          error("参数错误", "无效的案例ID");
          handleBack();
          return;
        }
        loadCaseData();
      } else {
        error("参数错误", "缺少案例ID");
        handleBack();
      }
    });
    return (_ctx, _cache) => {
      const _component_el_button = ElButton;
      const _component_el_tag = ElTag;
      return openBlock(), createElementBlock("div", _hoisted_1, [
        createBaseVNode("div", _hoisted_2, [
          createVNode(_component_el_button, {
            onClick: handleBack,
            icon: "ArrowLeft"
          }, {
            default: withCtx(() => [..._cache[0] || (_cache[0] = [
              createTextVNode("返回列表", -1)
            ])]),
            _: 1
          }),
          createBaseVNode("div", _hoisted_3, [
            createBaseVNode("h2", null, toDisplayString(caseData.value.case_title || "案例详情"), 1),
            caseData.value.contract_type ? (openBlock(), createBlock(_component_el_tag, {
              key: 0,
              type: caseData.value.contract_type === "合同" ? "primary" : "success"
            }, {
              default: withCtx(() => [
                createTextVNode(toDisplayString(caseData.value.contract_type), 1)
              ]),
              _: 1
            }, 8, ["type"])) : createCommentVNode("", true),
            caseData.value.product_category ? (openBlock(), createBlock(_component_el_tag, {
              key: 1,
              type: "primary"
            }, {
              default: withCtx(() => [
                createTextVNode(toDisplayString(caseData.value.product_category), 1)
              ]),
              _: 1
            })) : createCommentVNode("", true)
          ])
        ]),
        loading.value ? (openBlock(), createBlock(unref(Loading), {
          key: 0,
          text: "加载案例信息中..."
        })) : (openBlock(), createElementBlock("div", _hoisted_4, [
          createVNode(CaseBasicInfoTab, {
            "case-id": caseId.value,
            "case-data": caseData.value,
            onUpdate: handleDataUpdate
          }, null, 8, ["case-id", "case-data"])
        ]))
      ]);
    };
  }
});
const CaseDetail = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-ea362180"]]);
export {
  CaseDetail as default
};
