import { d as defineComponent, r as ref, c as computed, S as onMounted, e as createElementBlock, o as openBlock, k as createBlock, b4 as ElSkeleton, F as Fragment, n as createBaseVNode, l as createCommentVNode, p as createTextVNode, U as normalizeClass, t as toDisplayString, f as createVNode, w as withCtx, g as ElButton, m as ElAlert, X as ElTag, P as ElCheckbox, V as renderList, y as ElInput, aL as ElProgress, ay as ElDescriptions, az as ElDescriptionsItem, b5 as ElResult, a as axios, A as ElMessage, z as ElMessageBox, u as useRoute, M as useRouter, h as unref, Y as ElSelect, W as ElOption, ar as ElEmpty, as as ElCard } from "./vendor-MtO928VE.js";
import { L as Loading } from "./Loading-75jVWA4c.js";
/* empty css                                                                           */
import { P as PageHeader } from "./PageHeader-BhFuSmcR.js";
/* empty css                                                                         */
import { _ as _export_sfc } from "./index.js";
import { u as useProjectDocuments } from "./useProjectDocuments-CobiuthK.js";
import { u as useProjectStore } from "./project-X4Kuz_iO.js";
import "./tender-DvsgeLWX.js";
const _hoisted_1$1 = { class: "document-merge-panel" };
const _hoisted_2$1 = { class: "merge-section" };
const _hoisted_3$1 = { class: "files-status" };
const _hoisted_4$1 = { class: "status-icon" };
const _hoisted_5$1 = {
  key: 0,
  class: "bi bi-check-circle-fill text-success"
};
const _hoisted_6$1 = {
  key: 1,
  class: "bi bi-x-circle-fill text-danger"
};
const _hoisted_7$1 = { class: "file-info" };
const _hoisted_8$1 = { class: "file-name" };
const _hoisted_9 = { class: "file-meta" };
const _hoisted_10 = {
  key: 1,
  class: "text-muted"
};
const _hoisted_11 = {
  key: 0,
  class: "file-actions"
};
const _hoisted_12 = { class: "status-icon" };
const _hoisted_13 = {
  key: 0,
  class: "bi bi-check-circle-fill text-success"
};
const _hoisted_14 = {
  key: 1,
  class: "bi bi-dash-circle text-warning"
};
const _hoisted_15 = { class: "file-info" };
const _hoisted_16 = { class: "file-name" };
const _hoisted_17 = { class: "file-meta" };
const _hoisted_18 = {
  key: 1,
  class: "text-muted"
};
const _hoisted_19 = {
  key: 0,
  class: "file-actions"
};
const _hoisted_20 = { class: "status-icon" };
const _hoisted_21 = {
  key: 0,
  class: "bi bi-check-circle-fill text-success"
};
const _hoisted_22 = {
  key: 1,
  class: "bi bi-x-circle-fill text-danger"
};
const _hoisted_23 = { class: "file-info" };
const _hoisted_24 = { class: "file-name" };
const _hoisted_25 = { class: "file-meta" };
const _hoisted_26 = {
  key: 1,
  class: "text-muted"
};
const _hoisted_27 = {
  key: 0,
  class: "file-actions"
};
const _hoisted_28 = { key: 0 };
const _hoisted_29 = { key: 1 };
const _hoisted_30 = {
  key: 0,
  class: "merge-section"
};
const _hoisted_31 = { class: "config-group" };
const _hoisted_32 = { class: "doc-order-list" };
const _hoisted_33 = { class: "doc-order-item fixed" };
const _hoisted_34 = {
  key: 0,
  class: "doc-order-item"
};
const _hoisted_35 = { class: "doc-order-item" };
const _hoisted_36 = { class: "order-number" };
const _hoisted_37 = { class: "config-group" };
const _hoisted_38 = { class: "options-list" };
const _hoisted_39 = { class: "config-group" };
const _hoisted_40 = { class: "index-template-preview" };
const _hoisted_41 = { class: "score-items-preview" };
const _hoisted_42 = { class: "config-group" };
const _hoisted_43 = {
  key: 1,
  class: "merge-section"
};
const _hoisted_44 = {
  key: 0,
  class: "action-area"
};
const _hoisted_45 = {
  key: 1,
  class: "merge-progress"
};
const _hoisted_46 = { class: "progress-message" };
const _hoisted_47 = { class: "progress-details" };
const _hoisted_48 = {
  key: 0,
  class: "current"
};
const _hoisted_49 = {
  key: 2,
  class: "merge-result"
};
const _hoisted_50 = { class: "result-info" };
const _hoisted_51 = { class: "stats-list" };
const _hoisted_52 = { key: 0 };
const _hoisted_53 = { key: 1 };
const _hoisted_54 = { key: 2 };
const _hoisted_55 = { class: "processing-details" };
const _hoisted_56 = { key: 0 };
const _hoisted_57 = { key: 1 };
const _hoisted_58 = { key: 2 };
const _hoisted_59 = { key: 3 };
const _hoisted_60 = { class: "action-buttons" };
const _sfc_main$1 = /* @__PURE__ */ defineComponent({
  __name: "DocumentMergePanel",
  props: {
    projectId: {},
    currentDocuments: {}
  },
  setup(__props) {
    const props = __props;
    const loading = ref(true);
    const files = ref({});
    const indexRequirement = ref({ required: false, type: "none" });
    const mergeConfig = ref({
      include_p2p: true,
      doc_order: ["business", "p2p", "tech"],
      generate_toc: true,
      remove_blanks: true,
      unify_styles: true,
      add_section_breaks: true,
      output_filename: ""
    });
    const merging = ref(false);
    const starting = ref(false);
    const mergeProgress = ref(0);
    const mergeStatus = ref("");
    const mergeMessage = ref("");
    const currentStep = ref("");
    const completedSteps = ref([]);
    const mergeResult = ref(null);
    const indexEnabled = ref(true);
    const canMerge = computed(() => {
      return files.value.business && files.value.tech;
    });
    const loadMergeConfig = async () => {
      var _a, _b, _c, _d, _e, _f;
      try {
        loading.value = true;
        if (props.currentDocuments) {
          console.log("[DocumentMergePanel] 使用父组件传递的文档:", props.currentDocuments);
          const docs = props.currentDocuments;
          files.value = {};
          if (docs.businessResponseFile) {
            files.value.business = {
              status: "ready",
              file_path: docs.businessResponseFile.outputFile,
              file_name: ((_a = docs.businessResponseFile.outputFile) == null ? void 0 : _a.split("/").pop()) || "商务应答文件.docx",
              file_size: ((_b = docs.businessResponseFile.stats) == null ? void 0 : _b.file_size) || 0
            };
          }
          if (docs.p2pResponseFile) {
            files.value.p2p = {
              status: "ready",
              file_path: docs.p2pResponseFile.outputFile,
              file_name: ((_c = docs.p2pResponseFile.outputFile) == null ? void 0 : _c.split("/").pop()) || "点对点应答文件.docx",
              file_size: ((_d = docs.p2pResponseFile.stats) == null ? void 0 : _d.file_size) || 0
            };
          }
          if (docs.techProposalFile) {
            files.value.tech = {
              status: "ready",
              file_path: docs.techProposalFile.outputFile,
              file_name: ((_e = docs.techProposalFile.outputFile) == null ? void 0 : _e.split("/").pop()) || "技术方案文件.docx",
              file_size: ((_f = docs.techProposalFile.stats) == null ? void 0 : _f.file_size) || 0
            };
          }
          console.log("[DocumentMergePanel] 构建的文件信息:", files.value);
          mergeConfig.value = {
            include_p2p: !!files.value.p2p,
            doc_order: files.value.p2p ? ["business", "p2p", "tech"] : ["business", "tech"],
            generate_toc: true,
            remove_blanks: true,
            unify_styles: true,
            add_section_breaks: true,
            output_filename: `项目${props.projectId}_最终标书`
          };
          loading.value = false;
          return;
        }
        const response = await axios.get(`/api/projects/${props.projectId}/merge-config`);
        console.log("[DocumentMergePanel] API配置响应:", response.data);
        if (response.data.success) {
          const data = response.data.data;
          files.value = data.files || {};
          indexRequirement.value = data.index_requirement || { required: false, type: "none" };
          if (data.default_config) {
            mergeConfig.value = { ...data.default_config };
          }
        }
      } catch (error) {
        console.error("[DocumentMergePanel] 加载整合配置失败:", error);
        ElMessage.error("加载配置失败");
      } finally {
        loading.value = false;
      }
    };
    const startMerge = async () => {
      var _a, _b;
      try {
        starting.value = true;
        const file_paths = {
          business: files.value.business.file_path,
          tech: files.value.tech.file_path
        };
        if (mergeConfig.value.include_p2p && files.value.p2p) {
          file_paths.p2p = files.value.p2p.file_path;
        }
        const response = await axios.post(
          `/api/projects/${props.projectId}/merge-documents`,
          {
            file_paths,
            config: {
              ...mergeConfig.value,
              index_config: indexRequirement.value
            }
          }
        );
        if (response.data.success) {
          const taskId = response.data.task_id || props.projectId;
          console.log("[DocumentMergePanel] 整合任务已启动，task_id:", taskId);
          merging.value = true;
          starting.value = false;
          watchMergeProgress(taskId);
        }
      } catch (error) {
        console.error("启动整合失败:", error);
        ElMessage.error(((_b = (_a = error.response) == null ? void 0 : _a.data) == null ? void 0 : _b.error) || "启动整合失败");
        starting.value = false;
      }
    };
    const watchMergeProgress = (taskId) => {
      const eventSource = new EventSource(`/api/merge-status/${taskId}`);
      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          mergeProgress.value = data.progress_percentage || 0;
          mergeMessage.value = data.current_step || "";
          if (data.current_step && !completedSteps.value.includes(data.current_step)) {
            if (currentStep.value) {
              completedSteps.value.push(currentStep.value);
            }
            currentStep.value = data.current_step;
          }
          if (data.overall_status === "completed") {
            mergeStatus.value = "success";
            mergeProgress.value = 100;
            if (data.options) {
              const options = typeof data.options === "string" ? JSON.parse(data.options) : data.options;
              mergeResult.value = {
                filename: mergeConfig.value.output_filename + ".docx",
                file_path: options.merged_document_path,
                file_size: options.file_size || 0,
                stats: options.stats,
                created_at: (/* @__PURE__ */ new Date()).toLocaleString("zh-CN")
              };
            }
            merging.value = false;
            eventSource.close();
            ElMessage.success("文档整合完成！");
          } else if (data.overall_status === "failed") {
            mergeStatus.value = "exception";
            merging.value = false;
            eventSource.close();
            ElMessage.error("文档整合失败：" + data.current_step);
          }
        } catch (e) {
          console.error("解析进度数据失败:", e);
        }
      };
      eventSource.onerror = () => {
        eventSource.close();
        if (merging.value) {
          ElMessage.error("进度监听中断");
          merging.value = false;
        }
      };
    };
    const resetMerge = () => {
      ElMessageBox.confirm("确定要重新整合吗？", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      }).then(() => {
        mergeResult.value = null;
        mergeProgress.value = 0;
        mergeStatus.value = "";
        mergeMessage.value = "";
        currentStep.value = "";
        completedSteps.value = [];
      }).catch(() => {
      });
    };
    const convertToApiUrl = (filePath) => {
      if (!filePath) return "";
      if (filePath.startsWith("/api/")) {
        return filePath;
      }
      let apiPath = filePath;
      const absolutePrefix = "/Users/lvhe/Downloads/zhongbiao/zhongbiao/";
      if (apiPath.startsWith(absolutePrefix)) {
        apiPath = apiPath.substring(absolutePrefix.length);
      }
      if (apiPath.startsWith("ai_tender_system/data/")) {
        apiPath = apiPath.substring("ai_tender_system/data/".length);
      } else if (apiPath.startsWith("data/")) {
        apiPath = apiPath.substring("data/".length);
      }
      return `/api/files/serve/${apiPath}`;
    };
    const downloadMergedFile = () => {
      var _a;
      if ((_a = mergeResult.value) == null ? void 0 : _a.file_path) {
        const downloadUrl = convertToApiUrl(mergeResult.value.file_path) + "?download=true";
        console.log("[DocumentMergePanel] 下载URL:", downloadUrl);
        window.open(downloadUrl, "_blank");
      }
    };
    const previewMergedFile = () => {
      var _a;
      if ((_a = mergeResult.value) == null ? void 0 : _a.file_path) {
        const previewUrl = convertToApiUrl(mergeResult.value.file_path);
        console.log("[DocumentMergePanel] 预览URL:", previewUrl);
        window.open(previewUrl, "_blank");
      }
    };
    const editMergedFile = () => {
      var _a;
      if ((_a = mergeResult.value) == null ? void 0 : _a.file_path) {
        ElMessage.success("正在打开编辑器...");
        ElMessage.info("编辑功能开发中...");
      }
    };
    const handlePreviewFile = (type) => {
      const file = files.value[type];
      if (file == null ? void 0 : file.file_path) {
        const previewUrl = convertToApiUrl(file.file_path);
        console.log("[DocumentMergePanel] 预览文件:", previewUrl);
        window.open(previewUrl, "_blank");
      }
    };
    const formatFileSize = (bytes) => {
      if (!bytes) return "--";
      if (bytes < 1024) return bytes + " B";
      if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + " KB";
      return (bytes / (1024 * 1024)).toFixed(2) + " MB";
    };
    onMounted(() => {
      loadMergeConfig();
    });
    return (_ctx, _cache) => {
      const _component_el_skeleton = ElSkeleton;
      const _component_el_button = ElButton;
      const _component_el_alert = ElAlert;
      const _component_el_tag = ElTag;
      const _component_el_checkbox = ElCheckbox;
      const _component_el_input = ElInput;
      const _component_el_progress = ElProgress;
      const _component_el_descriptions_item = ElDescriptionsItem;
      const _component_el_descriptions = ElDescriptions;
      const _component_el_result = ElResult;
      return openBlock(), createElementBlock("div", _hoisted_1$1, [
        loading.value ? (openBlock(), createBlock(_component_el_skeleton, {
          key: 0,
          rows: 10,
          animated: ""
        })) : (openBlock(), createElementBlock(Fragment, { key: 1 }, [
          createBaseVNode("section", _hoisted_2$1, [
            _cache[18] || (_cache[18] = createBaseVNode("div", { class: "section-header" }, [
              createBaseVNode("h3", null, [
                createBaseVNode("i", { class: "bi bi-file-check" }),
                createTextVNode(" 步骤 1/3：文件状态检查")
              ])
            ], -1)),
            createBaseVNode("div", _hoisted_3$1, [
              createBaseVNode("div", {
                class: normalizeClass(["file-status-item", { "file-ready": files.value.business }])
              }, [
                createBaseVNode("div", _hoisted_4$1, [
                  files.value.business ? (openBlock(), createElementBlock("i", _hoisted_5$1)) : (openBlock(), createElementBlock("i", _hoisted_6$1))
                ]),
                createBaseVNode("div", _hoisted_7$1, [
                  _cache[11] || (_cache[11] = createBaseVNode("h4", null, "商务应答文件", -1)),
                  files.value.business ? (openBlock(), createElementBlock(Fragment, { key: 0 }, [
                    createBaseVNode("p", _hoisted_8$1, toDisplayString(files.value.business.file_name), 1),
                    createBaseVNode("p", _hoisted_9, toDisplayString(formatFileSize(files.value.business.file_size)), 1)
                  ], 64)) : (openBlock(), createElementBlock("p", _hoisted_10, "未生成"))
                ]),
                files.value.business ? (openBlock(), createElementBlock("div", _hoisted_11, [
                  createVNode(_component_el_button, {
                    size: "small",
                    onClick: _cache[0] || (_cache[0] = ($event) => handlePreviewFile("business"))
                  }, {
                    default: withCtx(() => [..._cache[12] || (_cache[12] = [
                      createBaseVNode("i", { class: "bi bi-eye" }, null, -1),
                      createTextVNode(" 预览 ", -1)
                    ])]),
                    _: 1
                  })
                ])) : createCommentVNode("", true)
              ], 2),
              createBaseVNode("div", {
                class: normalizeClass(["file-status-item", { "file-ready": files.value.p2p }])
              }, [
                createBaseVNode("div", _hoisted_12, [
                  files.value.p2p ? (openBlock(), createElementBlock("i", _hoisted_13)) : (openBlock(), createElementBlock("i", _hoisted_14))
                ]),
                createBaseVNode("div", _hoisted_15, [
                  _cache[13] || (_cache[13] = createBaseVNode("h4", null, "技术点对点应答", -1)),
                  files.value.p2p ? (openBlock(), createElementBlock(Fragment, { key: 0 }, [
                    createBaseVNode("p", _hoisted_16, toDisplayString(files.value.p2p.file_name), 1),
                    createBaseVNode("p", _hoisted_17, toDisplayString(formatFileSize(files.value.p2p.file_size)), 1)
                  ], 64)) : (openBlock(), createElementBlock("p", _hoisted_18, "未生成（可选）"))
                ]),
                files.value.p2p ? (openBlock(), createElementBlock("div", _hoisted_19, [
                  createVNode(_component_el_button, {
                    size: "small",
                    onClick: _cache[1] || (_cache[1] = ($event) => handlePreviewFile("p2p"))
                  }, {
                    default: withCtx(() => [..._cache[14] || (_cache[14] = [
                      createBaseVNode("i", { class: "bi bi-eye" }, null, -1),
                      createTextVNode(" 预览 ", -1)
                    ])]),
                    _: 1
                  })
                ])) : createCommentVNode("", true)
              ], 2),
              createBaseVNode("div", {
                class: normalizeClass(["file-status-item", { "file-ready": files.value.tech }])
              }, [
                createBaseVNode("div", _hoisted_20, [
                  files.value.tech ? (openBlock(), createElementBlock("i", _hoisted_21)) : (openBlock(), createElementBlock("i", _hoisted_22))
                ]),
                createBaseVNode("div", _hoisted_23, [
                  _cache[15] || (_cache[15] = createBaseVNode("h4", null, "技术方案文件", -1)),
                  files.value.tech ? (openBlock(), createElementBlock(Fragment, { key: 0 }, [
                    createBaseVNode("p", _hoisted_24, toDisplayString(files.value.tech.file_name), 1),
                    createBaseVNode("p", _hoisted_25, toDisplayString(formatFileSize(files.value.tech.file_size)), 1)
                  ], 64)) : (openBlock(), createElementBlock("p", _hoisted_26, "未生成"))
                ]),
                files.value.tech ? (openBlock(), createElementBlock("div", _hoisted_27, [
                  createVNode(_component_el_button, {
                    size: "small",
                    onClick: _cache[2] || (_cache[2] = ($event) => handlePreviewFile("tech"))
                  }, {
                    default: withCtx(() => [..._cache[16] || (_cache[16] = [
                      createBaseVNode("i", { class: "bi bi-eye" }, null, -1),
                      createTextVNode(" 预览 ", -1)
                    ])]),
                    _: 1
                  })
                ])) : createCommentVNode("", true)
              ], 2)
            ]),
            !canMerge.value ? (openBlock(), createBlock(_component_el_alert, {
              key: 0,
              type: "warning",
              closable: false,
              "show-icon": "",
              class: "mt-3"
            }, {
              title: withCtx(() => [..._cache[17] || (_cache[17] = [
                createTextVNode(" 无法整合：缺少必需的文件 ", -1)
              ])]),
              default: withCtx(() => [
                !files.value.business ? (openBlock(), createElementBlock("p", _hoisted_28, "• 商务应答文件未生成，请先完成商务应答")) : createCommentVNode("", true),
                !files.value.tech ? (openBlock(), createElementBlock("p", _hoisted_29, "• 技术方案文件未生成，请先完成技术方案")) : createCommentVNode("", true)
              ]),
              _: 1
            })) : createCommentVNode("", true)
          ]),
          canMerge.value ? (openBlock(), createElementBlock("section", _hoisted_30, [
            _cache[42] || (_cache[42] = createBaseVNode("div", { class: "section-header" }, [
              createBaseVNode("h3", null, [
                createBaseVNode("i", { class: "bi bi-sliders" }),
                createTextVNode(" 步骤 2/3：整合配置")
              ])
            ], -1)),
            createBaseVNode("div", _hoisted_31, [
              _cache[27] || (_cache[27] = createBaseVNode("h4", null, [
                createBaseVNode("i", { class: "bi bi-files" }),
                createTextVNode(" 文档组成与顺序")
              ], -1)),
              createBaseVNode("div", _hoisted_32, [
                createBaseVNode("div", _hoisted_33, [
                  _cache[20] || (_cache[20] = createBaseVNode("span", { class: "order-number" }, "1", -1)),
                  _cache[21] || (_cache[21] = createBaseVNode("span", { class: "doc-name" }, "商务应答", -1)),
                  createVNode(_component_el_tag, {
                    size: "small",
                    type: "info"
                  }, {
                    default: withCtx(() => [..._cache[19] || (_cache[19] = [
                      createTextVNode("固定第一部分", -1)
                    ])]),
                    _: 1
                  })
                ]),
                files.value.p2p ? (openBlock(), createElementBlock("div", _hoisted_34, [
                  _cache[23] || (_cache[23] = createBaseVNode("span", { class: "order-number" }, "2", -1)),
                  _cache[24] || (_cache[24] = createBaseVNode("span", { class: "doc-name" }, "点对点应答", -1)),
                  createVNode(_component_el_checkbox, {
                    modelValue: mergeConfig.value.include_p2p,
                    "onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => mergeConfig.value.include_p2p = $event)
                  }, {
                    default: withCtx(() => [..._cache[22] || (_cache[22] = [
                      createTextVNode("包含此部分", -1)
                    ])]),
                    _: 1
                  }, 8, ["modelValue"])
                ])) : createCommentVNode("", true),
                createBaseVNode("div", _hoisted_35, [
                  createBaseVNode("span", _hoisted_36, toDisplayString(files.value.p2p ? "3" : "2"), 1),
                  _cache[26] || (_cache[26] = createBaseVNode("span", { class: "doc-name" }, "技术方案", -1)),
                  createVNode(_component_el_tag, {
                    size: "small",
                    type: "success"
                  }, {
                    default: withCtx(() => [..._cache[25] || (_cache[25] = [
                      createTextVNode("✓ 包含", -1)
                    ])]),
                    _: 1
                  })
                ])
              ])
            ]),
            createBaseVNode("div", _hoisted_37, [
              _cache[32] || (_cache[32] = createBaseVNode("h4", null, [
                createBaseVNode("i", { class: "bi bi-palette" }),
                createTextVNode(" 格式与目录选项")
              ], -1)),
              createBaseVNode("div", _hoisted_38, [
                createVNode(_component_el_checkbox, {
                  modelValue: mergeConfig.value.generate_toc,
                  "onUpdate:modelValue": _cache[4] || (_cache[4] = ($event) => mergeConfig.value.generate_toc = $event)
                }, {
                  default: withCtx(() => [..._cache[28] || (_cache[28] = [
                    createTextVNode(" 自动生成目录（基于1-3级标题，带页码） ", -1)
                  ])]),
                  _: 1
                }, 8, ["modelValue"]),
                createVNode(_component_el_checkbox, {
                  modelValue: mergeConfig.value.remove_blanks,
                  "onUpdate:modelValue": _cache[5] || (_cache[5] = ($event) => mergeConfig.value.remove_blanks = $event)
                }, {
                  default: withCtx(() => [..._cache[29] || (_cache[29] = [
                    createTextVNode(" 删除空白页和空白段落 ", -1)
                  ])]),
                  _: 1
                }, 8, ["modelValue"]),
                createVNode(_component_el_checkbox, {
                  modelValue: mergeConfig.value.unify_styles,
                  "onUpdate:modelValue": _cache[6] || (_cache[6] = ($event) => mergeConfig.value.unify_styles = $event)
                }, {
                  default: withCtx(() => [..._cache[30] || (_cache[30] = [
                    createTextVNode(" 统一页眉页脚格式 ", -1)
                  ])]),
                  _: 1
                }, 8, ["modelValue"]),
                createVNode(_component_el_checkbox, {
                  modelValue: mergeConfig.value.add_section_breaks,
                  "onUpdate:modelValue": _cache[7] || (_cache[7] = ($event) => mergeConfig.value.add_section_breaks = $event)
                }, {
                  default: withCtx(() => [..._cache[31] || (_cache[31] = [
                    createTextVNode(" 每部分间添加分节符 ", -1)
                  ])]),
                  _: 1
                }, 8, ["modelValue"])
              ])
            ]),
            createBaseVNode("div", _hoisted_39, [
              _cache[39] || (_cache[39] = createBaseVNode("h4", null, [
                createBaseVNode("i", { class: "bi bi-list-ol" }),
                createTextVNode(" 索引设置")
              ], -1)),
              !indexRequirement.value.required ? (openBlock(), createBlock(_component_el_alert, {
                key: 0,
                type: "info",
                closable: false,
                "show-icon": ""
              }, {
                title: withCtx(() => [..._cache[33] || (_cache[33] = [
                  createTextVNode(" 招标文件未要求提供索引，无需生成 ", -1)
                ])]),
                _: 1
              })) : indexRequirement.value.type === "fixed_format" ? (openBlock(), createBlock(_component_el_alert, {
                key: 1,
                type: "warning",
                closable: false,
                "show-icon": ""
              }, {
                title: withCtx(() => [..._cache[34] || (_cache[34] = [
                  createTextVNode(" 招标文件要求提供固定格式索引 ", -1)
                ])]),
                default: withCtx(() => [
                  createBaseVNode("div", _hoisted_40, [
                    createBaseVNode("pre", null, toDisplayString(indexRequirement.value.template), 1)
                  ]),
                  createVNode(_component_el_checkbox, {
                    modelValue: indexEnabled.value,
                    "onUpdate:modelValue": _cache[8] || (_cache[8] = ($event) => indexEnabled.value = $event),
                    disabled: "",
                    checked: ""
                  }, {
                    default: withCtx(() => [..._cache[35] || (_cache[35] = [
                      createTextVNode(" 自动生成索引（必需） ", -1)
                    ])]),
                    _: 1
                  }, 8, ["modelValue"])
                ]),
                _: 1
              })) : indexRequirement.value.type === "score_based" ? (openBlock(), createBlock(_component_el_alert, {
                key: 2,
                type: "success",
                closable: false,
                "show-icon": ""
              }, {
                title: withCtx(() => [..._cache[36] || (_cache[36] = [
                  createTextVNode(" 招标文件要求以评分标准建立索引 ", -1)
                ])]),
                default: withCtx(() => [
                  createBaseVNode("div", _hoisted_41, [
                    _cache[37] || (_cache[37] = createBaseVNode("p", null, "将基于以下评分项生成索引：", -1)),
                    createBaseVNode("ul", null, [
                      (openBlock(true), createElementBlock(Fragment, null, renderList(indexRequirement.value.score_items, (item) => {
                        return openBlock(), createElementBlock("li", { key: item }, toDisplayString(item), 1);
                      }), 128))
                    ])
                  ]),
                  createVNode(_component_el_checkbox, {
                    modelValue: indexEnabled.value,
                    "onUpdate:modelValue": _cache[9] || (_cache[9] = ($event) => indexEnabled.value = $event),
                    disabled: "",
                    checked: ""
                  }, {
                    default: withCtx(() => [..._cache[38] || (_cache[38] = [
                      createTextVNode(" 自动生成评分标准索引（必需） ", -1)
                    ])]),
                    _: 1
                  }, 8, ["modelValue"])
                ]),
                _: 1
              })) : createCommentVNode("", true)
            ]),
            createBaseVNode("div", _hoisted_42, [
              _cache[41] || (_cache[41] = createBaseVNode("h4", null, [
                createBaseVNode("i", { class: "bi bi-file-earmark-text" }),
                createTextVNode(" 文档名称")
              ], -1)),
              createVNode(_component_el_input, {
                modelValue: mergeConfig.value.output_filename,
                "onUpdate:modelValue": _cache[10] || (_cache[10] = ($event) => mergeConfig.value.output_filename = $event),
                placeholder: "请输入最终标书文件名",
                maxlength: "100",
                "show-word-limit": ""
              }, {
                suffix: withCtx(() => [..._cache[40] || (_cache[40] = [
                  createTextVNode(".docx", -1)
                ])]),
                _: 1
              }, 8, ["modelValue"])
            ])
          ])) : createCommentVNode("", true),
          canMerge.value ? (openBlock(), createElementBlock("section", _hoisted_43, [
            _cache[58] || (_cache[58] = createBaseVNode("div", { class: "section-header" }, [
              createBaseVNode("h3", null, [
                createBaseVNode("i", { class: "bi bi-rocket-takeoff" }),
                createTextVNode(" 步骤 3/3：开始整合")
              ])
            ], -1)),
            !merging.value && !mergeResult.value ? (openBlock(), createElementBlock("div", _hoisted_44, [
              createVNode(_component_el_button, {
                type: "primary",
                size: "large",
                loading: starting.value,
                onClick: startMerge
              }, {
                default: withCtx(() => [..._cache[43] || (_cache[43] = [
                  createBaseVNode("i", { class: "bi bi-play-fill" }, null, -1),
                  createTextVNode(" 开始整合 ", -1)
                ])]),
                _: 1
              }, 8, ["loading"])
            ])) : createCommentVNode("", true),
            merging.value ? (openBlock(), createElementBlock("div", _hoisted_45, [
              createVNode(_component_el_progress, {
                percentage: mergeProgress.value,
                status: mergeStatus.value
              }, null, 8, ["percentage", "status"]),
              createBaseVNode("p", _hoisted_46, toDisplayString(mergeMessage.value), 1),
              createBaseVNode("div", _hoisted_47, [
                _cache[46] || (_cache[46] = createBaseVNode("h5", null, "处理详情：", -1)),
                createBaseVNode("ul", null, [
                  (openBlock(true), createElementBlock(Fragment, null, renderList(completedSteps.value, (step, index) => {
                    return openBlock(), createElementBlock("li", {
                      key: index,
                      class: "completed"
                    }, [
                      _cache[44] || (_cache[44] = createBaseVNode("i", { class: "bi bi-check-circle-fill" }, null, -1)),
                      createTextVNode(" " + toDisplayString(step), 1)
                    ]);
                  }), 128)),
                  currentStep.value ? (openBlock(), createElementBlock("li", _hoisted_48, [
                    _cache[45] || (_cache[45] = createBaseVNode("i", { class: "bi bi-arrow-right-circle-fill" }, null, -1)),
                    createTextVNode(" " + toDisplayString(currentStep.value), 1)
                  ])) : createCommentVNode("", true)
                ])
              ])
            ])) : createCommentVNode("", true),
            mergeResult.value ? (openBlock(), createElementBlock("div", _hoisted_49, [
              createVNode(_component_el_result, {
                icon: "success",
                title: "整合完成！",
                "sub-title": "您的最终标书已生成"
              }, {
                extra: withCtx(() => {
                  var _a, _b, _c, _d, _e, _f;
                  return [
                    createBaseVNode("div", _hoisted_50, [
                      _cache[55] || (_cache[55] = createBaseVNode("h4", null, [
                        createBaseVNode("i", { class: "bi bi-file-earmark-check" }),
                        createTextVNode(" 文件信息")
                      ], -1)),
                      createVNode(_component_el_descriptions, {
                        column: 2,
                        border: ""
                      }, {
                        default: withCtx(() => [
                          createVNode(_component_el_descriptions_item, { label: "文件名" }, {
                            default: withCtx(() => [
                              createTextVNode(toDisplayString(mergeResult.value.filename), 1)
                            ]),
                            _: 1
                          }),
                          createVNode(_component_el_descriptions_item, { label: "文件大小" }, {
                            default: withCtx(() => [
                              createTextVNode(toDisplayString(formatFileSize(mergeResult.value.file_size)), 1)
                            ]),
                            _: 1
                          }),
                          createVNode(_component_el_descriptions_item, { label: "总页数" }, {
                            default: withCtx(() => {
                              var _a2;
                              return [
                                createTextVNode(toDisplayString(((_a2 = mergeResult.value.stats) == null ? void 0 : _a2.total_pages) || "--") + " 页 ", 1)
                              ];
                            }),
                            _: 1
                          }),
                          createVNode(_component_el_descriptions_item, { label: "生成时间" }, {
                            default: withCtx(() => [
                              createTextVNode(toDisplayString(mergeResult.value.created_at), 1)
                            ]),
                            _: 1
                          })
                        ]),
                        _: 1
                      }),
                      _cache[56] || (_cache[56] = createBaseVNode("h4", { class: "mt-3" }, [
                        createBaseVNode("i", { class: "bi bi-bar-chart" }),
                        createTextVNode(" 文件组成统计")
                      ], -1)),
                      createBaseVNode("ul", _hoisted_51, [
                        ((_a = mergeResult.value.stats) == null ? void 0 : _a.toc_pages) ? (openBlock(), createElementBlock("li", _hoisted_52, " 目录：" + toDisplayString(mergeResult.value.stats.toc_pages) + " 页 ", 1)) : createCommentVNode("", true),
                        createBaseVNode("li", null, "商务应答：" + toDisplayString(((_b = mergeResult.value.stats) == null ? void 0 : _b.business_pages) || "--") + " 页", 1),
                        mergeConfig.value.include_p2p ? (openBlock(), createElementBlock("li", _hoisted_53, " 点对点应答：" + toDisplayString(((_c = mergeResult.value.stats) == null ? void 0 : _c.p2p_pages) || "--") + " 页 ", 1)) : createCommentVNode("", true),
                        createBaseVNode("li", null, "技术方案：" + toDisplayString(((_d = mergeResult.value.stats) == null ? void 0 : _d.tech_pages) || "--") + " 页", 1),
                        ((_e = mergeResult.value.stats) == null ? void 0 : _e.index_pages) ? (openBlock(), createElementBlock("li", _hoisted_54, " 索引：" + toDisplayString(mergeResult.value.stats.index_pages) + " 页 ", 1)) : createCommentVNode("", true)
                      ]),
                      _cache[57] || (_cache[57] = createBaseVNode("h4", { class: "mt-3" }, [
                        createBaseVNode("i", { class: "bi bi-tools" }),
                        createTextVNode(" 处理详情")
                      ], -1)),
                      createBaseVNode("ul", _hoisted_55, [
                        ((_f = mergeResult.value.stats) == null ? void 0 : _f.removed_blanks) ? (openBlock(), createElementBlock("li", _hoisted_56, [
                          _cache[47] || (_cache[47] = createBaseVNode("i", { class: "bi bi-check-circle text-success" }, null, -1)),
                          createTextVNode(" 已删除 " + toDisplayString(mergeResult.value.stats.removed_blanks) + " 个空白段落 ", 1)
                        ])) : createCommentVNode("", true),
                        mergeConfig.value.generate_toc ? (openBlock(), createElementBlock("li", _hoisted_57, [..._cache[48] || (_cache[48] = [
                          createBaseVNode("i", { class: "bi bi-check-circle text-success" }, null, -1),
                          createTextVNode(" 已生成多级目录 ", -1)
                        ])])) : createCommentVNode("", true),
                        indexRequirement.value.required ? (openBlock(), createElementBlock("li", _hoisted_58, [
                          _cache[49] || (_cache[49] = createBaseVNode("i", { class: "bi bi-check-circle text-success" }, null, -1)),
                          createTextVNode(" 已生成" + toDisplayString(indexRequirement.value.type === "score_based" ? "评分标准" : "固定格式") + "索引 ", 1)
                        ])) : createCommentVNode("", true),
                        mergeConfig.value.unify_styles ? (openBlock(), createElementBlock("li", _hoisted_59, [..._cache[50] || (_cache[50] = [
                          createBaseVNode("i", { class: "bi bi-check-circle text-success" }, null, -1),
                          createTextVNode(" 已统一页眉页脚 ", -1)
                        ])])) : createCommentVNode("", true)
                      ]),
                      createBaseVNode("div", _hoisted_60, [
                        createVNode(_component_el_button, {
                          type: "primary",
                          size: "large",
                          onClick: downloadMergedFile
                        }, {
                          default: withCtx(() => [..._cache[51] || (_cache[51] = [
                            createBaseVNode("i", { class: "bi bi-download" }, null, -1),
                            createTextVNode(" 下载Word版 ", -1)
                          ])]),
                          _: 1
                        }),
                        createVNode(_component_el_button, {
                          type: "success",
                          size: "large",
                          onClick: previewMergedFile
                        }, {
                          default: withCtx(() => [..._cache[52] || (_cache[52] = [
                            createBaseVNode("i", { class: "bi bi-eye" }, null, -1),
                            createTextVNode(" 在线预览 ", -1)
                          ])]),
                          _: 1
                        }),
                        createVNode(_component_el_button, {
                          type: "warning",
                          size: "large",
                          onClick: editMergedFile
                        }, {
                          default: withCtx(() => [..._cache[53] || (_cache[53] = [
                            createBaseVNode("i", { class: "bi bi-pencil-square" }, null, -1),
                            createTextVNode(" 在线编辑 ", -1)
                          ])]),
                          _: 1
                        }),
                        createVNode(_component_el_button, {
                          size: "large",
                          onClick: resetMerge
                        }, {
                          default: withCtx(() => [..._cache[54] || (_cache[54] = [
                            createBaseVNode("i", { class: "bi bi-arrow-clockwise" }, null, -1),
                            createTextVNode(" 重新整合 ", -1)
                          ])]),
                          _: 1
                        })
                      ])
                    ])
                  ];
                }),
                _: 1
              })
            ])) : createCommentVNode("", true)
          ])) : createCommentVNode("", true)
        ], 64))
      ]);
    };
  }
});
const DocumentMergePanel = /* @__PURE__ */ _export_sfc(_sfc_main$1, [["__scopeId", "data-v-4f5ce16e"]]);
const _hoisted_1 = { class: "final-tender-page" };
const _hoisted_2 = { class: "selector-content" };
const _hoisted_3 = { class: "project-option" };
const _hoisted_4 = { class: "project-name" };
const _hoisted_5 = { class: "project-status" };
const _hoisted_6 = { class: "project-info" };
const _hoisted_7 = { class: "project-header" };
const _hoisted_8 = { class: "project-meta" };
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "FinalTender",
  setup(__props) {
    const route = useRoute();
    const router = useRouter();
    useProjectStore();
    const {
      projects,
      loading,
      selectedProject,
      currentDocuments,
      hasProjects,
      loadProjects,
      handleProjectChange: handleProjectChangeComposable,
      restoreProjectFromStore
    } = useProjectDocuments();
    const form = ref({
      projectId: null
    });
    const handleProjectChange = async () => {
      await handleProjectChangeComposable(form.value.projectId, {
        onClear: () => {
          console.log("[最终标书] 项目切换，清空状态");
        },
        onDocumentsLoaded: (docs) => {
          console.log("[最终标书] 项目文档已加载:", docs);
          const hasBusinessResponse = !!docs.businessResponseFile;
          const hasTechProposal = !!docs.techProposalFile;
          if (!hasBusinessResponse || !hasTechProposal) {
            ElMessage.warning("该项目缺少商务应答或技术方案文件，无法整合");
          }
        }
      });
      if (form.value.projectId) {
        router.replace({
          name: "FinalTender",
          query: { projectId: form.value.projectId.toString() }
        });
      }
    };
    const changeProject = () => {
      form.value.projectId = null;
      router.replace({ name: "FinalTender" });
    };
    const handleRefresh = () => {
      loadProjects();
    };
    onMounted(async () => {
      await loadProjects();
      const restoredProjectId = await restoreProjectFromStore({
        onClear: () => {
          console.log("[最终标书] Store恢复，清空状态");
        },
        onDocumentsLoaded: (docs) => {
          console.log("[最终标书] Store恢复，文档已加载:", docs);
        }
      });
      if (restoredProjectId) {
        form.value.projectId = restoredProjectId;
        console.log("✅ 已从Store恢复项目:", restoredProjectId);
      }
      const projectIdFromRoute = route.query.projectId;
      if (projectIdFromRoute && !restoredProjectId) {
        const id = Number(projectIdFromRoute);
        if (projects.value.some((p) => p.id === id)) {
          form.value.projectId = id;
          await handleProjectChange();
        }
      }
    });
    return (_ctx, _cache) => {
      const _component_el_button = ElButton;
      const _component_el_tag = ElTag;
      const _component_el_option = ElOption;
      const _component_el_select = ElSelect;
      const _component_el_empty = ElEmpty;
      const _component_el_card = ElCard;
      return openBlock(), createElementBlock("div", _hoisted_1, [
        createVNode(unref(PageHeader), {
          title: "最终标书",
          "show-back": false
        }, {
          actions: withCtx(() => [
            createVNode(_component_el_button, { onClick: handleRefresh }, {
              default: withCtx(() => [..._cache[2] || (_cache[2] = [
                createBaseVNode("i", { class: "bi bi-arrow-clockwise" }, null, -1),
                createTextVNode(" 刷新 ", -1)
              ])]),
              _: 1
            })
          ]),
          _: 1
        }),
        unref(loading) ? (openBlock(), createBlock(unref(Loading), {
          key: 0,
          text: "加载项目列表..."
        })) : (openBlock(), createElementBlock(Fragment, { key: 1 }, [
          !form.value.projectId ? (openBlock(), createBlock(_component_el_card, {
            key: 0,
            class: "project-selector-card",
            shadow: "never"
          }, {
            default: withCtx(() => [
              createBaseVNode("div", _hoisted_2, [
                _cache[4] || (_cache[4] = createBaseVNode("div", { class: "selector-icon" }, [
                  createBaseVNode("i", { class: "bi bi-folder2-open" })
                ], -1)),
                _cache[5] || (_cache[5] = createBaseVNode("h3", null, "请选择要整合的项目", -1)),
                _cache[6] || (_cache[6] = createBaseVNode("p", { class: "text-muted" }, " 从下方列表中选择一个已完成商务应答和技术方案的项目 ", -1)),
                createVNode(_component_el_select, {
                  modelValue: form.value.projectId,
                  "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => form.value.projectId = $event),
                  placeholder: "选择项目",
                  size: "large",
                  filterable: "",
                  class: "project-select",
                  onChange: handleProjectChange
                }, {
                  default: withCtx(() => [
                    (openBlock(true), createElementBlock(Fragment, null, renderList(unref(projects), (project) => {
                      return openBlock(), createBlock(_component_el_option, {
                        key: project.id,
                        label: `${project.project_name} (${project.project_number || "-"})`,
                        value: project.id
                      }, {
                        default: withCtx(() => [
                          createBaseVNode("div", _hoisted_3, [
                            createBaseVNode("span", _hoisted_4, toDisplayString(project.project_name), 1),
                            createBaseVNode("div", _hoisted_5, [
                              createVNode(_component_el_tag, {
                                type: "info",
                                size: "small"
                              }, {
                                default: withCtx(() => [
                                  createTextVNode(toDisplayString(project.company_name), 1)
                                ]),
                                _: 2
                              }, 1024)
                            ])
                          ])
                        ]),
                        _: 2
                      }, 1032, ["label", "value"]);
                    }), 128))
                  ]),
                  _: 1
                }, 8, ["modelValue"]),
                !unref(hasProjects) ? (openBlock(), createBlock(_component_el_empty, {
                  key: 0,
                  description: "暂无项目",
                  "image-size": 120
                }, {
                  extra: withCtx(() => [
                    createVNode(_component_el_button, {
                      type: "primary",
                      onClick: _cache[1] || (_cache[1] = ($event) => _ctx.$router.push({ name: "TenderManagement" }))
                    }, {
                      default: withCtx(() => [..._cache[3] || (_cache[3] = [
                        createBaseVNode("i", { class: "bi bi-folder-plus" }, null, -1),
                        createTextVNode(" 前往项目管理 ", -1)
                      ])]),
                      _: 1
                    })
                  ]),
                  _: 1
                })) : createCommentVNode("", true)
              ])
            ]),
            _: 1
          })) : createCommentVNode("", true),
          form.value.projectId && unref(selectedProject) ? (openBlock(), createElementBlock(Fragment, { key: 1 }, [
            createVNode(_component_el_card, {
              class: "current-project-card",
              shadow: "never"
            }, {
              default: withCtx(() => [
                createBaseVNode("div", _hoisted_6, [
                  createBaseVNode("div", _hoisted_7, [
                    createBaseVNode("h3", null, [
                      _cache[7] || (_cache[7] = createBaseVNode("i", { class: "bi bi-folder-check" }, null, -1)),
                      createTextVNode(" " + toDisplayString(unref(selectedProject).project_name), 1)
                    ]),
                    createVNode(_component_el_button, {
                      size: "small",
                      text: "",
                      onClick: changeProject
                    }, {
                      default: withCtx(() => [..._cache[8] || (_cache[8] = [
                        createBaseVNode("i", { class: "bi bi-arrow-left-right" }, null, -1),
                        createTextVNode(" 切换项目 ", -1)
                      ])]),
                      _: 1
                    })
                  ]),
                  createBaseVNode("p", _hoisted_8, " 公司：" + toDisplayString(unref(selectedProject).company_name) + " | 项目编号：" + toDisplayString(unref(selectedProject).project_number || "-") + " | 创建时间：" + toDisplayString(unref(selectedProject).created_at), 1)
                ])
              ]),
              _: 1
            }),
            (openBlock(), createBlock(DocumentMergePanel, {
              "project-id": form.value.projectId,
              "current-documents": unref(currentDocuments),
              key: form.value.projectId
            }, null, 8, ["project-id", "current-documents"]))
          ], 64)) : createCommentVNode("", true)
        ], 64))
      ]);
    };
  }
});
const FinalTender = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-a7f77f31"]]);
export {
  FinalTender as default
};
