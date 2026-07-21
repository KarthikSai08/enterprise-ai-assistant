import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import logging
logging.disable(logging.CRITICAL)

from sql_chatbot.retrieval.tokenizer import SQLTokenizer
from sql_chatbot.metadata.loader import build

data = build()
texts = {name: t["text"] for name, t in data["tables"].items()}
column_texts = data.get("column_texts", {})


def evaluate_bm25(tokenizer, label):
    from rank_bm25 import BM25Okapi

    names = list(texts.keys())
    docs = [texts[n] for n in names]

    old_tokenized = [d.lower().split() for d in docs]
    new_tokenized = [tokenizer.tokenize(d) for d in docs]

    old_model = BM25Okapi(old_tokenized)
    new_model = BM25Okapi(new_tokenized)

    queries = [
        ("booking status", ["tbl_Booking"]),
        ("pending bookings", ["tbl_Booking"]),
        ("booking status dealer organization", ["tbl_Booking", "tbl_Organization"]),
        ("customer payment", ["tbl_Organization", "tbl_AccountLedger", "tbl_PaymentReceived"]),
        ("product master details", ["tbl_ProductMaster"]),
        ("sale invoice details", ["tbl_SaleInvoiceHeader", "tbl_SaleInvoiceDetail"]),
        ("employee department", ["tbl_Employee", "tbl_Department"]),
        ("inventory adjustment product", ["tbl_InventoryAdjustment", "tbl_ProductMaster"]),
        ("purchase order vendor", ["tbl_PurchaseOrder", "tbl_Organization"]),
        ("stock ledger warehouse", ["tbl_StockLedger", "tbl_Warehouse"]),
        ("total booking amount", ["tbl_Booking"]),
        ("leave application status employee", ["tbl_LeaveApplication", "tbl_Employee"]),
        ("quality checklist product", ["tbl_QualityChecklist", "tbl_ProductMaster"]),
        ("CNF Agent ID", ["tbl_Booking"]),
        ("route source city", ["tbl_RouteMaster"]),
        ("trip sheet driver", ["tbl_TripSheet", "tbl_DriverMaster"]),
        ("product grade category", ["tbl_ProductGrade", "tbl_ProductCategory"]),
        ("journal voucher ledger", ["tbl_JournalVoucher", "tbl_JournalVoucherDetail", "tbl_AccountLedger"]),
        ("credit debit note status", ["tbl_CreditDebitNote"]),
        ("loading detail invoice", ["tbl_LoadingDetail", "tbl_SaleInvoiceHeader"]),
    ]

    old_top1 = 0
    old_top3 = 0
    old_scores = []

    new_top1 = 0
    new_top3 = 0
    new_scores = []

    for query, expected_tables in queries:
        old_tok = query.lower().split()
        new_tok = tokenizer.tokenize(query)

        old_results = old_model.get_scores(old_tok)
        old_ranked = sorted(enumerate(old_results), key=lambda x: -x[1])
        old_top = [names[i] for i, s in old_ranked[:3] if s > 0]

        new_results = new_model.get_scores(new_tok)
        new_ranked = sorted(enumerate(new_results), key=lambda x: -x[1])
        new_top = [names[i] for i, s in new_ranked[:3] if s > 0]

        old_top1 += 1 if any(e == old_top[0] for e in expected_tables) else 0
        old_top3 += 1 if any(e in old_top for e in expected_tables) else 0

        new_top1 += 1 if any(e == new_top[0] for e in expected_tables) else 0
        new_top3 += 1 if any(e in new_top for e in expected_tables) else 0

        if len(old_results) > 0:
            old_scores.append(max(old_results))
        if len(new_results) > 0:
            new_scores.append(max(new_results))

    print(f"\n{'='*60}")
    print(f"  BM25 Benchmark: {label}")
    print(f"{'='*60}")
    print(f"  Tables indexed: {len(names)}")
    print(f"  Test queries:   {len(queries)}")
    print()
    print(f"  Old tokenizer (text.lower().split()):")
    print(f"    Top-1 accuracy:  {old_top1}/{len(queries)} ({100*old_top1/len(queries):.0f}%)")
    print(f"    Top-3 accuracy:  {old_top3}/{len(queries)} ({100*old_top3/len(queries):.0f}%)")
    print(f"    Avg max score:   {sum(old_scores)/len(old_scores):.4f}")
    print()
    print(f"  New tokenizer (SQLTokenizer):")
    print(f"    Top-1 accuracy:  {new_top1}/{len(queries)} ({100*new_top1/len(queries):.0f}%)")
    print(f"    Top-3 accuracy:  {new_top3}/{len(queries)} ({100*new_top3/len(queries):.0f}%)")
    print(f"    Avg max score:   {sum(new_scores)/len(new_scores):.4f}")
    print()

    old_doc_lens = [len(d.lower().split()) for d in docs]
    new_doc_lens = [len(tokenizer.tokenize(d)) for d in docs]
    print(f"  Document stats:")
    print(f"    Old avg tokens/doc:  {sum(old_doc_lens)/len(old_doc_lens):.1f}")
    print(f"    New avg tokens/doc:  {sum(new_doc_lens)/len(new_doc_lens):.1f}")
    print(f"    Old total terms:     {sum(old_doc_lens)}")
    print(f"    New total terms:     {sum(new_doc_lens)}")


if __name__ == "__main__":
    tok = SQLTokenizer(remove_stopwords=True, keep_full_identifiers=True)
    evaluate_bm25(tok, "SQLTokenizer (stopwords ON)")

    tok_ns = SQLTokenizer(remove_stopwords=False, keep_full_identifiers=True)
    evaluate_bm25(tok_ns, "SQLTokenizer (stopwords OFF)")
