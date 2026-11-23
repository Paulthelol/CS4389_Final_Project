// Turns a raw Newman JSON report (which contains tokens and response bodies) into a safe summary.
// Usage: node sanitize-report.js <raw-newman-report.json> <evidence-dir>
const fs = require("fs");
const path = require("path");

const [rawPath, outDir] = process.argv.slice(2);
if (!rawPath || !outDir) {
  console.error("Usage: node sanitize-report.js <raw-newman-report.json> <evidence-dir>");
  process.exit(1);
}

const report = JSON.parse(fs.readFileSync(rawPath, "utf8"));

// Session and setup tokens are 43-character URL-safe strings; redact anything that long, plus raw SSNs.
const redact = (s) => String(s)
  .replace(/[A-Za-z0-9_-]{32,}/g, "[REDACTED]")
  .replace(/\b\d{3}-\d{2}-\d{4}\b/g, "[REDACTED-SSN]");

// Map each request in the collection to its folder, in collection order.
const order = [];
for (const folder of report.collection.item) {
  for (const item of folder.item || []) order.push({ id: item.id, folder: folder.name, name: item.name });
}

const executions = new Map(report.run.executions.map((e) => [e.item.id, e]));

const requests = order.map(({ id, folder, name }) => {
  const e = executions.get(id);
  if (!e || !e.response) {
    return { folder, name, result: "NOT RUN", note: "skipped or not executed" };
  }
  const assertions = (e.assertions || []).map((a) => ({
    name: a.assertion,
    result: a.error ? "FAIL" : "PASS",
    ...(a.error ? { error: redact(a.error.message) } : {}),
  }));
  const url = e.request.url;
  const query = (url.query || []).map((q) => q.key).join("&");
  return {
    folder,
    name,
    method: e.request.method,
    path: "/" + url.path.join("/") + (query ? "?" + query + "=..." : ""),
    status: e.response.code,
    result: assertions.some((a) => a.result === "FAIL") ? "FAIL" : "PASS",
    assertions,
  };
});

const count = (r) => requests.filter((x) => x.result === r).length;
const allAssertions = requests.flatMap((r) => r.assertions || []);
const summary = {
  collection: report.collection.info.name,
  started_at: new Date(report.run.timings.started).toISOString(),
  completed_at: new Date(report.run.timings.completed).toISOString(),
  totals: {
    requests: requests.length,
    passed: count("PASS"),
    failed: count("FAIL"),
    not_run: count("NOT RUN"),
    assertions: allAssertions.length,
    assertions_failed: allAssertions.filter((a) => a.result === "FAIL").length,
  },
  requests,
};

const t = summary.totals;
const md = [
  "# Customers API test summary",
  "",
  `Generated from a Newman run of \`${summary.collection}\`.`,
  "",
  `- Started: ${summary.started_at}`,
  `- Completed: ${summary.completed_at}`,
  `- Requests: ${t.requests} (PASS ${t.passed}, FAIL ${t.failed}, NOT RUN ${t.not_run})`,
  `- Assertions: ${t.assertions} (${t.assertions_failed} failed)`,
  "",
  "| Test | Method | Path | Status | Result |",
  "| :--- | :--- | :--- | ---: | :--- |",
  ...requests.map((r) => `| ${r.name} | ${r.method || ""} | \`${r.path || ""}\` | ${r.status || ""} | ${r.result} |`),
  "",
];
const failures = requests.filter((r) => r.result === "FAIL");
if (failures.length) {
  md.push("## Failures", "");
  for (const r of failures) {
    for (const a of r.assertions.filter((x) => x.result === "FAIL")) md.push(`- **${r.name}**: ${a.name} — ${a.error}`);
  }
  md.push("");
}
const json = JSON.stringify(summary, null, 2) + "\n";
const text = md.join("\n");

// Last line of defense: write nothing if anything token-like slipped through.
if (/Bearer |[A-Za-z0-9_-]{32,}/.test(json + text)) {
  console.error("Refusing to write evidence: output contains a token-like value.");
  process.exit(1);
}

fs.mkdirSync(outDir, { recursive: true });
fs.writeFileSync(path.join(outDir, "customers_test_results.json"), json);
fs.writeFileSync(path.join(outDir, "customers_test_summary.md"), text);

console.log(`PASS ${t.passed} / FAIL ${t.failed} / NOT RUN ${t.not_run} (assertions failed: ${t.assertions_failed})`);
