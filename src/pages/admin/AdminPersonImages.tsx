import { useState, useEffect, useCallback } from "react";
import { Helmet } from "react-helmet-async";
import { Plus, Trash2, Search, Image as ImageIcon, Upload } from "lucide-react";
import { supabase } from "@/integrations/supabase/client";
import AdminLayout from "@/components/admin/AdminLayout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "sonner";

const sb = supabase as any;

type PersonImage = {
  id: string;
  person_name: string;
  image_url: string;
  orientation: string;
  license: string;
  attribution: string | null;
  source_url: string | null;
  img_w: number | null;
  img_h: number | null;
  created_at: string;
};

type GroupedPerson = {
  name: string;
  images: PersonImage[];
  landscapeCount: number;
  portraitCount: number;
};

export default function AdminPersonImages() {
  const [images, setImages] = useState<PersonImage[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [showAdd, setShowAdd] = useState(false);
  const [uploading, setUploading] = useState(false);

  // Add form state
  const [formName, setFormName] = useState("");
  const [formOrientation, setFormOrientation] = useState("landscape");
  const [formLicense, setFormLicense] = useState("CC BY 4.0");
  const [formAttribution, setFormAttribution] = useState("");
  const [formSourceUrl, setFormSourceUrl] = useState("");
  const [formFile, setFormFile] = useState<File | null>(null);
  const [formPreview, setFormPreview] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    const { data, error } = await sb
      .from("person_images")
      .select("*")
      .order("person_name", { ascending: true })
      .order("orientation", { ascending: true })
      .order("created_at", { ascending: false });

    if (error) {
      toast.error(error.message);
    } else {
      setImages(data ?? []);
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  // Group images by person
  const grouped: GroupedPerson[] = (() => {
    const map = new Map<string, PersonImage[]>();
    const filtered = search
      ? images.filter((i) =>
          i.person_name.toLowerCase().includes(search.toLowerCase())
        )
      : images;

    for (const img of filtered) {
      const key = img.person_name.toLowerCase().trim();
      if (!map.has(key)) map.set(key, []);
      map.get(key)!.push(img);
    }

    return Array.from(map.entries())
      .map(([, imgs]) => ({
        name: imgs[0].person_name,
        images: imgs,
        landscapeCount: imgs.filter((i) => i.orientation === "landscape").length,
        portraitCount: imgs.filter((i) => i.orientation === "portrait").length,
      }))
      .sort((a, b) => a.name.localeCompare(b.name));
  })();

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setFormFile(file);
    // Create preview
    const reader = new FileReader();
    reader.onload = () => setFormPreview(reader.result as string);
    reader.readAsDataURL(file);

    // Auto-detect orientation from image dimensions
    const img = new window.Image();
    img.onload = () => {
      const ratio = img.width / img.height;
      if (ratio > 1.1) setFormOrientation("landscape");
      else if (ratio < 0.9) setFormOrientation("portrait");
      else setFormOrientation("square");
    };
    img.src = URL.createObjectURL(file);
  }

  async function handleUpload() {
    if (!formFile || !formName.trim()) {
      toast.error("Person name and image file are required");
      return;
    }

    setUploading(true);
    try {
      // Upload to Supabase storage
      const ext = formFile.name.split(".").pop() || "jpg";
      const slug = formName
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, "-")
        .replace(/-+$/, "");
      const filename = `person-images/${slug}-${Date.now()}.${ext}`;

      const { error: uploadError } = await sb.storage
        .from("article-images")
        .upload(filename, formFile, {
          contentType: formFile.type,
          upsert: false,
        });

      if (uploadError) throw uploadError;

      // Get public URL
      const {
        data: { publicUrl },
      } = sb.storage.from("article-images").getPublicUrl(filename);

      // Get image dimensions
      const img = new window.Image();
      const dims = await new Promise<{ w: number; h: number }>((resolve) => {
        img.onload = () => resolve({ w: img.width, h: img.height });
        img.src = URL.createObjectURL(formFile!);
      });

      // Insert record
      const { error: insertError } = await sb.from("person_images").insert({
        person_name: formName.trim(),
        image_url: publicUrl,
        orientation: formOrientation,
        license: formLicense,
        attribution: formAttribution.trim() || null,
        source_url: formSourceUrl.trim() || null,
        img_w: dims.w,
        img_h: dims.h,
      });

      if (insertError) throw insertError;

      toast.success(`Added ${formOrientation} image for ${formName}`);
      setShowAdd(false);
      resetForm();
      load();
    } catch (err: any) {
      toast.error(err.message || "Upload failed");
    } finally {
      setUploading(false);
    }
  }

  async function handleDelete(img: PersonImage) {
    if (!confirm(`Delete this ${img.orientation} image of ${img.person_name}?`))
      return;

    const { error } = await sb
      .from("person_images")
      .delete()
      .eq("id", img.id);

    if (error) {
      toast.error(error.message);
    } else {
      toast.success("Deleted");
      load();
    }
  }

  function resetForm() {
    setFormName("");
    setFormOrientation("landscape");
    setFormLicense("CC BY 4.0");
    setFormAttribution("");
    setFormSourceUrl("");
    setFormFile(null);
    setFormPreview(null);
  }

  function openAddFor(personName?: string) {
    resetForm();
    if (personName) setFormName(personName);
    setShowAdd(true);
  }

  return (
    <AdminLayout>
      <Helmet>
        <title>Person Images | Admin</title>
      </Helmet>

      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Person Images</h1>
            <p className="text-sm text-muted-foreground mt-1">
              Curated photos for leaders & celebrities. Multiple per person, both orientations.
            </p>
          </div>
          <Button onClick={() => openAddFor()} className="gap-2">
            <Plus className="h-4 w-4" /> Add Image
          </Button>
        </div>

        {/* Search + stats */}
        <div className="flex items-center gap-4">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search by name..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9"
            />
          </div>
          <p className="text-sm text-muted-foreground">
            {grouped.length} people · {images.length} images
          </p>
        </div>

        {/* Person cards */}
        {loading ? (
          <p className="text-muted-foreground">Loading...</p>
        ) : grouped.length === 0 ? (
          <div className="text-center py-16 text-muted-foreground">
            <ImageIcon className="h-12 w-12 mx-auto mb-3 opacity-30" />
            <p className="text-lg font-medium">No person images yet</p>
            <p className="text-sm mt-1">
              Add curated photos for leaders & celebrities
            </p>
          </div>
        ) : (
          <div className="space-y-6">
            {grouped.map((person) => (
              <div
                key={person.name}
                className="border border-border rounded-xl p-5 bg-card"
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <h2 className="text-lg font-semibold">{person.name}</h2>
                    <Badge variant="outline" className="text-xs">
                      {person.landscapeCount}L · {person.portraitCount}P
                    </Badge>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => openAddFor(person.name)}
                    className="gap-1.5"
                  >
                    <Plus className="h-3.5 w-3.5" /> Add
                  </Button>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
                  {person.images.map((img) => (
                    <div
                      key={img.id}
                      className="group relative border border-border rounded-lg overflow-hidden bg-stone-100"
                    >
                      <div
                        className="w-full"
                        style={{
                          aspectRatio:
                            img.orientation === "portrait" ? "3/4" : "16/9",
                        }}
                      >
                        <img
                          src={img.image_url}
                          alt={img.person_name}
                          className="w-full h-full object-cover"
                          loading="lazy"
                        />
                      </div>
                      <div className="p-2 space-y-1">
                        <div className="flex items-center gap-1.5">
                          <Badge
                            variant="secondary"
                            className={`text-[10px] ${
                              img.orientation === "landscape"
                                ? "bg-blue-500/15 text-blue-600"
                                : img.orientation === "portrait"
                                ? "bg-purple-500/15 text-purple-600"
                                : "bg-gray-500/15 text-gray-600"
                            }`}
                          >
                            {img.orientation}
                          </Badge>
                          <span className="text-[10px] text-muted-foreground truncate">
                            {img.license}
                          </span>
                        </div>
                        {img.img_w && img.img_h && (
                          <p className="text-[10px] text-muted-foreground">
                            {img.img_w}×{img.img_h}
                          </p>
                        )}
                      </div>
                      {/* Delete button on hover */}
                      <button
                        onClick={() => handleDelete(img)}
                        className="absolute top-1.5 right-1.5 p-1.5 rounded-md bg-black/60 text-white opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-600"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Add Image Dialog */}
      <Dialog open={showAdd} onOpenChange={setShowAdd}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>Add Person Image</DialogTitle>
          </DialogHeader>

          <div className="space-y-4 py-2">
            <div>
              <label className="text-sm font-medium mb-1.5 block">
                Person Name *
              </label>
              <Input
                placeholder="e.g. Narendra Modi"
                value={formName}
                onChange={(e) => setFormName(e.target.value)}
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-1.5 block">
                Image File *
              </label>
              <div className="flex items-center gap-3">
                <label className="cursor-pointer flex items-center gap-2 px-4 py-2 border border-border rounded-lg hover:bg-accent transition-colors">
                  <Upload className="h-4 w-4" />
                  <span className="text-sm">
                    {formFile ? formFile.name : "Choose file"}
                  </span>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleFileChange}
                    className="hidden"
                  />
                </label>
              </div>
              {formPreview && (
                <div className="mt-3 rounded-lg overflow-hidden border border-border max-h-48">
                  <img
                    src={formPreview}
                    alt="Preview"
                    className="w-full h-full object-contain max-h-48"
                  />
                </div>
              )}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium mb-1.5 block">
                  Orientation
                </label>
                <Select
                  value={formOrientation}
                  onValueChange={setFormOrientation}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="landscape">Landscape</SelectItem>
                    <SelectItem value="portrait">Portrait</SelectItem>
                    <SelectItem value="square">Square</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="text-sm font-medium mb-1.5 block">
                  License
                </label>
                <Select value={formLicense} onValueChange={setFormLicense}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Public Domain">Public Domain</SelectItem>
                    <SelectItem value="CC0">CC0</SelectItem>
                    <SelectItem value="CC BY 2.0">CC BY 2.0</SelectItem>
                    <SelectItem value="CC BY 4.0">CC BY 4.0</SelectItem>
                    <SelectItem value="CC BY-SA 2.0">CC BY-SA 2.0</SelectItem>
                    <SelectItem value="CC BY-SA 4.0">CC BY-SA 4.0</SelectItem>
                    <SelectItem value="GODL-India">GODL-India</SelectItem>
                    <SelectItem value="Fair Use">Fair Use</SelectItem>
                    <SelectItem value="Other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div>
              <label className="text-sm font-medium mb-1.5 block">
                Attribution
              </label>
              <Input
                placeholder="e.g. Photo by White House / Public Domain"
                value={formAttribution}
                onChange={(e) => setFormAttribution(e.target.value)}
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-1.5 block">
                Source URL
              </label>
              <Input
                placeholder="Original source URL (for your records)"
                value={formSourceUrl}
                onChange={(e) => setFormSourceUrl(e.target.value)}
              />
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setShowAdd(false);
                resetForm();
              }}
            >
              Cancel
            </Button>
            <Button onClick={handleUpload} disabled={uploading}>
              {uploading ? "Uploading..." : "Upload & Save"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </AdminLayout>
  );
}
