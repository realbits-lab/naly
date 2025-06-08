import { Metadata } from "next";

export const constructMetadata = (metadata: Metadata): Metadata => {
  return {
    title: metadata.title,
    description: metadata.description,
    openGraph: {
      title: metadata.title!,
      description: metadata.description!,
      siteName: "Shadcn UI Blocks",
      type: "website",
      images: [
        {
          url: "/images/og-image.png",
          height: 630,
          width: 1200,
          alt: "Customized Shadcn UI Blocks & Components",
        },
      ],
      locale: "en_US",
      ...metadata.openGraph,
    },
    authors: [
      {
        name: "Akash Moradiya",
        url: "https://twitter.com/akash_3444",
      },
    ],
    manifest: "/site.webmanifest",
    ...metadata,
  };
};
