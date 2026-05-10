(function(){const t=document.createElement("link").relList;if(t&&t.supports&&t.supports("modulepreload"))return;for(const r of document.querySelectorAll('link[rel="modulepreload"]'))a(r);new MutationObserver(r=>{for(const s of r)if(s.type==="childList")for(const u of s.addedNodes)u.tagName==="LINK"&&u.rel==="modulepreload"&&a(u)}).observe(document,{childList:!0,subtree:!0});function n(r){const s={};return r.integrity&&(s.integrity=r.integrity),r.referrerPolicy&&(s.referrerPolicy=r.referrerPolicy),r.crossOrigin==="use-credentials"?s.credentials="include":r.crossOrigin==="anonymous"?s.credentials="omit":s.credentials="same-origin",s}function a(r){if(r.ep)return;r.ep=!0;const s=n(r);fetch(r.href,s)}})();const _="";async function h(e,t={}){const n=await fetch(`${_}${e}`,{headers:{"Content-Type":"application/json",...t.headers||{}},...t});if(!n.ok){const a=await n.text();throw new Error(a||`请求失败: ${n.status}`)}return n.json()}function v(e){return h("/api/review/run-with-content",{method:"POST",body:JSON.stringify(e)})}function S(){return h("/health")}const w=document.querySelector("#app");w.innerHTML=`
  <main class="container">
    <header class="topbar">
      <div>
        <h1>策略规划器</h1>
        <p class="subtitle">输入三份待审核内容和标准答案，后端会运行方案制定、执行和评价流程。</p>
      </div>
      <span id="backendStatus" class="status idle">检查连接中</span>
    </header>

    <section class="panel">
      <form id="reviewForm" class="form">
        <div class="grid two">
          <label>
            审核任务
            <input name="audit_task" value="根据三份输入差异完成审核并输出结构化结果" required />
          </label>
          <label>
            质量标准
            <input name="quality_bar" value="结果准确、覆盖关键差异、说明清晰、可复现" required />
          </label>
        </div>

        <div class="grid two">
          <label>
            达标分数
            <input type="number" name="pass_score" min="0" max="100" value="90" required />
          </label>
          <label>
            最大迭代次数
            <input type="number" name="max_iterations" min="1" max="20" value="3" required />
          </label>
        </div>

        <div class="file-grid">
          ${i("inputA","输入文件 A","case/input_a.json",'{\\n  "name": "input_a",\\n  "items": []\\n}')}
          ${i("inputB","输入文件 B","case/input_b.json",'{\\n  "name": "input_b",\\n  "items": []\\n}')}
          ${i("inputC","输入文件 C","case/input_c.json",'{\\n  "name": "input_c",\\n  "items": []\\n}')}
          ${i("standard","标准答案","case/standard_answer.json",'{\\n  "expected": "在这里填写标准审核结果"\\n}')}
        </div>

        <button id="runBtn" type="submit">运行审核</button>
      </form>

      <section class="result-wrap">
        <div class="result-header">
          <h2>运行结果</h2>
          <span id="runStatus" class="status idle">待运行</span>
        </div>
        <div id="summary" class="summary"></div>
        <pre id="result">点击“运行审核”后显示后端返回结果。</pre>
      </section>
    </section>
  </main>
`;const d=document.querySelector("#reviewForm"),m=document.querySelector("#runBtn"),p=document.querySelector("#runStatus"),f=document.querySelector("#backendStatus"),q=document.querySelector("#result"),y=document.querySelector("#summary");x();d.addEventListener("submit",async e=>{e.preventDefault();const t=$(new FormData(d));b(!0),c("loading","运行中"),l({message:"正在请求后端，请等待审核流程完成..."}),y.textContent="";try{const n=await v(t);c(n.passed?"success":"warning",n.passed?"已通过":"未通过"),y.textContent=`迭代 ${n.iterations} 次，结果文件：${n.final_actor_result_file||"-"}`,l(n)}catch(n){c("error","运行失败"),l({error:n instanceof Error?n.message:"未知错误"})}finally{b(!1)}});function i(e,t,n,a){return`
    <fieldset class="file-editor">
      <legend>${t}</legend>
      <label>
        文件路径
        <input name="${e}_path" value="${n}" required />
      </label>
      <label>
        文件内容
        <textarea name="${e}_content" rows="8" required>${a}</textarea>
      </label>
    </fieldset>
  `}function $(e){return{audit_task:String(e.get("audit_task")||""),quality_bar:String(e.get("quality_bar")||""),pass_score:Number(e.get("pass_score")||90),max_iterations:Number(e.get("max_iterations")||3),input_files:[o(e,"inputA"),o(e,"inputB"),o(e,"inputC")],standard_file:o(e,"standard")}}function o(e,t){return{path:String(e.get(`${t}_path`)||""),content:String(e.get(`${t}_content`)||"")}}async function x(){try{await S(),g("success","后端已连接")}catch{g("error","后端未连接")}}function b(e){m.disabled=e,m.textContent=e?"运行中...":"运行审核"}function c(e,t){p.className=`status ${e}`,p.textContent=t}function g(e,t){f.className=`status ${e}`,f.textContent=t}function l(e){q.textContent=JSON.stringify(e,null,2)}
