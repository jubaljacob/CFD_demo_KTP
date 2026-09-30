# Reactor Flow & AI Experiment Assistant

### A CFD learning project and KTP application showcase

[**Explore the live demo →**](https://cfd-demo-ktp.vercel.app/) · [**View the repository →**](https://github.com/jubaljacob/CFD_demo_KTP)

> An engineering question becomes a controlled simulation study—with reviewable decisions, numerical checks and traceable results.

## Why I built this

I built this project for my application to the **University of Exeter and Oxford Instruments Plasma Technology KTP role**.

My background is in Python, AI and agentic systems. Computational fluid dynamics was unfamiliar territory, so I used this project to learn the physical principles, numerical methods and verification practices needed to connect AI tools with a scientific simulation workflow.

The work progressed from OpenFOAM tutorials and analytical channel-flow comparisons to a simplified 3D reactor study and an AI-assisted experiment interface.

## The engineering question

**How does adding a fifth, central inlet affect nitrogen delivery above a wafer?**

The demonstration compares four-inlet and five-inlet configurations using steady nitrogen flow and time-dependent passive-tracer transport.

Nine fixed gas-sampling positions, **2 mm above the wafer**, measure how quickly the incoming tracer reaches the region of interest. The principal metric is the time at which **all nine positions reach 90% of the inlet tracer concentration**, remaining above that threshold at subsequent recorded samples.

> This measures arrival at nine sampled positions—not 90% coverage of the wafer surface.

## What the results show

| Configuration | Total nitrogen supply | All-nine-probe 90% arrival |
| :--- | ---: | ---: |
| Four inlets | 300 sccm | 33.11 s |
| Five inlets | 375 sccm | 25.32 s |

The five-inlet case reached the threshold approximately **7.79 seconds sooner**.

Both cases used **75 sccm per inlet**, so adding the fifth inlet increased total supply by **25%** as well as changing the geometry. The result therefore cannot isolate the benefit of inlet placement or establish an optimal design.

A useful next study would hold total supply constant while comparing the two layouts.

## The AI use case

The local prototype explores a practical workflow for an **engineering experiment assistant**:

1. **Clarify the question**  
   Establish what changes, what stays fixed and what counts as success.

2. **Prepare a reviewable plan**  
   State the assumptions, required simulations, comparison metrics and resource limits.

3. **Execute approved work**  
   Run the defined study through controlled tools, keeping new cases separate from the reference evidence.

4. **Assess the evidence**  
   Check the mesh, solver results, flow balance and tracer history before drawing conclusions.

5. **Report supported findings**  
   Compare eligible results, explain limitations and identify insufficient evidence.

The intention is to assist an engineer’s investigation through **reviewable decisions and traceable results**.

## What you can explore online

- **Compare runs:** switch between completed experiments and numerical reference studies.
- **Inspect the reactor:** rotate the 3D geometry, toggle components and focus on the wafer.
- **View calculated flow:** explore exported nitrogen streamlines and recorded tracer playback.
- **Explore delivery:** compare tracer histories and assess an illustrative arrival target.
- **Review evidence:** inspect passed and failed checks.
- **Download results:** access probe histories, balance records and source fingerprints.
- **See the AI interface:** inspect the original question composer and experiment-planning controls.

> **Public demo mode:** the website is a static results viewer. AI and experiment-execution controls are visibly inactive. It does not launch OpenFOAM, contact an AI service or require a reviewer account.

## Verification and limitations

### Numerical checks

The learning workflow included:

- Analytical channel-flow comparisons.
- Mesh-refinement and time-step studies.
- Flow-balance and tracer-conservation checks.
- Concentration-bound and observation-history checks.
- Retention of an unsuccessful early fine-mesh tracer run as an example of evidence that must be rejected.

### Outstanding work

The five-inlet mesh retained **76 concave cells and 78 concave faces**, with **one strict mesh check failing**. It received conditional review for exploratory use.

Further mesh and time-step sensitivity studies are still required for this variant.

### Physical scope

The model uses **simplified geometry and isothermal passive nitrogen transport**. It does not simulate:

- Plasma or chemical reactions.
- Adsorption or deposition.
- Heat transfer.
- Film growth or film uniformity.

The model has **not been validated against real reactor measurements**.

This is an independent application project.

## Run the public viewer locally

Install **Node.js 22.12 or a supported newer release**, then run:

```bash
# Install the locked dependencies
npm ci

# Check evidence integrity and assessment logic
npm test

# Start the local development server
npm run dev
```

To build and preview the static production site:

```bash
# Build the static website
npm run build

# Preview the production build locally
npm run preview
```

### Repository contents

| Location | Contents |
| :--- | :--- |
| `src/` | Dashboard, reactor viewer and inactive assistant interface |
| `public/data/` | Compact study results, geometry, flow paths and fingerprints |
| `public/evidence/` | Baseline and variant probe histories and tracer-balance records |
| `public/media/` | Recorded tracer playback |
| `tests/` | Evidence-integrity and assessment checks |
| `SOURCES.txt` | Research and software source notes |
| `vercel.json` | Static deployment configuration |

**Full OpenFOAM fields and the executable local agent are not included** in this public viewer repository.

## References and acknowledgements

| Source | Role in the project |
| :--- | :--- |
| [Kimes, Moore and Maslar (2012)](https://doi.org/10.1063/1.4742991) | Reactor geometry inspiration |
| [Burgess, NIST Technical Note 2279 (2024)](https://doi.org/10.6028/NIST.TN.2279) | Gas diffusion reference |
| [OpenCFD OpenFOAM documentation and tutorials](https://www.openfoam.com/documentation/tutorial-guide) | Modelling and numerical methods |
| [ParaView documentation](https://docs.paraview.org/en/latest/) | Visualisation and post-processing |
| [ChatCFD](https://doi.org/10.1002/aidi.202500174) | Agent-assisted CFD design ideas |
| [arXiv:2605.06607](https://arxiv.org/abs/2605.06607) | Agent-assisted CFD research discussion |

These sources informed the project; the demonstration does not reproduce their complete research systems. Additional source notes are provided in [`SOURCES.txt`](SOURCES.txt).

---
