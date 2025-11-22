const __vite__mapDeps=(i,m=__vite__mapDeps,d=(m.f||(m.f=["js/Login-BcDiUiTp.js","js/vendor-MtO928VE.js","css/vendor-DTen-cWt.css","css/Login-BrnYA_tN.css","js/MainLayout-Dw7IXQGF.js","js/DocumentPreview-9ke4Yi2d.js","css/DocumentPreview-Cxu5QVdc.css","js/project-X4Kuz_iO.js","js/tender-DvsgeLWX.js","css/MainLayout-OsCsUsD3.css","js/Dashboard-DOroGanq.js","js/Loading-D6Ei-uTU.js","css/HistoryFilesPanel-FCsKiwJe.css","js/Empty-CMm3i0ir.js","js/Card-CPf5jQx8.js","js/IconButton-DQmoTqqH.js","css/Dashboard-dE2PG4C7.css","js/Management-DeXpa9P9.js","js/company-z4Xg082l.js","css/Management-BqLBzwk3.css","js/ManagementDetail-CFFBuBwx.js","js/PageHeader-CEpp1iB-.js","css/ManagementDetail-slmDqOXk.css","js/Response-qxMI2X6g.js","js/DocumentUploader-BFiqpCwu.js","js/imageCompressor-DC3BCfPz.js","js/RichTextEditor-Bq9eh2QZ.js","js/helpers-Bcq2sOJ4.js","js/useProjectDocuments-CobiuthK.js","css/Response-q-DKWsBz.css","js/PointToPoint-BBAKMIZw.js","js/SSEStreamViewer-CpKSZAqP.js","css/PointToPoint-DduZzVIK.css","js/TechProposal-Ber2bVbZ.js","css/TechProposal-CNNPElhd.css","js/FinalTender-ZLPoQbmN.js","css/FinalTender-DLWyttS0.css","js/Scoring-DejPqCWD.js","css/Scoring-BetcfblH.css","js/CompanyLibrary-CBhyY8A5.js","css/CompanyLibrary-Cy000kxb.css","js/CompanyDetail-y_kKR4a5.js","css/CompanyDetail-C91oNUyX.css","js/CaseLibrary-Bv21JKFy.js","js/formatters-DrGE7noj.js","css/CaseLibrary-7KBVzdqc.css","js/CaseDetail-BuenWCDb.js","css/CaseDetail-Bo6Omcks.css","js/DocumentLibrary-BYnotdIp.js","css/DocumentLibrary-DiDHUMCx.css","js/ResumeLibrary-DQNWTB6i.js","js/validators-CS_37Iha.js","css/ResumeLibrary-iMhSTnm5.css","js/ResumeDetail-GuRPzGOe.js","css/ResumeDetail-C4J8e6NP.css","js/ParserComparison-fstppZLi.js","css/ParserComparison-BxEx9boQ.css","js/EditorTest-BBKl6AOs.js","css/EditorTest-CWNntlaA.css","js/OutlineComparison-BTu3hXEf.js","css/OutlineComparison-DDvMfcQE.css","js/UserManagement-BIrKEt36.js","css/UserManagement-C4FmEDdk.css","js/Processing-CbUueBNG.js","css/Processing-CerGZiGH.css","js/Status-C1LcZmGa.js","css/Status-CaoQTMXp.css","js/Help-D6qiRU_z.js","css/Help-DWLT3G60.css","js/Forbidden-BsFtRqrc.js","css/Forbidden-BAxWUymE.css","js/NotFound-D5cNlsL6.js","css/NotFound-p6GR2JiB.css","js/ServerError-Du7H2IIt.js","css/ServerError-DeuD4iax.css"])))=>i.map(i=>d[i]);
var __defProp = Object.defineProperty;
var __defNormalProp = (obj, key, value) => key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value;
var __publicField = (obj, key, value) => __defNormalProp(obj, typeof key !== "symbol" ? key + "" : key, value);
import { a as axios, d as defineComponent, u as useRoute, r as ref, b as reactive, c as computed, e as createElementBlock, o as openBlock, f as createVNode, E as ElTooltip, w as withCtx, g as ElButton, h as unref, i as edit_pen_default, j as ElDialog, k as createBlock, l as createCommentVNode, m as ElAlert, n as createBaseVNode, p as createTextVNode, t as toDisplayString, q as ElForm, s as ElFormItem, v as ElRadioGroup, x as ElRadio, y as ElInput, z as ElMessageBox, A as ElMessage, B as resolveComponent, F as Fragment, _ as __vitePreload, C as defineStore, D as watch, G as createPinia, H as ElNotification, I as createRouter, J as createWebHashHistory, K as createApp, L as B$e } from "./vendor-MtO928VE.js";
(function polyfill() {
  const relList = document.createElement("link").relList;
  if (relList && relList.supports && relList.supports("modulepreload")) {
    return;
  }
  for (const link of document.querySelectorAll('link[rel="modulepreload"]')) {
    processPreload(link);
  }
  new MutationObserver((mutations) => {
    for (const mutation of mutations) {
      if (mutation.type !== "childList") {
        continue;
      }
      for (const node of mutation.addedNodes) {
        if (node.tagName === "LINK" && node.rel === "modulepreload")
          processPreload(node);
      }
    }
  }).observe(document, { childList: true, subtree: true });
  function getFetchOpts(link) {
    const fetchOpts = {};
    if (link.integrity) fetchOpts.integrity = link.integrity;
    if (link.referrerPolicy) fetchOpts.referrerPolicy = link.referrerPolicy;
    if (link.crossOrigin === "use-credentials")
      fetchOpts.credentials = "include";
    else if (link.crossOrigin === "anonymous") fetchOpts.credentials = "omit";
    else fetchOpts.credentials = "same-origin";
    return fetchOpts;
  }
  function processPreload(link) {
    if (link.ep)
      return;
    link.ep = true;
    const fetchOpts = getFetchOpts(link);
    fetch(link.href, fetchOpts);
  }
})();
function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
function calculateBackoffDelay(retryCount, baseDelay = 1e3) {
  return Math.min(baseDelay * Math.pow(2, retryCount), 1e4);
}
function shouldRetry(error) {
  if (!error.response) {
    return true;
  }
  const status = error.response.status;
  return status >= 500 && status < 600;
}
function setupRequestInterceptor(instance) {
  instance.interceptors.request.use(
    (config) => {
      var _a, _b;
      const method = (_a = config.method) == null ? void 0 : _a.toUpperCase();
      if (["POST", "PUT", "DELETE", "PATCH"].includes(method || "")) {
        const csrfToken = getCsrfToken();
        if (csrfToken) {
          config.headers["X-CSRFToken"] = csrfToken;
        }
      }
      if (((_b = config.method) == null ? void 0 : _b.toUpperCase()) === "GET") {
        config.params = {
          ...config.params,
          _t: Date.now()
        };
      }
      return config;
    },
    (error) => {
      console.error("[API Request Error]", error);
      return Promise.reject(error);
    }
  );
}
function setupResponseInterceptor(instance, maxRetries = 3, retryDelay = 1e3) {
  instance.interceptors.response.use(
    (response) => {
      const data = response.data;
      if (data && typeof data === "object") {
        if ("success" in data && data.success === false) {
          const error = {
            message: data.message || data.error || "请求失败",
            code: data.code || response.status,
            details: data
          };
          return Promise.reject(error);
        }
      }
      return response;
    },
    async (error) => {
      var _a, _b, _c;
      const config = error.config;
      if (!config) {
        return Promise.reject(error);
      }
      if (!config.retryConfig) {
        config.retryConfig = {
          count: 0,
          maxRetries,
          retryDelay
        };
      }
      if (config.retryConfig.count < config.retryConfig.maxRetries && shouldRetry(error)) {
        config.retryConfig.count += 1;
        const backoffDelay = calculateBackoffDelay(config.retryConfig.count, config.retryConfig.retryDelay);
        console.warn(`[API Retry] 第${config.retryConfig.count}次重试，延迟${backoffDelay}ms`, {
          url: config.url,
          method: config.method
        });
        await delay(backoffDelay);
        return instance.request(config);
      }
      console.error("[API Response Error]", {
        url: config.url,
        method: config.method,
        status: (_a = error.response) == null ? void 0 : _a.status,
        message: error.message,
        data: (_b = error.response) == null ? void 0 : _b.data
      });
      const apiError = {
        message: "请求失败",
        code: ((_c = error.response) == null ? void 0 : _c.status) || 0
      };
      if (error.response) {
        const data = error.response.data;
        if (data && typeof data === "object") {
          apiError.message = data.message || data.error || `服务器错误 (${error.response.status})`;
          apiError.code = data.code || error.response.status;
          apiError.details = data;
        } else if (typeof data === "string") {
          apiError.message = data;
        } else {
          apiError.message = `HTTP ${error.response.status}: ${error.response.statusText}`;
        }
        switch (error.response.status) {
          case 401:
            apiError.message = "未授权，请重新登录";
            break;
          case 403:
            apiError.message = (data == null ? void 0 : data.message) || "无权限访问";
            break;
          case 404:
            apiError.message = (data == null ? void 0 : data.message) || "请求的资源不存在";
            break;
          case 422:
            apiError.message = (data == null ? void 0 : data.message) || "请求参数验证失败";
            break;
          case 500:
            apiError.message = (data == null ? void 0 : data.message) || "服务器内部错误";
            break;
          case 502:
            apiError.message = "网关错误";
            break;
          case 503:
            apiError.message = "服务暂时不可用";
            break;
          case 504:
            apiError.message = "网关超时";
            break;
        }
      } else if (error.request) {
        apiError.message = "网络连接失败，请检查网络设置";
        apiError.code = 0;
      } else {
        apiError.message = error.message || "请求配置错误";
        apiError.code = -1;
      }
      return Promise.reject(apiError);
    }
  );
}
function setupInterceptors(instance, options = {}) {
  const { maxRetries = 3, retryDelay = 1e3 } = options;
  setupRequestInterceptor(instance);
  setupResponseInterceptor(instance, maxRetries, retryDelay);
}
const DEFAULT_CONFIG = {
  baseURL: "/api",
  timeout: 3e4,
  // 30秒超时
  withCredentials: true,
  // 携带cookie（CSRF token需要）
  retryCount: 3,
  // 失败重试3次
  retryDelay: 1e3
  // 重试延迟1秒
};
function getCsrfToken() {
  const match = document.cookie.match(/csrf_token=([^;]+)/);
  if (match) {
    return match[1];
  }
  const metaTag = document.querySelector('meta[name="csrf-token"]');
  if (metaTag) {
    return metaTag.getAttribute("content");
  }
  return null;
}
function createAxiosInstance(config = {}) {
  const finalConfig = { ...DEFAULT_CONFIG, ...config };
  const instance = axios.create({
    baseURL: finalConfig.baseURL,
    timeout: finalConfig.timeout,
    withCredentials: finalConfig.withCredentials,
    headers: {
      "Content-Type": "application/json"
    }
  });
  return instance;
}
class ApiClient {
  constructor(config = {}) {
    __publicField(this, "instance");
    __publicField(this, "config");
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.instance = createAxiosInstance(this.config);
    setupInterceptors(this.instance, {
      maxRetries: this.config.retryCount,
      retryDelay: this.config.retryDelay
    });
  }
  /**
   * 获取Axios实例（用于自定义请求）
   */
  getInstance() {
    return this.instance;
  }
  /**
   * GET请求
   */
  async get(url, params, config) {
    const response = await this.instance.get(url, {
      params,
      ...config
    });
    return response.data;
  }
  /**
   * POST请求
   */
  async post(url, data, config) {
    const response = await this.instance.post(url, data, config);
    return response.data;
  }
  /**
   * PUT请求
   */
  async put(url, data, config) {
    const response = await this.instance.put(url, data, config);
    return response.data;
  }
  /**
   * DELETE请求
   */
  async delete(url, config) {
    const response = await this.instance.delete(url, config);
    return response.data;
  }
  /**
   * PATCH请求
   */
  async patch(url, data, config) {
    const response = await this.instance.patch(url, data, config);
    return response.data;
  }
  /**
   * 文件上传（multipart/form-data）
   */
  async upload(url, formData, onUploadProgress) {
    const response = await this.instance.post(url, formData, {
      headers: {
        "Content-Type": "multipart/form-data"
      },
      onUploadProgress
    });
    return response.data;
  }
  /**
   * 文件下载
   */
  async download(url, filename, onDownloadProgress) {
    const response = await this.instance.get(url, {
      responseType: "blob",
      onDownloadProgress
    });
    if (filename) {
      const blob = response.data;
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = downloadUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);
    }
    return response.data;
  }
  /**
   * 设置默认请求头
   */
  setHeader(key, value) {
    this.instance.defaults.headers.common[key] = value;
  }
  /**
   * 移除默认请求头
   */
  removeHeader(key) {
    delete this.instance.defaults.headers.common[key];
  }
  /**
   * 设置Authorization token
   */
  setAuthToken(token) {
    this.setHeader("Authorization", `Bearer ${token}`);
  }
  /**
   * 清除Authorization token
   */
  clearAuthToken() {
    this.removeHeader("Authorization");
  }
}
const apiClient = new ApiClient();
function submitFeedback(data) {
  return apiClient.post("/api/feedback/submit", data);
}
const _hoisted_1 = { class: "feedback-button-wrapper" };
const _hoisted_2 = { class: "context-info" };
const _hoisted_3 = { key: 0 };
const _hoisted_4 = { key: 1 };
const _hoisted_5 = { key: 2 };
const _hoisted_6 = { key: 3 };
const _hoisted_7 = { class: "dialog-footer" };
const _sfc_main$1 = /* @__PURE__ */ defineComponent({
  __name: "FeedbackButton",
  setup(__props) {
    const route = useRoute();
    const dialogVisible = ref(false);
    const submitting = ref(false);
    const formRef = ref();
    const formData = reactive({
      content: "",
      feedbackType: "general",
      priority: "medium"
    });
    const rules = {
      content: [
        { required: true, message: "请输入问题描述", trigger: "blur" },
        { min: 10, message: "问题描述至少10个字符", trigger: "blur" }
      ],
      feedbackType: [
        { required: true, message: "请选择反馈类型", trigger: "change" }
      ],
      priority: [
        { required: true, message: "请选择优先级", trigger: "change" }
      ]
    };
    const contextInfo = computed(() => {
      var _a;
      const username = localStorage.getItem("username") || "游客";
      const pageTitle = ((_a = route.meta) == null ? void 0 : _a.title) || route.name || "未知页面";
      const pageRoute = route.path;
      const projectId = route.params.projectId ? Number(route.params.projectId) : route.query.projectId ? Number(route.query.projectId) : void 0;
      const projectName = localStorage.getItem("currentProjectName") || void 0;
      const companyName = localStorage.getItem("companyName") || void 0;
      const companyId = localStorage.getItem("companyId") ? Number(localStorage.getItem("companyId")) : void 0;
      return {
        username,
        projectId,
        projectName,
        companyId,
        companyName,
        pageRoute,
        pageTitle
      };
    });
    const showContext = computed(() => {
      return !!(contextInfo.value.username || contextInfo.value.projectName || contextInfo.value.companyName || contextInfo.value.pageTitle);
    });
    const handleClose = () => {
      if (formData.content.trim()) {
        ElMessageBox.confirm(
          "您有未提交的反馈内容，确定要关闭吗？",
          "提示",
          {
            confirmButtonText: "确定",
            cancelButtonText: "取消",
            type: "warning"
          }
        ).then(() => {
          resetForm();
          dialogVisible.value = false;
        }).catch(() => {
        });
      } else {
        resetForm();
        dialogVisible.value = false;
      }
    };
    const resetForm = () => {
      var _a;
      (_a = formRef.value) == null ? void 0 : _a.resetFields();
      formData.content = "";
      formData.feedbackType = "general";
      formData.priority = "medium";
    };
    const handleSubmit = async () => {
      var _a, _b;
      if (!formRef.value) return;
      try {
        const valid = await formRef.value.validate();
        if (!valid) return;
        submitting.value = true;
        const submitData = {
          content: formData.content,
          feedbackType: formData.feedbackType,
          priority: formData.priority,
          ...contextInfo.value
        };
        const response = await submitFeedback(submitData);
        if (response.data.success) {
          ElMessage.success(response.data.message || "反馈提交成功，感谢您的宝贵意见！");
          resetForm();
          dialogVisible.value = false;
        } else {
          ElMessage.error("提交失败，请稍后重试");
        }
      } catch (error) {
        console.error("提交反馈失败:", error);
        ElMessage.error(((_b = (_a = error.response) == null ? void 0 : _a.data) == null ? void 0 : _b.error) || "提交失败，请稍后重试");
      } finally {
        submitting.value = false;
      }
    };
    return (_ctx, _cache) => {
      const _component_el_button = ElButton;
      const _component_el_tooltip = ElTooltip;
      const _component_el_alert = ElAlert;
      const _component_el_radio = ElRadio;
      const _component_el_radio_group = ElRadioGroup;
      const _component_el_form_item = ElFormItem;
      const _component_el_input = ElInput;
      const _component_el_form = ElForm;
      const _component_el_dialog = ElDialog;
      return openBlock(), createElementBlock("div", _hoisted_1, [
        createVNode(_component_el_tooltip, {
          content: "问题登记",
          placement: "right"
        }, {
          default: withCtx(() => [
            createVNode(_component_el_button, {
              class: "feedback-floating-button",
              type: "primary",
              icon: unref(edit_pen_default),
              circle: "",
              size: "large",
              onClick: _cache[0] || (_cache[0] = ($event) => dialogVisible.value = true)
            }, null, 8, ["icon"])
          ]),
          _: 1
        }),
        createVNode(_component_el_dialog, {
          modelValue: dialogVisible.value,
          "onUpdate:modelValue": _cache[4] || (_cache[4] = ($event) => dialogVisible.value = $event),
          title: "问题登记",
          width: "600px",
          "before-close": handleClose
        }, {
          footer: withCtx(() => [
            createBaseVNode("div", _hoisted_7, [
              createVNode(_component_el_button, { onClick: handleClose }, {
                default: withCtx(() => [..._cache[15] || (_cache[15] = [
                  createTextVNode("取消", -1)
                ])]),
                _: 1
              }),
              createVNode(_component_el_button, {
                type: "primary",
                loading: submitting.value,
                onClick: handleSubmit
              }, {
                default: withCtx(() => [..._cache[16] || (_cache[16] = [
                  createTextVNode(" 提交 ", -1)
                ])]),
                _: 1
              }, 8, ["loading"])
            ])
          ]),
          default: withCtx(() => [
            showContext.value ? (openBlock(), createBlock(_component_el_alert, {
              key: 0,
              title: "以下信息将与您的反馈一起提交",
              type: "info",
              closable: false,
              class: "context-alert"
            }, {
              default: withCtx(() => [
                createBaseVNode("div", _hoisted_2, [
                  contextInfo.value.username ? (openBlock(), createElementBlock("p", _hoisted_3, [
                    _cache[5] || (_cache[5] = createBaseVNode("strong", null, "当前用户:", -1)),
                    createTextVNode(" " + toDisplayString(contextInfo.value.username), 1)
                  ])) : createCommentVNode("", true),
                  contextInfo.value.projectName ? (openBlock(), createElementBlock("p", _hoisted_4, [
                    _cache[6] || (_cache[6] = createBaseVNode("strong", null, "所属项目:", -1)),
                    createTextVNode(" " + toDisplayString(contextInfo.value.projectName), 1)
                  ])) : createCommentVNode("", true),
                  contextInfo.value.companyName ? (openBlock(), createElementBlock("p", _hoisted_5, [
                    _cache[7] || (_cache[7] = createBaseVNode("strong", null, "所属公司:", -1)),
                    createTextVNode(" " + toDisplayString(contextInfo.value.companyName), 1)
                  ])) : createCommentVNode("", true),
                  contextInfo.value.pageTitle ? (openBlock(), createElementBlock("p", _hoisted_6, [
                    _cache[8] || (_cache[8] = createBaseVNode("strong", null, "当前页面:", -1)),
                    createTextVNode(" " + toDisplayString(contextInfo.value.pageTitle), 1)
                  ])) : createCommentVNode("", true)
                ])
              ]),
              _: 1
            })) : createCommentVNode("", true),
            createVNode(_component_el_form, {
              ref_key: "formRef",
              ref: formRef,
              model: formData,
              rules,
              "label-width": "100px",
              class: "feedback-form"
            }, {
              default: withCtx(() => [
                createVNode(_component_el_form_item, {
                  label: "反馈类型",
                  prop: "feedbackType"
                }, {
                  default: withCtx(() => [
                    createVNode(_component_el_radio_group, {
                      modelValue: formData.feedbackType,
                      "onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => formData.feedbackType = $event)
                    }, {
                      default: withCtx(() => [
                        createVNode(_component_el_radio, { value: "bug" }, {
                          default: withCtx(() => [..._cache[9] || (_cache[9] = [
                            createTextVNode("Bug反馈", -1)
                          ])]),
                          _: 1
                        }),
                        createVNode(_component_el_radio, { value: "suggestion" }, {
                          default: withCtx(() => [..._cache[10] || (_cache[10] = [
                            createTextVNode("功能建议", -1)
                          ])]),
                          _: 1
                        }),
                        createVNode(_component_el_radio, { value: "general" }, {
                          default: withCtx(() => [..._cache[11] || (_cache[11] = [
                            createTextVNode("一般问题", -1)
                          ])]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }, 8, ["modelValue"])
                  ]),
                  _: 1
                }),
                createVNode(_component_el_form_item, {
                  label: "优先级",
                  prop: "priority"
                }, {
                  default: withCtx(() => [
                    createVNode(_component_el_radio_group, {
                      modelValue: formData.priority,
                      "onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => formData.priority = $event)
                    }, {
                      default: withCtx(() => [
                        createVNode(_component_el_radio, { value: "low" }, {
                          default: withCtx(() => [..._cache[12] || (_cache[12] = [
                            createTextVNode("低", -1)
                          ])]),
                          _: 1
                        }),
                        createVNode(_component_el_radio, { value: "medium" }, {
                          default: withCtx(() => [..._cache[13] || (_cache[13] = [
                            createTextVNode("中", -1)
                          ])]),
                          _: 1
                        }),
                        createVNode(_component_el_radio, { value: "high" }, {
                          default: withCtx(() => [..._cache[14] || (_cache[14] = [
                            createTextVNode("高", -1)
                          ])]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }, 8, ["modelValue"])
                  ]),
                  _: 1
                }),
                createVNode(_component_el_form_item, {
                  label: "问题描述",
                  prop: "content"
                }, {
                  default: withCtx(() => [
                    createVNode(_component_el_input, {
                      modelValue: formData.content,
                      "onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => formData.content = $event),
                      type: "textarea",
                      rows: 6,
                      placeholder: "请详细描述您遇到的问题或建议...",
                      maxlength: "2000",
                      "show-word-limit": ""
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
const _export_sfc = (sfc, props) => {
  const target = sfc.__vccOpts || sfc;
  for (const [key, val] of props) {
    target[key] = val;
  }
  return target;
};
const FeedbackButton = /* @__PURE__ */ _export_sfc(_sfc_main$1, [["__scopeId", "data-v-a5aa5b81"]]);
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "App",
  setup(__props) {
    return (_ctx, _cache) => {
      const _component_router_view = resolveComponent("router-view");
      return openBlock(), createElementBlock(Fragment, null, [
        createVNode(_component_router_view),
        createVNode(FeedbackButton)
      ], 64);
    };
  }
});
const routes = [
  // ==================== 登录页 ====================
  {
    path: "/login",
    name: "Login",
    component: () => __vitePreload(() => import("./Login-BcDiUiTp.js"), true ? __vite__mapDeps([0,1,2,3]) : void 0),
    meta: {
      requiresAuth: false,
      title: "登录",
      hideBreadcrumb: true,
      showInMenu: false
    }
  },
  // ==================== 主布局路由 ====================
  {
    path: "/",
    component: () => __vitePreload(() => import("./MainLayout-Dw7IXQGF.js"), true ? __vite__mapDeps([4,1,2,5,6,7,8,9]) : void 0),
    meta: { requiresAuth: true },
    redirect: { name: "Home" },
    children: [
      // ========== 工作台 ==========
      {
        path: "",
        name: "Home",
        component: () => __vitePreload(() => import("./Dashboard-DOroGanq.js"), true ? __vite__mapDeps([10,1,2,7,8,11,12,13,14,15,16,6]) : void 0),
        meta: {
          title: "工作台",
          icon: "bi-house",
          category: "workspace",
          order: 1,
          affix: true,
          description: "项目总览和快捷入口"
        }
      },
      // ========== 项目管理 ==========
      {
        path: "tender-management",
        name: "TenderManagement",
        component: () => __vitePreload(() => import("./Management-DeXpa9P9.js"), true ? __vite__mapDeps([17,1,2,11,12,13,14,15,8,18,19,6]) : void 0),
        meta: {
          title: "投标管理",
          icon: "bi-file-earmark-text",
          category: "project",
          order: 2,
          keepAlive: true,
          description: "HITL人机协同系统"
        }
      },
      // 项目详情页
      {
        path: "tender-management/:id",
        name: "TenderManagementDetail",
        component: () => __vitePreload(() => import("./ManagementDetail-CFFBuBwx.js"), true ? __vite__mapDeps([20,1,2,11,12,21,5,6,8,18,7,22]) : void 0),
        meta: {
          title: "项目详情",
          icon: "bi-file-earmark-text",
          parent: "TenderManagement",
          showInMenu: false,
          hideBreadcrumb: false,
          description: "查看项目详细信息和资格要求"
        }
      },
      // ========== AI核心工具 - 智能应答 ==========
      {
        path: "business-response",
        name: "BusinessResponse",
        component: () => __vitePreload(() => import("./Response-qxMI2X6g.js"), true ? __vite__mapDeps([23,1,2,24,25,12,5,6,26,27,8,18,7,28,29]) : void 0),
        meta: {
          title: "商务应答",
          icon: "bi-briefcase",
          category: "ai-tools",
          order: 3,
          description: "智能生成商务应答文档"
        }
      },
      {
        path: "point-to-point",
        name: "PointToPoint",
        component: () => __vitePreload(() => import("./PointToPoint-BBAKMIZw.js"), true ? __vite__mapDeps([30,1,2,31,12,24,25,5,6,26,27,8,28,7,32]) : void 0),
        meta: {
          title: "点对点应答",
          icon: "bi-arrow-left-right",
          category: "ai-tools",
          order: 4,
          description: "针对招标要求逐点响应"
        }
      },
      // ========== AI核心工具 - 方案生成 ==========
      {
        path: "tech-proposal",
        name: "TechProposal",
        component: () => __vitePreload(() => import("./TechProposal-Ber2bVbZ.js"), true ? __vite__mapDeps([33,1,2,31,12,24,25,5,6,26,27,8,28,7,34]) : void 0),
        meta: {
          title: "技术方案",
          icon: "bi-file-code",
          category: "ai-tools",
          order: 5,
          description: "AI生成技术方案大纲"
        }
      },
      // ========== AI核心工具 - 最终标书 ==========
      {
        path: "final-tender",
        name: "FinalTender",
        component: () => __vitePreload(() => import("./FinalTender-ZLPoQbmN.js"), true ? __vite__mapDeps([35,1,2,11,12,21,28,8,7,36,6]) : void 0),
        meta: {
          title: "最终标书",
          icon: "bi-file-earmark-zip",
          category: "ai-tools",
          order: 6,
          description: "智能整合生成最终投标文件"
        }
      },
      // ========== AI核心工具 - 智能评审 ==========
      {
        path: "tender-scoring",
        name: "TenderScoring",
        component: () => __vitePreload(() => import("./Scoring-DejPqCWD.js"), true ? __vite__mapDeps([37,1,2,31,12,8,38,6]) : void 0),
        meta: {
          title: "标书评分",
          icon: "bi-star",
          category: "ai-tools",
          order: 6,
          description: "AI辅助标书评分和风险分析"
        }
      },
      // ========== 知识中心 ==========
      {
        path: "knowledge",
        name: "Knowledge",
        redirect: { name: "CompanyLibrary" },
        meta: {
          title: "知识中心",
          icon: "bi-book",
          order: 7,
          description: "AI系统的大脑和资料库"
        },
        children: [
          // 企业库
          {
            path: "company-library",
            name: "CompanyLibrary",
            component: () => __vitePreload(() => import("./CompanyLibrary-CBhyY8A5.js"), true ? __vite__mapDeps([39,1,2,11,12,13,14,18,40,6]) : void 0),
            meta: {
              title: "企业库",
              icon: "bi-building",
              order: 1,
              parent: "Knowledge",
              keepAlive: true,
              description: "管理企业基本信息和资质证书"
            }
          },
          // 企业详情
          {
            path: "company/:id",
            name: "CompanyDetail",
            component: () => __vitePreload(() => import("./CompanyDetail-y_kKR4a5.js"), true ? __vite__mapDeps([41,1,2,11,12,18,14,24,25,42,6]) : void 0),
            meta: {
              title: "企业详情",
              icon: "bi-building",
              parent: "Knowledge",
              showInMenu: false,
              hideBreadcrumb: false,
              description: "查看和编辑企业详细信息"
            }
          },
          // 案例库
          {
            path: "case-library",
            name: "CaseLibrary",
            component: () => __vitePreload(() => import("./CaseLibrary-Bv21JKFy.js"), true ? __vite__mapDeps([43,1,2,11,12,13,14,44,18,45,6]) : void 0),
            meta: {
              title: "案例库",
              icon: "bi-archive",
              order: 2,
              parent: "Knowledge",
              keepAlive: true,
              description: "管理历史项目案例"
            }
          },
          // 案例详情
          {
            path: "case/:id",
            name: "CaseDetail",
            component: () => __vitePreload(() => import("./CaseDetail-BuenWCDb.js"), true ? __vite__mapDeps([46,1,2,11,12,44,13,25,18,47,6]) : void 0),
            meta: {
              title: "案例详情",
              icon: "bi-archive",
              parent: "Knowledge",
              showInMenu: false,
              hideBreadcrumb: false,
              description: "查看和编辑案例详细信息"
            }
          },
          // 文档库
          {
            path: "document-library",
            name: "DocumentLibrary",
            component: () => __vitePreload(() => import("./DocumentLibrary-BYnotdIp.js"), true ? __vite__mapDeps([48,1,2,13,12,14,49,6]) : void 0),
            meta: {
              title: "文档库",
              icon: "bi-folder",
              order: 3,
              parent: "Knowledge",
              keepAlive: true,
              description: "管理企业知识文档"
            }
          },
          // 简历库
          {
            path: "resume-library",
            name: "ResumeLibrary",
            component: () => __vitePreload(() => import("./ResumeLibrary-DQNWTB6i.js"), true ? __vite__mapDeps([50,1,2,11,12,13,14,44,51,52,6]) : void 0),
            meta: {
              title: "简历库",
              icon: "bi-person-badge",
              order: 4,
              parent: "Knowledge",
              keepAlive: true,
              description: "管理人员简历信息"
            }
          },
          // 简历详情
          {
            path: "resume/:id",
            name: "ResumeDetail",
            component: () => __vitePreload(() => import("./ResumeDetail-GuRPzGOe.js"), true ? __vite__mapDeps([53,1,2,11,12,44,51,13,25,54,6]) : void 0),
            meta: {
              title: "简历详情",
              icon: "bi-person-badge",
              parent: "Knowledge",
              showInMenu: false,
              hideBreadcrumb: false,
              description: "查看和编辑简历详细信息"
            }
          }
        ]
      },
      // ========== AB测试（仅admin可见） ==========
      {
        path: "abtest",
        name: "ABTest",
        redirect: { name: "ParserComparison" },
        meta: {
          title: "AB测试",
          icon: "bi-bug",
          category: "abtest",
          order: 8,
          description: "开发调试工具（仅管理员可见）"
        },
        children: [
          // 目录解析对比
          {
            path: "parser-comparison",
            name: "ParserComparison",
            component: () => __vitePreload(() => import("./ParserComparison-fstppZLi.js"), true ? __vite__mapDeps([55,1,2,14,12,56,6]) : void 0),
            meta: {
              title: "目录解析对比",
              icon: "bi-file-earmark-diff",
              order: 1,
              parent: "ABTest",
              description: "对比不同解析方法的准确率",
              requiresAuth: false
            }
          },
          // 编辑器测试
          {
            path: "editor-test",
            name: "EditorTest",
            component: () => __vitePreload(() => import("./EditorTest-BBKl6AOs.js"), true ? __vite__mapDeps([57,1,2,26,12,58,6]) : void 0),
            meta: {
              title: "编辑器测试",
              icon: "bi-pencil-square",
              order: 2,
              parent: "ABTest",
              description: "Umo Editor功能测试"
            }
          },
          // 大纲生成对比
          {
            path: "outline-comparison",
            name: "OutlineComparison",
            component: () => __vitePreload(() => import("./OutlineComparison-BTu3hXEf.js"), true ? __vite__mapDeps([59,1,2,28,8,7,5,6,18,60,12]) : void 0),
            meta: {
              title: "大纲生成对比",
              icon: "bi-diagram-3",
              order: 3,
              parent: "ABTest",
              description: "对比不同大纲生成算法的效果"
            }
          },
          // 用户管理
          {
            path: "user-management",
            name: "UserManagement",
            component: () => __vitePreload(() => import("./UserManagement-BIrKEt36.js"), true ? __vite__mapDeps([61,1,2,62]) : void 0),
            meta: {
              title: "用户管理",
              icon: "bi-people",
              order: 4,
              parent: "ABTest",
              description: "用户和角色管理"
            }
          }
        ]
      }
    ]
  },
  // ==================== 投标处理页面(独立布局) ====================
  {
    path: "/tender-processing/:projectId?",
    name: "TenderProcessing",
    component: () => __vitePreload(() => import("./Processing-CbUueBNG.js"), true ? __vite__mapDeps([63,1,2,13,12,14,64,6]) : void 0),
    meta: {
      requiresAuth: true,
      title: "投标处理",
      icon: "bi-gear",
      showInMenu: false,
      hideBreadcrumb: false,
      customClass: "tender-processing-page"
    }
  },
  // ==================== 系统页面 ====================
  {
    path: "/system-status",
    name: "SystemStatus",
    component: () => __vitePreload(() => import("./Status-C1LcZmGa.js"), true ? __vite__mapDeps([65,1,2,66]) : void 0),
    meta: {
      requiresAuth: true,
      title: "系统状态",
      icon: "bi-hdd",
      showInMenu: false
    }
  },
  {
    path: "/help",
    name: "Help",
    component: () => __vitePreload(() => import("./Help-D6qiRU_z.js"), true ? __vite__mapDeps([67,1,2,13,12,14,68,6]) : void 0),
    meta: {
      requiresAuth: false,
      title: "帮助中心",
      icon: "bi-question-circle",
      showInMenu: false
    }
  },
  // ==================== 错误页面 ====================
  {
    path: "/403",
    name: "Forbidden",
    component: () => __vitePreload(() => import("./Forbidden-BsFtRqrc.js"), true ? __vite__mapDeps([69,1,2,70]) : void 0),
    meta: {
      requiresAuth: false,
      title: "403 - 无权限访问",
      hideBreadcrumb: true,
      showInMenu: false
    }
  },
  {
    path: "/404",
    name: "NotFound",
    component: () => __vitePreload(() => import("./NotFound-D5cNlsL6.js"), true ? __vite__mapDeps([71,1,2,72]) : void 0),
    meta: {
      requiresAuth: false,
      title: "404 - 页面未找到",
      hideBreadcrumb: true,
      showInMenu: false
    }
  },
  {
    path: "/500",
    name: "ServerError",
    component: () => __vitePreload(() => import("./ServerError-Du7H2IIt.js"), true ? __vite__mapDeps([73,1,2,74]) : void 0),
    meta: {
      requiresAuth: false,
      title: "500 - 服务器错误",
      hideBreadcrumb: true,
      showInMenu: false
    }
  },
  // ==================== 捕获所有未匹配路由 ====================
  {
    path: "/:pathMatch(.*)*",
    redirect: { name: "NotFound" }
  }
];
const legacyHashRoutes = {
  "#home": "/",
  "#project-overview": "/project-overview",
  "#tender-management": "/tender-management",
  "#business-response": "/business-response",
  "#point-to-point": "/point-to-point",
  "#tech-proposal": "/tech-proposal",
  "#check-export": "/check-export",
  "#tender-scoring": "/tender-scoring",
  "#knowledge-company-library": "/knowledge/company-library",
  "#knowledge-case-library": "/knowledge/case-library",
  "#knowledge-document-library": "/knowledge/document-library",
  "#knowledge-resume-library": "/knowledge/resume-library"
};
const authApi = {
  /**
   * 用户登录
   */
  async login(data) {
    var _a;
    const response = await apiClient.post("/auth/login", data);
    if ((_a = response.data) == null ? void 0 : _a.token) {
      localStorage.setItem("auth_token", response.data.token);
      apiClient.setAuthToken(response.data.token);
    }
    return response;
  },
  /**
   * 用户登出
   */
  async logout() {
    const response = await apiClient.post("/auth/logout");
    localStorage.removeItem("auth_token");
    apiClient.clearAuthToken();
    return response;
  },
  /**
   * 获取当前用户信息
   */
  async getCurrentUser() {
    return apiClient.get("/auth/user");
  },
  /**
   * 更新当前用户信息
   */
  async updateCurrentUser(data) {
    return apiClient.put("/auth/user", data);
  },
  /**
   * 修改密码
   */
  async changePassword(data) {
    return apiClient.post("/auth/change-password", data);
  },
  /**
   * 重置密码（需要管理员权限）
   */
  async resetPassword(userId, newPassword) {
    return apiClient.post("/auth/reset-password", {
      user_id: userId,
      new_password: newPassword
    });
  },
  /**
   * 验证token有效性
   */
  async verifyToken() {
    return apiClient.get("/auth/verify-token");
  },
  /**
   * 刷新token
   */
  async refreshToken() {
    var _a;
    const response = await apiClient.post("/auth/refresh-token");
    if ((_a = response.data) == null ? void 0 : _a.token) {
      localStorage.setItem("auth_token", response.data.token);
      apiClient.setAuthToken(response.data.token);
    }
    return response;
  },
  /**
   * 从localStorage恢复认证状态
   */
  restoreAuth() {
    const token = localStorage.getItem("auth_token");
    if (token) {
      apiClient.setAuthToken(token);
    }
  }
};
setupInterceptors(apiClient.getInstance(), {
  maxRetries: 3,
  // 最大重试3次
  retryDelay: 1e3
  // 重试延迟1秒
});
const useUserStore = defineStore("user", () => {
  const currentUser = ref(null);
  const token = ref(null);
  const permissions = ref([]);
  const loading = ref(false);
  const error = ref(null);
  const isLoggedIn = computed(() => !!currentUser.value && !!token.value);
  const userId = computed(() => {
    var _a;
    return ((_a = currentUser.value) == null ? void 0 : _a.id) || null;
  });
  const username = computed(() => {
    var _a;
    return ((_a = currentUser.value) == null ? void 0 : _a.username) || "";
  });
  const userEmail = computed(() => {
    var _a;
    return ((_a = currentUser.value) == null ? void 0 : _a.email) || "";
  });
  const hasPermission = computed(() => {
    return (permission) => permissions.value.includes(permission);
  });
  const isAdmin = computed(() => {
    var _a;
    return ((_a = currentUser.value) == null ? void 0 : _a.role) === "admin" || permissions.value.includes("admin");
  });
  async function login(credentials) {
    loading.value = true;
    error.value = null;
    try {
      const response = await authApi.login(credentials);
      if (response.success && response.data) {
        currentUser.value = response.data.user;
        token.value = response.data.token || null;
        saveToStorage();
        return true;
      }
      error.value = response.message || "登录失败";
      return false;
    } catch (err) {
      error.value = err.message || "登录失败";
      return false;
    } finally {
      loading.value = false;
    }
  }
  async function logout() {
    loading.value = true;
    try {
      await authApi.logout();
    } catch (err) {
      console.error("登出请求失败:", err);
    } finally {
      currentUser.value = null;
      token.value = null;
      permissions.value = [];
      error.value = null;
      clearStorage();
      loading.value = false;
    }
  }
  async function fetchCurrentUser() {
    loading.value = true;
    error.value = null;
    try {
      const response = await authApi.getCurrentUser();
      if (response.success && response.data) {
        currentUser.value = response.data;
        saveToStorage();
      }
    } catch (err) {
      error.value = err.message || "获取用户信息失败";
      console.error("获取用户信息失败:", err);
    } finally {
      loading.value = false;
    }
  }
  async function updateUser(data) {
    loading.value = true;
    error.value = null;
    try {
      const response = await authApi.updateCurrentUser(data);
      if (response.success && response.data) {
        currentUser.value = response.data;
        saveToStorage();
        return true;
      }
      error.value = response.message || "更新失败";
      return false;
    } catch (err) {
      error.value = err.message || "更新失败";
      return false;
    } finally {
      loading.value = false;
    }
  }
  async function changePassword(oldPassword, newPassword) {
    loading.value = true;
    error.value = null;
    try {
      const response = await authApi.changePassword({
        old_password: oldPassword,
        new_password: newPassword
      });
      if (response.success) {
        return true;
      }
      error.value = response.message || "密码修改失败";
      return false;
    } catch (err) {
      error.value = err.message || "密码修改失败";
      return false;
    } finally {
      loading.value = false;
    }
  }
  async function verifyToken() {
    var _a;
    if (!token.value) {
      return false;
    }
    try {
      const response = await authApi.verifyToken();
      if (response.success && ((_a = response.data) == null ? void 0 : _a.valid)) {
        if (response.data.user) {
          currentUser.value = response.data.user;
          saveToStorage();
        }
        return true;
      }
      await logout();
      return false;
    } catch (err) {
      console.error("Token验证失败:", err);
      await logout();
      return false;
    }
  }
  async function refreshToken() {
    try {
      const response = await authApi.refreshToken();
      if (response.success && response.data) {
        token.value = response.data.token;
        if (response.data.user) {
          currentUser.value = response.data.user;
        }
        saveToStorage();
        return true;
      }
      return false;
    } catch (err) {
      console.error("Token刷新失败:", err);
      return false;
    }
  }
  function setPermissions(newPermissions) {
    permissions.value = newPermissions;
    saveToStorage();
  }
  function restoreFromStorage() {
    try {
      const savedUser = localStorage.getItem("user");
      const savedToken = localStorage.getItem("auth_token");
      const savedPermissions = localStorage.getItem("user_permissions");
      if (savedUser) {
        currentUser.value = JSON.parse(savedUser);
      }
      if (savedToken) {
        token.value = savedToken;
        authApi.restoreAuth();
      }
      if (savedPermissions) {
        permissions.value = JSON.parse(savedPermissions);
      }
    } catch (err) {
      console.error("恢复用户状态失败:", err);
    }
  }
  function saveToStorage() {
    try {
      if (currentUser.value) {
        localStorage.setItem("user", JSON.stringify(currentUser.value));
      }
      if (token.value) {
        localStorage.setItem("auth_token", token.value);
      }
      if (permissions.value.length > 0) {
        localStorage.setItem("user_permissions", JSON.stringify(permissions.value));
      }
    } catch (err) {
      console.error("保存用户状态失败:", err);
    }
  }
  function clearStorage() {
    localStorage.removeItem("user");
    localStorage.removeItem("auth_token");
    localStorage.removeItem("user_permissions");
  }
  function $reset() {
    currentUser.value = null;
    token.value = null;
    permissions.value = [];
    loading.value = false;
    error.value = null;
    clearStorage();
  }
  return {
    // State
    currentUser,
    token,
    permissions,
    loading,
    error,
    // Getters
    isLoggedIn,
    userId,
    username,
    userEmail,
    hasPermission,
    isAdmin,
    // Actions
    login,
    logout,
    fetchCurrentUser,
    updateUser,
    changePassword,
    verifyToken,
    refreshToken,
    setPermissions,
    restoreFromStorage,
    saveToStorage,
    clearStorage,
    $reset
  };
});
const useSettingsStore = defineStore("settings", () => {
  const theme = ref("light");
  const language = ref("zh-CN");
  const autoSave = ref(true);
  const showHelpTooltips = ref(true);
  const compactMode = ref(false);
  const showSidebar = ref(true);
  const showBreadcrumb = ref(true);
  const showTabs = ref(false);
  const showFooter = ref(true);
  const fixedHeader = ref(true);
  const pageTransition = ref("fade");
  const isDarkMode = computed(() => theme.value === "dark");
  const isLightMode = computed(() => theme.value === "light");
  const isChineseLanguage = computed(() => language.value === "zh-CN");
  const isEnglishLanguage = computed(() => language.value === "en-US");
  function setTheme(newTheme) {
    theme.value = newTheme;
    applyTheme();
    saveToStorage();
  }
  function toggleTheme() {
    setTheme(theme.value === "light" ? "dark" : "light");
  }
  function applyTheme() {
    const htmlElement = document.documentElement;
    if (theme.value === "dark") {
      htmlElement.classList.add("dark");
    } else {
      htmlElement.classList.remove("dark");
    }
    htmlElement.setAttribute("data-theme", theme.value);
  }
  function setLanguage(newLanguage) {
    language.value = newLanguage;
    applyLanguage();
    saveToStorage();
  }
  function applyLanguage() {
    const htmlElement = document.documentElement;
    htmlElement.setAttribute("lang", language.value);
  }
  function setAutoSave(enabled) {
    autoSave.value = enabled;
    saveToStorage();
  }
  function toggleAutoSave() {
    setAutoSave(!autoSave.value);
  }
  function setShowHelpTooltips(enabled) {
    showHelpTooltips.value = enabled;
    saveToStorage();
  }
  function toggleHelpTooltips() {
    setShowHelpTooltips(!showHelpTooltips.value);
  }
  function setCompactMode(enabled) {
    compactMode.value = enabled;
    applyCompactMode();
    saveToStorage();
  }
  function toggleCompactMode() {
    setCompactMode(!compactMode.value);
  }
  function applyCompactMode() {
    const htmlElement = document.documentElement;
    if (compactMode.value) {
      htmlElement.classList.add("compact-mode");
    } else {
      htmlElement.classList.remove("compact-mode");
    }
  }
  function setShowSidebar(show) {
    showSidebar.value = show;
    saveToStorage();
  }
  function toggleSidebar() {
    setShowSidebar(!showSidebar.value);
  }
  function setShowBreadcrumb(show) {
    showBreadcrumb.value = show;
    saveToStorage();
  }
  function setShowTabs(show) {
    showTabs.value = show;
    saveToStorage();
  }
  function setShowFooter(show) {
    showFooter.value = show;
    saveToStorage();
  }
  function setFixedHeader(fixed) {
    fixedHeader.value = fixed;
    saveToStorage();
  }
  function setPageTransition(transition) {
    pageTransition.value = transition;
    saveToStorage();
  }
  function updateSettings(settings) {
    if (settings.theme !== void 0) {
      setTheme(settings.theme);
    }
    if (settings.language !== void 0) {
      setLanguage(settings.language);
    }
    if (settings.autoSave !== void 0) {
      setAutoSave(settings.autoSave);
    }
    if (settings.showHelpTooltips !== void 0) {
      setShowHelpTooltips(settings.showHelpTooltips);
    }
    if (settings.compactMode !== void 0) {
      setCompactMode(settings.compactMode);
    }
  }
  function restoreFromStorage() {
    try {
      const savedSettings = localStorage.getItem("app_settings");
      if (savedSettings) {
        const settings = JSON.parse(savedSettings);
        theme.value = settings.theme || "light";
        language.value = settings.language || "zh-CN";
        autoSave.value = settings.autoSave !== void 0 ? settings.autoSave : true;
        showHelpTooltips.value = settings.showHelpTooltips !== void 0 ? settings.showHelpTooltips : true;
        compactMode.value = settings.compactMode || false;
        showSidebar.value = settings.showSidebar !== void 0 ? settings.showSidebar : true;
        showBreadcrumb.value = settings.showBreadcrumb !== void 0 ? settings.showBreadcrumb : true;
        showTabs.value = settings.showTabs || false;
        showFooter.value = settings.showFooter !== void 0 ? settings.showFooter : true;
        fixedHeader.value = settings.fixedHeader !== void 0 ? settings.fixedHeader : true;
        pageTransition.value = settings.pageTransition || "fade";
        applyTheme();
        applyLanguage();
        applyCompactMode();
      }
    } catch (err) {
      console.error("恢复设置失败:", err);
    }
  }
  function saveToStorage() {
    try {
      const settings = {
        theme: theme.value,
        language: language.value,
        autoSave: autoSave.value,
        showHelpTooltips: showHelpTooltips.value,
        compactMode: compactMode.value,
        // 布局配置
        showSidebar: showSidebar.value,
        showBreadcrumb: showBreadcrumb.value,
        showTabs: showTabs.value,
        showFooter: showFooter.value,
        fixedHeader: fixedHeader.value,
        pageTransition: pageTransition.value
      };
      localStorage.setItem("app_settings", JSON.stringify(settings));
    } catch (err) {
      console.error("保存设置失败:", err);
    }
  }
  function resetToDefaults() {
    theme.value = "light";
    language.value = "zh-CN";
    autoSave.value = true;
    showHelpTooltips.value = true;
    compactMode.value = false;
    showSidebar.value = true;
    showBreadcrumb.value = true;
    showTabs.value = false;
    showFooter.value = true;
    fixedHeader.value = true;
    pageTransition.value = "fade";
    applyTheme();
    applyLanguage();
    applyCompactMode();
    saveToStorage();
  }
  function $reset() {
    resetToDefaults();
  }
  watch(theme, () => {
    applyTheme();
  });
  watch(language, () => {
    applyLanguage();
  });
  watch(compactMode, () => {
    applyCompactMode();
  });
  return {
    // State
    theme,
    language,
    autoSave,
    showHelpTooltips,
    compactMode,
    showSidebar,
    showBreadcrumb,
    showTabs,
    showFooter,
    fixedHeader,
    pageTransition,
    // Getters
    isDarkMode,
    isLightMode,
    isChineseLanguage,
    isEnglishLanguage,
    // Actions
    setTheme,
    toggleTheme,
    setLanguage,
    setAutoSave,
    toggleAutoSave,
    setShowHelpTooltips,
    toggleHelpTooltips,
    setCompactMode,
    toggleCompactMode,
    setShowSidebar,
    toggleSidebar,
    setShowBreadcrumb,
    setShowTabs,
    setShowFooter,
    setFixedHeader,
    setPageTransition,
    updateSettings,
    restoreFromStorage,
    saveToStorage,
    resetToDefaults,
    $reset
  };
});
const useNotificationStore = defineStore("notification", () => {
  const notifications = ref([]);
  const maxNotifications = ref(5);
  const notificationsCount = computed(() => notifications.value.length);
  const hasNotifications = computed(() => notifications.value.length > 0);
  const unreadCount = computed(() => {
    return notifications.value.length;
  });
  const recentNotifications = computed(() => {
    return notifications.value.slice(0, maxNotifications.value);
  });
  function addNotification(type, title, message, duration) {
    const id = `notification_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const notification = {
      id,
      type,
      title,
      message,
      duration: duration || 3e3,
      timestamp: /* @__PURE__ */ new Date()
    };
    notifications.value.unshift(notification);
    if (notifications.value.length > maxNotifications.value) {
      notifications.value = notifications.value.slice(0, maxNotifications.value);
    }
    if (notification.duration && notification.duration > 0) {
      setTimeout(() => {
        removeNotification(id);
      }, notification.duration);
    }
    return id;
  }
  function success(title, message = "", duration) {
    return addNotification("success", title, message, duration);
  }
  function error(title, message = "", duration) {
    return addNotification("error", title, message, duration || 5e3);
  }
  function warning(title, message = "", duration) {
    return addNotification("warning", title, message, duration);
  }
  function info(title, message = "", duration) {
    return addNotification("info", title, message, duration);
  }
  function removeNotification(id) {
    const index = notifications.value.findIndex((n) => n.id === id);
    if (index !== -1) {
      notifications.value.splice(index, 1);
    }
  }
  function clearAll() {
    notifications.value = [];
  }
  function clearByType(type) {
    notifications.value = notifications.value.filter((n) => n.type !== type);
  }
  function setMaxNotifications(max) {
    maxNotifications.value = max;
    if (notifications.value.length > max) {
      notifications.value = notifications.value.slice(0, max);
    }
  }
  function getNotification(id) {
    return notifications.value.find((n) => n.id === id) || null;
  }
  function $reset() {
    notifications.value = [];
    maxNotifications.value = 5;
  }
  return {
    // State
    notifications,
    maxNotifications,
    // Getters
    notificationsCount,
    hasNotifications,
    unreadCount,
    recentNotifications,
    // Actions
    addNotification,
    success,
    error,
    warning,
    info,
    removeNotification,
    clearAll,
    clearByType,
    setMaxNotifications,
    getNotification,
    $reset
  };
});
createPinia();
function useNotification() {
  const notificationStore = useNotificationStore();
  function success(titleOrMessage, messageOrDuration) {
    let message;
    let duration;
    if (typeof messageOrDuration === "string") {
      message = `${titleOrMessage}: ${messageOrDuration}`;
      duration = 3e3;
    } else {
      message = titleOrMessage;
      duration = messageOrDuration || 3e3;
    }
    ElMessage.success({
      message,
      duration,
      showClose: true
    });
    notificationStore.success("操作成功", message, duration);
  }
  function error(titleOrMessage, messageOrDuration) {
    let message;
    let duration;
    if (typeof messageOrDuration === "string") {
      message = `${titleOrMessage}: ${messageOrDuration}`;
      duration = 5e3;
    } else {
      message = titleOrMessage;
      duration = messageOrDuration || 5e3;
    }
    ElMessage.error({
      message,
      duration,
      showClose: true
    });
    notificationStore.error("操作失败", message, duration);
  }
  function warning(titleOrMessage, messageOrDuration) {
    let message;
    let duration;
    if (typeof messageOrDuration === "string") {
      message = `${titleOrMessage}: ${messageOrDuration}`;
      duration = 3e3;
    } else {
      message = titleOrMessage;
      duration = messageOrDuration || 3e3;
    }
    ElMessage.warning({
      message,
      duration,
      showClose: true
    });
    notificationStore.warning("警告", message, duration);
  }
  function info(titleOrMessage, messageOrDuration) {
    let message;
    let duration;
    if (typeof messageOrDuration === "string") {
      message = `${titleOrMessage}: ${messageOrDuration}`;
      duration = 3e3;
    } else {
      message = titleOrMessage;
      duration = messageOrDuration || 3e3;
    }
    ElMessage.info({
      message,
      duration,
      showClose: true
    });
    notificationStore.info("提示", message, duration);
  }
  function notify(options) {
    ElNotification({
      title: options.title || "通知",
      message: options.message,
      type: options.type || "info",
      duration: options.duration || 4500,
      showClose: options.showClose !== false,
      dangerouslyUseHTMLString: options.dangerouslyUseHTMLString || false
    });
    const type = options.type || "info";
    notificationStore.addNotification(
      type,
      options.title || "通知",
      options.message,
      options.duration
    );
  }
  function notifySuccess(title, message) {
    notify({
      title,
      message,
      type: "success",
      duration: 4500
    });
  }
  function notifyError(title, message) {
    notify({
      title,
      message,
      type: "error",
      duration: 6e3
      // 错误通知显示更久
    });
  }
  function notifyWarning(title, message) {
    notify({
      title,
      message,
      type: "warning",
      duration: 4500
    });
  }
  function notifyInfo(title, message) {
    notify({
      title,
      message,
      type: "info",
      duration: 4500
    });
  }
  async function confirm(options) {
    try {
      await ElMessageBox.confirm(options.message, options.title || "确认", {
        confirmButtonText: options.confirmButtonText || "确定",
        cancelButtonText: options.cancelButtonText || "取消",
        type: options.type || "warning",
        distinguishCancelAndClose: true
      });
      return true;
    } catch (action) {
      return false;
    }
  }
  async function alert(message, title = "提示") {
    await ElMessageBox.alert(message, title, {
      confirmButtonText: "确定",
      type: "info"
    });
  }
  async function prompt(message, title = "输入") {
    try {
      const { value } = await ElMessageBox.prompt(message, title, {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        inputPattern: /.+/,
        inputErrorMessage: "输入不能为空"
      });
      return value || "";
    } catch {
      return "";
    }
  }
  return {
    // Message
    success,
    error,
    warning,
    info,
    // Notification
    notify,
    notifySuccess,
    notifyError,
    notifyWarning,
    notifyInfo,
    // MessageBox
    confirm,
    alert,
    prompt
  };
}
function getBreadcrumbs(route) {
  const breadcrumbs = [];
  const matched = route.matched.filter((r) => {
    var _a, _b;
    return ((_a = r.meta) == null ? void 0 : _a.title) && !((_b = r.meta) == null ? void 0 : _b.hideBreadcrumb);
  });
  matched.forEach((r, index) => {
    breadcrumbs.push({
      title: r.meta.title,
      path: index === matched.length - 1 ? void 0 : r.path,
      // 最后一项不可点击
      icon: r.meta.icon,
      disabled: index === matched.length - 1
    });
  });
  return breadcrumbs;
}
function generateMenuFromRoutes(routes2, parentPath = "") {
  const menuItems = [];
  routes2.forEach((route) => {
    var _a, _b;
    if (((_a = route.meta) == null ? void 0 : _a.showInMenu) === false) {
      return;
    }
    if (!((_b = route.meta) == null ? void 0 : _b.title)) {
      return;
    }
    const fullPath = parentPath + (route.path.startsWith("/") ? route.path : `/${route.path}`);
    const menuItem = {
      name: route.name,
      path: fullPath,
      title: route.meta.title,
      icon: route.meta.icon,
      order: route.meta.order,
      meta: route.meta,
      children: []
    };
    if (route.children && route.children.length > 0) {
      menuItem.children = generateMenuFromRoutes(route.children, fullPath);
    }
    menuItems.push(menuItem);
  });
  menuItems.sort((a, b) => (a.order || 999) - (b.order || 999));
  return menuItems;
}
function handleLegacyHashRoute(hash) {
  if (hash && legacyHashRoutes[hash]) {
    return legacyHashRoutes[hash];
  }
  return null;
}
function getPageTitle(route, defaultTitle = "元景AI智能标书生成平台") {
  var _a;
  const routeTitle = (_a = route.meta) == null ? void 0 : _a.title;
  if (routeTitle) {
    return `${routeTitle} - ${defaultTitle}`;
  }
  return defaultTitle;
}
function setupRouterGuards(router2) {
  setupBeforeEachGuard(router2);
  setupAfterEachGuard(router2);
  setupErrorHandler(router2);
}
function setupBeforeEachGuard(router2) {
  router2.beforeEach(async (to, from, next) => {
    startProgress();
    if (handleOldHashRoute(to, next)) {
      return;
    }
    const authResult = await checkAuthentication(to, from, next);
    if (!authResult) {
      stopProgress();
      return;
    }
    setPageTitle(to);
    next();
  });
}
function setupAfterEachGuard(router2) {
  router2.afterEach((to, from) => {
    stopProgress();
    logNavigation(to, from);
    emitPageViewEvent(to);
  });
}
function setupErrorHandler(router2) {
  router2.onError((error) => {
    console.error("[Router] Navigation error:", error);
    const { error: showError } = useNotification();
    stopProgress();
    if (error.message.includes("Failed to fetch dynamically imported module")) {
      showError("页面加载失败，请刷新页面重试");
    } else if (error.message.includes("Redirected when going from")) {
      showError("路由配置错误，请联系管理员");
    } else {
      showError("页面加载失败");
    }
  });
}
function startProgress() {
  const settingsStore = useSettingsStore();
  if (settingsStore.showProgress) {
    if (typeof window !== "undefined" && window.NProgress) {
      window.NProgress.start();
    }
  }
}
function stopProgress() {
  if (typeof window !== "undefined" && window.NProgress) {
    window.NProgress.done();
  }
}
function handleOldHashRoute(to, next) {
  const hash = window.location.hash;
  const newPath = handleLegacyHashRoute(hash);
  if (newPath) {
    console.log(`[Router] 重定向旧hash路由: ${hash} → ${newPath}`);
    next({ path: newPath, replace: true });
    return true;
  }
  return false;
}
async function checkAuthentication(to, from, next) {
  const userStore = useUserStore();
  if (to.meta.requiresAuth === false) {
    return true;
  }
  if (!userStore.isLoggedIn) {
    userStore.restoreFromStorage();
    if (!userStore.isLoggedIn) {
      console.warn(`[Router] 未登录，重定向到登录页: ${to.path}`);
      const { warning } = useNotification();
      warning("请先登录");
      next({
        name: "Login",
        query: { redirect: to.fullPath },
        // 记录目标页面，登录后跳转
        replace: true
      });
      return false;
    }
  }
  try {
    const isValid = await userStore.verifyToken();
    if (!isValid) {
      console.warn("[Router] Token失效，重定向到登录页");
      const { warning } = useNotification();
      warning("登录已过期，请重新登录");
      await userStore.logout();
      next({
        name: "Login",
        query: { redirect: to.fullPath },
        replace: true
      });
      return false;
    }
  } catch (error) {
    console.error("[Router] Token验证失败:", error);
    await userStore.logout();
    next({
      name: "Login",
      query: { redirect: to.fullPath },
      replace: true
    });
    return false;
  }
  return true;
}
function setPageTitle(to) {
  const title = getPageTitle(to);
  document.title = title;
  if (to.meta.description) {
    setMetaTag("description", to.meta.description);
  }
  if (to.meta.keywords && Array.isArray(to.meta.keywords)) {
    setMetaTag("keywords", to.meta.keywords.join(", "));
  }
}
function setMetaTag(name, content) {
  let metaTag = document.querySelector(`meta[name="${name}"]`);
  if (!metaTag) {
    metaTag = document.createElement("meta");
    metaTag.setAttribute("name", name);
    document.head.appendChild(metaTag);
  }
  metaTag.setAttribute("content", content);
}
function logNavigation(to, from) {
  const fromName = from.name || "unknown";
  const toName = to.name || "unknown";
  console.log(`[Router] ${String(fromName)} → ${String(toName)}`, {
    from: from.path,
    to: to.path,
    params: to.params,
    query: to.query
  });
}
function emitPageViewEvent(to) {
  if (typeof window !== "undefined") {
    window.dispatchEvent(
      new CustomEvent("pageview", {
        detail: {
          path: to.path,
          name: to.name,
          title: to.meta.title
        }
      })
    );
  }
}
const scrollBehavior = (to, from, savedPosition) => {
  if (savedPosition) {
    return savedPosition;
  }
  if (to.hash) {
    return {
      el: to.hash,
      behavior: "smooth",
      top: 80
      // 偏移导航栏高度
    };
  }
  if (to.meta.keepScrollPosition) {
    return false;
  }
  return { top: 0, behavior: "smooth" };
};
const router = createRouter({
  // 使用Hash模式（不需要服务器配置，适合静态部署）
  // ✅ Hash路由的base必须是根路径，不能使用/static/dist/
  history: createWebHashHistory("/"),
  // 路由配置
  routes,
  // 滚动行为
  scrollBehavior,
  // 严格模式(路径末尾斜杠必须匹配)
  strict: false,
  // 大小写敏感
  sensitive: false
});
setupRouterGuards(router);
async function initCsrfToken() {
  try {
    await axios.get("/api/csrf-token", { withCredentials: true });
    console.log("[CSRF] Token initialized successfully");
  } catch (error) {
    console.error("[CSRF] Failed to initialize token:", error);
  }
}
async function initApp() {
  await initCsrfToken();
  const app = createApp(_sfc_main);
  app.use(createPinia());
  app.use(router);
  try {
    app.use(B$e, {
      // 简化配置，避免循环依赖
      toolbar: {
        defaultMode: "ribbon"
      }
    });
    console.log("[App] Umo Editor v8.x 注册成功");
  } catch (error) {
    console.error("[App] Umo Editor 注册失败:", error);
  }
  app.mount("#app");
}
initApp();
export {
  _export_sfc as _,
  useNotification as a,
  useNotificationStore as b,
  getBreadcrumbs as c,
  useSettingsStore as d,
  apiClient as e,
  generateMenuFromRoutes as g,
  useUserStore as u
};
