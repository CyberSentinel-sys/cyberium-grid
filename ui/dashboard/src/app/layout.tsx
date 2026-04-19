import type { Metadata } from "next";
import { Navbar } from "@/components/Navbar";
import "./globals.css";

export const metadata: Metadata = {
  title: "OrHaShield — SCADA Security Platform",
  description: "AI-native OT/ICS security operations center",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <Navbar />
        <main className="min-h-[calc(100vh-49px)]">{children}</main>
      </body>
    </html>
  );
}
