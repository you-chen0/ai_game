import React from 'react';
import { motion } from 'framer-motion';
import { User, Brain, Heart } from 'lucide-react';

interface ProgressBarProps {
  progress: number;
  attributes: {
    courage: number;
    wisdom: number;
    kindness: number;
  };
}

export const ProgressBar: React.FC<ProgressBarProps> = ({ progress, attributes }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card space-y-4"
    >
      {/* 故事进度 */}
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-white/70">故事进度</span>
          <span className="text-accent-yellow font-semibold">{Math.round(progress)}%</span>
        </div>
        <div className="w-full bg-white/10 rounded-full h-3 overflow-hidden">
          <motion.div
            className="h-full bg-gradient-to-r from-accent-yellow to-accent-orange"
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.5, ease: "easeOut" }}
          />
        </div>
      </div>

      {/* 属性条 */}
      <div className="space-y-3 pt-4 border-t border-white/10">
        <h3 className="text-sm font-semibold text-white/90">角色属性</h3>

        <div className="space-y-3">
          {/* 勇气 */}
          <div className="space-y-1">
            <div className="flex items-center justify-between text-xs">
              <div className="flex items-center space-x-2">
                <User size={14} className="text-red-400" />
                <span className="text-white/70">勇气</span>
              </div>
              <span className="text-white/90 font-medium">{attributes.courage}</span>
            </div>
            <div className="w-full bg-white/10 rounded-full h-2">
              <motion.div
                className="h-full bg-gradient-to-r from-red-500 to-orange-500 rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${attributes.courage}%` }}
                transition={{ duration: 0.5 }}
              />
            </div>
          </div>

          {/* 智慧 */}
          <div className="space-y-1">
            <div className="flex items-center justify-between text-xs">
              <div className="flex items-center space-x-2">
                <Brain size={14} className="text-blue-400" />
                <span className="text-white/70">智慧</span>
              </div>
              <span className="text-white/90 font-medium">{attributes.wisdom}</span>
            </div>
            <div className="w-full bg-white/10 rounded-full h-2">
              <motion.div
                className="h-full bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${attributes.wisdom}%` }}
                transition={{ duration: 0.5 }}
              />
            </div>
          </div>

          {/* 善良 */}
          <div className="space-y-1">
            <div className="flex items-center justify-between text-xs">
              <div className="flex items-center space-x-2">
                <Heart size={14} className="text-green-400" />
                <span className="text-white/70">善良</span>
              </div>
              <span className="text-white/90 font-medium">{attributes.kindness}</span>
            </div>
            <div className="w-full bg-white/10 rounded-full h-2">
              <motion.div
                className="h-full bg-gradient-to-r from-green-500 to-emerald-500 rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${attributes.kindness}%` }}
                transition={{ duration: 0.5 }}
              />
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};
