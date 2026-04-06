"use client";

import { useState, useCallback, useEffect, useRef } from "react";
import { useDropzone } from "react-dropzone";
import toast from "react-hot-toast";
import {
  Upload, FileText, Settings, Download, CheckCircle,
  AlertCircle, Loader2, BarChart3, RefreshCw, Zap,
  ChevronDown, ChevronUp, Database, TrendingUp,
  FileJson, FileSpreadsheet, File, ArrowRight,
} from "lucide-react";
import { uploadFile, getJob, getDownloadUrl } from "@/lib/api";
import { CleaningOptions, Job, JobSummary } from "@/types";

const defaultOptions: CleaningOptions = {
  remove_duplicates: true,
  missing_numeric: "median",
  missing_categorical: "unknown",
  normalize_types: true,
  handle_outliers: "clip",
  user_notes: "",
};

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [options, setOptions] = useState<CleaningOptions>(defaultOptions);
  const [jobId, setJobId] = useState<string | null>(null);
  const [job, setJob] = useState<Job | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [showStats, setShowStats] = useState(false);
  const pollRef = useRef<NodeJS.Timeout | null>(null);

  const onDrop = useCallback((accepted: File[]) => {
    if (accepted.length > 0) {
      const f = accepted[0];
      const ext = f.name.split(".").pop()?.toLowerCase();
      if (!["csv", "xlsx", "json"].includes(ext || "")) {
        toast.error("Only CSV, XLSX, and JSON files are supported.");
        return;
      }
      setFile(f);
      setJob(null);
      setJobId(null);
      toast.success(`File "${f.name}" selected!`);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "text/csv": [".csv"],
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
      "application/json": [".json"],
    },
    maxFiles: 1,
  });

  useEffect(() => {
    if (!jobId) return;
    if (job?.status === "completed" || job?.status === "failed") return;

    pollRef.current = setInterval(async () => {
      try {
        const updated = await getJob(jobId);
        setJob(updated);
        if (updated.status === "completed") {
          toast.success("Processing complete!");
          clearInterval(pollRef.current!);
        } else if (updated.status === "failed") {
          toast.error(`Processing failed: ${updated.error || "Unknown error"}`);
          clearInterval(pollRef.current!);
        }
      } catch {
        // ignore polling errors
      }
    }, 1500);

    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, [jobId, job?.status]);

  const handleSubmit = async () => {
    if (!file) {
      toast.error("Please select a file first.");
      return;
    }
    setIsUploading(true);
    try {
      const result = await uploadFile(file, options);
      setJobId(result.job_id);
      setJob({
        job_id: result.job_id,
        status: "pending",
        filename: result.filename,
        created_at: new Date().toISOString(),
        completed_at: null,
        error: null,
        summary: null,
      });
      toast.success("File uploaded! Processing started...");
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        "Upload failed";
      toast.error(msg);
    } finally {
      setIsUploading(false);
    }
  };

  const handleDownload = (format: "csv" | "xlsx" | "json" | "pdf") => {
    if (!jobId) return;
    const url = getDownloadUrl(jobId, format);
    const a = document.createElement("a");
    a.href = url;
    a.download = "";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  const summary: JobSummary | null | undefined = job?.summary;
  const rowsRemoved = summary ? summary.before.rows - summary.after.rows : 0;
  const totalMissingBefore = summary
    ? Object.values(summary.before.missing_by_column).reduce((a, b) => a + b, 0)
    : 0;
  const totalMissingAfter = summary
    ? Object.values(summary.after.missing_by_column).reduce((a, b) => a + b, 0)
    : 0;

  return (
    <div className="min-h-screen bg-dark-900 bg-grid-pattern bg-grid">
      {/* Ambient glow */}
      <div className="fixed top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-primary-500/10 blur-[120px] rounded-full pointer-events-none" />
      <div className="fixed bottom-0 right-0 w-[400px] h-[400px] bg-cyan-500/5 blur-[100px] rounded-full pointer-events-none" />

      {/* Header */}
      <header className="relative z-10 border-b border-white/5 glass">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-primary-500 flex items-center justify-center glow-purple">
              <Database className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-white">DataCleaner</h1>
              <p className="text-xs text-slate-400">AI-powered data pipeline</p>
            </div>
          </div>
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
            API Active
          </div>
        </div>
      </header>

      <main className="relative z-10 max-w-6xl mx-auto px-4 py-12">
        {/* Hero */}
        <div className="text-center mb-12 animate-fade-in">
          <div className="inline-flex items-center gap-2 bg-primary-500/10 border border-primary-500/30 rounded-full px-4 py-1.5 text-sm text-primary-400 mb-6">
            <Zap className="w-3.5 h-3.5" />
            No signup required · Free to use
          </div>
          <h2 className="text-4xl md:text-5xl font-extrabold text-white mb-4 leading-tight">
            Clean your data <span className="gradient-text">in seconds</span>
          </h2>
          <p className="text-slate-400 text-lg max-w-2xl mx-auto">
            Upload CSV, XLSX, or JSON files. Configure cleaning options. Download polished datasets + analysis reports.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left column: Upload + Options */}
          <div className="lg:col-span-2 space-y-6">
            {/* Upload Zone */}
            <div className="card animate-slide-up">
              <div className="flex items-center gap-2 mb-4">
                <Upload className="w-5 h-5 text-primary-400" />
                <h3 className="font-semibold text-white">Upload File</h3>
              </div>
              <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-all duration-200
                  ${isDragActive
                    ? "border-primary-400 bg-primary-500/10 scale-[1.01]"
                    : file
                    ? "border-green-500/50 bg-green-500/5"
                    : "border-slate-700 hover:border-primary-500/50 hover:bg-primary-500/5"
                  }`}
              >
                <input {...getInputProps()} />
                {file ? (
                  <div className="flex flex-col items-center gap-3">
                    <div className="w-12 h-12 rounded-xl bg-green-500/20 flex items-center justify-center">
                      <CheckCircle className="w-6 h-6 text-green-400" />
                    </div>
                    <div>
                      <p className="text-white font-medium">{file.name}</p>
                      <p className="text-slate-400 text-sm mt-1">
                        {(file.size / 1024).toFixed(1)} KB · Click to change
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="flex flex-col items-center gap-3">
                    <div className="w-12 h-12 rounded-xl bg-primary-500/20 flex items-center justify-center">
                      <Upload className="w-6 h-6 text-primary-400" />
                    </div>
                    <div>
                      <p className="text-white font-medium">
                        {isDragActive ? "Drop it here!" : "Drag & drop or click to upload"}
                      </p>
                      <p className="text-slate-400 text-sm mt-1">CSV, XLSX, JSON · Max 50MB</p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Cleaning Options */}
            <div className="card animate-slide-up" style={{ animationDelay: "0.1s" }}>
              <div className="flex items-center gap-2 mb-5">
                <Settings className="w-5 h-5 text-primary-400" />
                <h3 className="font-semibold text-white">Cleaning Options</h3>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                {/* Remove Duplicates */}
                <label className="flex items-center gap-3 cursor-pointer group">
                  <div
                    className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-all
                      ${options.remove_duplicates
                        ? "bg-primary-500 border-primary-500"
                        : "border-slate-600 group-hover:border-primary-500/50"
                      }`}
                    onClick={() => setOptions((o) => ({ ...o, remove_duplicates: !o.remove_duplicates }))}
                  >
                    {options.remove_duplicates && <CheckCircle className="w-3 h-3 text-white" />}
                  </div>
                  <span className="text-sm text-slate-300">Remove Duplicate Rows</span>
                </label>

                {/* Normalize Types */}
                <label className="flex items-center gap-3 cursor-pointer group">
                  <div
                    className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-all
                      ${options.normalize_types
                        ? "bg-primary-500 border-primary-500"
                        : "border-slate-600 group-hover:border-primary-500/50"
                      }`}
                    onClick={() => setOptions((o) => ({ ...o, normalize_types: !o.normalize_types }))}
                  >
                    {options.normalize_types && <CheckCircle className="w-3 h-3 text-white" />}
                  </div>
                  <span className="text-sm text-slate-300">Normalize Data Types</span>
                </label>

                {/* Missing Numeric */}
                <div>
                  <label className="block text-xs text-slate-400 mb-1.5">Numeric Missing Values</label>
                  <select
                    value={options.missing_numeric}
                    onChange={(e) =>
                      setOptions((o) => ({
                        ...o,
                        missing_numeric: e.target.value as CleaningOptions["missing_numeric"],
                      }))
                    }
                    className="w-full bg-[#1e293b] border border-slate-700 rounded-lg px-3 py-2 text-sm text-white
                               focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500/50 transition-all"
                  >
                    <option value="median">Fill with Median</option>
                    <option value="mean">Fill with Mean</option>
                    <option value="zero">Fill with Zero</option>
                    <option value="drop">Drop Rows</option>
                  </select>
                </div>

                {/* Missing Categorical */}
                <div>
                  <label className="block text-xs text-slate-400 mb-1.5">Categorical Missing Values</label>
                  <select
                    value={options.missing_categorical}
                    onChange={(e) =>
                      setOptions((o) => ({
                        ...o,
                        missing_categorical: e.target.value as CleaningOptions["missing_categorical"],
                      }))
                    }
                    className="w-full bg-[#1e293b] border border-slate-700 rounded-lg px-3 py-2 text-sm text-white
                               focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500/50 transition-all"
                  >
                    <option value="unknown">Fill with &quot;Unknown&quot;</option>
                    <option value="mode">Fill with Mode</option>
                    <option value="drop">Drop Rows</option>
                  </select>
                </div>

                {/* Outlier Handling */}
                <div className="md:col-span-2">
                  <label className="block text-xs text-slate-400 mb-1.5">Outlier Handling (IQR method)</label>
                  <div className="flex gap-3">
                    {(["none", "clip", "remove"] as const).map((val) => (
                      <button
                        key={val}
                        onClick={() => setOptions((o) => ({ ...o, handle_outliers: val }))}
                        className={`flex-1 py-2 rounded-lg text-sm font-medium border transition-all capitalize
                          ${options.handle_outliers === val
                            ? "bg-primary-500 border-primary-500 text-white"
                            : "bg-[#1e293b] border-slate-700 text-slate-400 hover:border-primary-500/50"
                          }`}
                      >
                        {val === "none" ? "No Handling" : val === "clip" ? "Clip (IQR)" : "Remove"}
                      </button>
                    ))}
                  </div>
                </div>

                {/* User Notes */}
                <div className="md:col-span-2">
                  <label className="block text-xs text-slate-400 mb-1.5">
                    What do you expect from this data? (optional)
                  </label>
                  <textarea
                    value={options.user_notes}
                    onChange={(e) => setOptions((o) => ({ ...o, user_notes: e.target.value }))}
                    placeholder="e.g., This is sales data for Q4. I want to identify top-performing products and remove outliers..."
                    rows={3}
                    className="w-full bg-[#1e293b] border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500
                               focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500/50 transition-all resize-none"
                  />
                </div>
              </div>

              {/* Submit */}
              <div className="mt-6">
                <button
                  onClick={handleSubmit}
                  disabled={
                    !file ||
                    isUploading ||
                    job?.status === "processing" ||
                    job?.status === "pending"
                  }
                  className="btn-primary w-full flex items-center justify-center gap-2 text-base"
                >
                  {isUploading || job?.status === "processing" || job?.status === "pending" ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      {isUploading ? "Uploading..." : "Processing..."}
                    </>
                  ) : (
                    <>
                      <Zap className="w-5 h-5" />
                      Clean My Data
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Right column: Status + Downloads */}
          <div className="space-y-6">
            {/* Status Card */}
            <div className="card animate-slide-up" style={{ animationDelay: "0.15s" }}>
              <div className="flex items-center gap-2 mb-4">
                <RefreshCw className="w-5 h-5 text-primary-400" />
                <h3 className="font-semibold text-white">Job Status</h3>
              </div>
              {!job ? (
                <div className="text-center py-8">
                  <div className="w-12 h-12 rounded-full bg-slate-800 flex items-center justify-center mx-auto mb-3">
                    <FileText className="w-6 h-6 text-slate-500" />
                  </div>
                  <p className="text-slate-500 text-sm">Upload a file to begin</p>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="flex items-center gap-3">
                    {job.status === "pending" && (
                      <Loader2 className="w-5 h-5 text-slate-400 animate-spin" />
                    )}
                    {job.status === "processing" && (
                      <Loader2 className="w-5 h-5 text-primary-400 animate-spin" />
                    )}
                    {job.status === "completed" && (
                      <CheckCircle className="w-5 h-5 text-green-400" />
                    )}
                    {job.status === "failed" && (
                      <AlertCircle className="w-5 h-5 text-red-400" />
                    )}
                    <div>
                      <p className="text-white text-sm font-medium capitalize">{job.status}</p>
                      <p className="text-slate-400 text-xs truncate max-w-[180px]">{job.filename}</p>
                    </div>
                  </div>

                  {/* Progress bar */}
                  <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-1000
                        ${job.status === "completed"
                          ? "w-full bg-green-400"
                          : job.status === "failed"
                          ? "w-full bg-red-400"
                          : job.status === "processing"
                          ? "w-2/3 bg-primary-400 animate-pulse"
                          : "w-1/4 bg-slate-600"
                        }`}
                    />
                  </div>

                  {job.status === "failed" && (
                    <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3">
                      <p className="text-red-400 text-xs">{job.error}</p>
                    </div>
                  )}

                  {job.status === "completed" && summary && (
                    <div className="grid grid-cols-2 gap-2 mt-2">
                      <div className="bg-[#1e293b] rounded-lg p-3 text-center">
                        <p className="text-primary-400 font-bold text-lg">
                          {summary.after.rows.toLocaleString()}
                        </p>
                        <p className="text-slate-400 text-xs">Clean rows</p>
                      </div>
                      <div className="bg-[#1e293b] rounded-lg p-3 text-center">
                        <p className="text-green-400 font-bold text-lg">
                          {summary.duplicates_removed}
                        </p>
                        <p className="text-slate-400 text-xs">Dupes removed</p>
                      </div>
                      <div className="bg-[#1e293b] rounded-lg p-3 text-center col-span-2">
                        <p className="text-yellow-400 font-bold text-lg">
                          {rowsRemoved.toLocaleString()}
                        </p>
                        <p className="text-slate-400 text-xs">Total rows removed</p>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Download Card */}
            {job?.status === "completed" && (
              <div className="card animate-slide-up">
                <div className="flex items-center gap-2 mb-4">
                  <Download className="w-5 h-5 text-primary-400" />
                  <h3 className="font-semibold text-white">Download</h3>
                </div>
                <div className="space-y-2">
                  {(
                    [
                      { format: "csv", label: "CSV", icon: FileText, color: "text-green-400" },
                      { format: "xlsx", label: "Excel", icon: FileSpreadsheet, color: "text-blue-400" },
                      { format: "json", label: "JSON", icon: FileJson, color: "text-yellow-400" },
                      { format: "pdf", label: "PDF Report", icon: File, color: "text-red-400" },
                    ] as const
                  ).map(({ format, label, icon: Icon, color }) => (
                    <button
                      key={format}
                      onClick={() => handleDownload(format)}
                      className="w-full flex items-center gap-3 bg-[#1e293b] hover:bg-[#334155] border border-slate-700 hover:border-primary-500/40
                                 rounded-xl px-4 py-3 transition-all group"
                    >
                      <Icon className={`w-4 h-4 ${color}`} />
                      <span className="text-sm text-slate-300 group-hover:text-white flex-1 text-left">
                        Download {label}
                      </span>
                      <Download className="w-4 h-4 text-slate-500 group-hover:text-primary-400 transition-colors" />
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Results Dashboard */}
        {job?.status === "completed" && summary && (
          <div className="mt-8 space-y-6 animate-slide-up">
            {/* Toggle */}
            <button
              onClick={() => setShowStats(!showStats)}
              className="w-full flex items-center justify-between glass rounded-2xl px-6 py-4 hover:border-primary-500/40 transition-all"
            >
              <div className="flex items-center gap-3">
                <BarChart3 className="w-5 h-5 text-primary-400" />
                <span className="font-semibold text-white">Analysis Results</span>
                <span className="bg-primary-500/20 text-primary-400 text-xs px-2 py-0.5 rounded-full">
                  {summary.steps.length} actions
                </span>
              </div>
              {showStats ? (
                <ChevronUp className="w-5 h-5 text-slate-400" />
              ) : (
                <ChevronDown className="w-5 h-5 text-slate-400" />
              )}
            </button>

            {showStats && (
              <div className="space-y-6">
                {/* Metrics Row */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {[
                    { label: "Rows Before", value: summary.before.rows.toLocaleString(), color: "text-slate-300" },
                    { label: "Rows After", value: summary.after.rows.toLocaleString(), color: "text-green-400" },
                    {
                      label: "Missing Resolved",
                      value: (totalMissingBefore - totalMissingAfter).toLocaleString(),
                      color: "text-cyan-400",
                    },
                    {
                      label: "Outliers Handled",
                      value: summary.outliers_handled.toLocaleString(),
                      color: "text-primary-400",
                    },
                  ].map((m) => (
                    <div key={m.label} className="card text-center">
                      <p className={`text-2xl font-bold ${m.color}`}>{m.value}</p>
                      <p className="text-slate-400 text-xs mt-1">{m.label}</p>
                    </div>
                  ))}
                </div>

                {/* Steps Applied */}
                {summary.steps.length > 0 && (
                  <div className="card">
                    <h4 className="font-semibold text-white mb-3 flex items-center gap-2">
                      <CheckCircle className="w-4 h-4 text-green-400" />
                      Cleaning Steps Applied
                    </h4>
                    <div className="space-y-2">
                      {summary.steps.map((step, i) => (
                        <div key={i} className="flex items-start gap-3 text-sm">
                          <span className="text-primary-400 font-mono text-xs mt-0.5">
                            {String(i + 1).padStart(2, "0")}
                          </span>
                          <span className="text-slate-300">{step}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Stats Table */}
                {Object.keys(summary.stats).length > 0 && (
                  <div className="card overflow-x-auto">
                    <h4 className="font-semibold text-white mb-3 flex items-center gap-2">
                      <TrendingUp className="w-4 h-4 text-primary-400" />
                      Numeric Column Statistics
                    </h4>
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-slate-700">
                          {["Column", "Mean", "Median", "Std", "Min", "Max"].map((h) => (
                            <th key={h} className="text-left text-slate-400 font-medium py-2 pr-4">
                              {h}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {Object.entries(summary.stats).map(([col, s]) => (
                          <tr key={col} className="border-b border-slate-800/50 hover:bg-slate-800/30">
                            <td className="py-2 pr-4 text-primary-300 font-medium">{col}</td>
                            <td className="py-2 pr-4 text-slate-300">{s.mean ?? "—"}</td>
                            <td className="py-2 pr-4 text-slate-300">{s.median ?? "—"}</td>
                            <td className="py-2 pr-4 text-slate-300">{s.std ?? "—"}</td>
                            <td className="py-2 pr-4 text-slate-300">{s.min ?? "—"}</td>
                            <td className="py-2 pr-4 text-slate-300">{s.max ?? "—"}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}

                {/* Correlations */}
                {summary.correlations.length > 0 && (
                  <div className="card">
                    <h4 className="font-semibold text-white mb-3 flex items-center gap-2">
                      <BarChart3 className="w-4 h-4 text-cyan-400" />
                      Top Feature Correlations
                    </h4>
                    <div className="space-y-2">
                      {summary.correlations.map((c, i) => (
                        <div key={i} className="flex items-center gap-3">
                          <div className="flex-1 flex items-center gap-2 min-w-0">
                            <span className="text-sm text-slate-300 truncate">{c.col1}</span>
                            <span className="text-slate-600 text-xs">↔</span>
                            <span className="text-sm text-slate-300 truncate">{c.col2}</span>
                          </div>
                          <div className="flex items-center gap-2 shrink-0">
                            <div className="w-24 h-1.5 bg-slate-800 rounded-full">
                              <div
                                className="h-full bg-primary-400 rounded-full"
                                style={{ width: `${c.correlation * 100}%` }}
                              />
                            </div>
                            <span className="text-xs text-primary-400 w-10 text-right font-mono">
                              {c.correlation}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Missing Values Map */}
                {Object.keys(summary.before.missing_by_column).some(
                  (k) => summary.before.missing_by_column[k] > 0
                ) && (
                  <div className="card">
                    <h4 className="font-semibold text-white mb-3 flex items-center gap-2">
                      <AlertCircle className="w-4 h-4 text-yellow-400" />
                      Missing Values: Before → After
                    </h4>
                    <div className="space-y-2">
                      {Object.entries(summary.before.missing_by_column)
                        .filter(([, v]) => v > 0)
                        .map(([col, before]) => {
                          const after = summary.after.missing_by_column[col] || 0;
                          return (
                            <div key={col} className="flex items-center gap-3 text-sm">
                              <span className="text-slate-300 flex-1 truncate">{col}</span>
                              <span className="text-red-400 font-mono">{before}</span>
                              <span className="text-slate-600">→</span>
                              <span className={`font-mono ${after === 0 ? "text-green-400" : "text-yellow-400"}`}>
                                {after}
                              </span>
                            </div>
                          );
                        })}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="relative z-10 border-t border-white/5 mt-20">
        <div className="max-w-6xl mx-auto px-4 py-8 text-center">
          <p className="text-slate-500 text-sm">
            DataCleaner MVP · Built for the modern data professional
          </p>
        </div>
      </footer>
    </div>
  );
}
