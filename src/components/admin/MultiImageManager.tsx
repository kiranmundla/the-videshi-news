import { useState, useRef } from "react";
import { X, Plus, GripVertical, Upload, Link as LinkIcon } from "lucide-react";

interface ImageItem {
  url: string;
  caption?: string;
}

interface MultiImageManagerProps {
  images: ImageItem[];
  onChange: (images: ImageItem[]) => void;
  onUpload: (files: File[]) => Promise<string[]>;
  label?: string;
  maxImages?: number;
}

export default function MultiImageManager({
  images,
  onChange,
  onUpload,
  label = "Images",
  maxImages = 10,
}: MultiImageManagerProps) {
  const [uploading, setUploading] = useState(false);
  const [urlInput, setUrlInput] = useState("");
  const [showUrlInput, setShowUrlInput] = useState(false);
  const [dragIdx, setDragIdx] = useState<number | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const handleFiles = async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    setUploading(true);
    try {
      const fileArr = Array.from(files).slice(0, maxImages - images.length);
      const urls = await onUpload(fileArr);
      const newItems = urls.map((url) => ({ url, caption: "" }));
      onChange([...images, ...newItems]);
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  };

  const addUrl = () => {
    const url = urlInput.trim();
    if (!url) return;
    onChange([...images, { url, caption: "" }]);
    setUrlInput("");
    setShowUrlInput(false);
  };

  const remove = (idx: number) => {
    onChange(images.filter((_, i) => i !== idx));
  };

  const updateCaption = (idx: number, caption: string) => {
    const updated = [...images];
    updated[idx] = { ...updated[idx], caption };
    onChange(updated);
  };

  const moveImage = (from: number, to: number) => {
    if (to < 0 || to >= images.length) return;
    const updated = [...images];
    const [item] = updated.splice(from, 1);
    updated.splice(to, 0, item);
    onChange(updated);
  };

  const setAsHero = (idx: number) => {
    if (idx === 0) return;
    moveImage(idx, 0);
  };

  return (
    <div className="space-y-3">
      <label className="text-sm font-medium text-foreground/70">{label}</label>

      {/* Image grid */}
      {images.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {images.map((img, idx) => (
            <div
              key={`${img.url}-${idx}`}
              className={`relative group rounded-lg border overflow-hidden ${
                idx === 0
                  ? "border-primary/50 ring-1 ring-primary/30"
                  : "border-border"
              }`}
              draggable
              onDragStart={() => setDragIdx(idx)}
              onDragOver={(e) => e.preventDefault()}
              onDrop={() => {
                if (dragIdx !== null && dragIdx !== idx) moveImage(dragIdx, idx);
                setDragIdx(null);
              }}
            >
              <img
                src={img.url}
                alt={img.caption || `Image ${idx + 1}`}
                className="w-full h-28 object-contain bg-black/20"
                loading="lazy"
              />
              {idx === 0 && (
                <span className="absolute top-1.5 left-1.5 text-[10px] font-bold bg-primary text-primary-foreground px-1.5 py-0.5 rounded">
                  HERO
                </span>
              )}
              {/* Actions overlay */}
              <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                <button
                  onClick={() => remove(idx)}
                  className="p-1.5 rounded-full bg-red-500/80 hover:bg-red-500 text-white"
                  title="Remove"
                >
                  <X className="h-3.5 w-3.5" />
                </button>
                {idx !== 0 && (
                  <button
                    onClick={() => setAsHero(idx)}
                    className="p-1.5 rounded-full bg-primary/80 hover:bg-primary text-primary-foreground text-[10px] font-bold"
                    title="Set as hero image"
                  >
                    ★
                  </button>
                )}
                <GripVertical className="h-4 w-4 text-white/60 cursor-grab" />
              </div>
              {/* Caption input */}
              <input
                type="text"
                value={img.caption || ""}
                onChange={(e) => updateCaption(idx, e.target.value)}
                placeholder="Caption..."
                className="w-full px-2 py-1 text-xs bg-background border-t border-border focus:outline-none focus:ring-1 focus:ring-primary"
              />
            </div>
          ))}
        </div>
      )}

      {/* Add buttons */}
      {images.length < maxImages && (
        <div className="flex items-center gap-2">
          <input
            ref={fileRef}
            type="file"
            accept="image/*"
            multiple
            className="hidden"
            onChange={(e) => handleFiles(e.target.files)}
          />
          <button
            onClick={() => fileRef.current?.click()}
            disabled={uploading}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium bg-primary/10 hover:bg-primary/20 text-primary rounded-lg border border-primary/20 transition-colors disabled:opacity-50"
          >
            {uploading ? (
              <>
                <div className="h-3.5 w-3.5 border-2 border-primary/30 border-t-primary rounded-full animate-spin" />
                Uploading...
              </>
            ) : (
              <>
                <Upload className="h-3.5 w-3.5" />
                Upload Images
              </>
            )}
          </button>
          <button
            onClick={() => setShowUrlInput(!showUrlInput)}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium bg-card hover:bg-card/80 text-foreground/70 rounded-lg border border-border transition-colors"
          >
            <LinkIcon className="h-3.5 w-3.5" />
            Paste URL
          </button>
          <span className="text-xs text-foreground/40">
            {images.length}/{maxImages}
          </span>
        </div>
      )}

      {/* URL input */}
      {showUrlInput && (
        <div className="flex gap-2">
          <input
            type="url"
            value={urlInput}
            onChange={(e) => setUrlInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && addUrl()}
            placeholder="https://..."
            className="flex-1 px-3 py-1.5 text-sm bg-background border border-border rounded-lg focus:outline-none focus:ring-1 focus:ring-primary"
            autoFocus
          />
          <button
            onClick={addUrl}
            className="px-3 py-1.5 text-xs font-medium bg-primary text-primary-foreground rounded-lg hover:bg-primary/90"
          >
            <Plus className="h-4 w-4" />
          </button>
        </div>
      )}
    </div>
  );
}
