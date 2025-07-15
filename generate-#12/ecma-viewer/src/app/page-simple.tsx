export default function SimplePage() {
  return (
    <div>
      <h1>ECMA-376 Database Viewer</h1>
      <p>Testing basic functionality</p>
      <a href="/api/health">Health Check</a>
      <br />
      <a href="/api/stats">Database Stats</a>
      <br />
      <a href="/api/sections?limit=5">Sample Sections</a>
    </div>
  );
}