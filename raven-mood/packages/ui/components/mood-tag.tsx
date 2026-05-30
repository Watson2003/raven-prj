"use client";

import * as React from "react"
import { Badge } from "./badge"
import { cn } from "./button"
import { motion } from "framer-motion"

interface MoodTagProps {
  mood: string
  className?: string
}

export function MoodTag({ mood, className }: MoodTagProps) {
  const m = mood.toUpperCase()
  let colorClass = "bg-white/10 text-white"
  let icon = "⚪"
  
  if (m.includes("CLEAN")) {
    colorClass = "bg-clean/20 text-clean border border-clean/30"
    icon = "😊"
  } else if (m.includes("MESSY")) {
    colorClass = "bg-messy/20 text-messy border border-messy/30"
    icon = "😤"
  } else if (m.includes("CHAOTIC")) {
    colorClass = "bg-chaotic/20 text-chaotic border border-chaotic/30"
    icon = "🤯"
  }

  const isChaotic = m.includes("CHAOTIC");

  const BadgeContent = (
    <Badge className={cn("gap-1 font-bold", colorClass, className)}>
      <span>{icon}</span>
      <span>{m.replace(/[^A-Z]/g, "") || m}</span>
    </Badge>
  );

  if (isChaotic) {
    return (
      <motion.div
        animate={{ scale: [1, 1.05, 1] }}
        transition={{ repeat: Infinity, duration: 1.5 }}
        className="inline-block"
      >
        {BadgeContent}
      </motion.div>
    );
  }

  return BadgeContent;
}
