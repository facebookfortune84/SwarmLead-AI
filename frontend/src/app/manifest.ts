import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "Genesis — Autonomous Business Launch Platform",
    short_name: "Genesis",
    description:
      "The first autonomous business launch platform powered by constitutional voice AI. Launch your business with your voice.",
    start_url: "/",
    display: "standalone",
    background_color: "#0a0a1a",
    theme_color: "#0a0a1a",
    icons: [
      {
        src: "/genesis_forge_logo_1.png",
        sizes: "512x512",
        type: "image/png",
        purpose: "any",
      },
    ],
  };
}
