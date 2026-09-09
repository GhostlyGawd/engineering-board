import { useState } from "react";

export function AccountRecovery() {
  const [step, setStep] = useState(1);
  const [method, setMethod] = useState("email");
  const next = () => setStep(value => Math.min(5, value + 1));
  return <main className="recovery" data-step={step}>
    <h1>Recover your Lantern account</h1>
    {step === 1 && <section><aside className="promotion"><button>See member benefits</button></aside><label htmlFor="recover-email">Email</label><input id="recover-email" type="email" defaultValue="mina@example.test"/><a className="quiet-recovery" href="#start" onClick={next}>I can’t sign in</a></section>}
    {step === 2 && <section><h2>Choose a recovery method</h2><button className={`method ${method === "email" ? "chosen" : ""}`} onClick={() => setMethod("email")}>Email m•••@example.test</button><button className={`method sms ${method === "sms" ? "chosen" : ""}`} onClick={() => setMethod("sms")}>SMS ending 0142</button><button onClick={next}>Continue</button></section>}
    {step === 3 && <section><h2>Enter the six-digit code</h2><div className="code-cells">{[0,1,2,3,4,5].map(i => <input key={i} aria-label={`Digit ${i+1}`} inputMode="numeric" maxLength={1}/>)}</div><p role="alert">Something went wrong.</p><button onClick={() => undefined}>Resend</button><button onClick={next}>Continue</button></section>}
    {step === 4 && <section className="password-panel"><h2>Reset password</h2><p className="faint">Use at least 12 characters.</p><label>New password<input type="password"/></label><button className="icon-button">◉</button><label>Confirm password<input type="password"/></label><button className="icon-button">◉</button><button onClick={next}>Save password</button></section>}
    {step === 5 && <section><span aria-hidden="true">◒</span><h2>Recovery complete</h2><a href="/missing">Continue</a><button onClick={() => setStep(1)}>Start over</button></section>}
  </main>;
}
