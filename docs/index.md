---
title: changelog.d
hide:
  - navigation
  - toc
---

# changelog.d

<div class="cd-hero" markdown>

<span class="cd-eyebrow">a changelog habit + a GitHub check</span>

<h1 class="cd-title">Every change gets <em>its own file.</em></h1>

<p class="cd-lede">
Most projects keep a <code>CHANGELOG.md</code>, and every pull request edits <b>the same few lines at the top</b>.
So when one is merged, the others break. changelog.d fixes that: <b>each pull request adds its own small file</b>
instead, and they're all gathered into the changelog when you release.
</p>

<div class="cd-cta">
  <a class="cd-btn cd-btn--hot" href="action/">Add it to your repo →</a>
  <a class="cd-btn" href="why/">Why it works</a>
  <a class="cd-btn" href="https://github.com/cagataycali/changelog.d">GitHub</a>
</div>

<div class="cd-term" aria-label="terminal demo"><div class="cd-term__dots"><i></i><i></i><i></i></div><pre class="cd-term__out"></pre></div>

</div>

## The problem, in one picture

<div class="cd-duel">
  <figure class="cd-scene cd-scene--bad">
    <figcaption>Without changelog.d<small>three pull requests, one shared line</small></figcaption>
    <div class="cd-stage">
      <span class="cd-card">#41</span><span class="cd-card">#42</span><span class="cd-card">#43</span>
      <div class="cd-boom">CONFLICT</div>
      <div class="cd-target">CHANGELOG.md</div>
    </div>
    <p class="cd-legend">The first one merges. The other two now conflict and have to be fixed by hand.</p>
  </figure>
  <figure class="cd-scene cd-scene--good">
    <figcaption>With changelog.d<small>three pull requests, three files</small></figcaption>
    <div class="cd-stage">
      <div class="cd-slots"><span class="cd-slot">41.md</span><span class="cd-slot">42.md</span><span class="cd-slot">43.md</span></div>
      <span class="cd-card">#41</span><span class="cd-card">#42</span><span class="cd-card">#43</span>
      <div class="cd-target">release → CHANGELOG.md</div>
    </div>
    <p class="cd-legend">Nobody touches the same file, so all three merge cleanly. They're combined at release.</p>
  </figure>
</div>

<div class="cd-aside" markdown>
**Think of it like sticky notes.** Rather than everyone queuing to write on the top line of one whiteboard,
each person drops a sticky note in a box. When it's time to release, you empty the box onto the board, newest first.
</div>

## How it works

<div class="cd-steps">
  <div class="cd-step"><b>Write a note</b><p>Your pull request adds one file, like <code>changelog.d/42-dark-mode.md</code>, saying what changed.</p></div>
  <div class="cd-step"><b>The check reads it</b><p>A GitHub Action makes sure the note is there and is written correctly. It takes a few seconds.</p></div>
  <div class="cd-step"><b>Release</b><p>Run <code>changelog-d apply</code>. Every note goes into <code>CHANGELOG.md</code> and the files are cleaned up.</p></div>
</div>

## Try it

Fill this in. The box below is the whole file you’d add.

<div class="cd-maker">
  <div class="cd-maker__row">
    <div><label for="cd-n">PR number</label><input id="cd-n" name="number" type="number" min="1" value="42"></div>
    <div><label for="cd-c">Kind</label><select id="cd-c" name="category">
      <option>Added</option><option selected>Fixed</option><option>Changed</option><option>Removed</option>
      <option>Security</option><option>Docs</option></select></div>
    <div><label for="cd-s">What changed</label><input id="cd-s" name="summary" type="text" value="the login button works on phones"></div>
  </div>
  <div class="cd-maker__file"></div>
  <pre><code class="language-markdown"></code></pre>
</div>

## Add it to your repo

Create this one file, and every pull request is checked from then on:

```yaml title=".github/workflows/changelog.yml"
on: pull_request
jobs:
  changelog:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: cagataycali/changelog.d@main
```

When it's time to release:

```bash
pip install git+https://github.com/cagataycali/changelog.d
changelog-d apply
```

<div class="cd-stat">
  <span class="cd-stat__n">97%</span>
  <p class="cd-stat__t">of commits on <a href="https://github.com/strands-labs/robots">strands-labs/robots</a> carried a note over
  11 weeks (<b>2,487 of 2,556</b>), while AI agents opened pull requests day and night. Not one commit edited the changelog by hand.</p>
</div>

Next: [what a note looks like →](fragments.md) · [using it with AI agents →](agents.md)
