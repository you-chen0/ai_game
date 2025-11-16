import React from 'react';
import { motion } from 'framer-motion';
import { Choice } from '@/types/story';
import { Zap, MessageCircle, Package, Heart } from 'lucide-react';

interface ChoiceButtonProps {
  choice: Choice;
  index: number;
  onSelect: (choice: Choice) => void;
  disabled?: boolean;
  totalChoices?: number; // 新增：总选择数量
}

const getChoiceIcon = (type: string) => {
  switch (type) {
    case 'action':
      return <Zap size={20} />;
    case 'dialogue':
      return <MessageCircle size={20} />;
    case 'item':
      return <Package size={20} />;
    case 'emotion':
      return <Heart size={20} />;
    default:
      return <Zap size={20} />;
  }
};

const getChoiceColor = (type: string) => {
  switch (type) {
    case 'action':
      return 'from-red-500/20 to-orange-500/20 hover:from-red-500/40 hover:to-orange-500/40';
    case 'dialogue':
      return 'from-blue-500/20 to-cyan-500/20 hover:from-blue-500/40 hover:to-cyan-500/40';
    case 'item':
      return 'from-purple-500/20 to-pink-500/20 hover:from-purple-500/40 hover:to-pink-500/40';
    case 'emotion':
      return 'from-green-500/20 to-emerald-500/20 hover:from-green-500/40 hover:to-emerald-500/40';
    default:
      return 'from-primary-blue/50 to-primary-purple/50';
  }
};

// 根据选择必要性获取样式
const getNecessityStyle = (necessity?: string, totalChoices?: number) => {
  if (totalChoices === 1) {
    return 'border-accent-yellow/60 shadow-lg shadow-accent-yellow/20';
  }
  if (necessity === 'mandatory') {
    return 'border-red-500/60 shadow-lg shadow-red-500/20';
  }
  if (necessity === 'forced') {
    return 'border-accent-orange/60 shadow-lg shadow-accent-orange/20';
  }
  return '';
};

export const ChoiceButton: React.FC<ChoiceButtonProps> = ({
  choice,
  index,
  onSelect,
  disabled = false,
  totalChoices = 3
}) => {
  return (
    <motion.button
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      whileHover={!disabled ? { scale: 1.02 } : {}}
      whileTap={!disabled ? { scale: 0.98 } : {}}
      onClick={() => !disabled && onSelect(choice)}
      disabled={disabled}
      className={`
        text-left p-6 rounded-xl backdrop-blur-sm border transition-all duration-300 group relative overflow-hidden
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        ${getChoiceColor(choice.type)}
        ${getNecessityStyle(choice.necessity, totalChoices)}
        hover:shadow-2xl hover:border-white/40
        ${totalChoices === 1 ? 'w-full col-span-2' : 'w-full'}
      `}
    >
      {/* 背景动画 */}
      {!disabled && (
        <motion.div
          className="absolute inset-0 bg-gradient-to-r from-accent-yellow/0 to-accent-orange/0 group-hover:from-accent-yellow/10 group-hover:to-accent-orange/10"
          initial={{ x: '-100%' }}
          whileHover={{ x: '100%' }}
          transition={{ duration: 0.6 }}
        />
      )}

      <div className="relative flex items-start space-x-4">
        <div className="flex-shrink-0 mt-1">
          {getChoiceIcon(choice.type)}
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-sm font-bold text-accent-yellow">
              [{choice.id}]
            </span>
            <span className="text-xs px-2 py-1 rounded bg-white/10 text-white/70 uppercase tracking-wider">
              {choice.type}
            </span>
            {/* 单选提示 */}
            {totalChoices === 1 && (
              <span className="text-xs px-2 py-1 rounded bg-accent-yellow/20 text-accent-yellow">
                必须执行
              </span>
            )}
          </div>

          <p className="text-white font-medium leading-relaxed">
            {choice.text}
          </p>

          {choice.consequence && (
            <p className="mt-2 text-sm text-white/60 italic">
              {choice.consequence}
            </p>
          )}
        </div>
      </div>

      {/* 悬浮效果 */}
      {!disabled && (
        <motion.div
          className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-accent-yellow to-accent-orange"
          initial={{ scaleX: 0 }}
          whileHover={{ scaleX: 1 }}
          transition={{ duration: 0.3 }}
        />
      )}
    </motion.button>
  );
};
