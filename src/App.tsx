import { useState, useEffect } from "react";
import { 
  Terminal, 
  Database, 
  Cpu, 
  HelpCircle, 
  RefreshCw, 
  BookOpen, 
  Send, 
  Sparkles, 
  CheckCircle2, 
  AlertCircle, 
  Code,
  Layers,
  ChevronRight,
  ClipboardCheck,
  Clipboard,
  Folder,
  FileCode,
  Play
} from "lucide-react";
import { motion, AnimatePresence } from "motion/react";

interface Source {
  title: string;
  score: number;
  snippet: string;
}

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
  steps_taken?: string[];
  processing_time_ms?: number;
  model_used?: string;
}

interface StatsObj {
  total_documents_indexed: number;
  vector_store_size_mb: number;
}

interface HealthObj {
  status: string;
  version: string;
  vector_store: string;
}

export default function App() {
  const [question, setQuestion] = useState("");
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  
  // Real-time server statuses
  const [stats, setStats] = useState<StatsObj>({ total_documents_indexed: 12453, vector_store_size_mb: 45.2 });
  const [health, setHealth] = useState<HealthObj | null>(null);
  
  // Active selection trace details
  const [selectedMsgIndex, setSelectedMsgIndex] = useState<number | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  // Suggested pre-coded questions for high testing accessibility
  const presetQuestions = [
    { label: "Pandas CSV", value: "How do I read a CSV file using pandas?" },
    { label: "List vs Tuple", value: "What is the difference between a list and a tuple in Python?" },
    { label: "SQLite Connect", value: "How to connect to a SQLite database using Python?" },
    { label: "GIL Multithreading", value: "What is the GIL in Python and how does it affect multithreading?" },
    { label: "Exception handling", value: "How do I handle exceptions in Python?" },
    { label: "Unpacking Dicts", value: "How to merge two dictionaries in Python 3?" }
  ];

  // Fetch telemetry & system state
  useEffect(() => {
    async function fetchSystemData() {
      try {
        const [healthRes, statsRes] = await Promise.all([
          fetch("/api/health"),
          fetch("/api/stats")
        ]);
        if (healthRes.ok) {
          const val = await healthRes.json();
          setHealth(val);
        }
        if (statsRes.ok) {
          const val = await statsRes.json();
          setStats(val);
        }
      } catch (err) {
        console.error("Error communicating with full-stack endpoints:", err);
      }
    }
    fetchSystemData();
  }, []);

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 1800);
  };

  const handleAsk = async (queryText: string) => {
    const trimmed = queryText.trim();
    if (!trimmed || isLoading) return;

    setIsLoading(true);
    setQuestion("");

    // Create unique ID for state logging
    const userMsgId = `usr-${Date.now()}`;
    const botMsgId = `bot-${Date.now()}`;

    const newUserMsg: ChatMessage = {
      id: userMsgId,
      role: "user",
      content: trimmed
    };

    setChatHistory(prev => [...prev, newUserMsg]);

    try {
      const response = await fetch("/api/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: trimmed, chat_history: [] })
      });

      if (!response.ok) {
        throw new Error("HTTP exception resolved as non-healthy.");
      }

      const resData = await response.json();
      
      const newBotMsg: ChatMessage = {
        id: botMsgId,
        role: "assistant",
        content: resData.answer,
        sources: resData.sources,
        steps_taken: resData.steps_taken,
        processing_time_ms: resData.processing_time_ms,
        model_used: resData.model_used
      };

      setChatHistory(prev => [...prev, newBotMsg]);
      // Focus on this newly created message
      setSelectedMsgIndex(chatHistory.length + 1);

    } catch (error) {
      console.error(error);
      const newBotMsg: ChatMessage = {
        id: botMsgId,
        role: "assistant",
        content: "I ran into an issue connecting with the generative service model. Please verify your `GEMINI_API_KEY` has been correctly loaded in the **Secrets** panel.",
        steps_taken: ["classify_question", "fallback"],
        model_used: "local-grounding-cache"
      };
      setChatHistory(prev => [...prev, newBotMsg]);
      setSelectedMsgIndex(chatHistory.length + 1);
    } finally {
      setIsLoading(false);
    }
  };

  const selectedMsg = selectedMsgIndex !== null && chatHistory[selectedMsgIndex] 
    ? chatHistory[selectedMsgIndex] 
    : (chatHistory.filter(m => m.role === "assistant").slice(-1)[0] || null);

  // Pre-renders Python statements and inline codes cleanly for the IDE look
  const renderMessageContent = (content: string) => {
    const parts = content.split(/(```python|```py|```javascript|```js|```json|```bash|```)/gi);
    let isCode = false;
    return parts.map((part, i) => {
      if (part.startsWith("```")) {
        isCode = !isCode;
        return null; // hide wrapper boundaries
      }
      if (isCode) {
        return (
          <pre key={i} className="bg-black p-3.5 rounded border border-gray-800 text-emerald-400 font-mono text-xs my-3 overflow-x-auto select-text whitespace-pre">
            <code>{part}</code>
          </pre>
        );
      }
      // Simple inline code highlighting inside backticks `code`
      const inlineParts = part.split(/`([^`]+)`/g);
      return (
        <span key={i} className="line-clamp-none whitespace-pre-wrap">
          {inlineParts.map((sub, idx) => {
            if (idx % 2 === 1) {
              return (
                <code key={idx} className="bg-gray-800 text-emerald-400 font-mono text-xs px-1.5 py-0.5 rounded border border-gray-700/60 font-medium">
                  {sub}
                </code>
              );
            }
            return sub;
          })}
        </span>
      );
    });
  };

  // Safe checks for the reactive node statuses
  const stepsTaken = selectedMsg?.steps_taken || [];
  const nodeClassifyActive = stepsTaken.includes("classify_question") || isLoading;
  const nodeRetrieveActive = stepsTaken.includes("retrieve_context");
  const nodeGenerateActive = stepsTaken.includes("generate_answer");
  const nodeFallbackActive = stepsTaken.includes("fallback");

  return (
    <div className="flex flex-col h-screen overflow-hidden text-sm bg-[#101112] text-gray-300 font-sans antialiased selection:bg-emerald-500/35 selection:text-white">
      
      {/* ─── Header Section (Height-14, Black backdrop, Emerald labels) ─── */}
      <header className="h-14 border-b border-gray-800 flex items-center justify-between px-6 bg-black flex-shrink-0 select-none">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-emerald-500 rounded flex items-center justify-center font-bold text-black font-mono tracking-tight text-sm shadow-[0_0_15px_rgba(16,185,129,0.2)]">
            PY
          </div>
          <div>
            <h1 className="font-bold text-gray-100 flex items-center gap-2 text-sm leading-tight">
              Python Q&A Assistant
              <span className="text-[10px] font-mono leading-none bg-emerald-950/40 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded-full uppercase tracking-wider">
                Agentic
              </span>
            </h1>
            <p className="text-[11px] text-gray-500">RAG + LangGraph State Orchestrator</p>
          </div>
        </div>

        <div className="flex items-center gap-6 text-xs font-mono">
          <div className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${health?.status === "healthy" ? "bg-emerald-400 animate-pulse" : "bg-amber-400"}`}></span>
            <span className="text-gray-400">
              {health ? `v${health.version} ${health.status.toUpperCase()}` : "CONNECTING ENGINE..."}
            </span>
          </div>
          <div className="hidden sm:flex items-center gap-2 border-l border-gray-800 pl-6">
            <span className="text-gray-500">PROVIDER:</span>
            <span className="text-emerald-400 uppercase">GEMINI</span>
          </div>
        </div>
      </header>

      {/* ─── Outer Shell Grid containing the 3 Panes ─── */}
      <div className="flex-1 flex overflow-hidden w-full">
        
        {/* ─── SIDEBAR LEFT: Project Explorer & Local Store Statistics ─── */}
        <aside className="w-64 border-r border-gray-800 bg-black overflow-hidden hidden md:flex flex-col flex-shrink-0 select-none">
          {/* Section: Project Explorer mock view */}
          <div className="p-4 border-b border-gray-800">
            <h3 className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-3 flex items-center gap-1.5">
              <Folder className="w-3.5 h-3.5 text-gray-400" />
              Project Explorer
            </h3>
            
            <div className="space-y-1 font-mono text-xs text-gray-400 leading-relaxed">
              <div className="flex items-center gap-1.5 text-emerald-400/95 font-medium">
                <span>▼</span>
                <span>/python-qa-assistant</span>
              </div>
              <div className="pl-4 py-0.5 text-gray-400 flex items-center gap-1.5">
                <span>└─</span>
                <span className="text-gray-500">app/</span>
                <span className="text-[10px] bg-gray-900 px-1 py-0.2 rounded border border-gray-800 text-gray-400">api/</span>
              </div>
              <div className="pl-8 py-0.5 text-gray-500 flex items-center gap-1.5 hover:text-gray-300 cursor-pointer">
                <span>├─</span>
                <span>routes.py</span>
              </div>
              <div className="pl-4 py-0.5 text-emerald-400 flex items-center gap-1.5 font-medium">
                <span>├─</span>
                <span>agent/</span>
                <span className="text-[9px] bg-emerald-950/40 text-emerald-400 border border-emerald-500/25 px-1 rounded font-bold uppercase tracking-tight">Active</span>
              </div>
              <div className="pl-8 py-0.5 text-gray-200 flex items-center gap-1.5 font-mono">
                <span>└─</span>
                <span>graph.py</span>
              </div>
              <div className="pl-4 py-0.5 text-gray-400 flex items-center gap-1.5">
                <span>├─</span>
                <span className="text-gray-500">rag/</span>
              </div>
              <div className="pl-4 py-0.5 text-gray-500">
                <span>└─ tests/</span>
              </div>

              <div className="mt-4 pt-4 border-t border-gray-900 text-gray-500 space-y-1">
                <div className="flex items-center gap-1.5 hover:text-gray-400 cursor-pointer">
                  <FileCode className="w-3 h-3 text-gray-500" />
                  <span>Dockerfile</span>
                </div>
                <div className="flex items-center gap-1.5 hover:text-gray-400 cursor-pointer">
                  <FileCode className="w-3 h-3 text-gray-500" />
                  <span>render.yaml</span>
                </div>
              </div>
            </div>
          </div>

          {/* Section: Local Vector Store statistics footprint */}
          <div className="p-4 flex-1 flex flex-col justify-end bg-gradient-to-t from-gray-950/60 to-transparent">
            <h3 className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-3 flex items-center gap-1.5">
              <Database className="w-3.5 h-3.5 text-emerald-400" />
              Vector Index
            </h3>
            
            <div className="bg-[#141516] rounded-lg p-3.5 border border-gray-800/80 space-y-3.5 shadow-md">
              <div className="space-y-1">
                <div className="flex justify-between text-[11px] font-mono leading-none">
                  <span className="text-gray-500">INDEXED CORPUS</span>
                  <span className="text-emerald-400 font-bold">{stats.total_documents_indexed.toLocaleString()} Docs</span>
                </div>
                <div className="w-full bg-gray-900 h-1 rounded-full overflow-hidden">
                  <div className="bg-emerald-500 h-full w-[82%] rounded-full shadow-[0_0_8px_#10b981]"></div>
                </div>
              </div>

              <div className="flex justify-between items-center text-[11px] font-mono border-t border-gray-900 pt-2.5 leading-none">
                <span className="text-gray-500">DISK FOOTPRINT</span>
                <span className="text-emerald-400 font-bold">{stats.vector_store_size_mb} MB</span>
              </div>
            </div>
          </div>
        </aside>

        {/* ─── MIDDLE MAIN SECTION: Interative message list & input footer ─── */}
        <main className="flex-1 flex flex-col bg-[#101112] overflow-hidden">
          
          {/* Scrollable messages panel */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin">
            
            {chatHistory.length === 0 ? (
              <div className="max-w-2xl mx-auto h-full flex flex-col items-center justify-center text-center p-6 bg-black/20 border border-gray-800/40 rounded-xl space-y-4">
                <BookOpen className="w-10 h-10 text-emerald-500/30" />
                <div>
                  <h3 className="text-gray-200 font-bold text-md">Begin Grounded Learning</h3>
                  <p className="text-xs text-gray-500 max-w-md mt-1.5 leading-relaxed">
                    Type a query or select a popular preloaded prompt in the system explorer to run the full FastAPI, SQLite & Chroma RAG workflow.
                  </p>
                </div>
              </div>
            ) : (
              <div className="max-w-3xl mx-auto w-full space-y-6">
                {chatHistory.map((msg, idx) => (
                  <motion.div
                    key={msg.id}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.2 }}
                    className="flex gap-4 items-start"
                  >
                    {/* Role Avatar Badge */}
                    {msg.role === "user" ? (
                      <div className="w-8 h-8 rounded bg-gray-800 flex-shrink-0 flex items-center justify-center font-bold font-mono text-xs border border-gray-700 text-gray-200 select-none">
                        US
                      </div>
                    ) : (
                      <div className="w-8 h-8 rounded bg-emerald-600 flex-shrink-0 flex items-center justify-center font-bold font-mono text-xs text-black shadow-[0_0_10px_rgba(16,185,129,0.3)] select-none">
                        AI
                      </div>
                    )}

                    {/* Chat Bubble card container matching High Density look */}
                    <div
                      onClick={() => {
                        if (msg.role === "assistant") {
                          setSelectedMsgIndex(idx);
                        }
                      }}
                      className={`flex-1 p-4 rounded-lg rounded-tl-none border cursor-pointer transition-all ${
                        msg.role === "user"
                          ? "bg-gray-800/50 border-gray-700/80 hover:border-gray-600/80 text-gray-200"
                          : `bg-black/40 ${
                              selectedMsgIndex === idx || (selectedMsgIndex === null && idx === chatHistory.length - 1)
                                ? "border-emerald-500/40 shadow-emerald-500/5 ring-1 ring-emerald-500/20"
                                : "border-gray-800 hover:border-gray-700"
                            }`
                      }`}
                    >
                      {/* Bubble Text Body */}
                      <div className="text-xs text-gray-400 font-mono mb-1.5 flex items-center justify-between select-none">
                        <span>{msg.role === "user" ? "USER INQUIRY" : "AGENTIC RESOLUTION"}</span>
                        {msg.model_used && (
                          <span className="text-[10px] bg-emerald-950/30 text-emerald-400 px-1.5 rounded">{msg.model_used}</span>
                        )}
                      </div>

                      <div className="text-gray-100 text-sm leading-relaxed antialiased font-sans">
                        {msg.role === "assistant" ? renderMessageContent(msg.content) : msg.content}
                      </div>

                      {/* Bot response actions box */}
                      {msg.role === "assistant" && (
                        <div className="mt-4 pt-3 border-t border-gray-800/60 flex items-center justify-between text-[10px] text-gray-500 font-mono select-none">
                          <div className="flex items-center gap-3">
                            {msg.processing_time_ms && (
                              <span>LATENCY: {msg.processing_time_ms}ms</span>
                            )}
                            {msg.sources && msg.sources.length > 0 && (
                              <span className="text-emerald-400 bg-emerald-950/20 border border-emerald-500/10 px-1 py-0.2 rounded font-bold">
                                CITATIONS: {msg.sources.length}
                              </span>
                            )}
                          </div>
                          
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleCopy(msg.id, msg.content);
                            }}
                            className="flex items-center gap-1 hover:text-emerald-400 hover:bg-gray-900 border border-gray-800 px-2 py-1 rounded transition-colors"
                          >
                            {copiedId === msg.id ? (
                              <>
                                <ClipboardCheck className="w-3 h-3 text-emerald-400 text-xs" />
                                <span className="text-emerald-400 font-medium">Copied!</span>
                              </>
                            ) : (
                              <>
                                <Clipboard className="w-3 h-3 text-xs" />
                                <span>Copy Code</span>
                              </>
                            )}
                          </button>
                        </div>
                      )}

                    </div>
                  </motion.div>
                ))}
              </div>
            )}

            {isLoading && (
              <div className="max-w-3xl mx-auto flex gap-4 items-start">
                <div className="w-8 h-8 rounded bg-emerald-600/50 flex-shrink-0 flex items-center justify-center font-bold font-mono text-xs text-black animate-pulse">
                  AI
                </div>
                <div className="flex-1 bg-black/20 border border-gray-800 p-4 rounded-lg rounded-tl-none flex items-center gap-3">
                  <RefreshCw className="w-4 h-4 animate-spin text-emerald-400" />
                  <span className="text-xs text-gray-400 font-mono">Running Node Graph trace... Calling retrieval models</span>
                </div>
              </div>
            )}

          </div>

          {/* Quick preset triggers row */}
          <div className="px-6 py-2 bg-black/20 border-t border-gray-900 flex items-center gap-3 flex-shrink-0 select-none">
            <span className="text-[10px] text-gray-500 font-bold tracking-widest uppercase flex-shrink-0">
              Preset prompts:
            </span>
            <div className="flex gap-2 overflow-x-auto py-1 scrollbar-none">
              {presetQuestions.map((pt, idx) => (
                <button
                  key={idx}
                  onClick={() => handleAsk(pt.value)}
                  className="text-[11px] whitespace-nowrap bg-black/60 hover:bg-emerald-950/20 border border-gray-850 hover:border-emerald-500/30 text-gray-400 hover:text-emerald-400 px-2.5 py-1 rounded transition-all flex items-center gap-1"
                >
                  <Play className="w-2.5 h-2.5 text-emerald-400" />
                  {pt.label}
                </button>
              ))}
            </div>
          </div>

          {/* Core high density bottom prompt bar (Height-20, Black overlay, Emerald actions) */}
          <div className="h-20 bg-black border-t border-gray-800 p-4 flex items-center gap-4 flex-shrink-0 select-none">
            <form 
              onSubmit={(e) => {
                e.preventDefault();
                handleAsk(question);
              }}
              className="w-full max-w-4xl mx-auto flex gap-4"
            >
              <input
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask a Python programming question (e.g., lists vs tuples details)..."
                className="flex-1 bg-[#101112] border border-gray-700 rounded px-4 py-2.5 text-sm text-gray-200 placeholder-gray-500 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500/20 transition-all font-mono"
              />
              <button
                type="submit"
                disabled={isLoading || !question.trim()}
                className="bg-emerald-600 hover:bg-emerald-500 disabled:bg-gray-800 disabled:text-gray-500 disabled:cursor-not-allowed text-black font-semibold tracking-wide px-6 py-2 rounded font-mono transition-colors shadow-lg flex items-center gap-1"
              >
                ASK
              </button>
            </form>
          </div>

        </main>

        {/* ─── SIDEBAR RIGHT: Graph trace execution state, Real-time telemetry, & Grounded citations ─── */}
        <aside className="w-80 border-l border-gray-800 bg-black p-4 flex flex-col gap-4 overflow-y-auto flex-shrink-0 select-none">
          
          {/* Module 1: Graph Flow Engine Visual trace */}
          <div className="border border-gray-850 bg-gray-950/40 p-4 rounded-lg flex flex-col">
            <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-4 flex items-center gap-1.5 font-mono">
              <Layers className="w-3.5 h-3.5 text-emerald-400" />
              Agent Workflow Nodes
            </h3>

            {/* Vertical Flow lines representing High Density node graphs */}
            <div className="relative py-1 flex flex-col items-center gap-3">
              
              {/* Node 1: classify_question */}
              <div className={`w-40 h-8 border rounded flex items-center justify-center text-[10px] font-mono transition-all duration-300 ${
                nodeClassifyActive 
                  ? "border-emerald-500 bg-emerald-500/10 text-emerald-400 font-semibold shadow-[0_0_8px_rgba(16,185,129,0.15)]" 
                  : "border-gray-850 bg-gray-900/40 text-gray-500"
              }`}>
                {nodeClassifyActive ? "●" : "○"} classify_question
              </div>
              
              <div className={`w-px h-4 transition-colors ${nodeRetrieveActive ? "bg-emerald-500" : "bg-gray-850"}`}></div>

              {/* Node 2: retrieve_context */}
              <div className={`w-40 h-8 border rounded flex items-center justify-center text-[10px] font-mono transition-all duration-300 ${
                nodeRetrieveActive 
                  ? "border-emerald-500 bg-emerald-500/10 text-emerald-400 font-semibold shadow-[0_0_8px_rgba(16,185,129,0.15)]" 
                  : "border-gray-850 bg-gray-900/40 text-gray-500"
              }`}>
                {nodeRetrieveActive ? "●" : "○"} retrieve_context
              </div>

              <div className={`w-px h-4 transition-colors ${nodeGenerateActive ? "bg-emerald-500" : "bg-gray-850"}`}></div>

              {/* Node 3: generate_answer */}
              <div className={`w-40 h-8 border rounded flex items-center justify-center text-[10px] font-mono transition-all duration-300 ${
                nodeGenerateActive 
                  ? "border-emerald-500 bg-emerald-500/10 text-emerald-400 font-semibold shadow-[0_0_8px_rgba(16,185,129,0.15)]" 
                  : "border-gray-850 bg-gray-900/40 text-gray-500"
              }`}>
                {nodeGenerateActive ? "●" : "○"} generate_answer
              </div>

              {/* Fallback edge when invalid question gets classified */}
              {nodeFallbackActive && (
                <div className="mt-2 flex flex-col items-center">
                  <div className="w-px h-4 bg-amber-500"></div>
                  <div className="w-40 h-8 border border-amber-500 bg-amber-500/10 rounded flex items-center justify-center text-[10px] font-mono text-amber-400 font-semibold shadow-[0_0_8px_rgba(245,158,11,0.15)]">
                    ▲ fallback_node
                  </div>
                </div>
              )}

            </div>
          </div>

          {/* Module 2: Grounded Citations match list */}
          <div className="flex-1 border border-gray-850 bg-gray-950/40 p-4 rounded-lg flex flex-col overflow-hidden">
            <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-3 flex items-center gap-1.5 font-mono">
              <Database className="w-3.5 h-3.5 text-emerald-400" />
              Retrieved Sources
            </h3>

            {selectedMsg && selectedMsg.sources && selectedMsg.sources.length > 0 ? (
              <div className="space-y-2 overflow-y-auto pr-1 flex-1 scrollbar-none">
                {selectedMsg.sources.map((src, idx) => (
                  <div key={idx} className="bg-black/40 p-2.5 border border-gray-850 rounded text-[11px] leading-tight space-y-1 hover:border-gray-700 transition">
                    <div className="flex justify-between gap-1 items-center font-mono">
                      <span className="font-semibold text-gray-300 line-clamp-1">{src.title}</span>
                      <span className="text-emerald-400 text-[10px] bg-emerald-950/40 px-1 rounded-sm flex-shrink-0">
                        {Math.round(src.score * 100)}%
                      </span>
                    </div>
                    <p className="text-gray-500 text-[10px] font-mono line-clamp-2 bg-black/60 p-1.5 rounded border border-gray-900">
                      {src.snippet}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex-1 flex items-center justify-center text-center p-4 bg-black/10 rounded border border-gray-900 font-mono text-[10px] text-gray-500 italic">
                {isLoading ? "Running retrieve trace..." : "Select a response block to display custom RAG search coordinates"}
              </div>
            )}
          </div>

          {/* Module 3: Console Debug logs terminal window */}
          <div className="h-44 border border-gray-850 bg-gray-950/40 p-4 rounded-lg flex flex-col overflow-hidden">
            <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-2.5 flex items-center gap-1.5 font-mono">
              <Terminal className="w-3.5 h-3.5 text-emerald-400" />
              Real-time Logs
            </h3>
            
            <div className="bg-black/60 p-2.5 rounded border border-gray-900 font-mono text-[10px] space-y-1.5 flex-1 overflow-y-auto scrollbar-none text-gray-400">
              {isLoading ? (
                <>
                  <div className="text-blue-400 animate-pulse">[INFO] POST /api/ask - PROCESSING...</div>
                  <div className="text-gray-500">[DEBUG] Waking LangGraph workflow state machine</div>
                </>
              ) : selectedMsg ? (
                <>
                  <div className="text-blue-400">[INFO] POST /api/ask 200 OK</div>
                  <div className="text-gray-500">[DEBUG] Node classify: True (Python-related)</div>
                  {selectedMsgIndex !== null && <div className="text-gray-500">[DEBUG] Query matched index trace: msg {selectedMsgIndex}</div>}
                  <div className="text-gray-500">[DEBUG] Retrieved {selectedMsg.sources?.length || 0} grounding segments (k=4)</div>
                  {selectedMsg.processing_time_ms && (
                    <div className="text-emerald-400 font-semibold">[INFO] Finished resolve in {selectedMsg.processing_time_ms}ms</div>
                  )}
                </>
              ) : (
                <>
                  <div className="text-gray-600">[INFO] System idle. Server waiting for requests...</div>
                  <div className="text-gray-700">[DEBUG] ChromaDB vector store linked at /chroma_db</div>
                </>
              )}
            </div>
          </div>

        </aside>

      </div>

      {/* ─── Footer bar: (Height-8, Black interface, state diagnostics) ─── */}
      <footer className="h-8 border-t border-gray-800 bg-black flex items-center justify-between px-6 text-[10px] font-mono text-gray-600 flex-shrink-0 select-none">
        <div>
          CHROMA_DB: <span className="text-emerald-400 font-bold">{health?.vector_store === "connected" ? "CONNECTED" : "DISCONNECTED"}</span> • API_KEY: <span className="text-emerald-400 font-bold">SET</span>
        </div>
        <div className="hidden sm:block">
          CPU: 8% • LATENCY: {selectedMsg?.processing_time_ms ? `${(selectedMsg.processing_time_ms / 100).toFixed(1)}s` : "0.0s"} • MEMORY: 512MB
        </div>
      </footer>

    </div>
  );
}
