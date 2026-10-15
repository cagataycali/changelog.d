---
title: changelog.d
hide:
  - navigation
  - toc
---

# changelog.d

<div class="cd-hero" markdown>

<span class="cd-eyebrow">a changelog convention + a GitHub Action</span>

<h1 class="cd-title">Every change gets <em>its own file.</em></h1>

<p class="cd-lede">
Ten pull requests open at once, maybe ten agents writing them. Each one adds a tiny
file to <code>changelog.d/</code> instead of editing the same line of
<code>CHANGELOG.md</code>. Nobody collides, nobody rebases, nobody waits for a second review.
</p>

<div class="cd-cta">
  <a class="cd-btn cd-btn--hot" href="action/">Add it to a repo →</a>
  <a class="cd-btn" href="why/">Why it works</a>
  <a class="cd-btn" href="https://github.com/cagataycali/changelog.d">GitHub</a>
</div>

<div class="cd-term" aria-label="terminal demo"><div class="cd-term__dots"><i></i><i></i><i></i></div><pre class="cd-term__out"></pre></div>

</div>

<div class="cd-duel">
  <figure class="cd-scene cd-scene--bad">
    <figcaption>The usual way<small>three PRs, one line to append to</small></figcaption>
    <div class="cd-stage">
      <span class="cd-card">#41</span><span class="cd-card">#42</span><span class="cd-card">#43</span>
      <div class="cd-boom">CONFLICT</div>
      <div class="cd-target">CHANGELOG.md · ## [Unreleased]</div>
    </div>
    <p class="cd-legend">The first merge wins. The other two go stale, get rebased and lose their approval.</p>
  </figure>
  <figure class="cd-scene cd-scene--good">
    <figcaption>changelog.d<small>three PRs, three files</small></figcaption>
    <div class="cd-stage">
      <div class="cd-slots"><span class="cd-slot">41-….md</span><span class="cd-slot">42-….md</span><span class="cd-slot">43-….md</span></div>
      <span class="cd-card">#41</span><span class="cd-card">#42</span><span class="cd-card">#43</span>
      <div class="cd-target">release → CHANGELOG.md</div>
    </div>
    <p class="cd-legend">Each one lands on its own. At release they are folded into the log in one go.</p>
  </figure>
</div>

<div class="cd-stat cd-reveal">
  <span class="cd-stat__n">2,487</span>
  <span class="cd-stat__t">of 2,556 commits on <a href="https://github.com/strands-labs/robots">strands-labs/robots</a> in the 11 weeks after
  the convention landed carried a fragment, while Strands Agents opened pull requests around the clock.
  <b>Zero</b> edited the changelog by hand.</span>
</div>

## Try it

Type a change. This is the whole file.

<div class="cd-maker">
  <div class="cd-maker__row">
    <input name="number" type="number" min="1" value="42" aria-label="PR number">
    <select name="category" aria-label="category">
      <option>Fixed</option><option>Added</option><option>Changed</option><option>Removed</option>
      <option>Security</option><option>Docs</option><option>Performance</option>
    </select>
    <input name="summary" type="text" value="a robot stops in 10 ms when you press the e-stop" aria-label="summary">
  </div>
  <div class="cd-maker__file"></div>
  <pre><code class="language-markdown"></code></pre>
</div>

## Three checks, one action

<div class="cd-grid cd-reveal">
  <div class="cd-tile"><span class="cd-n">01</span><b>Nothing written to the log</b><p>A new <code>###</code> entry under <code>[Unreleased]</code> is refused and named. Release PRs pass, entry by entry.</p></div>
  <div class="cd-tile"><span class="cd-n">02</span><b>Every fragment is valid</b><p>Real PR number, one <code>###</code> heading, no forged <code>##</code> versions. Only your branch's own files are judged.</p></div>
  <div class="cd-tile"><span class="cd-n">03</span><b>A fragment exists</b><p>Code changed? Then say what changed. Docs-only and labelled PRs can skip it.</p></div>
</div>

```yaml title=".github/workflows/changelog.yml"
on: pull_request
jobs:
  changelog:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: cagataycali/changelog.d@main
        with:
          ignore: "docs/**, *.md"
```

Then at release time:

```bash
pip install git+https://github.com/cagataycali/changelog.d
changelog-d apply      # folds every fragment into CHANGELOG.md and deletes them
```

That's it. [The fragment rules →](fragments.md) · [Teach your agents →](agents.md)
