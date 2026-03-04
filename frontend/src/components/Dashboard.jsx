import React, { useState, useMemo } from 'react';
import { 
  PieChart, Pie, Cell, Tooltip as RechartsTooltip, Legend, ResponsiveContainer, 
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  BarChart, Bar, ScatterChart, Scatter, ZAxis,
  Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis
} from 'recharts';
import ChatWindow from './ChatWindow';
import ReactMarkdown from 'react-markdown';
import { 
  FileText, Calendar, MessageSquare, TrendingUp, ThumbsUp, ThumbsDown, 
  Smile, Cloud, Users, Target, Activity, Zap, Maximize2, X, Filter,
  Film, MessageCircle, Clock, ChevronRight, AlignLeft
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

// --- MÀU SẮC CHỦ ĐẠO ---
const COLORS = {
  pos: '#22c55e', neg: '#ef4444', neu: '#94a3b8', primary: '#3b82f6', accent: '#8b5cf6',
};

const WORD_COLORS = [
  '#3b82f6', '#8b5cf6', '#ec4899', '#10b981', '#f59e0b', '#6366f1', '#ef4444', '#06b6d4', '#84cc16', '#d946ef'
];

const SENTIMENT_MAP = {
  'Tích cực': 'Positive', 'Tiêu cực': 'Negative', 'Trung tính': 'Neutral'
};

// ==========================================
// HELPER: PARSE TEXT THÔNG MINH
// ==========================================

/** Strip markdown syntax: ###, **, *, __ */
const stripMarkdown = (str) => {
  return str
    .replace(/^#{1,6}\s*/, '')        // ### heading
    .replace(/\*\*(.*?)\*\*/g, '$1')  // **bold**
    .replace(/__(.*?)__/g, '$1')      // __bold__
    .replace(/\*(.*?)\*/g, '$1')      // *italic*
    .replace(/`(.*?)`/g, '$1')        // `code`
    .trim();
};

/** Lấy text thuần sau khi strip markdown */
const cleanText = (str) => stripMarkdown(str);

/** Kiểm tra emoji đặc biệt ở đầu (sau khi strip markdown) */
const EMOJI_REGEX = /^\p{Extended_Pictographic}/u;
const startsWithEmoji = (str) => EMOJI_REGEX.test(str.trim());

/** Các icon "section header" nổi bật */
const SECTION_ICONS = ['🥘','🔸','📋','📰','👤','🕵️','⚠️','⚖️','🎙️','🌟','🌍','🔹','✅','❌','⭐','💡','🏆','📌','🎯','🗓️','📊','🔔','💬','🧵','🎤','🗣️','🍳','🧂','🫕'];
const isSectionIcon = (str) => SECTION_ICONS.some(ic => str.startsWith(ic));

/**
 * Parse text → array of typed blocks
 * Nhận dạng: heading, location, qa-question, qa-answer, note, section-highlight, bullet, plain
 */
const parseContentLines = (text) => {
  if (!text) return [];
  const lines = text.split('\n');
  const blocks = [];
  let inAnswer = false; // context: đang trong vùng trả lời

  for (let i = 0; i < lines.length; i++) {
    const raw = lines[i];
    const trimmed = raw.trim();

    // Dòng trống: giữ nguyên context nếu đang trong answer
    if (!trimmed) {
      blocks.push({ type: 'empty' });
      // Không reset inAnswer ở đây — dòng trống giữa các câu vẫn thuộc answer
      continue;
    }

    // Detect markdown heading → reset context
    if (/^#{1,6}\s/.test(trimmed)) {
      inAnswer = false;
      blocks.push({ type: 'heading', content: cleanText(trimmed) });
      continue;
    }

    // Detect location → reset context
    if (/^(📍|Đang ở:|Địa điểm:|Location:)/i.test(trimmed)) {
      inAnswer = false;
      blocks.push({ type: 'location', content: cleanText(trimmed) });
      continue;
    }

    const clean = cleanText(trimmed);

    // QA Question: reset context, bắt đầu câu hỏi mới
    if (clean.startsWith('❓') || /^\*\*❓/.test(trimmed) || trimmed.includes('**❓')) {
      inAnswer = false;
      const q = clean.replace(/^❓\s*/, '').trim();
      blocks.push({ type: 'qa-question', content: q });
      continue;
    }

    // QA Answer bắt đầu bằng ↳ → tạo block mới với lines[]
    if (clean.startsWith('↳')) {
      inAnswer = true;
      blocks.push({ type: 'qa-answer', lines: [clean.slice(1).trim()] });
      continue;
    }

    // Nếu đang trong context answer → append vào block answer cuối
    if (inAnswer) {
      const isNewBlock =
        isSectionIcon(clean) ||
        /^(•\s*)?(Lưu ý|Note|Chú ý)\s*:/i.test(clean);

      if (!isNewBlock) {
        const last = blocks[blocks.length - 1];
        if (last?.type === 'qa-answer') {
          last.lines.push(clean);
        } else {
          blocks.push({ type: 'qa-answer', lines: [clean] });
        }
        continue;
      }
      inAnswer = false;
    }

    // Note / Lưu ý
    if (/^(•\s*)?(Lưu ý|Note|Chú ý)\s*:/i.test(clean)) {
      blocks.push({ type: 'note', content: clean.replace(/^•\s*/, '') });
      continue;
    }

    // Section icon
    if (isSectionIcon(clean)) {
      const isHeader = clean.length <= 80 && (clean.endsWith(':') || /^[🥘🔸📋📰👤🕵️⚠️⚖️🎙️🌟🌍🔹✅❌⭐💡🏆📌🎯🗓️📊🔔💬🧵🎤🗣️]/.test(clean));
      blocks.push({ type: isHeader ? 'section-header' : 'section-highlight', content: clean });
      continue;
    }

    // Bullet
    if (/^[•\-]\s/.test(clean)) {
      blocks.push({ type: 'bullet', content: clean.replace(/^[•\-]\s/, '') });
      continue;
    }

    blocks.push({ type: 'plain', content: clean });
  }

  return blocks;
};

// ==========================================
// COMPONENT: RENDER NỘI DUNG TEXT THÔNG MINH
// ==========================================
const SmartTextRenderer = ({ content }) => {
  const blocks = parseContentLines(content);

  return (
    <div className="space-y-1.5">
      {blocks.map((block, idx) => {
        if (block.type === 'empty') return <div key={idx} className="h-2" />;

        // === HEADING (từ ### markdown) ===
        if (block.type === 'heading') {
          return (
            <div key={idx} className="mt-6 mb-3 first:mt-0">
              <div className="flex items-center gap-3 bg-gradient-to-r from-slate-800 to-slate-700 text-white rounded-2xl px-5 py-3.5 shadow-md">
                <span className="text-base font-extrabold tracking-wide leading-snug">{block.content}</span>
              </div>
            </div>
          );
        }

        // === LOCATION ===
        if (block.type === 'location') {
          const locationText = block.content.replace(/^(📍\s*|Đang ở:\s*)/i, '').trim();
          const prefix = block.content.includes('📍') ? '📍' : '🗺️';
          return (
            <div key={idx} className="flex items-center gap-2.5 bg-gradient-to-r from-emerald-50 to-teal-50 border border-emerald-200 rounded-xl px-4 py-2.5 mt-3 mb-2 shadow-sm w-fit">
              <span className="text-lg">{prefix}</span>
              <div>
                <span className="text-[10px] font-bold text-emerald-600 uppercase tracking-widest block">Địa điểm</span>
                <span className="text-slate-800 font-bold text-sm">{locationText}</span>
              </div>
            </div>
          );
        }

        // === SECTION HEADER (emoji + label ngắn) ===
        if (block.type === 'section-header') {
          return (
            <div key={idx} className="mt-5 mb-2 first:mt-0">
              <span className="inline-flex items-center gap-2 bg-indigo-50 border border-indigo-100 text-indigo-800 font-bold text-sm px-4 py-2 rounded-xl shadow-sm">
                {block.content}
              </span>
            </div>
          );
        }

        // === SECTION HIGHLIGHT (emoji + nội dung dài) ===
        if (block.type === 'section-highlight') {
          // Tách emoji đầu tiên ra
          const emojiMatch = block.content.match(/^(\p{Extended_Pictographic}+\s*)/u);
          const icon = emojiMatch ? emojiMatch[1].trim() : '';
          const text = icon ? block.content.slice(emojiMatch[0].length).trim() : block.content;
          return (
            <div key={idx} className="flex items-start gap-3 bg-gradient-to-r from-blue-50 via-indigo-50 to-blue-50 border border-blue-200 rounded-xl px-4 py-3.5 shadow-sm mt-2">
              {icon && <span className="text-xl flex-shrink-0 mt-0.5">{icon}</span>}
              <p className="text-slate-800 text-sm leading-relaxed font-medium">{text}</p>
            </div>
          );
        }

        // === QA QUESTION ===
        if (block.type === 'qa-question') {
          return (
            <div key={idx} className="flex items-start gap-3 bg-amber-50 border-l-4 border-amber-400 rounded-r-xl px-4 py-3.5 mt-5 shadow-sm">
              <div className="w-7 h-7 rounded-full bg-amber-400 flex items-center justify-center flex-shrink-0 mt-0.5 shadow-sm">
                <span className="text-white font-black text-xs">Q</span>
              </div>
              <p className="text-slate-800 text-sm leading-relaxed font-semibold">{block.content}</p>
            </div>
          );
        }

        // === QA ANSWER (gom thành 1 vùng) ===
        if (block.type === 'qa-answer') {
          const lines = block.lines || (block.content ? [block.content] : []);
          return (
            <div key={idx} className="flex items-start gap-3 bg-emerald-50 border-l-4 border-emerald-400 rounded-r-xl px-4 py-4 shadow-sm">
              <div className="w-7 h-7 rounded-full bg-emerald-400 flex items-center justify-center flex-shrink-0 mt-0.5 shadow-sm">
                <span className="text-white font-black text-xs">A</span>
              </div>
              <div className="space-y-1.5">
                {lines.filter(l => l.trim()).map((line, li) => (
                  <p key={li} className="text-slate-700 text-sm leading-relaxed italic">{line}</p>
                ))}
              </div>
            </div>
          );
        }

        // === NOTE / LƯU Ý ===
        if (block.type === 'note') {
          return (
            <div key={idx} className="flex items-start gap-3 bg-orange-50 border border-orange-200 rounded-xl px-4 py-3 shadow-sm mt-2">
              <span className="text-orange-500 text-lg flex-shrink-0 mt-0.5">⚠️</span>
              <p className="text-orange-800 text-sm leading-relaxed font-medium">{block.content.replace(/^(Lưu ý|Note|Chú ý)\s*:\s*/i, (m) => `${m}`)}</p>
            </div>
          );
        }

        // === BULLET ===
        if (block.type === 'bullet') {
          return (
            <div key={idx} className="flex items-start gap-2.5 px-3 py-1">
              <ChevronRight className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" />
              <p className="text-slate-700 text-sm leading-relaxed">{block.content}</p>
            </div>
          );
        }

        // === PLAIN TEXT ===
        return (
          <p key={idx} className="text-slate-600 text-sm leading-relaxed px-1">
            {block.content}
          </p>
        );
      })}
    </div>
  );
};

// ==========================================
// COMPONENT: TIMELINE VIEW
// ==========================================
const TimelineView = ({ timeline }) => {
  if (!timeline || timeline.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-slate-400">
        <Clock className="w-12 h-12 mb-3 opacity-20" />
        <p className="italic text-sm">Không có dữ liệu timeline.</p>
      </div>
    );
  }

  return (
    <div className="relative border-l-2 border-blue-100 ml-4 pl-8 space-y-10">
      {timeline.map((item, idx) => (
        <div key={idx} className="relative">
          <div className="absolute -left-[41px] top-0 w-5 h-5 bg-white border-4 border-blue-500 rounded-full shadow-sm" />
          <div className="flex items-center gap-3 mb-3">
            <span className="px-3 py-1 bg-blue-50 text-blue-700 text-xs font-bold rounded-lg shadow-sm font-mono">
              {item.time}
            </span>
            {item.label && (
              <h4 className="font-bold text-slate-800 uppercase tracking-wide text-sm">{item.label}</h4>
            )}
          </div>
          <div className="bg-slate-50 border border-slate-100 rounded-2xl p-5 space-y-3">
            {item?.points?.map((point, pIdx) => (
              <div key={pIdx} className="flex items-start gap-3">
                <ChevronRight className="w-4 h-4 text-blue-400 mt-1 flex-shrink-0" />
                <SmartTextRenderer content={point} />
              </div>
            ))}
            {item?.content && <SmartTextRenderer content={item.content} />}
          </div>
        </div>
      ))}
    </div>
  );
};

// ==========================================
// COMPONENT: TALKSHOW / INTERVIEW VIEW
// ==========================================
const TalkshowView = ({ content, guests }) => {
  if (!content) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-slate-400">
        <MessageCircle className="w-12 h-12 mb-3 opacity-20" />
        <p className="italic text-sm">Không có dữ liệu talkshow / phỏng vấn.</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {guests && guests.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-4 p-4 bg-purple-50 rounded-xl border border-purple-100">
          <span className="text-xs font-bold text-purple-700 uppercase tracking-wide w-full mb-1">Khách mời</span>
          {guests.map((g, i) => (
            <span key={i} className="px-3 py-1 bg-white border border-purple-200 text-purple-700 rounded-full text-xs font-medium shadow-sm">
              {g}
            </span>
          ))}
        </div>
      )}
      <SmartTextRenderer content={content} />
    </div>
  );
};

// ==========================================
// COMPONENT: NEWS / BULLET SUMMARY VIEW
// ==========================================
const NewsView = ({ items, content }) => {
  if (!items?.length && !content) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-slate-400">
        <FileText className="w-12 h-12 mb-3 opacity-20" />
        <p className="italic text-sm">Không có dữ liệu tin tức / tổng hợp.</p>
      </div>
    );
  }
  const raw = content || (items || []).join('\n');
  return <SmartTextRenderer content={raw} />;
};

// ==========================================
// COMPONENT: REPORT / PHÓNG SỰ VIEW
// ==========================================
const ReportView = ({ sections, content }) => {
  if (!sections?.length && !content) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-slate-400">
        <FileText className="w-12 h-12 mb-3 opacity-20" />
        <p className="italic text-sm">Không có dữ liệu phóng sự / báo cáo.</p>
      </div>
    );
  }
  if (content) return <SmartTextRenderer content={content} />;
  return (
    <div className="space-y-6">
      {sections.map((section, idx) => (
        <div key={idx} className="rounded-2xl border border-slate-100 overflow-hidden shadow-sm">
          {section.title && (
            <div className="px-5 py-3 bg-slate-800 flex items-center gap-2">
              <span className="text-white font-bold text-sm">{section.title}</span>
            </div>
          )}
          <div className="p-5 bg-white">
            <SmartTextRenderer content={(section.items || []).join('\n') + (section.content ? '\n' + section.content : '')} />
          </div>
        </div>
      ))}
    </div>
  );
};

// ==========================================
// COMPONENT CHÍNH: VIDEO SUMMARY RENDERER
// ==========================================
const VideoSummaryPanel = ({ videoSummary }) => {
  if (!videoSummary || (!videoSummary.type && !videoSummary.content && !videoSummary.timeline)) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-slate-400">
        <Film className="w-14 h-14 mb-3 opacity-20" />
        <p className="italic text-sm">Chưa có dữ liệu tóm tắt nội dung.</p>
      </div>
    );
  }

  const type = videoSummary.type || 'TEXT';

  const typeConfig = {
    TIMELINE: { icon: <Clock className="w-6 h-6" />, label: 'Trục thời gian (Timeline)', bg: 'bg-blue-50', text: 'text-blue-600' },
    TALKSHOW: { icon: <MessageCircle className="w-6 h-6" />, label: 'Tóm tắt Talkshow / Phỏng vấn', bg: 'bg-purple-50', text: 'text-purple-600' },
    NEWS: { icon: <FileText className="w-6 h-6" />, label: 'Tổng hợp Tin tức', bg: 'bg-green-50', text: 'text-green-600' },
    REPORT: { icon: <Target className="w-6 h-6" />, label: 'Phóng sự / Báo cáo chuyên sâu', bg: 'bg-red-50', text: 'text-red-600' },
    TEXT: { icon: <AlignLeft className="w-6 h-6" />, label: 'Tóm tắt nội dung', bg: 'bg-slate-50', text: 'text-slate-600' },
  };

  const cfg = typeConfig[type] || typeConfig.TEXT;

  return (
    <div className="bg-white p-6 md:p-8 rounded-3xl shadow-sm border border-slate-100 animate-in fade-in slide-in-from-bottom-4 duration-500">
      {/* Header */}
      <div className="flex items-center gap-3 mb-8">
        <div className={`p-3 rounded-xl ${cfg.bg} ${cfg.text}`}>{cfg.icon}</div>
        <div>
          <h3 className="font-bold text-xl text-slate-800">Bản tóm tắt</h3>
          <p className="text-sm text-slate-500">{cfg.label}{videoSummary.category ? ` · ${videoSummary.category}` : ''}</p>
        </div>
      </div>

      {/* Content by type */}
      {type === 'TIMELINE' && (
        <TimelineView timeline={videoSummary.timeline} />
      )}

      {type === 'TALKSHOW' && (
        <TalkshowView content={videoSummary.content} guests={videoSummary.guests} />
      )}

      {type === 'NEWS' && (
        <NewsView items={videoSummary.items} content={videoSummary.content} />
      )}

      {type === 'REPORT' && (
        <ReportView sections={videoSummary.sections} content={videoSummary.content} />
      )}

      {type === 'TEXT' && (
        <div className="prose prose-slate max-w-none">
          {videoSummary.content
            ? <SmartTextRenderer content={videoSummary.content} />
            : <p className="text-slate-400 italic text-center py-6">Không có dữ liệu văn bản.</p>
          }
        </div>
      )}
    </div>
  );
};

// --- COMPONENT: MODAL BÌNH LUẬN ---
const CommentModal = ({ isOpen, onClose, title, comments, type }) => {
  if (!isOpen) return null;
  return (
    <AnimatePresence>
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4" onClick={onClose}>
        <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl h-[80vh] flex flex-col overflow-hidden" onClick={(e) => e.stopPropagation()}>
          <div className="p-5 border-b border-slate-100 flex justify-between items-center bg-slate-50">
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded-lg ${type === 'danger' ? 'bg-red-100 text-red-600' : 'bg-blue-100 text-blue-600'}`}><Filter className="w-5 h-5" /></div>
              <div><h3 className="font-bold text-lg text-slate-800">Lọc bình luận theo:</h3><p className="text-sm text-slate-500 font-medium">{title}</p></div>
            </div>
            <button onClick={onClose} className="p-2 hover:bg-slate-200 rounded-full transition-colors"><X className="w-5 h-5 text-slate-500" /></button>
          </div>
          <div className="flex-1 overflow-y-auto p-5 space-y-4 custom-scrollbar">
            {comments.length > 0 ? comments.map((cmt, idx) => (
              <div key={idx} className="p-4 bg-white border border-slate-100 rounded-xl shadow-sm hover:shadow-md transition-shadow">
                <div className="flex justify-between items-start mb-2">
                  <span className="font-bold text-slate-700 text-sm">{cmt.tac_gia}</span>
                  <span className={`text-[10px] px-2 py-1 rounded-full font-bold uppercase ${cmt.cam_xuc_du_doan === 'Positive' ? 'bg-green-100 text-green-600' : cmt.cam_xuc_du_doan === 'Negative' ? 'bg-red-100 text-red-600' : 'bg-slate-100 text-slate-500'}`}>{cmt.cam_xuc_du_doan}</span>
                </div>
                <p className="text-slate-600 text-sm leading-relaxed">{cmt.ban_goc}</p>
              </div>
            )) : <div className="h-full flex flex-col items-center justify-center text-slate-400"><MessageSquare className="w-12 h-12 mb-2 opacity-20" /><p>Không tìm thấy bình luận nào phù hợp.</p></div>}
          </div>
          <div className="p-4 border-t border-slate-100 bg-slate-50 text-right text-xs text-slate-400">Hiển thị {comments.length} kết quả</div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

const CustomScatterTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="bg-white p-3 border border-slate-200 shadow-xl rounded-xl max-w-xs z-50">
        <div className="flex items-center gap-2 mb-1"><div className="w-2 h-2 rounded-full bg-blue-500"></div><p className="font-bold text-slate-700 text-sm">{data.author}</p></div>
        <p className="text-xs text-slate-600 line-clamp-3 italic">"{data.content}"</p>
      </div>
    );
  }
  return null;
};

// ==========================================
// COMPONENT CHÍNH: DASHBOARD
// ==========================================
export default function Dashboard({ data, taskId }) {
  const [activeTab, setActiveTab] = useState('comments');
  const [modalOpen, setModalOpen] = useState(false);
  const [filterType, setFilterType] = useState(null);
  const [filterValue, setFilterValue] = useState(null);
  const [timeRange, setTimeRange] = useState('7');

  // --- TRÍCH XUẤT DỮ LIỆU AN TOÀN (KHÔNG CÓ MOCK DATA) ---
  const video_url = data?.video_url || '';
  const sentimentData = data?.sentiment_chart?.length > 0 ? data.sentiment_chart : [];
  const emojiData = data?.emoji_stats?.length > 0 ? data.emoji_stats : [];
  const rawWordCloudData = data?.word_cloud?.length > 0 ? data.word_cloud : [];
  const totalComments = data?.total_comments || 0;
  const topUsers = data?.top_users?.length > 0 ? data.top_users : [];
  const scatterData = data?.scatter_clusters?.length > 0 ? data.scatter_clusters : [];
  const allComments = data?.all_comments?.length > 0 ? data.all_comments : [];
  const timeSeriesData = data?.time_series?.length > 0 ? data.time_series : [];
  const videoSummary = data?.video_summary || null;

  // Lọc Timeline cho biểu đồ bình luận
  const filteredTimeSeries = useMemo(() => {
    if (timeRange === 'all') return timeSeriesData;
    const cutoff = new Date(); cutoff.setDate(cutoff.getDate() - parseInt(timeRange));
    return timeSeriesData.filter(item => new Date(item.date) >= cutoff);
  }, [timeSeriesData, timeRange]);

  const positiveCount = sentimentData.find(i => i.name === 'Tích cực')?.value || 0;
  const negativeCount = sentimentData.find(i => i.name === 'Tiêu cực')?.value || 0;
  const neutralCount = sentimentData.find(i => i.name === 'Trung tính')?.value || 0;
  
  const positivePercent = totalComments > 0 ? Math.round((positiveCount / totalComments) * 100) : 0;
  const negativePercent = totalComments > 0 ? Math.round((negativeCount / totalComments) * 100) : 0;

  const handleWordClick = (w) => { setFilterType('WORD'); setFilterValue(w); setModalOpen(true); };
  const handleSentimentClick = (e) => { setFilterType('SENTIMENT'); setFilterValue(e.name); setModalOpen(true); };
  const handleUserClick = (u) => { setFilterType('USER'); setFilterValue(u); setModalOpen(true); };
  const handleEmojiClick = (e) => { if (e?.emoji) { setFilterType('EMOJI'); setFilterValue(e.emoji); setModalOpen(true); } };

  const filteredComments = useMemo(() => {
    if (!filterType || !filterValue) return [];
    return (allComments || []).filter(cmt => {
        if (filterType === 'USER') return cmt.tac_gia === filterValue;
        if (filterType === 'SENTIMENT') return cmt.cam_xuc_du_doan === SENTIMENT_MAP[filterValue];
        if (filterType === 'WORD') return cmt.ban_goc?.toLowerCase().includes(filterValue.toLowerCase());
        if (filterType === 'EMOJI') return cmt.ban_goc?.includes(filterValue);
        return false;
    });
  }, [filterType, filterValue, allComments]);

  const getModalTitle = () => {
      switch(filterType) {
          case 'USER': return `Người dùng: "${filterValue}"`;
          case 'SENTIMENT': return `Nhóm cảm xúc: ${filterValue}`;
          case 'WORD': return `Chứa từ khóa: "${filterValue}"`;
          case 'EMOJI': return `Chứa Emoji: ${filterValue}`;
          default: return '';
      }
  };

  const radarRealData = useMemo(() => {
    if (!totalComments) return [];
    const funEmojis = ['😂', '🤣', '😆', '😁', 'hihi', 'haha'];
    const funCount = (emojiData || []).reduce((acc, curr) => funEmojis.some(e => curr.emoji?.includes(e)) ? acc + curr.count : acc, 0);
    const scale = (val, max) => Math.min(100, Math.round((val / max) * 100)) || 20;
    return [
      { subject: 'Tích cực', A: scale(positiveCount, totalComments), fullMark: 100 },
      { subject: 'Tiêu cực', A: scale(negativeCount, totalComments), fullMark: 100 },
      { subject: 'Hài hước', A: scale(funCount, totalComments / 3), fullMark: 100 }, 
      { subject: 'Trung lập', A: scale(neutralCount, totalComments), fullMark: 100 },
      { subject: 'Sôi nổi', A: scale(totalComments, 500), fullMark: 100 }, 
      { subject: 'Sáng tạo', A: scale(rawWordCloudData.length, 100), fullMark: 100 }, 
    ];
  }, [positiveCount, negativeCount, neutralCount, emojiData, rawWordCloudData, totalComments]);

  const processedWordCloud = useMemo(() => {
    if (!rawWordCloudData.length) return { items: [], maxVal: 1, minVal: 0 };
    const maxVal = Math.max(...rawWordCloudData.map(w => w.value));
    const minVal = Math.min(...rawWordCloudData.map(w => w.value));
    const shuffledItems = [...rawWordCloudData].sort(() => Math.random() - 0.5);
    return { items: shuffledItems, maxVal, minVal };
  }, [rawWordCloudData]);

  // Empty state component
  const EmptyState = ({ icon: Icon, message }) => (
    <div className="flex flex-col items-center justify-center h-full text-slate-400 gap-2 py-8">
      <Icon className="w-10 h-10 opacity-20" />
      <p className="text-sm italic">{message}</p>
    </div>
  );

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }} className="max-w-7xl mx-auto space-y-6 pb-20 pt-8">
      
      <CommentModal isOpen={modalOpen} onClose={() => setModalOpen(false)} title={getModalTitle()} comments={filteredComments} type={filterValue === 'Tiêu cực' ? 'danger' : 'normal'} />

      {/* === HEADER & TABS === */}
      <div className="bg-white/90 backdrop-blur-md rounded-3xl shadow-sm border border-slate-100 overflow-hidden">
        <div className="p-6 md:px-8 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-slate-100">
          <div>
            <h2 className="text-2xl font-extrabold text-slate-800 flex items-center gap-2">
              <Activity className="w-6 h-6 text-blue-600" />
              Báo Cáo Phân Tích Toàn Diện
            </h2>
            <p className="text-slate-500 text-sm mt-1 flex items-center gap-2 flex-wrap">
               {video_url
                 ? <><span>Nguồn:</span><a href={video_url} target="_blank" rel="noreferrer" className="text-blue-600 hover:underline font-medium truncate max-w-[200px]">{video_url}</a></>
                 : <span className="italic text-slate-400">Chưa có nguồn video</span>
               }
               {videoSummary?.category && <span className="px-2 py-0.5 bg-slate-100 text-slate-600 rounded-md text-xs font-bold uppercase">{videoSummary.category}</span>}
            </p>
          </div>
          <button onClick={() => alert('Đang xuất báo cáo...')} className="flex items-center gap-2 px-5 py-2.5 bg-slate-900 text-white rounded-xl hover:bg-slate-800 transition-all font-medium text-sm shadow-lg shadow-slate-200">
              <FileText className="w-4 h-4" /> Xuất Excel
          </button>
        </div>

        <div className="flex px-6 pt-4 gap-6 bg-slate-50/50">
           <button 
              onClick={() => setActiveTab('comments')}
              className={`pb-4 px-2 font-bold text-sm md:text-base border-b-2 transition-colors flex items-center gap-2 ${activeTab === 'comments' ? 'border-blue-600 text-blue-600' : 'border-transparent text-slate-500 hover:text-slate-700'}`}
           >
              <MessageCircle className="w-5 h-5" /> Phân Tích Bình Luận
           </button>
           <button 
              onClick={() => setActiveTab('summary')}
              className={`pb-4 px-2 font-bold text-sm md:text-base border-b-2 transition-colors flex items-center gap-2 ${activeTab === 'summary' ? 'border-blue-600 text-blue-600' : 'border-transparent text-slate-500 hover:text-slate-700'}`}
           >
              <Film className="w-5 h-5" /> Tóm Tắt Nội Dung Video
           </button>
        </div>
      </div>

      {/* === MAIN LAYOUT === */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        
        {/* --- CỘT TRÁI (8 CỘT) --- */}
        <div className="lg:col-span-8 space-y-6">
          
          {/* TAB 1: TÓM TẮT NỘI DUNG VIDEO */}
          {activeTab === 'summary' && (
            <VideoSummaryPanel videoSummary={videoSummary} />
          )}

          {/* TAB 2: PHÂN TÍCH BÌNH LUẬN */}
          {activeTab === 'comments' && (
             <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                
                {/* KPI CARDS */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                  {[
                    { label: 'Tổng Bình Luận', val: totalComments > 0 ? totalComments.toLocaleString() : '—', icon: MessageSquare, color: 'text-blue-600', bg: 'bg-blue-50' },
                    { label: 'Điểm Cảm Xúc', val: totalComments > 0 ? `${positivePercent - negativePercent}` : '—', icon: Target, color: 'text-violet-600', bg: 'bg-violet-50', note: 'Chỉ số ròng' },
                    { label: 'Độ Tích Cực', val: totalComments > 0 ? `${positivePercent}%` : '—', icon: ThumbsUp, color: 'text-green-600', bg: 'bg-green-50' },
                    { label: 'Tiêu Cực / Toxic', val: totalComments > 0 ? `${negativePercent}%` : '—', icon: Zap, color: 'text-red-600', bg: 'bg-red-50' },
                  ].map((stat, i) => (
                    <div key={i} className="bg-white p-5 rounded-2xl shadow-sm border border-slate-100 flex items-start justify-between hover:shadow-md transition-shadow">
                      <div>
                        <p className="text-slate-500 text-[11px] font-bold uppercase tracking-wider mb-1">{stat.label}</p>
                        <p className={`text-3xl font-bold ${stat.val === '—' ? 'text-slate-300' : 'text-slate-800'}`}>{stat.val}</p>
                        {stat.note && <p className="text-[10px] text-slate-400 mt-1">{stat.note}</p>}
                      </div>
                      <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${stat.bg}`}>
                        <stat.icon className={`w-5 h-5 ${stat.color}`} />
                      </div>
                    </div>
                  ))}
                </div>

                {/* 1. TIME SERIES */}
                <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100">
                  <div className="flex flex-col sm:flex-row justify-between items-center mb-6 gap-4">
                    <h3 className="font-bold text-lg text-slate-800 flex items-center gap-2">
                      <TrendingUp className="w-5 h-5 text-blue-500"/> Xu hướng thảo luận
                    </h3>
                    <div className="flex bg-slate-100 p-1 rounded-lg">
                      {['7', '30', 'all'].map((range) => (
                        <button
                          key={range}
                          onClick={() => setTimeRange(range)}
                          className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all ${
                            timeRange === range ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-500 hover:text-slate-700'
                          }`}
                        >
                          {range === 'all' ? 'Tất cả' : `${range} ngày`}
                        </button>
                      ))}
                    </div>
                  </div>
                  <div className="h-72 w-full">
                    {filteredTimeSeries.length > 0 ? (
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={filteredTimeSeries}>
                          <defs>
                            <linearGradient id="colorComments" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="5%" stopColor={COLORS.primary} stopOpacity={0.2}/>
                              <stop offset="95%" stopColor={COLORS.primary} stopOpacity={0}/>
                            </linearGradient>
                          </defs>
                          <XAxis dataKey="date" stroke="#94a3b8" fontSize={11} tickLine={false} axisLine={false} dy={10}
                            tickFormatter={(str) => {
                              const dateObj = new Date(str);
                              if (isNaN(dateObj.getTime())) return str;
                              const hours = dateObj.getHours();
                              const minutes = dateObj.getMinutes();
                              if (hours === 0 && minutes === 0) return `${dateObj.getDate()}/${dateObj.getMonth() + 1}`;
                              return `${hours}:${minutes < 10 ? '0' : ''}${minutes}`;
                            }}
                          />
                          <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                          <RechartsTooltip contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)' }} />
                          <Area type="monotone" dataKey="comments" stroke={COLORS.primary} strokeWidth={3} fillOpacity={1} fill="url(#colorComments)" />
                        </AreaChart>
                      </ResponsiveContainer>
                    ) : (
                      <EmptyState icon={TrendingUp} message="Không có dữ liệu thời gian cho khoảng thời gian này." />
                    )}
                  </div>
                </div>

                {/* 2. ROW: SENTIMENT PIE & RADAR CHART */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                   <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100 relative group cursor-pointer hover:border-blue-200 transition-colors">
                      <div className="absolute top-4 right-4 text-[10px] text-slate-400 font-medium bg-slate-50 px-2 py-1 rounded-full border border-slate-100 opacity-0 group-hover:opacity-100 transition-opacity">
                          🖱️ Nhấn để lọc
                      </div>
                      <h3 className="font-bold text-lg text-slate-800 mb-2 text-center">Tỷ lệ Cảm Xúc</h3>
                      <div className="h-64 relative w-full">
                        {sentimentData.length > 0 ? (
                          <>
                            <ResponsiveContainer width="100%" height="100%">
                              <PieChart>
                                <Pie data={sentimentData} cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value" onClick={handleSentimentClick}>
                                  {sentimentData.map((entry, index) => (<Cell key={`cell-${index}`} fill={entry.color} stroke="none" className="hover:opacity-80 transition-opacity cursor-pointer"/>))}
                                </Pie>
                                <RechartsTooltip contentStyle={{ borderRadius: '12px', border: 'none' }} />
                                <Legend verticalAlign="bottom" iconType="circle" wrapperStyle={{fontSize: '12px', paddingTop: '10px'}}/>
                              </PieChart>
                            </ResponsiveContainer>
                            <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none pb-8">
                              <span className="text-3xl font-extrabold text-slate-800">{positivePercent}%</span>
                              <span className="text-xs text-slate-400 font-bold uppercase">Tích cực</span>
                            </div>
                          </>
                        ) : (
                          <EmptyState icon={Target} message="Không có dữ liệu cảm xúc." />
                        )}
                      </div>
                   </div>

                   <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100">
                       <h3 className="font-bold text-lg text-slate-800 mb-2 text-center flex items-center justify-center gap-2">
                          <Activity className="w-4 h-4 text-pink-500" /> Sắc thái Nội dung
                       </h3>
                       <div className="h-64 w-full">
                         {totalComments > 0 ? (
                           <ResponsiveContainer width="100%" height="100%">
                             <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarRealData}>
                               <PolarGrid stroke="#e2e8f0" />
                               <PolarAngleAxis dataKey="subject" tick={{ fill: '#64748b', fontSize: 11, fontWeight: 600 }} />
                               <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                               <Radar name="Video này" dataKey="A" stroke={COLORS.accent} strokeWidth={3} fill={COLORS.accent} fillOpacity={0.3} />
                               <RechartsTooltip contentStyle={{ borderRadius: '12px' }}/>
                             </RadarChart>
                           </ResponsiveContainer>
                         ) : (
                           <EmptyState icon={Activity} message="Không đủ dữ liệu phân tích sắc thái." />
                         )}
                       </div>
                   </div>
                </div>

                {/* 3. SCATTER PLOT */}
                <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100">
                  <h3 className="font-bold text-lg text-slate-800 mb-4 flex items-center gap-2">
                    <Target className="w-5 h-5 text-indigo-500"/> Bản đồ Phân cụm Chủ đề
                  </h3>
                  <div className="h-72 w-full bg-slate-50/50 rounded-2xl border border-slate-100">
                    {scatterData.length > 0 ? (
                      <ResponsiveContainer width="100%" height="100%">
                        <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                          <XAxis type="number" dataKey="x" name="PCA 1" hide />
                          <YAxis type="number" dataKey="y" name="PCA 2" hide />
                          <ZAxis type="number" dataKey="z" range={[60, 400]} />
                          <RechartsTooltip content={<CustomScatterTooltip />} cursor={{ strokeDasharray: '3 3' }} />
                          <Legend wrapperStyle={{fontSize: '12px'}}/>
                          <Scatter name="Nhóm 0" data={scatterData.filter(c => c.cluster === 'Nhóm 0')} fill="#3b82f6" shape="circle" />
                          <Scatter name="Nhóm 1" data={scatterData.filter(c => c.cluster === 'Nhóm 1')} fill="#ef4444" shape="triangle" />
                          <Scatter name="Nhóm 2" data={scatterData.filter(c => c.cluster === 'Nhóm 2')} fill="#10b981" shape="square" />
                        </ScatterChart>
                      </ResponsiveContainer>
                    ) : (
                      <EmptyState icon={Target} message="Không có dữ liệu phân cụm chủ đề." />
                    )}
                  </div>
                </div>

                {/* 4. WORD CLOUD */}
                <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100 flex flex-col relative group">
                  <div className="absolute top-6 right-6 text-[10px] text-slate-400 font-medium bg-slate-50 px-2 py-1 rounded-full border border-slate-100 opacity-0 group-hover:opacity-100 transition-opacity">
                       🖱️ Nhấn vào từ để xem comment
                  </div>
                  <h3 className="font-bold text-lg text-slate-800 mb-4 flex items-center gap-2">
                      <Cloud className="w-5 h-5 text-sky-500" /> Đám mây từ khóa
                  </h3>
                  <div className="min-h-[350px] bg-slate-50/50 rounded-2xl border border-slate-100 relative overflow-hidden flex flex-wrap content-center justify-center items-center gap-x-6 gap-y-3 p-6">
                     <div className="absolute top-0 right-0 w-40 h-40 bg-blue-200 rounded-full blur-3xl opacity-30 -z-10"></div>
                     <div className="absolute bottom-0 left-0 w-40 h-40 bg-purple-200 rounded-full blur-3xl opacity-30 -z-10"></div>
                     {processedWordCloud.items.length > 0 ? processedWordCloud.items.map((word, idx) => {
                       const ratio = (word.value - processedWordCloud.minVal) / (processedWordCloud.maxVal - processedWordCloud.minVal || 1);
                       const fontSize = 14 + (ratio * 45); 
                       const opacity = 0.6 + (ratio * 0.4);
                       const fontWeight = ratio > 0.5 ? 800 : (ratio > 0.3 ? 600 : 400);
                       return (
                         <motion.span 
                           key={idx}
                           initial={{ scale: 0, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} transition={{ delay: idx * 0.01, duration: 0.4 }} whileHover={{ scale: 1.2, zIndex: 10, rotate: 3 }}
                           style={{ fontSize: `${fontSize}px`, color: WORD_COLORS[idx % WORD_COLORS.length], opacity, fontWeight, lineHeight: '1.2' }}
                           className="cursor-pointer select-none font-sans hover:underline decoration-2" title={`${word.text}: ${word.value}`} onClick={() => handleWordClick(word.text)} 
                         >
                           {word.text}
                         </motion.span>
                       )
                     }) : <EmptyState icon={Cloud} message="Không trích xuất được từ khóa nổi bật nào." />}
                  </div>
                </div>

                {/* 5. ROW: TOP USERS & EMOJIS */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                   <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100 relative group">
                       <div className="absolute top-6 right-6 text-[10px] text-slate-400 font-medium bg-slate-50 px-2 py-1 rounded-full border border-slate-100 opacity-0 group-hover:opacity-100 transition-opacity">
                           🖱️ Chọn người dùng để xem lịch sử
                       </div>
                       <h3 className="font-bold text-lg text-slate-800 mb-4 flex items-center gap-2">
                         <Users className="w-5 h-5 text-orange-500" /> Người dùng nổi bật
                       </h3>
                       <div className="space-y-3 max-h-[300px] overflow-y-auto pr-2 custom-scrollbar">
                          {topUsers.length > 0 ? topUsers.map((user, idx) => (
                            <div key={idx} onClick={() => handleUserClick(user.name)} className="flex items-center justify-between p-3 bg-slate-50 rounded-xl hover:bg-blue-50 hover:border-blue-200 border border-transparent transition-all cursor-pointer group/item">
                               <div className="flex items-center gap-3 overflow-hidden">
                                  <div className="w-9 h-9 flex-shrink-0 rounded-full bg-white border border-slate-200 flex items-center justify-center text-sm font-bold text-slate-600 shadow-sm group-hover/item:scale-110 transition-transform">
                                    {user.name ? user.name.charAt(0).toUpperCase() : '?'}
                                  </div>
                                  <div className="min-w-0">
                                    <p className="text-xs font-bold text-slate-700 truncate max-w-[150px] group-hover/item:text-blue-600" title={user.name}>{user.name}</p>
                                    <p className="text-[10px] text-slate-400 mt-0.5">
                                      {user.sentiment === 'Positive' && <span className="text-green-600 font-medium">● Tích cực</span>}
                                      {user.sentiment === 'Negative' && <span className="text-red-600 font-medium">● Tiêu cực</span>}
                                      {user.sentiment === 'Neutral' && <span className="text-gray-500 font-medium">● Trung lập</span>}
                                    </p>
                                  </div>
                               </div>
                               <span className="text-xs font-bold text-slate-600 bg-white px-3 py-1 rounded-full border border-slate-200 shadow-sm group-hover/item:border-blue-200">
                                 {user.count}
                               </span>
                            </div>
                          )) : (
                            <div className="flex flex-col items-center justify-center h-32 text-slate-400 gap-2">
                              <Users className="w-8 h-8 opacity-20" />
                              <p className="text-sm italic">Chưa có dữ liệu người dùng nổi bật.</p>
                            </div>
                          )}
                       </div>
                    </div>

                    <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100 relative group">
                       <div className="absolute top-6 right-6 text-[10px] text-slate-400 font-medium bg-slate-50 px-2 py-1 rounded-full border border-slate-100 opacity-0 group-hover:opacity-100 transition-opacity">
                           🖱️ Nhấn Emoji để lọc
                       </div>
                       <h3 className="font-bold text-lg text-slate-800 mb-4 flex items-center gap-2">
                         <Smile className="w-5 h-5 text-yellow-500" /> Top Emoji phổ biến
                       </h3>
                       <div className="h-64 w-full">
                         {emojiData.length > 0 ? (
                           <ResponsiveContainer width="100%" height="100%">
                             <BarChart data={emojiData.slice(0, 7)} layout="vertical" margin={{ left: 0, right: 20 }}>
                               <XAxis type="number" hide />
                               <YAxis dataKey="emoji" type="category" width={40} tick={{ fontSize: 20 }} axisLine={false} tickLine={false} />
                               <RechartsTooltip cursor={{ fill: 'transparent' }} contentStyle={{ borderRadius: '8px' }} />
                               <Bar dataKey="count" fill="#fbbf24" radius={[0, 6, 6, 0]} barSize={24} background={{ fill: '#f8fafc', radius: [0,6,6,0] }} onClick={handleEmojiClick} className="cursor-pointer">
                                  {emojiData.map((entry, index) => (<Cell key={`cell-${index}`} fill="#fbbf24" className="hover:opacity-80 transition-opacity cursor-pointer"/>))}
                               </Bar>
                             </BarChart>
                           </ResponsiveContainer>
                         ) : (
                           <EmptyState icon={Smile} message="Không tìm thấy Emoji nào trong các bình luận." />
                         )}
                       </div>
                    </div>
                </div>
             </div>
          )}

        </div>

        {/* --- CỘT PHẢI (CHATBOT - LUÔN HIỂN THỊ) --- */}
        <div className="lg:col-span-4">
          <div className="sticky top-6 h-[calc(100vh-40px)] flex flex-col">
             <div className="flex-1 min-h-0 bg-white rounded-3xl shadow-sm border border-slate-100 overflow-hidden flex flex-col">
                <ChatWindow taskId={taskId} />
             </div>
             <div className="mt-4 p-5 bg-blue-50 text-blue-800 rounded-2xl text-sm border border-blue-100 shadow-sm">
                <strong className="flex items-center gap-2">💡 Gợi ý câu hỏi:</strong>
                <ul className="list-disc ml-4 mt-3 space-y-2 text-slate-600">
                   <li>Có vấn đề gì tiêu cực không?</li>
                   <li>Mọi người đang tranh luận về vấn đề gì?</li>
                   <li>Có từ khóa nào xuất hiện nhiều nhất?</li>
                </ul>
             </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}