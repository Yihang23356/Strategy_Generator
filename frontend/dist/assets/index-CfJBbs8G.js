(function(){const e=document.createElement("link").relList;if(e&&e.supports&&e.supports("modulepreload"))return;for(const t of document.querySelectorAll('link[rel="modulepreload"]'))a(t);new MutationObserver(t=>{for(const n of t)if(n.type==="childList")for(const i of n.addedNodes)i.tagName==="LINK"&&i.rel==="modulepreload"&&a(i)}).observe(document,{childList:!0,subtree:!0});function s(t){const n={};return t.integrity&&(n.integrity=t.integrity),t.referrerPolicy&&(n.referrerPolicy=t.referrerPolicy),t.crossOrigin==="use-credentials"?n.credentials="include":t.crossOrigin==="anonymous"?n.credentials="omit":n.credentials="same-origin",n}function a(t){if(t.ep)return;t.ep=!0;const n=s(t);fetch(t.href,n)}})();async function m(r){return f(r)}function f(r){const e=new Date().toLocaleString("zh-CN");return new Promise(s=>{setTimeout(()=>{s({source:"mock",message:"当前未配置 VITE_API_BASE_URL，返回的是前端模拟结果。",createdAt:e,input:r,result:{passed:!1,iterations:1,final_review:"建议先接入后端 /run 接口以得到真实评分结果。",history:[{round:1,plan:"根据输入参数生成执行计划（模拟）",actor_output:"执行者已完成一次模拟执行",evaluator_feedback:"评价者建议补充真实接口联调",gate:{pass:!1,score:65,reason:"mock 数据仅用于页面展示"}}]}})},700)})}const b=document.querySelector("#app");b.innerHTML=`
  <main class="container">
    <h1>策略规划器</h1>
    <p class="subtitle">填写参数后执行，可在右侧查看运行结果</p>

    <section class="panel">
      <form id="plannerForm" class="form">
        <label>
          审核任务
          <input name="audit_task" value="根据三份输入差异动态完成审核并输出结果" required />
        </label>
        <label>
          质量标准
          <input name="quality_bar" value="审核结果正确、覆盖关键差异、说明清晰" required />
        </label>
        <label>
          达标分数
          <input type="number" name="pass_score" min="1" max="100" value="90" required />
        </label>
        <label>
          最大迭代次数
          <input type="number" name="max_iterations" min="1" max="300" value="3" required />
        </label>
        <label>
          输入文件 A
          <input name="input_a" value="data/input_a.json" required />
        </label>
        <label>
          输入文件 B
          <input name="input_b" value="data/input_b.json" required />
        </label>
        <label>
          输入文件 C
          <input name="input_c" value="data/input_c.json" required />
        </label>
        <label>
          标准答案文件
          <input name="standard_file" value="data/standard_answer.json" required />
        </label>
        <button id="runBtn" type="submit">执行规划</button>
      </form>

      <div class="result-wrap">
        <div class="result-header">
          <h2>结果</h2>
          <span id="status" class="status idle">待执行</span>
        </div>
        <pre id="result">点击“执行规划”后显示结果...</pre>
      </div>
    </section>
  </main>
`;const l=document.querySelector("#plannerForm"),c=document.querySelector("#status"),_=document.querySelector("#result"),d=document.querySelector("#runBtn");l.addEventListener("submit",async r=>{r.preventDefault();const e=new FormData(l),s={audit_task:String(e.get("audit_task")||""),quality_bar:String(e.get("quality_bar")||""),pass_score:Number(e.get("pass_score")||90),max_iterations:Number(e.get("max_iterations")||3),input_files:[String(e.get("input_a")||""),String(e.get("input_b")||""),String(e.get("input_c")||"")],standard_file:String(e.get("standard_file")||"")};p(!0),u({message:"执行中..."});try{const a=await m(s);o("success","执行成功"),u(a)}catch(a){o("error","执行失败"),u({error:a instanceof Error?a.message:"未知错误"})}finally{p(!1)}});function p(r){d.disabled=r,d.textContent=r?"执行中...":"执行规划",r&&o("loading","执行中")}function o(r,e){c.className=`status ${r}`,c.textContent=e}function u(r){_.textContent=JSON.stringify(r,null,2)}
