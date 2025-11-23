import { d as defineComponent, c as computed, e as createElementBlock, o as openBlock, U as normalizeClass, n as createBaseVNode, l as createCommentVNode, t as toDisplayString, p as createTextVNode, f as createVNode, g as ElButton, w as withCtx, A as ElMessage, r as ref, D as watch, y as ElInput, k as createBlock, aq as ElTree, X as ElTag, ar as ElEmpty, S as onMounted, ak as ElRow, ai as ElCol, as as ElCard, m as ElAlert, at as ElUpload, au as ElButtonGroup, av as ElSpace, ad as ElIcon, h as unref, ap as loading_default, z as ElMessageBox, u as useRoute, M as useRouter, b as reactive, F as Fragment, aw as ElTabs, ax as ElTabPane, q as ElForm, s as ElFormItem, Y as ElSelect, V as renderList, W as ElOption, ay as ElDescriptions, az as ElDescriptionsItem, aA as ElInputNumber, aB as ElText, a6 as ElDivider, Z as ElBadge } from "./vendor-_9UVkM6-.js";
import { L as Loading } from "./Loading-dPNGnJM7.js";
/* empty css                                                                           */
import { P as PageHeader } from "./PageHeader-C0KfWJQh.js";
import { D as DocumentPreview } from "./DocumentPreview-kARaYjYY.js";
import { _ as _export_sfc } from "./index.js";
import { t as tenderApi } from "./tender-DvsgeLWX.js";
import { c as companyApi } from "./company-z4Xg082l.js";
import { u as useProjectStore } from "./project-COt-HjGx.js";
/* empty css                                                                         */
const _hoisted_1$3 = { class: "file-card__icon" };
const _hoisted_2$3 = { class: "file-card__info" };
const _hoisted_3$3 = { class: "file-card__name" };
const _hoisted_4$3 = { class: "file-card__meta" };
const _hoisted_5$3 = {
  key: 0,
  class: "meta-item"
};
const _hoisted_6$3 = {
  key: 0,
  class: "file-card__actions"
};
const _sfc_main$3 = /* @__PURE__ */ defineComponent({
  __name: "FileCard",
  props: {
    fileUrl: {},
    fileName: {},
    fileSize: {},
    uploadTime: {},
    type: { default: "default" },
    showActions: { type: Boolean, default: true }
  },
  emits: ["preview"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const fileName = computed(() => {
      if (props.fileName) return props.fileName;
      const parts = props.fileUrl.split("/");
      return parts[parts.length - 1] || "";
    });
    const fileIcon = computed(() => {
      var _a;
      const ext = (_a = fileName.value.split(".").pop()) == null ? void 0 : _a.toLowerCase();
      const iconMap = {
        pdf: "bi-file-pdf",
        doc: "bi-file-word",
        docx: "bi-file-word",
        xls: "bi-file-excel",
        xlsx: "bi-file-excel",
        zip: "bi-file-zip",
        rar: "bi-file-zip"
      };
      return iconMap[ext || ""] || "bi-file-earmark-text";
    });
    const uploadDate = computed(() => {
      if (!props.uploadTime) return "";
      return props.uploadTime.split(" ")[0] || props.uploadTime;
    });
    const convertToApiUrl = (filePath) => {
      if (filePath.startsWith("http://") || filePath.startsWith("https://") || filePath.startsWith("/api/")) {
        return filePath;
      }
      let apiPath = filePath;
      if (apiPath.startsWith("ai_tender_system/data/")) {
        apiPath = apiPath.substring("ai_tender_system/data/".length);
      }
      if (apiPath.startsWith("outputs/")) {
        apiPath = "download/" + apiPath.substring("outputs/".length);
      }
      return `/api/files/serve/${apiPath}`;
    };
    const handleDownload = () => {
      const apiUrl = convertToApiUrl(props.fileUrl);
      const link = document.createElement("a");
      link.href = apiUrl + "?download=true";
      link.download = fileName.value;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      ElMessage.success("文件下载已开始");
    };
    const handlePreview = () => {
      let ext = "";
      if (fileName.value) {
        const parts = fileName.value.split(".");
        if (parts.length > 1) {
          ext = parts[parts.length - 1].toLowerCase();
        }
      }
      if (!ext && props.fileUrl) {
        const urlWithoutQuery = props.fileUrl.split("?")[0];
        const parts = urlWithoutQuery.split(".");
        if (parts.length > 1) {
          ext = parts[parts.length - 1].toLowerCase();
        }
      }
      const isWordDoc = ext === "doc" || ext === "docx";
      if (isWordDoc) {
        emit("preview", props.fileUrl, fileName.value);
      } else {
        const apiUrl = convertToApiUrl(props.fileUrl);
        window.open(apiUrl, "_blank");
      }
    };
    return (_ctx, _cache) => {
      const _component_el_button = ElButton;
      return openBlock(), createElementBlock("div", {
        class: normalizeClass(["file-card", [`file-card--${__props.type}`]])
      }, [
        createBaseVNode("div", _hoisted_1$3, [
          createBaseVNode("i", {
            class: normalizeClass(fileIcon.value)
          }, null, 2)
        ]),
        createBaseVNode("div", _hoisted_2$3, [
          createBaseVNode("div", _hoisted_3$3, toDisplayString(fileName.value), 1),
          createBaseVNode("div", _hoisted_4$3, [
            uploadDate.value ? (openBlock(), createElementBlock("span", _hoisted_5$3, [
              _cache[0] || (_cache[0] = createBaseVNode("i", { class: "bi bi-calendar" }, null, -1)),
              createTextVNode(" " + toDisplayString(uploadDate.value), 1)
            ])) : createCommentVNode("", true)
          ])
        ]),
        __props.showActions ? (openBlock(), createElementBlock("div", _hoisted_6$3, [
          createVNode(_component_el_button, {
            size: "small",
            onClick: handleDownload
          }, {
            default: withCtx(() => [..._cache[1] || (_cache[1] = [
              createBaseVNode("i", { class: "bi bi-download" }, null, -1),
              createTextVNode(" 下载 ", -1)
            ])]),
            _: 1
          }),
          createVNode(_component_el_button, {
            size: "small",
            onClick: handlePreview
          }, {
            default: withCtx(() => [..._cache[2] || (_cache[2] = [
              createBaseVNode("i", { class: "bi bi-eye" }, null, -1),
              createTextVNode(" 预览 ", -1)
            ])]),
            _: 1
          })
        ])) : createCommentVNode("", true)
      ], 2);
    };
  }
});
const FileCard = /* @__PURE__ */ _export_sfc(_sfc_main$3, [["__scopeId", "data-v-010a89f5"]]);
const _hoisted_1$2 = { class: "chapter-tree" };
const _hoisted_2$2 = {
  key: 0,
  class: "chapter-search mb-3"
};
const _hoisted_3$2 = { class: "chapter-tree-container" };
const _hoisted_4$2 = { class: "chapter-tree-node" };
const _hoisted_5$2 = { class: "chapter-title" };
const _hoisted_6$2 = { class: "chapter-meta" };
const _hoisted_7$2 = {
  key: 1,
  class: "word-count text-muted ms-2"
};
const _sfc_main$2 = /* @__PURE__ */ defineComponent({
  __name: "ChapterTree",
  props: {
    chapters: {},
    showCheckbox: { type: Boolean, default: true },
    showSearch: { type: Boolean, default: true },
    defaultCheckedKeys: { default: () => [] }
  },
  emits: ["check", "select"],
  setup(__props, { expose: __expose, emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const treeRef = ref();
    const searchKeyword = ref("");
    const filteredChapters = ref([]);
    const treeProps = {
      children: "children",
      label: "title"
    };
    filteredChapters.value = props.chapters;
    watch(
      () => props.chapters,
      (newChapters) => {
        filteredChapters.value = newChapters;
        if (props.defaultCheckedKeys.length > 0 && treeRef.value) {
          treeRef.value.setCheckedKeys(props.defaultCheckedKeys);
        }
      },
      { immediate: true }
    );
    const handleSearch = () => {
      if (!searchKeyword.value.trim()) {
        filteredChapters.value = props.chapters;
        return;
      }
      const keyword = searchKeyword.value.toLowerCase();
      filteredChapters.value = filterChapters(props.chapters, keyword);
    };
    const filterChapters = (chapters, keyword) => {
      const result = [];
      for (const chapter of chapters) {
        if (chapter.title.toLowerCase().includes(keyword)) {
          result.push(chapter);
        } else if (chapter.children && chapter.children.length > 0) {
          const filteredChildren = filterChapters(chapter.children, keyword);
          if (filteredChildren.length > 0) {
            result.push({
              ...chapter,
              children: filteredChildren
            });
          }
        }
      }
      return result;
    };
    const handleCheck = () => {
      if (!treeRef.value) return;
      const checkedKeys = treeRef.value.getCheckedKeys();
      const checkedNodes = treeRef.value.getCheckedNodes();
      emit("check", checkedKeys, checkedNodes);
    };
    const getChapterIcon = (chapter) => {
      if (chapter.children && chapter.children.length > 0) {
        return "bi bi-folder";
      }
      return "bi bi-file-earmark-text";
    };
    const getLevelText = (level) => {
      const levelMap = {
        1: "一级",
        2: "二级",
        3: "三级",
        4: "四级",
        5: "五级"
      };
      return levelMap[level] || `${level}级`;
    };
    const formatWordCount = (count) => {
      if (count >= 1e4) {
        return `${(count / 1e4).toFixed(1)}万`;
      }
      return count.toLocaleString();
    };
    const setCheckedKeys = (keys) => {
      var _a;
      (_a = treeRef.value) == null ? void 0 : _a.setCheckedKeys(keys);
    };
    const getCheckedKeys = () => {
      var _a;
      return (_a = treeRef.value) == null ? void 0 : _a.getCheckedKeys();
    };
    const getCheckedNodes = () => {
      var _a;
      return (_a = treeRef.value) == null ? void 0 : _a.getCheckedNodes();
    };
    __expose({
      setCheckedKeys,
      getCheckedKeys,
      getCheckedNodes
    });
    return (_ctx, _cache) => {
      const _component_el_input = ElInput;
      const _component_el_tag = ElTag;
      const _component_el_tree = ElTree;
      const _component_el_empty = ElEmpty;
      return openBlock(), createElementBlock("div", _hoisted_1$2, [
        __props.showSearch ? (openBlock(), createElementBlock("div", _hoisted_2$2, [
          createVNode(_component_el_input, {
            modelValue: searchKeyword.value,
            "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => searchKeyword.value = $event),
            placeholder: "🔍 搜索章节...",
            clearable: "",
            onInput: handleSearch
          }, {
            prefix: withCtx(() => [..._cache[1] || (_cache[1] = [
              createBaseVNode("i", { class: "bi bi-search" }, null, -1)
            ])]),
            _: 1
          }, 8, ["modelValue"])
        ])) : createCommentVNode("", true),
        createBaseVNode("div", _hoisted_3$2, [
          createVNode(_component_el_tree, {
            ref_key: "treeRef",
            ref: treeRef,
            data: filteredChapters.value,
            props: treeProps,
            "show-checkbox": __props.showCheckbox,
            "check-strictly": false,
            "default-expand-all": false,
            "expand-on-click-node": false,
            "node-key": "id",
            onCheck: handleCheck
          }, {
            default: withCtx(({ node, data }) => [
              createBaseVNode("div", _hoisted_4$2, [
                createBaseVNode("span", _hoisted_5$2, [
                  createBaseVNode("i", {
                    class: normalizeClass([getChapterIcon(data), "me-1"])
                  }, null, 2),
                  createTextVNode(" " + toDisplayString(data.title), 1)
                ]),
                createBaseVNode("span", _hoisted_6$2, [
                  data.level ? (openBlock(), createBlock(_component_el_tag, {
                    key: 0,
                    size: "small",
                    type: "info"
                  }, {
                    default: withCtx(() => [
                      createTextVNode(toDisplayString(getLevelText(data.level)), 1)
                    ]),
                    _: 2
                  }, 1024)) : createCommentVNode("", true),
                  data.word_count ? (openBlock(), createElementBlock("span", _hoisted_7$2, toDisplayString(formatWordCount(data.word_count)) + "字 ", 1)) : createCommentVNode("", true)
                ])
              ])
            ]),
            _: 1
          }, 8, ["data", "show-checkbox"]),
          !filteredChapters.value || filteredChapters.value.length === 0 ? (openBlock(), createBlock(_component_el_empty, {
            key: 0,
            description: "暂无章节数据",
            "image-size": 80
          })) : createCommentVNode("", true)
        ])
      ]);
    };
  }
});
const ChapterTree = /* @__PURE__ */ _export_sfc(_sfc_main$2, [["__scopeId", "data-v-af38204c"]]);
const _hoisted_1$1 = { class: "tender-document-processor" };
const _hoisted_2$1 = { class: "card-header" };
const _hoisted_3$1 = { class: "upload-section" };
const _hoisted_4$1 = {
  key: 0,
  class: "existing-document"
};
const _hoisted_5$1 = { class: "d-flex align-items-center justify-content-between" };
const _hoisted_6$1 = { class: "me-3" };
const _hoisted_7$1 = { key: 1 };
const _hoisted_8$1 = {
  key: 0,
  class: "mt-3"
};
const _hoisted_9$1 = { class: "d-flex align-items-center justify-content-between" };
const _hoisted_10$1 = {
  key: 0,
  class: "bi bi-file-earmark-code me-1"
};
const _hoisted_11$1 = { class: "card-header" };
const _hoisted_12$1 = { class: "chapter-section" };
const _hoisted_13$1 = { class: "stats-grid mb-3" };
const _hoisted_14$1 = { class: "stat-card" };
const _hoisted_15$1 = { class: "stat-value" };
const _hoisted_16$1 = { class: "stat-card" };
const _hoisted_17$1 = { class: "stat-value text-success" };
const _hoisted_18$1 = { class: "stat-card" };
const _hoisted_19$1 = { class: "stat-value text-info" };
const _hoisted_20$1 = { class: "batch-operations mb-3" };
const _hoisted_21$1 = { class: "save-actions mt-4" };
const _hoisted_22$1 = {
  key: 0,
  class: "parsing-progress mt-3"
};
const _hoisted_23$1 = { class: "d-flex align-items-center" };
const _sfc_main$1 = /* @__PURE__ */ defineComponent({
  __name: "TenderDocumentProcessor",
  props: {
    projectId: {},
    companyId: {},
    projectDetail: {}
  },
  emits: ["success", "refresh", "preview"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const uploadRef = ref();
    const chapterTreeRef = ref();
    const fileList = ref([]);
    const uploadedFile = ref(null);
    const parsing = ref(false);
    const parsingMessage = ref("正在解析文档结构...");
    const chapters = ref([]);
    const selectedChapterIds = ref([]);
    const selectedChapterNodes = ref([]);
    const savingResponse = ref(false);
    const savingTechnical = ref(false);
    const existingDocumentInfo = ref(null);
    const totalChapters = computed(() => {
      const countChapters = (chaps) => {
        let count = chaps.length;
        chaps.forEach((chap) => {
          if (chap.children && chap.children.length > 0) {
            count += countChapters(chap.children);
          }
        });
        return count;
      };
      return countChapters(chapters.value);
    });
    const selectedCount = computed(() => selectedChapterIds.value.length);
    const selectedWordCount = computed(() => {
      return selectedChapterNodes.value.reduce((sum, node) => {
        return sum + (node.word_count || 0);
      }, 0);
    });
    const hasExistingDocument = computed(() => {
      return existingDocumentInfo.value !== null;
    });
    const handleFileChange = (file) => {
      if (file.raw) {
        uploadedFile.value = file.raw;
        fileList.value = [file];
      }
    };
    const handleFileRemove = () => {
      uploadedFile.value = null;
      fileList.value = [];
      chapters.value = [];
      selectedChapterIds.value = [];
    };
    const handlePreviewExisting = () => {
      if (existingDocumentInfo.value) {
        emit("preview", existingDocumentInfo.value.path, existingDocumentInfo.value.name);
      }
    };
    const handleClearExisting = () => {
      existingDocumentInfo.value = null;
      chapters.value = [];
      selectedChapterIds.value = [];
    };
    const handleParse = async () => {
      if (!uploadedFile.value) {
        ElMessage.warning("请先上传文档");
        return;
      }
      parsing.value = true;
      parsingMessage.value = "正在解析文档结构...";
      try {
        const formData = new FormData();
        formData.append("file", uploadedFile.value);
        formData.append("company_id", props.companyId.toString());
        formData.append("project_id", props.projectId.toString());
        const response = await tenderApi.parseDocumentStructure(formData);
        if (response.success) {
          chapters.value = response.chapters || [];
          ElMessage.success("文档解析成功，请选择章节");
        } else {
          throw new Error(response.message || response.error || "解析失败");
        }
      } catch (error) {
        console.error("文档解析失败:", error);
        const errorMessage = error instanceof Error ? error.message : "未知错误";
        if (errorMessage.includes(".doc") || errorMessage.includes("另存为") || errorMessage.includes("docx")) {
          ElMessageBox.alert(
            errorMessage,
            "不支持 .doc 格式",
            {
              confirmButtonText: "我知道了",
              type: "warning",
              dangerouslyUseHTMLString: false,
              customStyle: {
                width: "500px"
              }
            }
          );
        } else {
          ElMessage.error(`解析失败: ${errorMessage}`);
        }
      } finally {
        parsing.value = false;
      }
    };
    const handleChapterCheck = (checkedKeys, checkedNodes) => {
      selectedChapterIds.value = checkedKeys;
      selectedChapterNodes.value = checkedNodes;
    };
    const handleSelectAll = () => {
      var _a;
      const allKeys = getAllChapterIds(chapters.value);
      (_a = chapterTreeRef.value) == null ? void 0 : _a.setCheckedKeys(allKeys);
    };
    const handleUnselectAll = () => {
      var _a;
      (_a = chapterTreeRef.value) == null ? void 0 : _a.setCheckedKeys([]);
    };
    const handleSelectTech = () => {
      var _a;
      const techKeys = filterChaptersByKeywords(chapters.value, ["技术", "方案", "实施", "系统"]);
      (_a = chapterTreeRef.value) == null ? void 0 : _a.setCheckedKeys(techKeys);
    };
    const handleExcludeContract = () => {
      var _a;
      const allKeys = getAllChapterIds(chapters.value);
      const contractKeys = filterChaptersByKeywords(chapters.value, ["合同", "条款", "协议"]);
      const excludedKeys = allKeys.filter((key) => !contractKeys.includes(key));
      (_a = chapterTreeRef.value) == null ? void 0 : _a.setCheckedKeys(excludedKeys);
    };
    const getAllChapterIds = (chaps) => {
      const ids = [];
      chaps.forEach((chap) => {
        ids.push(chap.id);
        if (chap.children && chap.children.length > 0) {
          ids.push(...getAllChapterIds(chap.children));
        }
      });
      return ids;
    };
    const filterChaptersByKeywords = (chaps, keywords) => {
      const ids = [];
      chaps.forEach((chap) => {
        const matchesKeyword = keywords.some((keyword) => chap.title.includes(keyword));
        if (matchesKeyword) {
          ids.push(chap.id);
        }
        if (chap.children && chap.children.length > 0) {
          ids.push(...filterChaptersByKeywords(chap.children, keywords));
        }
      });
      return ids;
    };
    const handleSaveAsResponse = async () => {
      if (selectedCount.value === 0) {
        ElMessage.warning("请先选择章节");
        return;
      }
      savingResponse.value = true;
      try {
        await tenderApi.saveResponseFile(props.projectId, selectedChapterIds.value);
        emit("success", "response");
        emit("refresh");
      } catch (error) {
        console.error("保存失败:", error);
        ElMessage.error(`保存失败: ${error instanceof Error ? error.message : "未知错误"}`);
      } finally {
        savingResponse.value = false;
      }
    };
    const handleSaveAsTechnical = async () => {
      if (selectedCount.value === 0) {
        ElMessage.warning("请先选择章节");
        return;
      }
      savingTechnical.value = true;
      try {
        await tenderApi.saveTechnicalChapters(props.projectId, selectedChapterIds.value);
        emit("success", "technical");
        emit("refresh");
      } catch (error) {
        console.error("保存失败:", error);
        ElMessage.error(`保存失败: ${error instanceof Error ? error.message : "未知错误"}`);
      } finally {
        savingTechnical.value = false;
      }
    };
    const formatWordCount = (count) => {
      if (count >= 1e4) {
        return `${(count / 1e4).toFixed(1)}万`;
      }
      return count.toLocaleString();
    };
    const extractFilenameFromPath = (path) => {
      if (!path) return "招标文档";
      try {
        const normalizedPath = path.replace(/\\/g, "/");
        const parts = normalizedPath.split("/");
        const filename = parts[parts.length - 1];
        return decodeURIComponent(filename);
      } catch (e) {
        console.warn("提取文件名失败:", e);
        return "招标文档";
      }
    };
    const initializeExistingData = () => {
      if (!props.projectDetail) return;
      let step1Data = props.projectDetail.step1_data;
      if (typeof step1Data === "string") {
        try {
          step1Data = JSON.parse(step1Data);
        } catch (e) {
          console.warn("解析step1_data失败:", e);
          step1Data = null;
        }
      }
      if (props.projectDetail.tender_document_path) {
        const filename = props.projectDetail.original_filename || extractFilenameFromPath(props.projectDetail.tender_document_path);
        existingDocumentInfo.value = {
          path: props.projectDetail.tender_document_path,
          name: filename,
          uploadedAt: props.projectDetail.created_at
        };
      } else if (step1Data == null ? void 0 : step1Data.file_path) {
        const filename = step1Data.file_name || extractFilenameFromPath(step1Data.file_path);
        existingDocumentInfo.value = {
          path: step1Data.file_path,
          name: filename,
          uploadedAt: props.projectDetail.created_at
        };
      }
      if ((step1Data == null ? void 0 : step1Data.chapters) && Array.isArray(step1Data.chapters) && step1Data.chapters.length > 0) {
        chapters.value = step1Data.chapters;
      }
    };
    watch(() => props.projectDetail, () => {
      initializeExistingData();
    }, { immediate: true });
    onMounted(() => {
      initializeExistingData();
    });
    return (_ctx, _cache) => {
      const _component_el_tag = ElTag;
      const _component_el_button = ElButton;
      const _component_el_alert = ElAlert;
      const _component_el_upload = ElUpload;
      const _component_el_card = ElCard;
      const _component_el_col = ElCol;
      const _component_el_button_group = ElButtonGroup;
      const _component_el_space = ElSpace;
      const _component_el_row = ElRow;
      const _component_el_icon = ElIcon;
      return openBlock(), createElementBlock("div", _hoisted_1$1, [
        createVNode(_component_el_row, { gutter: 20 }, {
          default: withCtx(() => [
            createVNode(_component_el_col, {
              xs: 24,
              sm: 24,
              md: 10,
              lg: 10
            }, {
              default: withCtx(() => [
                createVNode(_component_el_card, {
                  shadow: "hover",
                  class: "step-card"
                }, {
                  header: withCtx(() => [
                    createBaseVNode("div", _hoisted_2$1, [
                      _cache[1] || (_cache[1] = createBaseVNode("i", { class: "bi bi-upload me-2 text-primary" }, null, -1)),
                      _cache[2] || (_cache[2] = createBaseVNode("span", { class: "step-title" }, "步骤1: 上传招标文档（可选）", -1)),
                      uploadedFile.value || hasExistingDocument.value ? (openBlock(), createBlock(_component_el_tag, {
                        key: 0,
                        type: "success",
                        size: "small",
                        class: "ms-2"
                      }, {
                        default: withCtx(() => [..._cache[0] || (_cache[0] = [
                          createTextVNode(" 已上传 ", -1)
                        ])]),
                        _: 1
                      })) : createCommentVNode("", true)
                    ])
                  ]),
                  default: withCtx(() => [
                    createBaseVNode("div", _hoisted_3$1, [
                      hasExistingDocument.value ? (openBlock(), createElementBlock("div", _hoisted_4$1, [
                        createVNode(_component_el_alert, {
                          type: "success",
                          closable: false
                        }, {
                          title: withCtx(() => [
                            createBaseVNode("div", _hoisted_5$1, [
                              createBaseVNode("div", null, [
                                _cache[4] || (_cache[4] = createBaseVNode("i", { class: "bi bi-file-earmark-check-fill me-2" }, null, -1)),
                                createBaseVNode("span", _hoisted_6$1, toDisplayString(existingDocumentInfo.value.name), 1),
                                createVNode(_component_el_tag, {
                                  size: "small",
                                  type: "success"
                                }, {
                                  default: withCtx(() => [..._cache[3] || (_cache[3] = [
                                    createTextVNode("已上传", -1)
                                  ])]),
                                  _: 1
                                })
                              ]),
                              createBaseVNode("div", null, [
                                createVNode(_component_el_button, {
                                  size: "small",
                                  onClick: handlePreviewExisting
                                }, {
                                  default: withCtx(() => [..._cache[5] || (_cache[5] = [
                                    createBaseVNode("i", { class: "bi bi-eye me-1" }, null, -1),
                                    createTextVNode(" 预览 ", -1)
                                  ])]),
                                  _: 1
                                }),
                                createVNode(_component_el_button, {
                                  size: "small",
                                  onClick: handleClearExisting
                                }, {
                                  default: withCtx(() => [..._cache[6] || (_cache[6] = [
                                    createBaseVNode("i", { class: "bi bi-arrow-repeat me-1" }, null, -1),
                                    createTextVNode(" 重新上传 ", -1)
                                  ])]),
                                  _: 1
                                })
                              ])
                            ])
                          ]),
                          _: 1
                        })
                      ])) : (openBlock(), createElementBlock("div", _hoisted_7$1, [
                        createVNode(_component_el_upload, {
                          ref_key: "uploadRef",
                          ref: uploadRef,
                          drag: "",
                          "auto-upload": false,
                          limit: 1,
                          accept: ".docx",
                          "on-change": handleFileChange,
                          "on-remove": handleFileRemove,
                          "file-list": fileList.value
                        }, {
                          tip: withCtx(() => [..._cache[7] || (_cache[7] = [
                            createBaseVNode("div", { class: "el-upload__tip" }, [
                              createBaseVNode("div", null, [
                                createTextVNode("推荐使用 "),
                                createBaseVNode("strong", null, ".docx"),
                                createTextVNode(" 格式（兼容性更好），文件大小不超过 50MB")
                              ]),
                              createBaseVNode("div", {
                                class: "text-warning",
                                style: { "font-size": "12px", "margin-top": "4px" }
                              }, [
                                createBaseVNode("i", { class: "bi bi-exclamation-triangle-fill me-1" }),
                                createTextVNode(" 注意：旧版 .doc 格式暂不支持章节解析，请先转换为 .docx ")
                              ])
                            ], -1)
                          ])]),
                          default: withCtx(() => [
                            _cache[8] || (_cache[8] = createBaseVNode("i", {
                              class: "bi bi-cloud-upload",
                              style: { "font-size": "36px", "color": "var(--el-color-primary)" }
                            }, null, -1)),
                            _cache[9] || (_cache[9] = createBaseVNode("div", { class: "el-upload__text" }, [
                              createTextVNode(" 拖拽文件到此处或 "),
                              createBaseVNode("em", null, "点击上传")
                            ], -1))
                          ]),
                          _: 1
                        }, 8, ["file-list"]),
                        uploadedFile.value ? (openBlock(), createElementBlock("div", _hoisted_8$1, [
                          createVNode(_component_el_alert, {
                            type: "success",
                            closable: false
                          }, {
                            title: withCtx(() => [
                              createBaseVNode("div", _hoisted_9$1, [
                                createBaseVNode("span", null, [
                                  _cache[10] || (_cache[10] = createBaseVNode("i", { class: "bi bi-check-circle-fill me-2" }, null, -1)),
                                  createTextVNode(" 已选择文件: " + toDisplayString(uploadedFile.value.name), 1)
                                ]),
                                createVNode(_component_el_button, {
                                  type: "primary",
                                  size: "small",
                                  loading: parsing.value,
                                  onClick: handleParse
                                }, {
                                  default: withCtx(() => [
                                    !parsing.value ? (openBlock(), createElementBlock("i", _hoisted_10$1)) : createCommentVNode("", true),
                                    createTextVNode(" " + toDisplayString(parsing.value ? "解析中..." : "解析文档结构"), 1)
                                  ]),
                                  _: 1
                                }, 8, ["loading"])
                              ])
                            ]),
                            _: 1
                          })
                        ])) : createCommentVNode("", true)
                      ]))
                    ])
                  ]),
                  _: 1
                })
              ]),
              _: 1
            }),
            createVNode(_component_el_col, {
              xs: 24,
              sm: 24,
              md: 14,
              lg: 14
            }, {
              default: withCtx(() => [
                chapters.value.length > 0 ? (openBlock(), createBlock(_component_el_card, {
                  key: 0,
                  shadow: "hover",
                  class: "step-card"
                }, {
                  header: withCtx(() => [
                    createBaseVNode("div", _hoisted_11$1, [
                      _cache[11] || (_cache[11] = createBaseVNode("i", { class: "bi bi-list-nested me-2 text-success" }, null, -1)),
                      _cache[12] || (_cache[12] = createBaseVNode("span", { class: "step-title" }, "步骤2: 选择章节", -1)),
                      selectedCount.value > 0 ? (openBlock(), createBlock(_component_el_tag, {
                        key: 0,
                        type: "success",
                        size: "small",
                        class: "ms-2"
                      }, {
                        default: withCtx(() => [
                          createTextVNode(" 已选 " + toDisplayString(selectedCount.value) + " 个 ", 1)
                        ]),
                        _: 1
                      })) : createCommentVNode("", true)
                    ])
                  ]),
                  default: withCtx(() => [
                    createBaseVNode("div", _hoisted_12$1, [
                      createBaseVNode("div", _hoisted_13$1, [
                        createBaseVNode("div", _hoisted_14$1, [
                          _cache[13] || (_cache[13] = createBaseVNode("div", { class: "stat-label" }, "总章节数", -1)),
                          createBaseVNode("div", _hoisted_15$1, toDisplayString(totalChapters.value), 1)
                        ]),
                        createBaseVNode("div", _hoisted_16$1, [
                          _cache[14] || (_cache[14] = createBaseVNode("div", { class: "stat-label" }, "已选择", -1)),
                          createBaseVNode("div", _hoisted_17$1, toDisplayString(selectedCount.value), 1)
                        ]),
                        createBaseVNode("div", _hoisted_18$1, [
                          _cache[15] || (_cache[15] = createBaseVNode("div", { class: "stat-label" }, "选中字数", -1)),
                          createBaseVNode("div", _hoisted_19$1, toDisplayString(formatWordCount(selectedWordCount.value)), 1)
                        ])
                      ]),
                      createBaseVNode("div", _hoisted_20$1, [
                        createVNode(_component_el_button_group, null, {
                          default: withCtx(() => [
                            createVNode(_component_el_button, {
                              size: "small",
                              onClick: handleSelectAll
                            }, {
                              default: withCtx(() => [..._cache[16] || (_cache[16] = [
                                createBaseVNode("i", { class: "bi bi-check-all me-1" }, null, -1),
                                createTextVNode(" 全选 ", -1)
                              ])]),
                              _: 1
                            }),
                            createVNode(_component_el_button, {
                              size: "small",
                              onClick: handleUnselectAll
                            }, {
                              default: withCtx(() => [..._cache[17] || (_cache[17] = [
                                createBaseVNode("i", { class: "bi bi-x me-1" }, null, -1),
                                createTextVNode(" 全不选 ", -1)
                              ])]),
                              _: 1
                            }),
                            createVNode(_component_el_button, {
                              size: "small",
                              type: "success",
                              onClick: handleSelectTech
                            }, {
                              default: withCtx(() => [..._cache[18] || (_cache[18] = [
                                createBaseVNode("i", { class: "bi bi-cpu me-1" }, null, -1),
                                createTextVNode(" 仅选技术章节 ", -1)
                              ])]),
                              _: 1
                            }),
                            createVNode(_component_el_button, {
                              size: "small",
                              type: "warning",
                              onClick: handleExcludeContract
                            }, {
                              default: withCtx(() => [..._cache[19] || (_cache[19] = [
                                createBaseVNode("i", { class: "bi bi-file-x me-1" }, null, -1),
                                createTextVNode(" 排除合同条款 ", -1)
                              ])]),
                              _: 1
                            })
                          ]),
                          _: 1
                        })
                      ]),
                      createVNode(ChapterTree, {
                        ref_key: "chapterTreeRef",
                        ref: chapterTreeRef,
                        chapters: chapters.value,
                        onCheck: handleChapterCheck
                      }, null, 8, ["chapters"]),
                      createBaseVNode("div", _hoisted_21$1, [
                        createVNode(_component_el_space, { size: 16 }, {
                          default: withCtx(() => [
                            createVNode(_component_el_button, {
                              type: "info",
                              size: "large",
                              disabled: selectedCount.value === 0,
                              loading: savingResponse.value,
                              onClick: handleSaveAsResponse
                            }, {
                              default: withCtx(() => [..._cache[20] || (_cache[20] = [
                                createBaseVNode("i", { class: "bi bi-file-earmark-arrow-down me-1" }, null, -1),
                                createTextVNode(" 另存为应答文件 ", -1)
                              ])]),
                              _: 1
                            }, 8, ["disabled", "loading"]),
                            createVNode(_component_el_button, {
                              type: "success",
                              size: "large",
                              disabled: selectedCount.value === 0,
                              loading: savingTechnical.value,
                              onClick: handleSaveAsTechnical
                            }, {
                              default: withCtx(() => [..._cache[21] || (_cache[21] = [
                                createBaseVNode("i", { class: "bi bi-file-code me-1" }, null, -1),
                                createTextVNode(" 另存为技术需求 ", -1)
                              ])]),
                              _: 1
                            }, 8, ["disabled", "loading"])
                          ]),
                          _: 1
                        })
                      ])
                    ])
                  ]),
                  _: 1
                })) : createCommentVNode("", true)
              ]),
              _: 1
            })
          ]),
          _: 1
        }),
        parsing.value ? (openBlock(), createElementBlock("div", _hoisted_22$1, [
          createVNode(_component_el_alert, {
            type: "info",
            closable: false
          }, {
            title: withCtx(() => [
              createBaseVNode("div", _hoisted_23$1, [
                createVNode(_component_el_icon, { class: "is-loading me-2" }, {
                  default: withCtx(() => [
                    createVNode(unref(loading_default))
                  ]),
                  _: 1
                }),
                createBaseVNode("span", null, toDisplayString(parsingMessage.value), 1)
              ])
            ]),
            _: 1
          })
        ])) : createCommentVNode("", true)
      ]);
    };
  }
});
const TenderDocumentProcessor = /* @__PURE__ */ _export_sfc(_sfc_main$1, [["__scopeId", "data-v-e1144ac8"]]);
const _hoisted_1 = { class: "tender-management-detail" };
const _hoisted_2 = { class: "tab-content" };
const _hoisted_3 = { class: "info-section" };
const _hoisted_4 = { class: "section-header" };
const _hoisted_5 = { class: "info-section" };
const _hoisted_6 = { class: "section-header" };
const _hoisted_7 = {
  key: 0,
  class: "bi bi-magic me-1"
};
const _hoisted_8 = {
  key: 0,
  class: "amount"
};
const _hoisted_9 = { key: 1 };
const _hoisted_10 = { class: "tab-content" };
const _hoisted_11 = { class: "info-section" };
const _hoisted_12 = { class: "section-header" };
const _hoisted_13 = {
  key: 0,
  class: "bi bi-magic me-1"
};
const _hoisted_14 = {
  key: 0,
  class: "requirements-list"
};
const _hoisted_15 = { class: "requirement-content" };
const _hoisted_16 = { class: "requirement-text" };
const _hoisted_17 = { key: 0 };
const _hoisted_18 = { key: 1 };
const _hoisted_19 = { class: "requirement-status" };
const _hoisted_20 = { class: "info-section" };
const _hoisted_21 = {
  key: 0,
  class: "requirements-list"
};
const _hoisted_22 = { class: "requirement-content" };
const _hoisted_23 = { class: "requirement-text" };
const _hoisted_24 = { key: 0 };
const _hoisted_25 = { key: 1 };
const _hoisted_26 = { key: 2 };
const _hoisted_27 = { class: "requirement-status" };
const _hoisted_28 = { class: "info-section" };
const _hoisted_29 = {
  key: 0,
  class: "requirements-list"
};
const _hoisted_30 = { class: "requirement-content" };
const _hoisted_31 = { class: "requirement-text" };
const _hoisted_32 = { key: 0 };
const _hoisted_33 = { key: 1 };
const _hoisted_34 = { key: 2 };
const _hoisted_35 = { class: "requirement-status" };
const _hoisted_36 = { class: "info-section" };
const _hoisted_37 = {
  key: 0,
  class: "financial-requirements"
};
const _hoisted_38 = { class: "requirement-content" };
const _hoisted_39 = { class: "requirement-text" };
const _hoisted_40 = { class: "tab-label" };
const _hoisted_41 = { class: "tab-content" };
const _hoisted_42 = { class: "file-section" };
const _hoisted_43 = { class: "section-header" };
const _hoisted_44 = { class: "file-section" };
const _hoisted_45 = { class: "section-header" };
const _hoisted_46 = { class: "action-area" };
const _hoisted_47 = { class: "tab-label" };
const _hoisted_48 = { class: "tab-content" };
const _hoisted_49 = { class: "info-section" };
const _hoisted_50 = { class: "section-header" };
const _hoisted_51 = {
  key: 0,
  class: "documents-grid"
};
const _hoisted_52 = {
  key: 1,
  class: "info-section"
};
const _hoisted_53 = { class: "section-header" };
const _hoisted_54 = { class: "tab-label" };
const _hoisted_55 = { class: "tab-content" };
const _hoisted_56 = { class: "file-section" };
const _hoisted_57 = { class: "section-header" };
const _hoisted_58 = { class: "file-section" };
const _hoisted_59 = { class: "section-header" };
const _hoisted_60 = { class: "file-section" };
const _hoisted_61 = { class: "section-header" };
const _hoisted_62 = { class: "action-area" };
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "ManagementDetail",
  setup(__props) {
    const route = useRoute();
    const router = useRouter();
    const projectStore = useProjectStore();
    const loading = ref(false);
    const saving = ref(false);
    const isEditing = ref(false);
    const projectDetail = ref(null);
    const activeTab = ref("basic");
    const companies = ref([]);
    const extractingBasicInfo = ref(false);
    const extractingQualifications = ref(false);
    const projectDocuments = ref([]);
    const parsedChapters = ref([]);
    const hasUnsavedChanges = ref(false);
    const previewVisible = ref(false);
    const previewFileUrl = ref("");
    const previewFileName = ref("");
    const formData = reactive({
      name: "",
      number: "",
      company_id: null,
      tenderer: "",
      agency: "",
      bidding_method: "",
      bidding_location: "",
      bidding_time: "",
      budget_amount: null,
      business_contact_name: "",
      business_contact_phone: "",
      tenderer_contact_person: "",
      // 招标方联系人
      tenderer_contact_method: "",
      // 招标方联系方式
      agency_contact_person: "",
      // 代理机构联系人
      agency_contact_method: "",
      // 代理机构联系方式
      authorized_person_name: "",
      authorized_person_id: ""
    });
    const formRules = {
      name: [{ required: true, message: "请输入项目名称", trigger: "blur" }],
      number: [{ required: true, message: "请输入项目编号", trigger: "blur" }],
      company_id: [{ required: true, message: "请选择公司", trigger: "change" }]
    };
    const projectId = computed(() => Number(route.params.id));
    const pageTitle = computed(() => {
      var _a;
      return ((_a = projectDetail.value) == null ? void 0 : _a.name) || "项目详情";
    });
    const totalParsedChapters = computed(() => {
      const countChapters = (chapters) => {
        let count = chapters.length;
        chapters.forEach((chapter) => {
          if (chapter.children && chapter.children.length > 0) {
            count += countChapters(chapter.children);
          }
        });
        return count;
      };
      return countChapters(parsedChapters.value);
    });
    const getFileInfo = (fileData) => {
      if (!fileData) return null;
      if (typeof fileData === "string") {
        return {
          fileUrl: fileData,
          fileName: void 0,
          fileSize: void 0
        };
      }
      return {
        fileUrl: fileData.file_url || fileData.download_url || fileData.file_path || "",
        // 优先使用file_url和download_url
        fileName: fileData.filename || fileData.file_name,
        fileSize: fileData.file_size
      };
    };
    const responseFileInfo = computed(() => {
      var _a, _b;
      return getFileInfo((_b = (_a = projectDetail.value) == null ? void 0 : _a.step1_data) == null ? void 0 : _b.response_file_path);
    });
    const businessResponseFileInfo = computed(() => {
      var _a, _b;
      return getFileInfo((_b = (_a = projectDetail.value) == null ? void 0 : _a.step1_data) == null ? void 0 : _b.business_response_file);
    });
    const technicalFileInfo = computed(() => {
      var _a, _b;
      return getFileInfo((_b = (_a = projectDetail.value) == null ? void 0 : _a.step1_data) == null ? void 0 : _b.technical_file_path);
    });
    const technicalP2PFileInfo = computed(() => {
      var _a, _b;
      return getFileInfo((_b = (_a = projectDetail.value) == null ? void 0 : _a.step1_data) == null ? void 0 : _b.technical_point_to_point_file);
    });
    const technicalProposalFileInfo = computed(() => {
      var _a, _b;
      return getFileInfo((_b = (_a = projectDetail.value) == null ? void 0 : _a.step1_data) == null ? void 0 : _b.technical_proposal_file);
    });
    const qualificationNameMapping = {
      // 基础资质类
      "business_license": "营业执照信息",
      "legal_id_front": "法人身份证正面",
      "legal_id_back": "法人身份证反面",
      "auth_id_front": "被授权人身份证正面",
      "auth_id_back": "被授权人身份证反面",
      "authorization_letter": "法人授权委托书",
      // 认证证书类
      "iso9001": "ISO9001质量管理体系认证",
      "iso20000": "ISO20000信息技术服务管理体系认证",
      "iso27001": "ISO27001信息安全管理体系认证",
      "cmmi": "CMMI能力成熟度认证",
      "itss": "ITSS信息技术服务标准认证",
      // 行业资质类
      "telecom_license": "电信业务许可证",
      "value_added_telecom_license": "增值电信业务许可证",
      "basic_telecom_license": "基础电信业务许可证",
      "level_protection": "等级保护认证",
      "software_copyright": "软件著作权",
      "patent_certificate": "专利证书",
      "audit_report": "财务要求",
      "project_performance": "项目业绩要求",
      // 社保和信用资质类
      "social_security": "社会保险证明",
      "dishonest_executor": "失信被执行人",
      "tax_violation_check": "重大税收违法",
      "gov_procurement_creditchina": "政府采购严重违法失信记录（信用中国）",
      "gov_procurement_ccgp": "政府采购严重违法失信记录（政府采购网）",
      "tax_compliance": "依法纳税",
      "commitment_letter": "承诺函",
      "property_certificate": "营业办公场所房产证明",
      "deposit_requirement": "保证金要求",
      "purchaser_blacklist": "采购人黑名单"
    };
    const getQualificationDisplayName = (nameOrKey) => {
      if (qualificationNameMapping[nameOrKey]) {
        return qualificationNameMapping[nameOrKey];
      }
      return nameOrKey;
    };
    const convertQualificationsData = (rawData) => {
      const certifications = [];
      const performance = [];
      const personnel = [];
      let financial = null;
      const certKeywords = ["ISO", "认证", "资质", "许可证", "证书", "等保", "著作权", "专利", "信用"];
      const perfKeywords = ["业绩", "项目", "案例", "合同"];
      const personnelKeywords = ["人员", "项目经理", "技术负责人", "工程师"];
      const financialKeywords = ["财务", "资本", "资产", "审计", "银行", "注册资金", "营业额"];
      Object.entries(rawData).forEach(([key, value]) => {
        const isRequired = value.constraint_type === "mandatory";
        const detail = value.detail || "";
        const summary = value.summary || key;
        if (financialKeywords.some((kw) => key.includes(kw))) {
          if (!financial) {
            financial = {
              description: []
            };
          }
          financial.description.push(`${summary}: ${detail}`);
        } else if (perfKeywords.some((kw) => key.includes(kw))) {
          performance.push({
            description: summary,
            detail,
            required: isRequired
          });
        } else if (personnelKeywords.some((kw) => key.includes(kw))) {
          personnel.push({
            position: summary,
            detail,
            required: isRequired
          });
        } else if (certKeywords.some((kw) => key.includes(kw))) {
          certifications.push({
            name: summary,
            note: detail,
            required: isRequired
          });
        } else {
          certifications.push({
            name: summary,
            note: detail,
            required: isRequired
          });
        }
      });
      if (financial && financial.description) {
        financial.description = financial.description.join("；");
      }
      return {
        certifications,
        performance,
        personnel,
        financial
      };
    };
    const qualifications = computed(() => {
      var _a;
      const rawData = (_a = projectDetail.value) == null ? void 0 : _a.qualifications_data;
      if (rawData && typeof rawData === "object" && Object.keys(rawData).length > 0) {
        return convertQualificationsData(rawData);
      }
      return {
        certifications: [],
        performance: [],
        personnel: [],
        financial: null
      };
    });
    const loadProjectDetail = async () => {
      if (!projectId.value) return;
      loading.value = true;
      try {
        const response = await tenderApi.getProject(projectId.value);
        const rawData = response.data;
        projectDetail.value = {
          id: rawData.project_id,
          name: rawData.project_name,
          number: rawData.project_number,
          company_id: rawData.company_id,
          company_name: rawData.company_name,
          status: rawData.status,
          created_at: rawData.created_at,
          updated_at: rawData.updated_at,
          authorized_person_name: rawData.authorized_person_name,
          authorized_person_id: rawData.authorized_person_id,
          // 招标信息
          tenderer: rawData.tenderer,
          agency: rawData.agency,
          bidding_method: rawData.bidding_method,
          bidding_location: rawData.bidding_location,
          bidding_time: rawData.bidding_time,
          budget_amount: rawData.budget_amount,
          // 联系人信息
          business_contact_name: rawData.business_contact_name,
          business_contact_phone: rawData.business_contact_phone,
          tenderer_contact_person: rawData.tenderer_contact_person,
          tenderer_contact_method: rawData.tenderer_contact_method,
          agency_contact_person: rawData.agency_contact_person,
          agency_contact_method: rawData.agency_contact_method,
          // step1_data 包含 AI 提取的文件路径
          step1_data: rawData.step1_data,
          // 保留原始数据
          ...rawData
        };
        formData.name = projectDetail.value.name || "";
        formData.number = projectDetail.value.number || "";
        formData.company_id = projectDetail.value.company_id || null;
        formData.tenderer = projectDetail.value.tenderer || "";
        formData.agency = projectDetail.value.agency || "";
        formData.bidding_method = projectDetail.value.bidding_method || "";
        formData.bidding_location = projectDetail.value.bidding_location || "";
        formData.bidding_time = projectDetail.value.bidding_time || "";
        formData.budget_amount = projectDetail.value.budget_amount || null;
        formData.business_contact_name = projectDetail.value.business_contact_name || "";
        formData.business_contact_phone = projectDetail.value.business_contact_phone || "";
        formData.tenderer_contact_person = projectDetail.value.tenderer_contact_person || "";
        formData.tenderer_contact_method = projectDetail.value.tenderer_contact_method || "";
        formData.agency_contact_person = projectDetail.value.agency_contact_person || "";
        formData.agency_contact_method = projectDetail.value.agency_contact_method || "";
        formData.authorized_person_name = projectDetail.value.authorized_person_name || "";
        formData.authorized_person_id = projectDetail.value.authorized_person_id || "";
        if (rawData.step1_data) {
          try {
            const step1Data = typeof rawData.step1_data === "string" ? JSON.parse(rawData.step1_data) : rawData.step1_data;
            console.log("[项目详情] step1_data:", step1Data);
            console.log("[项目详情] chapters字段存在?", !!step1Data.chapters);
            console.log("[项目详情] chapters类型:", typeof step1Data.chapters);
            console.log("[项目详情] chapters内容:", step1Data.chapters);
            if (step1Data.chapters && Array.isArray(step1Data.chapters)) {
              const filterInvalidChapters = (chapters) => {
                return chapters.filter((ch) => {
                  if (ch.para_start_idx >= ch.para_end_idx) {
                    console.warn(`过滤异常章节: ${ch.title} (索引: ${ch.para_start_idx} >= ${ch.para_end_idx})`);
                    return false;
                  }
                  if (ch.word_count === 0) {
                    console.warn(`过滤0字章节: ${ch.title}`);
                    return false;
                  }
                  if (ch.children && Array.isArray(ch.children)) {
                    ch.children = filterInvalidChapters(ch.children);
                  }
                  return true;
                });
              };
              parsedChapters.value = filterInvalidChapters(step1Data.chapters);
              if (parsedChapters.value.length < step1Data.chapters.length) {
                console.info(
                  `已过滤 ${step1Data.chapters.length - parsedChapters.value.length} 个异常章节，剩余 ${parsedChapters.value.length} 个有效章节`
                );
              }
            }
            const docs = [];
            let docId = 1;
            if (rawData.tender_document_path) {
              docs.push({
                id: docId++,
                file_path: rawData.tender_document_path,
                file_url: rawData.tender_document_path,
                original_filename: "招标文档",
                document_type: "tender",
                uploaded_at: rawData.created_at
              });
            }
            if (step1Data.response_file_path) {
              docs.push({
                id: docId++,
                file_path: step1Data.response_file_path,
                file_url: step1Data.response_file_path,
                original_filename: step1Data.response_filename || "应答文件模板",
                document_type: "response_template",
                file_size: step1Data.response_file_size,
                uploaded_at: rawData.updated_at
              });
            }
            if (step1Data.technical_file_path) {
              docs.push({
                id: docId++,
                file_path: step1Data.technical_file_path,
                file_url: step1Data.technical_file_path,
                original_filename: step1Data.technical_filename || "技术需求文件",
                document_type: "technical",
                file_size: step1Data.technical_file_size,
                uploaded_at: rawData.updated_at
              });
            }
            if (step1Data.business_response_file) {
              const businessFile = typeof step1Data.business_response_file === "string" ? { file_path: step1Data.business_response_file } : step1Data.business_response_file;
              docs.push({
                id: docId++,
                file_path: businessFile.file_path || businessFile.file_url,
                file_url: businessFile.file_url || businessFile.file_path,
                original_filename: businessFile.file_name || "商务应答完成文件",
                document_type: "business_response",
                file_size: businessFile.file_size,
                uploaded_at: rawData.updated_at
              });
            }
            if (step1Data.technical_point_to_point_file) {
              const techP2PFile = typeof step1Data.technical_point_to_point_file === "string" ? { file_path: step1Data.technical_point_to_point_file } : step1Data.technical_point_to_point_file;
              docs.push({
                id: docId++,
                file_path: techP2PFile.file_path || techP2PFile.file_url,
                file_url: techP2PFile.file_url || techP2PFile.file_path,
                original_filename: techP2PFile.file_name || "技术点对点应答文件",
                document_type: "technical_p2p",
                file_size: techP2PFile.file_size,
                uploaded_at: rawData.updated_at
              });
            }
            if (step1Data.technical_proposal_file) {
              const techProposalFile = typeof step1Data.technical_proposal_file === "string" ? { file_path: step1Data.technical_proposal_file } : step1Data.technical_proposal_file;
              docs.push({
                id: docId++,
                file_path: techProposalFile.file_path || techProposalFile.file_url,
                file_url: techProposalFile.file_url || techProposalFile.file_path,
                original_filename: techProposalFile.file_name || "技术方案文件",
                document_type: "technical_proposal",
                file_size: techProposalFile.file_size,
                uploaded_at: rawData.updated_at
              });
            }
            projectDocuments.value = docs;
          } catch (e) {
            console.warn("解析文档和章节数据失败:", e);
          }
        }
        if (projectDetail.value.name === "新项目" || projectDetail.value.status === "draft") {
          isEditing.value = true;
        }
        if (projectDetail.value) {
          projectStore.setCurrentProject(projectDetail.value);
          console.log("✅ 项目详情已同步到全局Store:", projectDetail.value.id, projectDetail.value.name);
        }
      } catch (error) {
        console.error("加载项目详情失败:", error);
        ElMessage.error("加载项目详情失败");
      } finally {
        loading.value = false;
      }
    };
    const loadCompanies = async () => {
      try {
        const response = await companyApi.getCompanies();
        companies.value = response.data || [];
      } catch (error) {
        console.error("加载公司列表失败:", error);
      }
    };
    const formatAmount = (amount) => {
      return amount.toLocaleString("zh-CN", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      });
    };
    const getStatusType = (status) => {
      const map = {
        active: "success",
        completed: "primary",
        draft: "info"
      };
      return map[status] || "info";
    };
    const getStatusText = (status) => {
      const map = {
        active: "进行中",
        completed: "已完成",
        draft: "草稿"
      };
      return map[status] || status;
    };
    const handleRefresh = () => {
      loadProjectDetail();
    };
    const handleEdit = () => {
      isEditing.value = true;
    };
    const handleCancel = () => {
      ElMessageBox.confirm("确定要取消编辑吗？未保存的更改将丢失", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      }).then(() => {
        loadProjectDetail();
        isEditing.value = false;
      }).catch(() => {
      });
    };
    const handleSave = async () => {
      var _a, _b;
      saving.value = true;
      try {
        const updateData = {
          project_name: formData.name,
          project_number: formData.number,
          company_id: formData.company_id,
          tenderer: formData.tenderer,
          agency: formData.agency,
          bidding_method: formData.bidding_method,
          bidding_location: formData.bidding_location,
          bidding_time: formData.bidding_time,
          budget_amount: formData.budget_amount,
          business_contact_name: formData.business_contact_name,
          business_contact_phone: formData.business_contact_phone,
          tenderer_contact_person: formData.tenderer_contact_person,
          tenderer_contact_method: formData.tenderer_contact_method,
          agency_contact_person: formData.agency_contact_person,
          agency_contact_method: formData.agency_contact_method,
          authorized_person_name: formData.authorized_person_name,
          authorized_person_id: formData.authorized_person_id,
          status: "active"
          // 保存后更新为活跃状态
        };
        await tenderApi.updateProject(projectId.value, updateData);
        ElMessage.success("保存成功");
        isEditing.value = false;
        hasUnsavedChanges.value = false;
        await loadProjectDetail();
      } catch (error) {
        console.error("保存失败:", error);
        const errorMessage = ((_b = (_a = error == null ? void 0 : error.response) == null ? void 0 : _a.data) == null ? void 0 : _b.message) || (error == null ? void 0 : error.message) || "保存失败，请检查项目名称和编号是否与其他项目重复";
        ElMessage.error({
          message: errorMessage,
          duration: 5e3,
          showClose: true
        });
      } finally {
        saving.value = false;
      }
    };
    const handleStartBusiness = async () => {
      var _a;
      if (!projectDetail.value) return;
      const responseFileUrl = (_a = projectDetail.value.step1_data) == null ? void 0 : _a.response_file_path;
      if (!responseFileUrl) {
        ElMessage.warning("未找到应答文件模板");
        return;
      }
      projectStore.setCurrentProject(projectDetail.value);
      await router.push({
        name: "BusinessResponse"
      });
    };
    const handleStartPointToPoint = async () => {
      var _a;
      if (!projectDetail.value) return;
      const technicalFileUrl = (_a = projectDetail.value.step1_data) == null ? void 0 : _a.technical_file_path;
      if (!technicalFileUrl) {
        ElMessage.warning("未找到技术需求文件");
        return;
      }
      projectStore.setCurrentProject(projectDetail.value);
      await router.push({
        name: "PointToPoint"
      });
    };
    const handleStartProposal = async () => {
      var _a;
      if (!projectDetail.value) return;
      const technicalFileUrl = (_a = projectDetail.value.step1_data) == null ? void 0 : _a.technical_file_path;
      if (!technicalFileUrl) {
        ElMessage.warning("未找到技术需求文件");
        return;
      }
      projectStore.setCurrentProject(projectDetail.value);
      await router.push({
        name: "TechProposal"
      });
    };
    const handleProcessSuccess = async (type) => {
      await loadProjectDetail();
      if (type === "response") {
        ElMessage.success("应答文件已保存，可以开始商务应答处理");
        activeTab.value = "business";
      } else if (type === "technical") {
        ElMessage.success("技术需求已保存，可以开始技术方案编写");
        activeTab.value = "technical";
      }
    };
    const handleExtractBasicInfo = async () => {
      if (!projectId.value) {
        ElMessage.warning("请先上传并解析招标文档");
        return;
      }
      extractingBasicInfo.value = true;
      try {
        const response = await tenderApi.extractBasicInfo(projectId.value);
        if (response.success && response.data) {
          const info = response.data;
          console.log("AI提取API返回的原始数据:", response.data);
          console.log("info对象:", info);
          console.log("project_name:", info.project_name);
          console.log("project_number:", info.project_number);
          Object.assign(formData, {
            name: info.project_name || formData.name,
            number: info.project_number || formData.number,
            tenderer: info.tender_party || formData.tenderer,
            agency: info.tender_agent || formData.agency,
            bidding_method: info.tender_method || formData.bidding_method,
            bidding_location: info.tender_location || formData.bidding_location,
            bidding_time: info.tender_deadline || formData.bidding_time,
            tenderer_contact_person: info.tenderer_contact_person || formData.tenderer_contact_person,
            tenderer_contact_method: info.tenderer_contact_method || formData.tenderer_contact_method,
            agency_contact_person: info.agency_contact_person || formData.agency_contact_person,
            agency_contact_method: info.agency_contact_method || formData.agency_contact_method
          });
          if (projectDetail.value) {
            Object.assign(projectDetail.value, {
              name: info.project_name || projectDetail.value.name,
              number: info.project_number || projectDetail.value.number,
              tenderer: info.tender_party || projectDetail.value.tenderer,
              agency: info.tender_agent || projectDetail.value.agency,
              bidding_method: info.tender_method || projectDetail.value.bidding_method,
              bidding_location: info.tender_location || projectDetail.value.bidding_location,
              bidding_time: info.tender_deadline || projectDetail.value.bidding_time,
              tenderer_contact_person: info.tenderer_contact_person || projectDetail.value.tenderer_contact_person,
              tenderer_contact_method: info.tenderer_contact_method || projectDetail.value.tenderer_contact_method,
              agency_contact_person: info.agency_contact_person || projectDetail.value.agency_contact_person,
              agency_contact_method: info.agency_contact_method || projectDetail.value.agency_contact_method
            });
          }
          if (!isEditing.value) {
            isEditing.value = true;
          }
          hasUnsavedChanges.value = true;
          ElMessage.success({
            message: "AI提取基本信息成功，已进入编辑模式，请检查信息后手动保存",
            duration: 5e3,
            showClose: true
          });
          setTimeout(() => {
            const basicInfoSection = document.querySelector(".info-section");
            if (basicInfoSection) {
              basicInfoSection.scrollIntoView({ behavior: "smooth", block: "start" });
            }
          }, 300);
        } else {
          throw new Error(response.error || "AI提取失败");
        }
      } catch (error) {
        console.error("AI提取基本信息失败:", error);
        ElMessage.error(`AI提取失败: ${error instanceof Error ? error.message : "未知错误"}`);
      } finally {
        extractingBasicInfo.value = false;
      }
    };
    const handleExtractQualifications = async () => {
      if (!projectId.value) {
        ElMessage.warning("请先上传并解析招标文档");
        return;
      }
      extractingQualifications.value = true;
      try {
        const response = await tenderApi.extractQualifications(projectId.value);
        if (response.success) {
          ElMessage.success("AI提取资格要求成功，正在刷新数据...");
          await loadProjectDetail();
          ElMessage.success("资格要求已更新");
        } else {
          throw new Error(response.error || "AI提取失败");
        }
      } catch (error) {
        console.error("AI提取资格要求失败:", error);
        ElMessage.error(`AI提取失败: ${error instanceof Error ? error.message : "未知错误"}`);
      } finally {
        extractingQualifications.value = false;
      }
    };
    const handlePreview = (fileUrl, fileName) => {
      previewFileUrl.value = fileUrl;
      previewFileName.value = fileName;
      previewVisible.value = true;
    };
    watch(() => formData.company_id, (newCompanyId) => {
      if (newCompanyId && companies.value.length > 0) {
        const selectedCompany = companies.value.find((c) => c.company_id === newCompanyId);
        if (selectedCompany) {
          formData.authorized_person_name = selectedCompany.authorized_person_name || "";
          formData.authorized_person_id = selectedCompany.authorized_person_id || "";
          if (projectDetail.value) {
            projectDetail.value.authorized_person_name = selectedCompany.authorized_person_name || "";
            projectDetail.value.authorized_person_id = selectedCompany.authorized_person_id || "";
          }
          if (selectedCompany.authorized_person_name) {
            ElMessage.success(`已自动填充被授权人信息: ${selectedCompany.authorized_person_name}`);
          }
        }
      }
    });
    watch(() => route.params.id, () => {
      loadProjectDetail();
    });
    onMounted(() => {
      loadCompanies();
      loadProjectDetail();
    });
    return (_ctx, _cache) => {
      const _component_el_button = ElButton;
      const _component_el_tag = ElTag;
      const _component_el_input = ElInput;
      const _component_el_form_item = ElFormItem;
      const _component_el_col = ElCol;
      const _component_el_option = ElOption;
      const _component_el_select = ElSelect;
      const _component_el_row = ElRow;
      const _component_el_form = ElForm;
      const _component_el_descriptions_item = ElDescriptionsItem;
      const _component_el_descriptions = ElDescriptions;
      const _component_el_input_number = ElInputNumber;
      const _component_el_tab_pane = ElTabPane;
      const _component_el_card = ElCard;
      const _component_el_empty = ElEmpty;
      const _component_el_badge = ElBadge;
      const _component_el_text = ElText;
      const _component_el_divider = ElDivider;
      const _component_el_space = ElSpace;
      const _component_el_tabs = ElTabs;
      return openBlock(), createElementBlock("div", _hoisted_1, [
        createVNode(unref(PageHeader), {
          title: pageTitle.value,
          "show-back": true
        }, {
          actions: withCtx(() => [
            !isEditing.value ? (openBlock(), createElementBlock(Fragment, { key: 0 }, [
              createVNode(_component_el_button, { onClick: handleRefresh }, {
                default: withCtx(() => [..._cache[17] || (_cache[17] = [
                  createBaseVNode("i", { class: "bi bi-arrow-clockwise" }, null, -1),
                  createTextVNode(" 刷新 ", -1)
                ])]),
                _: 1
              }),
              createVNode(_component_el_button, {
                type: "primary",
                onClick: handleEdit
              }, {
                default: withCtx(() => [..._cache[18] || (_cache[18] = [
                  createBaseVNode("i", { class: "bi bi-pencil" }, null, -1),
                  createTextVNode(" 编辑项目 ", -1)
                ])]),
                _: 1
              })
            ], 64)) : (openBlock(), createElementBlock(Fragment, { key: 1 }, [
              createVNode(_component_el_button, { onClick: handleCancel }, {
                default: withCtx(() => [..._cache[19] || (_cache[19] = [
                  createBaseVNode("i", { class: "bi bi-x-lg" }, null, -1),
                  createTextVNode(" 取消 ", -1)
                ])]),
                _: 1
              }),
              createVNode(_component_el_button, {
                type: "primary",
                loading: saving.value,
                onClick: handleSave
              }, {
                default: withCtx(() => [..._cache[20] || (_cache[20] = [
                  createBaseVNode("i", { class: "bi bi-check-lg" }, null, -1),
                  createTextVNode(" 保存 ", -1)
                ])]),
                _: 1
              }, 8, ["loading"])
            ], 64))
          ]),
          _: 1
        }, 8, ["title"]),
        loading.value ? (openBlock(), createBlock(unref(Loading), {
          key: 0,
          text: "加载项目详情..."
        })) : projectDetail.value ? (openBlock(), createElementBlock(Fragment, { key: 1 }, [
          createVNode(TenderDocumentProcessor, {
            "project-id": projectId.value,
            "company-id": projectDetail.value.company_id,
            "project-detail": projectDetail.value,
            onSuccess: handleProcessSuccess,
            onRefresh: loadProjectDetail,
            onPreview: handlePreview
          }, null, 8, ["project-id", "company-id", "project-detail"]),
          createVNode(_component_el_card, {
            class: "tabs-card",
            shadow: "never"
          }, {
            default: withCtx(() => [
              createVNode(_component_el_tabs, {
                modelValue: activeTab.value,
                "onUpdate:modelValue": _cache[15] || (_cache[15] = ($event) => activeTab.value = $event),
                class: "detail-tabs"
              }, {
                default: withCtx(() => [
                  createVNode(_component_el_tab_pane, { name: "basic" }, {
                    label: withCtx(() => [..._cache[21] || (_cache[21] = [
                      createBaseVNode("span", { class: "tab-label" }, [
                        createBaseVNode("i", { class: "bi bi-info-circle" }),
                        createTextVNode(" 基本信息 ")
                      ], -1)
                    ])]),
                    default: withCtx(() => [
                      createBaseVNode("div", _hoisted_2, [
                        createBaseVNode("section", _hoisted_3, [
                          createBaseVNode("div", _hoisted_4, [
                            _cache[22] || (_cache[22] = createBaseVNode("h3", null, [
                              createBaseVNode("i", { class: "bi bi-folder" }),
                              createTextVNode(" 项目基本信息")
                            ], -1)),
                            createVNode(_component_el_tag, {
                              type: getStatusType(projectDetail.value.status)
                            }, {
                              default: withCtx(() => [
                                createTextVNode(toDisplayString(getStatusText(projectDetail.value.status)), 1)
                              ]),
                              _: 1
                            }, 8, ["type"])
                          ]),
                          isEditing.value ? (openBlock(), createBlock(_component_el_form, {
                            key: 0,
                            model: formData,
                            rules: formRules,
                            "label-width": "120px",
                            class: "edit-form"
                          }, {
                            default: withCtx(() => [
                              createVNode(_component_el_row, { gutter: 20 }, {
                                default: withCtx(() => [
                                  createVNode(_component_el_col, { span: 24 }, {
                                    default: withCtx(() => [
                                      createVNode(_component_el_form_item, {
                                        label: "项目名称",
                                        prop: "name"
                                      }, {
                                        default: withCtx(() => [
                                          createVNode(_component_el_input, {
                                            modelValue: formData.name,
                                            "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => formData.name = $event),
                                            placeholder: "请输入项目名称"
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
                                        label: "项目编号",
                                        prop: "number"
                                      }, {
                                        default: withCtx(() => [
                                          createVNode(_component_el_input, {
                                            modelValue: formData.number,
                                            "onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => formData.number = $event),
                                            placeholder: "请输入项目编号"
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
                                        label: "公司名称",
                                        prop: "company_id"
                                      }, {
                                        default: withCtx(() => [
                                          createVNode(_component_el_select, {
                                            modelValue: formData.company_id,
                                            "onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => formData.company_id = $event),
                                            placeholder: "请选择公司",
                                            style: { "width": "100%" }
                                          }, {
                                            default: withCtx(() => [
                                              (openBlock(true), createElementBlock(Fragment, null, renderList(companies.value, (company) => {
                                                return openBlock(), createBlock(_component_el_option, {
                                                  key: company.company_id,
                                                  label: company.name,
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
                                  }),
                                  createVNode(_component_el_col, { span: 12 }, {
                                    default: withCtx(() => [
                                      createVNode(_component_el_form_item, { label: "被授权人" }, {
                                        default: withCtx(() => [
                                          createVNode(_component_el_input, {
                                            modelValue: formData.authorized_person_name,
                                            "onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => formData.authorized_person_name = $event),
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
                                      createVNode(_component_el_form_item, { label: "授权人身份证" }, {
                                        default: withCtx(() => [
                                          createVNode(_component_el_input, {
                                            modelValue: formData.authorized_person_id,
                                            "onUpdate:modelValue": _cache[4] || (_cache[4] = ($event) => formData.authorized_person_id = $event),
                                            placeholder: "请输入身份证号"
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
                          }, 8, ["model"])) : (openBlock(), createBlock(_component_el_descriptions, {
                            key: 1,
                            column: 2,
                            border: "",
                            size: "large"
                          }, {
                            default: withCtx(() => [
                              createVNode(_component_el_descriptions_item, {
                                label: "项目名称",
                                span: 2
                              }, {
                                default: withCtx(() => [
                                  createBaseVNode("strong", null, toDisplayString(projectDetail.value.name), 1)
                                ]),
                                _: 1
                              }),
                              createVNode(_component_el_descriptions_item, { label: "项目编号" }, {
                                default: withCtx(() => [
                                  createTextVNode(toDisplayString(projectDetail.value.number || "-"), 1)
                                ]),
                                _: 1
                              }),
                              createVNode(_component_el_descriptions_item, { label: "公司名称" }, {
                                default: withCtx(() => [
                                  createTextVNode(toDisplayString(projectDetail.value.company_name), 1)
                                ]),
                                _: 1
                              }),
                              createVNode(_component_el_descriptions_item, { label: "创建时间" }, {
                                default: withCtx(() => [
                                  createTextVNode(toDisplayString(projectDetail.value.created_at), 1)
                                ]),
                                _: 1
                              }),
                              createVNode(_component_el_descriptions_item, { label: "最后更新" }, {
                                default: withCtx(() => [
                                  createTextVNode(toDisplayString(projectDetail.value.updated_at || "-"), 1)
                                ]),
                                _: 1
                              }),
                              createVNode(_component_el_descriptions_item, { label: "被授权人" }, {
                                default: withCtx(() => [
                                  createTextVNode(toDisplayString(projectDetail.value.authorized_person_name || "-"), 1)
                                ]),
                                _: 1
                              }),
                              createVNode(_component_el_descriptions_item, { label: "授权人身份证" }, {
                                default: withCtx(() => [
                                  createTextVNode(toDisplayString(projectDetail.value.authorized_person_id || "-"), 1)
                                ]),
                                _: 1
                              })
                            ]),
                            _: 1
                          }))
                        ]),
                        createBaseVNode("section", _hoisted_5, [
                          createBaseVNode("div", _hoisted_6, [
                            createBaseVNode("h3", null, [
                              _cache[24] || (_cache[24] = createBaseVNode("i", { class: "bi bi-megaphone" }, null, -1)),
                              _cache[25] || (_cache[25] = createTextVNode(" 招标信息 ", -1)),
                              hasUnsavedChanges.value && isEditing.value ? (openBlock(), createBlock(_component_el_tag, {
                                key: 0,
                                type: "warning",
                                size: "small",
                                style: { "margin-left": "10px" }
                              }, {
                                default: withCtx(() => [..._cache[23] || (_cache[23] = [
                                  createBaseVNode("i", { class: "bi bi-exclamation-triangle-fill" }, null, -1),
                                  createTextVNode(" 有未保存的更改 ", -1)
                                ])]),
                                _: 1
                              })) : createCommentVNode("", true)
                            ]),
                            createVNode(_component_el_button, {
                              size: "small",
                              type: "primary",
                              loading: extractingBasicInfo.value,
                              disabled: !projectId.value || extractingBasicInfo.value,
                              onClick: handleExtractBasicInfo
                            }, {
                              default: withCtx(() => [
                                !extractingBasicInfo.value ? (openBlock(), createElementBlock("i", _hoisted_7)) : createCommentVNode("", true),
                                createTextVNode(" " + toDisplayString(extractingBasicInfo.value ? "AI提取中..." : "AI提取基本信息"), 1)
                              ]),
                              _: 1
                            }, 8, ["loading", "disabled"])
                          ]),
                          isEditing.value ? (openBlock(), createBlock(_component_el_form, {
                            key: 0,
                            model: formData,
                            "label-width": "120px",
                            class: "edit-form"
                          }, {
                            default: withCtx(() => [
                              createVNode(_component_el_row, { gutter: 20 }, {
                                default: withCtx(() => [
                                  createVNode(_component_el_col, { span: 12 }, {
                                    default: withCtx(() => [
                                      createVNode(_component_el_form_item, { label: "招标单位" }, {
                                        default: withCtx(() => [
                                          createVNode(_component_el_input, {
                                            modelValue: formData.tenderer,
                                            "onUpdate:modelValue": _cache[5] || (_cache[5] = ($event) => formData.tenderer = $event),
                                            placeholder: "请输入招标单位"
                                          }, null, 8, ["modelValue"])
                                        ]),
                                        _: 1
                                      })
                                    ]),
                                    _: 1
                                  }),
                                  createVNode(_component_el_col, { span: 12 }, {
                                    default: withCtx(() => [
                                      createVNode(_component_el_form_item, { label: "招标代理" }, {
                                        default: withCtx(() => [
                                          createVNode(_component_el_input, {
                                            modelValue: formData.agency,
                                            "onUpdate:modelValue": _cache[6] || (_cache[6] = ($event) => formData.agency = $event),
                                            placeholder: "请输入招标代理"
                                          }, null, 8, ["modelValue"])
                                        ]),
                                        _: 1
                                      })
                                    ]),
                                    _: 1
                                  }),
                                  createVNode(_component_el_col, { span: 12 }, {
                                    default: withCtx(() => [
                                      createVNode(_component_el_form_item, { label: "招标方式" }, {
                                        default: withCtx(() => [
                                          createVNode(_component_el_input, {
                                            modelValue: formData.bidding_method,
                                            "onUpdate:modelValue": _cache[7] || (_cache[7] = ($event) => formData.bidding_method = $event),
                                            placeholder: "请输入招标方式"
                                          }, null, 8, ["modelValue"])
                                        ]),
                                        _: 1
                                      })
                                    ]),
                                    _: 1
                                  }),
                                  createVNode(_component_el_col, { span: 12 }, {
                                    default: withCtx(() => [
                                      createVNode(_component_el_form_item, { label: "开标地点" }, {
                                        default: withCtx(() => [
                                          createVNode(_component_el_input, {
                                            modelValue: formData.bidding_location,
                                            "onUpdate:modelValue": _cache[8] || (_cache[8] = ($event) => formData.bidding_location = $event),
                                            placeholder: "请输入开标地点"
                                          }, null, 8, ["modelValue"])
                                        ]),
                                        _: 1
                                      })
                                    ]),
                                    _: 1
                                  }),
                                  createVNode(_component_el_col, { span: 12 }, {
                                    default: withCtx(() => [
                                      createVNode(_component_el_form_item, { label: "开标时间" }, {
                                        default: withCtx(() => [
                                          createVNode(_component_el_input, {
                                            modelValue: formData.bidding_time,
                                            "onUpdate:modelValue": _cache[9] || (_cache[9] = ($event) => formData.bidding_time = $event),
                                            placeholder: "请输入开标时间"
                                          }, null, 8, ["modelValue"])
                                        ]),
                                        _: 1
                                      })
                                    ]),
                                    _: 1
                                  }),
                                  createVNode(_component_el_col, { span: 12 }, {
                                    default: withCtx(() => [
                                      createVNode(_component_el_form_item, { label: "预算金额" }, {
                                        default: withCtx(() => [
                                          createVNode(_component_el_input_number, {
                                            modelValue: formData.budget_amount,
                                            "onUpdate:modelValue": _cache[10] || (_cache[10] = ($event) => formData.budget_amount = $event),
                                            controls: false,
                                            precision: 2,
                                            placeholder: "请输入预算金额",
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
                                      createVNode(_component_el_form_item, { label: "招标方联系人" }, {
                                        default: withCtx(() => [
                                          createVNode(_component_el_input, {
                                            modelValue: formData.tenderer_contact_person,
                                            "onUpdate:modelValue": _cache[11] || (_cache[11] = ($event) => formData.tenderer_contact_person = $event),
                                            placeholder: "请输入招标方联系人"
                                          }, null, 8, ["modelValue"])
                                        ]),
                                        _: 1
                                      })
                                    ]),
                                    _: 1
                                  }),
                                  createVNode(_component_el_col, { span: 12 }, {
                                    default: withCtx(() => [
                                      createVNode(_component_el_form_item, { label: "招标方联系电话" }, {
                                        default: withCtx(() => [
                                          createVNode(_component_el_input, {
                                            modelValue: formData.tenderer_contact_method,
                                            "onUpdate:modelValue": _cache[12] || (_cache[12] = ($event) => formData.tenderer_contact_method = $event),
                                            placeholder: "请输入招标方联系电话"
                                          }, null, 8, ["modelValue"])
                                        ]),
                                        _: 1
                                      })
                                    ]),
                                    _: 1
                                  }),
                                  createVNode(_component_el_col, { span: 12 }, {
                                    default: withCtx(() => [
                                      createVNode(_component_el_form_item, { label: "代理机构联系人" }, {
                                        default: withCtx(() => [
                                          createVNode(_component_el_input, {
                                            modelValue: formData.agency_contact_person,
                                            "onUpdate:modelValue": _cache[13] || (_cache[13] = ($event) => formData.agency_contact_person = $event),
                                            placeholder: "请输入代理机构联系人"
                                          }, null, 8, ["modelValue"])
                                        ]),
                                        _: 1
                                      })
                                    ]),
                                    _: 1
                                  }),
                                  createVNode(_component_el_col, { span: 12 }, {
                                    default: withCtx(() => [
                                      createVNode(_component_el_form_item, { label: "代理机构联系电话" }, {
                                        default: withCtx(() => [
                                          createVNode(_component_el_input, {
                                            modelValue: formData.agency_contact_method,
                                            "onUpdate:modelValue": _cache[14] || (_cache[14] = ($event) => formData.agency_contact_method = $event),
                                            placeholder: "请输入代理机构联系电话"
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
                          }, 8, ["model"])) : (openBlock(), createBlock(_component_el_descriptions, {
                            key: 1,
                            column: 2,
                            border: "",
                            size: "large"
                          }, {
                            default: withCtx(() => [
                              createVNode(_component_el_descriptions_item, { label: "招标单位" }, {
                                default: withCtx(() => [
                                  createTextVNode(toDisplayString(projectDetail.value.tenderer || "-"), 1)
                                ]),
                                _: 1
                              }),
                              createVNode(_component_el_descriptions_item, { label: "招标代理" }, {
                                default: withCtx(() => [
                                  createTextVNode(toDisplayString(projectDetail.value.agency || "-"), 1)
                                ]),
                                _: 1
                              }),
                              createVNode(_component_el_descriptions_item, { label: "招标方式" }, {
                                default: withCtx(() => [
                                  createTextVNode(toDisplayString(projectDetail.value.bidding_method || "-"), 1)
                                ]),
                                _: 1
                              }),
                              createVNode(_component_el_descriptions_item, { label: "开标地点" }, {
                                default: withCtx(() => [
                                  createTextVNode(toDisplayString(projectDetail.value.bidding_location || "-"), 1)
                                ]),
                                _: 1
                              }),
                              createVNode(_component_el_descriptions_item, { label: "开标时间" }, {
                                default: withCtx(() => [
                                  createTextVNode(toDisplayString(projectDetail.value.bidding_time || "-"), 1)
                                ]),
                                _: 1
                              }),
                              createVNode(_component_el_descriptions_item, { label: "预算金额" }, {
                                default: withCtx(() => [
                                  projectDetail.value.budget_amount ? (openBlock(), createElementBlock("span", _hoisted_8, " ¥ " + toDisplayString(formatAmount(projectDetail.value.budget_amount)), 1)) : (openBlock(), createElementBlock("span", _hoisted_9, "-"))
                                ]),
                                _: 1
                              }),
                              createVNode(_component_el_descriptions_item, { label: "招标方联系人" }, {
                                default: withCtx(() => [
                                  createTextVNode(toDisplayString(projectDetail.value.tenderer_contact_person || "-"), 1)
                                ]),
                                _: 1
                              }),
                              createVNode(_component_el_descriptions_item, { label: "招标方联系电话" }, {
                                default: withCtx(() => [
                                  createTextVNode(toDisplayString(projectDetail.value.tenderer_contact_method || "-"), 1)
                                ]),
                                _: 1
                              }),
                              createVNode(_component_el_descriptions_item, { label: "代理机构联系人" }, {
                                default: withCtx(() => [
                                  createTextVNode(toDisplayString(projectDetail.value.agency_contact_person || "-"), 1)
                                ]),
                                _: 1
                              }),
                              createVNode(_component_el_descriptions_item, { label: "代理机构联系电话" }, {
                                default: withCtx(() => [
                                  createTextVNode(toDisplayString(projectDetail.value.agency_contact_method || "-"), 1)
                                ]),
                                _: 1
                              })
                            ]),
                            _: 1
                          }))
                        ])
                      ])
                    ]),
                    _: 1
                  }),
                  createVNode(_component_el_tab_pane, { name: "qualifications" }, {
                    label: withCtx(() => [..._cache[26] || (_cache[26] = [
                      createBaseVNode("span", { class: "tab-label" }, [
                        createBaseVNode("i", { class: "bi bi-award" }),
                        createTextVNode(" 资格要求 ")
                      ], -1)
                    ])]),
                    default: withCtx(() => [
                      createBaseVNode("div", _hoisted_10, [
                        createBaseVNode("section", _hoisted_11, [
                          createBaseVNode("div", _hoisted_12, [
                            _cache[27] || (_cache[27] = createBaseVNode("h3", null, [
                              createBaseVNode("i", { class: "bi bi-patch-check" }),
                              createTextVNode(" 资质要求")
                            ], -1)),
                            createVNode(_component_el_button, {
                              size: "small",
                              type: "primary",
                              loading: extractingQualifications.value,
                              disabled: !projectId.value || extractingQualifications.value,
                              onClick: handleExtractQualifications
                            }, {
                              default: withCtx(() => [
                                !extractingQualifications.value ? (openBlock(), createElementBlock("i", _hoisted_13)) : createCommentVNode("", true),
                                createTextVNode(" " + toDisplayString(extractingQualifications.value ? "AI提取中..." : "AI提取资格要求"), 1)
                              ]),
                              _: 1
                            }, 8, ["loading", "disabled"])
                          ]),
                          qualifications.value.certifications.length > 0 ? (openBlock(), createElementBlock("div", _hoisted_14, [
                            (openBlock(true), createElementBlock(Fragment, null, renderList(qualifications.value.certifications, (cert, index) => {
                              return openBlock(), createBlock(_component_el_card, {
                                key: index,
                                shadow: "never",
                                class: "requirement-item"
                              }, {
                                default: withCtx(() => [
                                  createBaseVNode("div", _hoisted_15, [
                                    _cache[30] || (_cache[30] = createBaseVNode("div", { class: "requirement-icon" }, [
                                      createBaseVNode("i", { class: "bi bi-shield-check" })
                                    ], -1)),
                                    createBaseVNode("div", _hoisted_16, [
                                      createBaseVNode("h4", null, toDisplayString(getQualificationDisplayName(cert.name)), 1),
                                      cert.level ? (openBlock(), createElementBlock("p", _hoisted_17, "等级要求: " + toDisplayString(cert.level), 1)) : createCommentVNode("", true),
                                      cert.note ? (openBlock(), createElementBlock("p", _hoisted_18, toDisplayString(cert.note), 1)) : createCommentVNode("", true)
                                    ]),
                                    createBaseVNode("div", _hoisted_19, [
                                      cert.required ? (openBlock(), createBlock(_component_el_tag, {
                                        key: 0,
                                        type: "danger",
                                        size: "small"
                                      }, {
                                        default: withCtx(() => [..._cache[28] || (_cache[28] = [
                                          createTextVNode(" 必需 ", -1)
                                        ])]),
                                        _: 1
                                      })) : (openBlock(), createBlock(_component_el_tag, {
                                        key: 1,
                                        type: "info",
                                        size: "small"
                                      }, {
                                        default: withCtx(() => [..._cache[29] || (_cache[29] = [
                                          createTextVNode("可选", -1)
                                        ])]),
                                        _: 1
                                      }))
                                    ])
                                  ])
                                ]),
                                _: 2
                              }, 1024);
                            }), 128))
                          ])) : (openBlock(), createBlock(_component_el_empty, {
                            key: 1,
                            description: "暂无资质要求",
                            "image-size": 80
                          }))
                        ]),
                        createBaseVNode("section", _hoisted_20, [
                          _cache[34] || (_cache[34] = createBaseVNode("div", { class: "section-header" }, [
                            createBaseVNode("h3", null, [
                              createBaseVNode("i", { class: "bi bi-graph-up-arrow" }),
                              createTextVNode(" 业绩要求")
                            ])
                          ], -1)),
                          qualifications.value.performance.length > 0 ? (openBlock(), createElementBlock("div", _hoisted_21, [
                            (openBlock(true), createElementBlock(Fragment, null, renderList(qualifications.value.performance, (perf, index) => {
                              return openBlock(), createBlock(_component_el_card, {
                                key: index,
                                shadow: "never",
                                class: "requirement-item"
                              }, {
                                default: withCtx(() => [
                                  createBaseVNode("div", _hoisted_22, [
                                    _cache[33] || (_cache[33] = createBaseVNode("div", { class: "requirement-icon" }, [
                                      createBaseVNode("i", { class: "bi bi-briefcase" })
                                    ], -1)),
                                    createBaseVNode("div", _hoisted_23, [
                                      createBaseVNode("h4", null, toDisplayString(perf.description), 1),
                                      perf.amount ? (openBlock(), createElementBlock("p", _hoisted_24, "金额要求: ≥ ¥" + toDisplayString(formatAmount(perf.amount)), 1)) : createCommentVNode("", true),
                                      perf.time_range ? (openBlock(), createElementBlock("p", _hoisted_25, "时间范围: " + toDisplayString(perf.time_range), 1)) : createCommentVNode("", true),
                                      perf.count ? (openBlock(), createElementBlock("p", _hoisted_26, "数量要求: " + toDisplayString(perf.count) + " 个", 1)) : createCommentVNode("", true)
                                    ]),
                                    createBaseVNode("div", _hoisted_27, [
                                      perf.required ? (openBlock(), createBlock(_component_el_tag, {
                                        key: 0,
                                        type: "danger",
                                        size: "small"
                                      }, {
                                        default: withCtx(() => [..._cache[31] || (_cache[31] = [
                                          createTextVNode(" 必需 ", -1)
                                        ])]),
                                        _: 1
                                      })) : (openBlock(), createBlock(_component_el_tag, {
                                        key: 1,
                                        type: "info",
                                        size: "small"
                                      }, {
                                        default: withCtx(() => [..._cache[32] || (_cache[32] = [
                                          createTextVNode("可选", -1)
                                        ])]),
                                        _: 1
                                      }))
                                    ])
                                  ])
                                ]),
                                _: 2
                              }, 1024);
                            }), 128))
                          ])) : (openBlock(), createBlock(_component_el_empty, {
                            key: 1,
                            description: "暂无业绩要求",
                            "image-size": 80
                          }))
                        ]),
                        createBaseVNode("section", _hoisted_28, [
                          _cache[38] || (_cache[38] = createBaseVNode("div", { class: "section-header" }, [
                            createBaseVNode("h3", null, [
                              createBaseVNode("i", { class: "bi bi-people" }),
                              createTextVNode(" 人员配置要求")
                            ])
                          ], -1)),
                          qualifications.value.personnel.length > 0 ? (openBlock(), createElementBlock("div", _hoisted_29, [
                            (openBlock(true), createElementBlock(Fragment, null, renderList(qualifications.value.personnel, (person, index) => {
                              return openBlock(), createBlock(_component_el_card, {
                                key: index,
                                shadow: "never",
                                class: "requirement-item"
                              }, {
                                default: withCtx(() => [
                                  createBaseVNode("div", _hoisted_30, [
                                    _cache[37] || (_cache[37] = createBaseVNode("div", { class: "requirement-icon" }, [
                                      createBaseVNode("i", { class: "bi bi-person-badge" })
                                    ], -1)),
                                    createBaseVNode("div", _hoisted_31, [
                                      createBaseVNode("h4", null, toDisplayString(person.position), 1),
                                      person.count ? (openBlock(), createElementBlock("p", _hoisted_32, "人数: " + toDisplayString(person.count) + " 人", 1)) : createCommentVNode("", true),
                                      person.qualification ? (openBlock(), createElementBlock("p", _hoisted_33, "资格要求: " + toDisplayString(person.qualification), 1)) : createCommentVNode("", true),
                                      person.experience ? (openBlock(), createElementBlock("p", _hoisted_34, "经验要求: " + toDisplayString(person.experience), 1)) : createCommentVNode("", true)
                                    ]),
                                    createBaseVNode("div", _hoisted_35, [
                                      person.required ? (openBlock(), createBlock(_component_el_tag, {
                                        key: 0,
                                        type: "danger",
                                        size: "small"
                                      }, {
                                        default: withCtx(() => [..._cache[35] || (_cache[35] = [
                                          createTextVNode(" 必需 ", -1)
                                        ])]),
                                        _: 1
                                      })) : (openBlock(), createBlock(_component_el_tag, {
                                        key: 1,
                                        type: "info",
                                        size: "small"
                                      }, {
                                        default: withCtx(() => [..._cache[36] || (_cache[36] = [
                                          createTextVNode("可选", -1)
                                        ])]),
                                        _: 1
                                      }))
                                    ])
                                  ])
                                ]),
                                _: 2
                              }, 1024);
                            }), 128))
                          ])) : (openBlock(), createBlock(_component_el_empty, {
                            key: 1,
                            description: "暂无人员配置要求",
                            "image-size": 80
                          }))
                        ]),
                        createBaseVNode("section", _hoisted_36, [
                          _cache[41] || (_cache[41] = createBaseVNode("div", { class: "section-header" }, [
                            createBaseVNode("h3", null, [
                              createBaseVNode("i", { class: "bi bi-cash-stack" }),
                              createTextVNode(" 财务要求")
                            ])
                          ], -1)),
                          qualifications.value.financial ? (openBlock(), createElementBlock("div", _hoisted_37, [
                            createVNode(_component_el_card, {
                              shadow: "never",
                              class: "requirement-item"
                            }, {
                              default: withCtx(() => [
                                createBaseVNode("div", _hoisted_38, [
                                  _cache[40] || (_cache[40] = createBaseVNode("div", { class: "requirement-icon" }, [
                                    createBaseVNode("i", { class: "bi bi-cash-stack" })
                                  ], -1)),
                                  createBaseVNode("div", _hoisted_39, [
                                    _cache[39] || (_cache[39] = createBaseVNode("h4", null, "财务相关要求", -1)),
                                    createBaseVNode("p", null, toDisplayString(qualifications.value.financial.description), 1)
                                  ])
                                ])
                              ]),
                              _: 1
                            })
                          ])) : (openBlock(), createBlock(_component_el_empty, {
                            key: 1,
                            description: "暂无财务要求",
                            "image-size": 80
                          }))
                        ])
                      ])
                    ]),
                    _: 1
                  }),
                  createVNode(_component_el_tab_pane, { name: "business" }, {
                    label: withCtx(() => {
                      var _a;
                      return [
                        createBaseVNode("span", _hoisted_40, [
                          _cache[42] || (_cache[42] = createBaseVNode("i", { class: "bi bi-briefcase" }, null, -1)),
                          _cache[43] || (_cache[43] = createTextVNode(" 商务应答 ", -1)),
                          ((_a = projectDetail.value.step1_data) == null ? void 0 : _a.business_response_file) ? (openBlock(), createBlock(_component_el_badge, {
                            key: 0,
                            "is-dot": "",
                            type: "success"
                          })) : createCommentVNode("", true)
                        ])
                      ];
                    }),
                    default: withCtx(() => [
                      createBaseVNode("div", _hoisted_41, [
                        createBaseVNode("section", _hoisted_42, [
                          createBaseVNode("div", _hoisted_43, [
                            _cache[45] || (_cache[45] = createBaseVNode("h3", null, [
                              createBaseVNode("i", { class: "bi bi-file-earmark-text" }),
                              createTextVNode(" 应答文件模板")
                            ], -1)),
                            createVNode(_component_el_tag, {
                              type: "info",
                              size: "small"
                            }, {
                              default: withCtx(() => [..._cache[44] || (_cache[44] = [
                                createTextVNode("AI 自动提取", -1)
                              ])]),
                              _: 1
                            })
                          ]),
                          responseFileInfo.value ? (openBlock(), createBlock(FileCard, {
                            key: 0,
                            "file-url": responseFileInfo.value.fileUrl,
                            "file-name": responseFileInfo.value.fileName,
                            "file-size": responseFileInfo.value.fileSize,
                            "show-actions": true,
                            onPreview: handlePreview
                          }, null, 8, ["file-url", "file-name", "file-size"])) : (openBlock(), createBlock(_component_el_empty, {
                            key: 1,
                            description: "暂未提取到应答文件模板",
                            "image-size": 80
                          }, {
                            extra: withCtx(() => [
                              createVNode(_component_el_text, {
                                type: "info",
                                size: "small"
                              }, {
                                default: withCtx(() => [..._cache[46] || (_cache[46] = [
                                  createTextVNode(" 请先上传招标文件并进行 AI 解析 ", -1)
                                ])]),
                                _: 1
                              })
                            ]),
                            _: 1
                          }))
                        ]),
                        createVNode(_component_el_divider),
                        createBaseVNode("section", _hoisted_44, [
                          createBaseVNode("div", _hoisted_45, [
                            _cache[49] || (_cache[49] = createBaseVNode("h3", null, [
                              createBaseVNode("i", { class: "bi bi-file-earmark-check" }),
                              createTextVNode(" 商务应答完成文件")
                            ], -1)),
                            businessResponseFileInfo.value ? (openBlock(), createBlock(_component_el_tag, {
                              key: 0,
                              type: "success",
                              size: "small"
                            }, {
                              default: withCtx(() => [..._cache[47] || (_cache[47] = [
                                createBaseVNode("i", { class: "bi bi-check-circle-fill" }, null, -1),
                                createTextVNode(" 已生成 ", -1)
                              ])]),
                              _: 1
                            })) : (openBlock(), createBlock(_component_el_tag, {
                              key: 1,
                              type: "info",
                              size: "small"
                            }, {
                              default: withCtx(() => [..._cache[48] || (_cache[48] = [
                                createTextVNode("未生成", -1)
                              ])]),
                              _: 1
                            }))
                          ]),
                          businessResponseFileInfo.value ? (openBlock(), createBlock(FileCard, {
                            key: 0,
                            "file-url": businessResponseFileInfo.value.fileUrl,
                            "file-name": businessResponseFileInfo.value.fileName,
                            "file-size": businessResponseFileInfo.value.fileSize,
                            "show-actions": true,
                            type: "success",
                            onPreview: handlePreview
                          }, null, 8, ["file-url", "file-name", "file-size"])) : (openBlock(), createBlock(_component_el_empty, {
                            key: 1,
                            description: "暂未生成商务应答文件",
                            "image-size": 80
                          }, {
                            extra: withCtx(() => [
                              createVNode(_component_el_text, {
                                type: "info",
                                size: "small"
                              }, {
                                default: withCtx(() => [..._cache[50] || (_cache[50] = [
                                  createTextVNode(" 点击下方按钮开始生成商务应答 ", -1)
                                ])]),
                                _: 1
                              })
                            ]),
                            _: 1
                          }))
                        ]),
                        createBaseVNode("div", _hoisted_46, [
                          createVNode(_component_el_button, {
                            type: "primary",
                            size: "large",
                            disabled: !responseFileInfo.value,
                            onClick: handleStartBusiness
                          }, {
                            default: withCtx(() => [
                              _cache[51] || (_cache[51] = createBaseVNode("i", { class: "bi bi-rocket-takeoff" }, null, -1)),
                              createTextVNode(" " + toDisplayString(businessResponseFileInfo.value ? "重新生成" : "开始") + "商务应答 ", 1)
                            ]),
                            _: 1
                          }, 8, ["disabled"]),
                          !responseFileInfo.value ? (openBlock(), createBlock(_component_el_text, {
                            key: 0,
                            type: "warning",
                            size: "small"
                          }, {
                            default: withCtx(() => [..._cache[52] || (_cache[52] = [
                              createBaseVNode("i", { class: "bi bi-exclamation-triangle" }, null, -1),
                              createTextVNode(" 请先上传招标文件并进行 AI 解析 ", -1)
                            ])]),
                            _: 1
                          })) : createCommentVNode("", true)
                        ])
                      ])
                    ]),
                    _: 1
                  }),
                  createVNode(_component_el_tab_pane, { name: "documents" }, {
                    label: withCtx(() => [
                      createBaseVNode("span", _hoisted_47, [
                        _cache[53] || (_cache[53] = createBaseVNode("i", { class: "bi bi-files" }, null, -1)),
                        _cache[54] || (_cache[54] = createTextVNode(" 文档与章节 ", -1)),
                        projectDocuments.value.length > 0 || parsedChapters.value.length > 0 ? (openBlock(), createBlock(_component_el_badge, {
                          key: 0,
                          value: projectDocuments.value.length,
                          type: "success"
                        }, null, 8, ["value"])) : createCommentVNode("", true)
                      ])
                    ]),
                    default: withCtx(() => [
                      createBaseVNode("div", _hoisted_48, [
                        createBaseVNode("section", _hoisted_49, [
                          createBaseVNode("div", _hoisted_50, [
                            _cache[55] || (_cache[55] = createBaseVNode("h3", null, [
                              createBaseVNode("i", { class: "bi bi-file-earmark-text" }),
                              createTextVNode(" 项目文档")
                            ], -1)),
                            projectDocuments.value.length > 0 ? (openBlock(), createBlock(_component_el_tag, {
                              key: 0,
                              type: "success",
                              size: "small"
                            }, {
                              default: withCtx(() => [
                                createTextVNode(" 共 " + toDisplayString(projectDocuments.value.length) + " 个文件 ", 1)
                              ]),
                              _: 1
                            })) : createCommentVNode("", true)
                          ]),
                          projectDocuments.value.length > 0 ? (openBlock(), createElementBlock("div", _hoisted_51, [
                            (openBlock(true), createElementBlock(Fragment, null, renderList(projectDocuments.value, (doc) => {
                              return openBlock(), createBlock(FileCard, {
                                key: doc.id,
                                "file-url": doc.file_url || doc.file_path,
                                "file-name": doc.original_filename,
                                "file-size": doc.file_size,
                                "upload-time": doc.uploaded_at,
                                "show-actions": true,
                                onPreview: handlePreview
                              }, null, 8, ["file-url", "file-name", "file-size", "upload-time"]);
                            }), 128))
                          ])) : (openBlock(), createBlock(_component_el_empty, {
                            key: 1,
                            description: "暂无文档",
                            "image-size": 80
                          }, {
                            extra: withCtx(() => [
                              createVNode(_component_el_text, {
                                type: "info",
                                size: "small"
                              }, {
                                default: withCtx(() => [..._cache[56] || (_cache[56] = [
                                  createTextVNode(" 请在页面顶部上传招标文档 ", -1)
                                ])]),
                                _: 1
                              })
                            ]),
                            _: 1
                          }))
                        ]),
                        parsedChapters.value.length > 0 ? (openBlock(), createBlock(_component_el_divider, { key: 0 })) : createCommentVNode("", true),
                        parsedChapters.value.length > 0 ? (openBlock(), createElementBlock("section", _hoisted_52, [
                          createBaseVNode("div", _hoisted_53, [
                            _cache[57] || (_cache[57] = createBaseVNode("h3", null, [
                              createBaseVNode("i", { class: "bi bi-list-nested" }),
                              createTextVNode(" 已识别章节")
                            ], -1)),
                            createVNode(_component_el_tag, {
                              type: "success",
                              size: "small"
                            }, {
                              default: withCtx(() => [
                                createTextVNode(" 共 " + toDisplayString(totalParsedChapters.value) + " 个章节 ", 1)
                              ]),
                              _: 1
                            })
                          ]),
                          createVNode(ChapterTree, {
                            chapters: parsedChapters.value,
                            "show-checkbox": false,
                            "show-search": true
                          }, null, 8, ["chapters"])
                        ])) : createCommentVNode("", true)
                      ])
                    ]),
                    _: 1
                  }),
                  createVNode(_component_el_tab_pane, { name: "technical" }, {
                    label: withCtx(() => {
                      var _a, _b;
                      return [
                        createBaseVNode("span", _hoisted_54, [
                          _cache[58] || (_cache[58] = createBaseVNode("i", { class: "bi bi-cpu" }, null, -1)),
                          _cache[59] || (_cache[59] = createTextVNode(" 技术需求 ", -1)),
                          ((_a = projectDetail.value.step1_data) == null ? void 0 : _a.technical_point_to_point_file) || ((_b = projectDetail.value.step1_data) == null ? void 0 : _b.technical_proposal_file) ? (openBlock(), createBlock(_component_el_badge, {
                            key: 0,
                            "is-dot": "",
                            type: "success"
                          })) : createCommentVNode("", true)
                        ])
                      ];
                    }),
                    default: withCtx(() => [
                      createBaseVNode("div", _hoisted_55, [
                        createBaseVNode("section", _hoisted_56, [
                          createBaseVNode("div", _hoisted_57, [
                            _cache[61] || (_cache[61] = createBaseVNode("h3", null, [
                              createBaseVNode("i", { class: "bi bi-file-earmark-text" }),
                              createTextVNode(" 技术需求文件")
                            ], -1)),
                            createVNode(_component_el_tag, {
                              type: "info",
                              size: "small"
                            }, {
                              default: withCtx(() => [..._cache[60] || (_cache[60] = [
                                createTextVNode("AI 自动提取", -1)
                              ])]),
                              _: 1
                            })
                          ]),
                          technicalFileInfo.value ? (openBlock(), createBlock(FileCard, {
                            key: 0,
                            "file-url": technicalFileInfo.value.fileUrl,
                            "file-name": technicalFileInfo.value.fileName,
                            "file-size": technicalFileInfo.value.fileSize,
                            "show-actions": true,
                            onPreview: handlePreview
                          }, null, 8, ["file-url", "file-name", "file-size"])) : (openBlock(), createBlock(_component_el_empty, {
                            key: 1,
                            description: "暂未提取到技术需求文件",
                            "image-size": 80
                          }))
                        ]),
                        createVNode(_component_el_divider),
                        createBaseVNode("section", _hoisted_58, [
                          createBaseVNode("div", _hoisted_59, [
                            _cache[64] || (_cache[64] = createBaseVNode("h3", null, [
                              createBaseVNode("i", { class: "bi bi-arrow-left-right" }),
                              createTextVNode(" 点对点应答完成文件")
                            ], -1)),
                            technicalP2PFileInfo.value ? (openBlock(), createBlock(_component_el_tag, {
                              key: 0,
                              type: "success",
                              size: "small"
                            }, {
                              default: withCtx(() => [..._cache[62] || (_cache[62] = [
                                createBaseVNode("i", { class: "bi bi-check-circle-fill" }, null, -1),
                                createTextVNode(" 已生成 ", -1)
                              ])]),
                              _: 1
                            })) : (openBlock(), createBlock(_component_el_tag, {
                              key: 1,
                              type: "info",
                              size: "small"
                            }, {
                              default: withCtx(() => [..._cache[63] || (_cache[63] = [
                                createTextVNode("未生成", -1)
                              ])]),
                              _: 1
                            }))
                          ]),
                          technicalP2PFileInfo.value ? (openBlock(), createBlock(FileCard, {
                            key: 0,
                            "file-url": technicalP2PFileInfo.value.fileUrl,
                            "file-name": technicalP2PFileInfo.value.fileName,
                            "file-size": technicalP2PFileInfo.value.fileSize,
                            "show-actions": true,
                            type: "success",
                            onPreview: handlePreview
                          }, null, 8, ["file-url", "file-name", "file-size"])) : (openBlock(), createBlock(_component_el_empty, {
                            key: 1,
                            description: "暂未生成点对点应答文件",
                            "image-size": 80
                          }))
                        ]),
                        createVNode(_component_el_divider),
                        createBaseVNode("section", _hoisted_60, [
                          createBaseVNode("div", _hoisted_61, [
                            _cache[67] || (_cache[67] = createBaseVNode("h3", null, [
                              createBaseVNode("i", { class: "bi bi-file-code" }),
                              createTextVNode(" 技术方案完成文件")
                            ], -1)),
                            technicalProposalFileInfo.value ? (openBlock(), createBlock(_component_el_tag, {
                              key: 0,
                              type: "success",
                              size: "small"
                            }, {
                              default: withCtx(() => [..._cache[65] || (_cache[65] = [
                                createBaseVNode("i", { class: "bi bi-check-circle-fill" }, null, -1),
                                createTextVNode(" 已生成 ", -1)
                              ])]),
                              _: 1
                            })) : (openBlock(), createBlock(_component_el_tag, {
                              key: 1,
                              type: "info",
                              size: "small"
                            }, {
                              default: withCtx(() => [..._cache[66] || (_cache[66] = [
                                createTextVNode("未生成", -1)
                              ])]),
                              _: 1
                            }))
                          ]),
                          technicalProposalFileInfo.value ? (openBlock(), createBlock(FileCard, {
                            key: 0,
                            "file-url": technicalProposalFileInfo.value.fileUrl,
                            "file-name": technicalProposalFileInfo.value.fileName,
                            "file-size": technicalProposalFileInfo.value.fileSize,
                            "show-actions": true,
                            type: "success",
                            onPreview: handlePreview
                          }, null, 8, ["file-url", "file-name", "file-size"])) : (openBlock(), createBlock(_component_el_empty, {
                            key: 1,
                            description: "暂未生成技术方案文件",
                            "image-size": 80
                          }))
                        ]),
                        createBaseVNode("div", _hoisted_62, [
                          createVNode(_component_el_space, { size: 16 }, {
                            default: withCtx(() => [
                              createVNode(_component_el_button, {
                                type: "primary",
                                size: "large",
                                disabled: !technicalFileInfo.value,
                                onClick: handleStartPointToPoint
                              }, {
                                default: withCtx(() => [
                                  _cache[68] || (_cache[68] = createBaseVNode("i", { class: "bi bi-arrow-left-right" }, null, -1)),
                                  createTextVNode(" " + toDisplayString(technicalP2PFileInfo.value ? "重新生成" : "开始") + "点对点应答 ", 1)
                                ]),
                                _: 1
                              }, 8, ["disabled"]),
                              createVNode(_component_el_button, {
                                type: "primary",
                                size: "large",
                                disabled: !technicalFileInfo.value,
                                onClick: handleStartProposal
                              }, {
                                default: withCtx(() => [
                                  _cache[69] || (_cache[69] = createBaseVNode("i", { class: "bi bi-file-code" }, null, -1)),
                                  createTextVNode(" " + toDisplayString(technicalProposalFileInfo.value ? "重新生成" : "开始") + "技术方案编写 ", 1)
                                ]),
                                _: 1
                              }, 8, ["disabled"])
                            ]),
                            _: 1
                          }),
                          !technicalFileInfo.value ? (openBlock(), createBlock(_component_el_text, {
                            key: 0,
                            type: "warning",
                            size: "small"
                          }, {
                            default: withCtx(() => [..._cache[70] || (_cache[70] = [
                              createBaseVNode("i", { class: "bi bi-exclamation-triangle" }, null, -1),
                              createTextVNode(" 请先上传招标文件并进行 AI 解析 ", -1)
                            ])]),
                            _: 1
                          })) : createCommentVNode("", true)
                        ])
                      ])
                    ]),
                    _: 1
                  })
                ]),
                _: 1
              }, 8, ["modelValue"])
            ]),
            _: 1
          })
        ], 64)) : (openBlock(), createBlock(_component_el_empty, {
          key: 2,
          description: "项目不存在或加载失败"
        })),
        createVNode(unref(DocumentPreview), {
          modelValue: previewVisible.value,
          "onUpdate:modelValue": _cache[16] || (_cache[16] = ($event) => previewVisible.value = $event),
          "file-url": previewFileUrl.value,
          "file-name": previewFileName.value
        }, null, 8, ["modelValue", "file-url", "file-name"])
      ]);
    };
  }
});
const ManagementDetail = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-d161f48c"]]);
export {
  ManagementDetail as default
};
