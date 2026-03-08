import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
    title: "MDex Singularity Omni-v5",
    description: "Advanced Manga Downloader with IA Translation",
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en">
            <body className="antialiased selection:bg-cyan-500/30">
                <div className="fixed inset-0 bg-[radial-gradient(circle_at_50%_0%,rgba(0,188,212,0.15),transparent_50%)] pointer-events-none" />
                <main className="relative min-h-screen">
                    {children}
                </main>
            </body>
        </html>
    );
}
