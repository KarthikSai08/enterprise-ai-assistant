"""Structured bootstrap data for regenerating hand-written knowledge base files."""

DOMAINS_DATA = [
    {
        'domain': 'Sales',
        'description': 'Customer-facing sales transactions including booking, invoicing, order management, delivery tracking, and sale returns',
        'primary_tables': [
            'tbl_SaleInvoiceHeader',
            'tbl_SaleInvoiceDetail',
            'tbl_SaleOrder',
            'tbl_SaleOrderDetail',
            'tbl_Booking',
            'tbl_BookingDelivery',
            'tbl_SaleReturn'
        ],
        'support_tables': [
            'tbl_ProductMaster',
            'tbl_Organization',
            'tbl_ProductGrade',
            'dim_Status',
            'dim_PaymentTerm',
            'dim_UOM',
            'dim_TaxRate',
            'tbl_ProductPricing'
        ],
        'trigger_keywords': [
            'sale, sales, invoice, invoice number, billing, booking, order, customer order',
            'sold, revenue, dealer invoice, sell, sold to, sale return, sales return',
            'dispatch, delivery, consignment, receivable, pnl, profit and loss, dashboard',
            'business dashboard, sales dashboard, p&l'
        ],
        'anti_keywords': [
            'purchase, vendor, supplier, buy, procurement, payroll, hr, attendance, quality',
            'stock transfer, physical inventory'
        ]
    },
    {
        'domain': 'Purchase',
        'description': 'Procurement and supply chain operations including purchase enquiries, purchase orders, purchase invoices, scheduling, and vendor evaluation',
        'primary_tables': [
            'tbl_PurchaseOrder',
            'tbl_PurchaseInvoice',
            'tbl_PurchaseEnquiry',
            'tbl_PurchaseSchedule',
            'tbl_VendorEvaluation'
        ],
        'support_tables': [
            'tbl_ProductMaster',
            'tbl_Organization',
            'tbl_ProductGrade',
            'dim_Status',
            'dim_UOM',
            'dim_PaymentTerm'
        ],
        'trigger_keywords': [
            'purchase, purchase order, po, procurement, buy, bought, vendor, supplier',
            'vendor evaluation, purchase invoice, purchase enquiry, enquiry, indent',
            'material requirement, supply, supply order, purchase schedule, delivery schedule',
            'quotation, rfq, grn, purchase return, rate contract, goods receipt'
        ],
        'anti_keywords': [
            'sale, invoice, customer, booking, hr, attendance, payroll, quality'
        ]
    },
    {
        'domain': 'Inventory',
        'description': 'Warehouse and stock management including stock ledger, transfers between warehouses, physical inventory counts, and adjustments',
        'primary_tables': [
            'tbl_StockLedger',
            'tbl_StockTransfer',
            'tbl_PhysicalInventory',
            'tbl_InventoryAdjustment',
            'tbl_Warehouse'
        ],
        'support_tables': [
            'tbl_ProductMaster',
            'tbl_ProductGrade',
            'dim_UOM',
            'dim_Status'
        ],
        'trigger_keywords': [
            'stock, inventory, warehouse, stock ledger, stock transfer, physical inventory',
            'inventory adjustment, closing stock, opening stock, stock movement',
            'stock in hand, available stock, stock balance, godown, store, bin',
            'material movement, stock value, reorder, reorder level, min stock, max stock'
        ],
        'anti_keywords': [
            'sale invoice, purchase invoice, payroll, hr, quality inspection, booking'
        ]
    },
    {
        'domain': 'Finance',
        'description': 'Accounting and financial management including ledgers, accounts, journal entries, payments, credit/debit notes, and TDS',
        'primary_tables': [
            'tbl_AccountLedger',
            'tbl_AccountGroup',
            'tbl_JournalVoucher',
            'tbl_JournalVoucherDetail',
            'tbl_PaymentMade',
            'tbl_PaymentReceived',
            'tbl_CreditDebitNote',
            'tbl_TDSDeduction'
        ],
        'support_tables': [
            'tbl_Organization',
            'dim_Status',
            'dim_PaymentTerm'
        ],
        'trigger_keywords': [
            'finance, accounting, ledger, account, journal, voucher, payment',
            'payment made, payment received, credit note, debit note, tds',
            'tax deducted, accounts payable, accounts receivable, ap, ar',
            'outstanding, balance, revenue, expenses, pnl, profit and loss',
            'balance sheet, trial balance, debit, credit, double entry, bank, cash'
        ],
        'anti_keywords': [
            'attendance, leave, quality, trip, vehicle, driver'
        ]
    },
    {
        'domain': 'HR',
        'description': 'Human resources management including employee master, attendance tracking, leave management, payroll processing, and department/designation hierarchy',
        'primary_tables': [
            'tbl_Employee',
            'tbl_Attendance',
            'tbl_LeaveApplication',
            'tbl_LeaveType',
            'tbl_PayrollHeader',
            'tbl_PayrollDetail',
            'tbl_Department',
            'tbl_Designation'
        ],
        'support_tables': [
            'dim_Status',
            'dmn_City',
            'dmn_State'
        ],
        'trigger_keywords': [
            'employee, staff, personnel, hr, human resource, attendance, leave',
            'leave application, leave balance, payroll, salary, wages, department',
            'designation, reporting, manager, new joiners, resigned, active employees',
            'employee count, headcount, appraisal, overtime, bonus, pf, esi',
            'provident fund, termination, resignation, joining date',
            'employee details, employee state, employee city,'
        ],
        'anti_keywords': [
            'invoice, stock, warehouse, purchase order, product master, logistic, trip'
        ]
    },
    {
        'domain': 'Product',
        'description': 'Product catalog management including product master, categories, classes, grades, HSN codes, GST rates, and UOM definitions',
        'primary_tables': [
            'tbl_ProductMaster',
            'tbl_ProductCategory',
            'tbl_ProductClass',
            'tbl_ProductGrade'
        ],
        'support_tables': [
            'dim_UOM',
            'dim_TaxRate'
        ],
        'trigger_keywords': [
            'product, item, material, goods, product master, product category, product class',
            'product grade, grade, sku, hsn, hsn code, catalog, product catalog',
            'stock item, finished goods, raw material, product list, bom, bill of materials',
            'spare, part, variant, alternative item, product group'
        ],
        'anti_keywords': [
            'invoice, payment, payroll, attendance, trip, quality test'
        ]
    },
    {
        'domain': 'Logistics',
        'description': 'Transportation and logistics management including trip sheets, vehicle master, driver master, route planning, and loading details',
        'primary_tables': [
            'tbl_TripSheet',
            'tbl_VehicleMaster',
            'tbl_DriverMaster',
            'tbl_RouteMaster',
            'tbl_LoadingDetail'
        ],
        'support_tables': [
            'dmn_City',
            'dim_Status',
            'tbl_ProductMaster',
            'tbl_ProductGrade',
            'dim_UOM',
            'tbl_SaleInvoiceHeader',
            'tbl_PurchaseSchedule'
        ],
        'trigger_keywords': [
            'logistics, transport, transportation, trip, trip sheet, vehicle, truck, lorry',
            'driver, route, loading, unloading, freight, lr, lorry receipt, consignment',
            'dispatch, delivery, transporter, cnf, clearing, forwarding, logistics tracking',
            'vehicle number, rc, insurance, fitness'
        ],
        'anti_keywords': [
            'payroll, leave, attendance, journal, ledger, quality parameter, product category'
        ]
    },
    {
        'domain': 'Quality',
        'description': 'Quality control and inspection management including quality checklists, parameters, test results, and product quality tracking',
        'primary_tables': [
            'tbl_QualityChecklist',
            'tbl_QualityParameter',
            'tbl_QualityTestResult'
        ],
        'support_tables': [
            'tbl_ProductMaster',
            'tbl_ProductGrade',
            'tbl_SaleInvoiceHeader',
            'tbl_PurchaseSchedule',
            'dim_UOM'
        ],
        'trigger_keywords': [
            'quality, quality check, quality control, qc, inspection, checklist, parameter',
            'test, test result, quality parameter, quality test, specification',
            'quality standard, pass, fail, quality approval, sample'
        ],
        'anti_keywords': [
            'payment, ledger, payroll, attendance, trip, booking'
        ]
    },
    {
        'domain': 'Compliance',
        'description': 'Statutory and regulatory compliance including GST returns, E-Way Bills, TDS deductions, and organizational registrations',
        'primary_tables': [
            'tbl_GSTReturn',
            'tbl_EwayBill',
            'tbl_TDSDeduction',
            'tbl_OrgRegistration'
        ],
        'support_tables': [
            'tbl_Organization',
            'tbl_SaleInvoiceHeader',
            'tbl_PurchaseSchedule',
            'dim_Status'
        ],
        'trigger_keywords': [
            'compliance, gst, gst return, gstr, gstr1, gstr3b, tax return, eway bill',
            'e-way bill, waybill, tds, tds deduction, tax deducted, registration',
            'gst registration, pan, gstin, statutory, regulatory, filing, return filing',
            'tax filing, it return, income tax'
        ],
        'anti_keywords': [
            'stock ledger, attendance, payroll, trip, route, loading detail'
        ]
    },
    {
        'domain': 'Organization',
        'description': 'Business partner master data management including dealers, distributors, vendors, transporters, CNFs and their addresses, contacts, bank details',
        'primary_tables': [
            'tbl_Organization',
            'tbl_OrgAddress',
            'tbl_OrgContact',
            'tbl_OrgBankDetail'
        ],
        'support_tables': [
            'dim_OrgType',
            'dim_PaymentTerm',
            'dmn_City'
        ],
        'trigger_keywords': [
            'organization, company, party, dealer, vendor, supplier, customer, distributor',
            'cnf, transporter, firm, business partner, partner master, party master',
            'address, contact, bank detail, gst number, pan, registration',
            'credit limit, opening balance'
        ],
        'anti_keywords': [
            'stock ledger, stock transfer, attendance, payroll, leave, quality test, trip sheet, loading detail'
        ]
    },
    {
        'domain': 'Pricing',
        'description': 'Product pricing management including global purchase/sale rates, product-specific pricing, rate approvals, and rate bands',
        'primary_tables': [
            'tbl_GlobalPurchaseRate',
            'tbl_GlobalSaleRate',
            'tbl_ProductPricing',
            'tbl_RateApproval',
            'tbl_RateBand'
        ],
        'support_tables': [
            'tbl_ProductMaster',
            'tbl_ProductGrade'
        ],
        'trigger_keywords': [
            'pricing, price, rate, rate approval, rate band, purchase rate, sale rate',
            'global rate, product price, unit price, cost, cost price, selling price',
            'margin, markup, pricing master, price list, rate list, discount, mrp',
            'effective date, contract rate, special price, promotional'
        ],
        'anti_keywords': [
            'attendance, leave, trip, stock ledger, invoice, payment'
        ]
    },
    {
        'domain': 'Geography',
        'description': 'Geographic reference data including countries, states, and cities used across the system for addresses and route planning',
        'primary_tables': [
            'dmn_Country',
            'dmn_State',
            'dmn_City'
        ],
        'support_tables': [],
        'trigger_keywords': [
            
            'geography, location, city, state, country, address, place, region, district',
            'pincode, zip, area'
        ],
        'anti_keywords': [
            'invoice, payment, ledger, stock, payroll, leave, quality, trip, product'
        ]
    },
    {
        'domain': 'Reference',
        'description': 'System reference data including status codes, organization types, payment terms, UOM, and tax rate definitions used across all modules',
        'primary_tables': [
            'dim_Status',
            'dim_OrgType',
            'dim_PaymentTerm',
            'dim_UOM',
            'dim_TaxRate'
        ],
        'support_tables': [],
        'trigger_keywords': [
            'reference, master data, lookup, status, type, category, term, payment term',
            'uom, unit, tax rate, tax slab, org type'
        ],
        'anti_keywords': [
            'transaction, invoice, payment, stock, trip, attendance'
        ]
    },
    {
        'domain': 'System',
        'description': 'System administration and audit including user management, audit logs, and error tracking',
        'primary_tables': [
            'tbl_UserMaster',
            'tbl_AuditLog',
            'tbl_ErrorLog'
        ],
        'support_tables': [
            'tbl_Employee'
        ],
        'trigger_keywords': [
            'system, admin, user, login, audit, audit log, error log, error, exception',
            'user master, permission, role, access, activity log, user activity'
        ],
        'anti_keywords': [
            'invoice, payment, stock, product, purchase order, sale order'
        ]
    }
]

GLOSSARY_DATA = {
    'GRN': {
        'full_form': 'Goods Receipt Note',
        'synonyms': [
            'goods received note',
            'grn',
            'receipt note',
            'material receipt'
        ],
        'description': 'A document acknowledging receipt of goods from a supplier, used to match purchase orders and update inventory stock levels.',
        'domain': 'Inventory'
    },
    'GSTIN': {
        'full_form': 'Goods and Services Tax Identification Number',
        'synonyms': [
            'gstin',
            'gst number',
            'gst registration',
            'gst no',
            'gst id'
        ],
        'description': 'A unique 15-digit alphanumeric identification number assigned to each registered taxpayer under GST.',
        'domain': 'Compliance'
    },
    'HSN': {
        'full_form': 'Harmonized System of Nomenclature',
        'synonyms': [
            'hsn',
            'hsn code',
            'harmonized code',
            'tariff code',
            'commodity code'
        ],
        'description': 'A standardized system of names and numbers for classifying traded products, used for GST return filing.',
        'domain': 'Product'
    },
    'TDS': {
        'full_form': 'Tax Deducted at Source',
        'synonyms': [
            'tds',
            'tax deducted at source',
            'withholding tax',
            'tds deduction'
        ],
        'description': 'Tax collected by the government at the source of income, deducted by the payer and deposited with the tax authorities.',
        'domain': 'Compliance'
    },
    'E-Way Bill': {
        'full_form': 'Electronic Way Bill',
        'synonyms': [
            'eway bill',
            'e-way bill',
            'waybill',
            'electronic way bill',
            'transport bill'
        ],
        'description': 'An electronically generated document required for the movement of goods exceeding INR 50,000 in value, containing vehicle and shipment details.',
        'domain': 'Compliance'
    },
    'CNF': {
        'full_form': 'C&F Agent (Clearing and Forwarding Agent)',
        'synonyms': [
            'cnf',
            'c&f agent',
            'clearing agent',
            'forwarding agent',
            'cnf agent'
        ],
        'description': 'A logistics intermediary who handles clearance and forwarding of goods on behalf of the principal, commonly used in distribution networks.',
        'domain': 'Logistics'
    },
    'LR': {
        'full_form': 'Lorry Receipt',
        'synonyms': [
            'lr',
            'lorry receipt',
            'transport receipt',
            'consignment note',
            'transport document'
        ],
        'description': 'A receipt issued by a transporter acknowledging receipt of goods for shipment, serving as evidence of the transport contract.',
        'domain': 'Logistics'
    },
    'PO': {
        'full_form': 'Purchase Order',
        'synonyms': [
            'po',
            'purchase order',
            'procurement order',
            'buy order'
        ],
        'description': 'A commercial document issued by a buyer to a seller indicating the type, quantity, and agreed price of products or services.',
        'domain': 'Purchase'
    },
    'SO': {
        'full_form': 'Sales Order',
        'synonyms': [
            'so',
            'sales order',
            'sale order',
            'customer order',
            'booking'
        ],
        'description': 'A commercial document issued by a seller to a customer confirming the sale of products or services under agreed terms.',
        'domain': 'Sales'
    },
    'GST': {
        'full_form': 'Goods and Services Tax',
        'synonyms': [
            'gst',
            'goods and services tax',
            'gst tax',
            'indirect tax'
        ],
        'description': 'A comprehensive, multi-stage, destination-based indirect tax levied on every value addition, replacing many earlier indirect taxes.',
        'domain': 'Compliance'
    },
    'SGST': {
        'full_form': 'State Goods and Services Tax',
        'synonyms': [
            'sgst',
            'state gst',
            'state tax'
        ],
        'description': 'The state-level component of GST, collected by the state government on intra-state transactions.',
        'domain': 'Compliance'
    },
    'CGST': {
        'full_form': 'Central Goods and Services Tax',
        'synonyms': [
            'cgst',
            'central gst',
            'central tax'
        ],
        'description': 'The central-level component of GST, collected by the central government on intra-state transactions.',
        'domain': 'Compliance'
    },
    'IGST': {
        'full_form': 'Integrated Goods and Services Tax',
        'synonyms': [
            'igst',
            'integrated gst',
            'interstate gst'
        ],
        'description': 'The component of GST collected on inter-state transactions, shared between central and state governments.',
        'domain': 'Compliance'
    },
    'UOM': {
        'full_form': 'Unit of Measurement',
        'synonyms': [
            'uom',
            'unit of measure',
            'measure unit',
            'base unit'
        ],
        'description': 'The standard unit used to measure quantity of products such as KG, MT, Pieces, Liters, etc.',
        'domain': 'Product'
    },
    'PAN': {
        'full_form': 'Permanent Account Number',
        'synonyms': [
            'pan',
            'pan number',
            'pan no',
            'tax id',
            'permanent account number'
        ],
        'description': 'A unique 10-character alphanumeric identifier issued by the Income Tax Department to individuals and entities.',
        'domain': 'Compliance'
    },
    'GR': {
        'full_form': 'Goods Receipt',
        'synonyms': [
            'gr',
            'goods receipt',
            'material receipt',
            'goods received'
        ],
        'description': 'The process of receiving goods from a supplier and recording them into inventory, typically against a purchase order.',
        'domain': 'Inventory'
    },
    'Outstanding': {
        'full_form': 'Outstanding Amount',
        'synonyms': [
            'outstanding',
            'pending payment',
            'due amount',
            'balance due',
            'unpaid',
            'pending amount'
        ],
        'description': 'The amount that is yet to be paid by a customer or to a vendor, representing pending receivables or payables.',
        'domain': 'Finance'
    }
}

EXAMPLES_DATA = [
    {
        'nl': 'Show me all pending invoices with customer names',
        'sql': "SELECT sih.invoiceNo, sih.invoiceDate, sih.grandTotal, o.firmName AS customer FROM tbl_SaleInvoiceHeader sih JOIN tbl_Organization o ON sih.dealerOrgId = o.idOrganization JOIN dim_Status s ON sih.statusId = s.idStatus WHERE s.statusName = 'Pending' ORDER BY sih.invoiceDate DESC\n",
        'tables': [
            'tbl_SaleInvoiceHeader',
            'tbl_Organization',
            'dim_Status'
        ],
        'domain': 'Sales',
        'explanation': 'Joins sale invoices with organization for customer name and status for filtering pending records.'
    },
    {
        'nl': 'What is the total stock value across all warehouses?',
        'sql': 'SELECT SUM(sl.closingQty * pm.minStock) AS total_stock_value FROM tbl_StockLedger sl JOIN tbl_ProductMaster pm ON sl.productId = pm.idProduct\n',
        'tables': [
            'tbl_StockLedger',
            'tbl_ProductMaster'
        ],
        'domain': 'Inventory',
        'explanation': 'Multiplies closing quantity by min stock value across all products and warehouses.'
    },
    {
        'nl': 'List all employees in the Sales department with their designation',
        'sql': "SELECT e.employeeCode, e.firstName + ' ' + e.lastName AS employeeName,\n       d.departmentName, des.designationName\nFROM tbl_Employee e JOIN tbl_Department d ON e.departmentId = d.idDepartment JOIN tbl_Designation des ON e.designationId = des.idDesignation WHERE d.departmentName = 'Sales' ORDER BY e.firstName\n",
        'tables': [
            'tbl_Employee',
            'tbl_Department',
            'tbl_Designation'
        ],
        'domain': 'HR',
        'explanation': 'Filters employees by department name with a three-table join for department and designation names.'
    },
    {
        'nl': 'Show purchase orders created this month with vendor details',
        'sql': 'SELECT po.poNumber, po.poDate, po.totalAmount, o.firmName AS vendor FROM tbl_PurchaseOrder po JOIN tbl_Organization o ON po.vendorId = o.idOrganization WHERE MONTH(po.poDate) = MONTH(GETDATE()) AND YEAR(po.poDate) = YEAR(GETDATE()) ORDER BY po.poDate DESC\n',
        'tables': [
            'tbl_PurchaseOrder',
            'tbl_Organization'
        ],
        'domain': 'Purchase',
        'explanation': 'Filters purchase orders by current month with a join to organization for vendor name.'
    },
    {
        'nl': 'How many products are there in each category?',
        'sql': 'SELECT pc.categoryName, COUNT(pm.idProduct) AS productCount FROM tbl_ProductMaster pm JOIN tbl_ProductCategory pc ON pm.categoryId = pc.idCategory GROUP BY pc.categoryName ORDER BY productCount DESC\n',
        'tables': [
            'tbl_ProductMaster',
            'tbl_ProductCategory'
        ],
        'domain': 'Product',
        'explanation': 'Groups products by category with a join and counts products per category.'
    },
    {
        'nl': 'What is the total due amount (accounts receivable) from each customer?',
        'sql': "SELECT o.firmName, SUM(sih.grandTotal) AS total_receivable FROM tbl_SaleInvoiceHeader sih JOIN tbl_Organization o ON sih.dealerOrgId = o.idOrganization JOIN dim_Status s ON sih.statusId = s.idStatus WHERE s.statusName NOT IN ('Paid', 'Cancelled') GROUP BY o.firmName ORDER BY total_receivable DESC\n",
        'tables': [
            'tbl_SaleInvoiceHeader',
            'tbl_Organization',
            'dim_Status'
        ],
        'domain': 'Finance',
        'explanation': 'Aggregates unpaid invoice amounts grouped by customer to show accounts receivable.'
    },
    {
        'nl': 'Get all trips scheduled for today with driver and vehicle details',
        'sql': 'SELECT ts.tripNo, ts.tripDate, dm.driverName, vm.vehicleNo,\n       rm.sourceCityId, rm.destCityId\nFROM tbl_TripSheet ts JOIN tbl_DriverMaster dm ON ts.driverId = dm.idDriver JOIN tbl_VehicleMaster vm ON ts.vehicleId = vm.idVehicle JOIN tbl_RouteMaster rm ON ts.routeId = rm.idRoute WHERE CAST(ts.tripDate AS DATE) = CAST(GETDATE() AS DATE) ORDER BY ts.tripNo\n',
        'tables': [
            'tbl_TripSheet',
            'tbl_DriverMaster',
            'tbl_VehicleMaster',
            'tbl_RouteMaster'
        ],
        'domain': 'Logistics',
        'explanation': "Filters trips by today's date with joins to driver, vehicle, and route tables."
    },
    {
        'nl': 'Show me the last 5 credit notes issued to each customer',
        'sql': "SELECT o.firmName, cdn.noteNo, cdn.noteDate, cdn.amount, cdn.reason FROM tbl_CreditDebitNote cdn JOIN tbl_Organization o ON cdn.organizationId = o.idOrganization WHERE cdn.noteType = 'Credit' ORDER BY cdn.noteDate DESC\n",
        'tables': [
            'tbl_CreditDebitNote',
            'tbl_Organization'
        ],
        'domain': 'Finance',
        'explanation': 'Filters credit-type notes and joins with organization for customer name, ordered by date.'
    },
    {
        'nl': 'Which vendors have the highest quality evaluation scores?',
        'sql': 'SELECT o.firmName, ve.overallScore, ve.evaluationDate, ve.remarks FROM tbl_VendorEvaluation ve JOIN tbl_Organization o ON ve.vendorId = o.idOrganization ORDER BY ve.overallScore DESC\n',
        'tables': [
            'tbl_VendorEvaluation',
            'tbl_Organization'
        ],
        'domain': 'Purchase',
        'explanation': 'Joins vendor evaluation scores with organization names sorted highest first.'
    },
    {
        'nl': 'Show me the daily attendance for employee X for this month',
        'sql': "SELECT e.firstName + ' ' + e.lastName AS employeeName,\n       a.attendanceDate, a.status, a.inTime, a.outTime\nFROM tbl_Attendance a JOIN tbl_Employee e ON a.employeeId = e.idEmployee WHERE e.employeeCode = @employee_code\n  AND MONTH(a.attendanceDate) = MONTH(GETDATE())\n  AND YEAR(a.attendanceDate) = YEAR(GETDATE())\nORDER BY a.attendanceDate\n",
        'tables': [
            'tbl_Attendance',
            'tbl_Employee'
        ],
        'domain': 'HR',
        'explanation': 'Filters attendance by employee code and current month with employee name join.'
    }
]

BUSINESS_RULES_DATA = [
    {
        'name': 'credit_limit_check',
        'description': "Sales invoice grand total must not exceed the organization's credit limit unless explicitly approved",
        'category': 'finance',
        'severity': 'error',
        'applies_to': [
            'tbl_SaleInvoiceHeader'
        ],
        'condition': 'grandTotal > COALESCE(tbl_Organization.creditLimit, 0)',
        'error_message': 'Invoice amount exceeds credit limit for this organization. Approval required.',
        'related_tables': [
            'tbl_SaleInvoiceHeader',
            'tbl_Organization'
        ]
    },
    {
        'name': 'double_entry_balancing',
        'description': 'Every journal voucher must have debits equal to credits (double-entry accounting principle)',
        'category': 'finance',
        'severity': 'error',
        'applies_to': [
            'tbl_JournalVoucher',
            'tbl_JournalVoucherDetail'
        ],
        'condition': 'SUM(debit) != SUM(credit)',
        'error_message': 'Journal voucher is not balanced. Total debits must equal total credits.',
        'related_tables': [
            'tbl_JournalVoucher',
            'tbl_JournalVoucherDetail'
        ]
    },
    {
        'name': 'stock_non_negative',
        'description': 'Stock quantity in StockLedger must never go negative after any transaction',
        'category': 'inventory',
        'severity': 'error',
        'applies_to': [
            'tbl_StockLedger'
        ],
        'condition': 'closingQty < 0',
        'error_message': 'Stock cannot go negative. Insufficient inventory for this transaction.',
        'related_tables': [
            'tbl_StockLedger',
            'tbl_InventoryAdjustment'
        ]
    },
    {
        'name': 'gst_compliance',
        'description': "Every sale invoice must have valid GST rate applied based on product's HSN code and tax rate",
        'category': 'compliance',
        'severity': 'error',
        'applies_to': [
            'tbl_SaleInvoiceDetail'
        ],
        'condition': 'taxRateId IS NULL',
        'error_message': 'GST rate is mandatory for all sale invoice line items.',
        'related_tables': [
            'tbl_SaleInvoiceDetail',
            'tbl_ProductMaster',
            'dim_TaxRate'
        ]
    },
    {
        'name': 'ewaybill_mandatory',
        'description': 'E-Way Bill must be generated for inter-state sale invoices exceeding INR 50,000',
        'category': 'compliance',
        'severity': 'warning',
        'applies_to': [
            'tbl_EwayBill',
            'tbl_SaleInvoiceHeader'
        ],
        'condition': "grandTotal > 50000 AND tbl_SaleInvoiceHeader.consigneeId IN (SELECT idOrganization FROM tbl_Organization WHERE cityId NOT IN (SELECT idCity FROM dmn_City WHERE stateId = (SELECT idState FROM dmn_State WHERE stateName = 'State'))) AND tbl_EwayBill.ewayBillNo IS NULL",
        'error_message': 'E-Way Bill is required for inter-state invoices above INR 50,000.',
        'related_tables': [
            'tbl_EwayBill',
            'tbl_SaleInvoiceHeader',
            'tbl_Organization',
            'dmn_City',
            'dmn_State'
        ]
    },
    {
        'name': 'purchase_order_approval',
        'description': 'Purchase orders above a threshold require managerial approval',
        'category': 'purchase',
        'severity': 'warning',
        'applies_to': [
            'tbl_PurchaseOrder'
        ],
        'condition': "totalAmount > 100000 AND statusId NOT IN (SELECT idStatus FROM dim_Status WHERE statusCode = 'APPROVED')",
        'error_message': 'Purchase orders above INR 1,00,000 require approval before processing.',
        'related_tables': [
            'tbl_PurchaseOrder',
            'dim_Status'
        ]
    },
    {
        'name': 'attendance_leave_balance',
        'description': 'Employee cannot apply for leave if insufficient leave balance',
        'category': 'hr',
        'severity': 'error',
        'applies_to': [
            'tbl_LeaveApplication',
            'tbl_LeaveType'
        ],
        'condition': 'totalDaysTaken > COALESCE((SELECT balanceDays FROM tbl_LeaveType WHERE idLeaveType = tbl_LeaveApplication.leaveTypeId), 0)',
        'error_message': 'Insufficient leave balance. Cannot approve leave application.',
        'related_tables': [
            'tbl_LeaveApplication',
            'tbl_LeaveType',
            'tbl_Employee'
        ]
    },
    {
        'name': 'payment_reconciliation',
        'description': 'Payment received must reconcile with the corresponding sale invoice amount',
        'category': 'finance',
        'severity': 'error',
        'applies_to': [
            'tbl_PaymentReceived',
            'tbl_SaleInvoiceHeader'
        ],
        'condition': 'amount > (SELECT grandTotal FROM tbl_SaleInvoiceHeader WHERE idInvoice = tbl_PaymentReceived.invoiceId)',
        'error_message': 'Payment amount exceeds the invoice grand total. Verify the payment.',
        'related_tables': [
            'tbl_PaymentReceived',
            'tbl_SaleInvoiceHeader'
        ]
    },
    {
        'name': 'product_pricing_consistency',
        'description': "Sale price must be greater than or equal to the product's global sale rate",
        'category': 'pricing',
        'severity': 'warning',
        'applies_to': [
            'tbl_ProductPricing',
            'tbl_GlobalSaleRate'
        ],
        'condition': 'unitPrice < (SELECT saleRate FROM tbl_GlobalSaleRate WHERE productId = tbl_ProductPricing.productId AND gradeId = tbl_ProductPricing.gradeId)',
        'error_message': 'Sale price is below the global sale rate for this product. Margin may be negative.',
        'related_tables': [
            'tbl_ProductPricing',
            'tbl_GlobalSaleRate',
            'tbl_ProductMaster'
        ]
    },
    {
        'name': 'stock_transfer_validation',
        'description': 'Stock transfer quantity must be available in the source warehouse',
        'category': 'inventory',
        'severity': 'error',
        'applies_to': [
            'tbl_StockTransfer'
        ],
        'condition': 'quantity > (SELECT SUM(closingQty) FROM tbl_StockLedger WHERE warehouseId = tbl_StockTransfer.fromWarehouseId AND productId = tbl_StockTransfer.productId)',
        'error_message': 'Insufficient stock in source warehouse for this transfer.',
        'related_tables': [
            'tbl_StockTransfer',
            'tbl_StockLedger',
            'tbl_Warehouse'
        ]
    },
    {
        'name': 'duplicate_invoice_check',
        'description': 'Invoice number must be unique within the same financial year',
        'category': 'sales',
        'severity': 'error',
        'applies_to': [
            'tbl_SaleInvoiceHeader'
        ],
        'condition': 'EXISTS (SELECT 1 FROM tbl_SaleInvoiceHeader AS dup WHERE dup.invoiceNo = tbl_SaleInvoiceHeader.invoiceNo AND dup.idInvoice != tbl_SaleInvoiceHeader.idInvoice AND YEAR(dup.invoiceDate) = YEAR(tbl_SaleInvoiceHeader.invoiceDate))',
        'error_message': 'Duplicate invoice number found in the same financial year.',
        'related_tables': [
            'tbl_SaleInvoiceHeader'
        ]
    },
    {
        'name': 'vendor_evaluation_score',
        'description': 'New purchase orders should not be created for vendors with evaluation score below threshold',
        'category': 'purchase',
        'severity': 'warning',
        'applies_to': [
            'tbl_PurchaseOrder',
            'tbl_VendorEvaluation'
        ],
        'condition': 'EXISTS (SELECT 1 FROM tbl_VendorEvaluation WHERE vendorId = tbl_PurchaseOrder.vendorId AND overallScore < 2.0)',
        'error_message': 'Vendor has a low evaluation score. Consider reviewing before placing a new order.',
        'related_tables': [
            'tbl_PurchaseOrder',
            'tbl_VendorEvaluation',
            'tbl_Organization'
        ]
    }
]

SQL_PATTERNS_DATA = [
    {
        'category': 'aggregation',
        'description': 'Total sales revenue (sum of invoice grand totals) with optional date filtering',
        'sql_template': 'SELECT SUM(grandTotal) AS total_revenue FROM tbl_SaleInvoiceHeader WHERE invoiceDate BETWEEN @start_date AND @end_date\n',
        'tables': [
            'tbl_SaleInvoiceHeader'
        ],
        'intent': 'What is the total revenue for Q1 2024?'
    },
    {
        'category': 'aggregation_with_groupby',
        'description': 'Aggregate metric grouped by a dimension (e.g., sales by dealer)',
        'sql_template': 'SELECT o.firmName, SUM(sih.grandTotal) AS total_sales FROM tbl_SaleInvoiceHeader sih JOIN tbl_Organization o ON sih.dealerOrgId = o.idOrganization WHERE sih.invoiceDate BETWEEN @start_date AND @end_date GROUP BY o.firmName ORDER BY total_sales DESC\n',
        'tables': [
            'tbl_SaleInvoiceHeader',
            'tbl_Organization'
        ],
        'intent': 'Show total sales by customer for last month'
    },
    {
        'category': 'count',
        'description': 'Count records with optional group by dimension',
        'sql_template': 'SELECT COUNT(*) AS record_count FROM @table_name WHERE @filter_condition\n',
        'tables': [],
        'intent': 'How many customers do we have?'
    },
    {
        'category': 'join_two_tables',
        'description': 'Two-table join to fetch related data across entities',
        'sql_template': 'SELECT sih.invoiceNo, sih.invoiceDate, sih.grandTotal, o.firmName AS customer FROM tbl_SaleInvoiceHeader sih JOIN tbl_Organization o ON sih.dealerOrgId = o.idOrganization WHERE sih.invoiceDate BETWEEN @start_date AND @end_date ORDER BY sih.invoiceDate DESC\n',
        'tables': [
            'tbl_SaleInvoiceHeader',
            'tbl_Organization'
        ],
        'intent': 'Show me all invoices with customer names from last month'
    },
    {
        'category': 'join_multi_table',
        'description': 'Multi-table join combining sales, products, categories, and grades',
        'sql_template': 'SELECT sih.invoiceNo, sih.invoiceDate, sid.quantity, sid.unitPrice,\n       pm.productName, pc.categoryName, pg.gradeName\nFROM tbl_SaleInvoiceHeader sih JOIN tbl_SaleInvoiceDetail sid ON sih.idInvoice = sid.invoiceId JOIN tbl_ProductMaster pm ON sid.productId = pm.idProduct LEFT JOIN tbl_ProductCategory pc ON pm.categoryId = pc.idCategory LEFT JOIN tbl_ProductGrade pg ON sid.gradeId = pg.idGrade WHERE sih.invoiceDate BETWEEN @start_date AND @end_date\n',
        'tables': [
            'tbl_SaleInvoiceHeader',
            'tbl_SaleInvoiceDetail',
            'tbl_ProductMaster',
            'tbl_ProductCategory',
            'tbl_ProductGrade'
        ],
        'intent': 'Show invoice details with product, category, and grade information'
    },
    {
        'category': 'filter_by_status',
        'description': 'Fetch records filtered by a specific status',
        'sql_template': 'SELECT * FROM @table_name t JOIN dim_Status s ON t.statusId = s.idStatus WHERE s.statusName = @status_name\n',
        'tables': [
            'dim_Status'
        ],
        'intent': 'Show all pending invoices'
    },
    {
        'category': 'date_range_filter',
        'description': 'Filter records within a date range',
        'sql_template': 'SELECT * FROM @table_name WHERE @date_column BETWEEN @start_date AND @end_date ORDER BY @date_column DESC\n',
        'tables': [],
        'intent': 'Get me invoices between January 1st and March 31st 2024'
    },
    {
        'category': 'stock_balance',
        'description': 'Current stock balance for a product across warehouses',
        'sql_template': 'SELECT w.warehouseName, pm.productName, sl.closingQty FROM tbl_StockLedger sl JOIN tbl_Warehouse w ON sl.warehouseId = w.idWarehouse JOIN tbl_ProductMaster pm ON sl.productId = pm.idProduct WHERE sl.productId = @product_id ORDER BY w.warehouseName\n',
        'tables': [
            'tbl_StockLedger',
            'tbl_Warehouse',
            'tbl_ProductMaster'
        ],
        'intent': 'What is the current stock level of product X in each warehouse?'
    },
    {
        'category': 'top_n',
        'description': 'Top N records sorted by a metric',
        'sql_template': 'SELECT TOP (@n) o.firmName, SUM(sih.grandTotal) AS total_sales FROM tbl_SaleInvoiceHeader sih JOIN tbl_Organization o ON sih.dealerOrgId = o.idOrganization WHERE sih.invoiceDate BETWEEN @start_date AND @end_date GROUP BY o.firmName ORDER BY total_sales DESC\n',
        'tables': [
            'tbl_SaleInvoiceHeader',
            'tbl_Organization'
        ],
        'intent': 'Top 10 customers by sales this year'
    },
    {
        'category': 'comparison',
        'description': 'Compare two metrics side by side (e.g., sales vs purchase)',
        'sql_template': "SELECT 'Sales' AS type, SUM(grandTotal) AS total FROM tbl_SaleInvoiceHeader WHERE invoiceDate BETWEEN @start_date AND @end_date UNION ALL SELECT 'Purchases' AS type, SUM(totalAmount) AS total FROM tbl_PurchaseInvoice WHERE invoiceDate BETWEEN @start_date AND @end_date\n",
        'tables': [
            'tbl_SaleInvoiceHeader',
            'tbl_PurchaseInvoice'
        ],
        'intent': 'Compare total sales vs purchases for this month'
    }
]

STATS_DATA = {
    'tables_count': 68,
    'total_columns': 717,
    'total_foreign_keys': 149,
    'total_keywords': 1024,
    'total_intents': 388,
    'total_joins': 149,
    'total_domains': 14,
    'total_rules': 12,
    'total_glossary_terms': 17,
    'total_sql_patterns': 10,
    'total_examples': 10
}
