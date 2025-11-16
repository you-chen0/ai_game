import React, { useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useGameStore } from '@/store/gameStore';
import { ImageUpload } from '@/components/ImageUpload';
import { StoryDisplay } from '@/components/StoryDisplay';
import { ChoiceButton } from '@/components/ChoiceButton';
import { ProgressBar } from '@/components/ProgressBar';
import { Choice } from '@/types/story';
import { uploadImage, startStory, continueStory, rollbackStory } from '@/services/api';

function App() {
  const {
    phase,
    currentState,
    isLoading,
    imageFile,
    imageUrl,
    stateId,
    setPhase,
    setCurrentState,
    setLoading,
    setError,
    setStateId,
    reset,
  } = useGameStore();

  const handleStartStory = useCallback(async () => {
    if (!imageFile) return;

    try {
      setLoading(true);
      setError(null);
      setPhase('analyzing');

      // 上传图片
      const uploadResult = await uploadImage(imageFile);

      setPhase('generating_story');

      // 开始故事
      const storyResult = await startStory(uploadResult.url);

      // 更新状态
      setCurrentState(storyResult.state);
      setStateId(storyResult.state_id);

      setPhase('playing');
      setLoading(false);
    } catch (error) {
      console.error('Error starting story:', error);
      setError('故事生成失败，请重试');
      setLoading(false);
      setPhase('upload');
    }
  }, [imageFile, setPhase, setLoading, setError, setCurrentState, setStateId]);

  const handleChoice = useCallback(async (choice: Choice) => {
    if (!stateId) {
      setError('游戏状态丢失，请重新开始');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setPhase('generating_scene');

      // 继续故事
      const storyResult = await continueStory(choice.id, stateId);

      // 更新状态
      setCurrentState(storyResult.state);
      setStateId(storyResult.state_id);

      setPhase('playing');
      setLoading(false);
    } catch (error) {
      console.error('Error continuing story:', error);
      setError('故事继续失败，请重试');
      setLoading(false);
    }
  }, [stateId, setPhase, setLoading, setError, setCurrentState, setStateId]);

  const handleViewCompleteStory = useCallback(() => {
    setPhase('viewing_complete_story');
  }, [setPhase]);

  const handleRollback = useCallback(async (targetStep: number) => {
    if (!stateId) {
      setError('游戏状态丢失，请重新开始');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      // 回溯到指定步骤
      const result = await rollbackStory(targetStep, stateId);

      // 更新状态
      setCurrentState(result.state);
      setStateId(result.state_id);

      setPhase('playing');
      setLoading(false);
    } catch (error) {
      console.error('Error rolling back story:', error);
      setError('回溯失败，请重试');
      setLoading(false);
    }
  }, [stateId, setPhase, setLoading, setError, setCurrentState, setStateId]);

  const renderContent = () => {
    switch (phase) {
      case 'upload':
        return (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="container mx-auto px-4 py-8"
          >
            <div className="text-center mb-8">
              <h1 className="text-4xl md:text-6xl font-bold text-gradient mb-4">
                交互式图片故事生成系统
              </h1>
              <p className="text-lg text-white/70">
                上传一张图片，开启你的专属冒险之旅
              </p>
            </div>

            <ImageUpload />

            {imageFile && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-8 text-center"
              >
                <button
                  onClick={handleStartStory}
                  disabled={isLoading}
                  className="btn-primary text-lg px-8 py-4 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? '生成中...' : '开始故事冒险'}
                </button>
              </motion.div>
            )}
          </motion.div>
        );

      case 'playing':
      case 'choosing':
        return (
          <div className="container mx-auto px-4 py-8">
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
              {/* 主要内容区 */}
              <div className="lg:col-span-3 space-y-6">
                {currentState && (
                  <>
                    <StoryDisplay
                      scene={currentState.current_scene}
                      isGenerating={isLoading}
                    />

                    {/* 选择区域 */}
                    <AnimatePresence>
                      {!isLoading && (
                        <motion.div
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          exit={{ opacity: 0, y: -20 }}
                          className="space-y-4"
                        >
                          {/* 检查故事是否结束 - 多种情况 */}
                          {(currentState.current_scene.is_ending ||
                            currentState.is_ending ||
                            currentState.scene_count >= currentState.max_scenes) ? (
                            /* 故事结束提示 */
                            <div className="card text-center py-12">
                              <motion.div
                                initial={{ scale: 0.8, opacity: 0 }}
                                animate={{ scale: 1, opacity: 1 }}
                                transition={{ duration: 0.5 }}
                              >
                                <h2 className="text-3xl font-bold text-gradient mb-4">
                                  🎭 故事结束
                                </h2>
                                <p className="text-white/70 text-lg mb-6">
                                  恭喜！你已经完成了这个精彩的故事冒险
                                </p>
                                <div className="flex justify-center space-x-4">
                                  <button
                                    onClick={handleViewCompleteStory}
                                    className="btn-secondary"
                                  >
                                    📖 查看完整故事
                                  </button>
                                  <button
                                    onClick={reset}
                                    className="btn-primary"
                                  >
                                    开始新故事
                                  </button>
                                </div>
                              </motion.div>
                            </div>
                          ) : (
                            <>
                              <h3 className="text-xl font-bold text-white/90 mb-4">
                                你的选择将决定故事的走向...
                              </h3>
                              <div className="space-y-3">
                                {currentState.current_scene.choices.map((choice, index) => (
                                  <ChoiceButton
                                    key={choice.id}
                                    choice={choice}
                                    index={index}
                                    onSelect={handleChoice}
                                    disabled={isLoading}
                                    totalChoices={currentState.current_scene.choices.length}
                                  />
                                ))}
                              </div>
                            </>
                          )}
                        </motion.div>
                      )}
                    </AnimatePresence>

                    {/* 加载状态 */}
                    <AnimatePresence>
                      {isLoading && (
                        <motion.div
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          exit={{ opacity: 0 }}
                          className="card text-center py-12"
                        >
                          <div className="flex flex-col items-center space-y-4">
                            <div className="flex space-x-2">
                              <div className="w-3 h-3 bg-accent-yellow rounded-full animate-bounce" />
                              <div className="w-3 h-3 bg-accent-yellow rounded-full animate-bounce delay-75" />
                              <div className="w-3 h-3 bg-accent-yellow rounded-full animate-bounce delay-150" />
                            </div>
                            <p className="text-white/70">
                              {(phase as any) === 'generating_scene' ? '正在生成新场景...' : '正在思考中...'}
                            </p>
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </>
                )}
              </div>

              {/* 侧边栏 */}
              <div className="lg:col-span-1">
                {currentState && (
                  <>
                    <ProgressBar
                      progress={currentState.story_progress}
                      attributes={currentState.user_attributes}
                    />

                    <motion.button
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      onClick={reset}
                      className="btn-secondary w-full mt-4"
                    >
                      重新开始
                    </motion.button>

                    <motion.button
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      onClick={handleViewCompleteStory}
                      className="btn-secondary w-full mt-4"
                    >
                      📖 查看完整故事
                    </motion.button>
                  </>
                )}
              </div>
            </div>
          </div>
        );

      case 'viewing_complete_story':
        return (
          <div className="container mx-auto px-4 py-8">
            <div className="max-w-4xl mx-auto">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="card"
              >
                <h1 className="text-3xl font-bold text-gradient mb-8 text-center">
                  📖 完整故事回顾
                </h1>

                {currentState?.scene_history && (
                  <div className="space-y-8">
                    {currentState.scene_history.map((scene, index) => (
                      <motion.div
                        key={scene.scene_id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="border-l-4 border-accent-yellow pl-6 py-4"
                      >
                        <div className="flex items-center justify-between mb-4">
                          <div className="flex items-center">
                            <div className="bg-accent-yellow text-primary-dark px-4 py-2 rounded-full font-bold mr-4">
                              步骤 {scene.step + 1}
                            </div>
                            <div className="text-white/60">
                              你选择了：{scene.user_choice}
                            </div>
                          </div>
                          <button
                            onClick={() => handleRollback(scene.step)}
                            disabled={isLoading}
                            className="btn-secondary text-sm px-4 py-2 disabled:opacity-50 disabled:cursor-not-allowed"
                            title="从这一步重新开始"
                          >
                            ⏪ 从此处重新开始
                          </button>
                        </div>

                        <div className="relative overflow-hidden rounded-xl mb-4">
                          <img
                            src={scene.image_path}
                            alt={`步骤 ${scene.step + 1}`}
                            className="w-full h-64 object-cover"
                          />
                        </div>

                        <div className="prose prose-invert max-w-none">
                          <p className="text-white/90 leading-relaxed whitespace-pre-wrap">
                            {scene.story_text}
                          </p>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                )}

                <div className="flex justify-center space-x-4 mt-8">
                  <button
                    onClick={() => setPhase('playing')}
                    className="btn-secondary"
                  >
                    ← 返回故事
                  </button>
                  <button
                    onClick={reset}
                    className="btn-primary"
                  >
                    开始新故事
                  </button>
                </div>
              </motion.div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen">
      {renderContent()}

      {/* 错误提示 */}
      <AnimatePresence>
        {useGameStore.getState().error && (
          <motion.div
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -50 }}
            className="fixed top-4 right-4 bg-error text-white px-6 py-3 rounded-lg shadow-lg"
          >
            {useGameStore.getState().error}
            <button
              onClick={() => useGameStore.getState().setError(null)}
              className="ml-4 text-white/80 hover:text-white"
            >
              ×
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default App;
