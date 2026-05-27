const REPO_URL = 'https://github.com/<your-username>/Deepflow-Surrogate';
const LICENSE_URL = 'https://github.com/<your-username>/Deepflow-Surrogate#license';

const capabilities = [
  {
    title: 'Deterministic Mesh Generation',
    description:
      'Generate repeatable surrogate 2D meshes from simple geometric definitions for fast simulation pre-processing.',
  },
  {
    title: 'Test-Driven Workflows',
    description:
      'Validate mesh behavior with dedicated test modules covering core logic and CLI-like interaction pathways.',
  },
  {
    title: 'Performance Benchmarking',
    description:
      'Run lightweight benchmark scripts to profile generation speed and compare optimization changes over time.',
  },
];

export default function HomePage() {
  return (
    <main className="container">
      <header className="hero">
        <p className="eyebrow">Deepflow-Surrogate</p>
        <h1>Vercel-ready frontend showcase</h1>
        <p>
          This frontend demonstrates how the project can be presented as a clean product page while highlighting mesh generation,
          testing, and benchmarking capabilities.
        </p>
      </header>

      <section>
        <h2>Project capabilities</h2>
        <div className="grid">
          {capabilities.map((item) => (
            <article key={item.title} className="card">
              <h3>{item.title}</h3>
              <p>{item.description}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="codeBlock">
        <h2>Quick start commands</h2>
        <pre>
{`python mesh_generation.py
pytest -q
python benchmark_mesh_generation.py`}
        </pre>
      </section>

      <footer>
        <a href={REPO_URL} target="_blank" rel="noreferrer">GitHub Repository</a>
        <a href={LICENSE_URL} target="_blank" rel="noreferrer">License</a>
        <a href="https://dhruvhaldar.vercel.app/" target="_blank" rel="noreferrer">Dhruv Haldar</a>
      </footer>
    </main>
  );
}
