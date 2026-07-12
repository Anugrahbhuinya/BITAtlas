import { useState, useEffect, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import adminApi from "../services/api";
import { useAdminStore } from "../hooks/adminStore";
import { DashboardCard } from "../components/DashboardCard";
import { 
  Save, 
  FileText, 
  Trash2, 
  Layers, 
  Copy, 
  Eye, 
  EyeOff, 
  Tag, 
  Clock, 
  User, 
  CheckCircle, 
  ChevronLeft,
  Loader2,
  Sparkles
} from "lucide-react";

export const AdminKnowledgeEditorPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { showToast } = useAdminStore();
  
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [publishing, setPublishing] = useState(false);
  const [previewMode, setPreviewMode] = useState(false);
  
  // Form fields
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [category, setCategory] = useState("Other");
  const [department, setDepartment] = useState("");
  const [tagsInput, setTagsInput] = useState("");
  const [tags, setTags] = useState<string[]>([]);
  const [priority, setPriority] = useState(3);
  const [expiryDate, setExpiryDate] = useState("");
  const [author, setAuthor] = useState("admin");
  const [status, setStatus] = useState("draft");
  const [version, setVersion] = useState(1);
  const [originalFilename, setOriginalFilename] = useState<string | null>(null);
  
  const autoSaveTimer = useRef<any>(null);
  const isDirty = useRef(false);

  const categories = [
    "Academic", "Notice", "Event", "Department", "Hostel", "Placement", 
    "Club", "Faculty", "Library", "Transport", "Policy", "Admission", 
    "Scholarship", "FAQ", "Research", "Other"
  ];

  // Fetch existing item if ID present
  useEffect(() => {
    if (id) {
      const fetchItem = async () => {
        setLoading(true);
        try {
          const response = await adminApi.get(`/api/admin/knowledge/${id}`);
          const item = response.data;
          setTitle(item.title);
          setContent(item.content);
          setCategory(item.category);
          setDepartment(item.department || "");
          setTags(item.tags || []);
          setTagsInput(item.tags ? item.tags.join(", ") : "");
          setPriority(item.priority || 3);
          setAuthor(item.author || "admin");
          setStatus(item.status || "draft");
          setVersion(item.version || 1);
          setOriginalFilename(item.original_filename);
          if (item.expires_at) {
            setExpiryDate(new Date(item.expires_at).toISOString().split("T")[0]);
          }
        } catch (e: any) {
          showToast(e.response?.data?.detail || "Failed to load knowledge item", "error");
          navigate("/admin/knowledge-base");
        } finally {
          setLoading(false);
        }
      };
      fetchItem();
    } else {
      const savedUser = localStorage.getItem("bit_admin_username") || "admin";
      setAuthor(savedUser);
    }
  }, [id]);

  // Sync tags input
  useEffect(() => {
    const parsed = tagsInput
      .split(",")
      .map(t => t.trim())
      .filter(t => t.length > 0);
    setTags(parsed);
  }, [tagsInput]);

  // Auto save draft logic
  useEffect(() => {
    if (status === "draft" && id && isDirty.current) {
      if (autoSaveTimer.current) clearTimeout(autoSaveTimer.current);
      autoSaveTimer.current = setTimeout(() => {
        handleSaveDraft(true);
      }, 15000); // Auto-save draft every 15s if dirty
    }
    return () => {
      if (autoSaveTimer.current) clearTimeout(autoSaveTimer.current);
    };
  }, [title, content, category, department, tags, priority, expiryDate, status]);

  const handleSaveDraft = async (isAuto = false) => {
    if (!title.trim() || !content.trim()) {
      if (!isAuto) showToast("Title and content are required to save draft.", "error");
      return;
    }
    
    setSaving(true);
    const payload = {
      title,
      content,
      category,
      department,
      tags,
      priority,
      author,
      status: "draft",
      expires_at: expiryDate ? new Date(expiryDate).toISOString() : null
    };

    try {
      if (id) {
        await adminApi.put(`/api/admin/knowledge/${id}`, payload);
        isDirty.current = false;
        if (!isAuto) showToast("Draft saved successfully.", "success");
      } else {
        const res = await adminApi.post("/api/admin/knowledge", payload);
        isDirty.current = false;
        showToast("Draft created successfully.", "success");
        navigate(`/admin/knowledge/editor/${res.data._id}`);
      }
    } catch (e: any) {
      console.error(e);
      if (!isAuto) showToast(e.response?.data?.detail || "Failed to save draft", "error");
    } finally {
      setSaving(false);
    }
  };

  const handlePublish = async () => {
    if (!title.trim() || !content.trim()) {
      showToast("Title and content are required to publish.", "error");
      return;
    }

    setPublishing(true);
    const payload = {
      title,
      content,
      category,
      department,
      tags,
      priority,
      author,
      status: "published",
      expires_at: expiryDate ? new Date(expiryDate).toISOString() : null
    };

    try {
      if (id) {
        const response = await adminApi.put(`/api/admin/knowledge/${id}`, payload);
        setStatus("published");
        setVersion(response.data.version);
        showToast("Knowledge published and vector indexes updated successfully.", "success");
      } else {
        const response = await adminApi.post("/api/admin/knowledge", payload);
        showToast("Knowledge published and vector indexes updated successfully.", "success");
        navigate(`/admin/knowledge/editor/${response.data._id}`);
      }
      isDirty.current = false;
    } catch (e: any) {
      showToast(e.response?.data?.detail || "Failed to publish knowledge", "error");
    } finally {
      setPublishing(false);
    }
  };

  const handleDelete = async () => {
    if (!id) return;
    if (window.confirm("Are you sure you want to permanently delete this knowledge item? All version snapshots and ChromaDB vector chunks will be deleted.")) {
      try {
        await adminApi.delete(`/api/admin/knowledge/${id}`);
        showToast("Knowledge item deleted successfully.", "success");
        navigate("/admin/knowledge-base");
      } catch (e: any) {
        showToast(e.response?.data?.detail || "Failed to delete item", "error");
      }
    }
  };

  const handleDuplicate = () => {
    // Navigate to new editor with duplicated fields
    navigate("/admin/knowledge/editor", {
      state: {
        title: `${title} (Copy)`,
        content,
        category,
        department,
        tags,
        priority,
        expiryDate
      }
    });
    showToast("Duplicated document fields populated.", "info");
  };

  // Populate duplicated fields if navigated via duplicate state
  useEffect(() => {
    if (!id && window.history.state?.usr) {
      const dupe = window.history.state.usr;
      if (dupe.title) {
        setTitle(dupe.title);
        setContent(dupe.content || "");
        setCategory(dupe.category || "Other");
        setDepartment(dupe.department || "");
        setTags(dupe.tags || []);
        setTagsInput(dupe.tags ? dupe.tags.join(", ") : "");
        setPriority(dupe.priority || 3);
        setExpiryDate(dupe.expiryDate || "");
      }
    }
  }, [id]);

  const addFormatting = (marker: string, placeholder = "") => {
    const textarea = document.getElementById("editor-textarea") as HTMLTextAreaElement;
    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const text = textarea.value;
    const selected = text.substring(start, end) || placeholder;

    let replacement = "";
    if (marker === "bold") replacement = `**${selected}**`;
    else if (marker === "italic") replacement = `*${selected}*`;
    else if (marker === "heading") replacement = `\n### ${selected}\n`;
    else if (marker === "bullet") replacement = `\n- ${selected}\n`;
    else if (marker === "code") replacement = `\`${selected}\``;

    const newContent = text.substring(0, start) + replacement + text.substring(end);
    setContent(newContent);
    isDirty.current = true;
    
    // Reset focus & selection
    setTimeout(() => {
      textarea.focus();
      textarea.setSelectionRange(start + marker.length + 1, start + marker.length + 1 + selected.length);
    }, 50);
  };

  // Convert markdown to HTML (basic implementation for premium look without huge libraries)
  const renderMarkdownHtml = (mdText: string) => {
    if (!mdText) return "<p class='text-slate-500 italic'>No content written yet.</p>";
    
    let html = mdText
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
      
    // Headings
    html = html.replace(/^### (.*?)$/gm, "<h4 class='text-md font-bold text-slate-100 mt-4 mb-2'>$1</h4>");
    html = html.replace(/^## (.*?)$/gm, "<h3 class='text-lg font-bold text-slate-100 mt-5 mb-2 border-b border-slate-800 pb-1'>$1</h3>");
    html = html.replace(/^# (.*?)$/gm, "<h2 class='text-xl font-bold text-slate-100 mt-6 mb-3'>$1</h2>");
    
    // Bold & Italic
    html = html.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    html = html.replace(/\*(.*?)\*/g, "<em>$1</em>");
    
    // Inline code
    html = html.replace(/`(.*?)`/g, "<code class='bg-slate-900 border border-slate-800 px-1 rounded text-red-400 font-mono text-[11px]'>$1</code>");
    
    // Bullet lists
    html = html.replace(/^\- (.*?)$/gm, "<li class='list-disc list-inside text-xs text-slate-300 ml-4 my-1'>$1</li>");
    
    // Paragraphs
    html = html.replace(/^(?!<[a-z])(.*?)$/gm, "<p class='text-xs text-slate-300 leading-relaxed my-2'>$1</p>");
    
    return html;
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-[50vh] gap-4">
        <Loader2 className="w-8 h-8 text-primary animate-spin" />
        <span className="text-sm text-slate-400">Loading editor workspace...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top action bar */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div className="flex items-center gap-3">
          <button 
            onClick={() => navigate("/admin/knowledge-base")}
            className="p-2 hover:bg-surface-container rounded-xl border border-outline-variant text-slate-400 hover:text-slate-200 transition-colors"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <div>
            <h2 className="text-xl font-bold text-slate-100 tracking-tight">
              {id ? `Edit KMS Knowledge: v${version}` : "KMS Editor"}
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              {status === "published" ? "🔴 Live and index-searchable" : "🟡 Offline Draft Document"}
            </p>
          </div>
        </div>

        {/* Action button row */}
        <div className="flex flex-wrap items-center gap-2">
          {id && (
            <button
              onClick={() => navigate(`/admin/knowledge/versions/${id}`)}
              className="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 text-xs font-semibold rounded-xl flex items-center gap-2 transition-colors cursor-pointer"
            >
              <Layers className="w-3.5 h-3.5" />
              <span>Versions</span>
            </button>
          )}
          {id && (
            <button
              onClick={handleDuplicate}
              className="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 text-xs font-semibold rounded-xl flex items-center gap-2 transition-colors cursor-pointer"
            >
              <Copy className="w-3.5 h-3.5" />
              <span>Duplicate</span>
            </button>
          )}
          {id && (
            <button
              onClick={handleDelete}
              className="px-3 py-1.5 bg-red-950/20 hover:bg-red-950/40 border border-red-500/20 text-red-300 text-xs font-semibold rounded-xl flex items-center gap-2 transition-colors cursor-pointer"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Delete</span>
            </button>
          )}
          <button
            onClick={() => setPreviewMode(!previewMode)}
            className="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 text-xs font-semibold rounded-xl flex items-center gap-2 transition-colors cursor-pointer"
          >
            {previewMode ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
            <span>{previewMode ? "Edit Mode" : "Preview"}</span>
          </button>
          <button
            onClick={() => handleSaveDraft()}
            disabled={saving}
            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-xl flex items-center gap-2 transition-colors cursor-pointer disabled:opacity-50"
          >
            {saving ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Save className="w-3.5 h-3.5" />}
            <span>Save Draft</span>
          </button>
          <button
            onClick={handlePublish}
            disabled={publishing}
            className="px-4 py-1.5 bg-primary text-background text-xs font-bold rounded-xl flex items-center gap-2 shadow-lg transition-colors cursor-pointer disabled:opacity-50"
          >
            {publishing ? <Loader2 className="w-3.5 h-3.5 animate-spin text-background" /> : <CheckCircle className="w-3.5 h-3.5" />}
            <span>Publish Index</span>
          </button>
        </div>
      </div>

      {/* Main Workspace split */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Editor form card */}
        <div className={`${previewMode ? "lg:col-span-1" : "lg:col-span-2"} space-y-6 transition-all duration-300`}>
          <DashboardCard title="Document Metadata" subtitle="Core classification fields">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
              <div>
                <label className="text-[10px] uppercase font-bold text-slate-400 block mb-1">Title</label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => { setTitle(e.target.value); isDirty.current = true; }}
                  placeholder="Enter a clear title..."
                  className="w-full bg-slate-950/60 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-primary"
                />
              </div>

              <div>
                <label className="text-[10px] uppercase font-bold text-slate-400 block mb-1">Category</label>
                <select
                  value={category}
                  onChange={(e) => { setCategory(e.target.value); isDirty.current = true; }}
                  className="w-full bg-slate-950/60 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-primary"
                >
                  {categories.map((cat) => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-[10px] uppercase font-bold text-slate-400 block mb-1">Department</label>
                <input
                  type="text"
                  value={department}
                  onChange={(e) => { setDepartment(e.target.value); isDirty.current = true; }}
                  placeholder="e.g. CSE, ECE, Accounts..."
                  className="w-full bg-slate-950/60 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-primary"
                />
              </div>

              <div>
                <label className="text-[10px] uppercase font-bold text-slate-400 block mb-1">Tags (comma separated)</label>
                <input
                  type="text"
                  value={tagsInput}
                  onChange={(e) => { setTagsInput(e.target.value); isDirty.current = true; }}
                  placeholder="e.g. Exam, AI, Placement..."
                  className="w-full bg-slate-950/60 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-primary"
                />
              </div>

              <div>
                <label className="text-[10px] uppercase font-bold text-slate-400 block mb-1">Priority (1-5, 5 highest)</label>
                <input
                  type="number"
                  min="1"
                  max="5"
                  value={priority}
                  onChange={(e) => { setPriority(parseInt(e.target.value) || 3); isDirty.current = true; }}
                  className="w-full bg-slate-950/60 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-primary"
                />
              </div>

              <div>
                <label className="text-[10px] uppercase font-bold text-slate-400 block mb-1">Expiry Date</label>
                <input
                  type="date"
                  value={expiryDate}
                  onChange={(e) => { setExpiryDate(e.target.value); isDirty.current = true; }}
                  className="w-full bg-slate-950/60 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-primary"
                />
              </div>
            </div>
          </DashboardCard>

          {/* Form Content body editor */}
          {!previewMode && (
            <DashboardCard title="Document Content" subtitle="Markdown formatting supported">
              <div className="space-y-4 pt-2">
                {/* Editor Tool buttons */}
                <div className="flex flex-wrap items-center gap-1.5 p-1.5 bg-slate-950/40 border border-slate-900 rounded-xl">
                  <button 
                    type="button"
                    onClick={() => addFormatting("bold", "bold text")}
                    className="p-1.5 hover:bg-slate-900 text-xs font-bold text-slate-400 hover:text-slate-200 rounded cursor-pointer"
                  >
                    B
                  </button>
                  <button 
                    type="button"
                    onClick={() => addFormatting("italic", "italic text")}
                    className="p-1.5 hover:bg-slate-900 text-xs italic text-slate-400 hover:text-slate-200 rounded cursor-pointer"
                  >
                    I
                  </button>
                  <button 
                    type="button"
                    onClick={() => addFormatting("heading", "Heading text")}
                    className="p-1.5 hover:bg-slate-900 text-[10px] text-slate-400 hover:text-slate-200 rounded cursor-pointer"
                  >
                    H3
                  </button>
                  <button 
                    type="button"
                    onClick={() => addFormatting("bullet", "list item")}
                    className="p-1.5 hover:bg-slate-900 text-[10px] text-slate-400 hover:text-slate-200 rounded cursor-pointer"
                  >
                    List
                  </button>
                  <button 
                    type="button"
                    onClick={() => addFormatting("code", "code snippet")}
                    className="p-1.5 hover:bg-slate-900 text-[10px] text-slate-400 hover:text-slate-200 rounded cursor-pointer font-mono"
                  >
                    Code
                  </button>
                </div>

                {/* Textarea */}
                <textarea
                  id="editor-textarea"
                  value={content}
                  onChange={(e) => { setContent(e.target.value); isDirty.current = true; }}
                  placeholder="Start typing your knowledge content using markdown..."
                  rows={15}
                  className="w-full bg-slate-950/60 border border-slate-800 rounded-2xl p-4 text-xs font-mono text-slate-300 leading-relaxed focus:outline-none focus:border-primary resize-y"
                />
              </div>
            </DashboardCard>
          )}
        </div>

        {/* Live Preview panel */}
        {(previewMode || content) && (
          <div className={`${previewMode ? "lg:col-span-2" : "lg:col-span-1"} space-y-6 transition-all duration-300`}>
            <DashboardCard 
              title="KMS Document Preview" 
              subtitle="Simulated rendering matching agent context format"
            >
              <div className="pt-2 space-y-4 select-none">
                {/* Meta details badge row */}
                <div className="flex flex-wrap gap-2">
                  <span className="text-[9px] font-bold px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-300 flex items-center gap-1">
                    <Layers className="w-2.5 h-2.5" />
                    {category}
                  </span>
                  {department && (
                    <span className="text-[9px] font-bold px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-300 flex items-center gap-1">
                      <Sparkles className="w-2.5 h-2.5" />
                      {department}
                    </span>
                  )}
                  {tags.map((tag) => (
                    <span key={tag} className="text-[9px] font-bold px-2 py-0.5 rounded bg-primary/10 border border-primary/20 text-primary flex items-center gap-1">
                      <Tag className="w-2.5 h-2.5" />
                      {tag}
                    </span>
                  ))}
                  {expiryDate && (
                    <span className="text-[9px] font-bold px-2 py-0.5 rounded bg-red-950/20 border border-red-500/20 text-red-300 flex items-center gap-1">
                      <Clock className="w-2.5 h-2.5" />
                      Expires: {expiryDate}
                    </span>
                  )}
                </div>

                {/* Simulated Citation block */}
                <div className="p-3 bg-slate-950 border border-slate-900 rounded-xl">
                  <span className="text-[10px] text-slate-500 font-semibold uppercase block">Assembled RAG Citation:</span>
                  <span className="text-[11px] text-primary block mt-1 font-mono break-all font-semibold">
                    [Source: {title || "Untitled"}, Type: Manual, Priority: {priority}, Author: {author}]
                  </span>
                </div>

                {/* Rendered HTML */}
                <div 
                  className="p-5 bg-slate-950/60 border border-slate-900/60 rounded-2xl overflow-y-auto max-h-[400px] prose prose-invert custom-scrollbar"
                  dangerouslySetInnerHTML={{ __html: renderMarkdownHtml(content) }}
                />
              </div>
            </DashboardCard>

            {/* Author summary panel */}
            <div className="glass-panel p-4 rounded-2xl border border-slate-800/40 space-y-3">
              <div className="flex items-center justify-between text-[11px] text-slate-400">
                <span className="flex items-center gap-1.5">
                  <User className="w-3.5 h-3.5 text-slate-500" />
                  <span>Author: <strong>{author}</strong></span>
                </span>
                <span className="flex items-center gap-1.5">
                  <FileText className="w-3.5 h-3.5 text-slate-500" />
                  <span>Version: <strong>{version}</strong></span>
                </span>
              </div>
              {originalFilename && (
                <div className="text-[10px] text-slate-500 border-t border-slate-900 pt-2 flex justify-between">
                  <span>Source File: <strong>{originalFilename}</strong></span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
