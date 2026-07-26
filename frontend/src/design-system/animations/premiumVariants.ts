import { Variants } from "framer-motion";

export const orbState: Variants = {
  idle: {
    scale: 1,
    opacity: 0.7,
    transition: { duration: 0.3 },
  },
  listening: {
    scale: [1, 1.08, 1],
    opacity: 1,
    transition: {
      duration: 0.8,
      repeat: Infinity,
      ease: "easeInOut",
    },
  },
  speaking: {
    scale: [1, 1.12, 1],
    opacity: 1,
    transition: {
      duration: 0.5,
      repeat: Infinity,
      ease: "easeInOut",
    },
  },
  thinking: {
    scale: [1, 0.95, 1],
    opacity: 0.8,
    transition: {
      duration: 0.6,
      repeat: Infinity,
      ease: "easeInOut",
    },
  },
};
