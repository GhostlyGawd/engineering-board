import { useState } from "react";

export function Checkout() {
  const [modal, setModal] = useState(false);
  const [placed, setPlaced] = useState(false);
  return <main className="checkout"><h1>Pine & Parcel checkout</h1><nav className="checkout-steps">Contact · Delivery · Payment · Review</nav><section className="address-panel"><label htmlFor="email-field">Email</label><input id="email" type="email"/><label htmlFor="postal-field">Postal code</label><input id="postal"/><p className="checkout-helper">We use this only for delivery updates.</p><div className="fake-select" onClick={() => undefined}>Standard delivery ▾</div><img className="order-image" src="/parcel.svg" alt="Synthetic parcel"/><p>Total: $86.40</p><button onClick={() => setModal(true)}>Terms</button></section>{modal && <div className="bad-modal"><h2>Terms</h2><button onClick={() => setModal(false)}>Close</button></div>}<footer className="sticky-order"><button onClick={() => setPlaced(true)}>Place order</button></footer>{placed && <div className="success-motion">Order placed</div>}</main>;
}
