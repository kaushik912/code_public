Yes — and this is a great real-world correction that actually makes the saga *cleaner*, not messier. What you're describing is the **intent pattern** (Stripe calls it `PaymentIntent`, PayPal has the Orders v2 "create order" with intent `AUTHORIZE`/`CAPTURE`), and it changes the state model in a way that's worth understanding because it interacts directly with everything we discussed.

## Why intent-first, order-last

The naive "create order → charge → reserve" flow has a nasty property: **you've persisted a real order before you know money is good.** In commerce, money is the least reversible, most fraud-sensitive, most regulated step. So real systems flip it:

```
1. Create ORDER_INTENT / PaymentIntent   (a lightweight, disposable placeholder — cart snapshot + amount)
2. Authorize / capture payment            (the hard, external, money step)
3. THEN create the real ORDER             (only once money is committed)
4. Reserve inventory, schedule shipping…
```

The order intent is **cheap to abandon**. Carts get abandoned constantly — if you created a full `Order` row + reserved inventory for every "Place Order" click that never paid, you'd have garbage orders and phantom stock holds everywhere. The intent is a throwaway; the **order is a commitment you only make after payment clears.**

## The subtlety that maps *perfectly* onto your saga: auth vs capture

Payment itself is often **two phases**, and this is where it connects to compensation:

- **Authorize** — put a hold on the funds (reversible, cheap to release).
- **Capture** — actually move the money (the real commit).

This gives you a beautiful cheap compensation window. The smart ordering is:

```
authorize payment      (hold — reversible)
  → create order
  → reserve inventory
  → capture payment     (the LAST, irreversible-ish step, once everything else succeeded)
```

Now if inventory fails, your compensation is **`void the authorization`** — which is far cheaper and cleaner than **`refund a capture`**. A refund is a whole separate money movement with fees, settlement delays, and a customer seeing charge-then-refund on their statement. Voiding an auth is invisible. **You defer the irreversible step as late as possible** so most failures compensate by "release the hold," not "refund."

This is a genuine saga design principle: **order your steps so the irreversible/expensive-to-compensate ones happen last.**

## What this does to the state machine

Your earlier `ORDER_CREATED → PAYMENT_CHARGED` becomes something like:

```
INTENT_CREATED
  → PAYMENT_AUTHORIZED        (hold placed)
  → ORDER_CREATED             (now safe to persist the real order)
  → INVENTORY_RESERVED
  → PAYMENT_CAPTURED          (money actually taken — last)
  → CONFIRMED

compensations (reverse, and note how cheap the early ones are):
  INVENTORY_RESERVED  → release stock
  ORDER_CREATED       → cancel order
  PAYMENT_AUTHORIZED  → VOID auth   (cheap! no refund needed if we never captured)
  PAYMENT_CAPTURED    → refund      (only if we'd already captured)
```

## And it ties back to idempotency

The intent is also the natural home for the **idempotency key**. Stripe/PayPal literally give you the `PaymentIntent id` / order id up front, and you pass it on the capture call so a retried "capture" can't double-charge. It's the *same* dedup key we used for the outbox/consumer — the intent id threads through as correlation id, idempotency key, and trace id all at once. Everything we built converges on that one identifier.

## The interview soundbite

> "In real commerce the order isn't the first step — you create a payment *intent*, authorize (hold) the funds, and only create the real order once money is secured, capturing at the very end. That's deliberate: you sequence the saga so the least-reversible step (capturing money) happens last, so most failures compensate by *voiding an authorization* rather than *refunding a capture*. The intent id doubles as the idempotency and correlation key."

That reframing — "order your saga steps by cost-of-compensation, defer the irreversible one" — is exactly the kind of domain-aware judgment that separates someone who's *read* about sagas from someone who's *built* payment flows.

Want to fold this authorize-then-capture model into the state-machine + outbox sketch so you have the payment-realistic version end to end?
