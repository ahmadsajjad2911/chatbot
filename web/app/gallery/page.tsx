"use client";

import React, { useState, useEffect } from "react";
import { ImageUpload } from "@/components/ui/image-upload";
import { Button } from "@/components/ui/button";
import { Trash2, User } from "lucide-react";

export default function GalleryPage() {
  const [images, setImages] = useState<string[]>([]);
  const [avatar, setAvatar] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchImages = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/images");
      const data = await res.json();
      setImages(data.gallery);
      setAvatar(data.avatar);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchImages();
  }, []);

  const handleUpload = async (url: string, filename: string) => {
    setImages(prev => [...prev, filename]);
  };

  const deleteImage = async (filename: string) => {
    try {
      const res = await fetch(`http://localhost:8000/api/images/${filename}`, {
        method: "DELETE",
      });
      if (res.ok) {
        setImages(prev => prev.filter(f => f !== filename));
        if (avatar === filename) setAvatar(null);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const setAsAvatar = async (filename: string) => {
    try {
      const res = await fetch("http://localhost:8000/api/images/avatar", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ filename }),
      });
      if (res.ok) {
        setAvatar(filename);
      }
    } catch (e) {
      console.error(e);
    }
  };

  if (loading) return <div className="p-8 text-center">Loading Gallery...</div>;

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">Image Gallery</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="col-span-1 bg-gray-50 p-6 rounded-xl border">
          <h2 className="text-xl font-semibold mb-4">Upload New Image</h2>
          <ImageUpload
            label="Select an image to add to your library"
            onUploadSuccess={handleUpload}
          />
        </div>

        <div className="col-span-2">
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
            {images.map(filename => (
              <div key={filename} className="group relative aspect-square rounded-lg overflow-hidden border bg-gray-100">
                <img
                  src={`http://localhost:8000/static/uploads/${filename}`}
                  alt={filename}
                  className="w-full h-full object-cover transition-transform group-hover:scale-105"
                />
                <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                  <Button
                    variant="ghost"
                    size="icon"
                    className="bg-white/20 text-white hover:bg-white/40"
                    onClick={() => setAsAvatar(filename)}
                    title="Set as Avatar"
                  >
                    <User className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="bg-red-500/20 text-white hover:bg-red-500/40"
                    onClick={() => deleteImage(filename)}
                    title="Delete"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
                {avatar === filename && (
                  <div className="absolute top-2 left-2 bg-primary text-white text-[10px] px-2 py-0.5 rounded-full font-bold uppercase">
                    Avatar
                  </div>
                )}
              </div>
            ))}
            {images.length === 0 && (
              <div className="col-span-full text-center py-12 text-gray-500 italic">
                No images uploaded yet.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
