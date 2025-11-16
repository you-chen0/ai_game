import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion } from 'framer-motion';
import { Upload, Image as ImageIcon } from 'lucide-react';
import { useGameStore } from '@/store/gameStore';

export const ImageUpload: React.FC = () => {
  const { imageFile, imageUrl, setImageFile, setImageUrl } = useGameStore();

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) {
      setImageFile(file);
      const url = URL.createObjectURL(file);
      setImageUrl(url);
    }
  }, [setImageFile, setImageUrl]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif', '.webp']
    },
    multiple: false,
    maxSize: 10485760, // 10MB
  });

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full max-w-2xl mx-auto"
    >
      <div
        {...getRootProps()}
        className={`
          relative border-2 border-dashed rounded-xl p-12 text-center cursor-pointer
          transition-all duration-300 ease-in-out
          ${isDragActive
            ? 'border-accent-yellow bg-accent-yellow/10 scale-105'
            : 'border-white/30 hover:border-white/50 hover:bg-white/5'
          }
        `}
      >
        <input {...getInputProps()} />

        {imageUrl ? (
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="space-y-4"
          >
            <img
              src={imageUrl}
              alt="Uploaded"
              className="max-h-64 mx-auto rounded-lg shadow-2xl"
            />
            <p className="text-sm text-white/70">
              点击或拖拽更换图片
            </p>
          </motion.div>
        ) : (
          <motion.div
            initial={{ scale: 0.9 }}
            animate={{ scale: 1 }}
            className="space-y-6"
          >
            <motion.div
              animate={{
                scale: isDragActive ? 1.2 : 1,
                rotate: isDragActive ? 5 : 0
              }}
              transition={{ type: "spring", stiffness: 300 }}
            >
              {isDragActive ? (
                <ImageIcon size={80} className="mx-auto text-accent-yellow" />
              ) : (
                <Upload size={80} className="mx-auto text-white/50" />
              )}
            </motion.div>

            <div className="space-y-2">
              <h3 className="text-2xl font-bold text-gradient">
                {isDragActive ? '放开以上传图片' : '上传你的图片'}
              </h3>
              <p className="text-white/60">
                支持 JPG、PNG、GIF、WebP 格式，文件大小不超过 10MB
              </p>
            </div>
          </motion.div>
        )}
      </div>

      {imageFile && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-4 text-center"
        >
          <p className="text-sm text-white/70">
            文件名: {imageFile.name}
          </p>
        </motion.div>
      )}
    </motion.div>
  );
};
