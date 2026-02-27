import React from 'react';
import { Heart } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="w-full bg-white border-t border-slate-200 mt-auto">
      <div className="max-w-7xl mx-auto py-8 px-4 flex flex-col md:flex-row items-center justify-between gap-4 text-slate-500 text-sm">
        <p>© 2024 YT Analyst AI. All rights reserved.</p>
        
        <div className="flex items-center gap-1">
          Made with <Heart className="w-4 h-4 text-red-500 fill-current" /> by Developer
        </div>

        <div className="flex gap-6">
          <a href="#" className="hover:text-blue-600 transition">Điều khoản</a>
          <a href="#" className="hover:text-blue-600 transition">Bảo mật</a>
          <a href="#" className="hover:text-blue-600 transition">Liên hệ</a>
        </div>
      </div>
    </footer>
  );
}