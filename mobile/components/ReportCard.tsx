export default function ReportCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <article className="report-card">
      <h2>{title}</h2>
      {children}
    </article>
  );
}
