REACTOR EVIDENCE SHOWCASE

An independent KTP application demonstration by Jubal Jacob.

This repository contains a static reviewer dashboard, compact measured evidence,
reactor surfaces, calculated flow paths and recorded tracer playback. It does not
include the executable local AI agent, full OpenFOAM fields, or a live solver.
The assistant panel describes the demonstrated local workflow; it is not a live
conversation. The original question composer and planning controls are visible,
with live AI and execution actions explicitly disabled. Question drafts stay in
the browser. No API key, account connection or paid model is needed to view it.

LOCAL USE
Node.js 22.12+ (or a supported newer Node.js release) and npm are required.
  npm ci              Install the locked dependencies.
  npm test            Check evidence integrity and decision logic.
  npm run dev         Open the development viewer at the printed local address.
  npm run build       Produce the static site in dist/.
  npm run preview     Review the production build locally.

VERCEL
Import jubaljacob/CFD_demo_KTP from GitHub. Use the Vite framework preset,
npm run build, output directory dist, and no environment variables. This is a
static personal showcase; it does not need a server, database or paid AI service.

EVIDENCE
public/data/study.json contains the completed matched comparison and reference
assessments. public/evidence contains full nine-probe histories and tracer budget
records for the matched baseline and five-inlet variant. Download checksums verify
the included files; source-checksums identify original local evidence, some of
which is deliberately omitted here because raw CFD fields are large.

The source evidence was fingerprint-checked before export. Small numerical errors
and matching fingerprints do not establish experimental or engineering validity.
The study measured all nine gas probes 2 mm above the wafer reaching 90% of the
incoming passive nitrogen label. It did not measure 90% of wafer area, reaction
rate, deposition, real precursor purge or film uniformity.

The five-inlet study supplies 375 sccm versus the four-inlet baseline's 300 sccm:
75 sccm per inlet. Faster arrival combines increased supply and a layout change.
Strict concavity warnings were conditionally reviewed for exploratory use. Variant
mesh and time-step sensitivity and physical validation remain outstanding.

The reactor viewer renders surface geometry and a subset of ParaView-exported
steady velocity streamlines. Streamlines do not depict diffusion. The separate
movie is the original four-inlet tracer simulation, not the selected variant.

References and source roles are displayed on the site and in SOURCES.txt.
No Markdown documents, private chats, application documents or authentication
files are included. AI-assisted development is acknowledged on the site.
