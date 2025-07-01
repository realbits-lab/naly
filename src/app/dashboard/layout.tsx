import { DashboardNav } from "@/features/dashboard/components/dashboard-nav";
import { AuthProvider } from "@/providers/auth/auth-provider";
import { Button } from "@/components/ui/button";
import { Logo } from "@/components/logo";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AuthProvider>
      <div className="min-h-screen bg-background">
        <div className="flex">
          {/* Sidebar */}
          <div className="hidden md:flex md:w-64 md:flex-col">
            <div className="flex flex-col flex-grow pt-5 overflow-y-auto bg-muted/10 border-r">
              <div className="flex items-center flex-shrink-0 px-4 mb-6">
                <Link href="/marketplace" className="flex items-center space-x-2">
                  <Logo className="h-6 w-6" />
                  <span className="font-bold text-xl">Naly</span>
                </Link>
              </div>
              
              <div className="px-4 mb-6">
                <Button variant="outline" size="sm" asChild className="w-full">
                  <Link href="/marketplace">
                    <ArrowLeft className="h-4 w-4 mr-2" />
                    Back to Marketplace
                  </Link>
                </Button>
              </div>

              <div className="flex-1 px-4">
                <DashboardNav />
              </div>
            </div>
          </div>

          {/* Main content */}
          <div className="flex-1">
            <main className="p-6">
              {children}
            </main>
          </div>
        </div>
      </div>
    </AuthProvider>
  );
}