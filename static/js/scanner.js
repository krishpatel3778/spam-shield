(() => {
  const input = document.getElementById("emailText");
  const count = document.getElementById("charCount");
  const scanButton = document.getElementById("scanButton");
  const clearButton = document.getElementById("clearButton");
  const status = document.getElementById("scanStatus");
  const result = document.getElementById("scanResult");
  if (!input) return;
  input.addEventListener("input", () => { count.textContent = `${input.value.length} / 20000`; });
  clearButton.addEventListener("click", () => { input.value = ""; count.textContent = "0 / 20000"; status.textContent = ""; result.classList.add("hidden"); input.focus(); });
  scanButton.addEventListener("click", async () => {
    const text = input.value.trim(); result.classList.add("hidden");
    if (!text) { status.textContent = "Paste an email or message before scanning."; input.focus(); return; }
    scanButton.disabled = true; scanButton.innerHTML = '<span class="spinner"></span> Analysing message…'; status.textContent = "Checking the message for patterns. Please wait.";
    try {
      const response = await fetch("/predict", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text }) });
      const data = await response.json(); if (!response.ok) throw new Error(data.error || "Scan failed. Please try again.");
      const spam = data.prediction === "SPAM";
      document.getElementById("resultTitle").textContent = data.title;
      document.getElementById("resultClass").textContent = data.prediction;
      document.getElementById("resultStatus").textContent = spam ? "WARNING SIGNS FOUND" : "NO SPAM PATTERN FOUND";
      const symbol = document.getElementById("resultSymbol"); symbol.textContent = spam ? "!" : "✓"; symbol.className = "result-symbol " + (spam ? "symbol-spam" : "symbol-safe");
      document.getElementById("resultTitle").className = spam ? "title-spam" : "title-safe";
      document.getElementById("resultMessage").textContent = data.message;
      document.getElementById("riskValue").textContent = `${data.risk_score}%`;
      document.getElementById("riskLevel").textContent = `${data.risk_level} INDICATOR`;
      document.getElementById("riskBar").style.width = `${data.risk_score}%`;
      document.getElementById("modelName").textContent = data.model; document.getElementById("urlCount").textContent = String(data.url_count || 0);
      document.getElementById("recommendedAction").textContent = data.recommended_action;
      document.getElementById("ifInteracted").textContent = data.if_interacted;
      document.getElementById("modelSignals").textContent = data.model_signals;
      document.getElementById("riskNote").textContent = data.risk_note; document.getElementById("privacyNote").textContent = data.privacy;
      const list = document.getElementById("analysisList"); list.replaceChildren();
      if (data.analysis && data.analysis.length) data.analysis.forEach(signal => {
        const card = document.createElement("article"); card.className = "insight-card";
        const heading = document.createElement("h4"); heading.textContent = signal.title;
        const why = document.createElement("p"); why.textContent = signal.why;
        const match = document.createElement("small"); match.textContent = `Text matched: ${signal.matched_text}`;
        card.append(heading, why, match); list.appendChild(card);
      }); else {
        const card = document.createElement("article"); card.className = "insight-card insight-empty";
        const heading = document.createElement("h4"); heading.textContent = "No configured warning phrases found";
        const why = document.createElement("p"); why.textContent = "The model may still identify other patterns. Check the sender address, context, and any links yourself.";
        card.append(heading, why); list.appendChild(card);
      }
      result.classList.remove("hidden"); status.textContent = `Analysis complete using ${data.model}.`; result.scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (error) { status.textContent = error.message; }
    finally { scanButton.disabled = false; scanButton.innerHTML = 'Analyse message <span>↗</span>'; }
  });
})();