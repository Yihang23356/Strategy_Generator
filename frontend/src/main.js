import "./style.css";
import { getBackendHealth, getReviewRun, runReviewUpload } from "./api";

const app = document.querySelector("#app");

app.innerHTML = `
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
          ${uploadCard("input_a", "输入 A", "待审核输入文件")}
          ${uploadCard("input_b", "输入 B", "待审核输入文件")}
          ${uploadCard("input_c", "输入 C", "待审核输入文件")}
          ${uploadCard("standard_file", "标准答案", "用于评价审核结果")}
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
`;

const form = document.querySelector("#reviewForm");
const runBtn = document.querySelector("#runBtn");
const runStatus = document.querySelector("#runStatus");
const backendStatus = document.querySelector("#backendStatus");
const resultEl = document.querySelector("#result");
const summaryEl = document.querySelector("#summary");
const metricNode = document.querySelector("#metricNode");
const metricPassed = document.querySelector("#metricPassed");
const metricFile = document.querySelector("#metricFile");
const timelineEl = document.querySelector("#timeline");

let pollTimer = null;

bindUploadLabels();
checkBackend();

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearPolling();
  const formData = buildFormData(new FormData(form));

  setLoading(true);
  setRunStatus("loading", "提交中");
  setMetrics("-", "-", "-");
  setTimeline([]);
  summaryEl.textContent = "正在上传文件并创建后台任务。";
  setResult({ message: "提交中..." });

  try {
    const created = await runReviewUpload(formData);
    setRunStatus("loading", "运行中");
    summaryEl.textContent = `任务已创建：${created.run_id}`;
    setResult(created);
    startPolling(created.run_id);
  } catch (error) {
    setRunStatus("error", "提交失败");
    setMetrics("-", "失败", "-");
    summaryEl.textContent = "后端返回错误，请查看下方详情。";
    setResult({ error: error instanceof Error ? error.message : "未知错误" });
    setLoading(false);
  }
});

function uploadCard(name, title, hint) {
  return `
    <label class="upload-card">
      <input type="file" name="${name}" required />
      <span class="upload-title">${title}</span>
      <span class="upload-hint">${hint}</span>
      <span class="upload-file" data-file-label="${name}">选择文件</span>
    </label>
  `;
}

function bindUploadLabels() {
  document.querySelectorAll('input[type="file"]').forEach((input) => {
    input.addEventListener("change", () => {
      const label = document.querySelector(`[data-file-label="${input.name}"]`);
      label.textContent = input.files?.[0]?.name || "选择文件";
    });
  });
}

function buildFormData(data) {
  const formData = new FormData();
  formData.append("audit_task", String(data.get("audit_task") || ""));
  formData.append("quality_bar", String(data.get("quality_bar") || ""));
  formData.append("pass_score", String(data.get("pass_score") || 90));
  formData.append("max_iterations", String(data.get("max_iterations") || 3));
  formData.append("input_a", data.get("input_a"));
  formData.append("input_b", data.get("input_b"));
  formData.append("input_c", data.get("input_c"));
  formData.append("standard_file", data.get("standard_file"));
  return formData;
}

function startPolling(runId) {
  pollTimer = window.setInterval(() => pollRun(runId), 1000);
  pollRun(runId);
}

async function pollRun(runId) {
  try {
    const run = await getReviewRun(runId);
    renderRun(run);
    if (run.status === "completed" || run.status === "failed") {
      clearPolling();
      setLoading(false);
    }
  } catch (error) {
    clearPolling();
    setLoading(false);
    setRunStatus("error", "状态读取失败");
    setResult({ error: error instanceof Error ? error.message : "未知错误" });
  }
}

function renderRun(run) {
  const statusLabel = statusText(run.status);
  setRunStatus(run.status === "failed" ? "error" : run.status === "completed" ? "success" : "loading", statusLabel);
  setMetrics(run.current_node || "-", statusLabel, run.result?.final_actor_result_file || "-");
  summaryEl.textContent = run.error || `当前节点：${run.current_node || "-"}`;
  setTimeline(run.events || []);
  setResult(run.result || run);
}

function setTimeline(events) {
  if (!events.length) {
    timelineEl.className = "timeline empty";
    timelineEl.textContent = "暂无运行事件。";
    return;
  }
  timelineEl.className = "timeline";
  timelineEl.innerHTML = events
    .map((event) => {
      const data = Object.keys(event.data || {}).length
        ? `<pre>${escapeHtml(JSON.stringify(event.data, null, 2))}</pre>`
        : "";
      return `
        <article class="timeline-item ${event.type}">
          <div class="timeline-meta">
            <span>${escapeHtml(event.time || "")}</span>
            <strong>${escapeHtml(event.node || "")}</strong>
            <em>${escapeHtml(event.type || "info")}</em>
          </div>
          <p>${escapeHtml(event.message || "")}</p>
          ${data}
        </article>
      `;
    })
    .join("");
  timelineEl.scrollTop = timelineEl.scrollHeight;
}

async function checkBackend() {
  try {
    await getBackendHealth();
    setBackendStatus("success", "后端已连接");
  } catch {
    setBackendStatus("error", "后端未连接");
  }
}

function clearPolling() {
  if (pollTimer) {
    window.clearInterval(pollTimer);
    pollTimer = null;
  }
}

function setLoading(loading) {
  runBtn.disabled = loading;
  runBtn.textContent = loading ? "运行中..." : "运行审核";
}

function setRunStatus(type, text) {
  runStatus.className = `status ${type}`;
  runStatus.textContent = text;
}

function setBackendStatus(type, text) {
  backendStatus.className = `status ${type}`;
  backendStatus.textContent = text;
}

function setMetrics(node, status, file) {
  metricNode.textContent = node;
  metricPassed.textContent = status;
  metricFile.textContent = file;
}

function setResult(data) {
  resultEl.textContent = JSON.stringify(data, null, 2);
}

function statusText(status) {
  return {
    queued: "排队中",
    running: "运行中",
    completed: "已完成",
    failed: "失败",
  }[status] || status || "-";
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
