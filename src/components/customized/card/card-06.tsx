import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import {
  HeartIcon,
  MessageCircleIcon,
  MoreHorizontalIcon,
  ShareIcon,
} from "lucide-react";
import Image from "next/image";

export default function CardPost() {
  return (
    <Card className="w-full max-w-xs shadow-none">
      <CardHeader className="flex flex-row items-center justify-between py-2">
        <div className="flex items-center gap-3">
          <Image
            src="https://github.com/shadcn.png"
            className="h-8 w-8 rounded-full bg-secondary object-contain"
            alt=""
            height={32}
            width={32}
          />
          <div className="flex flex-col gap-0.5">
            <h6 className="text-sm leading-none font-medium">shadcn</h6>
            <span className="text-xs">@shadcn</span>
          </div>
        </div>
        <Button variant="ghost" size="icon">
          <MoreHorizontalIcon />
        </Button>
      </CardHeader>
      <CardContent className="p-0">
        <div className="relative aspect-video bg-muted border-y" />
        <div className="pt-3 pb-4 px-6">
          <h2 className="font-semibold">Exploring New Horizons</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Had an amazing time discovering hidden gems! 🌄 Can&apos;t wait to
            share more from this journey.{" "}
            <span className="text-blue-500">#Wanderlust</span>{" "}
            <span className="text-blue-500">#NatureLovers</span>
          </p>
        </div>
      </CardContent>
      <Separator />
      <CardFooter className="flex py-2 px-2">
        <Button variant="ghost" className="w-full text-muted-foreground">
          <HeartIcon /> <span className="hidden sm:inline">Like</span>
        </Button>
        <Button variant="ghost" className="w-ful text-muted-foreground">
          <MessageCircleIcon />
          <span className="hidden sm:inline">Comment</span>
        </Button>
        <Button variant="ghost" className="w-full text-muted-foreground">
          <ShareIcon /> <span className="hidden sm:inline">Share</span>
        </Button>
      </CardFooter>
    </Card>
  );
}
