import { d as defineComponent, r as ref, c as computed, S as onMounted, e as createElementBlock, o as openBlock, f as createVNode, k as createBlock, l as createCommentVNode, w as withCtx, q as ElForm, ak as ElRow, ai as ElCol, s as ElFormItem, Y as ElSelect, F as Fragment, V as renderList, h as unref, W as ElOption, y as ElInput, n as createBaseVNode, as as ElCard, a6 as ElDivider, p as createTextVNode, b1 as ElCheckboxGroup, P as ElCheckbox, g as ElButton, ad as ElIcon, b2 as promotion_default, aL as ElProgress, aa as withDirectives, aH as ElCollapse, aC as ElCollapseItem, t as toDisplayString, X as ElTag, ab as vShow, aq as ElTree, b3 as folder_default, ae as document_default, aE as download_default, aD as view_default, aF as upload_default, aG as refresh_right_default, A as ElMessage } from "./vendor-MtO928VE.js";
/* empty css                                                                           */
import { S as SSEStreamViewer } from "./SSEStreamViewer-CpKSZAqP.js";
import { D as DocumentUploader } from "./DocumentUploader-BFiqpCwu.js";
import { D as DocumentPreview } from "./DocumentPreview-9ke4Yi2d.js";
import { R as RichTextEditor } from "./RichTextEditor-Bq9eh2QZ.js";
import { u as useHitlIntegration, H as HitlFileAlert, S as StatsCard, a as HistoryFilesPanel, d as downloadFile } from "./helpers-Bcq2sOJ4.js";
import { _ as _export_sfc } from "./index.js";
import { t as tenderApi } from "./tender-DvsgeLWX.js";
import { u as useProjectDocuments } from "./useProjectDocuments-CobiuthK.js";
import "./imageCompressor-DC3BCfPz.js";
/* empty css                                                                         */
import "./project-X4Kuz_iO.js";
const _hoisted_1 = { class: "tech-proposal" };
const _hoisted_2 = { class: "card-header" };
const _hoisted_3 = { class: "action-controls" };
const _hoisted_4 = { class: "card-header" };
const _hoisted_5 = { class: "card-header" };
const _hoisted_6 = { class: "requirement-categories" };
const _hoisted_7 = { class: "category-title" };
const _hoisted_8 = { class: "category-content" };
const _hoisted_9 = {
  key: 0,
  class: "category-summary"
};
const _hoisted_10 = {
  key: 1,
  class: "category-keywords"
};
const _hoisted_11 = {
  key: 2,
  class: "category-points"
};
const _hoisted_12 = { class: "card-header" };
const _hoisted_13 = { class: "章节结构" };
const _hoisted_14 = { class: "tree-node" };
const _hoisted_15 = { class: "node-title" };
const _hoisted_16 = {
  key: 2,
  class: "node-desc"
};
const _hoisted_17 = { class: "card-header" };
const _hoisted_18 = { class: "header-actions" };
const _hoisted_19 = { class: "result-content" };
const _hoisted_20 = { class: "output-files" };
const _hoisted_21 = { class: "file-buttons" };
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "TechProposal",
  setup(__props) {
    const {
      projects,
      selectedProject,
      currentDocuments,
      loadProjects,
      handleProjectChange: handleProjectChangeComposable,
      restoreProjectFromStore
    } = useProjectDocuments();
    const {
      useHitlFile,
      hitlFileInfo,
      syncing,
      synced,
      loadFromHITL,
      cancelHitlFile,
      syncToHitl
    } = useHitlIntegration({
      onFileLoaded: () => {
        form.value.tenderFiles = [];
      }
    });
    const historyFiles = ref([]);
    const loadingHistory = ref(false);
    const loadHistoryFiles = async () => {
      console.log("历史文件API暂未实现");
    };
    const downloadHistoryFile = async (file) => {
      try {
        if (!file.downloadUrl) {
          ElMessage.error("下载地址无效");
          return;
        }
        const filename = file.filename || file.downloadUrl.split("/").pop() || "技术方案.docx";
        downloadFile(file.downloadUrl, filename);
        ElMessage.success("文件下载中...");
      } catch (error) {
        console.error("下载文件失败:", error);
        ElMessage.error(error.message || "下载文件失败");
      }
    };
    const form = ref({
      projectId: null,
      tenderFiles: []
    });
    const config = ref({
      outputPrefix: "技术方案",
      aiModel: "shihuang-gpt4o-mini",
      additionalOutputs: ["includeAnalysis", "includeMapping", "includeSummary"]
    });
    const generating = ref(false);
    const generationProgress = ref(0);
    const streamContent = ref("");
    const analysisResult = ref(null);
    const analysisExpanded = ref(true);
    const outlineData = ref(null);
    const outlineExpanded = ref(true);
    const generationResult = ref(null);
    const currentTechFile = ref(null);
    const previewVisible = ref(false);
    const previewFileUrl = ref("");
    const previewFileName = ref("");
    const showEditor = ref(false);
    const editorRef = ref(null);
    const editorContent = ref("");
    const editorLoading = ref(false);
    const editorSaving = ref(false);
    const chapterTreeData = computed(() => {
      var _a;
      if (!((_a = outlineData.value) == null ? void 0 : _a.chapters)) return [];
      return outlineData.value.chapters;
    });
    const canGenerate = computed(
      () => form.value.projectId && (useHitlFile.value || form.value.tenderFiles.length > 0)
    );
    const getPriorityType = (priority) => {
      const types = {
        "高": "danger",
        "high": "danger",
        "中": "warning",
        "medium": "warning",
        "低": "info",
        "low": "info"
      };
      return types[priority] || "info";
    };
    const handleTenderUpload = async (options) => {
      var _a;
      const { file, onSuccess, onError } = options;
      if (!form.value.projectId) {
        const error = new Error("请先选择项目");
        onError(error);
        ElMessage.error("请先选择项目");
        return;
      }
      if (!((_a = selectedProject.value) == null ? void 0 : _a.company_id)) {
        const error = new Error("项目没有关联公司");
        onError(error);
        ElMessage.error("项目没有关联公司");
        return;
      }
      try {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("company_id", selectedProject.value.company_id.toString());
        formData.append("project_id", form.value.projectId.toString());
        const response = await tenderApi.parseDocumentStructure(formData);
        if (response.success) {
          onSuccess(response.data);
          ElMessage.success("技术需求文档上传成功");
        } else {
          throw new Error(response.message || "上传失败");
        }
      } catch (error) {
        onError(error);
        ElMessage.error(error.message || "文档上传失败");
      }
    };
    const handleUploadSuccess = () => {
      ElMessage.success("文档上传成功");
    };
    const handleProjectChange = async () => {
      await handleProjectChangeComposable(form.value.projectId, {
        onClear: () => {
          form.value.tenderFiles = [];
          analysisResult.value = null;
          outlineData.value = null;
          generationResult.value = null;
          currentTechFile.value = null;
          streamContent.value = "";
          showEditor.value = false;
          editorContent.value = "";
          if (useHitlFile.value) {
            cancelHitlFile();
          }
        },
        onDocumentsLoaded: (docs) => {
          if (docs.technicalFile) {
            loadFromHITL(docs, "technicalFile");
          }
          if (docs.techProposalFile) {
            currentTechFile.value = docs.techProposalFile;
            ElMessage.success("已加载历史技术方案文件");
          }
        }
      });
    };
    const generateProposal = async () => {
      var _a;
      if (!canGenerate.value) {
        ElMessage.warning("请选择项目并上传技术需求文档");
        return;
      }
      generating.value = true;
      generationProgress.value = 0;
      streamContent.value = "";
      analysisResult.value = null;
      generationResult.value = null;
      showEditor.value = false;
      editorContent.value = "";
      try {
        const formData = new FormData();
        if (useHitlFile.value && hitlFileInfo.value) {
          formData.append("use_hitl_technical_file", "true");
          formData.append("project_id", form.value.projectId.toString());
        } else if ((_a = form.value.tenderFiles[0]) == null ? void 0 : _a.raw) {
          formData.append("tender_file", form.value.tenderFiles[0].raw);
        } else {
          throw new Error("请上传技术需求文档或使用技术文件");
        }
        formData.append("outputPrefix", config.value.outputPrefix);
        formData.append("companyId", selectedProject.value.company_id.toString());
        formData.append("projectName", selectedProject.value.project_name || "");
        formData.append("projectId", form.value.projectId.toString());
        formData.append("aiModel", config.value.aiModel);
        formData.append("includeAnalysis", config.value.additionalOutputs.includes("includeAnalysis") ? "true" : "false");
        formData.append("includeMapping", config.value.additionalOutputs.includes("includeMapping") ? "true" : "false");
        formData.append("includeSummary", config.value.additionalOutputs.includes("includeSummary") ? "true" : "false");
        await generateWithSSE(formData);
        ElMessage.success("技术方案生成完成");
      } catch (error) {
        console.error("生成失败:", error);
        ElMessage.error(error.message || "生成失败，请重试");
      } finally {
        generating.value = false;
      }
    };
    const generateWithSSE = async (formData) => {
      var _a, _b, _c;
      const useStreamingContent = true;
      const apiEndpoint = "/api/generate-proposal-stream-v2";
      const response = await fetch(apiEndpoint, {
        method: "POST",
        body: formData
      });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      const reader = (_a = response.body) == null ? void 0 : _a.getReader();
      if (!reader) {
        throw new Error("无法读取响应流");
      }
      const decoder = new TextDecoder();
      let buffer = "";
      const chapterContents = {};
      let currentChapterNumber = "";
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.progress !== void 0) {
                generationProgress.value = data.progress;
              }
              if (data.message) {
                streamContent.value += data.message + "\n";
              }
              if (data.stage === "analysis_completed" && data.analysis_result) {
                analysisResult.value = data.analysis_result;
              }
              if (data.stage === "outline_completed" && data.outline_data) {
                outlineData.value = data.outline_data;
              }
              if (data.stage === "content_generation") {
                if (data.event === "chapter_start") {
                  currentChapterNumber = data.chapter_number || "";
                  chapterContents[currentChapterNumber] = "";
                  streamContent.value += `

## ${data.chapter_number} ${data.chapter_title}

`;
                  if (!showEditor.value) {
                    showEditor.value = true;
                  }
                } else if (data.event === "content_chunk") {
                  const chapterNum = data.chapter_number || currentChapterNumber;
                  if (chapterNum) {
                    chapterContents[chapterNum] = (chapterContents[chapterNum] || "") + (data.content || "");
                    updateEditorContent(chapterContents);
                  }
                } else if (data.event === "chapter_end") {
                  streamContent.value += `
✓ ${data.chapter_title || "章节"} 生成完成
`;
                }
              }
              if (data.stage === "completed" && data.success) {
                generationResult.value = data;
                currentTechFile.value = {
                  outputFile: data.output_file,
                  downloadUrl: (_b = data.output_files) == null ? void 0 : _b.proposal,
                  stats: {
                    requirements_count: data.requirements_count,
                    sections_count: data.sections_count,
                    matches_count: data.matches_count
                  },
                  message: "技术方案已生成"
                };
                if (useStreamingContent) {
                  showEditor.value = true;
                }
                if (data.output_file && form.value.projectId) {
                  await syncToHitl(
                    form.value.projectId,
                    data.output_file,
                    "tech_proposal"
                  );
                }
              }
              if (data.stage === "error") {
                streamContent.value += `
❌ 错误: ${data.error || data.message}
`;
                throw new Error(data.error || data.message || "生成失败");
              }
            } catch (e) {
              if ((_c = e.message) == null ? void 0 : _c.includes("JSON")) ;
              else {
                console.error("SSE处理错误:", e, "原始数据:", line);
                throw e;
              }
            }
          }
        }
      }
    };
    const updateEditorContent = (chapterContents) => {
      var _a;
      if ((_a = outlineData.value) == null ? void 0 : _a.chapters) {
        let htmlContent = "";
        const generateChapterHtml = (chapters) => {
          for (const chapter of chapters) {
            const chapterNum = chapter.chapter_number;
            const content = chapterContents[chapterNum] || "";
            const headingLevel = chapter.level || 1;
            htmlContent += `<h${headingLevel}>${chapterNum} ${chapter.title}</h${headingLevel}>
`;
            if (content) {
              htmlContent += `<div>${content.replace(/\n/g, "<br>")}</div>
`;
            }
            if (chapter.subsections && chapter.subsections.length > 0) {
              generateChapterHtml(chapter.subsections);
            }
          }
        };
        generateChapterHtml(outlineData.value.chapters);
        editorContent.value = htmlContent;
      } else {
        let htmlContent = "";
        const sortedEntries = Object.entries(chapterContents).sort((a, b) => {
          const [numA] = a;
          const [numB] = b;
          return numA.localeCompare(numB, "zh-CN");
        });
        for (const [chapterNum, content] of sortedEntries) {
          htmlContent += `<h2>${chapterNum}</h2>
`;
          htmlContent += `<div>${content.replace(/\n/g, "<br>")}</div>
`;
        }
        editorContent.value = htmlContent;
      }
    };
    const stopGeneration = () => {
      generating.value = false;
      ElMessage.info("已停止生成");
    };
    const downloadDocument = (fileType) => {
      var _a, _b;
      if (!((_b = (_a = generationResult.value) == null ? void 0 : _a.output_files) == null ? void 0 : _b[fileType])) {
        ElMessage.warning("文件不存在");
        return;
      }
      const url = generationResult.value.output_files[fileType];
      const filename = url.split("/").pop() || `技术方案_${fileType}.docx`;
      downloadFile(url, filename);
      ElMessage.success("下载已开始");
    };
    const previewDocument = () => {
      var _a, _b, _c;
      if (!((_b = (_a = generationResult.value) == null ? void 0 : _a.output_files) == null ? void 0 : _b.proposal)) {
        ElMessage.warning("暂无文档可预览");
        return;
      }
      previewFileUrl.value = generationResult.value.output_files.proposal;
      previewFileName.value = `技术方案-${((_c = selectedProject.value) == null ? void 0 : _c.project_name) || "文档"}.docx`;
      previewVisible.value = true;
    };
    const previewFile = (file) => {
      previewFileUrl.value = file.file_path || file.outputFile;
      previewFileName.value = file.filename || "技术方案.docx";
      previewVisible.value = true;
    };
    const handleSyncToHitl = async () => {
      var _a;
      if (!((_a = generationResult.value) == null ? void 0 : _a.output_file)) {
        ElMessage.warning("没有可同步的文件");
        return;
      }
      if (!form.value.projectId) {
        ElMessage.error("项目ID无效");
        return;
      }
      await syncToHitl(
        form.value.projectId,
        generationResult.value.output_file,
        "tech_proposal"
      );
    };
    const handleRegenerate = () => {
      currentTechFile.value = null;
      generationResult.value = null;
      analysisResult.value = null;
      outlineData.value = null;
      showEditor.value = false;
      editorContent.value = "";
      ElMessage.info("请配置参数后重新生成");
    };
    const handleEditorSave = async (content) => {
      var _a;
      if (!((_a = generationResult.value) == null ? void 0 : _a.output_file)) {
        ElMessage.warning("没有可保存的文件");
        return;
      }
      try {
        editorSaving.value = true;
        const response = await fetch("/api/editor/save-html-to-word", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            html_content: content,
            project_id: form.value.projectId,
            document_type: "tech_proposal",
            original_file: generationResult.value.output_file
          })
        });
        const result = await response.json();
        if (result.success) {
          ElMessage.success("技术方案内容已保存");
          if (result.output_file) {
            generationResult.value.output_file = result.output_file;
            if (result.download_url && generationResult.value.output_files) {
              generationResult.value.output_files.proposal = result.download_url;
            }
          }
          if (result.output_file && form.value.projectId) {
            await syncToHitl(
              form.value.projectId,
              result.output_file,
              "tech_proposal"
            );
          }
        } else {
          throw new Error(result.error || "保存失败");
        }
      } catch (error) {
        console.error("[TechProposal] 保存编辑内容失败:", error);
        throw error;
      } finally {
        editorSaving.value = false;
      }
    };
    const loadWordToEditor = async (filePath) => {
      try {
        editorLoading.value = true;
        editorContent.value = '<p style="color: #409EFF;">正在转换Word文档为可编辑格式...</p>';
        const response = await fetch("/api/editor/convert-word-to-html", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ file_path: filePath })
        });
        const result = await response.json();
        if (result.success && result.html_content) {
          editorContent.value = result.html_content;
          if (editorRef.value) {
            editorRef.value.setContent(result.html_content);
          }
          console.log("[TechProposal] Word文档已加载到编辑器");
        } else {
          throw new Error(result.error || "转换失败");
        }
      } catch (error) {
        console.error("[TechProposal] 加载文档到编辑器失败:", error);
        editorContent.value = `
      <h1>📄 技术方案文档</h1>
      <div style="padding: 20px; background: #FFF3E0; border-left: 4px solid #FF9800; margin: 16px 0;">
        <p><strong>⚠️ 提示：</strong>Word文档转换失败</p>
        <p>原因：${error.message}</p>
        <p>您可以：</p>
        <ul>
          <li>直接在此编辑器中输入内容</li>
          <li>或点击下方"预览Word"或"下载"按钮查看原始文档</li>
        </ul>
      </div>
      <p>开始编辑您的内容...</p>
    `;
        ElMessage.warning("Word转换HTML失败，请使用预览或下载功能");
      } finally {
        editorLoading.value = false;
      }
    };
    const openHistoryInEditor = async () => {
      var _a;
      if (!((_a = currentTechFile.value) == null ? void 0 : _a.outputFile)) {
        ElMessage.error("历史文件信息无效");
        return;
      }
      try {
        showEditor.value = true;
        await loadWordToEditor(currentTechFile.value.outputFile);
        ElMessage.success("历史文件已加载到编辑器");
        setTimeout(() => {
          var _a2;
          (_a2 = document.querySelector(".editor-section")) == null ? void 0 : _a2.scrollIntoView({
            behavior: "smooth",
            block: "start"
          });
        }, 100);
      } catch (error) {
        console.error("[TechProposal] 打开历史文件失败:", error);
        ElMessage.error("打开历史文件失败: " + error.message);
      }
    };
    onMounted(async () => {
      await loadProjects();
      const restoredProjectId = await restoreProjectFromStore({
        onClear: () => {
          form.value.tenderFiles = [];
          analysisResult.value = null;
          outlineData.value = null;
          generationResult.value = null;
          currentTechFile.value = null;
          if (useHitlFile.value) {
            cancelHitlFile();
          }
        },
        onDocumentsLoaded: (docs) => {
          if (docs.technicalFile) {
            loadFromHITL(docs, "technicalFile");
          }
          if (docs.techProposalFile) {
            currentTechFile.value = docs.techProposalFile;
          }
        }
      });
      if (restoredProjectId) {
        form.value.projectId = restoredProjectId;
      }
    });
    return (_ctx, _cache) => {
      const _component_el_option = ElOption;
      const _component_el_select = ElSelect;
      const _component_el_form_item = ElFormItem;
      const _component_el_col = ElCol;
      const _component_el_input = ElInput;
      const _component_el_row = ElRow;
      const _component_el_form = ElForm;
      const _component_el_card = ElCard;
      const _component_el_button = ElButton;
      const _component_el_divider = ElDivider;
      const _component_el_checkbox = ElCheckbox;
      const _component_el_checkbox_group = ElCheckboxGroup;
      const _component_el_icon = ElIcon;
      const _component_el_progress = ElProgress;
      const _component_el_tag = ElTag;
      const _component_el_collapse_item = ElCollapseItem;
      const _component_el_collapse = ElCollapse;
      const _component_el_tree = ElTree;
      return openBlock(), createElementBlock("div", _hoisted_1, [
        createVNode(_component_el_card, {
          class: "project-section",
          shadow: "never"
        }, {
          header: withCtx(() => [..._cache[15] || (_cache[15] = [
            createBaseVNode("div", { class: "card-header" }, [
              createBaseVNode("span", null, "Step 1: 选择项目")
            ], -1)
          ])]),
          default: withCtx(() => [
            createVNode(_component_el_form, {
              model: form.value,
              "label-width": "100px"
            }, {
              default: withCtx(() => [
                createVNode(_component_el_row, { gutter: 20 }, {
                  default: withCtx(() => [
                    createVNode(_component_el_col, { span: 12 }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, { label: "项目" }, {
                          default: withCtx(() => [
                            createVNode(_component_el_select, {
                              modelValue: form.value.projectId,
                              "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => form.value.projectId = $event),
                              placeholder: "请选择项目",
                              filterable: "",
                              onChange: handleProjectChange,
                              style: { "width": "100%" }
                            }, {
                              default: withCtx(() => [
                                (openBlock(true), createElementBlock(Fragment, null, renderList(unref(projects), (project) => {
                                  return openBlock(), createBlock(_component_el_option, {
                                    key: project.id,
                                    label: `${project.project_name} (${project.project_number || "-"})`,
                                    value: project.id
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
                        createVNode(_component_el_form_item, { label: "公司" }, {
                          default: withCtx(() => {
                            var _a;
                            return [
                              createVNode(_component_el_input, {
                                value: ((_a = unref(selectedProject)) == null ? void 0 : _a.company_name) || "-",
                                disabled: ""
                              }, null, 8, ["value"])
                            ];
                          }),
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
        form.value.projectId ? (openBlock(), createBlock(_component_el_card, {
          key: 0,
          class: "upload-section",
          shadow: "never"
        }, {
          header: withCtx(() => [
            createBaseVNode("div", _hoisted_2, [
              _cache[17] || (_cache[17] = createBaseVNode("span", null, "Step 2: 上传技术需求文档", -1)),
              unref(currentDocuments).technicalFile && !unref(useHitlFile) ? (openBlock(), createBlock(_component_el_button, {
                key: 0,
                type: "primary",
                size: "small",
                onClick: _cache[1] || (_cache[1] = ($event) => unref(loadFromHITL)(unref(currentDocuments), "technicalFile"))
              }, {
                default: withCtx(() => [..._cache[16] || (_cache[16] = [
                  createTextVNode(" 使用技术需求文件 ", -1)
                ])]),
                _: 1
              })) : createCommentVNode("", true)
            ])
          ]),
          default: withCtx(() => [
            unref(useHitlFile) ? (openBlock(), createBlock(unref(HitlFileAlert), {
              key: 0,
              "file-info": unref(hitlFileInfo),
              label: "技术需求文件:",
              onCancel: unref(cancelHitlFile)
            }, null, 8, ["file-info", "onCancel"])) : createCommentVNode("", true),
            !unref(useHitlFile) ? (openBlock(), createBlock(unref(DocumentUploader), {
              key: 1,
              modelValue: form.value.tenderFiles,
              "onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => form.value.tenderFiles = $event),
              "http-request": handleTenderUpload,
              accept: ".pdf,.doc,.docx",
              limit: 1,
              "max-size": 50,
              drag: "",
              "tip-text": "上传技术需求文档",
              onSuccess: handleUploadSuccess
            }, null, 8, ["modelValue"])) : createCommentVNode("", true),
            createVNode(_component_el_divider, null, {
              default: withCtx(() => [..._cache[18] || (_cache[18] = [
                createTextVNode("生成选项", -1)
              ])]),
              _: 1
            }),
            createVNode(_component_el_form, {
              model: config.value,
              "label-width": "140px",
              class: "config-form"
            }, {
              default: withCtx(() => [
                createVNode(_component_el_row, { gutter: 20 }, {
                  default: withCtx(() => [
                    createVNode(_component_el_col, { span: 12 }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, { label: "输出文件前缀" }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: config.value.outputPrefix,
                              "onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => config.value.outputPrefix = $event),
                              placeholder: "技术方案"
                            }, null, 8, ["modelValue"])
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    createVNode(_component_el_col, { span: 12 }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, { label: "AI模型" }, {
                          default: withCtx(() => [
                            createVNode(_component_el_select, {
                              modelValue: config.value.aiModel,
                              "onUpdate:modelValue": _cache[4] || (_cache[4] = ($event) => config.value.aiModel = $event),
                              style: { "width": "100%" }
                            }, {
                              default: withCtx(() => [
                                createVNode(_component_el_option, {
                                  label: "GPT5（最强推理）",
                                  value: "shihuang-gpt5"
                                }),
                                createVNode(_component_el_option, {
                                  label: "Claude Sonnet 4.5（标书专用）",
                                  value: "shihuang-claude-sonnet-45"
                                }),
                                createVNode(_component_el_option, {
                                  label: "GPT4o Mini（推荐-默认）",
                                  value: "shihuang-gpt4o-mini"
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
                createVNode(_component_el_form_item, { label: "附加输出" }, {
                  default: withCtx(() => [
                    createVNode(_component_el_checkbox_group, {
                      modelValue: config.value.additionalOutputs,
                      "onUpdate:modelValue": _cache[5] || (_cache[5] = ($event) => config.value.additionalOutputs = $event)
                    }, {
                      default: withCtx(() => [
                        createVNode(_component_el_checkbox, { label: "includeAnalysis" }, {
                          default: withCtx(() => [..._cache[19] || (_cache[19] = [
                            createTextVNode("需求分析报告", -1)
                          ])]),
                          _: 1
                        }),
                        createVNode(_component_el_checkbox, { label: "includeMapping" }, {
                          default: withCtx(() => [..._cache[20] || (_cache[20] = [
                            createTextVNode("需求匹配表", -1)
                          ])]),
                          _: 1
                        }),
                        createVNode(_component_el_checkbox, { label: "includeSummary" }, {
                          default: withCtx(() => [..._cache[21] || (_cache[21] = [
                            createTextVNode("生成总结报告", -1)
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
            }, 8, ["model"]),
            createBaseVNode("div", _hoisted_3, [
              createVNode(_component_el_button, {
                type: "primary",
                size: "large",
                disabled: !canGenerate.value,
                loading: generating.value,
                onClick: generateProposal
              }, {
                default: withCtx(() => [
                  createVNode(_component_el_icon, null, {
                    default: withCtx(() => [
                      createVNode(unref(promotion_default))
                    ]),
                    _: 1
                  }),
                  _cache[22] || (_cache[22] = createTextVNode(" 生成技术方案 ", -1))
                ]),
                _: 1
              }, 8, ["disabled", "loading"])
            ])
          ]),
          _: 1
        })) : createCommentVNode("", true),
        generating.value ? (openBlock(), createBlock(_component_el_card, {
          key: 1,
          class: "generation-output",
          shadow: "never"
        }, {
          header: withCtx(() => [
            createBaseVNode("div", _hoisted_4, [
              _cache[23] || (_cache[23] = createBaseVNode("span", null, "AI正在生成技术方案...", -1)),
              createVNode(_component_el_progress, {
                percentage: generationProgress.value,
                status: generationProgress.value === 100 ? "success" : void 0,
                style: { "width": "300px" }
              }, null, 8, ["percentage", "status"])
            ])
          ]),
          default: withCtx(() => [
            createVNode(unref(SSEStreamViewer), {
              content: streamContent.value,
              "is-streaming": generating.value,
              onStop: stopGeneration
            }, null, 8, ["content", "is-streaming"])
          ]),
          _: 1
        })) : createCommentVNode("", true),
        analysisResult.value ? (openBlock(), createBlock(_component_el_card, {
          key: 2,
          class: "analysis-section",
          shadow: "never"
        }, {
          header: withCtx(() => [
            createBaseVNode("div", _hoisted_5, [
              _cache[24] || (_cache[24] = createBaseVNode("span", null, "需求分析结果", -1)),
              createVNode(_component_el_button, {
                size: "small",
                onClick: _cache[6] || (_cache[6] = ($event) => analysisExpanded.value = !analysisExpanded.value)
              }, {
                default: withCtx(() => [
                  createTextVNode(toDisplayString(analysisExpanded.value ? "收起" : "展开"), 1)
                ]),
                _: 1
              })
            ])
          ]),
          default: withCtx(() => [
            withDirectives(createBaseVNode("div", null, [
              createVNode(unref(StatsCard), {
                title: "文档摘要",
                stats: analysisResult.value.document_summary || {},
                "stat-items": [
                  { key: "total_requirements", label: "总需求数", suffix: "项" },
                  { key: "mandatory_count", label: "强制需求", suffix: "项" },
                  { key: "optional_count", label: "可选需求", suffix: "项" }
                ]
              }, null, 8, ["stats"]),
              createBaseVNode("div", _hoisted_6, [
                _cache[27] || (_cache[27] = createBaseVNode("h4", null, "需求分类", -1)),
                createVNode(_component_el_collapse, { accordion: "" }, {
                  default: withCtx(() => [
                    (openBlock(true), createElementBlock(Fragment, null, renderList(analysisResult.value.requirement_categories, (category, index) => {
                      return openBlock(), createBlock(_component_el_collapse_item, {
                        key: index,
                        name: index
                      }, {
                        title: withCtx(() => [
                          createBaseVNode("div", _hoisted_7, [
                            createBaseVNode("span", null, toDisplayString(category.category), 1),
                            createVNode(_component_el_tag, {
                              type: getPriorityType(category.priority),
                              size: "small"
                            }, {
                              default: withCtx(() => [
                                createTextVNode(toDisplayString(category.priority), 1)
                              ]),
                              _: 2
                            }, 1032, ["type"]),
                            createVNode(_component_el_tag, {
                              type: "info",
                              size: "small"
                            }, {
                              default: withCtx(() => [
                                createTextVNode(toDisplayString(category.requirements_count || 0) + "项 ", 1)
                              ]),
                              _: 2
                            }, 1024)
                          ])
                        ]),
                        default: withCtx(() => [
                          createBaseVNode("div", _hoisted_8, [
                            category.summary ? (openBlock(), createElementBlock("p", _hoisted_9, toDisplayString(category.summary), 1)) : createCommentVNode("", true),
                            category.keywords && category.keywords.length > 0 ? (openBlock(), createElementBlock("div", _hoisted_10, [
                              _cache[25] || (_cache[25] = createBaseVNode("strong", null, "关键词：", -1)),
                              (openBlock(true), createElementBlock(Fragment, null, renderList(category.keywords, (keyword) => {
                                return openBlock(), createBlock(_component_el_tag, {
                                  key: keyword,
                                  size: "small",
                                  style: { "margin-right": "8px" }
                                }, {
                                  default: withCtx(() => [
                                    createTextVNode(toDisplayString(keyword), 1)
                                  ]),
                                  _: 2
                                }, 1024);
                              }), 128))
                            ])) : createCommentVNode("", true),
                            category.key_points && category.key_points.length > 0 ? (openBlock(), createElementBlock("div", _hoisted_11, [
                              _cache[26] || (_cache[26] = createBaseVNode("strong", null, "要点：", -1)),
                              createBaseVNode("ul", null, [
                                (openBlock(true), createElementBlock(Fragment, null, renderList(category.key_points, (point, idx) => {
                                  return openBlock(), createElementBlock("li", { key: idx }, toDisplayString(point), 1);
                                }), 128))
                              ])
                            ])) : createCommentVNode("", true)
                          ])
                        ]),
                        _: 2
                      }, 1032, ["name"]);
                    }), 128))
                  ]),
                  _: 1
                })
              ])
            ], 512), [
              [vShow, analysisExpanded.value]
            ])
          ]),
          _: 1
        })) : createCommentVNode("", true),
        outlineData.value ? (openBlock(), createBlock(_component_el_card, {
          key: 3,
          class: "outline-section",
          shadow: "never"
        }, {
          header: withCtx(() => [
            createBaseVNode("div", _hoisted_12, [
              _cache[28] || (_cache[28] = createBaseVNode("span", null, "技术方案大纲", -1)),
              createVNode(_component_el_button, {
                size: "small",
                onClick: _cache[7] || (_cache[7] = ($event) => outlineExpanded.value = !outlineExpanded.value)
              }, {
                default: withCtx(() => [
                  createTextVNode(toDisplayString(outlineExpanded.value ? "收起" : "展开"), 1)
                ]),
                _: 1
              })
            ])
          ]),
          default: withCtx(() => [
            withDirectives(createBaseVNode("div", null, [
              createVNode(unref(StatsCard), {
                title: "大纲概览",
                stats: outlineData.value,
                "stat-items": [
                  { key: "total_chapters", label: "总章节数", suffix: "章" },
                  { key: "estimated_pages", label: "预计页数", suffix: "页" }
                ],
                span: 12
              }, null, 8, ["stats"]),
              createBaseVNode("div", _hoisted_13, [
                _cache[29] || (_cache[29] = createBaseVNode("h4", null, "章节结构", -1)),
                createVNode(_component_el_tree, {
                  data: chapterTreeData.value,
                  props: { label: "title", children: "subsections" },
                  "default-expand-all": "",
                  "node-key": "chapter_number"
                }, {
                  default: withCtx(({ node, data }) => [
                    createBaseVNode("span", _hoisted_14, [
                      data.level === 1 ? (openBlock(), createBlock(_component_el_icon, { key: 0 }, {
                        default: withCtx(() => [
                          createVNode(unref(folder_default))
                        ]),
                        _: 1
                      })) : (openBlock(), createBlock(_component_el_icon, { key: 1 }, {
                        default: withCtx(() => [
                          createVNode(unref(document_default))
                        ]),
                        _: 1
                      })),
                      createBaseVNode("span", _hoisted_15, toDisplayString(data.chapter_number) + " " + toDisplayString(data.title), 1),
                      data.description ? (openBlock(), createElementBlock("span", _hoisted_16, toDisplayString(data.description), 1)) : createCommentVNode("", true)
                    ])
                  ]),
                  _: 1
                }, 8, ["data"])
              ])
            ], 512), [
              [vShow, outlineExpanded.value]
            ])
          ]),
          _: 1
        })) : createCommentVNode("", true),
        showEditor.value ? (openBlock(), createBlock(_component_el_card, {
          key: 4,
          class: "editor-section",
          shadow: "never"
        }, {
          default: withCtx(() => [
            createVNode(unref(RichTextEditor), {
              ref_key: "editorRef",
              ref: editorRef,
              modelValue: editorContent.value,
              "onUpdate:modelValue": _cache[8] || (_cache[8] = ($event) => editorContent.value = $event),
              title: "技术方案文档",
              loading: editorLoading.value,
              saving: editorSaving.value,
              onSave: handleEditorSave
            }, null, 8, ["modelValue", "loading", "saving"])
          ]),
          _: 1
        })) : createCommentVNode("", true),
        generationResult.value ? (openBlock(), createBlock(_component_el_card, {
          key: 5,
          class: "result-section",
          shadow: "never"
        }, {
          header: withCtx(() => [
            createBaseVNode("div", _hoisted_17, [
              _cache[35] || (_cache[35] = createBaseVNode("span", null, "✅ 生成结果", -1)),
              createBaseVNode("div", _hoisted_18, [
                createVNode(_component_el_button, {
                  type: "primary",
                  icon: unref(view_default),
                  onClick: previewDocument
                }, {
                  default: withCtx(() => [..._cache[30] || (_cache[30] = [
                    createTextVNode(" 预览文档 ", -1)
                  ])]),
                  _: 1
                }, 8, ["icon"]),
                createVNode(_component_el_button, {
                  type: "success",
                  icon: unref(download_default),
                  onClick: _cache[9] || (_cache[9] = ($event) => downloadDocument("proposal"))
                }, {
                  default: withCtx(() => [..._cache[31] || (_cache[31] = [
                    createTextVNode(" 下载技术方案 ", -1)
                  ])]),
                  _: 1
                }, 8, ["icon"]),
                !unref(synced) ? (openBlock(), createBlock(_component_el_button, {
                  key: 0,
                  type: "info",
                  icon: unref(upload_default),
                  loading: unref(syncing),
                  onClick: handleSyncToHitl
                }, {
                  default: withCtx(() => [..._cache[32] || (_cache[32] = [
                    createTextVNode(" 同步到投标项目 ", -1)
                  ])]),
                  _: 1
                }, 8, ["icon", "loading"])) : (openBlock(), createBlock(_component_el_tag, {
                  key: 1,
                  type: "success",
                  size: "large"
                }, {
                  default: withCtx(() => [..._cache[33] || (_cache[33] = [
                    createTextVNode(" 已同步到投标项目 ", -1)
                  ])]),
                  _: 1
                })),
                createVNode(_component_el_button, {
                  type: "primary",
                  icon: unref(refresh_right_default),
                  onClick: generateProposal
                }, {
                  default: withCtx(() => [..._cache[34] || (_cache[34] = [
                    createTextVNode(" 重新生成 ", -1)
                  ])]),
                  _: 1
                }, 8, ["icon"])
              ])
            ])
          ]),
          default: withCtx(() => {
            var _a, _b, _c, _d;
            return [
              createBaseVNode("div", _hoisted_19, [
                createVNode(unref(StatsCard), {
                  title: "生成统计",
                  stats: generationResult.value,
                  "stat-items": [
                    { key: "requirements_count", label: "需求数量", suffix: "项" },
                    { key: "sections_count", label: "章节数量", suffix: "章" },
                    { key: "matches_count", label: "匹配数量", suffix: "项" }
                  ]
                }, null, 8, ["stats"]),
                createBaseVNode("div", _hoisted_20, [
                  _cache[40] || (_cache[40] = createBaseVNode("h4", null, "输出文件", -1)),
                  createBaseVNode("div", _hoisted_21, [
                    ((_a = generationResult.value.output_files) == null ? void 0 : _a.proposal) ? (openBlock(), createBlock(_component_el_button, {
                      key: 0,
                      type: "success",
                      onClick: _cache[10] || (_cache[10] = ($event) => downloadDocument("proposal"))
                    }, {
                      default: withCtx(() => [
                        createVNode(_component_el_icon, null, {
                          default: withCtx(() => [
                            createVNode(unref(download_default))
                          ]),
                          _: 1
                        }),
                        _cache[36] || (_cache[36] = createTextVNode(" 下载技术方案 ", -1))
                      ]),
                      _: 1
                    })) : createCommentVNode("", true),
                    ((_b = generationResult.value.output_files) == null ? void 0 : _b.analysis) ? (openBlock(), createBlock(_component_el_button, {
                      key: 1,
                      type: "primary",
                      onClick: _cache[11] || (_cache[11] = ($event) => downloadDocument("analysis"))
                    }, {
                      default: withCtx(() => [
                        createVNode(_component_el_icon, null, {
                          default: withCtx(() => [
                            createVNode(unref(download_default))
                          ]),
                          _: 1
                        }),
                        _cache[37] || (_cache[37] = createTextVNode(" 下载需求分析 ", -1))
                      ]),
                      _: 1
                    })) : createCommentVNode("", true),
                    ((_c = generationResult.value.output_files) == null ? void 0 : _c.mapping) ? (openBlock(), createBlock(_component_el_button, {
                      key: 2,
                      type: "info",
                      onClick: _cache[12] || (_cache[12] = ($event) => downloadDocument("mapping"))
                    }, {
                      default: withCtx(() => [
                        createVNode(_component_el_icon, null, {
                          default: withCtx(() => [
                            createVNode(unref(download_default))
                          ]),
                          _: 1
                        }),
                        _cache[38] || (_cache[38] = createTextVNode(" 下载匹配表 ", -1))
                      ]),
                      _: 1
                    })) : createCommentVNode("", true),
                    ((_d = generationResult.value.output_files) == null ? void 0 : _d.summary) ? (openBlock(), createBlock(_component_el_button, {
                      key: 3,
                      type: "warning",
                      onClick: _cache[13] || (_cache[13] = ($event) => downloadDocument("summary"))
                    }, {
                      default: withCtx(() => [
                        createVNode(_component_el_icon, null, {
                          default: withCtx(() => [
                            createVNode(unref(download_default))
                          ]),
                          _: 1
                        }),
                        _cache[39] || (_cache[39] = createTextVNode(" 下载生成报告 ", -1))
                      ]),
                      _: 1
                    })) : createCommentVNode("", true)
                  ])
                ])
              ])
            ];
          }),
          _: 1
        })) : createCommentVNode("", true),
        form.value.projectId ? (openBlock(), createBlock(unref(HistoryFilesPanel), {
          key: 6,
          title: "该项目的技术方案文件",
          "current-file": currentTechFile.value,
          "history-files": historyFiles.value,
          loading: loadingHistory.value,
          "show-stats": false,
          "show-editor-open": true,
          onPreview: previewFile,
          onDownload: downloadHistoryFile,
          onRegenerate: handleRegenerate,
          onRefresh: loadHistoryFiles,
          onOpenInEditor: openHistoryInEditor
        }, null, 8, ["current-file", "history-files", "loading"])) : createCommentVNode("", true),
        createVNode(unref(DocumentPreview), {
          modelValue: previewVisible.value,
          "onUpdate:modelValue": _cache[14] || (_cache[14] = ($event) => previewVisible.value = $event),
          "file-url": previewFileUrl.value,
          "file-name": previewFileName.value
        }, null, 8, ["modelValue", "file-url", "file-name"])
      ]);
    };
  }
});
const TechProposal = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-94c1a540"]]);
export {
  TechProposal as default
};
