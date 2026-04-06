import type { Metadata } from "next";
import { Toaster } from "react-hot-toast";
import "./globals.css";

export const metadata: Metadata = {
  title: "DataCleaner — AI Data Cleaning Platform",
  description: "Upload, clean, analyze, and download your data in seconds. Production-ready data cleaning pipeline.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        {children}
        <Toaster
          position="top-right"
          toastOptions={{
            style: {
              background: "#1e293b",
              color: "#f8fafc",
              border: "1px solid rgba(99,102,241,0.3)",
              borderRadius: "12px",
            },
            success: {
              iconTheme: { primary: "#22c55e", secondary: "#0f172a" },
            },
            error: {
              iconTheme: { primary: "#ef4444", secondary: "#0f172a" },
            },
          }}
        />
      </body>
    </html>
  );
}
