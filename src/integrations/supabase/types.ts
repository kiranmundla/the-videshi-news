export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  // Allows to automatically instantiate createClient with right options
  // instead of createClient<Database, { PostgrestVersion: 'XX' }>(URL, KEY)
  __InternalSupabase: {
    PostgrestVersion: "14.5"
  }
  public: {
    Tables: {
      articles: {
        Row: {
          article_type: string
          body: string
          category: string
          created_at: string | null
          featured_score: number
          id: string
          image_caption: string | null
          image_credit: string | null
          image_score: number | null
          image_url: string | null
          image_verified: boolean | null
          is_pinned_featured: boolean
          is_published: boolean | null
          nri_angle: string | null
          pinned_until: string | null
          published_at: string | null
          read_time_min: number | null
          slug: string | null
          sources_used: Json | null
          story_group_id: string | null
          subject_name: string | null
          subject_type: string | null
          summary: string
          tags: string[] | null
          title: string
          updated_at: string | null
          word_count: number | null
        }
        Insert: {
          article_type?: string
          body: string
          category: string
          created_at?: string | null
          featured_score?: number
          id?: string
          image_caption?: string | null
          image_credit?: string | null
          image_score?: number | null
          image_url?: string | null
          image_verified?: boolean | null
          is_pinned_featured?: boolean
          is_published?: boolean | null
          nri_angle?: string | null
          pinned_until?: string | null
          published_at?: string | null
          read_time_min?: number | null
          slug?: string | null
          sources_used?: Json | null
          story_group_id?: string | null
          subject_name?: string | null
          subject_type?: string | null
          summary: string
          tags?: string[] | null
          title: string
          updated_at?: string | null
          word_count?: number | null
        }
        Update: {
          article_type?: string
          body?: string
          category?: string
          created_at?: string | null
          featured_score?: number
          id?: string
          image_caption?: string | null
          image_credit?: string | null
          image_score?: number | null
          image_url?: string | null
          image_verified?: boolean | null
          is_pinned_featured?: boolean
          is_published?: boolean | null
          nri_angle?: string | null
          pinned_until?: string | null
          published_at?: string | null
          read_time_min?: number | null
          slug?: string | null
          sources_used?: Json | null
          story_group_id?: string | null
          subject_name?: string | null
          subject_type?: string | null
          summary?: string
          tags?: string[] | null
          title?: string
          updated_at?: string | null
          word_count?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "articles_story_group_id_fkey"
            columns: ["story_group_id"]
            isOneToOne: false
            referencedRelation: "story_groups"
            referencedColumns: ["id"]
          },
        ]
      }
      articles_pipeline: {
        Row: {
          body: string
          created_at: string
          diaspora_angle: string | null
          headline: string
          id: string
          is_featured: boolean
          published_at: string | null
          reviewed_at: string | null
          slug: string | null
          sources: Json
          status: string
          subheadline: string | null
          tags: string[]
          topic_id: string | null
          updated_at: string
          urgency: string | null
          vertical: string
          word_count: number | null
        }
        Insert: {
          body: string
          created_at?: string
          diaspora_angle?: string | null
          headline: string
          id?: string
          is_featured?: boolean
          published_at?: string | null
          reviewed_at?: string | null
          slug?: string | null
          sources?: Json
          status?: string
          subheadline?: string | null
          tags?: string[]
          topic_id?: string | null
          updated_at?: string
          urgency?: string | null
          vertical: string
          word_count?: number | null
        }
        Update: {
          body?: string
          created_at?: string
          diaspora_angle?: string | null
          headline?: string
          id?: string
          is_featured?: boolean
          published_at?: string | null
          reviewed_at?: string | null
          slug?: string | null
          sources?: Json
          status?: string
          subheadline?: string | null
          tags?: string[]
          topic_id?: string | null
          updated_at?: string
          urgency?: string | null
          vertical?: string
          word_count?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "articles_pipeline_topic_id_fkey"
            columns: ["topic_id"]
            isOneToOne: true
            referencedRelation: "topics"
            referencedColumns: ["id"]
          },
        ]
      }
      carousel_images: {
        Row: {
          caption: string | null
          created_at: string
          credit: string | null
          date: string
          id: string
          image_url: string
          location: string | null
          position: number
          search_term: string | null
        }
        Insert: {
          caption?: string | null
          created_at?: string
          credit?: string | null
          date: string
          id?: string
          image_url: string
          location?: string | null
          position: number
          search_term?: string | null
        }
        Update: {
          caption?: string | null
          created_at?: string
          credit?: string | null
          date?: string
          id?: string
          image_url?: string
          location?: string | null
          position?: number
          search_term?: string | null
        }
        Relationships: []
      }
      dead_letter_queue: {
        Row: {
          agent: string | null
          can_retry: boolean
          created_at: string
          error_history: string[] | null
          failure_reason: string | null
          id: string
          original_job_id: string | null
          story_brief: Json | null
        }
        Insert: {
          agent?: string | null
          can_retry?: boolean
          created_at?: string
          error_history?: string[] | null
          failure_reason?: string | null
          id?: string
          original_job_id?: string | null
          story_brief?: Json | null
        }
        Update: {
          agent?: string | null
          can_retry?: boolean
          created_at?: string
          error_history?: string[] | null
          failure_reason?: string | null
          id?: string
          original_job_id?: string | null
          story_brief?: Json | null
        }
        Relationships: []
      }
      feed_sources: {
        Row: {
          avg_items_per_day: number | null
          created_at: string
          fetch_interval_min: number
          id: string
          is_active: boolean
          last_fetched_at: string | null
          layer: string
          name: string
          tier: string
          type: string
          url: string
          verticals: string[]
        }
        Insert: {
          avg_items_per_day?: number | null
          created_at?: string
          fetch_interval_min?: number
          id?: string
          is_active?: boolean
          last_fetched_at?: string | null
          layer: string
          name: string
          tier?: string
          type: string
          url: string
          verticals?: string[]
        }
        Update: {
          avg_items_per_day?: number | null
          created_at?: string
          fetch_interval_min?: number
          id?: string
          is_active?: boolean
          last_fetched_at?: string | null
          layer?: string
          name?: string
          tier?: string
          type?: string
          url?: string
          verticals?: string[]
        }
        Relationships: []
      }
      pipeline_alerts: {
        Row: {
          agent: string
          created_at: string
          error_type: string | null
          id: string
          job_id: string | null
          message: string
          resolved: boolean
          severity: string
        }
        Insert: {
          agent: string
          created_at?: string
          error_type?: string | null
          id?: string
          job_id?: string | null
          message: string
          resolved?: boolean
          severity: string
        }
        Update: {
          agent?: string
          created_at?: string
          error_type?: string | null
          id?: string
          job_id?: string | null
          message?: string
          resolved?: boolean
          severity?: string
        }
        Relationships: []
      }
      pipeline_run_log: {
        Row: {
          created_at: string
          id: string
          items_processed: number
          notes: string | null
          stage: string
          status: string
        }
        Insert: {
          created_at?: string
          id?: string
          items_processed?: number
          notes?: string | null
          stage: string
          status?: string
        }
        Update: {
          created_at?: string
          id?: string
          items_processed?: number
          notes?: string | null
          stage?: string
          status?: string
        }
        Relationships: []
      }
      pipeline_runs: {
        Row: {
          articles_created: number | null
          error_message: string | null
          finished_at: string | null
          groups_created: number | null
          id: string
          raw_fetched: number | null
          raw_new: number | null
          run_type: string
          started_at: string | null
          status: string
        }
        Insert: {
          articles_created?: number | null
          error_message?: string | null
          finished_at?: string | null
          groups_created?: number | null
          id?: string
          raw_fetched?: number | null
          raw_new?: number | null
          run_type: string
          started_at?: string | null
          status: string
        }
        Update: {
          articles_created?: number | null
          error_message?: string | null
          finished_at?: string | null
          groups_created?: number | null
          id?: string
          raw_fetched?: number | null
          raw_new?: number | null
          run_type?: string
          started_at?: string | null
          status?: string
        }
        Relationships: []
      }
      raw_articles: {
        Row: {
          created_at: string | null
          credibility: string | null
          description: string | null
          fetched_at: string | null
          id: string
          image_url: string | null
          processed: boolean | null
          published_at: string | null
          source_name: string
          source_url: string | null
          title: string
          url: string
        }
        Insert: {
          created_at?: string | null
          credibility?: string | null
          description?: string | null
          fetched_at?: string | null
          id?: string
          image_url?: string | null
          processed?: boolean | null
          published_at?: string | null
          source_name: string
          source_url?: string | null
          title: string
          url: string
        }
        Update: {
          created_at?: string | null
          credibility?: string | null
          description?: string | null
          fetched_at?: string | null
          id?: string
          image_url?: string | null
          processed?: boolean | null
          published_at?: string | null
          source_name?: string
          source_url?: string | null
          title?: string
          url?: string
        }
        Relationships: []
      }
      raw_signals: {
        Row: {
          feed_source_id: string | null
          fetched_at: string
          id: string
          is_processed: boolean
          original_url: string
          published_at: string | null
          title: string
          topic_id: string | null
          url_hash: string
        }
        Insert: {
          feed_source_id?: string | null
          fetched_at?: string
          id?: string
          is_processed?: boolean
          original_url: string
          published_at?: string | null
          title: string
          topic_id?: string | null
          url_hash: string
        }
        Update: {
          feed_source_id?: string | null
          fetched_at?: string
          id?: string
          is_processed?: boolean
          original_url?: string
          published_at?: string | null
          title?: string
          topic_id?: string | null
          url_hash?: string
        }
        Relationships: [
          {
            foreignKeyName: "raw_signals_feed_source_id_fkey"
            columns: ["feed_source_id"]
            isOneToOne: false
            referencedRelation: "feed_sources"
            referencedColumns: ["id"]
          },
        ]
      }
      source_hunts: {
        Row: {
          content: string | null
          feed_source_id: string | null
          fetched_at: string
          id: string
          is_used: boolean
          published_at: string | null
          relevance_score: number | null
          title: string
          topic_id: string | null
          url: string
        }
        Insert: {
          content?: string | null
          feed_source_id?: string | null
          fetched_at?: string
          id?: string
          is_used?: boolean
          published_at?: string | null
          relevance_score?: number | null
          title: string
          topic_id?: string | null
          url: string
        }
        Update: {
          content?: string | null
          feed_source_id?: string | null
          fetched_at?: string
          id?: string
          is_used?: boolean
          published_at?: string | null
          relevance_score?: number | null
          title?: string
          topic_id?: string | null
          url?: string
        }
        Relationships: [
          {
            foreignKeyName: "source_hunts_feed_source_id_fkey"
            columns: ["feed_source_id"]
            isOneToOne: false
            referencedRelation: "feed_sources"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "source_hunts_topic_id_fkey"
            columns: ["topic_id"]
            isOneToOne: false
            referencedRelation: "topics"
            referencedColumns: ["id"]
          },
        ]
      }
      story_clusters: {
        Row: {
          article_ids: string[] | null
          auto_generated: boolean | null
          created_at: string | null
          description: string | null
          expires_at: string | null
          id: string
          is_active: boolean | null
          label: string
          slug: string | null
          source_count: number | null
          updated_at: string | null
        }
        Insert: {
          article_ids?: string[] | null
          auto_generated?: boolean | null
          created_at?: string | null
          description?: string | null
          expires_at?: string | null
          id?: string
          is_active?: boolean | null
          label: string
          slug?: string | null
          source_count?: number | null
          updated_at?: string | null
        }
        Update: {
          article_ids?: string[] | null
          auto_generated?: boolean | null
          created_at?: string | null
          description?: string | null
          expires_at?: string | null
          id?: string
          is_active?: boolean | null
          label?: string
          slug?: string | null
          source_count?: number | null
          updated_at?: string | null
        }
        Relationships: []
      }
      story_groups: {
        Row: {
          best_article_id: string | null
          category: string
          created_at: string | null
          diaspora_relevant: boolean | null
          enriched: boolean | null
          id: string
          priority: number
          raw_article_ids: string[]
          run_id: string
          source_count: number
          sources: string[]
          story_headline: string
        }
        Insert: {
          best_article_id?: string | null
          category: string
          created_at?: string | null
          diaspora_relevant?: boolean | null
          enriched?: boolean | null
          id?: string
          priority: number
          raw_article_ids: string[]
          run_id: string
          source_count: number
          sources: string[]
          story_headline: string
        }
        Update: {
          best_article_id?: string | null
          category?: string
          created_at?: string | null
          diaspora_relevant?: boolean | null
          enriched?: boolean | null
          id?: string
          priority?: number
          raw_article_ids?: string[]
          run_id?: string
          source_count?: number
          sources?: string[]
          story_headline?: string
        }
        Relationships: [
          {
            foreignKeyName: "story_groups_best_article_id_fkey"
            columns: ["best_article_id"]
            isOneToOne: false
            referencedRelation: "raw_articles"
            referencedColumns: ["id"]
          },
        ]
      }
      story_queue: {
        Row: {
          article_draft: Json | null
          attempts: number
          category: string | null
          created_at: string
          diaspora_relevance: string | null
          draft_version: number
          editor_decision: string | null
          editor_notes: string | null
          enriched_article: Json | null
          error_message: string | null
          featured_score: number
          id: string
          locked_by: string | null
          locked_until: string | null
          max_attempts: number
          max_revisions: number
          priority: number | null
          published_article_id: string | null
          raw_article_ids: string[] | null
          revision_count: number
          sources_found: Json | null
          status: string
          story_brief: Json | null
          updated_at: string
        }
        Insert: {
          article_draft?: Json | null
          attempts?: number
          category?: string | null
          created_at?: string
          diaspora_relevance?: string | null
          draft_version?: number
          editor_decision?: string | null
          editor_notes?: string | null
          enriched_article?: Json | null
          error_message?: string | null
          featured_score?: number
          id?: string
          locked_by?: string | null
          locked_until?: string | null
          max_attempts?: number
          max_revisions?: number
          priority?: number | null
          published_article_id?: string | null
          raw_article_ids?: string[] | null
          revision_count?: number
          sources_found?: Json | null
          status?: string
          story_brief?: Json | null
          updated_at?: string
        }
        Update: {
          article_draft?: Json | null
          attempts?: number
          category?: string | null
          created_at?: string
          diaspora_relevance?: string | null
          draft_version?: number
          editor_decision?: string | null
          editor_notes?: string | null
          enriched_article?: Json | null
          error_message?: string | null
          featured_score?: number
          id?: string
          locked_by?: string | null
          locked_until?: string | null
          max_attempts?: number
          max_revisions?: number
          priority?: number | null
          published_article_id?: string | null
          raw_article_ids?: string[] | null
          revision_count?: number
          sources_found?: Json | null
          status?: string
          story_brief?: Json | null
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "story_queue_published_article_id_fkey"
            columns: ["published_article_id"]
            isOneToOne: false
            referencedRelation: "articles"
            referencedColumns: ["id"]
          },
        ]
      }
      topics: {
        Row: {
          canonical_title: string
          created_at: string
          id: string
          keywords: string[]
          score_diaspora: number | null
          score_recency: number | null
          score_significance: number | null
          score_source_avail: number | null
          score_total: number | null
          signal_count: number
          status: string
          updated_at: string
          urgency: string
          vertical: string
        }
        Insert: {
          canonical_title: string
          created_at?: string
          id?: string
          keywords?: string[]
          score_diaspora?: number | null
          score_recency?: number | null
          score_significance?: number | null
          score_source_avail?: number | null
          score_total?: number | null
          signal_count?: number
          status?: string
          updated_at?: string
          urgency?: string
          vertical: string
        }
        Update: {
          canonical_title?: string
          created_at?: string
          id?: string
          keywords?: string[]
          score_diaspora?: number | null
          score_recency?: number | null
          score_significance?: number | null
          score_source_avail?: number | null
          score_total?: number | null
          signal_count?: number
          status?: string
          updated_at?: string
          urgency?: string
          vertical?: string
        }
        Relationships: []
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      calculate_featured_score: {
        Args: { article_id: string }
        Returns: number
      }
      claim_queue_job: {
        Args: { p_lock_secs?: number; p_status: string; p_worker_id: string }
        Returns: {
          article_draft: Json | null
          attempts: number
          category: string | null
          created_at: string
          diaspora_relevance: string | null
          draft_version: number
          editor_decision: string | null
          editor_notes: string | null
          enriched_article: Json | null
          error_message: string | null
          featured_score: number
          id: string
          locked_by: string | null
          locked_until: string | null
          max_attempts: number
          max_revisions: number
          priority: number | null
          published_article_id: string | null
          raw_article_ids: string[] | null
          revision_count: number
          sources_found: Json | null
          status: string
          story_brief: Json | null
          updated_at: string
        }
        SetofOptions: {
          from: "*"
          to: "story_queue"
          isOneToOne: true
          isSetofReturn: false
        }
      }
      find_similar_articles: {
        Args: { p_hours?: number; p_threshold?: number; p_title: string }
        Returns: {
          id: string
          similarity: number
          slug: string
          title: string
        }[]
      }
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DatabaseWithoutInternals = Omit<Database, "__InternalSupabase">

type DefaultSchema = DatabaseWithoutInternals[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof DatabaseWithoutInternals },
  EnumName extends DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof DatabaseWithoutInternals },
  CompositeTypeName extends PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never = never,
> = PublicCompositeTypeNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  public: {
    Enums: {},
  },
} as const
