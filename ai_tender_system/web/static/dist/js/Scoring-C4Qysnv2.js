import{d as W,I as X,G as Z,f as ee,q as te,o as ae,i as oe,Q as le,J as ne,K as se,Y as re,a as ie,p as de,$ as ue,k as v}from"./element-plus-IkZgpaz4.js";/* empty css                                                                          */import{S as U}from"./SSEStreamViewer-BoeXFWk-.js";import"./umo-editor-BmhDOXHm.js";/* empty css                                                                        */import{bT as ce,bt as b,bu as L,bG as pe,bU as M,bV as g,c8 as a,b$ as E,c3 as I,c0 as o,c7 as me,cC as _e,bY as n,c5 as m,c2 as ve,c6 as k,bv as j,dM as ge}from"./vendor-CdA3MjAt.js";import{_ as fe}from"./index.js";import{t as he}from"./tender-2TSD_jRl.js";import"./mermaid-e-fO57px.js";import"./echarts-Cqw1j_Z-.js";import"./onnxruntime-DkHy2lK3.js";const we={class:"tender-scoring"},be={class:"card-header"},ye={class:"scoring-actions"},Se={class:"weight-summary"},ke={key:0,class:"weight-tip"},$e={class:"card-header"},Ve={class:"header-actions"},Ce={class:"dimension-scores"},Ee=["innerHTML"],Ie={class:"risk-analysis"},je={class:"improvement-suggestions"},xe=ce({__name:"Scoring",setup(Ue){const _=b({projectId:null}),x=b([]),y=L(()=>x.value.find(t=>t.id===_.value.projectId)),f=b([{name:"技术方案完整性",weight:30,description:"技术方案的完整性和可行性"},{name:"商务响应度",weight:25,description:"商务条款的响应程度"},{name:"资质匹配度",weight:20,description:"公司资质与项目要求的匹配程度"},{name:"成本合理性",weight:15,description:"报价的合理性和竞争力"},{name:"风险控制",weight:10,description:"项目风险的识别和控制措施"}]),S=L(()=>f.value.reduce((t,e)=>t+e.weight,0)),z=L(()=>_.value.projectId&&S.value===100&&f.value.length>0),h=b(!1),$=b(""),s=b(null),B=async()=>{var t;try{const e=await he.getProjects({page:1,page_size:100});x.value=((t=e.data)==null?void 0:t.items)||[]}catch(e){console.error("加载项目列表失败:",e),v.error("加载项目列表失败")}},D=()=>{s.value=null,$.value=""},F=()=>{f.value.push({name:"",weight:0,description:""})},N=t=>{f.value.splice(t,1)},P=async()=>{if(!_.value.projectId){v.warning("请先选择项目");return}if(S.value!==100){v.warning("评分维度权重总和必须为100%");return}h.value=!0,$.value="",s.value=null;try{await O(),v.success("评分完成")}catch(t){console.error("评分失败:",t),v.error("评分失败，请重试")}finally{h.value=!1}},O=async()=>new Promise(t=>{let e=0;const c=setInterval(()=>{if(e+=10,$.value+=`
正在分析第 ${e/10} 个维度...`,e>=100){clearInterval(c);const r=f.value.map(p=>{const d=Math.random()*30+70;return{...p,score:Math.round(d),weightedScore:d*p.weight/100,analysis:`该维度表现${d>=85?"优秀":d>=70?"良好":"一般"}，${d>=85?"完全满足招标要求，具有明显竞争优势。":d>=70?"基本满足招标要求，但仍有改进空间。":"存在一定差距，需要重点改进。"}

**优势：**
- 方案设计合理
- 团队经验丰富

**不足：**
- 部分细节需要完善`}}),i=r.reduce((p,d)=>p+d.weightedScore,0);s.value={totalScore:Math.round(i),dimensions:r,riskAnalysis:`# 风险评估

## 技术风险
- **中等风险**: 部分技术方案需要进一步细化
- 建议加强技术团队的配置

## 商务风险
- **低风险**: 商务条款基本符合要求
- 价格竞争力较强

## 执行风险
- **中等风险**: 项目周期较紧
- 需要合理安排资源和进度`,suggestions:`# 改进建议

## 技术方案优化
1. 完善系统架构设计文档
2. 补充性能测试方案
3. 加强数据安全保障措施

## 商务条款完善
1. 明确验收标准
2. 补充售后服务承诺

## 团队能力提升
1. 增加项目相关经验人员
2. 提供更详细的团队简历`},t()}},300)}),G=()=>{h.value=!1,v.info("已停止评分")},A=t=>t>=90?"success":t>=80?"":t>=70?"warning":"danger",H=t=>{try{return ge.parse(t)}catch{return t}},Y=()=>{var i;if(!s.value)return;const t=q(),e=new Blob([t],{type:"text/plain;charset=utf-8"}),c=URL.createObjectURL(e),r=document.createElement("a");r.href=c,r.download=`标书评分报告-${((i=y.value)==null?void 0:i.project_name)||"report"}-${Date.now()}.txt`,document.body.appendChild(r),r.click(),document.body.removeChild(r),URL.revokeObjectURL(c),v.success("报告导出成功")},q=()=>{var e,c,r;if(!s.value)return"";let t=`# 标书评分报告

`;return t+=`## 项目信息
`,t+=`- 项目名称: ${(e=y.value)==null?void 0:e.project_name}
`,t+=`- 项目编号: ${(c=y.value)==null?void 0:c.project_number}
`,t+=`- 公司名称: ${(r=y.value)==null?void 0:r.company_name}
`,t+=`- 评分时间: ${new Date().toLocaleString()}

`,t+=`## 总体评分
`,t+=`**总分: ${s.value.totalScore} / 100**

`,t+=`## 各维度评分

`,s.value.dimensions.forEach((i,p)=>{t+=`### ${p+1}. ${i.name} (权重: ${i.weight}%)
`,t+=`- 得分: ${i.score}
`,t+=`- 加权得分: ${i.weightedScore.toFixed(2)}
`,t+=`- 分析:
${i.analysis}

`}),t+=`## ${s.value.riskAnalysis}

`,t+=`## ${s.value.suggestions}
`,t};return pe(()=>{B()}),(t,e)=>{const c=ae,r=te,i=ee,p=Z,d=oe,J=X,K=W,V=le,C=ie,u=se,Q=re,R=ne,T=de;return g(),M("div",we,[a(V,{class:"project-selector",shadow:"never"},{header:o(()=>[...e[1]||(e[1]=[n("div",{class:"card-header"},[n("span",null,"选择项目")],-1)])]),default:o(()=>[a(K,{model:_.value,"label-width":"100px"},{default:o(()=>[a(J,{gutter:20},{default:o(()=>[a(p,{span:12},{default:o(()=>[a(i,{label:"项目"},{default:o(()=>[a(r,{modelValue:_.value.projectId,"onUpdate:modelValue":e[0]||(e[0]=l=>_.value.projectId=l),placeholder:"请选择项目",filterable:"",onChange:D,style:{width:"100%"}},{default:o(()=>[(g(!0),M(me,null,_e(x.value,l=>(g(),E(c,{key:l.id,label:`${l.project_name} (${l.project_number})`,value:l.id},null,8,["label","value"]))),128))]),_:1},8,["modelValue"])]),_:1})]),_:1}),a(p,{span:12},{default:o(()=>[a(i,{label:"公司"},{default:o(()=>{var l;return[a(d,{value:((l=y.value)==null?void 0:l.company_name)||"-",disabled:""},null,8,["value"])]}),_:1})]),_:1})]),_:1})]),_:1},8,["model"])]),_:1}),_.value.projectId?(g(),E(V,{key:0,class:"scoring-config",shadow:"never"},{header:o(()=>[n("div",be,[e[3]||(e[3]=n("span",null,"评分维度配置",-1)),a(C,{type:"primary",size:"small",onClick:F},{default:o(()=>[...e[2]||(e[2]=[m(" 添加维度 ",-1)])]),_:1})])]),default:o(()=>[a(R,{data:f.value,border:""},{default:o(()=>[a(u,{type:"index",label:"序号",width:"60"}),a(u,{prop:"name",label:"评分维度","min-width":"150"},{default:o(({row:l})=>[a(d,{modelValue:l.name,"onUpdate:modelValue":w=>l.name=w,placeholder:"请输入评分维度"},null,8,["modelValue","onUpdate:modelValue"])]),_:1}),a(u,{prop:"weight",label:"权重 (%)",width:"120"},{default:o(({row:l})=>[a(Q,{modelValue:l.weight,"onUpdate:modelValue":w=>l.weight=w,min:0,max:100,step:5,"controls-position":"right",style:{width:"100%"}},null,8,["modelValue","onUpdate:modelValue"])]),_:1}),a(u,{prop:"description",label:"评分说明","min-width":"200"},{default:o(({row:l})=>[a(d,{modelValue:l.description,"onUpdate:modelValue":w=>l.description=w,type:"textarea",rows:2,placeholder:"请输入评分说明"},null,8,["modelValue","onUpdate:modelValue"])]),_:1}),a(u,{label:"操作",width:"100",fixed:"right"},{default:o(({$index:l})=>[a(C,{type:"danger",size:"small",text:"",onClick:w=>N(l)},{default:o(()=>[...e[4]||(e[4]=[m(" 删除 ",-1)])]),_:1},8,["onClick"])]),_:1})]),_:1},8,["data"]),n("div",ye,[n("div",Se,[e[5]||(e[5]=m(" 总权重: ",-1)),n("strong",{class:ve({error:S.value!==100})},k(S.value)+"%",3),S.value!==100?(g(),M("span",ke," (权重总和应为 100%) ")):I("",!0)]),a(C,{type:"primary",disabled:!z.value,loading:h.value,onClick:P},{default:o(()=>[...e[6]||(e[6]=[m(" 开始AI评分 ",-1)])]),_:1},8,["disabled","loading"])])]),_:1})):I("",!0),s.value?(g(),E(V,{key:1,class:"scoring-result",shadow:"never"},{header:o(()=>[n("div",$e,[e[8]||(e[8]=n("span",null,"评分结果",-1)),n("div",Ve,[a(T,{type:A(s.value.totalScore),size:"large"},{default:o(()=>[m(" 总分: "+k(s.value.totalScore)+" / 100 ",1)]),_:1},8,["type"]),a(C,{type:"success",size:"small",icon:j(ue),onClick:Y},{default:o(()=>[...e[7]||(e[7]=[m(" 导出报告 ",-1)])]),_:1},8,["icon"])])])]),default:o(()=>[n("div",Ce,[e[9]||(e[9]=n("h4",null,"各维度评分详情",-1)),a(R,{data:s.value.dimensions,border:""},{default:o(()=>[a(u,{type:"index",label:"序号",width:"60"}),a(u,{prop:"name",label:"评分维度","min-width":"150"}),a(u,{prop:"weight",label:"权重",width:"100"},{default:o(({row:l})=>[m(k(l.weight)+"% ",1)]),_:1}),a(u,{prop:"score",label:"得分",width:"100"},{default:o(({row:l})=>[a(T,{type:A(l.score)},{default:o(()=>[m(k(l.score),1)]),_:2},1032,["type"])]),_:1}),a(u,{prop:"weightedScore",label:"加权得分",width:"120"},{default:o(({row:l})=>[m(k(l.weightedScore.toFixed(2)),1)]),_:1}),a(u,{prop:"analysis",label:"AI分析","min-width":"300"},{default:o(({row:l})=>[n("div",{class:"analysis-content",innerHTML:H(l.analysis)},null,8,Ee)]),_:1})]),_:1},8,["data"])]),n("div",Ie,[e[10]||(e[10]=n("h4",null,"风险分析",-1)),a(j(U),{content:s.value.riskAnalysis,"is-streaming":!1,"enable-markdown":!0},null,8,["content"])]),n("div",je,[e[11]||(e[11]=n("h4",null,"改进建议",-1)),a(j(U),{content:s.value.suggestions,"is-streaming":!1,"enable-markdown":!0},null,8,["content"])])]),_:1})):I("",!0),h.value?(g(),E(V,{key:2,class:"streaming-output",shadow:"never"},{header:o(()=>[...e[12]||(e[12]=[n("div",{class:"card-header"},[n("span",null,"AI正在评分...")],-1)])]),default:o(()=>[a(j(U),{content:$.value,"is-streaming":h.value,onStop:G},null,8,["content","is-streaming"])]),_:1})):I("",!0)])}}}),Oe=fe(xe,[["__scopeId","data-v-187df135"]]);export{Oe as default};
