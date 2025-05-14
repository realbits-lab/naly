import Link from "next/link";

export default function Header() {
  return (
    <header className="w-full flex flex-col items-center mb-8">
      <nav className="w-full flex justify-center border-b border-b-foreground/10 h-16">
        <div className="w-full max-w-4xl flex justify-between items-center p-3 text-base font-medium">
          <div className="flex gap-8 items-center">
            <Link href="/" className="font-bold text-xl text-black">Naly</Link>
            <Link href="/products" className="text-black">Products</Link>
            <Link href="/components" className="text-black">Components</Link>
            <Link href="/pricing" className="text-black">Pricing</Link>
            <Link href="/contact" className="text-black">Contact</Link>
          </div>
          <Link href="/login" className="ml-8 text-black">Login</Link>
        </div>
      </nav>
    </header>
  );
}
