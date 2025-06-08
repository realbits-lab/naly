import { blockCategories } from "@/blocks";
import { Separator } from "@/components/ui/separator";
import { config } from "@/config";
import { components } from "@/description/app-sidebar";
import { capitalize } from "@/lib/utils";
import Link from "next/link";
import { Logo } from "../logo";
import { GithubLogo, TwitterLogo } from "../ui/icons";

const footerSections = [
  {
    title: "Components",
    links: components.slice(0, components.length / 2).map(({ title, url }) => ({
      title,
      href: url,
    })),
  },
  {
    title: "Components",
    links: components.slice(components.length / 2).map(({ title, url }) => ({
      title,
      href: url,
    })),
  },
  {
    title: "Blocks",
    links: blockCategories.map(({ name }) => ({
      title: `${capitalize(name)} section`,
      href: `/blocks/categories/${name}`,
    })),
  },
];

const Footer = () => {
  return (
    <footer className="bg-muted/50 border-t">
      <div className="max-w-screen-xl mx-auto">
        <div className="py-12 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-7 gap-x-8 gap-y-10 px-6 xl:px-0">
          <div className="col-span-full xl:col-span-2">
            {/* Logo */}
            <Link href="/" className="flex items-center gap-3">
              <Logo />
              <span className="font-bold text-lg">Shadcn UI Blocks</span>
            </Link>

            <p className="mt-4 text-muted-foreground">
              A collection of customized Shadcn UI blocks and components, ready
              for preview and copy.
            </p>
          </div>

          {footerSections.map(({ title, links }, index) => (
            <div key={index}>
              <h6 className="font-semibold">{title}</h6>
              <ul className="mt-6 space-y-4">
                {links.map(({ title, href }) => (
                  <li key={title}>
                    <Link
                      href={href}
                      className="text-muted-foreground hover:text-foreground"
                    >
                      {title}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
        <Separator />
        <div className="py-8 flex flex-col-reverse sm:flex-row items-center justify-between gap-x-2 gap-y-5 px-6 xl:px-0">
          {/* Copyright */}
          <span className="text-muted-foreground">
            &copy; {new Date().getFullYear()}{" "}
            <Link href="/" target="_blank">
              Shadcn UI Blocks
            </Link>
            . All rights reserved.
          </span>

          <div className="flex items-center gap-5 text-muted-foreground">
            <Link href={config.social.github} target="_blank">
              <GithubLogo className="h-5 w-5" />
            </Link>
            <Link href={config.social.twitter} target="_blank">
              <TwitterLogo className="h-5 w-5" />
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
