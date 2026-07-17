"""Generate comprehensive, query-optimized metadata for all 68 tables."""
import json
import yaml
from pathlib import Path
 
TABLE_META = {
    "dim_OrgType": {
        "display_name": "Organization Types",
        "domain": "Reference",
        "module": "Master Data",
        "description": "Reference table storing organization type classifications such as Dealer, Distributor, Vendor, CNF, Transporter, etc. Used to categorize business partners across sales, purchase, and logistics modules.",
        "search_weight": 4, "priority": "Low",
        "search_keywords": [
            "org type", "organization type", "party type", "partner type",
            "dealer type", "vendor type", "distributor type",
            "type master", "business partner type", "entity type",
            "org category", "organization category", "party category"
        ],
        "common_user_intents": [
            "What types of organizations exist",
            "List all organization types",
            "Show org type codes",
            "Types of business partners",
            "What are the different dealer types",
            "Organization type list with codes"
        ],
        "important_columns": ["orgTypeCode", "orgTypeName", "description"],
        "business_metrics": [],
        "common_filters": ["isActive"],
        "common_groupby": [],
    },
    "dim_PaymentTerm": {
        "display_name": "Payment Terms",
        "domain": "Finance",
        "module": "Master Data",
        "description": "Reference table for payment terms defining due days for invoices. Examples: Net 30, Net 60, Immediate, Credit 90. Used across sales invoicing, purchase invoicing, and accounts receivable/payable.",
        "search_weight": 5, "priority": "Medium",
        "search_keywords": [
            "payment term", "payment terms", "pay terms", "credit terms",
            "due days", "net days", "payment due", "payment condition",
            "invoice due", "credit period", "payment mode",
            "terms of payment", "payment schedule"
        ],
        "common_user_intents": [
            "What payment terms do we offer",
            "Show all payment terms with due days",
            "Payment terms available",
            "List credit terms",
            "Which payment terms have 30 days due",
            "Payment terms master data"
        ],
        "important_columns": ["termCode", "termName", "dueDays"],
        "business_metrics": ["dueDays"],
        "common_filters": ["isActive"],
        "common_groupby": [],
    },
    "dim_Status": {
        "display_name": "Status Master",
        "domain": "Reference",
        "module": "Master Data",
        "description": "Universal status reference table used across orders, invoices, deliveries, and approvals. Each status has a category (e.g., Order, Invoice, Delivery) and a code/name pair.",
        "search_weight": 6, "priority": "Medium",
        "search_keywords": [
            "status", "order status", "invoice status", "delivery status",
            "status code", "status name", "status master",
            "approval status", "payment status", "fulfillment status",
            "status category", "status list"
        ],
        "common_user_intents": [
            "What statuses are available",
            "Show all order statuses",
            "List invoice statuses",
            "Status codes and names",
            "What are the delivery statuses",
            "Status categories"
        ],
        "important_columns": ["statusCategory", "statusCode", "statusName"],
        "business_metrics": [],
        "common_filters": ["isActive"],
        "common_groupby": ["statusCategory"],
    },
    "dim_TaxRate": {
        "display_name": "Tax Rates",
        "domain": "Finance",
        "module": "Tax Management",
        "description": "Reference table for GST tax rates including SGST, CGST, IGST percentages. Used in invoicing, purchase orders, and tax calculations across all financial transactions.",
        "search_weight": 5, "priority": "Medium",
        "search_keywords": [
            "tax rate", "tax rates", "gst rate", "gst rates",
            "sgst", "cgst", "igst", "tax percentage", "tax slab",
            "tax master", "tax code", "tax name",
            "goods and services tax", "tax category"
        ],
        "common_user_intents": [
            "What tax rates are available",
            "Show GST rates",
            "List all tax percentages",
            "Tax rates master",
            "What is the 18% GST rate",
            "SGST CGST rates"
        ],
        "important_columns": ["taxCode", "taxName", "sgstRate", "cgstRate", "igstRate"],
        "business_metrics": ["sgstRate", "cgstRate", "igstRate"],
        "common_filters": ["isActive"],
        "common_groupby": [],
    },
    "dim_UOM": {
        "display_name": "Units of Measurement",
        "domain": "Reference",
        "module": "Master Data",
        "description": "Reference table for units of measurement (KG, MT, Litre, Piece, Box, etc.) used in product definitions, purchase orders, and sales invoices for quantity tracking.",
        "search_weight": 4, "priority": "Medium",
        "search_keywords": [
            "uom", "unit", "units", "unit of measurement",
            "measurement unit", "quantity unit", "weight unit",
            "kilogram", "litre", "piece", "box", "metric ton",
            "uom master", "unit master", "uom list"
        ],
        "common_user_intents": [
            "What units of measurement do we use",
            "Show all UOMs",
            "List measurement units",
            "UOM master data",
            "What UOM codes are available",
            "Units for weight and volume"
        ],
        "important_columns": ["uomCode", "uomName"],
        "business_metrics": [],
        "common_filters": ["isActive"],
        "common_groupby": [],
    },
    "dmn_City": {
        "display_name": "Cities",
        "domain": "Geography",
        "module": "Geography Master",
        "description": "City master table linked to states and countries. Used for organization addresses, warehouse locations, and delivery destinations.",
        "search_weight": 4, "priority": "Medium",
        "search_keywords": [
            "city", "cities", "town", "district", "location",
            "city master", "city list", "city name", "pin code",
            "postal code", "city code", "place", "area",
            "municipality", "metro", "urban", "rural", "locality",
            "city details", "city information", "address city",
            "pincode", "pin", "zip code", "zip"
        ],
        "common_user_intents": [
            "List all cities",
            "Show cities in a state",
            "Which city has pin code X",
            "City master data",
            "All cities in Maharashtra",
            "Cities by country",
            "City wise customers",
            "Delivery cities",
            "City directory"
        ],
        "important_columns": ["cityName", "stateId", "pinCode"],
        "business_metrics": [],
        "common_filters": ["isActive", "stateId"],
        "common_groupby": ["stateId"],
    },
    "dmn_Country": {
        "display_name": "Countries",
        "domain": "Geography",
        "module": "Geography Master",
        "description": "Country reference table. Top level of the geography hierarchy (Country > State > City). Used for address standardization and international trade.",
        "search_weight": 3, "priority": "Low",
        "search_keywords": [
            "country", "countries", "nation", "country master",
            "country list", "country code", "country name",
            "international", "foreign", "domestic", "global",
            "worldwide", "country details", "national",
            "iso country", "country lookup"
        ],
        "common_user_intents": [
            "List all countries",
            "Show country codes",
            "Which countries do we operate in",
            "Country master data",
            "Countries list",
            "Country directory"
        ],
        "important_columns": ["countryCode", "countryName"],
        "business_metrics": [],
        "common_filters": ["isActive"],
        "common_groupby": [],
    },
    "dmn_State": {
        "display_name": "States",
        "domain": "Geography",
        "module": "Geography Master",
        "description": "State reference table linked to countries and cities. Used for GST state codes, delivery routing, and regional sales analysis.",
        "search_weight": 4, "priority": "Medium",
        "search_keywords": [
            "state", "states", "state master", "state list",
            "state code", "state name", "gst state code",
            "region", "province", "territory", "division",
            "state details", "state lookup", "state directory",
            "gst state", "state wise"
        ],
        "common_user_intents": [
            "List all states",
            "Show states in India",
            "GST state codes",
            "Which states do we serve",
            "States by country",
            "State wise customers",
            "State directory"
        ],
        "important_columns": ["stateCode", "stateName", "countryId"],
        "business_metrics": [],
        "common_filters": ["isActive", "countryId"],
        "common_groupby": ["countryId"],
    },
    "tbl_AccountGroup": {
        "display_name": "Account Groups",
        "domain": "Finance",
        "module": "Accounting",
        "description": "Chart of accounts grouping structure. Parent-child hierarchy for ledgers (e.g., Assets > Current Assets > Cash). Used in journal vouchers and financial reporting.",
        "search_weight": 5, "priority": "Medium",
        "search_keywords": [
            "account group", "account groups", "ledger group",
            "chart of accounts", "account category", "account head",
            "financial group", "gl group", "general ledger group",
            "account hierarchy", "parent account"
        ],
        "common_user_intents": [
            "Show all account groups",
            "List ledger groups",
            "Chart of accounts structure",
            "Account group hierarchy",
            "Parent child account groups"
        ],
        "important_columns": ["groupName", "parentId", "groupType"],
        "business_metrics": [],
        "common_filters": ["isActive"],
        "common_groupby": ["groupType"],
    },
    "tbl_AccountLedger": {
        "display_name": "Account Ledgers",
        "domain": "Finance",
        "module": "Accounting",
        "description": "Individual account ledgers for tracking financial transactions. Each ledger belongs to an account group and records debits, credits, and balances.",
        "search_weight": 6, "priority": "Medium",
        "search_keywords": [
            "ledger", "ledgers", "account ledger", "account ledgers",
            "gl", "general ledger", "account head", "account name",
            "financial ledger", "account balance", "debit credit",
            "trial balance", "account code"
        ],
        "common_user_intents": [
            "Show all ledgers",
            "List account heads",
            "Ledger with balance",
            "Show GL codes",
            "Ledger master data",
            "Account ledger list"
        ],
        "important_columns": ["ledgerName", "ledgerCode", "groupId", "openingBalance"],
        "business_metrics": ["openingBalance"],
        "common_filters": ["isActive", "groupId"],
        "common_groupby": ["groupId"],
    },
    "tbl_Attendance": {
        "display_name": "Employee Attendance",
        "domain": "HR",
        "module": "Attendance Management",
        "description": "Daily employee attendance records tracking check-in, check-out, work hours, overtime, and status (present, absent, half-day, leave).",
        "search_weight": 5, "priority": "Medium",
        "search_keywords": [
            "attendance", "employee attendance", "check in", "check out",
            "present", "absent", "half day", "work hours", "overtime",
            "daily attendance", "attendance record", "punch in", "punch out",
            "attendance report", "attendance list"
        ],
        "common_user_intents": [
            "Show today's attendance",
            "List absent employees today",
            "Attendance for employee X this month",
            "Overtime hours summary",
            "Monthly attendance report",
            "Present employees today"
        ],
        "important_columns": ["employeeId", "attendanceDate", "checkInTime", "checkOutTime", "workHours", "overtimeHours", "status"],
        "business_metrics": ["workHours", "overtimeHours"],
        "common_filters": ["employeeId", "attendanceDate", "status"],
        "common_groupby": ["status", "attendanceDate"],
    },
    "tbl_AuditLog": {
        "display_name": "Audit Logs",
        "domain": "System",
        "module": "System Administration",
        "description": "System audit trail recording user actions (create, update, delete) across all modules. Tracks who changed what and when for compliance and debugging.",
        "search_weight": 4, "priority": "Medium",
        "search_keywords": [
            "audit log", "audit trail", "activity log", "change log",
            "user activity", "system log", "action log",
            "audit record", "modification history", "who changed"
        ],
        "common_user_intents": [
            "Show recent audit logs",
            "Who changed invoice X",
            "Audit trail for table Y",
            "Recent system changes",
            "User activity today"
        ],
        "important_columns": ["userId", "actionType", "tableName", "recordId", "actionTimestamp"],
        "business_metrics": [],
        "common_filters": ["userId", "tableName", "actionType", "actionTimestamp"],
        "common_groupby": ["tableName", "actionType"],
    },
    "tbl_Booking": {
        "display_name": "Bookings",
        "domain": "Sales",
        "module": "Sales Management",
        "description": "Sales booking records capturing customer orders, product details, quantities, pricing, and delivery schedule. Triggers the fulfillment pipeline through invoicing and delivery.",
        "search_weight": 8, "priority": "High",
        "search_keywords": [
            "booking", "bookings", "sales booking", "customer booking",
            "order booking", "booking details", "booking record",
            "booking number", "booking date", "booking status",
            "reservation", "sales order", "demand"
        ],
        "common_user_intents": [
            "Show all bookings",
            "Bookings for customer X",
            "Pending bookings today",
            "Booking details for booking number Y",
            "Total bookings this month",
            "Bookings by date range"
        ],
        "important_columns": ["bookingNo", "bookingDate", "organizationId", "totalAmount", "statusId"],
        "business_metrics": ["totalAmount", "totalQty"],
        "common_filters": ["organizationId", "statusId", "bookingDate"],
        "common_groupby": ["bookingDate", "statusId"],
    },
    "tbl_BookingDelivery": {
        "display_name": "Booking Deliveries",
        "domain": "Sales",
        "module": "Delivery Management",
        "description": "Delivery tracking for bookings. Records delivery date, quantity delivered, vehicle, driver, and delivery status for each booking shipment.",
        "search_weight": 6, "priority": "Medium",
        "search_keywords": [
            "delivery", "deliveries", "booking delivery", "shipment",
            "dispatch", "delivery details", "delivery status",
            "delivery date", "delivery tracking", "goods delivery",
            "consignment", "delivery note"
        ],
        "common_user_intents": [
            "Show pending deliveries",
            "Deliveries today",
            "Delivery status for booking X",
            "Undelivered shipments",
            "Delivery report this week",
            "Late deliveries"
        ],
        "important_columns": ["bookingId", "deliveryDate", "deliveredQty", "vehicleId", "driverId", "statusId"],
        "business_metrics": ["deliveredQty"],
        "common_filters": ["bookingId", "statusId", "deliveryDate"],
        "common_groupby": ["statusId", "deliveryDate"],
    },
    "tbl_CreditDebitNote": {
        "display_name": "Credit/Debit Notes",
        "domain": "Finance",
        "module": "Accounts Receivable/Payable",
        "description": "Credit notes (returns/allowances) and debit notes (additional charges) issued against invoices. Adjusts outstanding balances for customers and vendors.",
        "search_weight": 6, "priority": "Medium",
        "search_keywords": [
            "credit note", "debit note", "credit notes", "debit notes",
            "cdn", "dbn", "credit debit note", "adjustment note",
            "return note", "allowance", "rebate", "discount note",
            "note master", "purchase return", "sales return",
            "return records", "return adjustments", "credit debit"
        ],
        "common_user_intents": [
            "Show credit notes this month",
            "Debit notes for vendor X",
            "Pending credit notes",
            "Total credit notes value",
            "Credit notes against invoice Y",
            "Return adjustments"
        ],
        "important_columns": ["noteNo", "noteDate", "noteType", "organizationId", "amount", "invoiceId"],
        "business_metrics": ["amount", "taxAmount", "totalAmount"],
        "common_filters": ["noteType", "organizationId", "noteDate"],
        "common_groupby": ["noteType"],
    },
    "tbl_Department": {
        "display_name": "Departments",
        "domain": "HR",
        "module": "Organization Structure",
        "description": "Department master listing all organizational departments (Sales, Purchase, HR, Finance, Production, etc.). Each employee belongs to one department.",
        "search_weight": 3, "priority": "Low",
        "search_keywords": [
            "department", "departments", "dept", "dept list",
            "department master", "department name", "organizational unit",
            "team", "division", "section", "unit"
        ],
        "common_user_intents": [
            "List all departments",
            "How many departments",
            "Department master data",
            "Departments in the company",
            "Show department names"
        ],
        "important_columns": ["departmentName", "departmentCode"],
        "business_metrics": [],
        "common_filters": ["isActive"],
        "common_groupby": [],
    },
    "tbl_Designation": {
        "display_name": "Designations",
        "domain": "HR",
        "module": "Organization Structure",
        "description": "Job designation/title master (Manager, Executive, Director, etc.). Links to employees to define roles and reporting hierarchy.",
        "search_weight": 3, "priority": "Low",
        "search_keywords": [
            "designation", "designations", "job title", "job titles",
            "role", "position", "rank", "grade",
            "designation master", "title master", "job role"
        ],
        "common_user_intents": [
            "List all designations",
            "Show job titles",
            "Designation master data",
            "What designations exist",
            "Designations in HR"
        ],
        "important_columns": ["designationName", "designationCode"],
        "business_metrics": [],
        "common_filters": ["isActive"],
        "common_groupby": [],
    },
    "tbl_DriverMaster": {
        "display_name": "Drivers",
        "domain": "Logistics",
        "module": "Fleet Management",
        "description": "Driver master records with license details, contact information, and vehicle assignments. Used in trip sheets and delivery tracking.",
        "search_weight": 5, "priority": "Medium",
        "search_keywords": [
            "driver", "drivers", "driver master", "driver list",
            "chauffeur", "transporter driver", "driver name",
            "license number", "driver details", "driver contact",
            "vehicle driver"
        ],
        "common_user_intents": [
            "List all drivers",
            "Show driver details",
            "Driver with license X",
            "Active drivers",
            "Driver contact information",
            "Drivers assigned to vehicles"
        ],
        "important_columns": ["driverName", "licenseNo", "mobileNo", "vehicleId"],
        "business_metrics": [],
        "common_filters": ["isActive"],
        "common_groupby": [],
    },
    "tbl_Employee": {
        "display_name": "Employees",
        "domain": "HR",
        "module": "HR Management",
        "description": "Comprehensive employee master storing personal details, contact information, department, designation, reporting manager, employment type, work location, address, and bank/PF/ESI details. Core entity for HR, payroll, and attendance modules.",
        "search_weight": 8, "priority": "High",
        "search_keywords": [
            "employee", "employees", "staff", "staff member", "staff members",
            "worker", "workers", "personnel", "team member", "team members",
            "emp", "emp list", "employee list", "employee master",
            "human resource", "hr", "manpower", "workforce",
            "employee name", "employee code", "emp code",
            "worker details", "employee details", "staff details",
            "headcount", "head count", "man count",
            "new joiners", "joining", "new employee", "recent joiners",
            "who joined", "recently joined"
        ],
        "common_user_intents": [
            "List all employees",
            "Show employee details for X",
            "How many employees in department Y",
            "Employees who joined this year",
            "Total employees",
            "Employee attendance",
            "Employee master data",
            "Active employees list",
            "Employees by designation",
            "Employee contact details"
        ],
        "important_columns": ["empCode", "firstName", "lastName", "departmentId", "designationId", "reportingToId", "employmentType", "dateOfJoining", "mobileNo", "email"],
        "business_metrics": ["basicSalary", "ctc"],
        "common_filters": ["departmentId", "designationId", "isActive", "employmentType"],
        "common_groupby": ["departmentId", "designationId", "employmentType"],
    },
    "tbl_ErrorLog": {
        "display_name": "Error Logs",
        "domain": "System",
        "module": "System Administration",
        "description": "Application error logging table capturing exception details, stack traces, user context, and timestamps for debugging and monitoring.",
        "search_weight": 3, "priority": "Low",
        "search_keywords": [
            "error log", "error logs", "exception", "exceptions",
            "error", "errors", "bug", "system error",
            "application error", "crash log", "error report"
        ],
        "common_user_intents": [
            "Show recent errors",
            "Error log today",
            "What errors occurred",
            "Application exceptions",
            "Error details"
        ],
        "important_columns": ["errorCode", "errorMessage", "errorTimestamp", "userId"],
        "business_metrics": [],
        "common_filters": ["errorTimestamp"],
        "common_groupby": ["errorCode"],
    },
    "tbl_EwayBill": {
        "display_name": "E-Way Bills",
        "domain": "Compliance",
        "module": "Tax Compliance",
        "description": "E-way bill records for goods movement compliance. Generated for shipments above ₹50,000 as per GST rules. Contains transporter, vehicle, and goods details.",
        "search_weight": 6, "priority": "Medium",
        "search_keywords": [
            "eway bill", "e-way bill", "eway bills", "e-way bills",
            "eway", "ewaybill", "eway bill number", "eway bill details",
            "goods movement", "transport document", "eway generated",
            "eway bill status", "eway bill list"
        ],
        "common_user_intents": [
            "Show eway bills today",
            "Generate eway bill for invoice X",
            "Pending eway bills",
            "Eway bill details",
            "Eway bills by date range",
            "Eway bill status"
        ],
        "important_columns": ["ewayBillNo", "ewayBillDate", "invoiceId", "vehicleId", "driverId", "validUntil"],
        "business_metrics": ["totalValue"],
        "common_filters": ["ewayBillDate", "invoiceId"],
        "common_groupby": ["ewayBillDate"],
    },
    "tbl_GlobalPurchaseRate": {
        "display_name": "Global Purchase Rates",
        "domain": "Pricing",
        "module": "Purchase Pricing",
        "description": "Standard purchase rates for products across vendors. Defines base cost prices used in purchase orders and cost analysis.",
        "search_weight": 6, "priority": "Medium",
        "search_keywords": [
            "purchase rate", "purchase rates", "buying rate", "cost price",
            "purchase price", "vendor rate", "supplier rate",
            "buying price", "procurement rate", "purchase rate master",
            "global rate", "standard rate"
        ],
        "common_user_intents": [
            "Show purchase rates for product X",
            "Current buying rates",
            "Purchase rate list",
            "Rates from vendor Y",
            "Standard cost prices"
        ],
        "important_columns": ["productId", "vendorId", "rate", "effectiveFrom"],
        "business_metrics": ["rate"],
        "common_filters": ["productId", "vendorId"],
        "common_groupby": ["productId"],
    },
    "tbl_GlobalSaleRate": {
        "display_name": "Global Sale Rates",
        "domain": "Pricing",
        "module": "Sales Pricing",
        "description": "Standard sale rates for products across customers/dealers. Defines base selling prices used in sales orders, invoices, and price lists.",
        "search_weight": 6, "priority": "Medium",
        "search_keywords": [
            "sale rate", "sale rates", "selling rate", "selling price",
            "sale price", "customer rate", "dealer rate", "mrp",
            "list price", "price list", "global rate", "standard rate",
            "product rate", "pricing"
        ],
        "common_user_intents": [
            "Show sale rates for product X",
            "Current selling prices",
            "Sale rate list",
            "Price for customer Y",
            "Standard selling prices"
        ],
        "important_columns": ["productId", "customerId", "rate", "effectiveFrom"],
        "business_metrics": ["rate"],
        "common_filters": ["productId", "customerId"],
        "common_groupby": ["productId"],
    },
    "tbl_GSTReturn": {
        "display_name": "GST Returns",
        "domain": "Compliance",
        "module": "Tax Compliance",
        "description": "GST return filing records tracking GSTR-1, GSTR-3B filings with submission dates, status, and filed amounts. Ensures tax compliance.",
        "search_weight": 5, "priority": "Medium",
        "search_keywords": [
            "gst return", "gst returns", "gstr", "gstr1", "gstr3b",
            "tax return", "gst filing", "return filing",
            "gst submission", "monthly return", "quarterly return",
            "gst compliance", "tax filing status"
        ],
        "common_user_intents": [
            "Show GST returns filed",
            "Pending GST returns",
            "GSTR-3B status",
            "GST returns this month",
            "Filed GST returns"
        ],
        "important_columns": ["returnType", "returnPeriod", "filingDate", "status", "totalTax"],
        "business_metrics": ["totalTax", "totalValue"],
        "common_filters": ["returnType", "returnPeriod", "status"],
        "common_groupby": ["returnType", "returnPeriod"],
    },
    "tbl_InventoryAdjustment": {
        "display_name": "Inventory Adjustments",
        "domain": "Inventory",
        "module": "Inventory Management",
        "description": "Stock adjustment records for correcting inventory discrepancies. Records reason for adjustment (damage, expiry, theft, correction) and quantity changes.",
        "search_weight": 5, "priority": "Medium",
        "search_keywords": [
            "inventory adjustment", "stock adjustment", "stock correction",
            "adjustment", "adjustments", "inventory correction",
            "stock variance", "damage write off", "expiry adjustment",
            "physical adjustment", "stock loss", "stock gain"
        ],
        "common_user_intents": [
            "Show recent inventory adjustments",
            "Adjustments for product X",
            "Stock correction records",
            "Damage adjustments this month",
            "Adjustment reasons summary"
        ],
        "important_columns": ["productId", "adjustmentQty", "reason", "adjustmentDate", "warehouseId"],
        "business_metrics": ["adjustmentQty", "adjustedValue"],
        "common_filters": ["productId", "warehouseId", "adjustmentDate"],
        "common_groupby": ["reason"],
    },
    "tbl_JournalVoucher": {
        "display_name": "Journal Vouchers",
        "domain": "Finance",
        "module": "Accounting",
        "description": "Journal voucher header recording financial journal entries with debit/credit pairs, narration, and approval status. Core accounting transaction document.",
        "search_weight": 7, "priority": "High",
        "search_keywords": [
            "journal voucher", "journal vouchers", "journal entry",
            "journal entries", "jv", "jv list", "journal book",
            "accounting entry", "debit credit entry", "general journal",
            "journal record", "financial entry"
        ],
        "common_user_intents": [
            "Show journal vouchers this month",
            "Journal entries for account X",
            "Pending journal vouchers",
            "Total journal amount",
            "Journal voucher details",
            "Unapproved journal entries"
        ],
        "important_columns": ["voucherNo", "voucherDate", "totalDebit", "totalCredit", "narration", "statusId"],
        "business_metrics": ["totalDebit", "totalCredit"],
        "common_filters": ["voucherDate", "statusId"],
        "common_groupby": ["voucherDate"],
    },
    "tbl_JournalVoucherDetail": {
        "display_name": "Journal Voucher Details",
        "domain": "Finance",
        "module": "Accounting",
        "description": "Line-level details of journal vouchers. Each row is a debit or credit entry against a specific ledger account within a journal voucher.",
        "search_weight": 5, "priority": "Medium",
        "search_keywords": [
            "journal detail", "journal line", "journal voucher detail",
            "debit entry", "credit entry", "ledger entry",
            "journal line item", "accounting detail"
        ],
        "common_user_intents": [
            "Show journal lines for voucher X",
            "Debit entries in journal Y",
            "Ledger-wise journal breakdown",
            "Journal detail by account"
        ],
        "important_columns": ["voucherId", "ledgerId", "debitAmount", "creditAmount"],
        "business_metrics": ["debitAmount", "creditAmount"],
        "common_filters": ["voucherId", "ledgerId"],
        "common_groupby": ["ledgerId"],
    },
    "tbl_LeaveApplication": {
        "display_name": "Leave Applications",
        "domain": "HR",
        "module": "Leave Management",
        "description": "Employee leave applications with leave type, duration, reason, and approval status. Tracks leave balance consumption and manager approvals.",
        "search_weight": 5, "priority": "Medium",
        "search_keywords": [
            "leave", "leaves", "leave application", "leave applications",
            "leave request", "leave record", "leave details",
            "sick leave", "casual leave", "earned leave",
            "leave balance", "leave history", "time off"
        ],
        "common_user_intents": [
            "Show pending leave applications",
            "Leaves for employee X",
            "Approved leaves this month",
            "Leave balance for employee Y",
            "Total leaves taken this year",
            "Leave applications by status"
        ],
        "important_columns": ["employeeId", "leaveTypeId", "fromDate", "toDate", "days", "statusId"],
        "business_metrics": ["days"],
        "common_filters": ["employeeId", "leaveTypeId", "statusId"],
        "common_groupby": ["leaveTypeId", "statusId"],
    },
    "tbl_LeaveType": {
        "display_name": "Leave Types",
        "domain": "HR",
        "module": "Leave Management",
        "description": "Leave type master defining categories (Casual Leave, Sick Leave, Earned Leave, Maternity Leave, etc.) with annual quota and carry-forward rules.",
        "search_weight": 3, "priority": "Low",
        "search_keywords": [
            "leave type", "leave types", "leave category",
            "casual leave", "sick leave", "earned leave",
            "leave master", "leave name", "leave code",
            "paid leave", "unpaid leave", "maternity leave"
        ],
        "common_user_intents": [
            "List all leave types",
            "What leave types are available",
            "Leave types with quota",
            "Leave type master data"
        ],
        "important_columns": ["leaveTypeName", "leaveCode", "annualQuota"],
        "business_metrics": ["annualQuota"],
        "common_filters": ["isActive"],
        "common_groupby": [],
    },
    "tbl_LoadingDetail": {
        "display_name": "Loading Details",
        "domain": "Logistics",
        "module": "Warehouse Operations",
        "description": "Goods loading records for dispatch operations. Tracks what products, quantities, and packages are loaded onto vehicles for delivery.",
        "search_weight": 6, "priority": "Medium",
        "search_keywords": [
            "loading", "loading detail", "loading details",
            "loading record", "loading sheet", "loading list",
            "goods loading", "loading slip", "loading chit",
            "dispatch loading", "vehicle loading"
        ],
        "common_user_intents": [
            "Show loading details today",
            "Loading record for trip X",
            "What was loaded on vehicle Y",
            "Loading sheet for dispatch",
            "Products loaded today"
        ],
        "important_columns": ["tripSheetId", "productId", "loadedQty", "loadingDate"],
        "business_metrics": ["loadedQty"],
        "common_filters": ["tripSheetId", "loadingDate"],
        "common_groupby": ["loadingDate"],
    },
    "tbl_OrgAddress": {
        "display_name": "Organization Addresses",
        "domain": "Organization",
        "module": "Organization Master",
        "description": "Physical addresses for organizations (offices, warehouses, godowns). Multiple addresses per organization for billing, shipping, and registered office.",
        "search_weight": 5, "priority": "Medium",
        "search_keywords": [
            "address", "addresses", "org address", "organization address",
            "billing address", "shipping address", "registered address",
            "office address", "warehouse address", "location",
            "office location", "godown address"
        ],
        "common_user_intents": [
            "Show addresses for organization X",
            "Billing address of dealer Y",
            "Warehouse locations",
            "All addresses for company Z",
            "Shipping addresses"
        ],
        "important_columns": ["organizationId", "addressType", "addressLine1", "cityId", "pinCode"],
        "business_metrics": [],
        "common_filters": ["organizationId", "addressType"],
        "common_groupby": ["addressType"],
    },
    "tbl_Organization": {
        "display_name": "Organizations",
        "domain": "Organization",
        "module": "Organization Master",
        "description": "Central master for all business partners including dealers, distributors, vendors, CNFs, and transporters. Stores firm name, GST/PAN details, contact info, credit limits, opening balances, and payment terms. Referenced across sales, purchase, and finance modules.",
        "search_weight": 9, "priority": "High",
        "search_keywords": [
            "organization", "organizations", "company", "companies",
            "dealer", "dealers", "distributor", "distributors",
            "vendor", "vendors", "supplier", "suppliers",
            "firm", "firms", "partner", "partners",
            "customer", "customers", "client", "clients",
            "buyer", "buyers", "party", "parties", "registered parties",
            "business partner", "business partners", "trader",
            "cnf", "transporter", "consignee", "consignees", "consignee list",
            "firm name", "company name", "org name",
            "dealer name", "vendor name", "customer name",
            "gst number", "pan number", "gstin",
            "credit limit", "opening balance",
            "contact person", "mobile number", "email",
            "org code", "organization code", "party code",
            "all parties", "party list", "organization list"
        ],
        "common_user_intents": [
            "Show dealer details",
            "List all vendors",
            "Organization with GST number X",
            "Companies with credit limit above Y",
            "Dealer contact details",
            "Get me total customers",
            "How many customers do we have",
            "List all customers",
            "Count customers by city",
            "Customers with credit limit above X",
            "Show all organizations",
            "Active dealers list",
            "Vendor master data",
            "Customer master data",
            "Partners with outstanding balance"
        ],
        "important_columns": ["orgCode", "firmName", "tradingName", "gstNo", "panNo", "creditLimit", "paymentTermId", "orgTypeId", "cityId"],
        "business_metrics": ["creditLimit", "openingBalance"],
        "common_filters": ["orgTypeId", "isActive", "cityId", "paymentTermId"],
        "common_groupby": ["orgTypeId", "cityId"],
    },
    "tbl_OrgBankDetail": {
        "display_name": "Organization Bank Details",
        "domain": "Organization",
        "module": "Organization Master",
        "description": "Bank account details for organizations including account number, IFSC, bank name, and branch. Used for payment processing and NEFT/RTGS transfers.",
        "search_weight": 4, "priority": "Medium",
        "search_keywords": [
            "bank detail", "bank details", "bank account", "bank accounts",
            "account number", "ifsc", "bank name", "branch name",
            "org bank", "organization bank", "payment bank",
            "neft", "rtgs", "bank information"
        ],
        "common_user_intents": [
            "Show bank details for organization X",
            "Bank account of dealer Y",
            "List bank accounts",
            "IFSC code for company Z",
            "Payment bank details"
        ],
        "important_columns": ["organizationId", "accountNumber", "ifscCode", "bankName", "branchName"],
        "business_metrics": [],
        "common_filters": ["organizationId"],
        "common_groupby": [],
    },
    "tbl_OrgContact": {
        "display_name": "Organization Contacts",
        "domain": "Organization",
        "module": "Organization Master",
        "description": "Contact person details for organizations. Stores names, designations, phone numbers, emails, and WhatsApp for primary and secondary contacts.",
        "search_weight": 4, "priority": "Medium",
        "search_keywords": [
            "contact", "contacts", "org contact", "contact person",
            "contact details", "contact information", "phone number",
            "mobile number", "email", "whatsapp",
            "contact name", "person name", "key person"
        ],
        "common_user_intents": [
            "Show contacts for organization X",
            "Contact person at dealer Y",
            "Phone number of company Z",
            "Email contacts for vendors",
            "All contact details"
        ],
        "important_columns": ["organizationId", "contactName", "designation", "mobileNo", "email"],
        "business_metrics": [],
        "common_filters": ["organizationId"],
        "common_groupby": [],
    },
    "tbl_OrgRegistration": {
        "display_name": "Organization Registrations",
        "domain": "Compliance",
        "module": "Tax Compliance",
        "description": "Tax registration details for organizations including GSTIN, PAN, TAN, state codes, and registration types. Critical for tax compliance and invoice generation.",
        "search_weight": 4, "priority": "Medium",
        "search_keywords": [
            "registration", "registrations", "org registration",
            "gstin", "pan", "tan", "tax registration",
            "gst registration", "gst number", "pan number",
            "state code", "registration type", "tax id"
        ],
        "common_user_intents": [
            "Show registrations for organization X",
            "GSTIN of dealer Y",
            "Tax registrations list",
            "PAN details for company Z",
            "Registration by state"
        ],
        "important_columns": ["organizationId", "registrationType", "registrationNumber", "stateCode"],
        "business_metrics": [],
        "common_filters": ["organizationId", "registrationType"],
        "common_groupby": ["registrationType"],
    },
    "tbl_PaymentMade": {
        "display_name": "Payments Made",
        "domain": "Finance",
        "module": "Accounts Payable",
        "description": "Vendor payment records tracking amount paid, payment mode (NEFT/RTGS/Cheque/Cash), reference number, and linked purchase invoices.",
        "search_weight": 7, "priority": "High",
        "search_keywords": [
            "payment made", "payments made", "vendor payment", "vendor payments",
            "purchase payment", "payment to supplier", "payment to vendor",
            "payment record", "payment details", "payment list",
            "payment date", "payment amount", "payment mode",
            "neft", "rtgs", "cheque", "cash payment",
            "outgoing payment", "disbursement",
            "accounts payable", "payable", "expenses", "expenditure",
            "outflow", "cash out", "money paid", "total expenses",
            "dashboard", "expense dashboard", "payable dashboard",
            "pnl", "profit and loss", "p&l", "profit loss"
        ],
        "common_user_intents": [
            "Show payments made this month",
            "Payment to vendor X",
            "Total payments this quarter",
            "Payments by date range",
            "Pending payments",
            "Payment details for invoice Y"
        ],
        "important_columns": ["paymentNo", "paymentDate", "organizationId", "amount", "paymentMode", "referenceNo"],
        "business_metrics": ["amount", "tdsAmount", "netAmount"],
        "common_filters": ["organizationId", "paymentDate", "paymentMode"],
        "common_groupby": ["paymentMode", "paymentDate"],
    },
    "tbl_PaymentReceived": {
        "display_name": "Payments Received",
        "domain": "Finance",
        "module": "Accounts Receivable",
        "description": "Customer payment records tracking amount received, payment mode, reference number, and linked sale invoices. Core accounts receivable transaction.",
        "search_weight": 7, "priority": "High",
        "search_keywords": [
            "payment received", "payments received", "customer payment",
            "customer payments", "receipt", "receipts", "money received",
            "payment collection", "collection", "collections",
            "payment from customer", "dealer payment",
            "payment date", "payment amount", "payment mode",
            "incoming payment", "cash received",
            "accounts receivable", "receivable", "cash in", "money in",
            "dashboard", "finance dashboard", "collection dashboard",
            "pnl", "profit and loss", "p&l", "profit loss"
        ],
        "common_user_intents": [
            "Show payments received this month",
            "Payment from customer X",
            "Total collections this quarter",
            "Payments by date range",
            "Outstanding payments",
            "Payment details for invoice Y"
        ],
        "important_columns": ["receiptNo", "receiptDate", "organizationId", "amount", "paymentMode", "referenceNo"],
        "business_metrics": ["amount", "tdsAmount", "netAmount"],
        "common_filters": ["organizationId", "receiptDate", "paymentMode"],
        "common_groupby": ["paymentMode", "receiptDate"],
    },
    "tbl_PayrollDetail": {
        "display_name": "Payroll Details",
        "domain": "HR",
        "module": "Payroll Management",
        "description": "Line-level payroll records for each employee showing earnings (basic, HDA, DA, TA) and deductions (PF, ESI, TDS) within a payroll header.",
        "search_weight": 5, "priority": "Medium",
        "search_keywords": [
            "payroll detail", "payroll details", "salary detail",
            "salary details", "earnings", "deductions",
            "pf", "esi", "tds", "basic salary",
            "da", "hra", "ta", "pay slip", "payslip"
        ],
        "common_user_intents": [
            "Show salary details for employee X",
            "Payroll breakdown for month Y",
            "Earnings and deductions",
            "Salary slip for employee Z",
            "PF deduction details"
        ],
        "important_columns": ["payrollHeaderId", "employeeId", "basicSalary", "hra", "da", "pf", "esi"],
        "business_metrics": ["basicSalary", "hra", "da", "pf", "esi", "tds", "netPay"],
        "common_filters": ["payrollHeaderId", "employeeId"],
        "common_groupby": [],
    },
    "tbl_PayrollHeader": {
        "display_name": "Payroll Headers",
        "domain": "HR",
        "module": "Payroll Management",
        "description": "Monthly payroll batch headers summarizing total employees, total gross, total deductions, and net pay for a pay period. Contains payroll status and approval.",
        "search_weight": 6, "priority": "Medium",
        "search_keywords": [
            "payroll", "payroll header", "payroll batch",
            "salary", "salary batch", "monthly salary",
            "pay period", "pay month", "salary month",
            "gross salary", "net salary", "payroll summary",
            "payroll status", "salary processing"
        ],
        "common_user_intents": [
            "Show payroll this month",
            "Total salary expense",
            "Payroll batch status",
            "Processed payrolls",
            "Payroll summary for month X",
            "Total deductions this month"
        ],
        "important_columns": ["payrollMonth", "payrollYear", "totalEmployees", "totalGross", "totalDeductions", "totalNet", "statusId"],
        "business_metrics": ["totalGross", "totalDeductions", "totalNet"],
        "common_filters": ["payrollMonth", "payrollYear", "statusId"],
        "common_groupby": ["payrollMonth", "payrollYear"],
    },
    "tbl_PhysicalInventory": {
        "display_name": "Physical Inventory",
        "domain": "Inventory",
        "module": "Inventory Management",
        "description": "Physical stock count records comparing system stock with actual physical count. Used for annual/periodic inventory audits and stock reconciliation.",
        "search_weight": 5, "priority": "Medium",
        "search_keywords": [
            "physical inventory", "stock count", "physical count",
            "stock audit", "inventory audit", "stock verification",
            "physical stock", "stock take", "inventory count",
            "stock reconciliation", "variance report"
        ],
        "common_user_intents": [
            "Show physical inventory count",
            "Stock variance for product X",
            "Physical count results",
            "Inventory audit this month",
            "Stock discrepancy report"
        ],
        "important_columns": ["productId", "systemQty", "physicalQty", "variance", "warehouseId", "countDate"],
        "business_metrics": ["systemQty", "physicalQty", "variance"],
        "common_filters": ["productId", "warehouseId", "countDate"],
        "common_groupby": ["warehouseId", "countDate"],
    },
    "tbl_ProductCategory": {
        "display_name": "Product Categories",
        "domain": "Product",
        "module": "Product Master",
        "description": "Product category master for classifying products into groups (e.g., Raw Material, Finished Goods, Consumables). Top level of product hierarchy.",
        "search_weight": 5, "priority": "Medium",
        "search_keywords": [
            "product category", "product categories", "category",
            "categories", "product group", "item category",
            "item group", "product classification", "category master",
            "product type", "goods type"
        ],
        "common_user_intents": [
            "List all product categories",
            "Show category list",
            "Products in category X",
            "Category master data",
            "How many categories"
        ],
        "important_columns": ["categoryName", "categoryCode"],
        "business_metrics": [],
        "common_filters": ["isActive"],
        "common_groupby": [],
    },
    "tbl_ProductClass": {
        "display_name": "Product Classes",
        "domain": "Product",
        "module": "Product Master",
        "description": "Product class subclassification within categories. Provides finer grouping for product analysis and reporting.",
        "search_weight": 5, "priority": "Medium",
        "search_keywords": [
            "product class", "product classes", "class",
            "item class", "product subclass", "product classification",
            "class master", "product grade type"
        ],
        "common_user_intents": [
            "List all product classes",
            "Show class list",
            "Products in class X",
            "Class master data"
        ],
        "important_columns": ["className", "classCode", "categoryId"],
        "business_metrics": [],
        "common_filters": ["isActive", "categoryId"],
        "common_groupby": ["categoryId"],
    },
    "tbl_ProductGrade": {
        "display_name": "Product Grades",
        "domain": "Product",
        "module": "Product Master",
        "description": "Product quality grades (A, B, C, Premium, Standard, Economy). Used for quality-based pricing and inventory segregation.",
        "search_weight": 5, "priority": "Medium",
        "search_keywords": [
            "product grade", "product grades", "grade",
            "quality grade", "item grade", "product quality",
            "grade master", "quality level", "grade a", "grade b"
        ],
        "common_user_intents": [
            "List all product grades",
            "Show grade list",
            "Products with grade A",
            "Grade master data"
        ],
        "important_columns": ["gradeName", "gradeCode", "categoryId"],
        "business_metrics": [],
        "common_filters": ["isActive", "categoryId"],
        "common_groupby": ["categoryId"],
    },
    "tbl_ProductMaster": {
        "display_name": "Products",
        "domain": "Product",
        "module": "Product Master",
        "description": "Central product definition storing product code, name, description, category, class, UOM references, HSN code, GST rate, and stock management flags (batch, serial). Foundation for all sales, purchase, and inventory transactions.",
        "search_weight": 8, "priority": "High",
        "search_keywords": [
            "product", "products", "item", "items", "material", "materials",
            "goods", "inventory", "stock", "sku", "product master",
            "product code", "product name", "item code", "item name",
            "hsn code", "hsn", "product description",
            "product list", "product details", "item list",
            "raw material", "finished goods", "consumable",
            "product catalog", "catalog", "stock item",
            "product group", "product category"
        ],
        "common_user_intents": [
            "List all products",
            "Show product details for X",
            "Products under category Y",
            "Product with HSN code Z",
            "Products with low stock",
            "Out of stock products",
            "Active products list",
            "Product catalog",
            "Products by category",
            "Product master data"
        ],
        "important_columns": ["productCode", "productName", "categoryId", "classId", "gradeId", "baseUOMId", "hsnCode", "gstRate", "minStock", "maxStock"],
        "business_metrics": ["minStock", "maxStock", "gstRate"],
        "common_filters": ["categoryId", "classId", "gradeId", "isActive"],
        "common_groupby": ["categoryId", "classId", "gradeId"],
    },
    "tbl_ProductPricing": {
        "display_name": "Product Pricing",
        "domain": "Pricing",
        "module": "Pricing Management",
        "description": "Product-specific pricing rules with customer/dealer type segmentation. Defines selling prices, discount slabs, and volume-based pricing.",
        "search_weight": 6, "priority": "Medium",
        "search_keywords": [
            "product pricing", "pricing", "price", "prices",
            "selling price", "mrp", "list price", "price list",
            "customer price", "dealer price", "discount",
            "price slab", "volume price", "rate card",
            "price master", "product rate"
        ],
        "common_user_intents": [
            "Show pricing for product X",
            "Price list for dealer Y",
            "Current selling prices",
            "Discount slabs",
            "Price for customer type Z"
        ],
        "important_columns": ["productId", "orgTypeId", "rate", "discountPercent", "minQty", "maxQty"],
        "business_metrics": ["rate", "discountPercent"],
        "common_filters": ["productId", "orgTypeId"],
        "common_groupby": ["productId"],
    },
    "tbl_PurchaseEnquiry": {
        "display_name": "Purchase Enquiries",
        "domain": "Purchase",
        "module": "Purchase Management",
        "description": "Purchase enquiry records from customers/dealers requesting quotes for products. Triggers the purchase workflow from enquiry to order to invoice.",
        "search_weight": 6, "priority": "Medium",
        "search_keywords": [
            "purchase enquiry", "purchase enquiries", "enquiry", "enquiries",
            "inquiry", "inquiries", "rfq", "request for quote",
            "quote request", "price inquiry", "purchase request",
            "enquiry details", "enquiry list", "enquiry records",
            "total enquiries", "enquiry summary", "enquiry report",
            "quote inquiry", "quotation request", "vendor inquiry"
        ],
        "common_user_intents": [
            "Show pending purchase enquiries",
            "Enquiries from customer X",
            "Open enquiries today",
            "Enquiry details for enquiry Y",
            "Total enquiries this month",
            "Enquiries by product",
            "Enquiry list today",
            "How many enquiries this month"
        ],
        "important_columns": ["enquiryNo", "enquiryDate", "organizationId", "statusId"],
        "business_metrics": [],
        "common_filters": ["organizationId", "statusId", "enquiryDate"],
        "common_groupby": ["enquiryDate", "statusId"],
    },
    "tbl_PurchaseInvoice": {
        "display_name": "Purchase Invoices",
        "domain": "Purchase",
        "module": "Purchase Management",
        "description": "Vendor/supplier invoices recording goods received, quantities, rates, taxes, and total amount. Core purchase transaction document for accounts payable.",
        "search_weight": 8, "priority": "High",
        "search_keywords": [
            "purchase invoice", "purchase invoices", "vendor invoice",
            "supplier invoice", "purchase bill", "purchase bills",
            "pi", "pi list", "purchase entry", "purchase record",
            "purchase details", "invoice from vendor",
            "goods received note", "grn", "GRN", "grn details",
            "purchase invoice number", "goods receipt", "receipt note",
            "dashboard", "purchase dashboard", "procurement dashboard",
            "pnl", "profit and loss", "p&l", "profit loss"
        ],
        "common_user_intents": [
            "Show purchase invoices",
            "Invoice from vendor X",
            "Total purchases this month",
            "Purchase invoice details",
            "Pending purchase invoices",
            "Purchase invoices by date range"
        ],
        "important_columns": ["invoiceNo", "invoiceDate", "organizationId", "totalAmount", "taxAmount", "statusId"],
        "business_metrics": ["totalAmount", "taxAmount", "netAmount"],
        "common_filters": ["organizationId", "statusId", "invoiceDate"],
        "common_groupby": ["invoiceDate", "statusId"],
    },
    "tbl_PurchaseOrder": {
        "display_name": "Purchase Orders",
        "domain": "Purchase",
        "module": "Purchase Management",
        "description": "Purchase order records sent to vendors with product, quantity, rate, and delivery terms. Tracks order status from creation to delivery.",
        "search_weight": 8, "priority": "High",
        "search_keywords": [
            "purchase order", "purchase orders", "po", "po list",
            "vendor order", "supplier order", "procurement order",
            "po number", "po details", "purchase order list",
            "order to vendor", "buying order", "po status"
        ],
        "common_user_intents": [
            "Show purchase orders",
            "PO for vendor X",
            "Pending purchase orders",
            "Purchase order details",
            "Total PO value this month",
            "PO by date range"
        ],
        "important_columns": ["poNo", "poDate", "organizationId", "totalAmount", "statusId"],
        "business_metrics": ["totalAmount"],
        "common_filters": ["organizationId", "statusId", "poDate"],
        "common_groupby": ["poDate", "statusId"],
    },
    "tbl_PurchaseSchedule": {
        "display_name": "Purchase Schedules",
        "domain": "Purchase",
        "module": "Purchase Management",
        "description": "Detailed purchase schedule/line items for purchase orders. Contains product-wise breakdown with quantities, rates, amounts, tax details, and delivery tracking.",
        "search_weight": 8, "priority": "High",
        "search_keywords": [
            "purchase schedule", "purchase schedules", "schedule",
            "po schedule", "po line item", "purchase line",
            "purchase detail", "purchase item", "schedule detail",
            "purchase schedule detail", "delivery schedule"
        ],
        "common_user_intents": [
            "Show purchase schedule for PO X",
            "Line items for purchase order Y",
            "Product-wise purchase details",
            "Purchase schedule by product",
            "Pending delivery schedule"
        ],
        "important_columns": ["purchaseOrderId", "productId", "quantity", "rate", "amount", "taxAmount", "deliveryDate"],
        "business_metrics": ["quantity", "rate", "amount", "taxAmount", "netAmount"],
        "common_filters": ["purchaseOrderId", "productId", "deliveryDate"],
        "common_groupby": ["productId"],
    },
    "tbl_QualityChecklist": {
        "display_name": "Quality Checklists",
        "domain": "Quality",
        "module": "Quality Management",
        "description": "Quality inspection checklists defining parameters to test for each product or batch. Links quality parameters with inspection criteria.",
        "search_weight": 6, "priority": "Medium",
        "search_keywords": [
            "quality checklist", "quality checklists", "qc checklist",
            "inspection checklist", "quality check", "qc",
            "quality inspection", "checklist", "check list",
            "quality test checklist", "inspection list"
        ],
        "common_user_intents": [
            "Show quality checklists",
            "QC checklist for product X",
            "Inspection parameters",
            "Quality checklist list",
            "Checklist for batch Y"
        ],
        "important_columns": ["checklistName", "productId", "batchId"],
        "business_metrics": [],
        "common_filters": ["productId"],
        "common_groupby": ["productId"],
    },
    "tbl_QualityParameter": {
        "display_name": "Quality Parameters",
        "domain": "Quality",
        "module": "Quality Management",
        "description": "Quality test parameters master (moisture, pH, viscosity, color, hardness, etc.) with acceptable ranges and test methods.",
        "search_weight": 4, "priority": "Medium",
        "search_keywords": [
            "quality parameter", "quality parameters", "test parameter",
            "test parameters", "quality test", "inspection parameter",
            "parameter master", "test method", "acceptable range",
            "quality standard", "specification"
        ],
        "common_user_intents": [
            "List quality parameters",
            "Show test parameters",
            "Parameters for quality check",
            "Quality standards list"
        ],
        "important_columns": ["parameterName", "parameterCode", "minValue", "maxValue", "unit"],
        "business_metrics": ["minValue", "maxValue"],
        "common_filters": ["isActive"],
        "common_groupby": [],
    },
    "tbl_QualityTestResult": {
        "display_name": "Quality Test Results",
        "domain": "Quality",
        "module": "Quality Management",
        "description": "Actual quality test results recorded during inspection. Each result captures measured value against expected range and pass/fail status.",
        "search_weight": 5, "priority": "Medium",
        "search_keywords": [
            "quality result", "quality results", "test result", "test results",
            "qc result", "inspection result", "quality report",
            "pass fail", "quality test data", "test report",
            "quality inspection result", "qc report"
        ],
        "common_user_intents": [
            "Show quality test results",
            "QC results for batch X",
            "Failed quality tests",
            "Quality test report",
            "Results by product"
        ],
        "important_columns": ["checklistId", "parameterId", "measuredValue", "status", "testDate"],
        "business_metrics": ["measuredValue"],
        "common_filters": ["checklistId", "status", "testDate"],
        "common_groupby": ["status"],
    },
    "tbl_RateApproval": {
        "display_name": "Rate Approvals",
        "domain": "Pricing",
        "module": "Pricing Management",
        "description": "Rate/special pricing approval workflow records. Captures requested rate, approved rate, approval status, and approver details for deviating from standard pricing.",
        "search_weight": 5, "priority": "Medium",
        "search_keywords": [
            "rate approval", "rate approvals", "price approval",
            "special rate", "discount approval", "pricing approval",
            "approval", "approvals", "rate approval list",
            "rate request", "price request"
        ],
        "common_user_intents": [
            "Show pending rate approvals",
            "Rate approval for product X",
            "Approved special rates",
            "Rate approval status",
            "Rate approval history"
        ],
        "important_columns": ["productId", "organizationId", "requestedRate", "approvedRate", "statusId"],
        "business_metrics": ["requestedRate", "approvedRate"],
        "common_filters": ["statusId", "organizationId"],
        "common_groupby": ["statusId"],
    },
    "tbl_RateBand": {
        "display_name": "Rate Bands",
        "domain": "Pricing",
        "module": "Pricing Management",
        "description": "Rate band/bracket definitions for volume-based or slab-based pricing. Defines rate ranges applicable for different quantity or value brackets.",
        "search_weight": 5, "priority": "Medium",
        "search_keywords": [
            "rate band", "rate bands", "price band", "price slab",
            "rate slab", "slab", "slabs", "bracket",
            "volume pricing", "quantity discount", "tiered pricing",
            "rate card", "pricing tier"
        ],
        "common_user_intents": [
            "Show rate bands",
            "Price slabs for product X",
            "Volume discount bands",
            "Rate bands list",
            "Slab rates for dealer Y"
        ],
        "important_columns": ["bandName", "minQty", "maxQty", "rate"],
        "business_metrics": ["minQty", "maxQty", "rate"],
        "common_filters": ["productId"],
        "common_groupby": ["productId"],
    },
    "tbl_RouteMaster": {
        "display_name": "Routes",
        "domain": "Logistics",
        "module": "Fleet Management",
        "description": "Transport route definitions with origin, destination, distance, and estimated travel time. Used in trip planning and delivery scheduling.",
        "search_weight": 5, "priority": "Medium",
        "search_keywords": [
            "route", "routes", "route master", "transport route",
            "delivery route", "trip route", "route name",
            "origin destination", "distance", "travel time",
            "route list", "route planning"
        ],
        "common_user_intents": [
            "List all routes",
            "Show route details",
            "Routes from city X to Y",
            "Distance between locations",
            "Route master data"
        ],
        "important_columns": ["routeName", "origin", "destination", "distanceKm", "estimatedHours"],
        "business_metrics": ["distanceKm", "estimatedHours"],
        "common_filters": ["isActive"],
        "common_groupby": [],
    },
    "tbl_SaleInvoiceDetail": {
        "display_name": "Sale Invoice Details",
        "domain": "Sales",
        "module": "Sales Management",
        "description": "Line items for sale invoices capturing product, quantity, rate, discount, tax breakup (SGST/CGST/IGST), and line total. Core sales transaction detail.",
        "search_weight": 8, "priority": "High",
        "search_keywords": [
            "sale invoice detail", "sale invoice line", "invoice detail",
            "invoice line", "invoice item", "sale detail",
            "sale line item", "product on invoice",
            "invoice product detail", "sale product detail"
        ],
        "common_user_intents": [
            "Show invoice line items for invoice X",
            "Products sold in invoice Y",
            "Invoice detail by product",
            "Line items with quantities and rates",
            "Tax breakup for invoice Z"
        ],
        "important_columns": ["invoiceId", "productId", "quantity", "rate", "discount", "taxAmount", "lineTotal"],
        "business_metrics": ["quantity", "rate", "discount", "taxAmount", "lineTotal"],
        "common_filters": ["invoiceId", "productId"],
        "common_groupby": ["productId"],
    },
    "tbl_SaleInvoiceHeader": {
        "display_name": "Sale Invoices",
        "domain": "Sales",
        "module": "Sales Management",
        "description": "Master sales invoice records with dealer, distributor, consignee references, payment terms, transport details (vehicle, transporter, LR), and full tax breakup (basic, taxable, SGST, CGST, IGST, freight, loading, unloading, grand total). Core revenue recognition table.",
        "search_weight": 10, "priority": "High",
        "search_keywords": [
            "invoice", "invoices", "sale invoice", "sale invoices",
            "sales invoice", "bill", "bills", "tax invoice",
            "dealer invoice", "grand total", "total sales",
            "revenue", "billing", "invoice number",
            "invoice date", "invoice details", "invoice list",
            "invoice amount", "invoice status",
            "customer invoice", "consignee invoice",
            "sgst", "cgst", "igst", "tax breakup",
            "dashboard", "business dashboard", "sales dashboard",
            "pnl", "profit and loss", "p&l", "profit loss"
        ],
        "common_user_intents": [
            "Show invoices for dealer X",
            "Total sales this month",
            "Invoices pending confirmation",
            "Grand total of invoice Y",
            "Invoices by date range",
            "Get me total invoices",
            "Total revenue",
            "Sales by customer",
            "Invoice details for invoice number X",
            "Pending invoices list"
        ],
        "important_columns": ["invoiceNo", "invoiceDate", "dealerOrgId", "consigneeId", "distributorOrgId", "grandTotal", "taxableAmount", "statusId"],
        "business_metrics": ["basicAmount", "taxableAmount", "sgstAmount", "cgstAmount", "igstAmount", "freightAmount", "grandTotal"],
        "common_filters": ["dealerOrgId", "consigneeId", "distributorOrgId", "statusId", "invoiceDate"],
        "common_groupby": ["invoiceDate", "dealerOrgId", "statusId"],
    },
    "tbl_SaleOrder": {
        "display_name": "Sale Orders",
        "domain": "Sales",
        "module": "Sales Management",
        "description": "Customer/dealer order records capturing organization, total quantity, total amount, delivery date, and status. Represents confirmed demand that triggers the fulfillment pipeline through invoicing and delivery.",
        "search_weight": 7, "priority": "High",
        "search_keywords": [
            "sale order", "sale orders", "sales order", "sales orders",
            "so", "so list", "customer order", "dealer order",
            "order", "orders", "order list", "order details",
            "order number", "order date", "order status",
            "demand", "booking order"
        ],
        "common_user_intents": [
            "Show open sale orders",
            "Orders for customer X",
            "Total order value this quarter",
            "Orders due for delivery today",
            "Pending sale orders",
            "Sale order details"
        ],
        "important_columns": ["soNo", "soDate", "organizationId", "totalQty", "totalAmount", "deliveryDate", "statusId"],
        "business_metrics": ["totalQty", "totalAmount"],
        "common_filters": ["organizationId", "statusId", "soDate", "deliveryDate"],
        "common_groupby": ["soDate", "statusId"],
    },
    "tbl_SaleOrderDetail": {
        "display_name": "Sale Order Details",
        "domain": "Sales",
        "module": "Sales Management",
        "description": "Line items for sale orders with product, quantity, rate, and amount. Each row represents one product in a customer order.",
        "search_weight": 6, "priority": "Medium",
        "search_keywords": [
            "sale order detail", "order detail", "order line",
            "order item", "so detail", "so line item",
            "product on order", "order product detail"
        ],
        "common_user_intents": [
            "Show order line items for order X",
            "Products in order Y",
            "Order detail by product"
        ],
        "important_columns": ["saleOrderId", "productId", "quantity", "rate", "amount"],
        "business_metrics": ["quantity", "rate", "amount"],
        "common_filters": ["saleOrderId", "productId"],
        "common_groupby": ["productId"],
    },
    "tbl_SaleReturn": {
        "display_name": "Sale Returns",
        "domain": "Sales",
        "module": "Sales Management",
        "description": "Customer/dealer return records for products returned due to damage, quality issues, or excess stock. Triggers credit note generation and inventory adjustment.",
        "search_weight": 6, "priority": "Medium",
        "search_keywords": [
            "sale return", "sale returns", "sales return",
            "customer return", "dealer return", "product return",
            "return", "returns", "return note", "return list",
            "return details", "return bill"
        ],
        "common_user_intents": [
            "Show sale returns this month",
            "Returns from customer X",
            "Total return value",
            "Return details for return Y",
            "Returns by product"
        ],
        "important_columns": ["returnNo", "returnDate", "organizationId", "totalQty", "totalAmount", "reason"],
        "business_metrics": ["totalQty", "totalAmount"],
        "common_filters": ["organizationId", "returnDate"],
        "common_groupby": ["returnDate"],
    },
    "tbl_StockLedger": {
        "display_name": "Stock Ledger",
        "domain": "Inventory",
        "module": "Inventory Management",
        "description": "Running stock ledger tracking every inventory movement (inward/outward) with opening balance, quantity in, quantity out, and closing balance per product per warehouse.",
        "search_weight": 9, "priority": "High",
        "search_keywords": [
            "stock ledger", "stock ledger", "inventory ledger",
            "stock movement", "stock statement", "stock report",
            "opening stock", "closing stock", "stock balance",
            "inward", "outward", "stock in", "stock out",
            "current stock", "available stock", "stock summary",
            "stock position", "inventory position",
            "dashboard", "inventory dashboard", "stock dashboard"
        ],
        "common_user_intents": [
            "Show current stock for product X",
            "Stock ledger this month",
            "Opening and closing stock",
            "Stock movement for product Y",
            "Current inventory position",
            "Stock balance by warehouse"
        ],
        "important_columns": ["productId", "warehouseId", "openingQty", "qtyIn", "qtyOut", "closingQty", "transactionDate"],
        "business_metrics": ["openingQty", "qtyIn", "qtyOut", "closingQty"],
        "common_filters": ["productId", "warehouseId", "transactionDate"],
        "common_groupby": ["warehouseId", "transactionDate"],
    },
    "tbl_StockTransfer": {
        "display_name": "Stock Transfers",
        "domain": "Inventory",
        "module": "Inventory Management",
        "description": "Inter-warehouse stock transfer records. Tracks goods moved from one warehouse to another with quantities, transfer date, and approval status.",
        "search_weight": 6, "priority": "Medium",
        "search_keywords": [
            "stock transfer", "stock transfers", "warehouse transfer",
            "inter warehouse", "transfer", "transfers",
            "stock movement", "material transfer", "godown transfer",
            "transfer note", "transfer list"
        ],
        "common_user_intents": [
            "Show stock transfers this month",
            "Transfer from warehouse X to Y",
            "Pending stock transfers",
            "Transfer details",
            "Stock transfer list"
        ],
        "important_columns": ["transferNo", "fromWarehouseId", "toWarehouseId", "productId", "quantity", "transferDate"],
        "business_metrics": ["quantity"],
        "common_filters": ["fromWarehouseId", "toWarehouseId", "transferDate"],
        "common_groupby": ["fromWarehouseId", "toWarehouseId"],
    },
    "tbl_TDSDeduction": {
        "display_name": "TDS Deductions",
        "domain": "Compliance",
        "module": "Tax Compliance",
        "description": "Tax Deducted at Source (TDS) records for vendor payments. Captures TDS section, rate, deducted amount, and PAN for compliance filing.",
        "search_weight": 5, "priority": "Medium",
        "search_keywords": [
            "tds", "tds deduction", "tds deductions", "tax deducted",
            "tds amount", "tds rate", "tds section",
            "tds record", "tds entry", "tds detail",
            "tds certificate", "form 26q"
        ],
        "common_user_intents": [
            "Show TDS deductions this month",
            "TDS for vendor X",
            "Total TDS deducted",
            "TDS by section",
            "TDS deduction details"
        ],
        "important_columns": ["organizationId", "tdsSection", "tdsRate", "deductedAmount", "paymentId"],
        "business_metrics": ["deductedAmount"],
        "common_filters": ["organizationId", "tdsSection", "deductionDate"],
        "common_groupby": ["tdsSection"],
    },
    "tbl_TripSheet": {
        "display_name": "Trip Sheets",
        "domain": "Logistics",
        "module": "Fleet Management",
        "description": "Trip/dispatch records linking vehicle, driver, route, and deliveries. Tracks trip start/end, distance covered, fuel used, and toll charges.",
        "search_weight": 7, "priority": "High",
        "search_keywords": [
            "trip sheet", "trip sheets", "trip", "trips",
            "dispatch", "vehicle trip", "trip details",
            "trip record", "trip list", "route trip",
            "delivery trip", "transport trip", "fleet trip",
            "vehicle dispatch", "trip report"
        ],
        "common_user_intents": [
            "Show trips today",
            "Trip details for trip X",
            "Trips by vehicle Y",
            "Pending trips",
            "Trip report this week",
            "Trips by driver"
        ],
        "important_columns": ["tripNo", "tripDate", "vehicleId", "driverId", "routeId", "startKm", "endKm", "fuelUsed"],
        "business_metrics": ["distanceKm", "fuelUsed", "tollCharges", "totalTripCost"],
        "common_filters": ["vehicleId", "driverId", "tripDate"],
        "common_groupby": ["tripDate", "vehicleId"],
    },
    "tbl_UserMaster": {
        "display_name": "System Users",
        "domain": "System",
        "module": "System Administration",
        "description": "Application user accounts with login credentials, roles, and module access permissions. Controls who can access which parts of the system.",
        "search_weight": 4, "priority": "Medium",
        "search_keywords": [
            "user", "users", "user master", "system user", "system users",
            "login", "user account", "user accounts",
            "username", "user id", "user role",
            "admin", "operator", "active user"
        ],
        "common_user_intents": [
            "List all users",
            "Show user details",
            "Active users",
            "User roles",
            "Who logged in recently"
        ],
        "important_columns": ["userName", "userRole", "employeeId", "lastLogin"],
        "business_metrics": [],
        "common_filters": ["isActive", "userRole"],
        "common_groupby": ["userRole"],
    },
    "tbl_VehicleMaster": {
        "display_name": "Vehicles",
        "domain": "Logistics",
        "module": "Fleet Management",
        "description": "Vehicle master records with registration number, type, capacity, insurance, and fitness certificate details. Used in trip sheets and delivery tracking.",
        "search_weight": 5, "priority": "Medium",
        "search_keywords": [
            "vehicle", "vehicles", "vehicle master", "vehicle list",
            "truck", "lorry", "tempo", "carrier",
            "registration number", "vehicle number", "vehicle type",
            "fleet", "fleet master", "vehicle details"
        ],
        "common_user_intents": [
            "List all vehicles",
            "Show vehicle details",
            "Vehicle registration number X",
            "Active vehicles",
            "Vehicle capacity details"
        ],
        "important_columns": ["vehicleNo", "vehicleType", "capacity", "insuranceExpiry"],
        "business_metrics": ["capacity"],
        "common_filters": ["isActive", "vehicleType"],
        "common_groupby": ["vehicleType"],
    },
    "tbl_VendorEvaluation": {
        "display_name": "Vendor Evaluations",
        "domain": "Purchase",
        "module": "Purchase Management",
        "description": "Vendor performance evaluation records scoring suppliers on quality, delivery, pricing, and service. Used for vendor ranking and selection decisions.",
        "search_weight": 5, "priority": "Medium",
        "search_keywords": [
            "vendor evaluation", "vendor evaluations", "supplier evaluation",
            "vendor rating", "supplier rating", "vendor score",
            "vendor performance", "supplier performance",
            "evaluation", "rating", "score card"
        ],
        "common_user_intents": [
            "Show vendor evaluations",
            "Vendor performance scores",
            "Top rated vendors",
            "Evaluation for vendor X",
            "Vendor rating by criteria"
        ],
        "important_columns": ["organizationId", "qualityScore", "deliveryScore", "overallScore"],
        "business_metrics": ["qualityScore", "deliveryScore", "pricingScore", "overallScore"],
        "common_filters": ["organizationId"],
        "common_groupby": [],
    },
    "tbl_Warehouse": {
        "display_name": "Warehouses",
        "domain": "Inventory",
        "module": "Inventory Management",
        "description": "Warehouse/godown master with location, capacity, and in-charge details. Each warehouse maintains independent stock ledgers.",
        "search_weight": 6, "priority": "Medium",
        "search_keywords": [
            "warehouse", "warehouses", "godown", "godowns",
            "storage", "depot", "distribution center",
            "warehouse master", "warehouse list", "warehouse name",
            "location", "storage location", "stock location"
        ],
        "common_user_intents": [
            "List all warehouses",
            "Show warehouse details",
            "Stock in warehouse X",
            "Warehouse locations",
            "Warehouse capacity"
        ],
        "important_columns": ["warehouseName", "warehouseCode", "location", "capacity", "inchargeId"],
        "business_metrics": ["capacity"],
        "common_filters": ["isActive"],
        "common_groupby": [],
    },
}
 
# Column alias/role map: (table, column) -> aliases, role, importance, description
COLUMN_META = {
    ("dim_OrgType", "orgTypeCode"): {"aliases": ["type code", "org code", "type short"], "role": "identifier", "importance": "high", "description": "Short code for organization type (e.g., DLR, DIST, VND)"},
    ("dim_OrgType", "orgTypeName"): {"aliases": ["type name", "org type name", "type description"], "role": "dimension", "importance": "high", "description": "Full name of organization type (e.g., Dealer, Distributor)"},
    ("dim_OrgType", "description"): {"aliases": ["type detail", "notes"], "role": "description", "importance": "low", "description": "Detailed description of the organization type"},
    ("dim_PaymentTerm", "termCode"): {"aliases": ["terms code", "payment code"], "role": "identifier", "importance": "high", "description": "Short code for payment term"},
    ("dim_PaymentTerm", "termName"): {"aliases": ["terms name", "payment name", "payment description"], "role": "dimension", "importance": "high", "description": "Full name of payment term (e.g., Net 30, Immediate)"},
    ("dim_PaymentTerm", "dueDays"): {"aliases": ["days due", "credit days", "payment days", "net days"], "role": "metric", "importance": "high", "description": "Number of days until payment is due after invoice date"},
    ("dim_Status", "statusCategory"): {"aliases": ["category", "status type", "module"], "role": "dimension", "importance": "high", "description": "Which module this status belongs to (Order, Invoice, Delivery, etc.)"},
    ("dim_Status", "statusCode"): {"aliases": ["code", "status code"], "role": "identifier", "importance": "high", "description": "Short code for the status"},
    ("dim_Status", "statusName"): {"aliases": ["name", "status name", "status label"], "role": "dimension", "importance": "high", "description": "Display name of the status (e.g., Pending, Approved, Dispatched)"},
    ("dim_TaxRate", "taxCode"): {"aliases": ["tax code", "gst code"], "role": "identifier", "importance": "high", "description": "Short code for tax rate"},
    ("dim_TaxRate", "taxName"): {"aliases": ["tax name", "gst name"], "role": "dimension", "importance": "high", "description": "Full name of tax rate"},
    ("dim_TaxRate", "sgstRate"): {"aliases": ["sgst", "sgst percentage", "state tax"], "role": "metric", "importance": "high", "description": "State GST percentage"},
    ("dim_TaxRate", "cgstRate"): {"aliases": ["cgst", "cgst percentage", "central tax"], "role": "metric", "importance": "high", "description": "Central GST percentage"},
    ("dim_TaxRate", "igstRate"): {"aliases": ["igst", "igst percentage", "integrated tax"], "role": "metric", "importance": "high", "description": "Integrated GST percentage for inter-state transactions"},
    ("dim_UOM", "uomCode"): {"aliases": ["unit code", "uom short"], "role": "identifier", "importance": "high", "description": "Short code for unit of measurement (KG, MT, LTR, PCS)"},
    ("dim_UOM", "uomName"): {"aliases": ["unit name", "uom full", "measurement name"], "role": "dimension", "importance": "high", "description": "Full name of unit of measurement"},
    ("dmn_City", "cityName"): {"aliases": ["city", "city name", "town", "place"], "role": "dimension", "importance": "high", "description": "Name of the city"},
    ("dmn_City", "stateId"): {"aliases": ["state", "state reference"], "role": "foreign_key", "importance": "medium", "description": "Reference to the state this city belongs to"},
    ("dmn_City", "pinCode"): {"aliases": ["pin", "pincode", "postal code", "zip code"], "role": "identifier", "importance": "medium", "description": "PIN/ZIP postal code for the city"},
    ("dmn_Country", "countryCode"): {"aliases": ["country code", "nation code", "iso code"], "role": "identifier", "importance": "high", "description": "ISO country code (IN, US, etc.)"},
    ("dmn_Country", "countryName"): {"aliases": ["country", "country name", "nation"], "role": "dimension", "importance": "high", "description": "Full name of the country"},
    ("dmn_State", "stateCode"): {"aliases": ["state code", "gst state code"], "role": "identifier", "importance": "high", "description": "State code used for GST and identification"},
    ("dmn_State", "stateName"): {"aliases": ["state", "state name", "region"], "role": "dimension", "importance": "high", "description": "Full name of the state"},
    ("tbl_AccountGroup", "groupName"): {"aliases": ["group", "group name", "account group name"], "role": "dimension", "importance": "high", "description": "Name of the account group in chart of accounts"},
    ("tbl_AccountGroup", "parentId"): {"aliases": ["parent", "parent group", "parent id"], "role": "foreign_key", "importance": "medium", "description": "Reference to parent account group for hierarchy"},
    ("tbl_AccountGroup", "groupType"): {"aliases": ["type", "group type", "account type"], "role": "dimension", "importance": "high", "description": "Type of group (Asset, Liability, Income, Expense)"},
    ("tbl_AccountLedger", "ledgerName"): {"aliases": ["ledger", "account name", "account head"], "role": "dimension", "importance": "high", "description": "Name of the ledger account"},
    ("tbl_AccountLedger", "ledgerCode"): {"aliases": ["account code", "gl code", "ledger code"], "role": "identifier", "importance": "high", "description": "GL code for the ledger"},
    ("tbl_AccountLedger", "groupId"): {"aliases": ["group", "account group"], "role": "foreign_key", "importance": "medium", "description": "Reference to account group"},
    ("tbl_AccountLedger", "openingBalance"): {"aliases": ["opening bal", "opening", "balance"], "role": "metric", "importance": "high", "description": "Opening balance amount for the ledger"},
    ("tbl_Attendance", "employeeId"): {"aliases": ["employee", "emp", "staff"], "role": "foreign_key", "importance": "high", "description": "Reference to employee record"},
    ("tbl_Attendance", "attendanceDate"): {"aliases": ["date", "attendance date", "day", "present date"], "role": "dimension", "importance": "high", "description": "Date of attendance record"},
    ("tbl_Attendance", "checkInTime"): {"aliases": ["check in", "punch in", "in time", "start time"], "role": "dimension", "importance": "medium", "description": "Time employee checked in"},
    ("tbl_Attendance", "checkOutTime"): {"aliases": ["check out", "punch out", "out time", "end time"], "role": "dimension", "importance": "medium", "description": "Time employee checked out"},
    ("tbl_Attendance", "workHours"): {"aliases": ["hours", "work hours", "total hours", "working hours"], "role": "metric", "importance": "high", "description": "Total working hours for the day"},
    ("tbl_Attendance", "overtimeHours"): {"aliases": ["overtime", "ot", "extra hours", "over time"], "role": "metric", "importance": "medium", "description": "Overtime hours beyond regular working hours"},
    ("tbl_Attendance", "status"): {"aliases": ["attendance status", "present absent", "attendance type"], "role": "dimension", "importance": "high", "description": "Attendance status (Present, Absent, Half Day, Leave)"},
    ("tbl_Booking", "bookingNo"): {"aliases": ["booking number", "booking id", "booking ref"], "role": "identifier", "importance": "high", "description": "Unique booking reference number"},
    ("tbl_Booking", "bookingDate"): {"aliases": ["date", "booking date", "order date"], "role": "dimension", "importance": "high", "description": "Date when booking was created"},
    ("tbl_Booking", "organizationId"): {"aliases": ["customer", "dealer", "org", "party", "organization"], "role": "foreign_key", "importance": "high", "description": "Reference to customer/dealer organization"},
    ("tbl_Booking", "totalAmount"): {"aliases": ["amount", "total", "booking amount", "value"], "role": "metric", "importance": "high", "description": "Total booking amount"},
    ("tbl_BookingDelivery", "bookingId"): {"aliases": ["booking", "booking ref", "booking reference"], "role": "foreign_key", "importance": "high", "description": "Reference to parent booking"},
    ("tbl_BookingDelivery", "deliveryDate"): {"aliases": ["date", "delivery date", "dispatch date"], "role": "dimension", "importance": "high", "description": "Scheduled or actual delivery date"},
    ("tbl_BookingDelivery", "deliveredQty"): {"aliases": ["quantity", "delivered qty", "delivery qty"], "role": "metric", "importance": "high", "description": "Quantity actually delivered"},
    ("tbl_CreditDebitNote", "noteNo"): {"aliases": ["note number", "cdn number", "dbn number", "note ref"], "role": "identifier", "importance": "high", "description": "Credit/debit note reference number"},
    ("tbl_CreditDebitNote", "noteDate"): {"aliases": ["date", "note date", "issue date"], "role": "dimension", "importance": "high", "description": "Date the note was issued"},
    ("tbl_CreditDebitNote", "noteType"): {"aliases": ["type", "note type", "credit debit"], "role": "dimension", "importance": "high", "description": "Type of note (Credit or Debit)"},
    ("tbl_CreditDebitNote", "amount"): {"aliases": ["note amount", "value"], "role": "metric", "importance": "high", "description": "Amount of the credit/debit note"},
    ("tbl_Department", "departmentName"): {"aliases": ["department", "dept name", "dept"], "role": "dimension", "importance": "high", "description": "Name of the department"},
    ("tbl_Designation", "designationName"): {"aliases": ["designation", "job title", "title", "position"], "role": "dimension", "importance": "high", "description": "Name of the job designation/title"},
    ("tbl_DriverMaster", "driverName"): {"aliases": ["driver", "driver name", "chauffeur"], "role": "dimension", "importance": "high", "description": "Name of the driver"},
    ("tbl_DriverMaster", "licenseNo"): {"aliases": ["license", "licence", "driving license", "dl number"], "role": "identifier", "importance": "high", "description": "Driving license number"},
    ("tbl_DriverMaster", "mobileNo"): {"aliases": ["mobile", "phone", "contact", "driver phone"], "role": "dimension", "importance": "medium", "description": "Driver mobile/contact number"},
    ("tbl_Employee", "empCode"): {"aliases": ["employee code", "emp id", "employee id", "staff code", "worker code"], "role": "identifier", "importance": "high", "description": "Unique employee identification code"},
    ("tbl_Employee", "firstName"): {"aliases": ["first name", "name", "employee name", "staff name"], "role": "dimension", "importance": "high", "description": "Employee first name"},
    ("tbl_Employee", "lastName"): {"aliases": ["last name", "surname", "family name"], "role": "dimension", "importance": "medium", "description": "Employee last name/surname"},
    ("tbl_Employee", "departmentId"): {"aliases": ["department", "dept", "team"], "role": "foreign_key", "importance": "high", "description": "Reference to department"},
    ("tbl_Employee", "designationId"): {"aliases": ["designation", "job title", "position", "role"], "role": "foreign_key", "importance": "high", "description": "Reference to designation"},
    ("tbl_Employee", "reportingToId"): {"aliases": ["manager", "reports to", "reporting manager", "supervisor"], "role": "foreign_key", "importance": "medium", "description": "Reference to reporting manager (self-referencing)"},
    ("tbl_Employee", "dateOfJoining"): {"aliases": ["joining date", "join date", "doj", "start date"], "role": "dimension", "importance": "medium", "description": "Date employee joined the organization"},
    ("tbl_Employee", "mobileNo"): {"aliases": ["mobile", "phone", "contact", "employee phone"], "role": "dimension", "importance": "medium", "description": "Employee mobile number"},
    ("tbl_Employee", "email"): {"aliases": ["email", "email address", "mail"], "role": "dimension", "importance": "low", "description": "Employee email address"},
    ("tbl_EwayBill", "ewayBillNo"): {"aliases": ["eway number", "eway bill", "bill number"], "role": "identifier", "importance": "high", "description": "E-way bill reference number"},
    ("tbl_EwayBill", "ewayBillDate"): {"aliases": ["eway date", "generated date"], "role": "dimension", "importance": "high", "description": "Date e-way bill was generated"},
    ("tbl_GlobalPurchaseRate", "rate"): {"aliases": ["price", "cost", "buying rate", "purchase rate", "cost price"], "role": "metric", "importance": "high", "description": "Standard purchase rate for the product"},
    ("tbl_GlobalSaleRate", "rate"): {"aliases": ["price", "selling rate", "sale price", "mrp", "list price"], "role": "metric", "importance": "high", "description": "Standard selling rate for the product"},
    ("tbl_GSTReturn", "returnType"): {"aliases": ["type", "return type", "gstr type"], "role": "dimension", "importance": "high", "description": "Type of GST return (GSTR-1, GSTR-3B)"},
    ("tbl_GSTReturn", "returnPeriod"): {"aliases": ["period", "month", "filing period"], "role": "dimension", "importance": "high", "description": "Tax period (month/year) for the return"},
    ("tbl_GSTReturn", "totalTax"): {"aliases": ["tax", "tax amount", "gst amount"], "role": "metric", "importance": "high", "description": "Total tax amount for the return period"},
    ("tbl_InventoryAdjustment", "productId"): {"aliases": ["product", "item", "material"], "role": "foreign_key", "importance": "high", "description": "Reference to product being adjusted"},
    ("tbl_InventoryAdjustment", "adjustmentQty"): {"aliases": ["quantity", "adj qty", "adjusted qty", "variance qty"], "role": "metric", "importance": "high", "description": "Quantity adjusted (positive for gain, negative for loss)"},
    ("tbl_InventoryAdjustment", "reason"): {"aliases": ["reason", "adjustment reason", "remarks"], "role": "dimension", "importance": "medium", "description": "Reason for adjustment (Damage, Expiry, Theft, Correction)"},
    ("tbl_JournalVoucher", "voucherNo"): {"aliases": ["voucher number", "jv number", "journal number"], "role": "identifier", "importance": "high", "description": "Unique journal voucher number"},
    ("tbl_JournalVoucher", "voucherDate"): {"aliases": ["date", "jv date", "journal date", "entry date"], "role": "dimension", "importance": "high", "description": "Date of the journal entry"},
    ("tbl_JournalVoucher", "totalDebit"): {"aliases": ["debit", "total debit", "debit amount"], "role": "metric", "importance": "high", "description": "Total debit amount for the voucher"},
    ("tbl_JournalVoucher", "totalCredit"): {"aliases": ["credit", "total credit", "credit amount"], "role": "metric", "importance": "high", "description": "Total credit amount for the voucher"},
    ("tbl_JournalVoucher", "narration"): {"aliases": ["description", "narration", "remarks", "note"], "role": "description", "importance": "medium", "description": "Narration/description of the journal entry"},
    ("tbl_LeaveApplication", "employeeId"): {"aliases": ["employee", "emp", "staff"], "role": "foreign_key", "importance": "high", "description": "Reference to employee applying for leave"},
    ("tbl_LeaveApplication", "fromDate"): {"aliases": ["start date", "leave from", "from"], "role": "dimension", "importance": "high", "description": "Leave start date"},
    ("tbl_LeaveApplication", "toDate"): {"aliases": ["end date", "leave to", "to"], "role": "dimension", "importance": "high", "description": "Leave end date"},
    ("tbl_LeaveApplication", "days"): {"aliases": ["leave days", "total days", "no of days", "duration"], "role": "metric", "importance": "high", "description": "Total number of leave days"},
    ("tbl_Organization", "orgCode"): {"aliases": ["org code", "party code", "customer code", "dealer code", "vendor code", "company code"], "role": "identifier", "importance": "high", "description": "Unique organization/party code"},
    ("tbl_Organization", "firmName"): {"aliases": ["firm", "company name", "org name", "business name", "party name", "dealer name", "vendor name", "customer name"], "role": "dimension", "importance": "high", "description": "Legal/business name of the organization"},
    ("tbl_Organization", "tradingName"): {"aliases": ["trading name", "trade name", "dba", "display name"], "role": "dimension", "importance": "medium", "description": "Trading/doing-business-as name if different from firm name"},
    ("tbl_Organization", "gstNo"): {"aliases": ["gstin", "gst number", "gst no", "gst registration"], "role": "identifier", "importance": "high", "description": "GST registration number"},
    ("tbl_Organization", "panNo"): {"aliases": ["pan", "pan number", "pan no"], "role": "identifier", "importance": "high", "description": "PAN card number"},
    ("tbl_Organization", "creditLimit"): {"aliases": ["credit", "credit limit", "credit amount", "credit allowed"], "role": "metric", "importance": "high", "description": "Maximum credit amount allowed for this organization"},
    ("tbl_Organization", "orgTypeId"): {"aliases": ["type", "org type", "party type", "organization type", "dealer type", "vendor type"], "role": "foreign_key", "importance": "high", "description": "Reference to organization type (Dealer, Vendor, etc.)"},
    ("tbl_Organization", "cityId"): {"aliases": ["city", "location", "city reference"], "role": "foreign_key", "importance": "medium", "description": "Reference to city"},
    ("tbl_Organization", "paymentTermId"): {"aliases": ["payment terms", "payment term", "terms"], "role": "foreign_key", "importance": "medium", "description": "Reference to payment term"},
    ("tbl_Organization", "contactPerson"): {"aliases": ["contact", "person", "key person", "primary contact"], "role": "dimension", "importance": "medium", "description": "Primary contact person name"},
    ("tbl_Organization", "mobileNo"): {"aliases": ["mobile", "phone", "contact number", "phone number"], "role": "dimension", "importance": "medium", "description": "Primary mobile/contact number"},
    ("tbl_Organization", "email"): {"aliases": ["email", "email address", "mail"], "role": "dimension", "importance": "low", "description": "Primary email address"},
    ("tbl_PaymentMade", "paymentNo"): {"aliases": ["payment number", "payment ref", "receipt number"], "role": "identifier", "importance": "high", "description": "Unique payment reference number"},
    ("tbl_PaymentMade", "paymentDate"): {"aliases": ["date", "payment date", "paid date"], "role": "dimension", "importance": "high", "description": "Date payment was made"},
    ("tbl_PaymentMade", "organizationId"): {"aliases": ["vendor", "supplier", "org", "party", "payee"], "role": "foreign_key", "importance": "high", "description": "Reference to vendor/supplier being paid"},
    ("tbl_PaymentMade", "amount"): {"aliases": ["payment amount", "paid amount", "value"], "role": "metric", "importance": "high", "description": "Amount paid"},
    ("tbl_PaymentMade", "paymentMode"): {"aliases": ["mode", "payment mode", "payment type", "method"], "role": "dimension", "importance": "medium", "description": "Mode of payment (NEFT, RTGS, Cheque, Cash)"},
    ("tbl_PaymentReceived", "receiptNo"): {"aliases": ["receipt number", "receipt ref", "payment number"], "role": "identifier", "importance": "high", "description": "Unique receipt reference number"},
    ("tbl_PaymentReceived", "receiptDate"): {"aliases": ["date", "receipt date", "received date", "collection date"], "role": "dimension", "importance": "high", "description": "Date payment was received"},
    ("tbl_PaymentReceived", "organizationId"): {"aliases": ["customer", "dealer", "org", "party", "payer"], "role": "foreign_key", "importance": "high", "description": "Reference to customer/dealer who paid"},
    ("tbl_PaymentReceived", "amount"): {"aliases": ["receipt amount", "received amount", "collection amount", "value"], "role": "metric", "importance": "high", "description": "Amount received"},
    ("tbl_PaymentReceived", "paymentMode"): {"aliases": ["mode", "payment mode", "payment type", "method"], "role": "dimension", "importance": "medium", "description": "Mode of payment received"},
    ("tbl_PayrollHeader", "payrollMonth"): {"aliases": ["month", "pay month", "salary month"], "role": "dimension", "importance": "high", "description": "Month of the payroll period"},
    ("tbl_PayrollHeader", "payrollYear"): {"aliases": ["year", "pay year", "salary year"], "role": "dimension", "importance": "high", "description": "Year of the payroll period"},
    ("tbl_PayrollHeader", "totalGross"): {"aliases": ["gross", "gross salary", "total gross", "gross pay"], "role": "metric", "importance": "high", "description": "Total gross salary for all employees in this payroll"},
    ("tbl_PayrollHeader", "totalDeductions"): {"aliases": ["deductions", "total deductions", "total deducted"], "role": "metric", "importance": "high", "description": "Total deductions (PF, ESI, TDS) for all employees"},
    ("tbl_PayrollHeader", "totalNet"): {"aliases": ["net", "net pay", "net salary", "total net", "take home"], "role": "metric", "importance": "high", "description": "Total net pay after deductions"},
    ("tbl_ProductMaster", "productCode"): {"aliases": ["code", "item code", "sku", "product id", "material code"], "role": "identifier", "importance": "high", "description": "Unique product/item code"},
    ("tbl_ProductMaster", "productName"): {"aliases": ["name", "item name", "product name", "material name", "item"], "role": "dimension", "importance": "high", "description": "Name of the product"},
    ("tbl_ProductMaster", "categoryId"): {"aliases": ["category", "product category", "item category", "group"], "role": "foreign_key", "importance": "high", "description": "Reference to product category"},
    ("tbl_ProductMaster", "hsnCode"): {"aliases": ["hsn", "hsn code", "harmonized code"], "role": "identifier", "importance": "high", "description": "HSN (Harmonized System of Nomenclature) code for GST"},
    ("tbl_ProductMaster", "gstRate"): {"aliases": ["gst", "tax rate", "gst percentage", "tax"], "role": "metric", "importance": "high", "description": "GST rate applicable to this product"},
    ("tbl_ProductPricing", "rate"): {"aliases": ["price", "selling price", "mrp", "list price", "product rate"], "role": "metric", "importance": "high", "description": "Selling price/rate for the product"},
    ("tbl_ProductPricing", "discountPercent"): {"aliases": ["discount", "disc", "discount %", "percentage discount"], "role": "metric", "importance": "medium", "description": "Discount percentage applicable"},
    ("tbl_PurchaseEnquiry", "enquiryNo"): {"aliases": ["enquiry number", "inquiry number", "enquiry ref"], "role": "identifier", "importance": "high", "description": "Unique purchase enquiry reference number"},
    ("tbl_PurchaseEnquiry", "enquiryDate"): {"aliases": ["date", "enquiry date", "rfq date"], "role": "dimension", "importance": "high", "description": "Date the enquiry was received"},
    ("tbl_PurchaseEnquiry", "organizationId"): {"aliases": ["customer", "dealer", "org", "party", "enquirer"], "role": "foreign_key", "importance": "high", "description": "Reference to organization that made the enquiry"},
    ("tbl_PurchaseInvoice", "invoiceNo"): {"aliases": ["invoice number", "pi number", "vendor invoice"], "role": "identifier", "importance": "high", "description": "Purchase invoice number"},
    ("tbl_PurchaseInvoice", "invoiceDate"): {"aliases": ["date", "invoice date", "bill date"], "role": "dimension", "importance": "high", "description": "Date of the purchase invoice"},
    ("tbl_PurchaseInvoice", "organizationId"): {"aliases": ["vendor", "supplier", "org", "party"], "role": "foreign_key", "importance": "high", "description": "Reference to vendor/supplier"},
    ("tbl_PurchaseInvoice", "totalAmount"): {"aliases": ["amount", "total", "invoice amount", "bill amount", "total bill"], "role": "metric", "importance": "high", "description": "Total invoice amount including taxes"},
    ("tbl_PurchaseOrder", "poNo"): {"aliases": ["po number", "po no", "purchase order number", "order number"], "role": "identifier", "importance": "high", "description": "Purchase order number"},
    ("tbl_PurchaseOrder", "poDate"): {"aliases": ["date", "po date", "order date"], "role": "dimension", "importance": "high", "description": "Date the purchase order was raised"},
    ("tbl_PurchaseOrder", "organizationId"): {"aliases": ["vendor", "supplier", "org", "party"], "role": "foreign_key", "importance": "high", "description": "Reference to vendor/supplier"},
    ("tbl_PurchaseOrder", "totalAmount"): {"aliases": ["amount", "total", "po amount", "order value"], "role": "metric", "importance": "high", "description": "Total purchase order value"},
    ("tbl_PurchaseSchedule", "productId"): {"aliases": ["product", "item", "material"], "role": "foreign_key", "importance": "high", "description": "Reference to product being purchased"},
    ("tbl_PurchaseSchedule", "quantity"): {"aliases": ["qty", "ordered qty", "purchase qty"], "role": "metric", "importance": "high", "description": "Quantity ordered"},
    ("tbl_PurchaseSchedule", "rate"): {"aliases": ["price", "unit rate", "purchase rate"], "role": "metric", "importance": "high", "description": "Unit rate/price"},
    ("tbl_PurchaseSchedule", "amount"): {"aliases": ["total", "line total", "total amount"], "role": "metric", "importance": "high", "description": "Line total (quantity × rate)"},
    ("tbl_SaleInvoiceHeader", "invoiceNo"): {"aliases": ["invoice number", "bill number", "si number", "invoice ref"], "role": "identifier", "importance": "high", "description": "Unique sale invoice number"},
    ("tbl_SaleInvoiceHeader", "invoiceDate"): {"aliases": ["date", "invoice date", "bill date", "sale date"], "role": "dimension", "importance": "high", "description": "Date of the sale invoice"},
    ("tbl_SaleInvoiceHeader", "dealerOrgId"): {"aliases": ["dealer", "customer", "sold to", "buyer"], "role": "foreign_key", "importance": "high", "description": "Reference to dealer/customer who purchased"},
    ("tbl_SaleInvoiceHeader", "consigneeId"): {"aliases": ["consignee", "ship to", "delivery address", "delivery party"], "role": "foreign_key", "importance": "medium", "description": "Reference to consignee (delivery address)"},
    ("tbl_SaleInvoiceHeader", "distributorOrgId"): {"aliases": ["distributor", "distributor party"], "role": "foreign_key", "importance": "medium", "description": "Reference to distributor"},
    ("tbl_SaleInvoiceHeader", "grandTotal"): {"aliases": ["total", "grand total", "invoice total", "total amount", "bill amount", "final amount"], "role": "metric", "importance": "high", "description": "Grand total amount of the invoice"},
    ("tbl_SaleInvoiceHeader", "taxableAmount"): {"aliases": ["taxable", "taxable value", "base amount", "net amount"], "role": "metric", "importance": "high", "description": "Amount before tax"},
    ("tbl_SaleInvoiceHeader", "sgstAmount"): {"aliases": ["sgst", "state tax amount"], "role": "metric", "importance": "medium", "description": "SGST amount"},
    ("tbl_SaleInvoiceHeader", "cgstAmount"): {"aliases": ["cgst", "central tax amount"], "role": "metric", "importance": "medium", "description": "CGST amount"},
    ("tbl_SaleInvoiceHeader", "igstAmount"): {"aliases": ["igst", "integrated tax amount"], "role": "metric", "importance": "medium", "description": "IGST amount for inter-state sales"},
    ("tbl_SaleOrder", "soNo"): {"aliases": ["so number", "order number", "sale order number", "order ref"], "role": "identifier", "importance": "high", "description": "Sale order number"},
    ("tbl_SaleOrder", "soDate"): {"aliases": ["date", "order date", "sale date"], "role": "dimension", "importance": "high", "description": "Date the sale order was placed"},
    ("tbl_SaleOrder", "organizationId"): {"aliases": ["customer", "dealer", "org", "party", "buyer"], "role": "foreign_key", "importance": "high", "description": "Reference to customer/dealer"},
    ("tbl_SaleOrder", "totalQty"): {"aliases": ["quantity", "qty", "total quantity", "order quantity"], "role": "metric", "importance": "high", "description": "Total quantity ordered"},
    ("tbl_SaleOrder", "totalAmount"): {"aliases": ["amount", "total", "order amount", "order value"], "role": "metric", "importance": "high", "description": "Total order amount"},
    ("tbl_SaleReturn", "returnNo"): {"aliases": ["return number", "return ref", "credit note number"], "role": "identifier", "importance": "high", "description": "Sale return reference number"},
    ("tbl_SaleReturn", "returnDate"): {"aliases": ["date", "return date"], "role": "dimension", "importance": "high", "description": "Date of the return"},
    ("tbl_SaleReturn", "organizationId"): {"aliases": ["customer", "dealer", "org", "party", "returner"], "role": "foreign_key", "importance": "high", "description": "Reference to customer/dealer returning goods"},
    ("tbl_SaleReturn", "totalQty"): {"aliases": ["quantity", "qty", "returned qty", "return quantity"], "role": "metric", "importance": "high", "description": "Total quantity returned"},
    ("tbl_SaleReturn", "totalAmount"): {"aliases": ["amount", "total", "return amount", "credit amount"], "role": "metric", "importance": "high", "description": "Total return amount"},
    ("tbl_StockLedger", "productId"): {"aliases": ["product", "item", "material"], "role": "foreign_key", "importance": "high", "description": "Reference to product"},
    ("tbl_StockLedger", "warehouseId"): {"aliases": ["warehouse", "godown", "location", "depot"], "role": "foreign_key", "importance": "high", "description": "Reference to warehouse"},
    ("tbl_StockLedger", "openingQty"): {"aliases": ["opening", "opening stock", "opening balance", "opening quantity"], "role": "metric", "importance": "high", "description": "Opening stock quantity for the period"},
    ("tbl_StockLedger", "qtyIn"): {"aliases": ["inward", "received", "stock in", "quantity in", "incoming"], "role": "metric", "importance": "high", "description": "Quantity received/inward during the period"},
    ("tbl_StockLedger", "qtyOut"): {"aliases": ["outward", "issued", "stock out", "quantity out", "outgoing", "dispatched"], "role": "metric", "importance": "high", "description": "Quantity issued/outward during the period"},
    ("tbl_StockLedger", "closingQty"): {"aliases": ["closing", "closing stock", "current stock", "available stock", "balance", "closing quantity"], "role": "metric", "importance": "high", "description": "Closing stock quantity"},
    ("tbl_StockLedger", "transactionDate"): {"aliases": ["date", "transaction date", "movement date", "stock date"], "role": "dimension", "importance": "high", "description": "Date of stock movement"},
    ("tbl_TripSheet", "tripNo"): {"aliases": ["trip number", "trip id", "dispatch number"], "role": "identifier", "importance": "high", "description": "Unique trip/dispatch number"},
    ("tbl_TripSheet", "tripDate"): {"aliases": ["date", "trip date", "dispatch date"], "role": "dimension", "importance": "high", "description": "Date of the trip"},
    ("tbl_TripSheet", "vehicleId"): {"aliases": ["vehicle", "truck", "lorry", "vehicle number"], "role": "foreign_key", "importance": "high", "description": "Reference to vehicle"},
    ("tbl_TripSheet", "driverId"): {"aliases": ["driver", "chauffeur"], "role": "foreign_key", "importance": "high", "description": "Reference to driver"},
    ("tbl_TripSheet", "routeId"): {"aliases": ["route", "path"], "role": "foreign_key", "importance": "medium", "description": "Reference to route"},
    ("tbl_Warehouse", "warehouseName"): {"aliases": ["warehouse", "godown", "depot", "storage", "location"], "role": "dimension", "importance": "high", "description": "Name of the warehouse/godown"},
    ("tbl_Warehouse", "warehouseCode"): {"aliases": ["warehouse code", "godown code", "location code"], "role": "identifier", "importance": "high", "description": "Short code for the warehouse"},
    ("tbl_Warehouse", "capacity"): {"aliases": ["max capacity", "storage capacity", "capacity units"], "role": "metric", "importance": "medium", "description": "Maximum storage capacity"},
}
 
# All known isActive columns should get these aliases
ACTIVE_ALIASES = {"aliases": ["active", "enabled", "is active", "is enabled", "active flag", "status"], "role": "status", "importance": "low", "description": "Whether this record is active/enabled"}
 
 
def generate():
    tables_dir = Path("knowledge_base/tables")
    cols_dir = Path("knowledge_base/columns")
 
    with open("schema_dump.json") as f:
        schema = json.load(f)
 
    db_tables = schema["tables"]
    db_fks = schema["foreign_keys"]
 
    # Build FK map
    fk_map = {}
    for parent, pcol, ref, rcol in db_fks:
        fk_map.setdefault(parent, []).append({"col": pcol, "ref_table": ref, "ref_col": rcol})
 
    # Build reverse FK map (what references this table)
    rev_fk_map = {}
    for parent, pcol, ref, rcol in db_fks:
        rev_fk_map.setdefault(ref, []).append({"from_table": parent, "from_col": pcol, "to_col": rcol})
 
    stats = {"tables": 0, "keywords_total": 0, "intents_total": 0}
 
    for table_name, columns in sorted(db_tables.items()):
        meta = TABLE_META.get(table_name, {})
 
        # Build foreign_keys
        foreign_keys = []
        for fk in fk_map.get(table_name, []):
            foreign_keys.append({
                "name": fk["col"],
                "references": f"{fk['ref_table']}.{fk['ref_col']}"
            })
 
        # Build related_tables
        related = set()
        for fk in fk_map.get(table_name, []):
            related.add(fk["ref_table"])
        for rev in rev_fk_map.get(table_name, []):
            related.add(rev["from_table"])
 
        # Build important_columns from COLUMN_META
        important_cols = []
        for col in columns:
            cname = col["name"]
            cm = COLUMN_META.get((table_name, cname), {})
            if cm.get("importance") == "high":
                important_cols.append(cname)
 
        # Build table YAML
        table_yaml = {
            "table_name": table_name,
            "display_name": meta.get("display_name", table_name),
            "domain": meta.get("domain", ""),
            "module": meta.get("module", ""),
            "description": meta.get("description", f"Table {table_name} from database."),
            "primary_key": next((c["name"] for c in columns if c.get("is_pk")), ""),
            "estimated_rows": 0,
            "search_weight": meta.get("search_weight", 5),
            "priority": meta.get("priority", "Medium"),
            "search_keywords": meta.get("search_keywords", []),
            "common_user_intents": meta.get("common_user_intents", []),
            "foreign_keys": foreign_keys,
            "related_tables": sorted(related),
            "important_columns": important_cols or meta.get("important_columns", []),
            "business_metrics": meta.get("business_metrics", []),
            "common_filters": meta.get("common_filters", []),
            "common_groupby": meta.get("common_groupby", []),
            "columns": [],
        }
 
        # Build column entries
        col_entries = []
        for col in columns:
            cname = col["name"]
            cm = COLUMN_META.get((table_name, cname), {})
 
            # Handle isActive uniformly
            if cname == "isActive":
                cm = ACTIVE_ALIASES.copy()
 
            col_entries.append({
                "name": cname,
                "display_name": cname,
                "datatype": col["type"],
                "description": cm.get("description", f"{cname} column in {table_name}"),
                "nullable": col["nullable"] == "YES",
                "role": cm.get("role", "attribute"),
                "importance": cm.get("importance", "medium"),
                "is_primary_key": col.get("is_pk", False),
                "is_join_key": cname in [fk["col"] for fk in fk_map.get(table_name, [])],
                "filterable": cm.get("role") in ("foreign_key", "dimension", "identifier", "status") or cname in ("isActive", "statusId"),
                "groupable": cm.get("role") in ("dimension", "identifier", "foreign_key", "status"),
                "aggregatable": cm.get("role") == "metric",
                "aggregations_allowed": ["SUM", "AVG", "MIN", "MAX"] if cm.get("role") == "metric" else [],
                "aliases": cm.get("aliases", []),
            })
 
        table_yaml["columns"] = col_entries
 
        # Write table YAML
        with open(tables_dir / f"{table_name}.yaml", "w", encoding="utf-8") as f:
            yaml.dump(table_yaml, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
 
        # Write column YAML
        col_yaml = {"columns": col_entries}
        with open(cols_dir / f"{table_name}.yaml", "w", encoding="utf-8") as f:
            yaml.dump(col_yaml, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
 
        stats["tables"] += 1
        stats["keywords_total"] += len(meta.get("search_keywords", []))
        stats["intents_total"] += len(meta.get("common_user_intents", []))
        print(f"  [{table_name}] keywords={len(meta.get('search_keywords', []))}, intents={len(meta.get('common_user_intents', []))}, cols={len(col_entries)}")
 
    print(f"\nDone: {stats['tables']} tables, {stats['keywords_total']} keywords, {stats['intents_total']} intents")
 
 
if __name__ == "__main__":
    generate()
 
