import os
import random
from decimal import Decimal, ROUND_HALF_UP
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
from django.db import transaction
from django.conf import settings
from finance.models import (
    Payment,
    GatewayTransaction,
    BankTransaction,
    GroundTruthRecord,
    ReconciliationResult,
    ExceptionRecord,
    AuditLog,
    ReconciliationJob,
)


class SyntheticDatasetGenerator:
    """
    Generates deterministic, production-grade financial records across:
    1. Internal Customer Payments Ledger
    2. Payment Gateway Captured Transactions
    3. Bank Statement Credit Entries
    4. Immutable Ground Truth Validation Table
    """

    COMPANIES = [
        "Tata Consultancy Services", "Reliance Retail Ltd", "Infosys Technologies",
        "HDFC Life Insurance", "Zomato Media Pvt Ltd", "Swiggy Bundl Technologies",
        "Flipkart Internet Pvt Ltd", "Paytm One97 Comm", "Zerodha Broking Ltd",
        "Wipro Enterprises", "Mahindra & Mahindra", "Bharti Airtel Ltd",
        "Larsen & Toubro Ltd", "Apollo Hospitals Ent", "Titan Company Ltd",
        "Nykaa FSN E-Commerce", "Ola ANI Technologies", "Delhivery Logistics",
        "MakeMyTrip India", "Urban Company Technologies"
    ]

    NAME_VARIATIONS = {
        "Tata Consultancy Services": ["TCS Ltd", "Tata Sons - TCS Div", "T.C.S. IND"],
        "Reliance Retail Ltd": ["Reliance Ind - Retail", "R-Retail Ventures", "RELIANCE RETAIL"],
        "Infosys Technologies": ["Infosys Ltd", "INFOSYS TECH", "Infy Software Div"],
        "Zomato Media Pvt Ltd": ["Zomato Ltd", "ZOMATO HYPERPURE", "Zomato Online"],
        "Swiggy Bundl Technologies": ["Bundl Tech Swiggy", "SWIGGY BANGALORE", "Swiggy Delivery"],
        "Flipkart Internet Pvt Ltd": ["Flipkart India", "FLIPKART PAYMENTS", "FK Internet"],
        "Zerodha Broking Ltd": ["Zerodha Securities", "ZERODHA BROKING", "Zerodha Trading"],
    }

    GATEWAYS = ["RAZORPAY", "STRIPE_IN", "PAYU", "CASHFREE"]
    BANKS = ["HDFC Bank", "ICICI Bank", "State Bank of India", "Axis Bank", "Kotak Mahindra Bank"]

    def __init__(self, record_count: int = 150, seed: int = 42, export_csv: bool = True):
        self.record_count = record_count
        self.seed = seed
        self.export_csv = export_csv
        random.seed(self.seed)
        self.base_date = date(2026, 8, 1)

    def _calculate_proportions(self) -> Dict[str, int]:
        """Calculates exact record distribution scaling proportionally to record_count."""
        n = self.record_count
        if n == 150:
            return {
                "EXACT_MATCH": 80,
                "ENTITY_VARIATION": 20,
                "DELAYED_SETTLEMENT": 10,
                "AMOUNT_MISMATCH_FEE": 10,
                "DUPLICATE_SETTLEMENT": 10,
                "MISSING_BANK": 10,
                "MISSING_GATEWAY": 5,
                "UNEXPLAINED_DIFF": 5,
            }
        
        # Scaling ratios for other batch sizes (50, 100, 500)
        exact = int(n * 0.53)
        entity = int(n * 0.13)
        delayed = int(n * 0.07)
        fee_mismatch = int(n * 0.07)
        duplicate = int(n * 0.07)
        missing_bank = int(n * 0.065)
        missing_gw = int(n * 0.033)
        unexplained = n - (exact + entity + delayed + fee_mismatch + duplicate + missing_bank + missing_gw)

        return {
            "EXACT_MATCH": exact,
            "ENTITY_VARIATION": entity,
            "DELAYED_SETTLEMENT": delayed,
            "AMOUNT_MISMATCH_FEE": fee_mismatch,
            "DUPLICATE_SETTLEMENT": duplicate,
            "MISSING_BANK": missing_bank,
            "MISSING_GATEWAY": missing_gw,
            "UNEXPLAINED_DIFF": unexplained,
        }

    @transaction.atomic
    def generate(self) -> Dict[str, Any]:
        """Generates all datasets, clears existing records, and writes to database & CSV."""
        # 1. Purge existing tables cleanly
        AuditLog.objects.all().delete()
        ExceptionRecord.objects.all().delete()
        ReconciliationResult.objects.all().delete()
        BankTransaction.objects.all().delete()
        GatewayTransaction.objects.all().delete()
        Payment.objects.all().delete()
        GroundTruthRecord.objects.all().delete()

        proportions = self._calculate_proportions()
        
        payments_to_create: List[Payment] = []
        gateway_to_create: List[GatewayTransaction] = []
        bank_to_create: List[BankTransaction] = []
        ground_truth_to_create: List[GroundTruthRecord] = []

        running_idx = 1

        for scenario, count in proportions.items():
            for _ in range(count):
                pid = f"P{running_idx:04d}"
                raw_company = random.choice(self.COMPANIES)
                base_amount = Decimal(random.randint(50, 1500) * 100)  # Clean thousands e.g. 5,000 - 150,000
                pay_date = self.base_date + timedelta(days=random.randint(0, 15))
                gateway_name = random.choice(self.GATEWAYS)
                bank_name = random.choice(self.BANKS)

                # Standard 2% gateway fee + 18% GST on fee
                gw_fee = (base_amount * Decimal("0.02")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                tax_fee = (gw_fee * Decimal("0.18")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                net_expected = base_amount - (gw_fee + tax_fee)

                # Base Payment Model
                payment = Payment(
                    payment_id=pid,
                    customer_name=raw_company,
                    amount=base_amount,
                    currency="INR",
                    payment_date=pay_date,
                    gateway=gateway_name,
                )
                payments_to_create.append(payment)

                # Scenario Handling
                if scenario == "EXACT_MATCH":
                    # 1:1 Clean Match
                    gw_tx = GatewayTransaction(
                        gateway_transaction_id=f"GTW_{pid}",
                        payment=payment,
                        amount=base_amount,
                        gateway_fee=gw_fee,
                        tax_on_fee=tax_fee,
                        settlement_date=pay_date + timedelta(days=1),
                        status="CAPTURED",
                    )
                    gateway_to_create.append(gw_tx)

                    bank_tx = BankTransaction(
                        bank_transaction_id=f"BTX_{pid}",
                        reference=f"{gateway_name}_SETTLE_{pid}",
                        amount=net_expected,
                        transaction_date=pay_date + timedelta(days=1),
                        description=f"Settlement for {pid} / {raw_company}",
                        bank_name=bank_name,
                    )
                    bank_to_create.append(bank_tx)

                    ground_truth_to_create.append(GroundTruthRecord(
                        payment_id=pid,
                        customer_name=raw_company,
                        scenario_type=scenario,
                        expected_status="MATCHED",
                        expected_confidence=0.99,
                        expected_difference=Decimal("0.00"),
                        expected_reason="Deterministic 1:1 match across Payment, Gateway, and Bank credit.",
                        is_resolvable=True,
                    ))

                elif scenario == "ENTITY_VARIATION":
                    # Customer name variation in bank reference
                    aliases = self.NAME_VARIATIONS.get(raw_company, [f"{raw_company} India", f"{raw_company} ENT"])
                    alias_name = random.choice(aliases)

                    gw_tx = GatewayTransaction(
                        gateway_transaction_id=f"GTW_{pid}",
                        payment=payment,
                        amount=base_amount,
                        gateway_fee=gw_fee,
                        tax_on_fee=tax_fee,
                        settlement_date=pay_date + timedelta(days=1),
                        status="CAPTURED",
                    )
                    gateway_to_create.append(gw_tx)

                    bank_tx = BankTransaction(
                        bank_transaction_id=f"BTX_{pid}",
                        reference=f"{gateway_name}_PAY_{pid}",
                        amount=net_expected,
                        transaction_date=pay_date + timedelta(days=1),
                        description=f"Direct Credit from {alias_name}",
                        bank_name=bank_name,
                    )
                    bank_to_create.append(bank_tx)

                    ground_truth_to_create.append(GroundTruthRecord(
                        payment_id=pid,
                        customer_name=raw_company,
                        scenario_type=scenario,
                        expected_status="RESOLVED",
                        expected_confidence=0.96,
                        expected_difference=Decimal("0.00"),
                        expected_reason=f"Entity variation '{alias_name}' mapped to '{raw_company}'. Amount matched.",
                        is_resolvable=True,
                    ))

                elif scenario == "DELAYED_SETTLEMENT":
                    # Settled after 7 days (T+7 instead of T+1)
                    gw_tx = GatewayTransaction(
                        gateway_transaction_id=f"GTW_{pid}",
                        payment=payment,
                        amount=base_amount,
                        gateway_fee=gw_fee,
                        tax_on_fee=tax_fee,
                        settlement_date=pay_date + timedelta(days=7),
                        status="CAPTURED",
                    )
                    gateway_to_create.append(gw_tx)

                    bank_tx = BankTransaction(
                        bank_transaction_id=f"BTX_{pid}",
                        reference=f"{gateway_name}_DELAYED_{pid}",
                        amount=net_expected,
                        transaction_date=pay_date + timedelta(days=7),
                        description=f"Delayed Settlement for {pid} due to weekend/bank holiday",
                        bank_name=bank_name,
                    )
                    bank_to_create.append(bank_tx)

                    ground_truth_to_create.append(GroundTruthRecord(
                        payment_id=pid,
                        customer_name=raw_company,
                        scenario_type=scenario,
                        expected_status="MATCHED_DELAYED",
                        expected_confidence=0.98,
                        expected_difference=Decimal("0.00"),
                        expected_reason="Settlement confirmed with acceptable 7-day gateway hold delay.",
                        is_resolvable=True,
                    ))

                elif scenario == "AMOUNT_MISMATCH_FEE":
                    # Gateway deducted an extra fixed ₹500 chargeback dispute/interchange fee
                    extra_charge = Decimal("500.00")
                    actual_settled = net_expected - extra_charge

                    gw_tx = GatewayTransaction(
                        gateway_transaction_id=f"GTW_{pid}",
                        payment=payment,
                        amount=base_amount,
                        gateway_fee=gw_fee + extra_charge,
                        tax_on_fee=tax_fee,
                        settlement_date=pay_date + timedelta(days=1),
                        status="CAPTURED",
                    )
                    gateway_to_create.append(gw_tx)

                    bank_tx = BankTransaction(
                        bank_transaction_id=f"BTX_{pid}",
                        reference=f"{gateway_name}_NET_{pid}",
                        amount=actual_settled,
                        transaction_date=pay_date + timedelta(days=1),
                        description=f"Settlement with ₹500 dispute resolution fee adjustment",
                        bank_name=bank_name,
                    )
                    bank_to_create.append(bank_tx)

                    ground_truth_to_create.append(GroundTruthRecord(
                        payment_id=pid,
                        customer_name=raw_company,
                        scenario_type=scenario,
                        expected_status="RESOLVED",
                        expected_confidence=0.97,
                        expected_difference=extra_charge,
                        expected_reason="Discrepancy explained by audited ₹500 gateway dispute handling surcharge.",
                        is_resolvable=True,
                    ))

                elif scenario == "DUPLICATE_SETTLEMENT":
                    # Bank statement contains two identical credits for the same transaction
                    gw_tx = GatewayTransaction(
                        gateway_transaction_id=f"GTW_{pid}",
                        payment=payment,
                        amount=base_amount,
                        gateway_fee=gw_fee,
                        tax_on_fee=tax_fee,
                        settlement_date=pay_date + timedelta(days=1),
                        status="CAPTURED",
                    )
                    gateway_to_create.append(gw_tx)

                    bank_tx_1 = BankTransaction(
                        bank_transaction_id=f"BTX_{pid}_A",
                        reference=f"{gateway_name}_DUP_{pid}",
                        amount=net_expected,
                        transaction_date=pay_date + timedelta(days=1),
                        description=f"First credit settlement for {pid}",
                        bank_name=bank_name,
                    )
                    bank_tx_2 = BankTransaction(
                        bank_transaction_id=f"BTX_{pid}_B",
                        reference=f"{gateway_name}_DUP_{pid}",
                        amount=net_expected,
                        transaction_date=pay_date + timedelta(days=1),
                        description=f"Duplicate second credit for {pid}",
                        bank_name=bank_name,
                    )
                    bank_to_create.extend([bank_tx_1, bank_tx_2])

                    ground_truth_to_create.append(GroundTruthRecord(
                        payment_id=pid,
                        customer_name=raw_company,
                        scenario_type=scenario,
                        expected_status="EXCEPTION",
                        expected_confidence=0.99,
                        expected_difference=net_expected,
                        expected_reason="Duplicate bank credit transaction detected for identical settlement reference.",
                        is_resolvable=False,
                    ))

                elif scenario == "MISSING_BANK":
                    # Payment captured on Gateway, but no funds reached Bank
                    gw_tx = GatewayTransaction(
                        gateway_transaction_id=f"GTW_{pid}",
                        payment=payment,
                        amount=base_amount,
                        gateway_fee=gw_fee,
                        tax_on_fee=tax_fee,
                        settlement_date=pay_date + timedelta(days=1),
                        status="CAPTURED",
                    )
                    gateway_to_create.append(gw_tx)

                    ground_truth_to_create.append(GroundTruthRecord(
                        payment_id=pid,
                        customer_name=raw_company,
                        scenario_type=scenario,
                        expected_status="UNRESOLVED",
                        expected_confidence=0.96,
                        expected_difference=net_expected,
                        expected_reason="Payment captured on Gateway but missing in Bank Statement. Manual escalation required.",
                        is_resolvable=False,
                    ))

                elif scenario == "MISSING_GATEWAY":
                    # Payment logged in DB, but dropped before Gateway capture
                    ground_truth_to_create.append(GroundTruthRecord(
                        payment_id=pid,
                        customer_name=raw_company,
                        scenario_type=scenario,
                        expected_status="UNRESOLVED",
                        expected_confidence=0.98,
                        expected_difference=base_amount,
                        expected_reason="Payment record initiated but no corresponding Gateway capture record exists.",
                        is_resolvable=False,
                    ))

                elif scenario == "UNEXPLAINED_DIFF":
                    # Random unresolved difference (e.g. ₹312.45 missing with no explanation)
                    mystery_diff = Decimal("312.45")
                    actual_settled = net_expected - mystery_diff

                    gw_tx = GatewayTransaction(
                        gateway_transaction_id=f"GTW_{pid}",
                        payment=payment,
                        amount=base_amount,
                        gateway_fee=gw_fee,
                        tax_on_fee=tax_fee,
                        settlement_date=pay_date + timedelta(days=1),
                        status="CAPTURED",
                    )
                    gateway_to_create.append(gw_tx)

                    bank_tx = BankTransaction(
                        bank_transaction_id=f"BTX_{pid}",
                        reference=f"{gateway_name}_MYST_{pid}",
                        amount=actual_settled,
                        transaction_date=pay_date + timedelta(days=1),
                        description=f"Settlement credit with unexplained gap",
                        bank_name=bank_name,
                    )
                    bank_to_create.append(bank_tx)

                    ground_truth_to_create.append(GroundTruthRecord(
                        payment_id=pid,
                        customer_name=raw_company,
                        scenario_type=scenario,
                        expected_status="UNRESOLVED",
                        expected_confidence=0.92,
                        expected_difference=mystery_diff,
                        expected_reason=f"Unexplained variance of ₹{mystery_diff}. No matching fee schedule or deduction record.",
                        is_resolvable=False,
                    ))

                running_idx += 1

        # Bulk Create Records in Transaction
        Payment.objects.bulk_create(payments_to_create)
        GatewayTransaction.objects.bulk_create(gateway_to_create)
        BankTransaction.objects.bulk_create(bank_to_create)
        GroundTruthRecord.objects.bulk_create(ground_truth_to_create)

        # Export CSVs if required
        if self.export_csv:
            self._export_to_csv()

        return {
            "total_records": len(payments_to_create),
            "distribution": proportions,
            "payments_count": Payment.objects.count(),
            "gateway_count": GatewayTransaction.objects.count(),
            "bank_count": BankTransaction.objects.count(),
            "ground_truth_count": GroundTruthRecord.objects.count(),
        }

    def _export_to_csv(self):
        """Exports data to CSV files in the data/ directory."""
        data_dir = Path(settings.BASE_DIR).parent / "data"
        os.makedirs(data_dir, exist_ok=True)

        payments_df = pd.DataFrame(list(Payment.objects.all().values()))
        gateway_df = pd.DataFrame(list(GatewayTransaction.objects.all().values()))
        bank_df = pd.DataFrame(list(BankTransaction.objects.all().values()))
        gt_df = pd.DataFrame(list(GroundTruthRecord.objects.all().values()))

        payments_df.to_csv(data_dir / "payments.csv", index=False)
        gateway_df.to_csv(data_dir / "gateway_transactions.csv", index=False)
        bank_df.to_csv(data_dir / "bank_transactions.csv", index=False)
        gt_df.to_csv(data_dir / "ground_truth.csv", index=False)