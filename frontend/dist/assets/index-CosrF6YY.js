(function(){const t=document.createElement("link").relList;if(t&&t.supports&&t.supports("modulepreload"))return;for(const s of document.querySelectorAll('link[rel="modulepreload"]'))r(s);new MutationObserver(s=>{for(const a of s)if(a.type==="childList")for(const o of a.addedNodes)o.tagName==="LINK"&&o.rel==="modulepreload"&&r(o)}).observe(document,{childList:!0,subtree:!0});function n(s){const a={};return s.integrity&&(a.integrity=s.integrity),s.referrerPolicy&&(a.referrerPolicy=s.referrerPolicy),s.crossOrigin==="use-credentials"?a.credentials="include":s.crossOrigin==="anonymous"?a.credentials="omit":a.credentials="same-origin",a}function r(s){if(s.ep)return;s.ep=!0;const a=n(s);fetch(s.href,a)}})();const h="";async function g(e){if(!e.ok){const t=await e.text();throw new Error(t||`请求失败: ${e.status}`)}return e.json()}async function _(e){const t=await fetch(`${h}/api/review/run-upload`,{method:"POST",body:e});return g(t)}async function S(){const e=await fetch(`${h}/health`);return g(e)}const q=document.querySelector("#app");q.innerHTML=`
  <main class="shell">
    <header class="app-header">
      <div class="brand">
        <span class="brand-mark" aria-hidden="true"></span>
        <div>
          <h1>策略规划器</h1>
          <p>上传三份输入文件与标准答案，自动完成方案制定、执行和评价闭环。</p>
        </div>
      </div>
      <div class="header-actions">
        <span id="backendStatus" class="status idle">检查连接中</span>
      </div>
    </header>

    <section class="workspace">
      <form id="reviewForm" class="input-pane">
        <div class="section-head">
          <div>
            <h2>审核配置</h2>
            <p>这些参数会和上传文件一起发送到后端审核流程。</p>
          </div>
          <button id="runBtn" class="primary-button" type="submit">运行审核</button>
        </div>

        <div class="form-grid">
          <label class="field span-2">
            <span>审核任务</span>
            <input name="audit_task" value="根据三份输入差异完成审核并输出结构化结果" required />
          </label>
          <label class="field span-2">
            <span>质量标准</span>
            <input name="quality_bar" value="结果准确、覆盖关键差异、说明清晰、可复现" required />
          </label>
          <label class="field">
            <span>达标分数</span>
            <input type="number" name="pass_score" min="0" max="100" value="90" required />
          </label>
          <label class="field">
            <span>最大迭代次数</span>
            <input type="number" name="max_iterations" min="1" max="20" value="3" required />
          </label>
        </div>

        <div class="section-head compact">
          <div>
            <h2>输入文件</h2>
            <p>选择本地文件，后端会保存到 workspace/input/uploads 后进入审核图流程。</p>
          </div>
        </div>

        <div class="upload-list">
          ${i("input_a","输入 A","待审核输入文件")}
          ${i("input_b","输入 B","待审核输入文件")}
          ${i("input_c","输入 C","待审核输入文件")}
          ${i("standard_file","标准答案","用于评价审核结果")}
        </div>
      </form>

      <aside class="result-pane">
        <div class="section-head">
          <div>
            <h2>运行结果</h2>
            <p id="summary">等待任务提交。</p>
          </div>
          <span id="runStatus" class="status idle">待运行</span>
        </div>

        <div class="metric-row">
          <div class="metric">
            <span>状态</span>
            <strong id="metricPassed">-</strong>
          </div>
          <div class="metric">
            <span>迭代</span>
            <strong id="metricIterations">-</strong>
          </div>
          <div class="metric">
            <span>结果文件</span>
            <strong id="metricFile">-</strong>
          </div>
        </div>

        <pre id="result">点击“运行审核”后显示后端返回结果。</pre>
      </aside>
    </section>
  </main>
`;const p=document.querySelector("#reviewForm"),m=document.querySelector("#runBtn"),f=document.querySelector("#runStatus"),y=document.querySelector("#backendStatus"),x=document.querySelector("#result"),c=document.querySelector("#summary"),w=document.querySelector("#metricPassed"),$=document.querySelector("#metricIterations"),C=document.querySelector("#metricFile");L();E();p.addEventListener("submit",async e=>{e.preventDefault();const t=k(new FormData(p));v(!0),l("loading","运行中"),u("-","-","-"),c.textContent="正在上传文件并请求后端，请等待审核流程完成。",d({message:"审核流程运行中..."});try{const n=await _(t),r=n.passed?"已通过":"未通过";l(n.passed?"success":"warning",r),u(r,n.iterations??"-",n.final_actor_result_file||"-"),c.textContent=`审核完成，执行 ${n.iterations??0} 轮。`,d(n)}catch(n){l("error","运行失败"),u("失败","-","-"),c.textContent="后端返回错误，请查看下方详情。",d({error:n instanceof Error?n.message:"未知错误"})}finally{v(!1)}});function i(e,t,n){return`
    <label class="upload-card">
      <input type="file" name="${e}" required />
      <span class="upload-title">${t}</span>
      <span class="upload-hint">${n}</span>
      <span class="upload-file" data-file-label="${e}">选择文件</span>
    </label>
  `}function L(){document.querySelectorAll('input[type="file"]').forEach(e=>{e.addEventListener("change",()=>{var n,r;const t=document.querySelector(`[data-file-label="${e.name}"]`);t.textContent=((r=(n=e.files)==null?void 0:n[0])==null?void 0:r.name)||"选择文件"})})}function k(e){const t=new FormData;return t.append("audit_task",String(e.get("audit_task")||"")),t.append("quality_bar",String(e.get("quality_bar")||"")),t.append("pass_score",String(e.get("pass_score")||90)),t.append("max_iterations",String(e.get("max_iterations")||3)),t.append("input_a",e.get("input_a")),t.append("input_b",e.get("input_b")),t.append("input_c",e.get("input_c")),t.append("standard_file",e.get("standard_file")),t}async function E(){try{await S(),b("success","后端已连接")}catch{b("error","后端未连接")}}function v(e){m.disabled=e,m.textContent=e?"运行中...":"运行审核"}function l(e,t){f.className=`status ${e}`,f.textContent=t}function b(e,t){y.className=`status ${e}`,y.textContent=t}function u(e,t,n){w.textContent=e,$.textContent=t,C.textContent=n}function d(e){x.textContent=JSON.stringify(e,null,2)}
