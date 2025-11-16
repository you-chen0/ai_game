export type ChoiceNecessity = 'mandatory' | 'optional' | 'forced';

export interface Choice {
  id: string;
  text: string;
  type: 'action' | 'dialogue' | 'item' | 'emotion';
  consequence?: string;
  story_impact?: number;
  necessity?: ChoiceNecessity;
  reasoning?: string;
}

export interface StoryOutline {
  characters: Array<{
    name: string;
    description: string;
  }>;
  key_items: Array<{
    name: string;
    description: string;
  }>;
  important_npcs: Array<{
    name: string;
    role: string;
    description: string;
  }>;
  key_decisions: string[];
  success_conditions: string;
  failure_conditions: string;
  plot_threads: string[];
}

export interface StoryScene {
  id: string;
  image_path: string;
  story_text: string;
  genre: string;
  choices: Choice[];
  is_ending?: boolean;
  ending_type?: string;
}

export interface GameStateMetadata {
  last_choice_count?: number;
  last_choice_necessity?: string;
}

export interface StoryState {
  current_scene: StoryScene;
  choice_history: string[];
  story_progress: number;
  scene_count: number;
  max_scenes: number;
  is_ending: boolean;
  story_theme: string;
  user_attributes: {
    courage: number;
    wisdom: number;
    kindness: number;
  };
  story_outline?: StoryOutline;
  item_states?: Record<string, any>;
  npc_relations?: Record<string, any>;
  danger_level?: number;
  consecutive_failures?: number;
  metadata?: GameStateMetadata;
}

export interface ImageAnalysisResult {
  scene_description: string;
  characters: Array<{
    name: string;
    description: string;
    emotion: string;
  }>;
  key_objects: string[];
  color_style: {
    dominant_colors: string[];
    style: string;
  };
  story_elements: string;
  emotional_tone: string;
  genre_suggestion: string;
  story_outline?: StoryOutline;
}

export type GamePhase =
  | 'upload'
  | 'analyzing'
  | 'generating_story'
  | 'playing'
  | 'choosing'
  | 'generating_scene'
  | 'ending'
  | 'viewing_complete_story';

export interface GameStore {
  phase: GamePhase;
  currentState: StoryState | null;
  isLoading: boolean;
  error: string | null;
  imageFile: File | null;
  imageUrl: string | null;
  stateId: string | null;

  // Actions
  setPhase: (phase: GamePhase) => void;
  setCurrentState: (state: StoryState) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setImageFile: (file: File | null) => void;
  setImageUrl: (url: string | null) => void;
  setStateId: (id: string | null) => void;
  reset: () => void;
}
