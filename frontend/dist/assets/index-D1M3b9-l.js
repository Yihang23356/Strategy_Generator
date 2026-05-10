(function(){const t=document.createElement("link").relList;if(t&&t.supports&&t.supports("modulepreload"))return;for(const s of document.querySelectorAll('link[rel="modulepreload"]'))i(s);new MutationObserver(s=>{for(const a of s)if(a.type==="childList")for(const f of a.addedNodes)f.tagName==="LINK"&&f.rel==="modulepreload"&&i(f)}).observe(document,{childList:!0,subtree:!0});function n(s){const a={};return s.integrity&&(a.integrity=s.integrity),s.referrerPolicy&&(a.referrerPolicy=s.referrerPolicy),s.crossOrigin==="use-credentials"?a.credentials="include":s.crossOrigin==="anonymous"?a.credentials="omit":a.credentials="same-origin",a}function i(s){if(s.ep)return;s.ep=!0;const a=n(s);fetch(s.href,a)}})();const v="";async function h(e){if(!e.ok){const t=await e.text();throw new Error(t||`请求失败: ${e.status}`)}return e.json()}async function C(e){const t=await fetch(`${v}/api/review/run-upload`,{method:"POST",body:e});return h(t)}async function L(e){const t=await fetch(`${v}/api/review/runs/${e}`);return h(t)}async function N(){const e=await fetch(`${v}/health`);return h(e)}const E=document.querySelector("#app");E.innerHTML=`
  <main class="shell">
    <header class="app-header">
      <div class="brand">
        <span class="brand-mark" aria-hidden="true"></span>
        <div>
          <h1>策略规划器</h1>
          <p>上传三份输入文件与标准答案，查看后端节点进度、大模型调用和工具调用。</p>
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
            <p>提交后会创建后台任务，右侧同步显示运行状态。</p>
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
            <p>文件会保存到后端 workspace/input/uploads，再进入审核图流程。</p>
          </div>
        </div>

        <div class="upload-list">
          ${u("input_a","输入 A","待审核输入文件")}
          ${u("input_b","输入 B","待审核输入文件")}
          ${u("input_c","输入 C","待审核输入文件")}
          ${u("standard_file","标准答案","用于评价审核结果")}
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
            <span>当前节点</span>
            <strong id="metricNode">-</strong>
          </div>
          <div class="metric">
            <span>任务状态</span>
            <strong id="metricPassed">-</strong>
          </div>
          <div class="metric">
            <span>结果文件</span>
            <strong id="metricFile">-</strong>
          </div>
        </div>

        <div class="timeline-wrap">
          <h3>后端运行日志</h3>
          <div id="timeline" class="timeline empty">暂无运行事件。</div>
        </div>

        <pre id="result">点击“运行审核”后显示后端返回结果。</pre>
      </aside>
    </section>
  </main>
`;const b=document.querySelector("#reviewForm"),_=document.querySelector("#runBtn"),S=document.querySelector("#runStatus"),w=document.querySelector("#backendStatus"),P=document.querySelector("#result"),d=document.querySelector("#summary"),k=document.querySelector("#metricNode"),A=document.querySelector("#metricPassed"),O=document.querySelector("#metricFile"),r=document.querySelector("#timeline");let p=null;F();D();b.addEventListener("submit",async e=>{e.preventDefault(),y();const t=R(new FormData(b));m(!0),o("loading","提交中"),g("-","-","-"),x([]),d.textContent="正在上传文件并创建后台任务。",c({message:"提交中..."});try{const n=await C(t);o("loading","运行中"),d.textContent=`任务已创建：${n.run_id}`,c(n),B(n.run_id)}catch(n){o("error","提交失败"),g("-","失败","-"),d.textContent="后端返回错误，请查看下方详情。",c({error:n instanceof Error?n.message:"未知错误"}),m(!1)}});function u(e,t,n){return`
    <label class="upload-card">
      <input type="file" name="${e}" required />
      <span class="upload-title">${t}</span>
      <span class="upload-hint">${n}</span>
      <span class="upload-file" data-file-label="${e}">选择文件</span>
    </label>
  `}function F(){document.querySelectorAll('input[type="file"]').forEach(e=>{e.addEventListener("change",()=>{var n,i;const t=document.querySelector(`[data-file-label="${e.name}"]`);t.textContent=((i=(n=e.files)==null?void 0:n[0])==null?void 0:i.name)||"选择文件"})})}function R(e){const t=new FormData;return t.append("audit_task",String(e.get("audit_task")||"")),t.append("quality_bar",String(e.get("quality_bar")||"")),t.append("pass_score",String(e.get("pass_score")||90)),t.append("max_iterations",String(e.get("max_iterations")||3)),t.append("input_a",e.get("input_a")),t.append("input_b",e.get("input_b")),t.append("input_c",e.get("input_c")),t.append("standard_file",e.get("standard_file")),t}function B(e){p=window.setInterval(()=>$(e),1e3),$(e)}async function $(e){try{const t=await L(e);T(t),(t.status==="completed"||t.status==="failed")&&(y(),m(!1))}catch(t){y(),m(!1),o("error","状态读取失败"),c({error:t instanceof Error?t.message:"未知错误"})}}function T(e){var n;const t=H(e.status);o(e.status==="failed"?"error":e.status==="completed"?"success":"loading",t),g(e.current_node||"-",t,((n=e.result)==null?void 0:n.final_actor_result_file)||"-"),d.textContent=e.error||`当前节点：${e.current_node||"-"}`,x(e.events||[]),c(e.result||e)}function x(e){if(!e.length){r.className="timeline empty",r.textContent="暂无运行事件。";return}r.className="timeline",r.innerHTML=e.map(t=>{const n=Object.keys(t.data||{}).length?`<pre>${l(JSON.stringify(t.data,null,2))}</pre>`:"";return`
        <article class="timeline-item ${t.type}">
          <div class="timeline-meta">
            <span>${l(t.time||"")}</span>
            <strong>${l(t.node||"")}</strong>
            <em>${l(t.type||"info")}</em>
          </div>
          <p>${l(t.message||"")}</p>
          ${n}
        </article>
      `}).join(""),r.scrollTop=r.scrollHeight}async function D(){try{await N(),q("success","后端已连接")}catch{q("error","后端未连接")}}function y(){p&&(window.clearInterval(p),p=null)}function m(e){_.disabled=e,_.textContent=e?"运行中...":"运行审核"}function o(e,t){S.className=`status ${e}`,S.textContent=t}function q(e,t){w.className=`status ${e}`,w.textContent=t}function g(e,t,n){k.textContent=e,A.textContent=t,O.textContent=n}function c(e){P.textContent=JSON.stringify(e,null,2)}function H(e){return{queued:"排队中",running:"运行中",completed:"已完成",failed:"失败"}[e]||e||"-"}function l(e){return String(e).replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;").replaceAll("'","&#039;")}
