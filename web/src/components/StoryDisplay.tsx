import React from 'react';
import { motion } from 'framer-motion';
import { StoryScene } from '@/types/story';

interface StoryDisplayProps {
  scene: StoryScene;
  isGenerating?: boolean;
}

export const StoryDisplay: React.FC<StoryDisplayProps> = ({ scene, isGenerating = false }) => {
  return (
    <motion.div
      key={scene.id}
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      {/* 场景图片 */}
      <div className="relative overflow-hidden rounded-xl">
        <motion.img
          src={scene.image_path}
          alt="Scene"
          className="w-full h-64 md:h-96 object-cover"
          initial={{ scale: 1.1 }}
          animate={{ scale: 1 }}
          transition={{ duration: 0.5 }}
        />
        {isGenerating && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="absolute inset-0 bg-primary-dark/50 flex items-center justify-center backdrop-blur-sm"
          >
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-accent-yellow rounded-full animate-bounce" />
              <div className="w-3 h-3 bg-accent-yellow rounded-full animate-bounce delay-75" />
              <div className="w-3 h-3 bg-accent-yellow rounded-full animate-bounce delay-150" />
            </div>
          </motion.div>
        )}
      </div>

      {/* 故事文本 */}
      <motion.div
        className="card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <div className="prose prose-invert max-w-none">
          <p className="text-lg leading-relaxed text-white/90 whitespace-pre-wrap">
            {scene.story_text}
          </p>
        </div>

        {/* 进度指示器 */}
        <div className="mt-6 space-y-2">
          <div className="flex justify-between text-sm text-white/60">
            <span>故事进度</span>
            <span>{scene.id}</span>
          </div>
          <div className="w-full bg-white/10 rounded-full h-2 overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-accent-yellow to-accent-orange"
              initial={{ width: 0 }}
              animate={{ width: '100%' }}
              transition={{ duration: 0.5 }}
            />
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};
