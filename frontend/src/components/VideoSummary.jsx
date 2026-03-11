import React from 'react';
import { Clock, MessageCircle, FileText, Target, AlignLeft, ChevronRight, Film, MapPin, AlertTriangle, Quote } from 'lucide-react';

// ==========================================
// HELPER: PARSE TEXT
// ==========================================
const stripMarkdown = (str) => {
  return str
    .replace(/^#{1,6}\s*/, '')
    .replace(/\*\*(.*?)\*\*/g, '$1')
    .replace(/__(.*?)__/g, '$1')
    .replace(/\*(.*?)\*/g, '$1')
    .replace(/`(.*?)`/g, '$1')
    .trim();
};

const parseContentLines = (text) => {
  if (!text) return [];
  const lines = text.split('\n');
  const blocks = [];
  let inAnswer = false;

  for (let i = 0; i < lines.length; i++) {
    const trimmed = lines[i].trim();
    if (!trimmed) { blocks.push({ type: 'empty' }); continue; }
    const clean = stripMarkdown(trimmed);

    // 1. Headings
    if (/^#{1,6}\s/.test(trimmed) || /^(?:\[TỔNG HỢP\]|\[TÓM TẮT\])/i.test(clean)) {
      inAnswer = false;
      const content = clean.replace(/^(?:\[TỔNG HỢP\]|\[TÓM TẮT\])\s*/i, '').trim();
      blocks.push({ type: 'heading', content: content || clean });
      continue;
    }
    // 2. Location
    if (/^(Đang ở:|Địa điểm:|Location:|\[ĐỊA ĐIỂM\])/i.test(clean)) {
      inAnswer = false;
      blocks.push({ type: 'location', content: clean.replace(/^(Đang ở:|Địa điểm:|Location:|\[ĐỊA ĐIỂM\])\s*/i, '').trim() });
      continue;
    }
    // 3. Blockquote
    if (/^>\s/.test(trimmed)) {
      inAnswer = false;
      blocks.push({ type: 'quote', content: clean.replace(/^>\s*/, '').trim() });
      continue;
    }
    // 4. QA Question
    if (clean.startsWith('[HỎI]') || /^\*\*\[HỎI\]/.test(trimmed)) {
      inAnswer = false;
      blocks.push({ type: 'qa-question', content: clean.replace(/^\[HỎI\]\s*/i, '').trim() });
      continue;
    }
    // 5. QA Answer
    if (clean.startsWith('[ĐÁP]')) {
      inAnswer = true;
      blocks.push({ type: 'qa-answer', lines: [clean.replace(/^\[ĐÁP\]\s*/i, '').trim()] });
      continue;
    }
    if (inAnswer) {
      const isNewBlock =
        /^\[.*?\]/.test(clean) ||
        /^(•\s*)?(Lưu ý|Note|Chú ý|Nguyên liệu|Ingredients)\s*:/i.test(clean) ||
        /^[•\-*]\s/.test(trimmed);
      if (!isNewBlock) {
        const last = blocks[blocks.length - 1];
        if (last?.type === 'qa-answer') { last.lines.push(clean); }
        else { blocks.push({ type: 'qa-answer', lines: [clean] }); }
        continue;
      }
      inAnswer = false;
    }
    // 6. Note
    if (/^(•\s*)?(Lưu ý|Note|Chú ý)\s*:/i.test(clean)) {
      blocks.push({ type: 'note', content: clean.replace(/^(•\s*)?(Lưu ý|Note|Chú ý)\s*:\s*/i, '') });
      continue;
    }
    // 6b. "Nguyên liệu: ..." plain text → section-header + bullet
    const nlRegex = /^(?:\[?(?:•\s*)?(?:Nguyên liệu|Ingredients)\]?\s*[:\-]?\s*)+/i;
    
    if (nlRegex.test(clean)) {
      // Lệnh replace này sẽ gọt sạch sành sanh mọi chữ "Nguyên liệu", dấu hai chấm, dấu ngoặc ở đầu
      let ingredientContent = clean.replace(nlRegex, '').trim();
      
      // Đề phòng AI bọc cả câu bằng ngoặc vuông, ta xóa nốt dấu "]" ở cuối
      ingredientContent = ingredientContent.replace(/\]$/, '').trim();

      // Render khối Tiêu đề (xanh đậm)
      blocks.push({ type: 'section-header', content: 'NGUYÊN LIỆU' });
      
      // Render khối Nội dung (xanh nhạt) với phần text đã được gọt sạch sẽ
      if (ingredientContent) {
        blocks.push({ type: 'section-highlight', content: ingredientContent });
      }
      continue;
    }
    // 7. [TAG] labels
    const tagMatch = clean.match(/^\[(.*?)\]/);
    if (tagMatch) {
      const tagText = tagMatch[1];
      let contentText = clean.replace(tagMatch[0], '').trim().replace(/^[:\-]\s*/, '').replace(/:\s*$/, '').trim();
      const isHeader =
        contentText === '' ||
        (clean.length <= 100 && /^(TIÊU ĐIỂM|NẠN NHÂN|DIỄN BIẾN|HẬU QUẢ|PHÁP LÝ|GIỚI THIỆU|NGUYÊN LIỆU|HƯỚNG DẪN|CÁCH LÀM|THỰC HIỆN|BƯỚC)/i.test(tagText));
      blocks.push({
        type: isHeader ? 'section-header' : 'section-highlight',
        content: isHeader && contentText === '' ? tagText : contentText,
      });
      continue;
    }
    // 8. Bullet / Plain
    if (/^[•\-*]\s/.test(trimmed)) {
      blocks.push({ type: 'bullet', content: clean.replace(/^[•\-*]\s/, '') });
      continue;
    }
    blocks.push({ type: 'plain', content: clean });
  }
  return blocks;
};

// ==========================================
// RENDER BLOCK ĐẶC BIỆT (dùng chung, không xử lý bullet/plain)
// ==========================================
const renderSpecialBlock = (block, idx) => {
  if (block.type === 'heading') return (
    <div key={idx} className="mt-6 mb-4 first:mt-0">
      <div className="flex items-center gap-3 bg-gradient-to-r from-slate-800 to-slate-700 text-white rounded-2xl px-5 py-3.5 shadow-md">
        <span className="text-base font-extrabold tracking-wide uppercase leading-snug">{block.content}</span>
      </div>
    </div>
  );

  if (block.type === 'location') return (
    <div key={idx} className="flex items-center gap-3 bg-gradient-to-r from-emerald-50 to-teal-50 border border-emerald-200 rounded-xl px-4 py-3 mt-3 mb-2 shadow-sm w-fit">
      <MapPin className="text-emerald-500 w-5 h-5 flex-shrink-0" />
      <div>
        <span className="text-[10px] font-bold text-emerald-600 uppercase tracking-widest block">Địa điểm</span>
        <span className="text-slate-800 font-bold text-sm">{block.content}</span>
      </div>
    </div>
  );

  if (block.type === 'quote') return (
    <div key={idx} className="flex items-start gap-2.5 my-4 border-l-4 border-slate-300 bg-slate-50 rounded-r-xl px-4 py-3">
      <Quote className="w-4 h-4 text-slate-400 mt-0.5 flex-shrink-0" />
      <p className="text-slate-500 italic text-sm">{block.content}</p>
    </div>
  );

  if (block.type === 'section-header') return (
    <div key={idx} className="mt-4 mb-2 first:mt-0">
      <div className="inline-flex items-center bg-gradient-to-r from-indigo-600 to-blue-500 text-white rounded-xl px-4 py-2 shadow-md">
        <h4 className="font-bold text-sm md:text-[15px] uppercase tracking-wide">{block.content}</h4>
      </div>
    </div>
  );

  if (block.type === 'section-highlight') return (
    <div key={idx} className="flex items-start gap-3 bg-gradient-to-r from-blue-50 via-indigo-50 to-blue-50 border border-blue-200 rounded-xl px-4 py-3.5 shadow-sm mt-2">
      <p className="text-slate-800 text-sm leading-relaxed font-bold mt-0.5">{block.content}</p>
    </div>
  );

  if (block.type === 'qa-question') return (
    <div key={idx} className="flex items-start gap-3 bg-amber-50 border-l-4 border-amber-400 rounded-r-xl px-4 py-3.5 mt-5 shadow-sm">
      <div className="w-7 h-7 rounded-full bg-amber-400 flex items-center justify-center flex-shrink-0 mt-0.5 shadow-sm">
        <span className="text-white font-black text-xs">Q</span>
      </div>
      <p className="text-slate-800 text-sm leading-relaxed font-semibold">{block.content}</p>
    </div>
  );

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

  if (block.type === 'note') return (
    <div key={idx} className="flex items-start gap-3 bg-orange-50 border border-orange-200 rounded-xl px-4 py-3 shadow-sm mt-2">
      <AlertTriangle className="text-orange-500 w-5 h-5 flex-shrink-0 mt-0.5" />
      <p className="text-orange-800 text-sm leading-relaxed font-medium">{block.content}</p>
    </div>
  );

  return null;
};

// ==========================================
// SmartTextRenderer: bullet/plain có ChevronRight
// ==========================================
const SmartTextRenderer = ({ content }) => {
  const blocks = parseContentLines(content);
  return (
    <div className="space-y-1.5">
      {blocks.map((block, idx) => {
        if (block.type === 'empty') return <div key={idx} className="h-2" />;
        if (block.type === 'bullet' || block.type === 'plain') return (
          <div 
            key={idx} 
            className="group flex items-start gap-3.5 px-4 py-3 bg-white border border-slate-200/80 rounded-xl shadow-[0_2px_8px_-4px_rgba(0,0,0,0.05)] hover:shadow-[0_4px_16px_-4px_rgba(59,130,246,0.2)] hover:border-blue-300 hover:bg-gradient-to-r hover:from-blue-50/40 hover:to-white transition-all duration-300"
          >
            {/* Box bọc Icon: Đổi màu nền, viền và text khi hover */}
            <div className="flex items-center justify-center w-6 h-6 mt-0.5 rounded-full bg-blue-50 border border-blue-200 text-blue-600 group-hover:bg-blue-500 group-hover:text-white group-hover:border-blue-500 group-hover:scale-110 shadow-sm transition-all duration-300 flex-shrink-0">
              <ChevronRight className="w-3.5 h-3.5" strokeWidth={3} />
            </div>
            {/* Phần Text: Đậm lên và trượt nhẹ sang phải khi hover */}
            <p className="text-slate-700 text-[14.5px] leading-relaxed group-hover:text-slate-900 group-hover:translate-x-1 transition-all duration-300">
              {block.content}
            </p>
          </div>
        );
        return renderSpecialBlock(block, idx);
      })}
    </div>
  );
};

// ==========================================
// PlainTextRenderer: dành cho TimelineView
// bullet/plain → text thuần (ChevronRight đã có bọc ngoài)
// block đặc biệt → renderSpecialBlock trực tiếp (không re-encode string)
// ==========================================
const PlainTextRenderer = ({ content }) => {
  const blocks = parseContentLines(content);
  return (
    <div className="space-y-1.5">
      {blocks.map((block, idx) => {
        if (block.type === 'empty') return <div key={idx} className="h-2" />;
        if (block.type === 'bullet' || block.type === 'plain') return (
          <p key={idx} className="text-slate-700 text-sm leading-relaxed">{block.content}</p>
        );
        return renderSpecialBlock(block, idx);
      })}
    </div>
  );
};

// ==========================================
// CÁC VIEW COMPONENT
// ==========================================
const TimelineView = ({ timeline }) => {
  if (!timeline || timeline.length === 0) return (
    <div className="flex flex-col items-center justify-center py-16 text-slate-400">
      <Clock className="w-12 h-12 mb-3 opacity-20" />
      <p className="italic text-sm">Không có dữ liệu timeline.</p>
    </div>
  );

  return (
    <div className="relative border-l-2 border-blue-100 ml-4 pl-8 space-y-10">
      {timeline.map((item, idx) => (
        <div key={idx} className="relative">
          <div className="absolute -left-[41px] top-0 w-5 h-5 bg-white border-4 border-blue-500 rounded-full shadow-sm" />
          <div className="flex items-center gap-3 mb-3">
            <span className="px-3 py-1 bg-blue-50 text-blue-700 text-xs font-bold rounded-lg shadow-sm font-mono">{item.time}</span>
            {item.label && <h4 className="font-bold text-slate-800 uppercase tracking-wide text-sm">{item.label}</h4>}
          </div>
          <div className="bg-slate-50 border border-slate-100 rounded-2xl p-5 space-y-3">
            {item?.points?.map((point, pIdx) => {
              // Kiểm tra block đầu tiên: nếu là block đặc biệt thì KHÔNG bọc ChevronRight
              const firstBlock = parseContentLines(point)[0];
              const isSpecial = firstBlock &&
                firstBlock.type !== 'bullet' &&
                firstBlock.type !== 'plain' &&
                firstBlock.type !== 'empty';

              if (isSpecial) return <PlainTextRenderer key={pIdx} content={point} />;

              return (
                <div key={pIdx} className="flex items-start gap-3">
                  <ChevronRight className="w-4 h-4 text-blue-400 mt-1 flex-shrink-0" />
                  <PlainTextRenderer content={point} />
                </div>
              );
            })}
            {item?.content && <SmartTextRenderer content={item.content} />}
          </div>
        </div>
      ))}
    </div>
  );
};

const TalkshowView = ({ content, guests }) => {
  if (!content) return (
    <div className="flex flex-col items-center justify-center py-16 text-slate-400">
      <MessageCircle className="w-12 h-12 mb-3 opacity-20" />
      <p className="italic text-sm">Không có dữ liệu talkshow / phỏng vấn.</p>
    </div>
  );
  return (
    <div className="space-y-3">
      {guests && guests.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-4 p-4 bg-purple-50 rounded-xl border border-purple-100">
          <span className="text-xs font-bold text-purple-700 uppercase tracking-wide w-full mb-1">Khách mời</span>
          {guests.map((g, i) => (
            <span key={i} className="px-3 py-1 bg-white border border-purple-200 text-purple-700 rounded-full text-xs font-medium shadow-sm">{g}</span>
          ))}
        </div>
      )}
      <SmartTextRenderer content={content} />
    </div>
  );
};

const NewsView = ({ items, content }) => {
  if (!items?.length && !content) return (
    <div className="flex flex-col items-center justify-center py-16 text-slate-400">
      <FileText className="w-12 h-12 mb-3 opacity-20" />
      <p className="italic text-sm">Không có dữ liệu tin tức / tổng hợp.</p>
    </div>
  );
  return <SmartTextRenderer content={content || (items || []).join('\n')} />;
};

const ReportView = ({ sections, content }) => {
  if (!sections?.length && !content) return (
    <div className="flex flex-col items-center justify-center py-16 text-slate-400">
      <FileText className="w-12 h-12 mb-3 opacity-20" />
      <p className="italic text-sm">Không có dữ liệu phóng sự / báo cáo.</p>
    </div>
  );
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
// COMPONENT CHÍNH EXPORT
// ==========================================
export default function VideoSummaryPanel({ videoSummary }) {
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
      <div className="flex items-center gap-3 mb-8">
        <div className={`p-3 rounded-xl ${cfg.bg} ${cfg.text}`}>{cfg.icon}</div>
        <div>
          <h3 className="font-bold text-xl text-slate-800">Bản tóm tắt</h3>
          <p className="text-sm text-slate-500">{cfg.label}{videoSummary.category ? ` · ${videoSummary.category}` : ''}</p>
        </div>
      </div>

      {type === 'TIMELINE' && <TimelineView timeline={videoSummary.timeline} />}
      {type === 'TALKSHOW' && <TalkshowView content={videoSummary.content} guests={videoSummary.guests} />}
      {type === 'NEWS' && <NewsView items={videoSummary.items} content={videoSummary.content} />}
      {type === 'REPORT' && <ReportView sections={videoSummary.sections} content={videoSummary.content} />}
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
}