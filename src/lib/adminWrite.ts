import { supabase } from "@/integrations/supabase/client";

const KEY_STORAGE = "admin_key";

export function getAdminKey(): string {
  return localStorage.getItem(KEY_STORAGE) ?? "";
}

export function setAdminKey(k: string): void {
  localStorage.setItem(KEY_STORAGE, k);
}

type WriteOp = "insert" | "update" | "delete";
type AllowedTable = "p2_feed_sources" | "p2_topics" | "p2_articles" | "videshi_sources";

interface WriteArgs {
  table: AllowedTable;
  op: WriteOp;
  id?: string;
  payload?: Record<string, unknown>;
}

export async function adminWrite(args: WriteArgs): Promise<{ error?: string; data?: unknown }> {
  const adminKey = getAdminKey();
  if (!adminKey) return { error: "Admin key required. Set it on the Admin page." };

  const { data, error } = await supabase.functions.invoke("admin-pipeline-write", {
    body: args,
    headers: { "x-admin-key": adminKey },
  });
  if (error) return { error: error.message };
  if ((data as any)?.error) return { error: (data as any).error };
  return { data: (data as any)?.data };
}
