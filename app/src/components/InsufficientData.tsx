export function InsufficientData({
  items,
}: {
  items: { question: string; n_yes: number; n_answered: number }[]
}) {
  return (
    <section className="insufficient-data" aria-label="Insufficient data">
      <h2>Not enough data to say anything</h2>
      <p className="section-subtitle">
        These journal questions were tracked, but too few "yes" answers exist to support a
        claim. Showing them is the honest alternative to a confident-sounding n=8 statistic.
      </p>
      <div className="table-scroll">
      <table>
        <thead>
          <tr>
            <th>Question</th>
            <th>Yes</th>
            <th>Answered</th>
          </tr>
        </thead>
        <tbody>
          {items.map((row) => (
            <tr key={row.question}>
              <td>{row.question}</td>
              <td>{row.n_yes}</td>
              <td>{row.n_answered}</td>
            </tr>
          ))}
        </tbody>
      </table>
      </div>
    </section>
  )
}
