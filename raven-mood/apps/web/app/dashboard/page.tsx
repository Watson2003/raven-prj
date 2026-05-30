"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle, MoodTag, Button } from "ui";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import { ArrowLeft } from "lucide-react";

export default function Dashboard() {
  const router = useRouter();
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    const stored = sessionStorage.getItem("moodData");
    if (!stored) {
      router.push("/");
    } else {
      setData(JSON.parse(stored));
    }
  }, [router]);

  if (!data) return null;

  const { overall_mood, files, summary } = data;

  const chartData = [
    { name: "Clean", value: summary.clean, color: "#22c55e" },
    { name: "Messy", value: summary.messy, color: "#f59e0b" },
    { name: "Chaotic", value: summary.chaotic, color: "#ef4444" },
  ].filter(d => d.value > 0);

  let overallColor = "from-neutral-500 to-neutral-700";
  let overallEmoji = "⚪";
  if (overall_mood === "CLEAN") {
    overallColor = "from-clean/20 to-clean/5";
    overallEmoji = "😊";
  } else if (overall_mood === "MESSY") {
    overallColor = "from-messy/20 to-messy/5";
    overallEmoji = "😤";
  } else if (overall_mood === "CHAOTIC") {
    overallColor = "from-chaotic/20 to-chaotic/5";
    overallEmoji = "🤯";
  }

  return (
    <div className="min-h-screen p-8 space-y-8 max-w-7xl mx-auto">
      <div className="flex items-center gap-4">
        <Button onClick={() => router.push("/")} className="bg-transparent border border-white/10 hover:bg-white/5 text-white">
          <ArrowLeft className="w-4 h-4 mr-2" /> Back
        </Button>
        <h1 className="text-2xl font-bold tracking-tight">Codebase Mood Analysis</h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="md:col-span-2"
        >
          <Card className={`h-full overflow-hidden relative border-0 bg-gradient-to-br ${overallColor}`}>
            <CardContent className="p-10 flex flex-col items-center justify-center h-full text-center space-y-6">
              <motion.div 
                animate={overall_mood === 'CHAOTIC' ? { scale: [1, 1.1, 1] } : {}}
                transition={{ repeat: Infinity, duration: 2 }}
                className="text-8xl"
              >
                {overallEmoji}
              </motion.div>
              <div>
                <h2 className="text-lg font-medium text-white/60 mb-2">Overall Project Mood</h2>
                <div className="text-5xl font-bold tracking-tight">{overall_mood}</div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <Card className="h-full">
            <CardHeader>
              <CardTitle>Mood Distribution</CardTitle>
            </CardHeader>
            <CardContent className="flex justify-center items-center h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={chartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                    stroke="none"
                  >
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#111', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                    itemStyle={{ color: '#fff' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <Card>
          <CardHeader>
            <CardTitle>File-by-File Breakdown</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="text-xs uppercase bg-white/5 text-neutral-400">
                  <tr>
                    <th className="px-6 py-4 rounded-tl-lg font-medium">File Name</th>
                    <th className="px-6 py-4 font-medium">Lines</th>
                    <th className="px-6 py-4 font-medium">Mood</th>
                    <th className="px-6 py-4 rounded-tr-lg font-medium">Reason</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {files.map((file: any, i: number) => (
                    <tr key={i} className="hover:bg-white/5 transition-colors">
                      <td className="px-6 py-4 font-mono text-neutral-300">{file.name}</td>
                      <td className="px-6 py-4 text-neutral-500">{file.lines}</td>
                      <td className="px-6 py-4">
                        <MoodTag mood={file.mood} />
                      </td>
                      <td className="px-6 py-4 text-neutral-400">{file.reason}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
