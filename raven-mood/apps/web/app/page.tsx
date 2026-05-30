"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Button } from "ui";
import { UploadCloud, Github, Loader2 } from "lucide-react";

export default function Home() {
  const router = useRouter();
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleAnalyzeUrl = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url) return;
    setLoading(true);
    setError("");

    try {
      const formData = new FormData();
      formData.append("github_url", url);
      
      // Validate GitHub URL format
      const githubPattern = /^https:\/\/github\.com\/[^\/]+\/[^\/]+$/i;
      if (!githubPattern.test(url)) {
        setError('Please enter a valid GitHub repository URL (e.g., https://github.com/user/repo)');
        setLoading(false);
        return;
      }

      // Using relative path; next.config rewrites to FastAPI in dev
      const res = await fetch('/api/analyze', {
        method: 'POST',
        body: formData,
      });
      
            // Read response body once
      const rawText = await res.text();
      if (!res.ok) {
        // Use raw text as error message; if it's JSON, try to extract detail
        let errorMessage = rawText || "Failed to analyze repository";
        try {
          const parsed = JSON.parse(rawText);
          if (parsed && parsed.detail) errorMessage = parsed.detail;
        } catch {}
        throw new Error(errorMessage);
      }
      // Parse successful JSON response
      const data = JSON.parse(rawText);
      sessionStorage.setItem("moodData", JSON.stringify(data));
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message);
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setLoading(true);
    setError("");

    try {
      const formData = new FormData();
      formData.append("file", file);
      
      const baseUrl = process.env.NODE_ENV === "production" ? "" : "http://localhost:8000";
      const res = await fetch(`${baseUrl}/analyze`, {
        method: "POST",
        body: formData,
      });
      
      // Read response body once
      const rawText = await res.text();
      if (!res.ok) {
        let errorMessage = rawText || "Failed to analyze repository";
        try {
          const parsed = JSON.parse(rawText);
          if (parsed && parsed.detail) errorMessage = parsed.detail;
        } catch {}
        throw new Error(errorMessage);
      }
      // Parse successful JSON response
      const data = JSON.parse(rawText);
      sessionStorage.setItem("moodData", JSON.stringify(data));
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message);
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-neutral-900 via-background to-background">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="z-10 max-w-5xl w-full items-center justify-center font-mono text-sm flex flex-col gap-8"
      >
        <div className="text-center space-y-4">
          <motion.h1 
            className="text-5xl md:text-7xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-neutral-100 to-neutral-500"
            initial={{ scale: 0.9 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.5 }}
          >
            Raven Mood
          </motion.h1>
          <p className="text-xl md:text-2xl text-neutral-400 font-sans">
            Know your code&apos;s mood before your team does
          </p>
        </div>

        <div className="w-full max-w-md space-y-6 mt-12 bg-white/5 p-8 rounded-2xl border border-white/10 backdrop-blur-md">
          {error && (
            <div className="p-3 rounded bg-red-500/20 text-red-300 text-sm border border-red-500/30">
              {error}
            </div>
          )}
          
          <form onSubmit={handleAnalyzeUrl} className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-neutral-300">Connect GitHub Repository</label>
              <div className="flex gap-2">
                <div className="relative flex-1">
                  <Github className="absolute left-3 top-2.5 h-4 w-4 text-neutral-400" />
                  <input 
                    type="url"
                    placeholder="https://github.com/user/repo"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    className="flex h-10 w-full rounded-md border border-white/10 bg-black/50 px-3 py-2 pl-10 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-neutral-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  />
                </div>
                <Button type="submit" disabled={loading || !url}>
                  {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Analyze'}
                </Button>
              </div>
            </div>
          </form>

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t border-white/10" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-[#111111] px-2 text-neutral-500">Or upload</span>
            </div>
          </div>

          <div className="flex items-center justify-center w-full">
            <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed rounded-lg cursor-pointer hover:bg-white/5 border-white/10 transition-colors">
              <div className="flex flex-col items-center justify-center pt-5 pb-6">
                <UploadCloud className="w-8 h-8 mb-3 text-neutral-400" />
                <p className="mb-2 text-sm text-neutral-400"><span className="font-semibold">Click to upload</span> a .zip file</p>
              </div>
              <input type="file" className="hidden" accept=".zip" onChange={handleFileUpload} disabled={loading} />
            </label>
          </div>
        </div>
      </motion.div>
    </main>
  );
}
