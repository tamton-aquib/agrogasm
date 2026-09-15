export interface CommunityComment {
  id?: number;
  author: string;
  description: string;
  upvote: number;
  downvote: number;
  created_at?: string;
}

export interface Post {
  pid: number;
  author: string;
  title: string;
  description: string;
  upvote: number;
  downvote: number;
  reliability: string;
  created_at?: string;
  comments: CommunityComment[];
}

export interface CommunityData {
  posts: Post[];
  global: {
    threshold: number;
  };
}

export type SortMode = 'new' | 'old' | 'top';
export type ReliabilityFilter = '' | 'new' | 'reliable' | 'unsure' | 'unreliable';
