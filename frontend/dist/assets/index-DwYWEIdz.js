(function(){const t=document.createElement("link").relList;if(t&&t.supports&&t.supports("modulepreload"))return;for(const s of document.querySelectorAll('link[rel="modulepreload"]'))a(s);new MutationObserver(s=>{for(const r of s)if(r.type==="childList")for(const c of r.addedNodes)c.tagName==="LINK"&&c.rel==="modulepreload"&&a(c)}).observe(document,{childList:!0,subtree:!0});function n(s){const r={};return s.integrity&&(r.integrity=s.integrity),s.referrerPolicy&&(r.referrerPolicy=s.referrerPolicy),s.crossOrigin==="use-credentials"?r.credentials="include":s.crossOrigin==="anonymous"?r.credentials="omit":r.credentials="same-origin",r}function a(s){if(s.ep)return;s.ep=!0;const r=n(s);fetch(s.href,r)}})();const _="";async function g(e,t={}){const n=await fetch(`${_}${e}`,{headers:{"Content-Type":"application/json",...t.headers||{}},...t});if(!n.ok){const a=await n.text();throw new Error(a||`请求失败: ${n.status}`)}return n.json()}function S(e){return g("/api/review/run-with-content",{method:"POST",body:JSON.stringify(e)})}function q(){return g("/health")}const x=document.querySelector("#app");x.innerHTML=`
  <main class="shell">
    <header class="app-header">
      <div class="brand">
        <span class="brand-mark" aria-hidden="true"></span>
        <div>
          <h1>策略规划器</h1>
          <p>提交三份输入与标准答案，自动完成方案制定、执行和评价闭环。</p>
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
            <p>这些参数会直接发送到后端审核流程。</p>
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
            <p>文件会写入后端 workspace/input，再进入审核图流程。</p>
          </div>
        </div>

        <div class="file-list">
          ${i("inputA","输入 A","case/input_a.json",'{\\n  "name": "input_a",\\n  "items": []\\n}')}
          ${i("inputB","输入 B","case/input_b.json",'{\\n  "name": "input_b",\\n  "items": []\\n}')}
          ${i("inputC","输入 C","case/input_c.json",'{\\n  "name": "input_c",\\n  "items": []\\n}')}
          ${i("standard","标准答案","case/standard_answer.json",'{\\n  "expected": "在这里填写标准审核结果"\\n}')}
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
`;const m=document.querySelector("#reviewForm"),f=document.querySelector("#runBtn"),v=document.querySelector("#runStatus"),y=document.querySelector("#backendStatus"),w=document.querySelector("#result"),u=document.querySelector("#summary"),$=document.querySelector("#metricPassed"),C=document.querySelector("#metricIterations"),P=document.querySelector("#metricFile");L();m.addEventListener("submit",async e=>{e.preventDefault();const t=B(new FormData(m));h(!0),l("loading","运行中"),d("-","-","-"),u.textContent="正在请求后端，请等待审核流程完成。",p({message:"审核流程运行中..."});try{const n=await S(t),a=n.passed?"已通过":"未通过";l(n.passed?"success":"warning",a),d(a,n.iterations??"-",n.final_actor_result_file||"-"),u.textContent=`审核完成，执行 ${n.iterations??0} 轮。`,p(n)}catch(n){l("error","运行失败"),d("失败","-","-"),u.textContent="后端返回错误，请查看下方详情。",p({error:n instanceof Error?n.message:"未知错误"})}finally{h(!1)}});function i(e,t,n,a){return`
    <section class="file-editor">
      <div class="file-title">
        <strong>${t}</strong>
        <input name="${e}_path" value="${n}" aria-label="${t}路径" required />
      </div>
      <textarea name="${e}_content" rows="8" aria-label="${t}内容" required>${a}</textarea>
    </section>
  `}function B(e){return{audit_task:String(e.get("audit_task")||""),quality_bar:String(e.get("quality_bar")||""),pass_score:Number(e.get("pass_score")||90),max_iterations:Number(e.get("max_iterations")||3),input_files:[o(e,"inputA"),o(e,"inputB"),o(e,"inputC")],standard_file:o(e,"standard")}}function o(e,t){return{path:String(e.get(`${t}_path`)||""),content:String(e.get(`${t}_content`)||"")}}async function L(){try{await q(),b("success","后端已连接")}catch{b("error","后端未连接")}}function h(e){f.disabled=e,f.textContent=e?"运行中...":"运行审核"}function l(e,t){v.className=`status ${e}`,v.textContent=t}function b(e,t){y.className=`status ${e}`,y.textContent=t}function d(e,t,n){$.textContent=e,C.textContent=t,P.textContent=n}function p(e){w.textContent=JSON.stringify(e,null,2)}
