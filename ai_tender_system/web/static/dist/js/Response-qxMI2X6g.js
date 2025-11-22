import { d as defineComponent, r as ref, c as computed, S as onMounted, A as ElMessage, e as createElementBlock, o as openBlock, f as createVNode, k as createBlock, l as createCommentVNode, w as withCtx, m as ElAlert, p as createTextVNode, q as ElForm, ak as ElRow, ai as ElCol, s as ElFormItem, Y as ElSelect, F as Fragment, V as renderList, h as unref, W as ElOption, y as ElInput, n as createBaseVNode, as as ElCard, g as ElButton, aC as ElCollapseItem, ay as ElDescriptions, az as ElDescriptionsItem, t as toDisplayString, Q as ElLink, aD as view_default, aE as download_default, aF as upload_default, X as ElTag, aG as refresh_right_default, aH as ElCollapse } from "./vendor-MtO928VE.js";
/* empty css                                                                           */
import { D as DocumentUploader } from "./DocumentUploader-BFiqpCwu.js";
import { D as DocumentPreview } from "./DocumentPreview-9ke4Yi2d.js";
import { R as RichTextEditor } from "./RichTextEditor-Bq9eh2QZ.js";
import { u as useHitlIntegration, H as HitlFileAlert, a as HistoryFilesPanel, S as StatsCard, d as downloadFile } from "./helpers-Bcq2sOJ4.js";
import { e as apiClient, _ as _export_sfc } from "./index.js";
import { t as tenderApi } from "./tender-DvsgeLWX.js";
import { c as companyApi } from "./company-z4Xg082l.js";
import { u as useProjectStore } from "./project-X4Kuz_iO.js";
import { u as useProjectDocuments } from "./useProjectDocuments-CobiuthK.js";
import "./imageCompressor-DC3BCfPz.js";
/* empty css                                                                         */
const businessLegacyApi = {
  /**
   * 处理商务应答（调用旧版API）
   *
   * 功能：
   * - 在Word模板上填充公司信息
   * - 处理表格
   * - 插入图片（营业执照、资质证书等）
   * - 生成真实的.docx文档
   */
  async processBusinessResponse(data) {
    const formData = new FormData();
    formData.append("company_id", data.company_id.toString());
    formData.append("project_name", data.project_name);
    if (data.tender_no) formData.append("tender_no", data.tender_no);
    if (data.date_text) formData.append("date_text", data.date_text);
    formData.append("hitl_file_path", data.hitl_file_path);
    formData.append("use_mcp", data.use_mcp !== false ? "true" : "false");
    return apiClient.post("/process-business-response", formData, {
      headers: {
        "Content-Type": "multipart/form-data"
      }
    });
  }
};
const _hoisted_1 = { class: "business-response" };
const _hoisted_2 = { class: "upload-item" };
const _hoisted_3 = { class: "upload-item" };
const _hoisted_4 = { class: "generation-controls" };
const _hoisted_5 = { class: "card-header" };
const _hoisted_6 = { class: "header-actions" };
const _hoisted_7 = { class: "result-content" };
const _hoisted_8 = { class: "file-info-section" };
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "Response",
  setup(__props) {
    useProjectStore();
    const {
      projects,
      selectedProject,
      loadProjects,
      handleProjectChange: handleProjectChangeComposable,
      restoreProjectFromStore
    } = useProjectDocuments();
    const {
      useHitlFile: useHitlTemplate,
      hitlFileInfo: hitlTemplateInfo,
      syncing,
      synced,
      loadFromHITL: loadTemplateFromHITL,
      cancelHitlFile: cancelHitlTemplate,
      syncToHitl
    } = useHitlIntegration({
      onFileLoaded: () => {
        form.value.templateFiles = [];
      }
    });
    const {
      useHitlFile: useHitlTender,
      hitlFileInfo: hitlTenderInfo,
      loadFromHITL: loadTenderFromHITL,
      cancelHitlFile: cancelHitlTender
    } = useHitlIntegration({
      onFileLoaded: () => {
        form.value.tenderFiles = [];
      }
    });
    const form = ref({
      projectId: null,
      companyId: null,
      // 新建项目：公司ID
      projectName: "新项目",
      // 新建项目：项目名称
      projectNumber: `PRJ-${Date.now()}`,
      // 新建项目：项目编号
      tenderFiles: [],
      templateFiles: []
    });
    const companies = ref([]);
    computed(
      () => companies.value.find((c) => c.company_id === form.value.companyId)
    );
    const canGenerate = computed(
      () => form.value.projectId && (form.value.templateFiles.length > 0 || useHitlTemplate.value)
    );
    const generating = ref(false);
    const generationProgress = ref(0);
    const streamContent = ref("");
    const generationResult = ref(null);
    const showEditor = ref(false);
    const editorRef = ref(null);
    const editorContent = ref("");
    const editorSaving = ref(false);
    const previewVisible = ref(false);
    const activeCollapse = ref([]);
    const handleTemplateUpload = async (options) => {
      var _a;
      const { file, onSuccess, onError } = options;
      try {
        if (!form.value.projectId) {
          if (!form.value.companyId) {
            throw new Error("请先选择公司");
          }
          ElMessage.info("正在创建新项目...");
          const createResponse = await tenderApi.createProject({
            company_id: form.value.companyId,
            project_name: form.value.projectName || "新项目",
            project_number: form.value.projectNumber || `PRJ-${Date.now()}`
          });
          form.value.projectId = createResponse.project_id;
          await loadProjects();
          ElMessage.success("新项目已创建");
          await handleProjectChange();
        }
        const companyId = (_a = selectedProject.value) == null ? void 0 : _a.company_id;
        if (!companyId) {
          throw new Error("项目没有关联公司");
        }
        const formData = new FormData();
        formData.append("file", file);
        formData.append("company_id", companyId.toString());
        formData.append("project_id", form.value.projectId.toString());
        const response = await tenderApi.parseDocumentStructure(formData);
        if (response.success) {
          onSuccess(response.data);
          ElMessage.success("商务应答模板上传成功");
        } else {
          throw new Error(response.message || "上传失败");
        }
      } catch (error) {
        onError(error);
        ElMessage.error(error.message || "模板上传失败");
      }
    };
    const handleTenderUpload = async (options) => {
      var _a;
      const { file, onSuccess, onError } = options;
      try {
        if (!form.value.projectId) {
          if (!form.value.companyId) {
            throw new Error("请先选择公司");
          }
          ElMessage.info("正在创建新项目...");
          const createResponse = await tenderApi.createProject({
            company_id: form.value.companyId,
            project_name: form.value.projectName || "新项目",
            project_number: form.value.projectNumber || `PRJ-${Date.now()}`
          });
          form.value.projectId = createResponse.project_id;
          await loadProjects();
          ElMessage.success("新项目已创建");
          await handleProjectChange();
        }
        const companyId = (_a = selectedProject.value) == null ? void 0 : _a.company_id;
        if (!companyId) {
          throw new Error("项目没有关联公司");
        }
        const formData = new FormData();
        formData.append("file", file);
        formData.append("company_id", companyId.toString());
        formData.append("project_id", form.value.projectId.toString());
        const response = await tenderApi.parseDocumentStructure(formData);
        if (response.success) {
          onSuccess(response.data);
          ElMessage.success("招标文档上传成功");
        } else {
          throw new Error(response.message || "上传失败");
        }
      } catch (error) {
        onError(error);
        ElMessage.error(error.message || "招标文档上传失败");
      }
    };
    const loadCompanies = async () => {
      try {
        const response = await companyApi.getCompanies();
        companies.value = response.data || [];
      } catch (error) {
        console.error("加载公司列表失败:", error);
        ElMessage.error("加载公司列表失败");
      }
    };
    const handleProjectChange = async () => {
      await handleProjectChangeComposable(form.value.projectId, {
        // 清空回调：清空页面特定状态
        onClear: () => {
          generationResult.value = null;
          streamContent.value = "";
          form.value.tenderFiles = [];
          form.value.templateFiles = [];
          showEditor.value = false;
          editorContent.value = "";
          activeCollapse.value = [];
          if (useHitlTemplate.value) {
            cancelHitlTemplate();
          }
          if (useHitlTender.value) {
            cancelHitlTender();
          }
        },
        // 文档加载完成回调：同步到页面状态
        onDocumentsLoaded: (docs) => {
          if (docs.tenderFile) {
            loadTenderFromHITL(docs, "tenderFile");
          }
          if (docs.templateFile) {
            loadTemplateFromHITL(docs, "templateFile");
          }
          if (docs.businessResponseFile) {
            generationResult.value = docs.businessResponseFile;
            showEditor.value = false;
            console.log("[Response] 检测到历史商务应答文件:", docs.businessResponseFile.outputFile);
            ElMessage.info('检测到历史商务应答文件，点击"在编辑器中打开"可编辑');
          }
        }
      });
      if (!form.value.projectId) {
        form.value.projectNumber = `PRJ-${Date.now()}`;
      }
    };
    const handleTenderUploadSuccess = () => {
      ElMessage.success("招标文档上传成功");
    };
    const handleTemplateUploadSuccess = () => {
      ElMessage.success("商务应答模板上传成功");
    };
    const startGeneration = async () => {
      var _a;
      if (!form.value.projectId) {
        ElMessage.warning("请先选择项目");
        return;
      }
      generating.value = true;
      generationProgress.value = 0;
      streamContent.value = "";
      generationResult.value = null;
      showEditor.value = true;
      editorContent.value = '<h1>📄 商务应答文档</h1><p style="color: #909399;">AI正在生成内容，请稍候...</p>';
      setTimeout(() => {
        var _a2;
        (_a2 = document.querySelector(".editor-section")) == null ? void 0 : _a2.scrollIntoView({
          behavior: "smooth",
          block: "start"
        });
      }, 100);
      try {
        streamContent.value = "正在加载项目信息...\n";
        const projectResponse = await tenderApi.getProject(form.value.projectId);
        const projectData = projectResponse.data;
        const templateFilePath = (_a = projectData.step1_data) == null ? void 0 : _a.response_file_path;
        if (!templateFilePath) {
          throw new Error("未找到商务应答模板文件路径，请先在标书管理中上传模板");
        }
        streamContent.value += "正在处理商务应答文档...\n";
        generationProgress.value = 30;
        const response = await businessLegacyApi.processBusinessResponse({
          company_id: projectData.company_id,
          project_name: projectData.project_name,
          tender_no: projectData.project_number || "",
          date_text: projectData.bidding_time || "",
          hitl_file_path: templateFilePath,
          use_mcp: true
        });
        generationProgress.value = 80;
        streamContent.value += "处理完成，正在生成结果...\n";
        console.log("完整响应:", response);
        console.log("response.data:", response.data);
        console.log("response.success:", response.success);
        const result = response.data ? response.data : response;
        console.log("处理后的result:", result);
        if (result.success) {
          generationProgress.value = 100;
          streamContent.value += result.message + "\n";
          generationResult.value = {
            success: true,
            outputFile: result.output_file,
            downloadUrl: result.download_url,
            stats: result.stats || {},
            message: result.message
          };
          await loadWordToEditor(result.output_file);
          ElMessage.success("商务应答生成完成！可以编辑了");
          if (result.output_file && form.value.projectId) {
            await syncToHitl(
              form.value.projectId,
              result.output_file,
              "business_response"
            );
          }
        } else {
          throw new Error(result.message || result.error || "处理失败");
        }
      } catch (error) {
        console.error("生成失败:", error);
        streamContent.value += `
❌ 错误: ${error.message}
`;
        if (editorRef.value) {
          editorRef.value.appendContent(`<p style="color: red;">❌ 错误: ${error.message}</p>`);
        }
        ElMessage.error(error.message || "生成失败，请重试");
      } finally {
        generating.value = false;
        if (generationProgress.value < 100) {
          generationProgress.value = 0;
        }
      }
    };
    const loadWordToEditor = async (filePath) => {
      try {
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
          console.log("[Response] Word文档已加载到编辑器");
        } else {
          throw new Error(result.error || "转换失败");
        }
      } catch (error) {
        console.error("[Response] 加载文档到编辑器失败:", error);
        editorContent.value = `
      <h1>📄 商务应答文档</h1>
      <div style="padding: 20px; background: #FFF3E0; border-left: 4px solid #FF9800; margin: 16px 0;">
        <p><strong>⚠️ 提示：</strong>Word文档转换失败</p>
        <p>原因：${error.message}</p>
        <p>您可以：</p>
        <ul>
          <li>直接在此编辑器中输入内容</li>
          <li>或点击下方"查看原始生成结果"下载Word文档查看</li>
        </ul>
      </div>
      <p>开始编辑您的内容...</p>
    `;
        ElMessage.warning("Word转换HTML失败，请使用下载功能或手动输入");
      }
    };
    const handleEditorSave = async (htmlContent) => {
      var _a, _b;
      if (!form.value.projectId) {
        ElMessage.error("项目ID无效");
        return;
      }
      editorSaving.value = true;
      try {
        const response = await fetch("/api/editor/save-html-to-word", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            html_content: htmlContent,
            project_id: form.value.projectId,
            document_type: "business_response",
            original_file: (_a = generationResult.value) == null ? void 0 : _a.outputFile
          })
        });
        const result = await response.json();
        if (result.success) {
          generationResult.value = {
            success: true,
            outputFile: result.output_file,
            downloadUrl: result.download_url,
            stats: ((_b = generationResult.value) == null ? void 0 : _b.stats) || {},
            message: "文档已保存"
          };
          console.log("[Response] 编辑内容已保存:", result.output_file);
          if (result.output_file) {
            await syncToHitl(
              form.value.projectId,
              result.output_file,
              "business_response"
            );
          }
        } else {
          throw new Error(result.error || "保存失败");
        }
      } catch (error) {
        console.error("[Response] 保存编辑内容失败:", error);
        throw error;
      } finally {
        editorSaving.value = false;
      }
    };
    const previewDocument = () => {
      if (!generationResult.value) {
        ElMessage.warning("暂无文档可预览");
        return;
      }
      if (!generationResult.value.downloadUrl) {
        ElMessage.warning("文档地址无效");
        return;
      }
      previewVisible.value = true;
    };
    const downloadDocument = () => {
      var _a;
      if (!generationResult.value) {
        ElMessage.warning("暂无文档可下载");
        return;
      }
      try {
        const url = generationResult.value.downloadUrl;
        const filename = `商务应答-${((_a = selectedProject.value) == null ? void 0 : _a.project_name) || "文档"}-${Date.now()}.docx`;
        downloadFile(url, filename);
        ElMessage.success("Word文档下载成功");
      } catch (error) {
        console.error("下载失败:", error);
        ElMessage.error("文档下载失败，请重试");
      }
    };
    const handleSyncToHitl = async () => {
      var _a;
      if (!((_a = generationResult.value) == null ? void 0 : _a.outputFile)) {
        ElMessage.warning("没有可同步的文件");
        return;
      }
      if (!form.value.projectId) {
        ElMessage.error("项目ID无效");
        return;
      }
      await syncToHitl(
        form.value.projectId,
        generationResult.value.outputFile,
        "business_response"
      );
    };
    const getFileName = (path) => {
      if (!path) return "-";
      let decodedPath = path;
      try {
        decodedPath = decodeURIComponent(path);
      } catch {
      }
      const parts = decodedPath.split("/");
      return parts[parts.length - 1] || "-";
    };
    const openHistoryInEditor = async () => {
      var _a;
      if (!((_a = generationResult.value) == null ? void 0 : _a.outputFile)) {
        ElMessage.error("历史文件信息无效");
        return;
      }
      try {
        showEditor.value = true;
        await loadWordToEditor(generationResult.value.outputFile);
        ElMessage.success("历史文件已加载到编辑器");
        setTimeout(() => {
          var _a2;
          (_a2 = document.querySelector(".editor-section")) == null ? void 0 : _a2.scrollIntoView({
            behavior: "smooth",
            block: "start"
          });
        }, 100);
      } catch (error) {
        console.error("[Response] 打开历史文件失败:", error);
        ElMessage.error("打开历史文件失败: " + error.message);
      }
    };
    onMounted(async () => {
      await Promise.all([
        loadProjects(),
        loadCompanies()
      ]);
      const restoredProjectId = await restoreProjectFromStore({
        onClear: () => {
          generationResult.value = null;
          streamContent.value = "";
          form.value.tenderFiles = [];
          form.value.templateFiles = [];
          showEditor.value = false;
          editorContent.value = "";
          if (useHitlTemplate.value) {
            cancelHitlTemplate();
          }
          if (useHitlTender.value) {
            cancelHitlTender();
          }
        },
        onDocumentsLoaded: (docs) => {
          if (docs.tenderFile) {
            loadTenderFromHITL(docs, "tenderFile");
          }
          if (docs.templateFile) {
            loadTemplateFromHITL(docs, "templateFile");
          }
          if (docs.businessResponseFile) {
            generationResult.value = docs.businessResponseFile;
            showEditor.value = false;
            console.log("[Response] 从Store恢复历史商务应答文件:", docs.businessResponseFile.outputFile);
            ElMessage.info('检测到历史商务应答文件，点击"在编辑器中打开"可编辑');
          }
        }
      });
      if (restoredProjectId) {
        form.value.projectId = restoredProjectId;
        console.log("✅ 已从Store恢复项目:", restoredProjectId);
      }
    });
    return (_ctx, _cache) => {
      var _a, _b;
      const _component_el_alert = ElAlert;
      const _component_el_option = ElOption;
      const _component_el_select = ElSelect;
      const _component_el_form_item = ElFormItem;
      const _component_el_col = ElCol;
      const _component_el_input = ElInput;
      const _component_el_row = ElRow;
      const _component_el_form = ElForm;
      const _component_el_card = ElCard;
      const _component_el_button = ElButton;
      const _component_el_tag = ElTag;
      const _component_el_descriptions_item = ElDescriptionsItem;
      const _component_el_link = ElLink;
      const _component_el_descriptions = ElDescriptions;
      const _component_el_collapse_item = ElCollapseItem;
      const _component_el_collapse = ElCollapse;
      return openBlock(), createElementBlock("div", _hoisted_1, [
        createVNode(_component_el_card, {
          class: "project-section",
          shadow: "never"
        }, {
          header: withCtx(() => [..._cache[9] || (_cache[9] = [
            createBaseVNode("div", { class: "card-header" }, [
              createBaseVNode("span", null, "Step 1: 选择项目")
            ], -1)
          ])]),
          default: withCtx(() => [
            createVNode(_component_el_alert, {
              type: "info",
              closable: false,
              style: { "margin-bottom": "16px" }
            }, {
              default: withCtx(() => [..._cache[10] || (_cache[10] = [
                createTextVNode(" 💡 提示：可选择现有项目，或选择公司后新建项目并上传文档 ", -1)
              ])]),
              _: 1
            }),
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
                              placeholder: "请选择项目或直接新建",
                              filterable: "",
                              clearable: "",
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
                            var _a2;
                            return [
                              form.value.projectId ? (openBlock(), createBlock(_component_el_input, {
                                key: 0,
                                value: ((_a2 = unref(selectedProject)) == null ? void 0 : _a2.company_name) || "-",
                                disabled: ""
                              }, null, 8, ["value"])) : (openBlock(), createBlock(_component_el_select, {
                                key: 1,
                                modelValue: form.value.companyId,
                                "onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => form.value.companyId = $event),
                                placeholder: "请选择公司（必填）",
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
                              }, 8, ["modelValue"]))
                            ];
                          }),
                          _: 1
                        })
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                }),
                !form.value.projectId ? (openBlock(), createBlock(_component_el_row, {
                  key: 0,
                  gutter: 20
                }, {
                  default: withCtx(() => [
                    createVNode(_component_el_col, { span: 12 }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, { label: "项目名称" }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: form.value.projectName,
                              "onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => form.value.projectName = $event),
                              placeholder: "新项目"
                            }, null, 8, ["modelValue"])
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    createVNode(_component_el_col, { span: 12 }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, { label: "项目编号" }, {
                          default: withCtx(() => [
                            createVNode(_component_el_input, {
                              modelValue: form.value.projectNumber,
                              "onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => form.value.projectNumber = $event),
                              placeholder: "PRJ-..."
                            }, null, 8, ["modelValue"])
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                })) : createCommentVNode("", true)
              ]),
              _: 1
            }, 8, ["model"])
          ]),
          _: 1
        }),
        createVNode(_component_el_card, {
          class: "upload-section",
          shadow: "never"
        }, {
          header: withCtx(() => [..._cache[11] || (_cache[11] = [
            createBaseVNode("div", { class: "card-header" }, [
              createBaseVNode("span", null, "Step 2: 上传相关文档")
            ], -1)
          ])]),
          default: withCtx(() => [
            createVNode(_component_el_row, { gutter: 20 }, {
              default: withCtx(() => [
                createVNode(_component_el_col, { span: 12 }, {
                  default: withCtx(() => [
                    createBaseVNode("div", _hoisted_2, [
                      _cache[12] || (_cache[12] = createBaseVNode("h4", null, [
                        createTextVNode("商务应答模板 "),
                        createBaseVNode("span", { class: "required" }, "*")
                      ], -1)),
                      unref(useHitlTemplate) ? (openBlock(), createBlock(unref(HitlFileAlert), {
                        key: 0,
                        "file-info": unref(hitlTemplateInfo),
                        label: "商务应答模板:",
                        onCancel: unref(cancelHitlTemplate)
                      }, null, 8, ["file-info", "onCancel"])) : createCommentVNode("", true),
                      !unref(useHitlTemplate) ? (openBlock(), createBlock(unref(DocumentUploader), {
                        key: 1,
                        modelValue: form.value.templateFiles,
                        "onUpdate:modelValue": _cache[4] || (_cache[4] = ($event) => form.value.templateFiles = $event),
                        "http-request": handleTemplateUpload,
                        accept: ".doc,.docx",
                        limit: 1,
                        "max-size": 20,
                        drag: "",
                        "tip-text": "必须上传商务应答模板，用于生成应答文档",
                        onSuccess: handleTemplateUploadSuccess
                      }, null, 8, ["modelValue"])) : createCommentVNode("", true)
                    ])
                  ]),
                  _: 1
                }),
                createVNode(_component_el_col, { span: 12 }, {
                  default: withCtx(() => [
                    createBaseVNode("div", _hoisted_3, [
                      _cache[13] || (_cache[13] = createBaseVNode("h4", null, "招标文档（可选）", -1)),
                      unref(useHitlTender) ? (openBlock(), createBlock(unref(HitlFileAlert), {
                        key: 0,
                        "file-info": unref(hitlTenderInfo),
                        label: "招标文档:",
                        onCancel: unref(cancelHitlTender)
                      }, null, 8, ["file-info", "onCancel"])) : createCommentVNode("", true),
                      !unref(useHitlTender) ? (openBlock(), createBlock(unref(DocumentUploader), {
                        key: 1,
                        modelValue: form.value.tenderFiles,
                        "onUpdate:modelValue": _cache[5] || (_cache[5] = ($event) => form.value.tenderFiles = $event),
                        "http-request": handleTenderUpload,
                        accept: ".pdf,.doc,.docx",
                        limit: 5,
                        "max-size": 50,
                        drag: "",
                        "tip-text": "可选上传招标文档作为参考，支持PDF、Word格式，最大50MB",
                        onSuccess: handleTenderUploadSuccess
                      }, null, 8, ["modelValue"])) : createCommentVNode("", true)
                    ])
                  ]),
                  _: 1
                })
              ]),
              _: 1
            }),
            createBaseVNode("div", _hoisted_4, [
              createVNode(_component_el_button, {
                type: "primary",
                size: "large",
                disabled: !canGenerate.value,
                loading: generating.value,
                onClick: startGeneration
              }, {
                default: withCtx(() => [..._cache[14] || (_cache[14] = [
                  createTextVNode(" 开始生成商务应答 ", -1)
                ])]),
                _: 1
              }, 8, ["disabled", "loading"])
            ])
          ]),
          _: 1
        }),
        generationResult.value && !showEditor.value ? (openBlock(), createBlock(unref(HistoryFilesPanel), {
          key: 0,
          title: "📄 该项目已有商务应答文件",
          "current-file": generationResult.value,
          "history-files": [],
          "show-editor-open": true,
          "show-stats": true,
          "current-file-message": "检测到该项目的历史商务应答文件",
          onOpenInEditor: openHistoryInEditor,
          onPreview: previewDocument,
          onDownload: downloadDocument,
          onRegenerate: startGeneration
        }, null, 8, ["current-file"])) : createCommentVNode("", true),
        showEditor.value ? (openBlock(), createBlock(_component_el_card, {
          key: 1,
          class: "editor-section",
          shadow: "never"
        }, {
          default: withCtx(() => [
            createVNode(unref(RichTextEditor), {
              ref_key: "editorRef",
              ref: editorRef,
              modelValue: editorContent.value,
              "onUpdate:modelValue": _cache[6] || (_cache[6] = ($event) => editorContent.value = $event),
              title: "商务应答文档",
              streaming: generating.value,
              height: 1e3,
              onSave: handleEditorSave,
              onPreview: previewDocument,
              onExport: downloadDocument
            }, null, 8, ["modelValue", "streaming"])
          ]),
          _: 1
        })) : createCommentVNode("", true),
        showEditor.value && generationResult.value ? (openBlock(), createBlock(_component_el_collapse, {
          key: 2,
          modelValue: activeCollapse.value,
          "onUpdate:modelValue": _cache[7] || (_cache[7] = ($event) => activeCollapse.value = $event),
          class: "result-collapse"
        }, {
          default: withCtx(() => [
            createVNode(_component_el_collapse_item, {
              name: "result",
              title: "📄 查看原始生成结果"
            }, {
              default: withCtx(() => [
                createVNode(_component_el_card, {
                  class: "result-section",
                  shadow: "never"
                }, {
                  header: withCtx(() => [
                    createBaseVNode("div", _hoisted_5, [
                      createBaseVNode("span", null, toDisplayString(generationResult.value.isHistory ? "📄 历史应答文件" : "✅ 生成结果"), 1),
                      createBaseVNode("div", _hoisted_6, [
                        createVNode(_component_el_button, {
                          type: "primary",
                          icon: unref(view_default),
                          onClick: previewDocument
                        }, {
                          default: withCtx(() => [..._cache[15] || (_cache[15] = [
                            createTextVNode(" 预览文档 ", -1)
                          ])]),
                          _: 1
                        }, 8, ["icon"]),
                        createVNode(_component_el_button, {
                          type: "success",
                          icon: unref(download_default),
                          onClick: downloadDocument
                        }, {
                          default: withCtx(() => [..._cache[16] || (_cache[16] = [
                            createTextVNode(" 下载Word文档 ", -1)
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
                          default: withCtx(() => [..._cache[17] || (_cache[17] = [
                            createTextVNode(" 同步到投标项目 ", -1)
                          ])]),
                          _: 1
                        }, 8, ["icon", "loading"])) : (openBlock(), createBlock(_component_el_tag, {
                          key: 1,
                          type: "success",
                          size: "large"
                        }, {
                          default: withCtx(() => [..._cache[18] || (_cache[18] = [
                            createTextVNode(" 已同步到投标项目 ", -1)
                          ])]),
                          _: 1
                        })),
                        createVNode(_component_el_button, {
                          type: "primary",
                          icon: unref(refresh_right_default),
                          onClick: startGeneration
                        }, {
                          default: withCtx(() => [..._cache[19] || (_cache[19] = [
                            createTextVNode(" 重新生成 ", -1)
                          ])]),
                          _: 1
                        }, 8, ["icon"])
                      ])
                    ])
                  ]),
                  default: withCtx(() => [
                    createBaseVNode("div", _hoisted_7, [
                      createVNode(_component_el_alert, {
                        type: generationResult.value.isHistory ? "info" : "success",
                        title: generationResult.value.message,
                        closable: false,
                        "show-icon": "",
                        style: { "margin-bottom": "20px" }
                      }, null, 8, ["type", "title"]),
                      createVNode(unref(StatsCard), {
                        title: "处理统计",
                        stats: generationResult.value.stats
                      }, null, 8, ["stats"]),
                      createBaseVNode("div", _hoisted_8, [
                        _cache[20] || (_cache[20] = createBaseVNode("h4", null, "生成文件", -1)),
                        createVNode(_component_el_descriptions, {
                          column: 2,
                          border: ""
                        }, {
                          default: withCtx(() => [
                            createVNode(_component_el_descriptions_item, { label: "文件名" }, {
                              default: withCtx(() => [
                                createTextVNode(toDisplayString(getFileName(generationResult.value.outputFile)), 1)
                              ]),
                              _: 1
                            }),
                            createVNode(_component_el_descriptions_item, { label: "下载地址" }, {
                              default: withCtx(() => [
                                createVNode(_component_el_link, {
                                  href: generationResult.value.downloadUrl,
                                  type: "primary"
                                }, {
                                  default: withCtx(() => [
                                    createTextVNode(toDisplayString(getFileName(generationResult.value.downloadUrl)), 1)
                                  ]),
                                  _: 1
                                }, 8, ["href"])
                              ]),
                              _: 1
                            })
                          ]),
                          _: 1
                        })
                      ])
                    ])
                  ]),
                  _: 1
                })
              ]),
              _: 1
            })
          ]),
          _: 1
        }, 8, ["modelValue"])) : createCommentVNode("", true),
        createVNode(unref(DocumentPreview), {
          modelValue: previewVisible.value,
          "onUpdate:modelValue": _cache[8] || (_cache[8] = ($event) => previewVisible.value = $event),
          "file-url": (_a = generationResult.value) == null ? void 0 : _a.downloadUrl,
          "file-name": `商务应答-${((_b = unref(selectedProject)) == null ? void 0 : _b.project_name) || "文档"}.docx`
        }, null, 8, ["modelValue", "file-url", "file-name"])
      ]);
    };
  }
});
const Response = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-8de17eee"]]);
export {
  Response as default
};
