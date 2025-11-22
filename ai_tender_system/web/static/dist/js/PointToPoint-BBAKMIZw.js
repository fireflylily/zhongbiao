import { d as defineComponent, r as ref, c as computed, D as watch, S as onMounted, e as createElementBlock, o as openBlock, f as createVNode, k as createBlock, l as createCommentVNode, w as withCtx, q as ElForm, ak as ElRow, ai as ElCol, s as ElFormItem, Y as ElSelect, F as Fragment, V as renderList, h as unref, W as ElOption, y as ElInput, n as createBaseVNode, as as ElCard, a6 as ElDivider, p as createTextVNode, v as ElRadioGroup, x as ElRadio, g as ElButton, aL as ElProgress, aC as ElCollapseItem, m as ElAlert, ay as ElDescriptions, az as ElDescriptionsItem, t as toDisplayString, Q as ElLink, aD as view_default, aE as download_default, aF as upload_default, X as ElTag, aG as refresh_right_default, aH as ElCollapse, al as ElTable, am as ElTableColumn, ad as ElIcon, aZ as search_default, j as ElDialog, aa as withDirectives, ae as document_default, aJ as vLoading, ar as ElEmpty, R as withModifiers, A as ElMessage } from "./vendor-MtO928VE.js";
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
const _hoisted_1 = { class: "point-to-point" };
const _hoisted_2 = { class: "card-header" };
const _hoisted_3 = { class: "action-controls" };
const _hoisted_4 = { class: "card-header" };
const _hoisted_5 = { class: "card-header" };
const _hoisted_6 = { class: "header-actions" };
const _hoisted_7 = { class: "result-content" };
const _hoisted_8 = { class: "file-info-section" };
const _hoisted_9 = { class: "card-header" };
const _hoisted_10 = { class: "header-actions" };
const _hoisted_11 = { class: "requirement-text" };
const _hoisted_12 = { class: "card-header" };
const _hoisted_13 = { class: "card-header" };
const _hoisted_14 = { class: "header-actions" };
const _hoisted_15 = { class: "collapse-title" };
const _hoisted_16 = { class: "requirement-preview" };
const _hoisted_17 = { class: "response-content" };
const _hoisted_18 = { class: "response-item" };
const _hoisted_19 = { class: "requirement-detail" };
const _hoisted_20 = { class: "response-item" };
const _hoisted_21 = {
  key: 0,
  class: "response-item"
};
const _hoisted_22 = {
  key: 0,
  class: "response-dialog"
};
const _hoisted_23 = { class: "dialog-section" };
const _hoisted_24 = { class: "requirement-detail" };
const _hoisted_25 = { class: "dialog-section" };
const _hoisted_26 = {
  key: 0,
  class: "dialog-section"
};
const _hoisted_27 = { class: "collapse-header" };
const _hoisted_28 = { class: "filename-cell" };
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "PointToPoint",
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
    const form = ref({
      projectId: null,
      tenderFiles: []
    });
    const config = ref({
      bidRole: "primary",
      responseFrequency: "every_paragraph",
      responseMode: "simple",
      aiModel: "shihuang-gpt4o-mini"
    });
    const extracting = ref(false);
    const extractProgress = ref(0);
    const extractContent = ref("");
    const requirements = ref([]);
    const selectedRequirements = ref([]);
    const searchKeyword = ref("");
    const filterCategory = ref("");
    const filteredRequirements = computed(() => {
      let filtered = requirements.value;
      if (searchKeyword.value) {
        filtered = filtered.filter(
          (req) => req.requirement.toLowerCase().includes(searchKeyword.value.toLowerCase())
        );
      }
      if (filterCategory.value) {
        filtered = filtered.filter((req) => req.category === filterCategory.value);
      }
      return filtered;
    });
    const generating = ref(false);
    const generationProgress = ref(0);
    const streamContent = ref("");
    const outputFile = ref("");
    const downloadUrl = ref("");
    const processingStats = ref(null);
    const generationResult = ref(null);
    const showEditor = ref(false);
    const editorRef = ref(null);
    const editorContent = ref("");
    const editorSaving = ref(false);
    const activeCollapse = ref([]);
    const currentP2pFile = ref(null);
    const historyFiles = ref([]);
    const loadingHistory = ref(false);
    const showAllHistory = ref([]);
    const previewVisible = ref(false);
    const previewFileUrl = ref("");
    const previewFileName = ref("");
    const hasResponses = computed(
      () => requirements.value.some((req) => req.response)
    );
    const activeResponses = ref([]);
    const responseDialogVisible = ref(false);
    const currentRequirement = ref(null);
    const canExtract = computed(
      () => form.value.projectId && (form.value.tenderFiles.length > 0 || useHitlFile.value)
    );
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
          ElMessage.success("招标文档上传成功");
        } else {
          throw new Error(response.message || "上传失败");
        }
      } catch (error) {
        onError(error);
        ElMessage.error(error.message || "招标文档上传失败");
      }
    };
    const handleProjectChange = async () => {
      await handleProjectChangeComposable(form.value.projectId, {
        // 清空回调：清空页面特定状态
        onClear: () => {
          form.value.tenderFiles = [];
          requirements.value = [];
          selectedRequirements.value = [];
          currentP2pFile.value = null;
          generationResult.value = null;
          showEditor.value = false;
          editorContent.value = "";
          activeCollapse.value = [];
          if (useHitlFile.value) {
            cancelHitlFile();
          }
        },
        // 文档加载完成回调：使用共享函数
        onDocumentsLoaded: handleDocumentsLoaded
      });
    };
    const handleUploadSuccess = () => {
      ElMessage.success("文档上传成功");
    };
    const handleDocumentsLoaded = (docs) => {
      if (docs.technicalFile) {
        loadFromHITL(docs, "technicalFile");
      } else if (docs.tenderFile) {
        form.value.tenderFiles = [docs.tenderFile];
      }
      if (docs.p2pResponseFile) {
        currentP2pFile.value = docs.p2pResponseFile;
        showEditor.value = false;
        console.log("[PointToPoint] 检测到历史点对点应答文件:", docs.p2pResponseFile.outputFile);
        ElMessage.info('检测到历史点对点应答文件，点击"在编辑器中打开"可编辑');
      }
    };
    const extractRequirements = async () => {
      extracting.value = true;
      extractProgress.value = 0;
      extractContent.value = "";
      requirements.value = [];
      try {
        await simulateExtraction();
        ElMessage.success("招标要求提取完成");
      } catch (error) {
        console.error("提取失败:", error);
        ElMessage.error("提取失败，请重试");
      } finally {
        extracting.value = false;
      }
    };
    const simulateExtraction = async () => {
      return new Promise((resolve) => {
        const stages = [
          { progress: 25, message: "正在解析招标文档..." },
          { progress: 50, message: "正在识别招标要求..." },
          { progress: 75, message: "正在分类整理..." },
          { progress: 100, message: "提取完成！" }
        ];
        let currentStage = 0;
        const interval = setInterval(() => {
          if (currentStage < stages.length) {
            const stage = stages[currentStage];
            extractProgress.value = stage.progress;
            extractContent.value += `
[${stage.progress}%] ${stage.message}`;
            currentStage++;
          } else {
            clearInterval(interval);
            requirements.value = [
              {
                id: 1,
                category: "technical",
                requirement: "系统应支持不少于10000个并发用户同时在线访问",
                priority: "高",
                status: "pending"
              },
              {
                id: 2,
                category: "technical",
                requirement: "系统响应时间应不超过3秒",
                priority: "高",
                status: "pending"
              },
              {
                id: 3,
                category: "business",
                requirement: "项目实施周期不超过6个月",
                priority: "高",
                status: "pending"
              },
              {
                id: 4,
                category: "qualification",
                requirement: "投标人应具有ISO 9001质量管理体系认证",
                priority: "中",
                status: "pending"
              },
              {
                id: 5,
                category: "qualification",
                requirement: "投标人应具有信息安全等级保护三级资质",
                priority: "中",
                status: "pending"
              },
              {
                id: 6,
                category: "business",
                requirement: "质保期不少于2年",
                priority: "中",
                status: "pending"
              },
              {
                id: 7,
                category: "technical",
                requirement: "系统应支持移动端访问（iOS和Android）",
                priority: "中",
                status: "pending"
              },
              {
                id: 8,
                category: "other",
                requirement: "投标文件应包含详细的培训计划",
                priority: "低",
                status: "pending"
              }
            ];
            resolve();
          }
        }, 600);
      });
    };
    const handleSelectionChange = (selection) => {
      selectedRequirements.value = selection;
    };
    const generateResponses = async () => {
      if (selectedRequirements.value.length === 0) {
        ElMessage.warning("请选择要生成应答的要求");
        return;
      }
      generating.value = true;
      generationProgress.value = 0;
      streamContent.value = "";
      try {
        await simulateGeneration();
        ElMessage.success("点对点应答生成完成");
      } catch (error) {
        console.error("生成失败:", error);
        ElMessage.error("生成失败，请重试");
      } finally {
        generating.value = false;
      }
    };
    const simulateGeneration = async () => {
      return new Promise((resolve) => {
        const total = selectedRequirements.value.length;
        let current = 0;
        const interval = setInterval(() => {
          if (current < total) {
            const req = selectedRequirements.value[current];
            generationProgress.value = Math.round((current + 1) / total * 100);
            streamContent.value += `
[${current + 1}/${total}] 正在生成"${req.requirement.substring(0, 20)}..."的应答`;
            const index = requirements.value.findIndex((r) => r.id === req.id);
            if (index !== -1) {
              requirements.value[index] = {
                ...requirements.value[index],
                status: "generated",
                response: generateMockResponse(req),
                compliance: Math.random() > 0.3 ? "完全符合" : "部分符合"
              };
            }
            current++;
          } else {
            clearInterval(interval);
            resolve();
          }
        }, 800);
      });
    };
    const processPointToPointDirect = async () => {
      if (!form.value.projectId || !selectedProject.value) {
        ElMessage.error("请先选择项目");
        return;
      }
      if (!useHitlFile.value && form.value.tenderFiles.length === 0) {
        ElMessage.error("请先上传招标文档或使用技术文件");
        return;
      }
      generating.value = true;
      generationProgress.value = 0;
      generationResult.value = null;
      showEditor.value = true;
      editorContent.value = '<h1>📄 点对点应答文档</h1><p style="color: #909399;">AI正在生成内联应答，请稍候...</p>';
      setTimeout(() => {
        var _a;
        (_a = document.querySelector(".editor-section")) == null ? void 0 : _a.scrollIntoView({
          behavior: "smooth",
          block: "start"
        });
      }, 100);
      try {
        const formData = new FormData();
        if (useHitlFile.value && hitlFileInfo.value) {
          formData.append("use_hitl_technical_file", "true");
          formData.append("project_id", form.value.projectId.toString());
        } else {
          if (form.value.tenderFiles.length > 0 && form.value.tenderFiles[0].raw) {
            formData.append("file", form.value.tenderFiles[0].raw);
          }
        }
        formData.append("companyId", selectedProject.value.company_id.toString());
        formData.append("projectName", selectedProject.value.project_name || "");
        formData.append("responseFrequency", config.value.responseFrequency);
        formData.append("responseMode", config.value.responseMode);
        formData.append("aiModel", config.value.aiModel);
        const response = await fetch("/api/process-point-to-point", {
          method: "POST",
          body: formData
        });
        console.log("点对点应答API响应状态:", response.status, response.statusText);
        const result = await response.json();
        console.log("点对点应答API响应数据:", result);
        if (result.success) {
          outputFile.value = result.output_file;
          downloadUrl.value = result.download_url;
          processingStats.value = result.stats;
          generationResult.value = {
            success: true,
            outputFile: result.output_file,
            downloadUrl: result.download_url,
            stats: result.stats || {},
            message: result.message || "点对点应答生成完成"
          };
          await loadWordToEditor(result.output_file);
          ElMessage.success("点对点应答生成完成！可以编辑了");
          if (result.output_file) {
            await syncToHitl(
              form.value.projectId,
              result.output_file,
              "point_to_point"
            );
          }
        } else {
          let errorMsg = "处理失败";
          if (result.error) {
            if (typeof result.error === "object" && result.error.message) {
              errorMsg = result.error.message;
            } else if (typeof result.error === "string") {
              errorMsg = result.error;
            } else {
              errorMsg = JSON.stringify(result.error);
            }
          } else if (result.message) {
            errorMsg = result.message;
          }
          console.error("处理失败，错误信息:", errorMsg, "完整结果:", result);
          throw new Error(errorMsg);
        }
      } catch (error) {
        console.error("点对点应答处理失败:", error);
        let errorMessage = "处理失败，请重试";
        if (typeof error === "string") {
          errorMessage = error;
        } else if (error == null ? void 0 : error.message) {
          errorMessage = error.message;
        } else if (error == null ? void 0 : error.error) {
          errorMessage = error.error;
        } else if (typeof error === "object") {
          errorMessage = JSON.stringify(error);
        }
        if (editorRef.value) {
          editorRef.value.appendContent(`<p style="color: red;">❌ 错误: ${errorMessage}</p>`);
        }
        ElMessage.error({
          message: errorMessage,
          duration: 5e3
        });
      } finally {
        generating.value = false;
      }
    };
    const generateMockResponse = (req) => {
      const responses = {
        technical: `## 技术响应

我方系统完全满足该技术要求：

### 方案说明
1. 采用xxx架构设计，支持高并发访问
2. 经过压力测试，可支持xxx并发用户
3. 配置xxx服务器集群，确保系统稳定性

### 技术指标
- 并发处理能力：满足要求
- 响应时间：平均2秒以内
- 系统可用性：99.9%

### 证明材料
详见附件《技术方案书》第xx页`,
        business: `## 商务响应

我方完全接受该商务条款：

### 承诺内容
1. 严格按照要求执行
2. 提供相应的保障措施
3. 确保按时完成

### 具体安排
- 项目周期：符合要求
- 质保期：满足要求
- 验收标准：按照招标文件执行

### 服务保障
详见附件《商务应答书》第xx页`,
        qualification: `## 资质响应

我方具备该项资质要求：

### 资质证明
1. 持有xxx证书，证书编号：xxx
2. 证书有效期：xxxx年xx月至xxxx年xx月
3. 认证范围：覆盖本项目需求

### 相关业绩
- 近三年完成类似项目xx个
- 项目验收合格率100%

### 附件材料
详见附件《资质证明文件》`,
        other: `## 其他要求响应

我方承诺满足该要求：

### 具体安排
1. 制定详细计划
2. 配备专业人员
3. 提供完整文档

### 执行标准
- 严格按照招标文件要求
- 确保质量和进度

### 相关文件
详见附件相关章节`
      };
      return responses[req.category] || "我方完全响应该要求。";
    };
    const stopGeneration = () => {
      generating.value = false;
      ElMessage.info("已停止生成");
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
          console.log("[PointToPoint] Word文档已加载到编辑器");
        } else {
          throw new Error(result.error || "转换失败");
        }
      } catch (error) {
        console.error("[PointToPoint] 加载文档到编辑器失败:", error);
        editorContent.value = `
      <h1>📄 点对点应答文档</h1>
      <div style="padding: 20px; background: #FFF3E0; border-left: 4px solid #FF9800; margin: 16px 0;">
        <p><strong>⚠️ 提示：</strong>Word文档转换失败</p>
        <p>原因：${error.message}</p>
        <p>您可以：</p>
        <ul>
          <li>点击下方"查看原始生成结果"下载Word文档查看</li>
          <li>Word文档中已包含内联回复（灰色底纹标记）</li>
        </ul>
      </div>
    `;
        ElMessage.warning("Word转换HTML失败，请使用下载功能查看");
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
            document_type: "point_to_point",
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
          console.log("[PointToPoint] 编辑内容已保存:", result.output_file);
          if (result.output_file) {
            await syncToHitl(
              form.value.projectId,
              result.output_file,
              "point_to_point"
            );
          }
        } else {
          throw new Error(result.error || "保存失败");
        }
      } catch (error) {
        console.error("[PointToPoint] 保存编辑内容失败:", error);
        throw error;
      } finally {
        editorSaving.value = false;
      }
    };
    const viewResponse = (req) => {
      currentRequirement.value = req;
      responseDialogVisible.value = true;
    };
    const previewDocument = () => {
      var _a;
      if (!generationResult.value) {
        ElMessage.warning("暂无文档可预览");
        return;
      }
      if (!generationResult.value.downloadUrl) {
        ElMessage.warning("文档地址无效");
        return;
      }
      previewFileUrl.value = generationResult.value.outputFile;
      previewFileName.value = `点对点应答-${((_a = selectedProject.value) == null ? void 0 : _a.project_name) || "文档"}.docx`;
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
        const filename = `点对点应答-${((_a = selectedProject.value) == null ? void 0 : _a.project_name) || "文档"}-${Date.now()}.docx`;
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
        "point_to_point"
      );
    };
    const exportResponses = () => {
      var _a;
      const responsesText = requirements.value.filter((req) => req.response).map((req, index) => {
        return `${index + 1}. 【${getCategoryLabel(req.category)}】${req.requirement}

${req.response}

符合性：${req.compliance}

---
`;
      }).join("\n");
      const blob = new Blob([`# 点对点应答文档

${responsesText}`], {
        type: "text/plain;charset=utf-8"
      });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `点对点应答-${((_a = selectedProject.value) == null ? void 0 : _a.project_name) || "export"}-${Date.now()}.txt`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      ElMessage.success("导出成功");
    };
    const getCategoryLabel = (category) => {
      const labels = {
        technical: "技术要求",
        business: "商务要求",
        qualification: "资质要求",
        other: "其他要求"
      };
      return labels[category] || category;
    };
    const getCategoryType = (category) => {
      const types = {
        technical: "primary",
        business: "success",
        qualification: "warning",
        other: "info"
      };
      return types[category] || "";
    };
    const getPriorityType = (priority) => {
      const types = {
        "高": "danger",
        "中": "warning",
        "低": "info"
      };
      return types[priority] || "";
    };
    const getStatusLabel = (status) => {
      const labels = {
        pending: "待生成",
        generated: "已生成",
        reviewed: "已审核"
      };
      return labels[status] || status;
    };
    const getStatusType = (status) => {
      const types = {
        pending: "info",
        generated: "success",
        reviewed: "primary"
      };
      return types[status] || "";
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
    const loadFilesList = async () => {
      loadingHistory.value = true;
      try {
        const response = await fetch("/api/point-to-point/files");
        const result = await response.json();
        if (result.success) {
          historyFiles.value = result.data || [];
          ElMessage.success(`加载了 ${historyFiles.value.length} 个历史文件`);
        } else {
          throw new Error(result.error || "加载失败");
        }
      } catch (error) {
        console.error("加载历史文件失败:", error);
        ElMessage.error(error.message || "加载历史文件失败");
      } finally {
        loadingHistory.value = false;
      }
    };
    const formatFileSize = (bytes) => {
      const units = ["B", "KB", "MB", "GB"];
      let size = bytes;
      let unitIndex = 0;
      while (size >= 1024 && unitIndex < units.length - 1) {
        size /= 1024;
        unitIndex++;
      }
      return `${size.toFixed(1)} ${units[unitIndex]}`;
    };
    const formatDate = (dateStr) => {
      try {
        const date = new Date(dateStr);
        return date.toLocaleString("zh-CN", {
          year: "numeric",
          month: "2-digit",
          day: "2-digit",
          hour: "2-digit",
          minute: "2-digit"
        });
      } catch {
        return dateStr;
      }
    };
    const previewFile = (file) => {
      if (!file.file_path) {
        ElMessage.warning("无法获取文件信息");
        return;
      }
      previewFileUrl.value = file.file_path;
      previewFileName.value = file.filename;
      previewVisible.value = true;
    };
    const previewCurrentFile = () => {
      var _a;
      if (!currentP2pFile.value) return;
      previewFileUrl.value = currentP2pFile.value.outputFile;
      previewFileName.value = `点对点应答-${((_a = selectedProject.value) == null ? void 0 : _a.project_name) || "文档"}.docx`;
      previewVisible.value = true;
    };
    const downloadCurrentFile = () => {
      var _a;
      if (!currentP2pFile.value) return;
      try {
        const filename = `点对点应答-${((_a = selectedProject.value) == null ? void 0 : _a.project_name) || "文档"}-${Date.now()}.docx`;
        downloadFile(currentP2pFile.value.downloadUrl, filename);
        ElMessage.success("文档下载成功");
      } catch (error) {
        console.error("下载失败:", error);
        ElMessage.error("文档下载失败，请重试");
      }
    };
    const regenerateCurrentFile = () => {
      currentP2pFile.value = null;
      ElMessage.info('请配置参数后点击"直接生成Word文档"按钮重新生成');
    };
    const openHistoryInEditor = async () => {
      var _a;
      if (!((_a = currentP2pFile.value) == null ? void 0 : _a.outputFile)) {
        ElMessage.error("历史文件信息无效");
        return;
      }
      try {
        showEditor.value = true;
        generationResult.value = {
          success: true,
          outputFile: currentP2pFile.value.outputFile,
          downloadUrl: currentP2pFile.value.downloadUrl || "",
          stats: currentP2pFile.value.stats || {},
          message: currentP2pFile.value.message || "历史点对点应答文件"
        };
        await loadWordToEditor(currentP2pFile.value.outputFile);
        ElMessage.success("历史文件已加载到编辑器");
        setTimeout(() => {
          var _a2;
          (_a2 = document.querySelector(".editor-section")) == null ? void 0 : _a2.scrollIntoView({
            behavior: "smooth",
            block: "start"
          });
        }, 100);
      } catch (error) {
        console.error("[PointToPoint] 打开历史文件失败:", error);
        ElMessage.error("打开历史文件失败: " + error.message);
      }
    };
    watch(showAllHistory, (newVal) => {
      if (newVal.includes("history") && historyFiles.value.length === 0 && !loadingHistory.value) {
        loadFilesList();
      }
    });
    onMounted(async () => {
      await loadProjects();
      const restoredProjectId = await restoreProjectFromStore({
        onClear: () => {
          form.value.tenderFiles = [];
          requirements.value = [];
          selectedRequirements.value = [];
          currentP2pFile.value = null;
          generationResult.value = null;
          showEditor.value = false;
          editorContent.value = "";
          if (useHitlFile.value) {
            cancelHitlFile();
          }
        },
        // 文档加载完成回调：使用共享函数
        onDocumentsLoaded: handleDocumentsLoaded
      });
      if (restoredProjectId) {
        form.value.projectId = restoredProjectId;
        console.log("✅ 已从Store恢复项目:", restoredProjectId);
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
      const _component_el_radio = ElRadio;
      const _component_el_radio_group = ElRadioGroup;
      const _component_el_progress = ElProgress;
      const _component_el_tag = ElTag;
      const _component_el_alert = ElAlert;
      const _component_el_descriptions_item = ElDescriptionsItem;
      const _component_el_link = ElLink;
      const _component_el_descriptions = ElDescriptions;
      const _component_el_collapse_item = ElCollapseItem;
      const _component_el_collapse = ElCollapse;
      const _component_el_icon = ElIcon;
      const _component_el_table_column = ElTableColumn;
      const _component_el_table = ElTable;
      const _component_el_dialog = ElDialog;
      const _component_el_empty = ElEmpty;
      const _directive_loading = vLoading;
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
              _cache[17] || (_cache[17] = createBaseVNode("span", null, "Step 2: 选择技术需求文档", -1)),
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
              limit: 5,
              "max-size": 50,
              drag: "",
              "tip-text": "上传技术需求文档",
              onSuccess: handleUploadSuccess
            }, null, 8, ["modelValue"])) : createCommentVNode("", true),
            createVNode(_component_el_divider, null, {
              default: withCtx(() => [..._cache[18] || (_cache[18] = [
                createTextVNode("处理配置", -1)
              ])]),
              _: 1
            }),
            createVNode(_component_el_form, {
              model: config.value,
              "label-width": "100px",
              class: "config-form"
            }, {
              default: withCtx(() => [
                createVNode(_component_el_row, { gutter: 20 }, {
                  default: withCtx(() => [
                    createVNode(_component_el_col, { span: 12 }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, { label: "投标角色" }, {
                          default: withCtx(() => [
                            createVNode(_component_el_radio_group, {
                              modelValue: config.value.bidRole,
                              "onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => config.value.bidRole = $event)
                            }, {
                              default: withCtx(() => [
                                createVNode(_component_el_radio, { label: "primary" }, {
                                  default: withCtx(() => [..._cache[19] || (_cache[19] = [
                                    createTextVNode("应标", -1)
                                  ])]),
                                  _: 1
                                }),
                                createVNode(_component_el_radio, { label: "secondary" }, {
                                  default: withCtx(() => [..._cache[20] || (_cache[20] = [
                                    createTextVNode("陪标", -1)
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
                    createVNode(_component_el_col, { span: 12 }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, { label: "应答频率" }, {
                          default: withCtx(() => [
                            createVNode(_component_el_select, {
                              modelValue: config.value.responseFrequency,
                              "onUpdate:modelValue": _cache[4] || (_cache[4] = ($event) => config.value.responseFrequency = $event),
                              style: { "width": "100%" }
                            }, {
                              default: withCtx(() => [
                                createVNode(_component_el_option, {
                                  label: "每段应答",
                                  value: "every_paragraph"
                                }),
                                createVNode(_component_el_option, {
                                  label: "每页应答",
                                  value: "every_page"
                                }),
                                createVNode(_component_el_option, {
                                  label: "每章节应答",
                                  value: "every_section"
                                }),
                                createVNode(_component_el_option, {
                                  label: "文档末尾统一应答",
                                  value: "end_of_document"
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
                        createVNode(_component_el_form_item, { label: "应答方式" }, {
                          default: withCtx(() => [
                            createVNode(_component_el_radio_group, {
                              modelValue: config.value.responseMode,
                              "onUpdate:modelValue": _cache[5] || (_cache[5] = ($event) => config.value.responseMode = $event)
                            }, {
                              default: withCtx(() => [
                                createVNode(_component_el_radio, { label: "simple" }, {
                                  default: withCtx(() => [..._cache[21] || (_cache[21] = [
                                    createTextVNode("简单模板应答", -1)
                                  ])]),
                                  _: 1
                                }),
                                createVNode(_component_el_radio, { label: "ai" }, {
                                  default: withCtx(() => [..._cache[22] || (_cache[22] = [
                                    createTextVNode("AI智能应答", -1)
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
                    config.value.responseMode === "ai" ? (openBlock(), createBlock(_component_el_col, {
                      key: 0,
                      span: 12
                    }, {
                      default: withCtx(() => [
                        createVNode(_component_el_form_item, { label: "AI模型" }, {
                          default: withCtx(() => [
                            createVNode(_component_el_select, {
                              modelValue: config.value.aiModel,
                              "onUpdate:modelValue": _cache[6] || (_cache[6] = ($event) => config.value.aiModel = $event),
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
                    })) : createCommentVNode("", true)
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
                disabled: !canExtract.value,
                loading: extracting.value,
                onClick: extractRequirements
              }, {
                default: withCtx(() => [..._cache[23] || (_cache[23] = [
                  createTextVNode(" 提取招标要求 ", -1)
                ])]),
                _: 1
              }, 8, ["disabled", "loading"]),
              createVNode(_component_el_button, {
                type: "success",
                size: "large",
                disabled: !canExtract.value,
                loading: generating.value,
                onClick: processPointToPointDirect
              }, {
                default: withCtx(() => [..._cache[24] || (_cache[24] = [
                  createTextVNode(" 直接生成Word文档 ", -1)
                ])]),
                _: 1
              }, 8, ["disabled", "loading"])
            ])
          ]),
          _: 1
        })) : createCommentVNode("", true),
        extracting.value ? (openBlock(), createBlock(_component_el_card, {
          key: 1,
          class: "extracting-section",
          shadow: "never"
        }, {
          header: withCtx(() => [
            createBaseVNode("div", _hoisted_4, [
              _cache[25] || (_cache[25] = createBaseVNode("span", null, "正在提取招标要求...", -1)),
              createVNode(_component_el_progress, {
                percentage: extractProgress.value,
                status: extractProgress.value === 100 ? "success" : void 0,
                style: { "width": "300px" }
              }, null, 8, ["percentage", "status"])
            ])
          ]),
          default: withCtx(() => [
            createVNode(unref(SSEStreamViewer), {
              content: extractContent.value,
              "is-streaming": extracting.value
            }, null, 8, ["content", "is-streaming"])
          ]),
          _: 1
        })) : createCommentVNode("", true),
        showEditor.value ? (openBlock(), createBlock(_component_el_card, {
          key: 2,
          class: "editor-section",
          shadow: "never"
        }, {
          default: withCtx(() => [
            createVNode(unref(RichTextEditor), {
              ref_key: "editorRef",
              ref: editorRef,
              modelValue: editorContent.value,
              "onUpdate:modelValue": _cache[7] || (_cache[7] = ($event) => editorContent.value = $event),
              title: "点对点应答文档",
              streaming: generating.value,
              height: 700,
              onSave: handleEditorSave,
              onPreview: previewDocument,
              onExport: downloadDocument
            }, null, 8, ["modelValue", "streaming"])
          ]),
          _: 1
        })) : createCommentVNode("", true),
        showEditor.value && generationResult.value ? (openBlock(), createBlock(_component_el_collapse, {
          key: 3,
          modelValue: activeCollapse.value,
          "onUpdate:modelValue": _cache[8] || (_cache[8] = ($event) => activeCollapse.value = $event),
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
                      _cache[31] || (_cache[31] = createBaseVNode("span", null, "✅ 生成结果", -1)),
                      createBaseVNode("div", _hoisted_6, [
                        createVNode(_component_el_button, {
                          type: "primary",
                          size: "large",
                          icon: unref(view_default),
                          onClick: previewDocument
                        }, {
                          default: withCtx(() => [..._cache[26] || (_cache[26] = [
                            createTextVNode(" 预览文档 ", -1)
                          ])]),
                          _: 1
                        }, 8, ["icon"]),
                        createVNode(_component_el_button, {
                          type: "success",
                          size: "large",
                          icon: unref(download_default),
                          onClick: downloadDocument
                        }, {
                          default: withCtx(() => [..._cache[27] || (_cache[27] = [
                            createTextVNode(" 下载Word文档 ", -1)
                          ])]),
                          _: 1
                        }, 8, ["icon"]),
                        !unref(synced) ? (openBlock(), createBlock(_component_el_button, {
                          key: 0,
                          type: "info",
                          size: "large",
                          icon: unref(upload_default),
                          loading: unref(syncing),
                          onClick: handleSyncToHitl
                        }, {
                          default: withCtx(() => [..._cache[28] || (_cache[28] = [
                            createTextVNode(" 同步到投标项目 ", -1)
                          ])]),
                          _: 1
                        }, 8, ["icon", "loading"])) : (openBlock(), createBlock(_component_el_tag, {
                          key: 1,
                          type: "success",
                          size: "large"
                        }, {
                          default: withCtx(() => [..._cache[29] || (_cache[29] = [
                            createTextVNode(" 已同步到投标项目 ", -1)
                          ])]),
                          _: 1
                        })),
                        createVNode(_component_el_button, {
                          type: "primary",
                          size: "large",
                          icon: unref(refresh_right_default),
                          onClick: processPointToPointDirect
                        }, {
                          default: withCtx(() => [..._cache[30] || (_cache[30] = [
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
                        type: "success",
                        title: generationResult.value.message,
                        closable: false,
                        "show-icon": "",
                        style: { "margin-bottom": "20px" }
                      }, null, 8, ["title"]),
                      generationResult.value.stats && Object.keys(generationResult.value.stats).length > 0 ? (openBlock(), createBlock(unref(StatsCard), {
                        key: 0,
                        title: "处理统计",
                        stats: generationResult.value.stats
                      }, null, 8, ["stats"])) : createCommentVNode("", true),
                      createBaseVNode("div", _hoisted_8, [
                        _cache[32] || (_cache[32] = createBaseVNode("h4", null, "生成文件", -1)),
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
        requirements.value.length > 0 ? (openBlock(), createBlock(_component_el_card, {
          key: 4,
          class: "requirements-section",
          shadow: "never"
        }, {
          header: withCtx(() => [
            createBaseVNode("div", _hoisted_9, [
              createBaseVNode("span", null, "招标要求列表 (共 " + toDisplayString(requirements.value.length) + " 条)", 1),
              createBaseVNode("div", _hoisted_10, [
                createVNode(_component_el_input, {
                  modelValue: searchKeyword.value,
                  "onUpdate:modelValue": _cache[9] || (_cache[9] = ($event) => searchKeyword.value = $event),
                  placeholder: "搜索要求...",
                  clearable: "",
                  style: { "width": "200px" }
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
                }, 8, ["modelValue"]),
                createVNode(_component_el_select, {
                  modelValue: filterCategory.value,
                  "onUpdate:modelValue": _cache[10] || (_cache[10] = ($event) => filterCategory.value = $event),
                  placeholder: "筛选分类",
                  clearable: "",
                  style: { "width": "150px" }
                }, {
                  default: withCtx(() => [
                    createVNode(_component_el_option, {
                      label: "全部",
                      value: ""
                    }),
                    createVNode(_component_el_option, {
                      label: "技术要求",
                      value: "technical"
                    }),
                    createVNode(_component_el_option, {
                      label: "商务要求",
                      value: "business"
                    }),
                    createVNode(_component_el_option, {
                      label: "资质要求",
                      value: "qualification"
                    }),
                    createVNode(_component_el_option, {
                      label: "其他要求",
                      value: "other"
                    })
                  ]),
                  _: 1
                }, 8, ["modelValue"]),
                createVNode(_component_el_button, {
                  type: "primary",
                  disabled: selectedRequirements.value.length === 0,
                  loading: generating.value,
                  onClick: generateResponses
                }, {
                  default: withCtx(() => [
                    createTextVNode(" 生成应答 (" + toDisplayString(selectedRequirements.value.length) + ") ", 1)
                  ]),
                  _: 1
                }, 8, ["disabled", "loading"])
              ])
            ])
          ]),
          default: withCtx(() => [
            createVNode(_component_el_table, {
              data: filteredRequirements.value,
              border: "",
              onSelectionChange: handleSelectionChange,
              "max-height": "500"
            }, {
              default: withCtx(() => [
                createVNode(_component_el_table_column, {
                  type: "selection",
                  width: "55"
                }),
                createVNode(_component_el_table_column, {
                  type: "index",
                  label: "序号",
                  width: "60"
                }),
                createVNode(_component_el_table_column, {
                  prop: "category",
                  label: "分类",
                  width: "100"
                }, {
                  default: withCtx(({ row }) => [
                    createVNode(_component_el_tag, {
                      type: getCategoryType(row.category),
                      size: "small"
                    }, {
                      default: withCtx(() => [
                        createTextVNode(toDisplayString(getCategoryLabel(row.category)), 1)
                      ]),
                      _: 2
                    }, 1032, ["type"])
                  ]),
                  _: 1
                }),
                createVNode(_component_el_table_column, {
                  prop: "requirement",
                  label: "招标要求",
                  "min-width": "300"
                }, {
                  default: withCtx(({ row }) => [
                    createBaseVNode("div", _hoisted_11, toDisplayString(row.requirement), 1)
                  ]),
                  _: 1
                }),
                createVNode(_component_el_table_column, {
                  prop: "priority",
                  label: "优先级",
                  width: "100"
                }, {
                  default: withCtx(({ row }) => [
                    createVNode(_component_el_tag, {
                      type: getPriorityType(row.priority),
                      size: "small"
                    }, {
                      default: withCtx(() => [
                        createTextVNode(toDisplayString(row.priority), 1)
                      ]),
                      _: 2
                    }, 1032, ["type"])
                  ]),
                  _: 1
                }),
                createVNode(_component_el_table_column, {
                  prop: "status",
                  label: "应答状态",
                  width: "100"
                }, {
                  default: withCtx(({ row }) => [
                    createVNode(_component_el_tag, {
                      type: getStatusType(row.status),
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
                  label: "操作",
                  width: "100",
                  fixed: "right"
                }, {
                  default: withCtx(({ row }) => [
                    row.response ? (openBlock(), createBlock(_component_el_button, {
                      key: 0,
                      type: "primary",
                      size: "small",
                      text: "",
                      onClick: ($event) => viewResponse(row)
                    }, {
                      default: withCtx(() => [..._cache[33] || (_cache[33] = [
                        createTextVNode(" 查看 ", -1)
                      ])]),
                      _: 1
                    }, 8, ["onClick"])) : createCommentVNode("", true)
                  ]),
                  _: 1
                })
              ]),
              _: 1
            }, 8, ["data"])
          ]),
          _: 1
        })) : createCommentVNode("", true),
        generating.value ? (openBlock(), createBlock(_component_el_card, {
          key: 5,
          class: "generation-output",
          shadow: "never"
        }, {
          header: withCtx(() => [
            createBaseVNode("div", _hoisted_12, [
              _cache[34] || (_cache[34] = createBaseVNode("span", null, "AI正在生成点对点应答...", -1)),
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
        hasResponses.value ? (openBlock(), createBlock(_component_el_card, {
          key: 6,
          class: "responses-section",
          shadow: "never"
        }, {
          header: withCtx(() => [
            createBaseVNode("div", _hoisted_13, [
              _cache[36] || (_cache[36] = createBaseVNode("span", null, "点对点应答结果", -1)),
              createBaseVNode("div", _hoisted_14, [
                createVNode(_component_el_button, {
                  type: "success",
                  icon: unref(download_default),
                  onClick: exportResponses
                }, {
                  default: withCtx(() => [..._cache[35] || (_cache[35] = [
                    createTextVNode(" 导出应答文档 ", -1)
                  ])]),
                  _: 1
                }, 8, ["icon"])
              ])
            ])
          ]),
          default: withCtx(() => [
            createVNode(_component_el_collapse, {
              modelValue: activeResponses.value,
              "onUpdate:modelValue": _cache[11] || (_cache[11] = ($event) => activeResponses.value = $event),
              accordion: ""
            }, {
              default: withCtx(() => [
                (openBlock(true), createElementBlock(Fragment, null, renderList(requirements.value.filter((r) => r.response), (req) => {
                  return openBlock(), createBlock(_component_el_collapse_item, {
                    key: req.id,
                    name: req.id
                  }, {
                    title: withCtx(() => [
                      createBaseVNode("div", _hoisted_15, [
                        createVNode(_component_el_tag, {
                          type: getCategoryType(req.category),
                          size: "small"
                        }, {
                          default: withCtx(() => [
                            createTextVNode(toDisplayString(getCategoryLabel(req.category)), 1)
                          ]),
                          _: 2
                        }, 1032, ["type"]),
                        createBaseVNode("span", _hoisted_16, toDisplayString(req.requirement), 1),
                        createVNode(_component_el_tag, {
                          type: getStatusType(req.status),
                          size: "small"
                        }, {
                          default: withCtx(() => [
                            createTextVNode(toDisplayString(getStatusLabel(req.status)), 1)
                          ]),
                          _: 2
                        }, 1032, ["type"])
                      ])
                    ]),
                    default: withCtx(() => [
                      createBaseVNode("div", _hoisted_17, [
                        createBaseVNode("div", _hoisted_18, [
                          _cache[37] || (_cache[37] = createBaseVNode("h4", null, "招标要求", -1)),
                          createBaseVNode("div", _hoisted_19, toDisplayString(req.requirement), 1)
                        ]),
                        createBaseVNode("div", _hoisted_20, [
                          _cache[38] || (_cache[38] = createBaseVNode("h4", null, "我方应答", -1)),
                          createVNode(unref(SSEStreamViewer), {
                            content: req.response || "",
                            "is-streaming": false,
                            "enable-markdown": true
                          }, null, 8, ["content"])
                        ]),
                        req.compliance ? (openBlock(), createElementBlock("div", _hoisted_21, [
                          _cache[39] || (_cache[39] = createBaseVNode("h4", null, "符合性说明", -1)),
                          createVNode(_component_el_tag, {
                            type: req.compliance === "完全符合" ? "success" : "warning",
                            size: "large"
                          }, {
                            default: withCtx(() => [
                              createTextVNode(toDisplayString(req.compliance), 1)
                            ]),
                            _: 2
                          }, 1032, ["type"])
                        ])) : createCommentVNode("", true)
                      ])
                    ]),
                    _: 2
                  }, 1032, ["name"]);
                }), 128))
              ]),
              _: 1
            }, 8, ["modelValue"])
          ]),
          _: 1
        })) : createCommentVNode("", true),
        createVNode(_component_el_dialog, {
          modelValue: responseDialogVisible.value,
          "onUpdate:modelValue": _cache[12] || (_cache[12] = ($event) => responseDialogVisible.value = $event),
          title: "应答详情",
          width: "800px",
          "destroy-on-close": ""
        }, {
          default: withCtx(() => [
            currentRequirement.value ? (openBlock(), createElementBlock("div", _hoisted_22, [
              createBaseVNode("div", _hoisted_23, [
                _cache[40] || (_cache[40] = createBaseVNode("h4", null, "招标要求", -1)),
                createBaseVNode("div", _hoisted_24, toDisplayString(currentRequirement.value.requirement), 1)
              ]),
              createBaseVNode("div", _hoisted_25, [
                _cache[41] || (_cache[41] = createBaseVNode("h4", null, "我方应答", -1)),
                createVNode(unref(SSEStreamViewer), {
                  content: currentRequirement.value.response || "",
                  "is-streaming": false,
                  "enable-markdown": true
                }, null, 8, ["content"])
              ]),
              currentRequirement.value.compliance ? (openBlock(), createElementBlock("div", _hoisted_26, [
                _cache[42] || (_cache[42] = createBaseVNode("h4", null, "符合性", -1)),
                createVNode(_component_el_tag, {
                  type: currentRequirement.value.compliance === "完全符合" ? "success" : "warning"
                }, {
                  default: withCtx(() => [
                    createTextVNode(toDisplayString(currentRequirement.value.compliance), 1)
                  ]),
                  _: 1
                }, 8, ["type"])
              ])) : createCommentVNode("", true)
            ])) : createCommentVNode("", true)
          ]),
          _: 1
        }, 8, ["modelValue"]),
        currentP2pFile.value && !showEditor.value ? (openBlock(), createBlock(unref(HistoryFilesPanel), {
          key: 7,
          title: "📄 该项目已有点对点应答文件",
          "current-file": currentP2pFile.value,
          "history-files": [],
          "show-editor-open": true,
          "show-stats": true,
          "current-file-message": "检测到该项目的历史点对点应答文件",
          onOpenInEditor: openHistoryInEditor,
          onPreview: previewCurrentFile,
          onDownload: downloadCurrentFile,
          onRegenerate: regenerateCurrentFile
        }, null, 8, ["current-file"])) : createCommentVNode("", true),
        createVNode(_component_el_collapse, {
          modelValue: showAllHistory.value,
          "onUpdate:modelValue": _cache[13] || (_cache[13] = ($event) => showAllHistory.value = $event),
          class: "history-collapse"
        }, {
          default: withCtx(() => [
            createVNode(_component_el_collapse_item, { name: "history" }, {
              title: withCtx(() => [
                createBaseVNode("div", _hoisted_27, [
                  createBaseVNode("span", null, "📂 查看所有历史处理文件 (" + toDisplayString(historyFiles.value.length) + ")", 1),
                  showAllHistory.value ? (openBlock(), createBlock(_component_el_button, {
                    key: 0,
                    type: "primary",
                    size: "small",
                    loading: loadingHistory.value,
                    onClick: withModifiers(loadFilesList, ["stop"]),
                    style: { "margin-left": "16px" }
                  }, {
                    default: withCtx(() => [..._cache[43] || (_cache[43] = [
                      createTextVNode(" 刷新列表 ", -1)
                    ])]),
                    _: 1
                  }, 8, ["loading"])) : createCommentVNode("", true)
                ])
              ]),
              default: withCtx(() => [
                createVNode(_component_el_card, {
                  shadow: "never",
                  style: { "border": "none" }
                }, {
                  default: withCtx(() => [
                    withDirectives((openBlock(), createBlock(_component_el_table, {
                      data: historyFiles.value,
                      border: "",
                      stripe: "",
                      "max-height": "400"
                    }, {
                      default: withCtx(() => [
                        createVNode(_component_el_table_column, {
                          type: "index",
                          label: "序号",
                          width: "60"
                        }),
                        createVNode(_component_el_table_column, {
                          prop: "filename",
                          label: "文件名",
                          "min-width": "300"
                        }, {
                          default: withCtx(({ row }) => [
                            createBaseVNode("div", _hoisted_28, [
                              createVNode(_component_el_icon, null, {
                                default: withCtx(() => [
                                  createVNode(unref(document_default))
                                ]),
                                _: 1
                              }),
                              createBaseVNode("span", null, toDisplayString(row.filename), 1)
                            ])
                          ]),
                          _: 1
                        }),
                        createVNode(_component_el_table_column, {
                          prop: "size",
                          label: "文件大小",
                          width: "120"
                        }, {
                          default: withCtx(({ row }) => [
                            createTextVNode(toDisplayString(formatFileSize(row.size)), 1)
                          ]),
                          _: 1
                        }),
                        createVNode(_component_el_table_column, {
                          prop: "process_time",
                          label: "处理时间",
                          width: "180"
                        }, {
                          default: withCtx(({ row }) => [
                            createTextVNode(toDisplayString(formatDate(row.process_time)), 1)
                          ]),
                          _: 1
                        }),
                        createVNode(_component_el_table_column, {
                          label: "操作",
                          width: "200",
                          fixed: "right"
                        }, {
                          default: withCtx(({ row }) => [
                            createVNode(_component_el_button, {
                              type: "primary",
                              size: "small",
                              onClick: ($event) => previewFile(row)
                            }, {
                              default: withCtx(() => [..._cache[44] || (_cache[44] = [
                                createTextVNode(" 预览 ", -1)
                              ])]),
                              _: 1
                            }, 8, ["onClick"]),
                            createVNode(_component_el_button, {
                              type: "success",
                              size: "small",
                              onClick: ($event) => unref(downloadFile)(row)
                            }, {
                              default: withCtx(() => [..._cache[45] || (_cache[45] = [
                                createTextVNode(" 下载 ", -1)
                              ])]),
                              _: 1
                            }, 8, ["onClick"])
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }, 8, ["data"])), [
                      [_directive_loading, loadingHistory.value]
                    ]),
                    !loadingHistory.value && historyFiles.value.length === 0 ? (openBlock(), createBlock(_component_el_empty, {
                      key: 0,
                      description: "暂无历史文件",
                      "image-size": 100
                    })) : createCommentVNode("", true)
                  ]),
                  _: 1
                })
              ]),
              _: 1
            })
          ]),
          _: 1
        }, 8, ["modelValue"]),
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
const PointToPoint = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-22a375e3"]]);
export {
  PointToPoint as default
};
