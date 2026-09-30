"use client";

import React, { useState, useEffect } from "react";
import { ImageUpload } from "@/components/ui/image-upload";
import { Button } from "@/components/ui/button";
import { User, Save } from "lucide-react";

export default function SettingsPage() {
  const [avatar, setAvatar] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchAvatar() {
      try {
        const res = await fetch("http://localhost:8000/api/images");
        const data = await res.json();
        setAvatar(data.avatar);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    fetchAvatar();
  }, []);

  const handleUpload = async (url: string, filename: string) => {
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

  if (loading) return <div className="p-8 text-center">Loading Settings...</div>;

  return (
    <div className="p-8 max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">User Settings</h1>

      <div className="bg-white p-6 rounded-xl border shadow-sm space-y-8">
        <section>
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <User className="w-5 h-5" /> Profile Picture
          </h2>
          <div className="flex items-center gap-8">
            <div className="relative w-32 h-32 rounded-full overflow-hidden border-4 border-gray-100 bg-gray-50">
              {avatar ? (
                <img
                  src={`http://localhost:8000/static/uploads/${avatar}`}
                  alt="Avatar"
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-gray-400">
                  <User className="w-12 h-12" />
                </div>
              )}
            </div>
            <div className="flex flex-col gap-2">
              <p className="text-sm text-gray-500">
                Click the upload button to change your profile picture.
              </p>
              <ImageUpload
                label=""
                onUploadSuccess={handleUpload}
              />
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
