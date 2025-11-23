import { r as ref, c as computed, A as ElMessage, ao as dayjs, d as defineComponent, e as createElementBlock, o as openBlock, l as createCommentVNode, f as createVNode, t as toDisplayString, w as withCtx, F as Fragment, V as renderList, ak as ElRow, k as createBlock, ai as ElCol, n as createBaseVNode, aj as ElStatistic, aW as createSlots, ad as ElIcon, h as unref, ae as document_default, X as ElTag, p as createTextVNode, aM as renderSlot, m as ElAlert, g as ElButton, aX as close_default, as as ElCard, ay as ElDescriptions, az as ElDescriptionsItem, Q as ElLink, aY as edit_default, aD as view_default, aE as download_default, aG as refresh_right_default, aH as ElCollapse, aC as ElCollapseItem, aa as withDirectives, al as ElTable, am as ElTableColumn, aJ as vLoading, ar as ElEmpty, R as withModifiers } from "./vendor-_9UVkM6-.js";
/* empty css                                                                           */
import { _ as _export_sfc } from "./index.js";
function useHitlIntegration(options = {}) {
  const { onFileLoaded, onFileCancelled, onSyncSuccess } = options;
  const useHitlFile = ref(false);
  const hitlFileInfo = ref(null);
  const syncing = ref(false);
  const synced = ref(false);
  const hasHitlFile = computed(() => !!hitlFileInfo.value);
  const loadFromHITL = (docs, fileKey = "technicalFile") => {
    const file = docs[fileKey];
    if (!file) {
      ElMessage.warning(`当前项目没有${getFileTypeLabel(fileKey)}`);
      return false;
    }
    hitlFileInfo.value = {
      filename: file.filename || file.name || "未知文件",
      file_path: file.file_path || file.url || "",
      file_size: file.file_size || file.size,
      file_url: file.file_url || file.url
    };
    useHitlFile.value = true;
    synced.value = false;
    ElMessage.success({
      message: `已加载HITL${getFileTypeLabel(fileKey)}: ${hitlFileInfo.value.filename}`,
      duration: 3e3
    });
    if (onFileLoaded) {
      onFileLoaded(hitlFileInfo.value);
    }
    return true;
  };
  const cancelHitlFile = () => {
    useHitlFile.value = false;
    hitlFileInfo.value = null;
    synced.value = false;
    ElMessage.info("已取消使用HITL文件");
    if (onFileCancelled) {
      onFileCancelled();
    }
  };
  const syncToHitl = async (projectId, outputFilePath, fileType) => {
    if (!projectId) {
      ElMessage.error("项目ID无效");
      return false;
    }
    if (!outputFilePath) {
      ElMessage.error("文件路径无效");
      return false;
    }
    syncing.value = true;
    try {
      const response = await fetch(
        `/api/tender-processing/sync-file/${projectId}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            file_path: outputFilePath,
            file_type: fileType
          })
        }
      );
      const contentType = response.headers.get("content-type");
      if (!(contentType == null ? void 0 : contentType.includes("application/json"))) {
        const text = await response.text();
        console.error("同步API返回非JSON响应:", {
          status: response.status,
          statusText: response.statusText,
          contentType,
          responsePreview: text.substring(0, 200)
        });
        throw new Error(
          `服务器返回异常响应 (${response.status}): ${response.statusText}。可能是后端配置问题，请联系管理员。`
        );
      }
      const result = await response.json();
      if (result.success || response.ok) {
        synced.value = true;
        ElMessage.success({
          message: result.message || "已成功同步到投标项目",
          duration: 3e3
        });
        if (onSyncSuccess) {
          await onSyncSuccess();
        }
        return true;
      } else {
        throw new Error(result.error || result.message || "同步失败");
      }
    } catch (error) {
      console.error("同步到项目失败:", error);
      let errorMessage = "同步到项目失败";
      if (error.message) {
        errorMessage = error.message;
      } else if (error.name === "TypeError") {
        errorMessage = "网络请求失败，请检查网络连接";
      }
      ElMessage.error({
        message: errorMessage,
        duration: 5e3
      });
      return false;
    } finally {
      syncing.value = false;
    }
  };
  const resetSyncStatus = () => {
    synced.value = false;
  };
  const getFileTypeLabel = (fileKey) => {
    const labels = {
      technicalFile: "技术需求文件",
      tenderFile: "招标文档",
      templateFile: "应答模板",
      businessResponseFile: "商务应答文件",
      p2pResponseFile: "点对点应答文件",
      techProposalFile: "技术方案文件"
    };
    return labels[fileKey] || "文件";
  };
  return {
    // 状态
    useHitlFile,
    hitlFileInfo,
    hasHitlFile,
    syncing,
    synced,
    // 方法
    loadFromHITL,
    cancelHitlFile,
    syncToHitl,
    resetSyncStatus
  };
}
function formatDate(date, format = "YYYY-MM-DD") {
  if (!date) return "";
  return dayjs(date).format(format);
}
function formatFileSize(bytes, decimals = 2) {
  if (bytes === null || bytes === void 0 || bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB", "TB", "PB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${(bytes / Math.pow(k, i)).toFixed(decimals)} ${sizes[i]}`;
}
const _hoisted_1$2 = { class: "stats-card" };
const _hoisted_2$2 = {
  key: 0,
  class: "stats-title"
};
const _hoisted_3$2 = { class: "stat-item" };
const _hoisted_4$2 = { class: "stat-prefix" };
const _hoisted_5$2 = { class: "stat-suffix" };
const _sfc_main$2 = /* @__PURE__ */ defineComponent({
  __name: "StatsCard",
  props: {
    title: {},
    stats: {},
    statItems: {},
    span: { default: 6 },
    gutter: { default: 20 },
    valueStyle: { default: () => ({}) }
  },
  setup(__props) {
    const props = __props;
    const defaultStatItems = [
      { key: "total_replacements", label: "文本替换", suffix: "处" },
      { key: "tables_processed", label: "表格处理", suffix: "个" },
      { key: "cells_filled", label: "单元格填充", suffix: "个" },
      { key: "images_inserted", label: "图片插入", suffix: "张" }
    ];
    const statItems = computed(() => {
      return props.statItems || defaultStatItems;
    });
    const getStatValue = (key) => {
      const keys = key.split(".");
      let value = props.stats;
      for (const k of keys) {
        value = value == null ? void 0 : value[k];
        if (value === void 0 || value === null) break;
      }
      return typeof value === "number" ? value : 0;
    };
    return (_ctx, _cache) => {
      const _component_el_statistic = ElStatistic;
      const _component_el_col = ElCol;
      const _component_el_row = ElRow;
      return openBlock(), createElementBlock("div", _hoisted_1$2, [
        __props.title ? (openBlock(), createElementBlock("h4", _hoisted_2$2, toDisplayString(__props.title), 1)) : createCommentVNode("", true),
        createVNode(_component_el_row, { gutter: __props.gutter }, {
          default: withCtx(() => [
            (openBlock(true), createElementBlock(Fragment, null, renderList(statItems.value, (stat) => {
              return openBlock(), createBlock(_component_el_col, {
                key: stat.key,
                span: __props.span
              }, {
                default: withCtx(() => [
                  createBaseVNode("div", _hoisted_3$2, [
                    createVNode(_component_el_statistic, {
                      title: stat.label,
                      value: getStatValue(stat.key),
                      precision: stat.precision,
                      "value-style": __props.valueStyle
                    }, createSlots({ _: 2 }, [
                      stat.prefix ? {
                        name: "prefix",
                        fn: withCtx(() => [
                          createBaseVNode("span", _hoisted_4$2, toDisplayString(stat.prefix), 1)
                        ]),
                        key: "0"
                      } : void 0,
                      stat.suffix ? {
                        name: "suffix",
                        fn: withCtx(() => [
                          createBaseVNode("span", _hoisted_5$2, toDisplayString(stat.suffix), 1)
                        ]),
                        key: "1"
                      } : void 0
                    ]), 1032, ["title", "value", "precision", "value-style"])
                  ])
                ]),
                _: 2
              }, 1032, ["span"]);
            }), 128))
          ]),
          _: 1
        }, 8, ["gutter"])
      ]);
    };
  }
});
const StatsCard = /* @__PURE__ */ _export_sfc(_sfc_main$2, [["__scopeId", "data-v-a61794d1"]]);
const _hoisted_1$1 = { class: "alert-content" };
const _hoisted_2$1 = { class: "file-info" };
const _hoisted_3$1 = { class: "file-details" };
const _hoisted_4$1 = { class: "file-label" };
const _hoisted_5$1 = { class: "file-name" };
const _hoisted_6$1 = {
  key: 0,
  class: "file-size"
};
const _hoisted_7$1 = { class: "alert-actions" };
const _sfc_main$1 = /* @__PURE__ */ defineComponent({
  __name: "HitlFileAlert",
  props: {
    fileInfo: {},
    type: { default: "success" },
    label: { default: "使用HITL文件:" },
    showCancel: { type: Boolean, default: true },
    cancelText: { default: "取消使用" },
    showTag: { type: Boolean, default: true }
  },
  emits: ["cancel"],
  setup(__props, { emit: __emit }) {
    const emit = __emit;
    const handleCancel = () => {
      emit("cancel");
    };
    return (_ctx, _cache) => {
      const _component_el_icon = ElIcon;
      const _component_el_tag = ElTag;
      const _component_el_button = ElButton;
      const _component_el_alert = ElAlert;
      return __props.fileInfo ? (openBlock(), createBlock(_component_el_alert, {
        key: 0,
        type: __props.type,
        closable: false,
        class: "hitl-file-alert"
      }, {
        title: withCtx(() => [
          createBaseVNode("div", _hoisted_1$1, [
            createBaseVNode("div", _hoisted_2$1, [
              createVNode(_component_el_icon, { class: "file-icon" }, {
                default: withCtx(() => [
                  createVNode(unref(document_default))
                ]),
                _: 1
              }),
              createBaseVNode("div", _hoisted_3$1, [
                createBaseVNode("span", _hoisted_4$1, toDisplayString(__props.label), 1),
                createBaseVNode("span", _hoisted_5$1, toDisplayString(__props.fileInfo.filename), 1),
                __props.fileInfo.file_size ? (openBlock(), createElementBlock("span", _hoisted_6$1, " (" + toDisplayString(unref(formatFileSize)(__props.fileInfo.file_size)) + ") ", 1)) : createCommentVNode("", true),
                __props.showTag ? (openBlock(), createBlock(_component_el_tag, {
                  key: 1,
                  type: "success",
                  size: "small",
                  class: "hitl-tag"
                }, {
                  default: withCtx(() => [..._cache[0] || (_cache[0] = [
                    createTextVNode(" 已从投标项目加载 ", -1)
                  ])]),
                  _: 1
                })) : createCommentVNode("", true)
              ])
            ]),
            createBaseVNode("div", _hoisted_7$1, [
              renderSlot(_ctx.$slots, "actions", {}, () => [
                __props.showCancel ? (openBlock(), createBlock(_component_el_button, {
                  key: 0,
                  type: "text",
                  size: "small",
                  onClick: handleCancel
                }, {
                  default: withCtx(() => [
                    createVNode(_component_el_icon, null, {
                      default: withCtx(() => [
                        createVNode(unref(close_default))
                      ]),
                      _: 1
                    }),
                    createTextVNode(" " + toDisplayString(__props.cancelText), 1)
                  ]),
                  _: 1
                })) : createCommentVNode("", true)
              ], true)
            ])
          ])
        ]),
        _: 3
      }, 8, ["type"])) : createCommentVNode("", true);
    };
  }
});
const HitlFileAlert = /* @__PURE__ */ _export_sfc(_sfc_main$1, [["__scopeId", "data-v-1a132715"]]);
const _hoisted_1 = { class: "history-files-panel" };
const _hoisted_2 = { class: "card-header" };
const _hoisted_3 = { class: "header-title" };
const _hoisted_4 = { class: "current-file-content" };
const _hoisted_5 = { class: "history-actions" };
const _hoisted_6 = { class: "collapse-header" };
const _hoisted_7 = { class: "filename-cell" };
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "HistoryFilesPanel",
  props: {
    title: { default: "" },
    currentFile: {},
    historyFiles: {},
    loading: { type: Boolean, default: false },
    showRegenerate: { type: Boolean, default: true },
    showStats: { type: Boolean, default: true },
    statItems: {},
    currentFileMessage: { default: "该项目已有生成文件" },
    showEditorOpen: { type: Boolean, default: false }
  },
  emits: ["openInEditor", "preview", "download", "regenerate", "refresh"],
  setup(__props) {
    const activeNames = ref([]);
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
    return (_ctx, _cache) => {
      const _component_el_tag = ElTag;
      const _component_el_alert = ElAlert;
      const _component_el_descriptions_item = ElDescriptionsItem;
      const _component_el_link = ElLink;
      const _component_el_descriptions = ElDescriptions;
      const _component_el_icon = ElIcon;
      const _component_el_button = ElButton;
      const _component_el_card = ElCard;
      const _component_el_table_column = ElTableColumn;
      const _component_el_table = ElTable;
      const _component_el_empty = ElEmpty;
      const _component_el_collapse_item = ElCollapseItem;
      const _component_el_collapse = ElCollapse;
      const _directive_loading = vLoading;
      return openBlock(), createElementBlock("div", _hoisted_1, [
        __props.currentFile ? (openBlock(), createBlock(_component_el_card, {
          key: 0,
          shadow: "never",
          class: "current-file-card"
        }, {
          header: withCtx(() => [
            createBaseVNode("div", _hoisted_2, [
              createBaseVNode("div", _hoisted_3, [
                createBaseVNode("span", null, toDisplayString(__props.title || "📄 该项目的生成文件"), 1),
                createVNode(_component_el_tag, { type: "info" }, {
                  default: withCtx(() => [..._cache[6] || (_cache[6] = [
                    createTextVNode("历史文件", -1)
                  ])]),
                  _: 1
                })
              ])
            ])
          ]),
          default: withCtx(() => [
            createBaseVNode("div", _hoisted_4, [
              createVNode(_component_el_alert, {
                type: "info",
                title: __props.currentFile.message || __props.currentFileMessage,
                closable: false,
                "show-icon": "",
                style: { "margin-bottom": "20px" }
              }, null, 8, ["title"]),
              __props.currentFile.stats && __props.showStats ? (openBlock(), createBlock(StatsCard, {
                key: 0,
                stats: __props.currentFile.stats,
                "stat-items": __props.statItems
              }, null, 8, ["stats", "stat-items"])) : createCommentVNode("", true),
              createVNode(_component_el_descriptions, {
                column: 2,
                border: "",
                style: { "margin-bottom": "20px" }
              }, {
                default: withCtx(() => [
                  createVNode(_component_el_descriptions_item, { label: "文件名" }, {
                    default: withCtx(() => [
                      createTextVNode(toDisplayString(getFileName(__props.currentFile.outputFile || __props.currentFile.file_path)), 1)
                    ]),
                    _: 1
                  }),
                  createVNode(_component_el_descriptions_item, { label: "下载地址" }, {
                    default: withCtx(() => [
                      createVNode(_component_el_link, {
                        href: __props.currentFile.downloadUrl,
                        type: "primary"
                      }, {
                        default: withCtx(() => [
                          createTextVNode(toDisplayString(getFileName(__props.currentFile.downloadUrl)), 1)
                        ]),
                        _: 1
                      }, 8, ["href"])
                    ]),
                    _: 1
                  })
                ]),
                _: 1
              }),
              createBaseVNode("div", _hoisted_5, [
                __props.showEditorOpen ? (openBlock(), createBlock(_component_el_button, {
                  key: 0,
                  type: "primary",
                  size: "large",
                  onClick: _cache[0] || (_cache[0] = ($event) => _ctx.$emit("openInEditor", __props.currentFile))
                }, {
                  default: withCtx(() => [
                    createVNode(_component_el_icon, null, {
                      default: withCtx(() => [
                        createVNode(unref(edit_default))
                      ]),
                      _: 1
                    }),
                    _cache[7] || (_cache[7] = createTextVNode(" 在编辑器中打开 ", -1))
                  ]),
                  _: 1
                })) : createCommentVNode("", true),
                createVNode(_component_el_button, {
                  type: "primary",
                  size: "large",
                  icon: unref(view_default),
                  onClick: _cache[1] || (_cache[1] = ($event) => _ctx.$emit("preview", __props.currentFile))
                }, {
                  default: withCtx(() => [..._cache[8] || (_cache[8] = [
                    createTextVNode(" 预览Word ", -1)
                  ])]),
                  _: 1
                }, 8, ["icon"]),
                createVNode(_component_el_button, {
                  type: "success",
                  size: "large",
                  icon: unref(download_default),
                  onClick: _cache[2] || (_cache[2] = ($event) => _ctx.$emit("download", __props.currentFile))
                }, {
                  default: withCtx(() => [..._cache[9] || (_cache[9] = [
                    createTextVNode(" 下载 ", -1)
                  ])]),
                  _: 1
                }, 8, ["icon"]),
                __props.showRegenerate ? (openBlock(), createBlock(_component_el_button, {
                  key: 1,
                  size: "large",
                  icon: unref(refresh_right_default),
                  onClick: _cache[3] || (_cache[3] = ($event) => _ctx.$emit("regenerate"))
                }, {
                  default: withCtx(() => [..._cache[10] || (_cache[10] = [
                    createTextVNode(" 重新生成 ", -1)
                  ])]),
                  _: 1
                }, 8, ["icon"])) : createCommentVNode("", true)
              ])
            ])
          ]),
          _: 1
        })) : createCommentVNode("", true),
        __props.historyFiles.length > 0 ? (openBlock(), createBlock(_component_el_collapse, {
          key: 1,
          modelValue: activeNames.value,
          "onUpdate:modelValue": _cache[5] || (_cache[5] = ($event) => activeNames.value = $event),
          class: "history-collapse"
        }, {
          default: withCtx(() => [
            createVNode(_component_el_collapse_item, { name: "history" }, {
              title: withCtx(() => [
                createBaseVNode("div", _hoisted_6, [
                  createBaseVNode("span", null, "📂 查看所有历史处理文件 (" + toDisplayString(__props.historyFiles.length) + ")", 1),
                  activeNames.value.includes("history") ? (openBlock(), createBlock(_component_el_button, {
                    key: 0,
                    type: "primary",
                    size: "small",
                    loading: __props.loading,
                    onClick: _cache[4] || (_cache[4] = withModifiers(($event) => _ctx.$emit("refresh"), ["stop"])),
                    style: { "margin-left": "16px" }
                  }, {
                    default: withCtx(() => [..._cache[11] || (_cache[11] = [
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
                      data: __props.historyFiles,
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
                            createBaseVNode("div", _hoisted_7, [
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
                            createTextVNode(toDisplayString(unref(formatFileSize)(row.size)), 1)
                          ]),
                          _: 1
                        }),
                        createVNode(_component_el_table_column, {
                          prop: "process_time",
                          label: "处理时间",
                          width: "180"
                        }, {
                          default: withCtx(({ row }) => [
                            createTextVNode(toDisplayString(unref(formatDate)(row.process_time || row.generated_at, "YYYY-MM-DD HH:mm:ss")), 1)
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
                              onClick: ($event) => _ctx.$emit("preview", row)
                            }, {
                              default: withCtx(() => [..._cache[12] || (_cache[12] = [
                                createTextVNode(" 预览 ", -1)
                              ])]),
                              _: 1
                            }, 8, ["onClick"]),
                            createVNode(_component_el_button, {
                              type: "success",
                              size: "small",
                              onClick: ($event) => _ctx.$emit("download", row)
                            }, {
                              default: withCtx(() => [..._cache[13] || (_cache[13] = [
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
                      [_directive_loading, __props.loading]
                    ]),
                    !__props.loading && __props.historyFiles.length === 0 ? (openBlock(), createBlock(_component_el_empty, {
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
        }, 8, ["modelValue"])) : createCommentVNode("", true)
      ]);
    };
  }
});
const HistoryFilesPanel = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-6814751e"]]);
function downloadFile(blob, filename) {
  const url = typeof blob === "string" ? blob : URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  if (typeof blob !== "string") {
    URL.revokeObjectURL(url);
  }
}
export {
  HitlFileAlert as H,
  StatsCard as S,
  HistoryFilesPanel as a,
  downloadFile as d,
  useHitlIntegration as u
};
