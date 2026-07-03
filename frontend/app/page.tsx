import CopyButton from './CopyButton';

const REPO_URL = 'https://github.com/<your-username>/Deepflow-Surrogate';

const demos = [
  {
    name: 'Deterministic Mesh Generation',
    tag: 'Core Demo',
    command: 'python mesh_generation.py --shape rectangle --width 8 --height 4 --seed 42',
    summary: 'Generate the same mesh topology every run for reproducible simulation pre-processing.',
  },
  {
    name: 'Test-Driven Validation',
    tag: 'Quality Demo',
    command: 'pytest -q',
    summary: 'Run focused tests that verify geometry behaviors and guard against regressions.',
  },
  {
    name: 'Performance Benchmarking',
    tag: 'Speed Demo',
    command: 'python benchmark_mesh_generation.py --runs 30',
    summary: 'Track throughput trends and compare optimization wins across commits.',
  },
];

export default function HomePage() {
  return (
    <main id="main-content" tabIndex={-1} className="page">
      <section className="hero glass" aria-labelledby="hero-heading">
        <p className="kicker">Deepflow-Surrogate</p>
        <h1 id="hero-heading">Show, don&apos;t tell.</h1>
        <p className="lead">
          A modern demo-driven showcase inspired by clean product storytelling—so visitors can immediately run,
          verify, and benchmark what this library does.
        </p>
        <div className="heroActions">
          <a
            className="button primary"
            href="#demos"
            style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}
          >
            Explore demos <span aria-hidden="true">↓</span>
          </a>
          <a
            className="button ghost"
            href={REPO_URL}
            target="_blank"
            rel="noopener noreferrer"
            aria-label="View on GitHub (opens in a new tab)"
            style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}
          >
            View on GitHub <span aria-hidden="true">↗</span>
          </a>
        </div>
      </section>

      <section id="demos" tabIndex={-1} className="section" aria-labelledby="demos-heading">
        <div className="sectionHeading">
          <h2 id="demos-heading">Demo flows</h2>
          <p>Each card is a practical workflow you can run in seconds.</p>
        </div>
        <ul role="list" className="cards" style={{ listStyle: 'none', padding: 0 }}>
          {demos.map((demo) => (
            <li className="card glass" key={demo.name}>
              <span className="chip">{demo.tag}</span>
              <h3>{demo.name}</h3>
              <p>{demo.summary}</p>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', justifyContent: 'space-between', minWidth: 0 }}>
                <code tabIndex={0} role="region" aria-label={`Code snippet for ${demo.name}`} style={{ flex: 1, margin: 0, minWidth: 0 }}>{demo.command}</code>
                <CopyButton text={demo.command} ariaLabel={`Copy command for ${demo.name}`} />
              </div>
            </li>
          ))}
        </ul>
      </section>

      <section className="section glass stack" aria-labelledby="run-everything-heading">
        <div className="sectionHeading">
          <h2 id="run-everything-heading">Run everything</h2>
          <p>Use the full sequence to preview generation, confidence checks, and performance baselines.</p>
        </div>
        <div style={{ position: 'relative' }}>
          <pre tabIndex={0} role="region" aria-label="Code snippet for full sequence" style={{ paddingRight: '5rem', margin: 0 }}>
{`python mesh_generation.py
pytest -q
python benchmark_mesh_generation.py`}
          </pre>
          <div style={{ position: 'absolute', top: '0.5rem', right: '0.5rem' }}>
            <CopyButton text={"python mesh_generation.py\npytest -q\npython benchmark_mesh_generation.py"} ariaLabel="Copy all commands" className="button overlay" />
          </div>
        </div>
      </section>
    </main>
  );
}
