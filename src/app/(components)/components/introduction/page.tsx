import { MainHeading } from "@/components/typography";
import { Metadata } from "next";
import React from "react";

export const metadata: Metadata = {
  title: "Introduction to Customized Shadcn UI Components",
  description:
    "Customized Shadcn UI components are pre-designed components that you can preview, copy, and implement directly into your projects.",
  alternates: {
    canonical: "/components/introduction",
  },
};

const Introduction = () => {
  return (
    <div className="prose prose-headings:text-foreground prose-p:text-foreground/80 prose-h2:mb-4 prose-strong:text-foreground prose-p:text-[17px] prose-h2:text-2xl prose-blockquote:text-foreground prose-blockquote:not-italic prose-blockquote:bg-muted/40 prose-blockquote:py-2">
      <MainHeading>Introduction</MainHeading>
      <p>
        Naly provides a wide variety of web UI components and blocks. You can easily browse, preview, and use these components and blocks in your own projects to accelerate your development and enhance your web applications.
      </p>
      <p>
        With Naly, you can seamlessly integrate high-quality UI elements into your workflow, making it simple to build beautiful and functional web interfaces.
      </p>
    </div>
  );
};

export default Introduction;
