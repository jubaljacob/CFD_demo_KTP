import React,{useState} from 'react';

export default function EvidenceAssistant({run,target}) {
 const [question,setQuestion]=useState('Does tracer-fine-corrected meet a 35-second target for 90% arrival at all nine sampled positions? Explain the evidence and limitations.');
 return <section className="reactor-agent" aria-label="Evidence assistant">
  <div className="reactor-agent-heading"><h2>Evidence assistant</h2><span>GPT-6 Sol</span></div>
  <p className="inactive-notice"><b>Inactive in this public demo.</b> The original interaction layout is shown below. Live questions, saved private investigations and experiment execution are available only in the local application.</p>
  <p className="reactor-note">Investigate results or propose a controlled experiment. You can draft a question here; it stays in this browser and is not sent to an AI service.</p>
  <form onSubmit={e=>e.preventDefault()}>
   <label htmlFor="question">Your engineering question</label>
   <textarea id="question" value={question} maxLength={6000} onChange={e=>setQuestion(e.target.value)} rows={5}/>
   <div className="reactor-controls"><button type="button" onClick={()=>setQuestion(`Does ${run.name} meet a ${target || '35'}-second target for 90% arrival at all nine sampled positions? Explain the evidence and limitations.`)}>Use selected case &amp; target</button><button className="reactor-primary" type="submit" disabled title="The AI agent is inactive on this static public site">Ask agent</button><span className="inactive-label">Inactive</span></div>
  </form>
  <p className="reactor-note">Local capabilities: analysis and planning · up to 4 tool calls · execution requires approval of a displayed plan.</p>
  <label className="reactor-saved">Saved investigations<select aria-label="Saved investigations" disabled defaultValue=""><option value="">Select a recorded answer…</option></select></label>
  <p className="reactor-note">Private investigation history is not published.</p>
  <section className="reactor-experiments" aria-label="Experiment workspace"><h3>Experiment workspace</h3><p className="reactor-note">In the local application, review a plan and then start its fixed recipe. New results and logs stay separate from the reference cases.</p>
   <fieldset disabled className="reactor-experiment-fields"><legend>Planning controls · inactive</legend><label>Study recipe<select defaultValue="fifth_inlet"><option value="startup_comparison">Short tracer startup comparison</option><option value="fifth_inlet">Fifth inlet: geometry and mesh stage</option></select></label><label>Gas supply basis<select defaultValue="same_per_inlet"><option value="unspecified">Choose what stays fixed…</option><option value="same_total">300 sccm total · 60 per inlet</option><option value="same_per_inlet">75 sccm per inlet · 375 total</option></select></label><label>All nine positions reach 90% by (seconds)<input type="number" defaultValue="35"/></label><label>Maximum arrival spread (seconds)<input type="number" placeholder="Optional target"/></label><label>How to rank successful designs<select defaultValue="least_gas_meeting_targets"><option value="fastest_at_fixed_supply">Fastest arrival at fixed gas supply</option><option value="least_gas_meeting_targets">Least gas used while meeting targets</option></select></label><button type="button">Prepare reviewable plan</button></fieldset>
  </section>
 </section>;
}
