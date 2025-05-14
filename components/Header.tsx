import Link from "next/link";
import AuthButton from "./AuthButton";

export default async function Header() {
  return (
    <header className="w-full flex flex-col items-center mb-8">
      <nav className="w-full flex justify-center border-b border-b-foreground/10 h-16">
        <div className="w-full max-w-4xl flex justify-between items-center p-3 text-base font-medium">
          <div className="flex gap-8 items-center">
            <Link href="/" className="font-bold text-xl text-white">Naly</Link>
            <Link href="/products" className="text-gray-100">Products</Link>
            <Link href="/components" className="text-gray-100">Components</Link>
            <Link href="/pricing" className="text-gray-100">Pricing</Link>
            <Link href="/contact" className="text-gray-100">Contact</Link>
          </div>
          <div className="ml-8">
            <AuthButton />
          </div>
        </div>
      </nav>
    </header>
  );
}
