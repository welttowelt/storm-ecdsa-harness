const $ = (id) => document.getElementById(id);

function clear(el) {
  while (el.firstChild) el.removeChild(el.firstChild);
}

function appendText(parent, tag, text, className) {
  const el = document.createElement(tag);
  if (className) el.className = className;
  el.textContent = text;
  parent.appendChild(el);
  return el;
}

function statusClass(status) {
  if (status === "ready" || status === "ack") return "status-ok";
  if (status === "blocked" || status === "closed") return "status-stop";
  return "status-warn";
}

function renderNews(items) {
  const target = $("news");
  clear(target);
  items.slice(0, 3).forEach((item) => {
    const article = document.createElement("article");
    article.className = "news";
    appendText(article, "time", item.time);
    appendText(article, "h3", item.headline);
    appendText(article, "p", item.detail);
    target.appendChild(article);
  });
}

function renderRows(id, items) {
  const target = $(id);
  clear(target);
  items.forEach((item) => {
    const row = document.createElement("div");
    row.className = "row";

    const body = document.createElement("div");
    appendText(body, "strong", item.name);
    appendText(body, "p", item.detail);
    row.appendChild(body);

    appendText(row, "div", item.score || item.status, `score ${statusClass(item.status)}`);
    target.appendChild(row);
  });
}

function renderFleet(items) {
  const target = $("fleet");
  clear(target);
  items.forEach((item) => {
    const article = document.createElement("article");
    article.className = "pod";
    appendText(article, "strong", item.label);
    appendText(article, "p", item.task);
    appendText(article, "small", item.status, statusClass(item.status));
    target.appendChild(article);
  });
}

async function load() {
  const res = await fetch("./fixtures/status.json", { cache: "no-store" });
  const data = await res.json();

  $("subtitle").textContent = data.subtitle;
  $("target").textContent = data.current_target.label;
  $("target-detail").textContent = data.current_target.detail;
  $("route").textContent = data.active_route.label;
  $("route-detail").textContent = data.active_route.detail;
  $("submit").textContent = data.submit_gate.status;
  $("submit-detail").textContent = data.submit_gate.detail;

  renderNews(data.breaking_news);
  renderRows("workers", data.workers);
  renderRows("mailbox", data.mailbox);
  renderFleet(data.fleet);
}

$("refresh").addEventListener("click", load);
load().catch((err) => {
  $("subtitle").textContent = `Failed to load fixture data: ${err.message}`;
});
