// Daily Summary Template for Typst
// Usage: #import "daily-summary.typ": *
// Then call: #show: daily-summary.with(date: "2026-03-16", projects: ("proj1", "proj2"))

#let accent = rgb("#2563eb")       // blue-600
#let accent-light = rgb("#dbeafe") // blue-100
#let accent-dark = rgb("#1e40af")  // blue-800
#let subtle = rgb("#64748b")       // slate-500
#let bg-code = rgb("#f8fafc")      // slate-50
#let border = rgb("#e2e8f0")       // slate-200
#let success = rgb("#059669")      // emerald-600
#let warning = rgb("#d97706")      // amber-600

#let tag(body, color: accent) = {
  box(
    fill: color.lighten(85%),
    stroke: color.lighten(50%),
    radius: 3pt,
    inset: (x: 6pt, y: 3pt),
    text(color.darken(20%), size: 8pt, weight: "medium", body)
  )
}

#let snippet-box(lang: "bash", body) = {
  block(
    width: 100%,
    fill: bg-code,
    stroke: border,
    radius: 4pt,
    inset: 12pt,
    above: 8pt,
    below: 8pt,
    {
      text(subtle, size: 8pt, weight: "medium", upper(lang))
      v(4pt)
      text(font: "Menlo", size: 9pt, body)
    }
  )
}

#let concept-card(title, body) = {
  block(
    width: 100%,
    fill: accent-light.lighten(50%),
    stroke: accent.lighten(60%),
    radius: 4pt,
    inset: 12pt,
    above: 6pt,
    below: 6pt,
    {
      text(accent-dark, weight: "bold", size: 10pt, title)
      v(4pt)
      text(size: 9.5pt, body)
    }
  )
}

#let problem-solved(problem, solution) = {
  block(
    width: 100%,
    inset: (left: 12pt),
    above: 4pt,
    below: 4pt,
    {
      text(weight: "bold", size: 10pt, problem)
      linebreak()
      text(success, size: 9.5pt, sym.arrow.r + " " + solution)
    }
  )
}

#let daily-summary(
  date: none,
  sessions: 0,
  projects: (),
  web-conversations: 0,
  body,
) = {
  // Page setup
  set page(
    paper: "a4",
    margin: (top: 2cm, bottom: 2cm, left: 2cm, right: 2cm),
    header: context {
      if counter(page).get().first() > 1 {
        set text(8pt, subtle)
        [Daily Learning Summary]
        h(1fr)
        [#date]
      }
    },
    footer: context {
      set text(8pt, subtle)
      h(1fr)
      counter(page).display("1 / 1", both: true)
      h(1fr)
    },
  )

  // Typography
  set text(font: "New Computer Modern", size: 10.5pt, lang: "en")
  set par(leading: 0.7em, justify: true)

  // Headings
  show heading.where(level: 1): it => {
    v(0.3em)
    text(size: 22pt, weight: "bold", fill: accent-dark, it.body)
    v(0.2em)
  }

  show heading.where(level: 2): it => {
    v(0.8em)
    block(
      below: 0.5em,
      {
        text(size: 13pt, weight: "bold", fill: accent, it.body)
        v(2pt)
        line(length: 100%, stroke: 0.5pt + accent.lighten(60%))
      }
    )
  }

  show heading.where(level: 3): it => {
    v(0.4em)
    text(size: 11pt, weight: "bold", it.body)
    v(0.2em)
  }

  // Code blocks
  show raw.where(block: true): it => {
    block(
      width: 100%,
      fill: bg-code,
      stroke: border,
      radius: 4pt,
      inset: 10pt,
      above: 8pt,
      below: 8pt,
      text(font: "Menlo", size: 9pt, it)
    )
  }

  show raw.where(block: false): it => {
    box(
      fill: bg-code,
      stroke: border,
      radius: 2pt,
      inset: (x: 4pt, y: 2pt),
      text(font: "Menlo", size: 9pt, it)
    )
  }

  // Lists
  set list(marker: text(accent, sym.bullet), indent: 12pt, body-indent: 6pt)

  // Title block
  {
    v(1cm)
    align(center, {
      text(subtle, size: 10pt, weight: "medium", [DAILY LEARNING SUMMARY])
      v(6pt)
      text(size: 28pt, weight: "bold", fill: accent-dark, date)
      v(12pt)
      line(length: 40%, stroke: 1pt + accent.lighten(60%))
      v(12pt)

      // Stats row
      let stat-box(label, value) = {
        box(inset: (x: 16pt), {
          text(size: 18pt, weight: "bold", fill: accent, str(value))
          linebreak()
          text(size: 8pt, fill: subtle, weight: "medium", upper(label))
        })
      }

      stat-box("Sessions", sessions)
      stat-box("Projects", projects.len())
      stat-box("Web Chats", web-conversations)

      v(8pt)
      for p in projects {
        tag(p)
        h(4pt)
      }
    })
    v(0.5cm)
  }

  body
}
