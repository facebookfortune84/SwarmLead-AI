"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface Node {
  id: string;
  label: string;
  x: number;
  y: number;
  color: string;
  pulse: boolean;
}

interface Edge {
  from: string;
  to: string;
  active: boolean;
}

const NODES: Node[] = [
  { id: "query", label: "User Query", x: 50, y: 50, color: "#818cf8", pulse: false },
  { id: "embed", label: "Embedding", x: 25, y: 30, color: "#a78bfa", pulse: false },
  { id: "retrieve", label: "Vector Search", x: 50, y: 20, color: "#c084fc", pulse: false },
  { id: "docs", label: "Knowledge Base", x: 75, y: 30, color: "#e879f9", pulse: false },
  { id: "context", label: "Context Window", x: 50, y: 40, color: "#f472b6", pulse: false },
  { id: "augment", label: "Augment Prompt", x: 30, y: 55, color: "#fb923c", pulse: false },
  { id: "llm", label: "LLM Inference", x: 50, y: 65, color: "#34d399", pulse: false },
  { id: "response", label: "Response", x: 50, y: 80, color: "#22d3ee", pulse: false },
];

const EDGES: Edge[] = [
  { from: "query", to: "embed", active: true },
  { from: "embed", to: "retrieve", active: true },
  { from: "retrieve", to: "docs", active: true },
  { from: "docs", to: "context", active: true },
  { from: "context", to: "augment", active: true },
  { from: "augment", to: "llm", active: true },
  { from: "llm", to: "response", active: true },
];

export function RAGVisualization({ className = "" }: { className?: string }) {
  const [activeNode, setActiveNode] = useState<string | null>(null);
  const [flowStep, setFlowStep] = useState(0);
  const [particles, setParticles] = useState<{ x: number; y: number; id: number }[]>([]);
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    const interval = setInterval(() => {
      setFlowStep((prev) => {
        const next = prev >= NODES.length - 1 ? 0 : prev + 1;
        setActiveNode(NODES[next].id);
        return next;
      });
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (flowStep === 0) return;
    const fromNode = NODES[flowStep - 1];
    const toNode = NODES[flowStep];
    if (!fromNode || !toNode) return;

    const newParticles = Array.from({ length: 5 }, (_, i) => ({
      x: fromNode.x,
      y: fromNode.y,
      id: Date.now() + i,
    }));
    setParticles((prev) => [...prev, ...newParticles].slice(-30));
    const timer = setTimeout(() => {
      setParticles((prev) => prev.filter((p) => !newParticles.find((np) => np.id === p.id)));
    }, 1000);
    return () => clearTimeout(timer);
  }, [flowStep]);

  const getNodePos = (id: string) => NODES.find((n) => n.id === id) || { x: 50, y: 50 };

  return (
    <div className={`relative ${className}`}>
      <svg
        ref={svgRef}
        viewBox="0 0 100 100"
        className="w-full h-full"
        preserveAspectRatio="xMidYMid meet"
      >
        {EDGES.map((edge) => {
          const from = getNodePos(edge.from);
          const to = getNodePos(edge.to);
          const isActive = NODES.findIndex((n) => n.id === edge.to) <= flowStep;
          return (
            <line
              key={`${edge.from}-${edge.to}`}
              x1={from.x}
              y1={from.y}
              x2={to.x}
              y2={to.y}
              stroke={isActive ? "#818cf8" : "#ffffff15"}
              strokeWidth={isActive ? 0.3 : 0.15}
              className="transition-all duration-500"
            />
          );
        })}

        {particles.map((p) => (
          <circle
            key={p.id}
            cx={p.x}
            cy={p.y}
            r={0.3}
            fill="#818cf8"
            className="animate-ping"
          />
        ))}

        {NODES.map((node) => {
          const isActiveNode = activeNode === node.id;
          const isPast = NODES.findIndex((n) => n.id === node.id) <= flowStep;
          return (
            <g key={node.id} className="cursor-pointer" onClick={() => setActiveNode(node.id)}>
              <circle
                cx={node.x}
                cy={node.y}
                r={isActiveNode ? 4 : 3}
                fill={isPast ? node.color : "#ffffff10"}
                stroke={isActiveNode ? "#ffffff" : isPast ? node.color : "#ffffff20"}
                strokeWidth={isActiveNode ? 0.5 : 0.2}
                className={`transition-all duration-500 ${isActiveNode ? "animate-pulse" : ""}`}
              />
              <text
                x={node.x}
                y={node.y + 5}
                textAnchor="middle"
                fill={isPast ? "#ffffffcc" : "#ffffff40"}
                fontSize="2.5"
                fontWeight={isActiveNode ? "bold" : "normal"}
                className="transition-all duration-500"
              >
                {node.label}
              </text>
            </g>
          );
        })}
      </svg>

      <AnimatePresence mode="wait">
        {activeNode && (
          <motion.div
            key={activeNode}
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -5 }}
            className="absolute bottom-2 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full bg-indigo-600/20 border border-indigo-500/30 text-indigo-300 text-xs whitespace-nowrap"
          >
            {NODES.find((n) => n.id === activeNode)?.label}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}