import { MarketplaceNavbar } from "@/components/layout/marketplace-navbar";
import { AuthProvider } from "@/providers/auth/auth-provider";

export default function MarketplaceLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AuthProvider>
      <div className="min-h-screen bg-background">
        <MarketplaceNavbar />
        <main>{children}</main>
      </div>
    </AuthProvider>
  );
}