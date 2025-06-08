import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function FileInputDemo() {
  return (
    <div className="w-full max-w-xs">
      <Label htmlFor="picture">Profile Picture</Label>
      <Input id="picture" type="file" className="mt-1 file:pt-0.5" />
    </div>
  );
}
