const $ = (id) => document.getElementById(id);

function statusClass(status) {
  if (status === "ready" || status === "ack") return "status-ok";
  if (status === "blocked" || status === "closed") return "status-stop";
  return "status-warn";
}

function renderNews(items) {
  $("news").innerHTML = items.slice(0, 3).map((item) => `
    <article class="news">
      <time>${item.time}</time>
      <h3>${item.headline}</h3>
      <p>${item.detail}</p>
    </article>
  `).join("");
}

function renderRows(id, items) {
  $(id).innerHTML = items.map((item) => `
    <div class="row">
      <div>
        <strong>${item.name}</strong>
        <p>${item.detail}</p>
      </div>
      <div class="score ${statusClass(item.status)}">${item.score || item.status}</div>
    </div>
  `).join("");
}

function renderFleet(items) {
  $("fleet").innerHTML = items.map((item) => `
    <article class="pod">
      <strong>${item.label}</strong>
      <p>${item.task}</p>
      <small class="${statusClass(item.status)}">${item.status}</small>
    </article>
  `).join("");
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

