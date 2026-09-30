REACTOR FLOW & AI EXPERIMENT ASSISTANT
A CFD learning project and KTP application showcase

Live demo: https://cfd-demo-ktp.vercel.app/
Repository: https://github.com/jubaljacob/CFD_demo_KTP


WHY I BUILT THIS

I built this project for my application to the University of Exeter and Oxford Instruments Plasma Technology KTP role.

My background is in Python, AI and agentic systems. Computational fluid dynamics was unfamiliar territory, so I used this project to learn the physical principles, numerical methods and verification practices needed to connect AI tools with a scientific simulation workflow.

The work progressed from OpenFOAM tutorials and analytical channel-flow comparisons to a simplified 3D reactor study and an AI-assisted experiment interface.


THE ENGINEERING QUESTION

How does adding a fifth, central inlet affect nitrogen delivery above a wafer?

The demonstration compares four-inlet and five-inlet configurations using steady nitrogen flow and time-dependent passive-tracer transport. Nine fixed gas-sampling positions, 2 mm above the wafer, measure how quickly the incoming tracer reaches the region of interest.

The principal metric is the time at which all nine positions reach 90% of the inlet tracer concentration and remain above that threshold at subsequent recorded samples.

This measures arrival at nine sampled positions—not 90% coverage of the wafer surface.


WHAT THE RESULTS SHOW

Four inlets:
• Nitrogen supply: 300 sccm
• All-nine-probe 90% arrival: 33.11 seconds

Five inlets:
• Nitrogen supply: 375 sccm
• All-nine-probe 90% arrival: 25.32 seconds

The five-inlet case reached the threshold approximately 7.79 seconds sooner.

Both cases used 75 sccm per inlet. Adding the fifth inlet therefore increased total supply by 25%, as well as changing the geometry. The result cannot isolate the benefit of inlet placement or establish an optimal design.

A useful next study would hold total supply constant while comparing the two layouts.


THE AI USE CASE

The local prototype explores a practical workflow for an engineering experiment assistant:

1. Clarify the question: what changes, what stays fixed and what counts as success.
2. Prepare a reviewable experiment plan with explicit assumptions and resource limits.
3. Execute approved work through controlled tools.
4. Check the mesh, solver results, flow balance and tracer evidence.
5. Report supported comparisons and identify insufficient evidence.

The intention is to assist an engineer’s investigation, with reviewable decisions and traceable results.


WHAT YOU CAN EXPLORE ONLINE

• Switch between completed runs and numerical reference studies.
• Rotate the 3D reactor and inspect calculated nitrogen flow paths.
• Toggle reactor components and focus on the wafer region.
• Compare tracer histories and assess an illustrative arrival target.
• Inspect passed and failed evidence checks.
• Download probe histories, balance records and source fingerprints.
• View the original AI question and experiment-planning interface.

The public site is a static results viewer. AI and experiment-execution controls are visibly inactive. It does not launch OpenFOAM, contact an AI service or require a reviewer account.


VERIFICATION AND LIMITATIONS

The learning workflow included analytical channel-flow checks, mesh refinement, time-step comparisons and tracer conservation checks. An unsuccessful early fine-mesh tracer run is retained as an example of evidence that must be rejected.

The five-inlet mesh retained 76 concave cells and 78 concave faces, with one strict mesh check failing. It received conditional review for exploratory use. Further mesh and time-step sensitivity studies are still required for this variant.

The model uses simplified geometry and isothermal passive nitrogen transport. It does not simulate plasma, chemical reactions, adsorption, heat transfer or deposition, and has not been validated against reactor measurements.

This is an independent application project, not a validated model of Oxford Instruments equipment.


RUN THE PUBLIC VIEWER LOCALLY

Install Node.js 22.12 or a supported newer release, then run:

npm ci
npm test
npm run dev

To build and preview the static production site:

npm run build
npm run preview

The repository contains the viewer, compact evidence, reactor surfaces, exported flow paths and recorded tracer playback. Full OpenFOAM fields and the executable local agent are not included.


REFERENCES AND ACKNOWLEDGEMENTS

• Kimes, Moore and Maslar (2012): reactor geometry inspiration.
  https://doi.org/10.1063/1.4742991

• Burgess, NIST Technical Note 2279 (2024): gas diffusion reference.
  https://doi.org/10.6028/NIST.TN.2279

• OpenCFD OpenFOAM documentation and tutorials: modelling and numerical methods.
  https://www.openfoam.com/documentation/tutorial-guide

• ParaView documentation: visualisation and post-processing.
  https://docs.paraview.org/en/latest/

• ChatCFD and arXiv:2605.06607: agent-assisted CFD design ideas.
  https://doi.org/10.1002/aidi.202500174
  https://arxiv.org/abs/2605.06607

These sources informed the project; the demonstration does not reproduce their complete research systems. Additional source notes are provided in SOURCES.txt.

Created by Jubal Jacob with AI-assisted development.
