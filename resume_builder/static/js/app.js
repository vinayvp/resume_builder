/**
 * Resume Builder Frontend Application Logic
 */

document.addEventListener("DOMContentLoaded", () => {
  // Lucide Icons initialization
  if (window.lucide) {
    window.lucide.createIcons();
  }

  // State
  let currentToken = null;
  let currentResolvedFilename = "";
  let isCustomFilenameActive = false;
  let customFilenameOverride = null;
  let currentZoom = 100;

  // DOM Elements
  const companyInput = document.getElementById("companyName");
  const roleInput = document.getElementById("roleName");
  const lblFilenamePreview = document.getElementById("lblFilenamePreview");
  const btnEditFilename = document.getElementById("btnEditFilename");
  const saveDirectoryInput = document.getElementById("saveDirectory");

  const selTheme = document.getElementById("selTheme");
  const selFont = document.getElementById("selFont");
  const customFontInput = document.getElementById("customFontInput");
  const selPageSize = document.getElementById("selPageSize");
  const selPhoneFormat = document.getElementById("selPhoneFormat");
  const chkNoFooterNote = document.getElementById("chkNoFooterNote");
  const chkAllowPageBreak = document.getElementById("chkAllowPageBreak");

  const yamlEditor = document.getElementById("yamlEditor");
  const yamlLineCount = document.getElementById("yamlLineCount");
  const dropZone = document.getElementById("dropZone");
  const dropOverlay = document.getElementById("dropOverlay");
  const fileUploadInput = document.getElementById("fileUploadInput");
  const btnLoadSample = document.getElementById("btnLoadSample");
  const btnClearYaml = document.getElementById("btnClearYaml");
  const btnRenderResume = document.getElementById("btnRenderResume");
  const lblRenderBtnText = document.getElementById("lblRenderBtnText");

  const pipelineStatusBadge = document.getElementById("pipelineStatusBadge");
  const btnToggleCliLogs = document.getElementById("btnToggleCliLogs");
  const cliLogsPanel = document.getElementById("cliLogsPanel");
  const cliLogsContent = document.getElementById("cliLogsContent");
  const btnCopyLogs = document.getElementById("btnCopyLogs");

  const metricsReviewCard = document.getElementById("metricsReviewCard");
  const metricPageCount = document.getElementById("metricPageCount");
  const metricPageBadge = document.getElementById("metricPageBadge");
  const metricTotalWords = document.getElementById("metricTotalWords");
  const metricWordDensity = document.getElementById("metricWordDensity");
  const metricPageWords = document.getElementById("metricPageWords");
  const metricRenderTime = document.getElementById("metricRenderTime");
  const lblTargetLocation = document.getElementById("lblTargetLocation");
  const btnDownloadPdf = document.getElementById("btnDownloadPdf");
  const btnAcceptSave = document.getElementById("btnAcceptSave");

  const previewControls = document.getElementById("previewControls");
  const previewPageIndicator = document.getElementById("previewPageIndicator");
  const previewEmptyState = document.getElementById("previewEmptyState");
  const previewPagesContainer = document.getElementById("previewPagesContainer");
  const zoomLevel = document.getElementById("zoomLevel");
  const btnZoomIn = document.getElementById("btnZoomIn");
  const btnZoomOut = document.getElementById("btnZoomOut");
  const btnZoomFit = document.getElementById("btnZoomFit");

  const successModal = document.getElementById("successModal");
  const modalSavedPath = document.getElementById("modalSavedPath");
  const btnCopySavedPath = document.getElementById("btnCopySavedPath");
  const btnCloseModal = document.getElementById("btnCloseModal");
  const btnToggleTheme = document.getElementById("btnToggleTheme");

  // -------------------------------------------------------------
  // Theme Management (Light / Dark)
  // -------------------------------------------------------------
  const updateFavicon = (isDark) => {
    const fav = document.getElementById("faviconLink");
    if (fav) {
      fav.href = isDark ? "/static/img/favicon-dark.png" : "/static/img/favicon-light.png";
    }
  };

  const initTheme = () => {
    const savedTheme = localStorage.getItem("rb-theme");
    const isDark = savedTheme === "dark" || (!savedTheme && window.matchMedia("(prefers-color-scheme: dark)").matches);
    if (isDark) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
    updateFavicon(isDark);
  };
  initTheme();

  btnToggleTheme.addEventListener("click", () => {
    const isDark = document.documentElement.classList.toggle("dark");
    localStorage.setItem("rb-theme", isDark ? "dark" : "light");
    updateFavicon(isDark);
  });

  // -------------------------------------------------------------
  // Dynamic Filename Calculator
  // -------------------------------------------------------------
  const sanitizeName = (val) => {
    if (!val) return "";
    return val.trim().replace(/[\s\-]+/g, "_").replace(/[^\w]/g, "");
  };

  const updateFilenamePreview = () => {
    if (isCustomFilenameActive && customFilenameOverride) {
      currentResolvedFilename = customFilenameOverride;
      lblFilenamePreview.textContent = currentResolvedFilename;
      return;
    }

    const role = sanitizeName(roleInput.value);
    const company = sanitizeName(companyInput.value);

    let name = "VinayakPastey_Resume";
    if (role && company) {
      name += `_${role}_${company}`;
    } else if (role) {
      name += `_${role}`;
    } else if (company) {
      name += `_${company}`;
    }
    name += ".pdf";

    currentResolvedFilename = name;
    lblFilenamePreview.textContent = name;
    lblFilenamePreview.title = name;
  };

  companyInput.addEventListener("input", () => {
    isCustomFilenameActive = false;
    updateFilenamePreview();
  });

  roleInput.addEventListener("input", () => {
    isCustomFilenameActive = false;
    updateFilenamePreview();
  });

  btnEditFilename.addEventListener("click", () => {
    const custom = prompt("Enter custom filename:", currentResolvedFilename);
    if (custom !== null && custom.trim() !== "") {
      let trimmed = custom.trim();
      if (!trimmed.toLowerCase().endsWith(".pdf")) trimmed += ".pdf";
      customFilenameOverride = trimmed;
      isCustomFilenameActive = true;
      updateFilenamePreview();
    }
  });

  updateFilenamePreview();

  // -------------------------------------------------------------
  // Font Selector Custom Input Handler
  // -------------------------------------------------------------
  selFont.addEventListener("change", () => {
    if (selFont.value === "__custom__") {
      customFontInput.style.display = "block";
      customFontInput.focus();
    } else {
      customFontInput.style.display = "none";
    }
  });

  const getSelectedFont = () => {
    if (selFont.value === "__custom__") {
      return customFontInput.value.trim() || "Calibri";
    }
    return selFont.value;
  };

  // -------------------------------------------------------------
  // YAML Editor Helper & Line Counter
  // -------------------------------------------------------------
  const updateLineCount = () => {
    const lines = yamlEditor.value.split("\n").length;
    yamlLineCount.textContent = `${lines} lines`;
  };

  yamlEditor.addEventListener("input", updateLineCount);

  // Tab key support in textarea
  yamlEditor.addEventListener("keydown", (e) => {
    if (e.key === "Tab") {
      e.preventDefault();
      const start = yamlEditor.selectionStart;
      const end = yamlEditor.selectionEnd;
      yamlEditor.value = yamlEditor.value.substring(0, start) + "  " + yamlEditor.value.substring(end);
      yamlEditor.selectionStart = yamlEditor.selectionEnd = start + 2;
      updateLineCount();
    } else if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      triggerRender();
    }
  });

  // -------------------------------------------------------------
  // Sample Loader & Clear
  // -------------------------------------------------------------
  const loadSampleYaml = async () => {
    try {
      btnLoadSample.disabled = true;
      btnLoadSample.innerHTML = '<span class="inline-block animate-spin mr-1">↻</span> Loading...';
      const res = await fetch("/api/sample");
      if (!res.ok) throw new Error("Failed to load sample resume");
      const data = await res.json();
      yamlEditor.value = data.yaml;
      updateLineCount();
    } catch (err) {
      alert("Error loading sample YAML: " + err.message);
    } finally {
      btnLoadSample.disabled = false;
      btnLoadSample.innerHTML = '<i data-lucide="file-code-2" class="w-3.5 h-3.5 mr-1"></i><span>Load Sample YAML</span>';
      if (window.lucide) window.lucide.createIcons();
    }
  };

  btnLoadSample.addEventListener("click", loadSampleYaml);

  btnClearYaml.addEventListener("click", () => {
    if (confirm("Reset YAML editor?")) {
      yamlEditor.value = "";
      updateLineCount();
      resetSteps();
    }
  });

  // -------------------------------------------------------------
  // Drag & Drop File Upload
  // -------------------------------------------------------------
  ["dragenter", "dragover"].forEach((eventName) => {
    dropZone.addEventListener(eventName, (e) => {
      e.preventDefault();
      dropOverlay.classList.remove("hidden");
    });
  });

  ["dragleave", "drop"].forEach((eventName) => {
    dropZone.addEventListener(eventName, (e) => {
      e.preventDefault();
      dropOverlay.classList.add("hidden");
    });
  });

  dropZone.addEventListener("drop", (e) => {
    const dt = e.dataTransfer;
    const file = dt.files[0];
    if (file) {
      readFile(file);
    }
  });

  fileUploadInput.addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (file) {
      readFile(file);
    }
  });

  const readFile = (file) => {
    const reader = new FileReader();
    reader.onload = (event) => {
      yamlEditor.value = event.target.result;
      updateLineCount();
    };
    reader.readAsText(file);
  };

  // -------------------------------------------------------------
  // Stepper Visual Management (1-Line Stepper)
  // -------------------------------------------------------------
  const stepTickerDot = document.getElementById("stepTickerDot");
  const stepTickerText = document.getElementById("stepTickerText");

  const resetSteps = () => {
    const stepIds = [
      "validate_input",
      "apply_design",
      "execute_cli",
      "analyze_metrics",
      "prepare_preview",
    ];

    stepIds.forEach((id, idx) => {
      const el = document.getElementById(`step-${id}`);
      if (el) {
        el.className = "step-pill flex items-center space-x-1.5 px-2 py-1 rounded-md bg-slate-200/70 dark:bg-slate-800 text-slate-500 text-[11px] font-medium transition-all";
        const icon = el.querySelector(".step-icon");
        if (icon) {
          icon.className = "step-icon w-4 h-4 rounded-full bg-slate-300 dark:bg-slate-700 text-slate-600 dark:text-slate-300 flex items-center justify-center text-[10px]";
          icon.innerHTML = (idx + 1).toString();
        }
      }
      const line = document.getElementById(`step-line-${idx + 1}`);
      if (line) {
        line.className = "flex-1 h-0.5 min-w-[6px] bg-slate-200 dark:bg-slate-700 transition-colors";
      }
    });

    if (stepTickerText) stepTickerText.textContent = "Ready to render";
    if (stepTickerDot) stepTickerDot.className = "w-2 h-2 rounded-full bg-slate-400 flex-shrink-0";
    if (pipelineStatusBadge) {
      pipelineStatusBadge.textContent = "Idle";
      pipelineStatusBadge.className = "inline-flex items-center px-2 py-0.2 text-[10px] font-medium rounded-full bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400";
    }
    if (metricsReviewCard) metricsReviewCard.classList.add("hidden");
    if (previewControls) previewControls.classList.add("opacity-40", "pointer-events-none");
    if (previewPagesContainer) previewPagesContainer.classList.add("hidden");
    if (previewEmptyState) previewEmptyState.classList.remove("hidden");
    if (previewPageIndicator) previewPageIndicator.textContent = "No document rendered";
  };

  const updateStepUI = (step, idx) => {
    const el = document.getElementById(`step-${step.id}`);
    if (!el) return;

    const icon = el.querySelector(".step-icon");

    if (step.status === "completed") {
      el.className = "step-pill flex items-center space-x-1.5 px-2 py-1 rounded-md bg-emerald-100 dark:bg-emerald-950/70 text-emerald-800 dark:text-emerald-200 text-[11px] font-semibold border border-emerald-300 dark:border-emerald-800/60 transition-all";
      if (icon) {
        icon.className = "step-icon w-4 h-4 rounded-full bg-emerald-500 text-white flex items-center justify-center text-[10px]";
        icon.innerHTML = '<i data-lucide="check" class="w-3 h-3"></i>';
      }
      const line = document.getElementById(`step-line-${idx + 1}`);
      if (line) {
        line.className = "flex-1 h-0.5 min-w-[6px] bg-emerald-500 transition-colors";
      }
      if (stepTickerText) {
        stepTickerText.textContent = `✓ Step ${idx + 1}: ${step.name} (${step.duration_ms || 0} ms)`;
      }
      if (stepTickerDot) {
        stepTickerDot.className = "w-2 h-2 rounded-full bg-emerald-500 flex-shrink-0";
      }
    } else if (step.status === "running") {
      el.className = "step-pill flex items-center space-x-1.5 px-2 py-1 rounded-md bg-emerald-500 text-white text-[11px] font-semibold shadow-sm transition-all animate-pulse";
      if (icon) {
        icon.className = "step-icon w-4 h-4 rounded-full bg-white text-emerald-700 flex items-center justify-center text-[10px] animate-spin";
        icon.innerHTML = '<i data-lucide="loader-2" class="w-3 h-3"></i>';
      }
      if (stepTickerText) {
        stepTickerText.textContent = `Running ${step.name}...`;
      }
      if (stepTickerDot) {
        stepTickerDot.className = "w-2 h-2 rounded-full bg-emerald-500 flex-shrink-0 animate-ping";
      }
    } else if (step.status === "failed") {
      el.className = "step-pill flex items-center space-x-1.5 px-2 py-1 rounded-md bg-red-100 dark:bg-red-950 text-red-700 dark:text-red-300 text-[11px] font-semibold border border-red-300 dark:border-red-800 transition-all";
      if (icon) {
        icon.className = "step-icon w-4 h-4 rounded-full bg-red-500 text-white flex items-center justify-center text-[10px]";
        icon.innerHTML = '<i data-lucide="x" class="w-3 h-3"></i>';
      }
      if (stepTickerText) {
        stepTickerText.textContent = `✗ ${step.name} failed: ${step.message || 'Error'}`;
      }
      if (stepTickerDot) {
        stepTickerDot.className = "w-2 h-2 rounded-full bg-red-500 flex-shrink-0";
      }
    }

    if (window.lucide) window.lucide.createIcons();
  };

  // -------------------------------------------------------------
  // CLI Logs Toggle
  // -------------------------------------------------------------
  btnToggleCliLogs.addEventListener("click", () => {
    cliLogsPanel.classList.toggle("hidden");
  });

  btnCopyLogs.addEventListener("click", () => {
    navigator.clipboard.writeText(cliLogsContent.textContent);
    btnCopyLogs.textContent = "Copied!";
    setTimeout(() => {
      btnCopyLogs.textContent = "Copy Logs";
    }, 2000);
  });

  // -------------------------------------------------------------
  // Render Resume Trigger
  // -------------------------------------------------------------
  const triggerRender = async () => {
    const yamlContent = yamlEditor.value.trim();
    if (!yamlContent) {
      alert("Please enter or load a YAML resume first.");
      return;
    }

    resetSteps();
    btnRenderResume.disabled = true;
    lblRenderBtnText.textContent = "Rendering...";
    pipelineStatusBadge.textContent = "Executing...";
    pipelineStatusBadge.className = "inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 animate-pulse";

    const payload = {
      yaml_content: yamlContent,
      company_name: companyInput.value.trim(),
      role_name: roleInput.value.trim(),
      custom_filename: isCustomFilenameActive ? customFilenameOverride : null,
      save_directory: saveDirectoryInput.value.trim(),
      design: {
        theme: selTheme.value,
        font_family: getSelectedFont(),
        page_size: selPageSize.value,
        no_footer_or_top_note: chkNoFooterNote.checked,
        phone_number_format: selPhoneFormat.value,
        allow_page_break_in_entries: chkAllowPageBreak.checked,
      },
    };

    try {
      const res = await fetch("/api/render", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await res.json();

      // Update CLI logs
      if (data.cli_logs) {
        cliLogsContent.textContent = data.cli_logs;
      }

      // Update Steps
      if (data.steps && data.steps.length) {
        data.steps.forEach((step, idx) => {
          updateStepUI(step, idx);
        });
      }

      if (!data.success) {
        pipelineStatusBadge.textContent = "Failed";
        pipelineStatusBadge.className = "inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-300";
        cliLogsPanel.classList.remove("hidden");
        alert("Render Error: " + (data.error || "Execution failed. Check CLI logs."));
        return;
      }

      currentToken = data.token;
      currentResolvedFilename = data.resolved_filename || currentResolvedFilename;
      lblFilenamePreview.textContent = currentResolvedFilename;

      pipelineStatusBadge.textContent = "Rendered";
      pipelineStatusBadge.className = "inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300";

      // -------------------------------------------------------------
      // Populate Metrics
      // -------------------------------------------------------------
      if (data.metrics) {
        const pages = data.metrics.page_count;
        const totalWords = data.metrics.total_words;

        metricPageCount.textContent = pages;
        if (pages === 1) {
          metricPageBadge.textContent = "Single Page";
          metricPageBadge.className = "inline-block mt-1 text-[10px] font-medium px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300";
        } else {
          metricPageBadge.textContent = `${pages} Pages`;
          metricPageBadge.className = "inline-block mt-1 text-[10px] font-medium px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300";
        }

        metricTotalWords.textContent = totalWords.toLocaleString();
        const avgWords = Math.round(totalWords / Math.max(pages, 1));
        metricWordDensity.textContent = `~${avgWords} words/page`;

        if (data.metrics.page_words && data.metrics.page_words.length) {
          const breakdown = data.metrics.page_words
            .map((w, idx) => `P${idx + 1}: ${w}w`)
            .join(" · ");
          metricPageWords.textContent = breakdown;
        }

        // Compute total pipeline render time from steps
        const totalTime = data.steps.reduce((acc, s) => acc + (s.duration_ms || 0), 0);
        metricRenderTime.textContent = `${Math.round(totalTime)} ms`;

        if (stepTickerText) {
          stepTickerText.textContent = `✓ Complete in ${Math.round(totalTime)} ms (${pages} pg, ${totalWords.toLocaleString()} words)`;
        }
        if (stepTickerDot) {
          stepTickerDot.className = "w-2 h-2 rounded-full bg-emerald-500 flex-shrink-0";
        }

        lblTargetLocation.textContent = `${saveDirectoryInput.value.trim()}/${currentResolvedFilename}`;
        btnDownloadPdf.href = data.pdf_preview_url;

        metricsReviewCard.classList.remove("hidden");
      }

      // -------------------------------------------------------------
      // Populate Preview Pages
      // -------------------------------------------------------------
      if (data.preview_urls && data.preview_urls.length) {
        previewPagesContainer.innerHTML = "";
        data.preview_urls.forEach((url, idx) => {
          const pageWrapper = document.createElement("div");
          pageWrapper.className = "relative flex flex-col items-center w-full max-w-[800px]";

          const pageHeader = document.createElement("div");
          pageHeader.className = "w-full flex items-center justify-between pb-1.5 px-1 text-[11px] text-slate-400 font-mono";
          pageHeader.innerHTML = `<span>Page ${idx + 1} of ${data.preview_urls.length}</span><span>${data.metrics?.page_words?.[idx] || 0} words</span>`;

          const img = document.createElement("img");
          img.src = `${url}?t=${Date.now()}`;
          img.alt = `Resume Page ${idx + 1}`;
          img.className = "resume-page-sheet w-full";

          pageWrapper.appendChild(pageHeader);
          pageWrapper.appendChild(img);
          previewPagesContainer.appendChild(pageWrapper);
        });

        previewEmptyState.classList.add("hidden");
        previewPagesContainer.classList.remove("hidden");
        previewControls.classList.remove("opacity-40", "pointer-events-none");
        previewPageIndicator.textContent = `${data.preview_urls.length} page(s) ready`;
        currentZoom = 100;
        applyZoom();
      }

    } catch (err) {
      pipelineStatusBadge.textContent = "Network Error";
      pipelineStatusBadge.className = "inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium bg-red-100 text-red-800";
      alert("Error invoking render: " + err.message);
    } finally {
      btnRenderResume.disabled = false;
      lblRenderBtnText.textContent = "Render Resume";
      if (window.lucide) window.lucide.createIcons();
    }
  };

  btnRenderResume.addEventListener("click", triggerRender);

  // -------------------------------------------------------------
  // Zoom Controls
  // -------------------------------------------------------------
  const applyZoom = () => {
    previewPagesContainer.style.transform = `scale(${currentZoom / 100})`;
    zoomLevel.textContent = `${currentZoom}%`;
  };

  btnZoomIn.addEventListener("click", () => {
    if (currentZoom < 180) {
      currentZoom += 15;
      applyZoom();
    }
  });

  btnZoomOut.addEventListener("click", () => {
    if (currentZoom > 50) {
      currentZoom -= 15;
      applyZoom();
    }
  });

  btnZoomFit.addEventListener("click", () => {
    currentZoom = 100;
    applyZoom();
  });

  // -------------------------------------------------------------
  // Acceptance & Save Workflow
  // -------------------------------------------------------------
  btnAcceptSave.addEventListener("click", async () => {
    if (!currentToken) {
      alert("No active rendered resume to save. Please click Render Resume first.");
      return;
    }

    const targetDir = saveDirectoryInput.value.trim();
    btnAcceptSave.disabled = true;
    btnAcceptSave.innerHTML = '<span class="inline-block animate-spin mr-1">↻</span> Saving...';

    try {
      const res = await fetch("/api/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          token: currentToken,
          custom_filename: currentResolvedFilename,
          save_directory: targetDir,
        }),
      });

      const data = await res.json();
      if (!res.ok || !data.success) {
        throw new Error(data.error || data.message || "Failed to save file.");
      }

      // Show success modal
      modalSavedPath.textContent = data.saved_path;
      successModal.classList.remove("hidden");

    } catch (err) {
      alert("Save Failed: " + err.message);
    } finally {
      btnAcceptSave.disabled = false;
      btnAcceptSave.innerHTML = '<i data-lucide="save" class="w-3.5 h-3.5 mr-1.5"></i><span>Accept & Save to Folder</span>';
      if (window.lucide) window.lucide.createIcons();
    }
  });

  // Modal actions
  btnCloseModal.addEventListener("click", () => {
    successModal.classList.add("hidden");
  });

  btnCopySavedPath.addEventListener("click", () => {
    navigator.clipboard.writeText(modalSavedPath.textContent.trim());
    btnCopySavedPath.textContent = "Copied!";
    setTimeout(() => {
      btnCopySavedPath.textContent = "Copy File Path";
    }, 2000);
  });

  // Auto-load sample resume on initial page load for convenience
  loadSampleYaml();
});

