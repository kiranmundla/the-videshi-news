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
          body: string
          category: string
          created_at: string | null
          id: string
          image_url: string | null
          is_published: boolean | null
          nri_angle: string | null
          published_at: string | null
          read_time_min: number | null
          slug: string | null
          sources_used: Json | null
          story_group_id: string | null
          summary: string
          tags: string[] | null
          title: string
          updated_at: string | null
          word_count: number | null
        }
        Insert: {
          body: string
          category: string
          created_at?: string | null
          id?: string
          image_url?: string | null
          is_published?: boolean | null
          nri_angle?: string | null
          published_at?: string | null
          read_time_min?: number | null
          slug?: string | null
          sources_used?: Json | null
          story_group_id?: string | null
          summary: string
          tags?: string[] | null
          title: string
          updated_at?: string | null
          word_count?: number | null
        }
        Update: {
          body?: string
          category?: string
          created_at?: string | null
          id?: string
          image_url?: string | null
          is_published?: boolean | null
          nri_angle?: string | null
          published_at?: string | null
          read_time_min?: number | null
          slug?: string | null
          sources_used?: Json | null
          story_group_id?: string | null
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
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
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
