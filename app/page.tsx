import AuthButton from "../components/AuthButton";
import Header from "../components/Header";

export default function Index() {
  return (
    <div className="flex-1 w-full flex flex-col items-center bg-white min-h-screen">
      <Header />
      <main className="w-full max-w-7xl flex flex-col items-center px-4">
        <div className="w-full flex flex-col md:flex-row gap-8 mt-8">
          {/* Left side: Chart and stat cards */}
          <div className="flex-1 flex flex-col gap-6">
            <div className="bg-gray-100 rounded-lg h-32 w-full flex items-center justify-center">
              {/* Chart Placeholder */}
              <span className="text-black">[Chart]</span>
            </div>
            <div className="bg-gray-100 rounded-lg h-12 w-2/3 flex items-center justify-center mx-auto">
              {/* Placeholder for small card */}
              <span className="text-black">[ ]</span>
            </div>
            <div className="bg-white rounded-xl shadow p-4 w-60 mt-8">
              <div className="text-xs text-black mb-1">Subscriptions</div>
              <div className="text-2xl font-bold text-black">+2350</div>
              <div className="text-xs text-green-600 font-semibold mb-2">+180.1% from last month</div>
              <div className="h-12 flex items-end">
                {/* Bar chart placeholder */}
                <div className="w-full h-8 bg-gray-200 rounded" />
              </div>
            </div>
          </div>

          {/* Center: Hero section */}
          <div className="flex-[2] flex flex-col items-center justify-center text-center gap-6">
            <div className="font-semibold text-lg mt-4 text-black">4000+ components</div>
            <h1 className="text-4xl md:text-5xl font-bold leading-tight text-black">Analyze your design with AI<br />& make better components</h1>
            <p className="max-w-xl mx-auto text-black">
              Analyze User Interface and improve User eXperience.<br />
              Naly AI can analyze your UI design based on simulated user persona and make beautiful components that fit your analysis results
            </p>
            <div className="flex w-full max-w-md mx-auto mt-2">
              <input
                className="flex-1 border border-gray-300 rounded-l px-4 py-2 focus:outline-none text-black"
                placeholder="Upload your design ..."
                type="text"
              />
              <button className="bg-gray-200 border border-gray-300 rounded-r px-6 py-2 font-semibold hover:bg-gray-300 transition text-black">Analyze</button>
            </div>
            <div className="flex flex-col md:flex-row gap-6 w-full justify-center mt-8">
              <div className="flex-1 bg-white border rounded-lg p-6 min-w-[200px]">
                <div className="font-bold text-lg mb-2 text-black">Usability Test</div>
                <div className="text-black text-sm">Test your UI for usability issues and get actionable feedback.</div>
              </div>
              <div className="flex-1 bg-white border rounded-lg p-6 min-w-[200px]">
                <div className="font-bold text-lg mb-2 text-black">Heuristic Evaluation</div>
                <div className="text-black text-sm">Evaluate your design against usability heuristics and best practices.</div>
              </div>
              <div className="flex-1 bg-white border rounded-lg p-6 min-w-[200px]">
                <div className="font-bold text-lg mb-2 text-black">Components Guide</div>
                <div className="text-black text-sm">Get suggestions for beautiful, effective UI components.</div>
              </div>
            </div>
          </div>

          {/* Right side: Team members */}
          <div className="flex-1 flex flex-col gap-6 items-end">
            <div className="bg-gray-100 rounded-lg h-32 w-full flex items-center justify-center">
              {/* Placeholder for image/card */}
              <span className="text-black">[ ]</span>
            </div>
            <div className="bg-white rounded-xl shadow p-4 w-72 mt-8">
              <div className="font-semibold text-black mb-2">Team Members</div>
              <div className="text-xs text-black mb-3">Invite your team members to collaborate</div>
              <ul className="space-y-2">
                <li className="flex items-center gap-2">
                  <span className="inline-block w-7 h-7 rounded-full bg-gray-200" />
                  <div>
                    <div className="font-medium text-sm text-black">Sofia Davis</div>
                    <div className="text-xs text-black">m@example.com</div>
                  </div>
                </li>
                <li className="flex items-center gap-2">
                  <span className="inline-block w-7 h-7 rounded-full bg-gray-200" />
                  <div>
                    <div className="font-medium text-sm text-black">Jackson Lee</div>
                    <div className="text-xs text-black">p@example.com</div>
                  </div>
                </li>
                <li className="flex items-center gap-2">
                  <span className="inline-block w-7 h-7 rounded-full bg-gray-200" />
                  <div>
                    <div className="font-medium text-sm text-black">Isabella Nguyen</div>
                    <div className="text-xs text-black">i@example.com</div>
                  </div>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
