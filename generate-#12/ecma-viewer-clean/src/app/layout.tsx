import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ECMA-376 Database Viewer",
  description: "Browse and search ECMA-376 documentation sections",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
