import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "Genesis Forge — Autonomous Business Launch Platform by Realms 2 Riches",
    short_name: "Genesis Forge",
    description:
      "The first autonomous business launch platform powered by constitutional voice AI. Launch your business with your voice.",
    start_url: "/",
    display: "standalone",
    background_color: "#0a0a1a",
    theme_color: "#0a0a1a",
    icons: [
      {
        src: "/voice_agent_image_1.png",
        sizes: "512x512",
        type: "image/png",
        purpose: "any",
      },
    ],
  };
}
