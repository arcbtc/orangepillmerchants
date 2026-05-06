# orangepillmerchants

`orangepillmerchants` is a superuser-only [LNbits](https://github.com/lnbits/lnbits) extension for onboarding merchants with a temporary repayment flow.

## What It Does

The extension is designed for a simple real-world onboarding pattern:

1. A superuser gives a merchant some cash in fiat, for example `GBP 50`.
2. The superuser enters the merchant's name, email address, fiat amount, and the superuser wallet that should receive repayments.
3. The extension creates a new LNbits user for the merchant.
4. The extension enables `tpos` for that new user and creates a merchant-owned TPoS.
5. The merchant receives an email containing only the public TPoS page link.
6. Each paid TPoS sale is internally forwarded to the selected superuser wallet while the onboarding amount is still being repaid.
7. Once the merchant has repaid the configured onboarding amount, the forwarding stops.
8. The merchant then receives a second email with their LNbits login link and user ID so they can access their account and set a password.

After the onboarding amount has been fully repaid, any further funds received through that TPoS stay with the merchant.

## Permissions

This extension is intended to be `super_user_only`.

All extension API endpoints are restricted to the LNbits superuser.

## Email Flow

The extension sends two emails by using the LNbits core email notification utility:

- Initial email: sends only the merchant's public TPoS page link.
- Completion email: sends the merchant's LNbits login link and user ID, with instructions to set a password after logging in.

For email delivery to work, LNbits email notifications must already be configured at the core application level.

## How Repayment Works

Repayment is tracked against the configured fiat onboarding amount.

- The merchant takes payments through their TPoS.
- When a TPoS invoice is paid, the extension listens for that payment event.
- If the merchant is still in the onboarding period, the extension creates an internal payout to the configured superuser wallet.
- The extension records the sale and keeps a running total of the repaid onboarding amount.
- When the running total reaches or exceeds the configured onboarding amount, the merchant is marked as completed and the second email is sent.

## Admin UI

The extension admin page allows the superuser to:

- create a merchant onboarding record
- choose the recoup wallet
- review merchant repayment progress
- resend the relevant merchant email
- delete the onboarding record

Deleting an onboarding record removes the extension's own recordkeeping, but does not delete the created LNbits user or their TPoS.

## Main Data Stored

The extension stores:

- merchant onboarding records
- the LNbits merchant user and wallet references
- the selected superuser source wallet reference
- the generated `tpos` id
- repayment progress
- a ledger of processed merchant sale payments

## Development Notes

This extension was originally scaffolded from the LNbits Extension Builder, but it has been reworked into a purpose-built onboarding flow.
