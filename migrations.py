empty_dict: dict[str, str] = {}


async def m001_initial_schema(db):
    await db.execute(
        f"""
        CREATE TABLE orangepillmerchant.merchants (
            id TEXT PRIMARY KEY,
            owner_id TEXT NOT NULL,
            merchant_user_id TEXT NOT NULL UNIQUE,
            merchant_wallet_id TEXT NOT NULL UNIQUE,
            source_wallet_id TEXT NOT NULL,
            tpos_id TEXT NOT NULL UNIQUE,
            base_url TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            currency TEXT NOT NULL,
            onboarding_amount REAL NOT NULL,
            repaid_amount REAL NOT NULL DEFAULT 0,
            onboarding_completed BOOLEAN NOT NULL DEFAULT FALSE,
            initial_email_sent_at TIMESTAMP,
            login_email_sent_at TIMESTAMP,
            completed_at TIMESTAMP,
            created_at TIMESTAMP NOT NULL DEFAULT {db.timestamp_now},
            updated_at TIMESTAMP NOT NULL DEFAULT {db.timestamp_now}
        );
    """
    )
    await db.execute(
        f"""
        CREATE TABLE orangepillmerchant.merchant_payments (
            id TEXT PRIMARY KEY,
            merchant_id TEXT NOT NULL,
            payment_hash TEXT NOT NULL UNIQUE,
            sale_amount REAL NOT NULL,
            payout_amount_sat INT NOT NULL,
            payout_payment_hash TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT {db.timestamp_now},
            updated_at TIMESTAMP NOT NULL DEFAULT {db.timestamp_now}
        );
    """
    )


async def m002_ensure_schema(db):
    await db.execute(
        f"""
        CREATE TABLE IF NOT EXISTS orangepillmerchant.merchants (
            id TEXT PRIMARY KEY,
            owner_id TEXT NOT NULL,
            merchant_user_id TEXT NOT NULL UNIQUE,
            merchant_wallet_id TEXT NOT NULL UNIQUE,
            source_wallet_id TEXT NOT NULL,
            tpos_id TEXT NOT NULL UNIQUE,
            base_url TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            currency TEXT NOT NULL,
            onboarding_amount REAL NOT NULL,
            repaid_amount REAL NOT NULL DEFAULT 0,
            onboarding_completed BOOLEAN NOT NULL DEFAULT FALSE,
            initial_email_sent_at TIMESTAMP,
            login_email_sent_at TIMESTAMP,
            completed_at TIMESTAMP,
            created_at TIMESTAMP NOT NULL DEFAULT {db.timestamp_now},
            updated_at TIMESTAMP NOT NULL DEFAULT {db.timestamp_now}
        );
    """
    )
    await db.execute(
        f"""
        CREATE TABLE IF NOT EXISTS orangepillmerchant.merchant_payments (
            id TEXT PRIMARY KEY,
            merchant_id TEXT NOT NULL,
            payment_hash TEXT NOT NULL UNIQUE,
            sale_amount REAL NOT NULL,
            payout_amount_sat INT NOT NULL,
            payout_payment_hash TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT {db.timestamp_now},
            updated_at TIMESTAMP NOT NULL DEFAULT {db.timestamp_now}
        );
    """
    )


async def m003_ensure_schema_again(db):
    await m002_ensure_schema(db)
