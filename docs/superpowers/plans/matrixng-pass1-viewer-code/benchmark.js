/**
 * benchmark.js — Benchmark tab rendering.
 * Metrics table and criteria detail view.
 */
(() => {
	var MV = (window.MatrixViewer = window.MatrixViewer || {});

	MV.renderBenchmark = () => {
		var data = MV.getState().data;
		if (!data || !data.benchmark) return;

		renderMetricsTable(document.getElementById("metrics-panel"), data);
		renderCriteriaDetail(document.getElementById("criteria-panel"), data);
	};

	// --- Metrics Table ---

	function renderMetricsTable(container, data) {
		var bm = data.benchmark;
		if (!bm.configurations || bm.configurations.length === 0) {
			container.innerHTML = "<p>No benchmark data available.</p>";
			return;
		}

		var html = '<table class="metrics-table">';
		html += "<thead><tr>";
		html +=
			"<th>Configuration</th><th>Eval</th><th>Pass Rate</th><th>Tokens</th><th>Duration</th>";
		html += "</tr></thead><tbody>";

		bm.configurations.forEach((config) => {
			// Per-eval rows
			config.evals.forEach((ev) => {
				html += "<tr>";
				html += `<td>${escapeHtml(config.name)}</td>`;
				html += `<td>${escapeHtml(ev.eval_name)}</td>`;
				html +=
					'<td class="' +
					passRateClass(ev.pass_rate) +
					'">' +
					(ev.pass_rate * 100).toFixed(0) +
					"%</td>";
				html += `<td>${formatNumber(ev.tokens)}</td>`;
				html += `<td>${ev.duration_seconds.toFixed(1)}s</td>`;
				html += "</tr>";
			});

			// Aggregate row
			var agg = config.aggregate;
			html += '<tr class="aggregate-row">';
			html += `<td>${escapeHtml(config.name)}</td>`;
			html += "<td><em>Aggregate</em></td>";
			html +=
				'<td class="' +
				passRateClass(agg.mean_pass_rate) +
				'">' +
				(agg.mean_pass_rate * 100).toFixed(0) +
				"%</td>";
			html += `<td>${formatNumber(agg.mean_tokens)}</td>`;
			html += `<td>${agg.mean_duration_seconds.toFixed(1)}s</td>`;
			html += "</tr>";
		});

		// Delta row
		if (bm.delta && Object.keys(bm.delta).length > 0) {
			html += '<tr class="aggregate-row" style="background:#f0fff0">';
			html += '<td colspan="2"><strong>Delta (skill vs baseline)</strong></td>';
			html += `<td>${escapeHtml(bm.delta.pass_rate || "")}</td>`;
			html += `<td>${escapeHtml(bm.delta.tokens || "")}</td>`;
			html += `<td>${escapeHtml(bm.delta.duration || "")}</td>`;
			html += "</tr>";
		}

		html += "</tbody></table>";

		// Analysis observations
		if (bm.analysis?.observations && bm.analysis.observations.length > 0) {
			html += '<h3 style="margin-top:20px">Analysis</h3><ul>';
			bm.analysis.observations.forEach((obs) => {
				html += `<li>${escapeHtml(obs)}</li>`;
			});
			html += "</ul>";
		}

		container.innerHTML = html;
	}

	// --- Criteria Detail ---

	function renderCriteriaDetail(container, data) {
		var html = "";

		// Filter buttons
		html += '<div class="criteria-filters">';
		["all", "structural", "quality", "behavioral"].forEach((type) => {
			var label = type.charAt(0).toUpperCase() + type.slice(1);
			html +=
				'<button class="' +
				(type === "all" ? "active" : "") +
				'" data-filter="' +
				type +
				'">' +
				label +
				"</button>";
		});
		html += "</div>";

		// Grouped by eval
		data.evals.forEach((ev) => {
			html += '<div class="criteria-group">';
			html += `<h3>${formatEvalName(ev.evalName)}</h3>`;

			var grading = ev.configurations.with_skill.grading;
			if (!grading || !grading.expectations) {
				html += "<p>No grading data.</p></div>";
				return;
			}

			grading.expectations.forEach((exp, idx) => {
				// Find the matching assertion to get its type
				var assertion = ev.assertions.find((a) => a.text === exp.text);
				var type = assertion ? assertion.type : "quality";

				html += `<div class="criteria-item" data-type="${type}">`;
				html += `<span class="criteria-badge ${exp.passed ? "pass" : "fail"}">`;
				html += exp.passed ? "\u2713" : "\u2717";
				html += "</span>";
				html += "<div>";
				html +=
					"<div>" +
					escapeHtml(exp.text) +
					' <span style="color:#999;font-size:11px">(' +
					type +
					")</span></div>";
				html += `<div class="criteria-evidence" id="evidence-${ev.evalId}-${idx}">`;
				html += escapeHtml(exp.evidence);
				html += "</div>";
				html += "</div>";
				html += "</div>";
			});

			html += "</div>";
		});

		container.innerHTML = html;

		// Wire up filter buttons
		container.querySelectorAll(".criteria-filters button").forEach((btn) => {
			btn.addEventListener("click", () => {
				container.querySelectorAll(".criteria-filters button").forEach((b) => {
					b.classList.remove("active");
				});
				btn.classList.add("active");
				var filter = btn.dataset.filter;
				container.querySelectorAll(".criteria-item").forEach((item) => {
					if (filter === "all" || item.dataset.type === filter) {
						item.style.display = "";
					} else {
						item.style.display = "none";
					}
				});
			});
		});

		// Wire up evidence expand/collapse
		container.querySelectorAll(".criteria-item").forEach((item) => {
			item.addEventListener("click", () => {
				var evidence = item.querySelector(".criteria-evidence");
				if (evidence) evidence.classList.toggle("expanded");
			});
		});
	}

	// --- Helpers ---

	function passRateClass(rate) {
		if (rate >= 0.8) return "pass-high";
		if (rate >= 0.5) return "pass-mid";
		return "pass-low";
	}

	function formatNumber(n) {
		if (n >= 1000) return `${(n / 1000).toFixed(1)}k`;
		return n.toString();
	}

	function formatEvalName(name) {
		return name.replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
	}

	function escapeHtml(text) {
		if (!text) return "";
		return String(text)
			.replace(/&/g, "&amp;")
			.replace(/</g, "&lt;")
			.replace(/>/g, "&gt;");
	}
})();
