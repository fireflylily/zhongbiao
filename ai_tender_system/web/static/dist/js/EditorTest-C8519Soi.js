import{U as O,V as W,c as j,R as N,D as U,a8 as q,a as D,Q as F,k as i}from"./element-plus-IkZgpaz4.js";/* empty css                                                                          */import{bT as I,bt as b,bU as Q,bV as k,c8 as s,b$ as w,c3 as x,c0 as l,c5 as u,bY as v,bv as L,c6 as z}from"./vendor-CdA3MjAt.js";import"./umo-editor-BmhDOXHm.js";/* empty css                                                                        */import{R as J}from"./RichTextEditor-BDdJ_J7M.js";import{_ as Y}from"./index.js";import"./onnxruntime-DkHy2lK3.js";import"./mermaid-e-fO57px.js";import"./echarts-Cqw1j_Z-.js";const G={class:"editor-test-page"},K={style:{"white-space":"pre-wrap","font-size":"12px"}},X={class:"editor-container"},Z=I({__name:"EditorTest",setup(ee){const o=b(null),y=b(""),E=b("word"),h=b(null),_=b(!1),f=b(""),S=t=>{t.raw&&(h.value=t.raw,i.success(`已选择文件: ${t.name}`))},R=async()=>{if(!h.value){i.warning("请先选择Word文档");return}_.value=!0,f.value=`正在转换Word文档...
`;try{const t=new FormData;t.append("file",h.value);const e=await fetch("/api/editor/upload-temp",{method:"POST",body:t});if(!e.ok)throw new Error("文件上传失败");const n=(await e.json()).file_path;f.value+=`✓ 文件已上传: ${n}
`,f.value+=`正在转换为HTML...
`;const a=await(await fetch("/api/editor/convert-word-to-html",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({file_path:n})})).json();if(a.success&&a.html_content){f.value+=`✓ 转换成功！HTML长度: ${a.html_content.length}
`;const d=(a.html_content.match(/page-break/g)||[]).length;f.value+=`✓ 检测到 ${d} 个分页符
`,y.value=a.html_content,o.value&&o.value.setContent(a.html_content),i.success("Word文档已加载到编辑器")}else throw new Error(a.error||"转换失败")}catch(t){f.value+=`❌ 错误: ${t.message}
`,i.error("转换失败: "+t.message)}finally{_.value=!1}},B=()=>{const t=`
<h1>第一章 项目概述</h1>
<p>这是第一章的内容。我们将在这里介绍项目的基本情况和背景。</p>
<p>项目名称：智能标书管理系统</p>
<p>项目目标：提高标书编写效率，降低人工成本。</p>

<hr data-type="page-break" />

<h1>第二章 技术方案</h1>
<p>本章介绍我们采用的技术方案和架构设计。</p>
<h2>2.1 系统架构</h2>
<p>系统采用前后端分离架构，前端使用Vue3 + TypeScript，后端使用Python Flask。</p>
<h2>2.2 技术栈</h2>
<ul>
  <li>前端：Vue3 + Element Plus + UmoEditor</li>
  <li>后端：Python Flask + SQLAlchemy</li>
  <li>数据库：SQLite / MySQL</li>
</ul>

<hr data-type="page-break" />

<h1>第三章 实施计划</h1>
<p>本章描述项目的实施计划和时间安排。</p>
<table>
  <tr>
    <th>阶段</th>
    <th>任务</th>
    <th>时间</th>
  </tr>
  <tr>
    <td>第一阶段</td>
    <td>需求分析</td>
    <td>2周</td>
  </tr>
  <tr>
    <td>第二阶段</td>
    <td>系统开发</td>
    <td>8周</td>
  </tr>
  <tr>
    <td>第三阶段</td>
    <td>测试上线</td>
    <td>2周</td>
  </tr>
</table>

<hr data-type="page-break" />

<h1>第四章 总结</h1>
<p>通过本项目的实施，将大幅提升标书编写效率。</p>
<p><strong>预期成果：</strong></p>
<ul>
  <li>标书编写时间缩短50%</li>
  <li>错误率降低80%</li>
  <li>用户满意度提升</li>
</ul>
  `;y.value=t,o.value&&o.value.setContent(t),i.success("测试内容已加载（包含3个分页符）")},P=()=>{if(!o.value){i.warning("编辑器未就绪");return}const r=o.value.getContent()+'<hr data-type="page-break" />';o.value.setContent(r),i.success("已插入分页符")},V=()=>{y.value="",o.value&&o.value.clear(),i.success("编辑器已清空")},$=()=>{const t="<p>"+"这是一个很长的段落内容。".repeat(50)+`</p>
`,e=`
<h1>第一章 项目背景</h1>
${t.repeat(30)}

<div class="umo-page-break" data-line-number="false" data-content="分页符"></div>

<h1>第二章 需求分析</h1>
${t.repeat(30)}

<div class="umo-page-break" data-line-number="false" data-content="分页符"></div>

<h1>第三章 技术方案</h1>
${t.repeat(30)}

<div class="umo-page-break" data-line-number="false" data-content="分页符"></div>

<h1>第四章 实施计划</h1>
${t.repeat(30)}

<div class="umo-page-break" data-line-number="false" data-content="分页符"></div>

<h1>第五章 总结</h1>
${t.repeat(30)}
  `;y.value=e,o.value&&o.value.setContent(e),i.success("超长文档已加载（包含原生分页符）")},A=()=>{if(!o.value){i.warning("编辑器未就绪");return}try{console.log("[EditorTest] 准备插入原生分页符...");const t=o.value.insertPageBreak();console.log("[EditorTest] insertPageBreak 返回:",t),t?(i.success("✅ 已插入原生分页符"),setTimeout(()=>{const e=o.value.getContent();console.log("[EditorTest] 当前HTML长度:",e.length);const r=e.match(/<div class="umo-page-break"[^>]*>/g);console.log("[EditorTest] 找到分页符数量:",(r==null?void 0:r.length)||0),r&&r.length>0&&console.log("[EditorTest] 分页符HTML:",r);const n=document.querySelector('[contenteditable="true"]');if(n){const c=n.querySelectorAll(".umo-page-break");console.log("[EditorTest] DOM中的分页符数量:",c.length)}},200)):i.error("插入失败，返回false")}catch(t){console.error("插入原生分页符失败:",t),i.error("插入失败: "+t.message)}},T=()=>{var e,r,n,c;if(!o.value){i.warning("编辑器未就绪");return}console.log("========== 编辑器调试信息 =========="),console.log("1. editorRef 方法:",Object.keys(o.value).filter(a=>typeof o.value[a]=="function"));let t=o.value.getEditor();if(t&&t.__v_isRef&&(console.log("2a. 检测到RefImpl，正在解包..."),t=t.value),t){if(console.log("2. 底层编辑器类型:",(e=t.constructor)==null?void 0:e.name),console.log("3. 编辑器对象:",t),console.log("4. 可用命令:",t.commands?Object.keys(t.commands):"无"),t.commands){const a=Object.keys(t.commands).filter(d=>d.toLowerCase().includes("page")||d.toLowerCase().includes("break"));console.log("5. 分页相关命令:",a)}console.log("6. 编辑器属性:",Object.keys(t)),console.log("7. 当前布局:",(c=(n=(r=t.view)==null?void 0:r.dom)==null?void 0:n.closest(".umo-editor-container"))==null?void 0:c.classList)}else console.log("2. 底层编辑器未找到");console.log("================================"),i.success("调试信息已输出到Console，请查看")},H=()=>{var t,e,r;if(!o.value){i.warning("编辑器未就绪");return}try{let n=o.value.getEditor();n&&n.__v_isRef&&(n=n.value),console.log("[EditorTest] 当前布局:",(e=(t=n.extensionStorage)==null?void 0:t.page)==null?void 0:e.layout),o.value.setLayout&&(o.value.setLayout("page"),console.log('[EditorTest] ✓ 调用了 setLayout("page")')),(r=n.extensionStorage)!=null&&r.page&&(n.extensionStorage.page.layout="page",console.log('[EditorTest] ✓ 直接设置 extensionStorage.page.layout = "page"'));const c=document.querySelector(".umo-editor-container");c&&(c.classList.add("page-layout"),c.classList.remove("continuous-layout"),console.log("[EditorTest] ✓ 添加了 page-layout 类"));const a=document.querySelectorAll('.umo-editor-container button, .umo-toolbar button, [role="button"]');console.log("[EditorTest] 工具栏按钮总数:",a.length);const d=Array.from(a).filter(p=>{const g=p.textContent||"",m=p.getAttribute("title")||"",C=p.getAttribute("aria-label")||"";return g.includes("页面")||g.includes("布局")||m.includes("页面")||m.includes("布局")||m.toLowerCase().includes("layout")||C.includes("页面")||C.includes("布局")});console.log("[EditorTest] 找到可能的布局按钮:",d.length),d.forEach((p,g)=>{console.log(`  ${g+1}. ${p.textContent||p.getAttribute("title")}`,p)}),d.length>0&&(console.log("[EditorTest] 尝试点击第一个布局按钮..."),d[0].click()),setTimeout(()=>{var g,m;console.log("[EditorTest] 300ms后布局:",(m=(g=n.extensionStorage)==null?void 0:g.page)==null?void 0:m.layout);const p=document.querySelectorAll(".umo-page, [data-page-number]");console.log("[EditorTest] 页面元素数量:",p.length)},300),i.success("已尝试强制启用分页模式，请查看Console")}catch(n){console.error("[EditorTest] 强制启用失败:",n),i.error("操作失败: "+n.message)}},M=()=>{console.log("[EditorTest] 编辑器已就绪"),setTimeout(()=>{T()},500)};return(t,e)=>{const r=j,n=U,c=N,a=D,d=W,p=O,g=F;return k(),Q("div",G,[s(g,{shadow:"never"},{header:l(()=>[...e[2]||(e[2]=[v("h2",null,"📝 编辑器 & 分页符测试",-1)])]),default:l(()=>[s(p,{modelValue:E.value,"onUpdate:modelValue":e[0]||(e[0]=m=>E.value=m),type:"card"},{default:l(()=>[s(d,{label:"Word文档测试",name:"word"},{default:l(()=>[s(r,{type:"info",closable:!1,style:{"margin-bottom":"16px"}},{default:l(()=>[...e[3]||(e[3]=[u(" 💡 上传一个包含分页符的Word文档，测试分页符是否正确显示 ",-1)])]),_:1}),s(c,{class:"upload-demo",drag:"","auto-upload":!1,limit:1,accept:".doc,.docx","on-change":S},{tip:l(()=>[...e[4]||(e[4]=[v("div",{class:"el-upload__tip"}," 仅支持 .doc / .docx 格式文件 ",-1)])]),default:l(()=>[s(n,{class:"el-icon--upload"},{default:l(()=>[s(L(q))]),_:1}),e[5]||(e[5]=v("div",{class:"el-upload__text"},[u(" 拖拽Word文档到此处或 "),v("em",null,"点击上传")],-1))]),_:1}),h.value?(k(),w(a,{key:0,type:"primary",loading:_.value,onClick:R,style:{"margin-top":"16px"}},{default:l(()=>[...e[6]||(e[6]=[u(" 转换并加载到编辑器 ",-1)])]),_:1},8,["loading"])):x("",!0)]),_:1}),s(d,{label:"手动分页符测试",name:"manual"},{default:l(()=>[s(r,{type:"info",closable:!1,style:{"margin-bottom":"16px"}},{default:l(()=>[...e[7]||(e[7]=[u(" 💡 点击下方按钮加载包含分页符的测试内容 ",-1)])]),_:1}),s(a,{type:"primary",onClick:B},{default:l(()=>[...e[8]||(e[8]=[u(" 加载测试内容（带分页符） ",-1)])]),_:1}),s(a,{onClick:P,disabled:!o.value},{default:l(()=>[...e[9]||(e[9]=[u(" 插入HR分页符 ",-1)])]),_:1},8,["disabled"]),s(a,{onClick:A,disabled:!o.value,type:"success"},{default:l(()=>[...e[10]||(e[10]=[u(" 插入原生分页符（实验） ",-1)])]),_:1},8,["disabled"]),s(a,{onClick:T,disabled:!o.value,type:"warning"},{default:l(()=>[...e[11]||(e[11]=[u(" 调试编辑器API ",-1)])]),_:1},8,["disabled"]),s(a,{onClick:H,disabled:!o.value,type:"danger"},{default:l(()=>[...e[12]||(e[12]=[u(" 强制启用分页模式 ",-1)])]),_:1},8,["disabled"]),s(a,{onClick:V,disabled:!o.value},{default:l(()=>[...e[13]||(e[13]=[u(" 清空编辑器 ",-1)])]),_:1},8,["disabled"])]),_:1}),s(d,{label:"长文档测试",name:"long"},{default:l(()=>[s(r,{type:"info",closable:!1,style:{"margin-bottom":"16px"}},{default:l(()=>[...e[14]||(e[14]=[u(" 💡 加载超长文档，测试编辑器性能和分页布局 ",-1)])]),_:1}),s(a,{type:"primary",onClick:$},{default:l(()=>[...e[15]||(e[15]=[u(" 加载长文档（4章节） ",-1)])]),_:1})]),_:1})]),_:1},8,["modelValue"])]),_:1}),f.value?(k(),w(g,{key:0,shadow:"never",style:{"margin-top":"16px"}},{header:l(()=>[...e[16]||(e[16]=[v("h3",null,"转换日志",-1)])]),default:l(()=>[v("pre",K,z(f.value),1)]),_:1})):x("",!0),s(g,{shadow:"never",style:{"margin-top":"16px"}},{header:l(()=>[...e[17]||(e[17]=[v("h3",null,"富文本编辑器",-1)])]),default:l(()=>[v("div",X,[s(L(J),{ref_key:"editorRef",ref:o,modelValue:y.value,"onUpdate:modelValue":e[1]||(e[1]=m=>y.value=m),title:"测试文档",height:800,onReady:M},null,8,["modelValue"])])]),_:1})])}}}),ce=Y(Z,[["__scopeId","data-v-e5c086fb"]]);export{ce as default};
