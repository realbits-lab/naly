import Link from "next/link";
import { Button } from "./ui/button";
import { GithubLogo } from "./ui/icons";

const OWNER = "akash3444";
const REPO = "shadcn-ui-blocks";

export const GithubStarButton = async () => {
  return (
    <Button variant="outline" className="rounded-full shadow-none px-3" asChild>
      <Link href={`https://github.com/${OWNER}/${REPO}`} target="_blank">
        <GithubLogo className="!h-5 !w-5" />
        Star
      </Link>
    </Button>
  );
};
