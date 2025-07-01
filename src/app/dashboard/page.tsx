import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Download, Heart, Upload, Crown, TrendingUp, Calendar } from "lucide-react";

export default function DashboardPage() {
  // Mock user data - will be replaced with real data from Supabase
  const user = {
    name: "John Doe",
    email: "john@example.com",
    subscription: "Premium",
    downloads_this_month: 24,
    total_downloads: 156,
    favorites_count: 12,
    uploads_count: 3,
  };

  const recentDownloads = [
    {
      id: "1",
      title: "Modern Business Presentation",
      category: "Business",
      downloaded_at: "2024-01-15",
    },
    {
      id: "2", 
      title: "Creative Portfolio Template",
      category: "Design",
      downloaded_at: "2024-01-14",
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground mt-2">
          Welcome back, {user.name}! Here's what's happening with your account.
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Downloads This Month</CardTitle>
            <Download className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{user.downloads_this_month}</div>
            <p className="text-xs text-muted-foreground">
              +20% from last month
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Downloads</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{user.total_downloads}</div>
            <p className="text-xs text-muted-foreground">
              Since you joined
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Favorites</CardTitle>
            <Heart className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{user.favorites_count}</div>
            <p className="text-xs text-muted-foreground">
              Templates saved
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Uploads</CardTitle>
            <Upload className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{user.uploads_count}</div>
            <p className="text-xs text-muted-foreground">
              Templates shared
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Subscription Status */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Crown className="h-5 w-5 text-yellow-500" />
              Subscription Status
            </CardTitle>
            <CardDescription>
              Your current plan and usage
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="font-medium">Current Plan</span>
                <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
                  <Crown className="h-3 w-3 mr-1" />
                  {user.subscription}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Next billing date</span>
                <span className="text-sm">February 15, 2024</span>
              </div>
              <Button className="w-full">Manage Subscription</Button>
            </div>
          </CardContent>
        </Card>

        {/* Recent Downloads */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              Recent Downloads
            </CardTitle>
            <CardDescription>
              Your latest template downloads
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentDownloads.map((download) => (
                <div key={download.id} className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">{download.title}</p>
                    <p className="text-sm text-muted-foreground">{download.category}</p>
                  </div>
                  <span className="text-sm text-muted-foreground">
                    {download.downloaded_at}
                  </span>
                </div>
              ))}
              <Button variant="outline" className="w-full">
                View All Downloads
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}