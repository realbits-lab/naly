import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

export default function AvatarWithRingDemo() {
  return (
    <Avatar className="ring-2 ring-green-500 ring-offset-[3px] ring-offset-background">
      <AvatarImage src="https://github.com/shadcn.png" alt="@shadcn" />
      <AvatarFallback>CN</AvatarFallback>
    </Avatar>
  );
}
