import { supabase } from "@/integrations/supabase/client";

const sb = supabase as any;

/**
 * Upload a file to Supabase storage and return the public URL.
 */
export async function uploadImage(
  bucket: string,
  path: string,
  file: File,
): Promise<string | null> {
  const { error } = await sb.storage.from(bucket).upload(path, file, {
    upsert: true,
    contentType: file.type,
  });
  if (error) {
    console.error("Upload error:", error);
    return null;
  }
  const { data } = sb.storage.from(bucket).getPublicUrl(path);
  return data?.publicUrl ?? null;
}

/**
 * Upload multiple files and return array of public URLs.
 */
export async function uploadMultipleImages(
  bucket: string,
  prefix: string,
  slug: string,
  files: File[],
): Promise<string[]> {
  const urls: string[] = [];
  for (let i = 0; i < files.length; i++) {
    const ext = files[i].name.split(".").pop()?.toLowerCase() ?? "jpg";
    const path = `${prefix}/${slug}_${Date.now()}_${i}.${ext}`;
    const url = await uploadImage(bucket, path, files[i]);
    if (url) urls.push(url);
  }
  return urls;
}

/**
 * Generate a safe filename from a slug + file extension.
 */
export function makeStoragePath(prefix: string, slug: string, file: File): string {
  const ext = file.name.split(".").pop()?.toLowerCase() ?? "jpg";
  return `${prefix}/${slug}.${ext}`;
}
