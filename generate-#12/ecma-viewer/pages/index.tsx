import Head from 'next/head';

export default function Home() {
  return (
    <>
      <Head>
        <title>ECMA-376 Database Viewer</title>
        <meta name="description" content="Browse and search ECMA-376 documentation sections" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>
      
      <div className="container">
        {/* Header */}
        <div className="header">
          <h1>ECMA-376 Database Viewer</h1>
          <p>Browse and search ECMA-376 documentation sections</p>
          <div style={{ marginTop: '12px' }}>
            <span>Database: </span>
            <span id="db-status" className="status-badge">Checking...</span>
          </div>
        </div>

        {/* Statistics */}
        <div id="stats-grid" className="stats-grid">
          <div className="stat-card">
            <div className="stat-value" id="total-sections">--</div>
            <div className="stat-label">Total Sections</div>
          </div>
          <div className="stat-card">
            <div className="stat-value" id="with-embeddings">--</div>
            <div className="stat-label">With Embeddings</div>
          </div>
          <div className="stat-card">
            <div className="stat-value" id="depth-levels">--</div>
            <div className="stat-label">Depth Levels</div>
          </div>
          <div className="stat-card">
            <div className="stat-value" id="section-types">--</div>
            <div className="stat-label">Section Types</div>
          </div>
        </div>

        {/* Controls */}
        <div className="controls">
          <div className="search-row">
            <input type="text" id="search-input" className="search-input" placeholder="Search sections by title or description..." />
            <button onClick={() => (window as any).search()} className="btn btn-primary">Search</button>
            <button onClick={() => (window as any).clearSearch()} className="btn btn-secondary">Clear</button>
          </div>
          <div className="filter-buttons">
            <button onClick={() => (window as any).filterDepth(null)} className="btn btn-outline active" id="filter-all">All Levels</button>
            <button onClick={() => (window as any).filterDepth(1)} className="btn btn-outline" id="filter-1">Level 1</button>
            <button onClick={() => (window as any).filterDepth(2)} className="btn btn-outline" id="filter-2">Level 2</button>
            <button onClick={() => (window as any).filterDepth(3)} className="btn btn-outline" id="filter-3">Level 3</button>
            <button onClick={() => (window as any).filterDepth(4)} className="btn btn-outline" id="filter-4">Level 4</button>
            <button onClick={() => (window as any).filterDepth(5)} className="btn btn-outline" id="filter-5">Level 5</button>
          </div>
        </div>

        {/* Table */}
        <div className="table-container">
          <div id="loading" className="loading">Loading...</div>
          <table className="table" id="sections-table" style={{ display: 'none' }}>
            <thead>
              <tr>
                <th>Section #</th>
                <th>Level</th>
                <th>Title</th>
                <th>Description</th>
                <th>Type</th>
              </tr>
            </thead>
            <tbody id="table-body">
            </tbody>
          </table>
          <div id="load-more" className="load-more" style={{ display: 'none' }}>
            <button onClick={() => (window as any).loadMore()} className="btn btn-outline">Load More</button>
          </div>
        </div>

        {/* Pagination Controls */}
        <div id="pagination-controls" className="pagination-controls" style={{ display: 'none' }}>
          <div id="pagination-info" className="pagination-info"></div>
          <div className="pagination-buttons">
            <button id="prev-btn" onClick={() => (window as any).previousPage()} className="btn btn-outline">Previous</button>
            <span id="page-info" style={{ margin: '0 16px', fontWeight: 500 }}></span>
            <button id="next-btn" onClick={() => (window as any).nextPage()} className="btn btn-outline">Next</button>
          </div>
        </div>
      </div>

      <style jsx>{`
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: system-ui, -apple-system, sans-serif; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: white; padding: 24px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 24px; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 16px; margin-bottom: 24px; }
        .stat-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stat-value { font-size: 2rem; font-weight: bold; color: #333; }
        .stat-label { color: #666; font-size: 0.9rem; margin-top: 4px; }
        .controls { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 24px; }
        .search-row { display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; }
        .search-input { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; min-width: 200px; }
        .btn { padding: 10px 16px; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; }
        .btn-primary { background: #007bff; color: white; }
        .btn-secondary { background: #6c757d; color: white; }
        .btn-outline { background: white; color: #007bff; border: 1px solid #007bff; }
        .btn.active { background: #007bff; color: white; }
        .filter-buttons { display: flex; gap: 8px; flex-wrap: wrap; }
        .table-container { background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); overflow: hidden; }
        .table { width: 100%; border-collapse: collapse; }
        .table th, .table td { padding: 12px; text-align: left; border-bottom: 1px solid #eee; }
        .table th { background: #f8f9fa; font-weight: 600; }
        .badge { display: inline-block; padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: 500; }
        .loading { text-align: center; padding: 40px; color: #666; }
        .status-badge { padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: 500; }
        .status-healthy { background: #d4edda; color: #155724; }
        .status-error { background: #f8d7da; color: #721c24; }
        .load-more { text-align: center; padding: 20px; }
        .pagination-controls { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-top: 24px; text-align: center; }
        .pagination-info { margin-bottom: 16px; color: #666; font-size: 14px; }
        .pagination-buttons { display: flex; gap: 12px; justify-content: center; align-items: center; }
        .btn-disabled { background: #e9ecef; color: #6c757d; cursor: not-allowed; }
        .depth-1 { background: #fee; color: #c33; }
        .depth-2 { background: #eef; color: #33c; }
        .depth-3 { background: #efe; color: #3c3; }
        .depth-4 { background: #ffe; color: #cc3; }
        .depth-5 { background: #fef; color: #c3c; }
      `}</style>

      <script dangerouslySetInnerHTML={{
        __html: `
        let currentSections = [];
        let currentOffset = 0;
        let currentSearch = '';
        let currentDepth = null;
        let hasMore = true;
        
        // Pagination state
        let currentPage = 1;
        let totalPages = 1;
        let totalSections = 0;
        let pageSize = 50;
        let isPaginating = false;

        // Initialize
        async function init() {
          await checkHealth();
          await loadStats();
          await loadSections();
        }

        // Health check
        async function checkHealth() {
          try {
            const response = await fetch('/api/health');
            const data = await response.json();
            const statusEl = document.getElementById('db-status');
            if (data.status === 'healthy') {
              statusEl.className = 'status-badge status-healthy';
              statusEl.textContent = 'Connected';
            } else {
              statusEl.className = 'status-badge status-error';
              statusEl.textContent = 'Error';
            }
          } catch (error) {
            const statusEl = document.getElementById('db-status');
            statusEl.className = 'status-badge status-error';
            statusEl.textContent = 'Disconnected';
          }
        }

        // Load statistics
        async function loadStats() {
          try {
            const response = await fetch('/api/stats');
            const data = await response.json();
            document.getElementById('total-sections').textContent = data.general.total_sections.toLocaleString();
            document.getElementById('with-embeddings').textContent = data.general.sections_with_embeddings.toLocaleString();
            document.getElementById('depth-levels').textContent = Object.keys(data.depth_distribution).length;
            document.getElementById('section-types').textContent = Object.keys(data.type_distribution).length;
          } catch (error) {
            console.error('Failed to load stats:', error);
          }
        }

        // Load sections
        async function loadSections(reset = false) {
          if (reset) {
            currentOffset = 0;
            currentSections = [];
            document.getElementById('table-body').innerHTML = '';
          }

          const params = new URLSearchParams();
          params.set('limit', '50');
          params.set('offset', currentOffset.toString());
          
          if (currentSearch) params.set('search', currentSearch);
          if (currentDepth !== null) params.set('depth', currentDepth.toString());

          try {
            document.getElementById('loading').style.display = reset ? 'block' : 'none';
            
            const response = await fetch(\`/api/sections?\${params.toString()}\`);
            const data = await response.json();
            
            if (reset) {
              currentSections = data.sections;
            } else {
              currentSections = [...currentSections, ...data.sections];
            }

            renderSections();
            hasMore = data.sections.length === 50;
            document.getElementById('load-more').style.display = hasMore && !currentSearch && currentDepth === null ? 'block' : 'none';
            currentOffset += data.sections.length;

          } catch (error) {
            console.error('Failed to load sections:', error);
          } finally {
            document.getElementById('loading').style.display = 'none';
            document.getElementById('sections-table').style.display = 'table';
          }
        }

        // Load sections with pagination
        async function loadSectionsWithPagination() {
          const params = new URLSearchParams();
          params.set('limit', pageSize.toString());
          params.set('offset', ((currentPage - 1) * pageSize).toString());
          
          if (currentSearch) params.set('search', currentSearch);
          if (currentDepth !== null) params.set('depth', currentDepth.toString());

          try {
            document.getElementById('loading').style.display = 'block';
            document.getElementById('sections-table').style.display = 'none';
            
            const response = await fetch(\`/api/sections?\${params.toString()}\`);
            const data = await response.json();
            
            currentSections = data.sections;
            
            // Get total count for pagination
            const countParams = new URLSearchParams();
            if (currentSearch) countParams.set('search', currentSearch);
            if (currentDepth !== null) countParams.set('depth', currentDepth.toString());
            countParams.set('limit', '1');
            countParams.set('offset', '0');
            
            // Use a large limit to get total count (we'll improve this later)
            const countResponse = await fetch(\`/api/sections?\${countParams.toString()}&limit=10000\`);
            const countData = await countResponse.json();
            totalSections = countData.sections.length;
            totalPages = Math.ceil(totalSections / pageSize);
            
            renderSections();
            updatePaginationUI();
            
            // Hide load more button and show pagination
            document.getElementById('load-more').style.display = 'none';
            document.getElementById('pagination-controls').style.display = 'block';

          } catch (error) {
            console.error('Failed to load sections with pagination:', error);
          } finally {
            document.getElementById('loading').style.display = 'none';
            document.getElementById('sections-table').style.display = 'table';
          }
        }

        // Update pagination UI
        function updatePaginationUI() {
          const prevBtn = document.getElementById('prev-btn');
          const nextBtn = document.getElementById('next-btn');
          const pageInfo = document.getElementById('page-info');
          const paginationInfo = document.getElementById('pagination-info');
          
          // Update page info
          pageInfo.textContent = \`Page \${currentPage} of \${totalPages}\`;
          
          // Update pagination info
          const startItem = (currentPage - 1) * pageSize + 1;
          const endItem = Math.min(currentPage * pageSize, totalSections);
          paginationInfo.textContent = \`Showing \${startItem}-\${endItem} of \${totalSections.toLocaleString()} sections\`;
          
          // Update button states
          if (currentPage <= 1) {
            prevBtn.classList.add('btn-disabled');
            prevBtn.disabled = true;
          } else {
            prevBtn.classList.remove('btn-disabled');
            prevBtn.disabled = false;
          }
          
          if (currentPage >= totalPages) {
            nextBtn.classList.add('btn-disabled');
            nextBtn.disabled = true;
          } else {
            nextBtn.classList.remove('btn-disabled');
            nextBtn.disabled = false;
          }
        }

        // Previous page
        function previousPage() {
          if (currentPage > 1) {
            currentPage--;
            loadSectionsWithPagination();
          }
        }

        // Next page
        function nextPage() {
          if (currentPage < totalPages) {
            currentPage++;
            loadSectionsWithPagination();
          }
        }

        // Render sections
        function renderSections() {
          const tbody = document.getElementById('table-body');
          tbody.innerHTML = '';

          currentSections.forEach(section => {
            const row = document.createElement('tr');
            row.innerHTML = \`
              <td style="font-family: monospace; font-size: 0.9em;">\${section.full_section_number}</td>
              <td><span class="badge depth-\${section.depth}">\${section.depth}</span></td>
              <td style="font-weight: 500;">\${truncate(section.title, 80)}</td>
              <td style="color: #666; font-size: 0.9em;">\${truncate(section.description || '', 120)}</td>
              <td style="font-size: 0.9em;">\${section.section_type || '-'}</td>
            \`;
            tbody.appendChild(row);
          });
        }

        // Search
        function search() {
          currentSearch = document.getElementById('search-input').value.trim();
          loadSections(true);
        }

        // Clear search
        function clearSearch() {
          currentSearch = '';
          document.getElementById('search-input').value = '';
          loadSections(true);
        }

        // Filter by depth with pagination
        async function filterDepth(depth) {
          currentDepth = depth;
          currentPage = 1;
          isPaginating = depth !== null;
          
          // Update button states
          document.querySelectorAll('.filter-buttons .btn').forEach(btn => {
            btn.classList.remove('active');
            btn.classList.add('btn-outline');
          });
          
          const activeBtn = depth === null ? 
            document.getElementById('filter-all') : 
            document.getElementById(\`filter-\${depth}\`);
          activeBtn.classList.add('active');
          activeBtn.classList.remove('btn-outline');

          if (isPaginating) {
            await loadSectionsWithPagination();
          } else {
            loadSections(true);
          }
        }

        // Load more
        function loadMore() {
          loadSections(false);
        }

        // Utility functions
        function truncate(text, maxLength) {
          if (!text) return '-';
          return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
        }

        // Event listeners
        document.addEventListener('DOMContentLoaded', function() {
          document.getElementById('search-input').addEventListener('keydown', function(e) {
            if (e.key === 'Enter') search();
          });
          
          // Initialize the app
          init();
        });

        // Make functions available globally
        window.search = search;
        window.clearSearch = clearSearch;
        window.filterDepth = filterDepth;
        window.loadMore = loadMore;
        window.previousPage = previousPage;
        window.nextPage = nextPage;
        `
      }} />
    </>
  );
}