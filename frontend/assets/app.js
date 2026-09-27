/* Resume Parser — front end for the rule-based FastAPI resume parser. */
(function () {
  "use strict";

  const { $, $$, el, esc, icon, http, toast, modal, bytes, date, initials, debounce } = UI;

  http.base = "";

  let resumes = [];

  const LIST_FIELDS = ["skills", "education", "experience", "projects", "certifications", "languages"];
  const TEXT_FIELDS = ["full_name", "email", "phone_number", "linkedin", "github", "summary"];
  const ALL_FIELDS = TEXT_FIELDS.concat(LIST_FIELDS);

  const FIELD_ICONS = {
    full_name: "user", email: "mail", phone_number: "phone", linkedin: "link",
    github: "code", summary: "quote", skills: "zap", education: "school",
    experience: "briefcase", projects: "layers", certifications: "award", languages: "globe",
  };

  const label = (key) => String(key).replace(/_/g, " ");

  /* ---------------- connection ---------------- */
  async function ping() {
    const node = $("#conn");
    const text = $(".conn-text", node);
    try {
      await http.get("/openapi.json");
      node.className = "conn online";
      text.textContent = "API connected";
    } catch (_) {
      node.className = "conn offline";
      text.textContent = "API unreachable";
    }
  }

  /* ---------------- data ---------------- */
  async function load() {
    try {
      const data = await http.get("/resume");
      resumes = Array.isArray(data) ? data : [];
    } catch (err) {
      resumes = [];
      toast(err.message, "error");
    }
    $("[data-count='res']").textContent = resumes.length;
    renderStats();
    renderCoverage();
    renderTopSkills();
    renderTable();
  }

  const listOf = (r, key) => (Array.isArray(r[key]) ? r[key] : []);

  /* ---------------- overview ---------------- */
  function renderStats() {
    const skills = new Set();
    resumes.forEach((r) => listOf(r, "skills").forEach((s) => skills.add(String(s).toLowerCase())));
    const withContact = resumes.filter((r) => r.email || r.phone_number).length;
    const size = resumes.reduce((a, r) => a + (r.file_size || 0), 0);

    $("#stats").innerHTML = [
      { label: "Résumés", value: resumes.length, hint: "parsed and stored", ic: "fileText" },
      { label: "With contact details", value: withContact, hint: "email or phone matched", ic: "mail" },
      { label: "Distinct skills", value: skills.size, hint: "across the collection", ic: "zap" },
      { label: "Stored size", value: bytes(size), hint: "of original PDFs", ic: "database" },
    ]
      .map(
        (t) => `<div class="stat">
          <div class="stat-icon">${icon(t.ic, 16)}</div>
          <div class="stat-label">${esc(t.label)}</div>
          <div class="stat-value">${esc(t.value)}</div>
          <div class="stat-hint">${esc(t.hint)}</div></div>`
      )
      .join("");
  }

  function renderCoverage() {
    const host = $("#coverage");
    if (!resumes.length) {
      host.innerHTML = `<p class="muted small">Coverage appears once résumés have been parsed.</p>`;
      return;
    }

    host.innerHTML = ALL_FIELDS.map((key) => {
      const hits = resumes.filter((r) =>
        LIST_FIELDS.includes(key) ? listOf(r, key).length : !!r[key]
      ).length;
      const ratio = hits / resumes.length;
      return `
      <div class="cov-row">
        <div class="cov-name">${esc(label(key))}</div>
        <div class="cov-bar">
          <div class="meter ${ratio > 0.66 ? "ok" : ratio > 0.33 ? "warn" : ""}">
            <span style="width:${ratio * 100}%"></span>
          </div>
        </div>
        <div class="cov-pct">${Math.round(ratio * 100)}%</div>
      </div>`;
    }).join("");
  }

  function renderTopSkills() {
    const map = new Map();
    resumes.forEach((r) =>
      listOf(r, "skills").forEach((s) => {
        const name = String(s).trim();
        if (!name) return;
        const key = name.toLowerCase();
        const entry = map.get(key) || { name, count: 0 };
        entry.count++;
        map.set(key, entry);
      })
    );

    const top = Array.from(map.values()).sort((a, b) => b.count - a.count).slice(0, 14);
    const host = $("#topSkills");

    if (!top.length) {
      host.innerHTML = `<p class="muted small">Skills appear once a résumé lists them.</p>`;
      return;
    }

    host.innerHTML = `<div class="tag-list">${top
      .map((s) => `<span class="tag">${esc(s.name)} <b style="color:var(--accent)">${s.count}</b></span>`)
      .join("")}</div>`;
  }

  /* ---------------- table ---------------- */
  function renderTable() {
    const term = ($("#filter").value || "").toLowerCase();
    const rows = resumes.filter((r) =>
      !term
        ? true
        : [r.full_name, r.email, r.filename, r.phone_number]
            .filter(Boolean).join(" ").toLowerCase().includes(term)
    );

    $("#badge").textContent = `${rows.length} of ${resumes.length}`;
    const host = $("#table");

    if (!rows.length) {
      host.innerHTML = `<div class="empty">
        <div class="empty-icon">${icon("users", 24)}</div>
        <h3>${resumes.length ? "No match for that filter" : "No résumés yet"}</h3>
        <p>${resumes.length ? "Clear the filter to see everything." : "Upload a PDF to get started."}</p></div>`;
      return;
    }

    host.innerHTML = `
      <div class="table-wrap"><table class="table">
        <thead><tr><th>Candidate</th><th>Contact</th><th class="num">Skills</th><th>File</th><th>Uploaded</th><th></th></tr></thead>
        <tbody>${rows
          .map(
            (r) => `
          <tr>
            <td>
              <div class="cand-cell">
                <div class="avatar">${esc(initials(r.full_name))}</div>
                <div class="ci">
                  <div class="cn truncate">${esc(r.full_name || "Name not matched")}</div>
                  <div class="ce truncate">${esc(r.email || "—")}</div>
                </div>
              </div>
            </td>
            <td class="nowrap">${esc(r.phone_number || "—")}</td>
            <td class="num">${listOf(r, "skills").length}</td>
            <td class="truncate">${esc(r.filename || "—")}</td>
            <td class="nowrap">${esc(date(r.uploaded_at))}</td>
            <td class="actions">
              <button class="btn btn-sm btn-ghost" data-open="${r.pdf_id}" title="Open">${icon("eye", 13)}</button>
              <button class="btn btn-sm btn-ghost" data-edit="${r.pdf_id}" title="Edit">${icon("edit", 13)}</button>
              <button class="btn btn-sm btn-ghost" data-del="${r.pdf_id}" title="Delete">${icon("trash", 13)}</button>
            </td>
          </tr>`
          )
          .join("")}</tbody></table></div>`;

    $$("#table [data-open]").forEach((b) => b.addEventListener("click", () => openResume(Number(b.dataset.open))));
    $$("#table [data-edit]").forEach((b) => b.addEventListener("click", () => editResume(Number(b.dataset.edit))));
    $$("#table [data-del]").forEach((b) => b.addEventListener("click", () => removeResume(Number(b.dataset.del))));
  }

  /* ---------------- detail ---------------- */
  function detailHtml(r) {
    const section = (key, content) =>
      content
        ? `<div class="section"><h4>${icon(FIELD_ICONS[key] || "fileText", 14)} ${esc(label(key))}</h4>${content}</div>`
        : "";

    const links = [
      r.linkedin && ["link", "LinkedIn", r.linkedin],
      r.github && ["code", "GitHub", r.github],
    ].filter(Boolean);

    return `
      <div class="row mb-2" style="gap:13px">
        <div class="avatar lg">${esc(initials(r.full_name))}</div>
        <div>
          <h3>${esc(r.full_name || "Name not matched")}</h3>
          <div class="muted small">${esc(r.filename || "")}</div>
        </div>
      </div>

      <dl class="kv mb-3">
        ${r.email ? `<dt>Email</dt><dd>${esc(r.email)}</dd>` : ""}
        ${r.phone_number ? `<dt>Phone</dt><dd>${esc(r.phone_number)}</dd>` : ""}
        ${
          links.length
            ? `<dt>Links</dt><dd class="row tight">${links
                .map(([ic, name, url]) => `<a class="tag" href="${esc(url)}" target="_blank" rel="noopener">${icon(ic, 13)} ${esc(name)}</a>`)
                .join("")}</dd>`
            : ""
        }
        ${r.file_size ? `<dt>File size</dt><dd>${esc(bytes(r.file_size))}</dd>` : ""}
        ${r.uploaded_at ? `<dt>Uploaded</dt><dd>${esc(date(r.uploaded_at, true))}</dd>` : ""}
      </dl>

      ${section("summary", r.summary ? `<p class="small muted">${esc(r.summary)}</p>` : null)}
      ${section(
        "skills",
        listOf(r, "skills").length
          ? `<div class="tag-list">${listOf(r, "skills").map((s) => `<span class="tag">${esc(s)}</span>`).join("")}</div>`
          : null
      )}
      ${["experience", "education", "projects", "certifications", "languages"]
        .map((key) =>
          section(
            key,
            listOf(r, key).length
              ? `<ul class="bullets">${listOf(r, key).map((v) => `<li>${esc(v)}</li>`).join("")}</ul>`
              : null
          )
        )
        .join("")}`;
  }

  async function openResume(id) {
    const m = modal({
      title: "Loading résumé…",
      size: "lg",
      body: `<div class="skeleton skeleton-line"></div><div class="skeleton skeleton-line"></div><div class="skeleton skeleton-line"></div>`,
    });

    try {
      const r = await http.get(`/resume/${id}`);
      $("h3", m.box).textContent = r.full_name || r.filename || "Résumé";
      m.body.innerHTML = detailHtml(r);
    } catch (err) {
      m.body.innerHTML = `<p class="muted">${esc(err.message)}</p>`;
    }
  }

  async function editResume(id) {
    let r;
    try {
      r = await http.get(`/resume/${id}`);
    } catch (err) {
      toast(err.message, "error");
      return;
    }

    const form = el("form", { class: "edit-grid" });
    form.innerHTML = `
      ${TEXT_FIELDS.filter((k) => k !== "summary")
        .map(
          (key) => `
        <div class="field">
          <label>${esc(label(key))}</label>
          <input class="input" name="${key}" value="${esc(r[key] || "")}">
        </div>`
        )
        .join("")}
      <div class="field full">
        <label>Summary</label>
        <textarea class="textarea" name="summary" rows="3">${esc(r.summary || "")}</textarea>
      </div>
      ${LIST_FIELDS.map(
        (key) => `
        <div class="field full">
          <label>${esc(label(key))}</label>
          <textarea class="textarea" name="${key}" rows="3" placeholder="One entry per line">${esc(
            listOf(r, key).join("\n")
          )}</textarea>
          <span class="hint">One entry per line</span>
        </div>`
      ).join("")}`;

    modal({
      title: `Edit ${r.full_name || r.filename || "résumé"}`,
      size: "lg",
      body: form,
      actions: [
        { label: "Cancel", onClick: (close) => close() },
        {
          label: "Save changes",
          variant: "primary",
          onClick: async (close, btn) => {
            btn.classList.add("loading");
            const data = new FormData(form);
            const payload = {};

            TEXT_FIELDS.forEach((key) => {
              const value = (data.get(key) || "").trim();
              payload[key] = value || null;
            });
            LIST_FIELDS.forEach((key) => {
              const lines = String(data.get(key) || "")
                .split("\n").map((l) => l.trim()).filter(Boolean);
              payload[key] = lines.length ? lines : null;
            });

            try {
              const res = await http.post(`/resume/${id}`, payload);
              toast(res && res.message ? res.message : "Résumé updated", "success");
              close();
              load();
            } catch (err) {
              toast(err.message, "error");
            } finally {
              btn.classList.remove("loading");
            }
          },
        },
      ],
    });
  }

  async function removeResume(id) {
    const r = resumes.find((x) => x.pdf_id === id);
    const ok = await UI.confirm({
      title: "Delete this résumé?",
      message: `${r ? r.full_name || r.filename : "The résumé"} and its stored PDF will be removed.`,
      confirmLabel: "Delete",
      danger: true,
    });
    if (!ok) return;
    try {
      const res = await http.del(`/resume/${id}`);
      toast(res && res.message ? res.message : "Résumé deleted", "success");
      load();
    } catch (err) {
      toast(err.message, "error");
    }
  }

  /* ---------------- upload ---------------- */
  async function upload(file) {
    if (!/\.pdf$/i.test(file.name)) {
      toast(`${file.name} is not a PDF`, "warn");
      return;
    }

    const chip = el("div", { class: "file-chip" });
    chip.innerHTML = `
      <div class="fi">${icon("file", 16)}</div>
      <div class="fbody">
        <div class="fname">${esc(file.name)}</div>
        <div class="fmeta">${esc(bytes(file.size))} · extracting…</div>
        <div class="progress-bar indeterminate mt-1"><span></span></div>
      </div>`;
    $("#queue").prepend(chip);

    const form = new FormData();
    form.append("file", file);

    try {
      const res = await http.post("/upload", form);
      const matched = ALL_FIELDS.filter((k) => {
        const v = res.metadata && res.metadata[k];
        return Array.isArray(v) ? v.length : !!v;
      }).length;

      chip.querySelector(".fmeta").textContent = `${bytes(file.size)} · ${matched} of ${ALL_FIELDS.length} fields matched`;
      chip.querySelector(".progress-bar").remove();
      const fi = chip.querySelector(".fi");
      fi.style.background = "var(--ok-soft)";
      fi.style.color = "var(--ok)";
      fi.innerHTML = icon("check", 16);

      toast(res.message || "Résumé parsed", "success");
      showLatest(res);
      load();
    } catch (err) {
      chip.querySelector(".fmeta").textContent = err.message;
      chip.querySelector(".fmeta").style.color = "var(--danger)";
      chip.querySelector(".progress-bar").remove();
      const fi = chip.querySelector(".fi");
      fi.style.background = "var(--danger-soft)";
      fi.style.color = "var(--danger)";
      fi.innerHTML = icon("alert", 16);
      toast(err.message, "error");
    }
  }

  function showLatest(res) {
    const r = Object.assign({ pdf_id: res.pdf_id }, res.metadata || {});
    $("#latest").innerHTML = detailHtml(r);
  }

  /* ---------------- boot ---------------- */
  function init() {
    UI.shell({ start: "overview" });

    $("#fieldTags").innerHTML = ALL_FIELDS.map(
      (key) => `<span class="tag">${icon(FIELD_ICONS[key] || "fileText", 13)} ${esc(label(key))}</span>`
    ).join("");

    UI.dropzone($("#dropzone"), (files) => [].concat(files).forEach(upload), {
      accept: "application/pdf",
      multiple: true,
    });

    $("#filter").addEventListener("input", debounce(renderTable, 180));
    $("#refresh").addEventListener("click", async (e) => {
      e.currentTarget.classList.add("loading");
      await Promise.all([ping(), load()]);
      e.currentTarget.classList.remove("loading");
      toast("Collection reloaded", "success");
    });

    ping();
    load();
  }

  document.addEventListener("DOMContentLoaded", init);
})();
