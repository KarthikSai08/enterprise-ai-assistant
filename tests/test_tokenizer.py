import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from sql_chatbot.retrieval.tokenizer import SQLTokenizer, _decompose_identifier


def test_simple_natural_language():
    t = SQLTokenizer()
    assert t.tokenize("show me booking status") == ["show", "booking", "status"]
    assert t.tokenize("how many bookings are pending") == ["many", "bookings", "pending"]
    assert t.tokenize("list all customers") == ["list", "customers"]


def test_snake_case():
    t = SQLTokenizer()
    assert t.tokenize("customer_id") == ["customer_id", "customer", "id"]
    assert t.tokenize("booking_status") == ["booking_status", "booking", "status"]
    assert t.tokenize("tbl_Booking") == ["tbl_booking", "tbl", "booking"]
    assert t.tokenize("dealer_org_id") == ["dealer_org_id", "dealer", "org", "id"]


def test_camel_case():
    t = SQLTokenizer()
    assert t.tokenize("getCustomerById") == ["getcustomerbyid", "get", "customer", "by", "id"]
    assert t.tokenize("dealerOrgId") == ["dealerorgid", "dealer", "org", "id"]
    assert t.tokenize("totalAmount") == ["totalamount", "total", "amount"]


def test_pascal_case():
    t = SQLTokenizer()
    assert t.tokenize("BookingStatus") == ["bookingstatus", "booking", "status"]
    assert t.tokenize("CustomerAccountID") == ["customeraccountid", "customer", "account", "id"]
    assert t.tokenize("CNFAgentID") == ["cnfagentid", "cnf", "agent", "id"]


def test_screaming_snake_case():
    t = SQLTokenizer()
    assert t.tokenize("SCREAMING_SNAKE_CASE") == [
        "screaming_snake_case", "screaming", "snake", "case"
    ]


def test_upper_sql_identifiers():
    t = SQLTokenizer()
    result = t.tokenize("TBL_BOOKING")
    assert "tbl_booking" in result
    assert "tbl" in result
    assert "booking" in result


def test_mixed_alphanumeric():
    t = SQLTokenizer()
    assert t.tokenize("invoice_2024") == ["invoice_2024", "invoice", "2024"]
    assert t.tokenize("addr2") == ["addr2", "addr", "2"]
    assert t.tokenize("2nd_place") == ["2nd_place", "2", "nd", "place"]


def test_punctuation():
    t = SQLTokenizer()
    assert t.tokenize("kebab-case") == ["kebab-case", "kebab", "case"]
    assert t.tokenize("dot.separated") == ["dot.separated", "dot", "separated"]
    assert t.tokenize("slash/separated") == ["slash/separated", "slash", "separated"]


def test_empty_string():
    t = SQLTokenizer()
    assert t.tokenize("") == []
    assert t.tokenize("   ") == []



def test_repeated_separators():
    t = SQLTokenizer()
    result = t.tokenize("tbl__Booking")
    assert "tbl__booking" in result
    assert "tbl" in result
    assert "booking" in result


def test_unicode():
    t = SQLTokenizer()
    result = t.tokenize("café cliente")
    assert result


def test_whole_identifiers_preserved():
    t = SQLTokenizer(keep_full_identifiers=True)
    assert "tbl_booking" in t.tokenize("tbl_Booking")
    assert "customer_id" in t.tokenize("customer_id")
    assert "getcustomerbyid" in t.tokenize("getCustomerById")

    t2 = SQLTokenizer(keep_full_identifiers=False)
    assert "tbl_booking" not in t2.tokenize("tbl_Booking")


def test_stopword_removal():
    t = SQLTokenizer(remove_stopwords=True)
    assert "the" not in t.tokenize("the booking")
    assert "of" not in t.tokenize("list of bookings")
    assert "for" not in t.tokenize("status for order")

    t2 = SQLTokenizer(remove_stopwords=False)
    assert "the" in t2.tokenize("the booking")
    assert "of" in t2.tokenize("list of bookings")


def test_sql_subtokens_not_removed():
    t = SQLTokenizer(remove_stopwords=True)
    assert "id" in t.tokenize("booking_id")
    assert "status" in t.tokenize("booking_status")
    assert "date" in t.tokenize("booking_date")
    assert "name" in t.tokenize("customer_name")
    assert "is" in t.tokenize("isConfirmed")
    assert "by" in t.tokenize("getCustomerById")


def test_decompose_identifier():
    assert _decompose_identifier("customer_id") == ["customer_id"]
    assert _decompose_identifier("getCustomerById") == ["get", "customer", "by", "id"]
    assert _decompose_identifier("CustomerAccountID") == ["customer", "account", "id"]
    assert _decompose_identifier("CNFAgentID") == ["cnf", "agent", "id"]
    assert _decompose_identifier("SCREAMING_SNAKE_CASE") == ["screaming_snake_case"]
    assert _decompose_identifier("") == []
    assert _decompose_identifier("plain") == ["plain"]
    assert _decompose_identifier("invoice2024") == ["invoice", "2024"]
    assert _decompose_identifier("2ndPlace") == ["2", "nd", "place"]


def test_sql_join_notation():
    t = SQLTokenizer()
    result = t.tokenize("tbl_Booking.productId = tbl_ProductMaster.idProduct")
    assert "tbl_booking.productid" in result
    assert "tbl_productmaster.idproduct" in result
    assert "product" in result
    assert "master" in result
    assert "booking" in result
    assert "tbl" in result


def test_schema_text():
    t = SQLTokenizer()
    text = (
        "Table: tbl_Booking Display: Bookings "
        "Description: Sales booking records capturing customer orders "
        "Column: totalAmount (totalAmount) - decimal - Total booking amount"
    )
    result = t.tokenize(text)
    assert "tbl_booking" in result
    assert "bookings" in result
    assert "booking" in result
    assert "totalamount" in result
    assert "total" in result
    assert "amount" in result
    assert "customer" in result


def test_decompose_case_only():
    assert _decompose_identifier("BookingStatus") == ["booking", "status"]
    assert _decompose_identifier("idBooking") == ["id", "booking"]


def test_query_with_numbers():
    t = SQLTokenizer()
    result = t.tokenize("show bookings from 2024")
    assert "bookings" in result
    assert "2024" in result


def test_non_english_unicode():
    t = SQLTokenizer()
    result = t.tokenize("über réservation")
    assert result


if __name__ == "__main__":
    test_simple_natural_language()
    test_snake_case()
    test_camel_case()
    test_pascal_case()
    test_screaming_snake_case()
    test_upper_sql_identifiers()
    test_mixed_alphanumeric()
    test_punctuation()
    test_empty_string()
    test_repeated_separators()
    test_unicode()
    test_whole_identifiers_preserved()
    test_stopword_removal()
    test_sql_subtokens_not_removed()
    test_decompose_identifier()
    test_sql_join_notation()
    test_schema_text()
    test_decompose_case_only()
    test_query_with_numbers()
    test_non_english_unicode()
    print("All tests passed!")
