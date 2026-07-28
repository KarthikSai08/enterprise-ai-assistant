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
    },
    'PF': {
        'full_form': 'Provident Fund',
        'synonyms': [
            'pf',
            'provident fund',
            'epf',
            'employees provident fund'
        ],
        'description': 'A mandatory retirement benefit scheme where both employer and employee contribute a percentage of the employee\'s basic salary.',
        'domain': 'HR'
    },
    'ESI': {
        'full_form': 'Employee State Insurance',
        'synonyms': [
            'esi',
            'employee state insurance',
            'medical insurance'
        ],
        'description': 'A self-financing health insurance scheme for employees earning below a threshold, providing medical and cash benefits.',
        'domain': 'HR'
    },
    'CTC': {
        'full_form': 'Cost to Company',
        'synonyms': [
            'ctc',
            'cost to company',
            'total compensation',
            'salary package'
        ],
        'description': 'The total cost an employer incurs for an employee including salary, benefits, bonuses, PF, and insurance.',
        'domain': 'HR'
    },
    'LOP': {
        'full_form': 'Loss of Pay',
        'synonyms': [
            'lop',
            'loss of pay',
            'unpaid leave',
            'leave without pay'
        ],
        'description': 'Leave taken by an employee without pay when leave balance is exhausted or leave type is unpaid.',
        'domain': 'HR'
    },
    'HRA': {
        'full_form': 'House Rent Allowance',
        'synonyms': [
            'hra',
            'house rent allowance',
            'rent allowance'
        ],
        'description': 'A component of salary provided to employees to cover rental housing expenses, partially tax-exempt under income tax rules.',
        'domain': 'HR'
    },
    'TA': {
        'full_form': 'Travel Allowance',
        'synonyms': [
            'ta',
            'travel allowance',
            'conveyance allowance',
            'transport allowance'
        ],
        'description': 'An allowance paid to employees to cover travel expenses incurred for official purposes or commuting.',
        'domain': 'HR'
    },
    'DA': {
        'full_form': 'Dearness Allowance',
        'synonyms': [
            'da',
            'dearness allowance',
            'cost of living allowance'
        ],
        'description': 'An allowance paid to employees to offset the impact of inflation on their cost of living, calculated as a percentage of basic salary.',
        'domain': 'HR'
    },
    'SKU': {
        'full_form': 'Stock Keeping Unit',
        'synonyms': [
            'sku',
            'stock keeping unit',
            'product code',
            'item code',
            'part number'
        ],
        'description': 'A unique identifier for each distinct product or item that can be purchased, stored, and sold in inventory management.',
        'domain': 'Product'
    },
    'BOM': {
        'full_form': 'Bill of Materials',
        'synonyms': [
            'bom',
            'bill of materials',
            'product structure',
            'component list',
            'parts list'
        ],
        'description': 'A comprehensive list of raw materials, components, and sub-assemblies required to manufacture a finished product.',
        'domain': 'Product'
    },
    'MRP': {
        'full_form': 'Maximum Retail Price',
        'synonyms': [
            'mrp',
            'maximum retail price',
            'max price',
            'retail price'
        ],
        'description': 'The highest price at which a product can be sold to the end consumer as printed on the packaging, inclusive of all taxes.',
        'domain': 'Product'
    },
    'COGS': {
        'full_form': 'Cost of Goods Sold',
        'synonyms': [
            'cogs',
            'cost of goods sold',
            'cost of sales',
            'cost of revenue'
        ],
        'description': 'The direct cost attributable to the production of goods sold, including raw material and labor costs.',
        'domain': 'Finance'
    },
    'P&L': {
        'full_form': 'Profit and Loss Statement',
        'synonyms': [
            'pnl',
            'p&l',
            'profit and loss',
            'income statement',
            'statement of operations'
        ],
        'description': 'A financial statement summarizing revenues, costs, and expenses over a period to show net profit or loss.',
        'domain': 'Finance'
    },
    'AP': {
        'full_form': 'Accounts Payable',
        'synonyms': [
            'ap',
            'accounts payable',
            'payables',
            'creditors',
            'vendor payables'
        ],
        'description': 'Money owed by a business to its suppliers or vendors for goods and services purchased on credit.',
        'domain': 'Finance'
    },
    'AR': {
        'full_form': 'Accounts Receivable',
        'synonyms': [
            'ar',
            'accounts receivable',
            'receivables',
            'debtors',
            'customer receivables'
        ],
        'description': 'Money owed to a business by its customers for goods or services delivered but not yet paid for.',
        'domain': 'Finance'
    },
    'LRR': {
        'full_form': 'Lorry Receipt Number',
        'synonyms': [
            'lrr',
            'lr number',
            'lorry receipt no',
            'transport receipt number'
        ],
        'description': 'The unique reference number on a lorry receipt used to track consignments during transportation.',
        'domain': 'Logistics'
    },
    'FTL': {
        'full_form': 'Full Truck Load',
        'synonyms': [
            'ftl',
            'full truck load',
            'full load',
            'full vehicle load'
        ],
        'description': 'A shipping mode where an entire truck is dedicated to a single consignment, typically for large volume shipments.',
        'domain': 'Logistics'
    },
    'LTL': {
        'full_form': 'Less Than Truck Load',
        'synonyms': [
            'ltl',
            'less than truck load',
            'part load',
            'consolidated shipment'
        ],
        'description': 'A shipping mode where multiple consignments share truck space, each paying for the portion of space used.',
        'domain': 'Logistics'
    },
    'QC': {
        'full_form': 'Quality Control',
        'synonyms': [
            'qc',
            'quality control',
            'quality inspection',
            'quality check'
        ],
        'description': 'The process of inspecting products to ensure they meet specified quality standards and requirements.',
        'domain': 'Quality'
    },
    'RFQ': {
        'full_form': 'Request for Quotation',
        'synonyms': [
            'rfq',
            'request for quotation',
            'request for quote',
            'quotation request',
            'price enquiry'
        ],
        'description': 'A document sent to suppliers requesting pricing and terms for specified products or services.',
        'domain': 'Purchase'
    },
    'SOH': {
        'full_form': 'Stock on Hand',
        'synonyms': [
            'soh',
            'stock on hand',
            'available stock',
            'current stock',
            'inventory level'
        ],
        'description': 'The quantity of a product currently available in inventory at a given location or across all warehouses.',
        'domain': 'Inventory'
    },
    'GSTR': {
        'full_form': 'GST Return',
        'synonyms': [
            'gstr',
            'gst return',
            'gst filing',
            'tax return'
        ],
        'description': 'Periodic returns filed by registered taxpayers to report sales, purchases, and tax paid/collected under GST.',
        'domain': 'Compliance'
    },
    'TAN': {
        'full_form': 'Tax Deduction and Collection Account Number',
        'synonyms': [
            'tan',
            'tax deduction account number',
            'tds account number',
            'tan number'
        ],
        'description': 'A 10-character alphanumeric number required for persons who are responsible for deducting or collecting tax at source.',
        'domain': 'Compliance'
    },
    'FIFO': {
        'full_form': 'First In, First Out',
        'synonyms': [
            'fifo',
            'first in first out',
            'inventory valuation method'
        ],
        'description': 'An inventory valuation method assuming the oldest stock items are sold or used first, affecting cost of goods sold.',
        'domain': 'Inventory'
    },
    'Indent': {
        'full_form': 'Purchase Indent',
        'synonyms': [
            'indent',
            'purchase indent',
            'material requisition',
            'store requisition',
            'demand note'
        ],
        'description': 'An internal document raised by a department requesting the purchase department to procure specified materials.',
        'domain': 'Purchase'
    },
    'Consignment': {
        'full_form': 'Consignment Shipment',
        'synonyms': [
            'consignment',
            'shipment',
            'dispatch',
            'cargo',
            'goods shipment'
        ],
        'description': 'A batch of goods sent from one party to another for delivery or sale, tracked via a consignment note.',
        'domain': 'Logistics'
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
    },
    {
        'nl': 'Show the total payroll summary for this month',
        'sql': "SELECT ph.payMonth, COUNT(DISTINCT pd.employeeId) AS totalEmployees,\n       SUM(pd.grossPay) AS totalGross, SUM(pd.totalDeductions) AS totalDeductions,\n       SUM(pd.netPay) AS totalNetPay\nFROM tbl_PayrollHeader ph JOIN tbl_PayrollDetail pd ON ph.idPayrollHeader = pd.payrollHeaderId\nWHERE MONTH(ph.payPeriodStart) = MONTH(GETDATE()) AND YEAR(ph.payPeriodStart) = YEAR(GETDATE())\nGROUP BY ph.payMonth\n",
        'tables': ['tbl_PayrollHeader', 'tbl_PayrollDetail'],
        'domain': 'HR',
        'explanation': 'Aggregates payroll details by month to show total employees, gross, deductions, and net pay.'
    },
    {
        'nl': 'What is the current stock balance of product X?',
        'sql': 'SELECT w.warehouseName, sl.closingQty\nFROM tbl_StockLedger sl JOIN tbl_Warehouse w ON sl.warehouseId = w.idWarehouse\nWHERE sl.productId = @product_id ORDER BY w.warehouseName\n',
        'tables': ['tbl_StockLedger', 'tbl_Warehouse'],
        'domain': 'Inventory',
        'explanation': 'Shows closing stock quantity for a product across all warehouses.'
    },
    {
        'nl': 'Show pending purchase orders with vendor name',
        'sql': "SELECT po.poNumber, po.poDate, po.totalAmount, o.firmName AS vendor\nFROM tbl_PurchaseOrder po JOIN tbl_Organization o ON po.vendorId = o.idOrganization\nJOIN dim_Status s ON po.statusId = s.idStatus\nWHERE s.statusName = 'Pending' ORDER BY po.poDate DESC\n",
        'tables': ['tbl_PurchaseOrder', 'tbl_Organization', 'dim_Status'],
        'domain': 'Purchase',
        'explanation': 'Filters purchase orders by pending status with vendor name join.'
    },
    {
        'nl': 'List all E-Way Bills expiring this week',
        'sql': "SELECT eb.ewayBillNo, eb.validFrom, eb.validTo,\n       sih.invoiceNo, o.firmName AS consignor\nFROM tbl_EwayBill eb JOIN tbl_SaleInvoiceHeader sih ON eb.invoiceId = sih.idInvoice\nJOIN tbl_Organization o ON sih.dealerOrgId = o.idOrganization\nWHERE eb.validTo BETWEEN GETDATE() AND DATEADD(DAY, 7, GETDATE())\nORDER BY eb.validTo\n",
        'tables': ['tbl_EwayBill', 'tbl_SaleInvoiceHeader', 'tbl_Organization'],
        'domain': 'Compliance',
        'explanation': 'Shows e-way bills expiring within 7 days with invoice and consignor details.'
    },
    {
        'nl': 'Show the leave balance for each employee',
        'sql': "SELECT e.firstName + ' ' + e.lastName AS employeeName,\n       lt.leaveCode, lt.maxDays,\n       (lt.maxDays - COALESCE(SUM(la.totalDays), 0)) AS balanceDays\nFROM tbl_Employee e CROSS JOIN tbl_LeaveType lt\nLEFT JOIN tbl_LeaveApplication la ON e.idEmployee = la.employeeId\n    AND la.leaveTypeId = lt.idLeaveType\n    AND YEAR(la.fromDate) = YEAR(GETDATE())\nGROUP BY e.firstName, e.lastName, lt.leaveCode, lt.maxDays\nORDER BY employeeName, lt.leaveCode\n",
        'tables': ['tbl_Employee', 'tbl_LeaveType', 'tbl_LeaveApplication'],
        'domain': 'HR',
        'explanation': 'Calculates remaining leave balance by subtracting used days from max allowed per leave type.'
    },
    {
        'nl': 'What is the total TDS deducted this financial year?',
        'sql': 'SELECT tdsSection, SUM(tdsAmount) AS totalTds\nFROM tbl_TDSDeduction\nWHERE YEAR(tdsDate) = YEAR(GETDATE())\nGROUP BY tdsSection ORDER BY tdsSection\n',
        'tables': ['tbl_TDSDeduction'],
        'domain': 'Finance',
        'explanation': 'Aggregates TDS deductions by section for the current financial year.'
    },
    {
        'nl': 'Show the account ledger balance for a specific account',
        'sql': 'SELECT al.transactionDate, al.particulars, al.debit, al.credit,\n       SUM(al.debit - al.credit) OVER (ORDER BY al.transactionDate, al.idLedger) AS runningBalance\nFROM tbl_AccountLedger al\nWHERE al.accountGroupId = @account_group_id\nORDER BY al.transactionDate\n',
        'tables': ['tbl_AccountLedger', 'tbl_AccountGroup'],
        'domain': 'Finance',
        'explanation': 'Displays ledger entries with a running balance calculation for a specific account.'
    },
    {
        'nl': 'List quality checklists for a product category',
        'sql': 'SELECT qc.checklistName, qp.parameterName, qp.standardValue, qp.uomId\nFROM tbl_QualityChecklist qc\nJOIN tbl_QualityParameter qp ON qc.idChecklist = qp.checklistId\nJOIN tbl_ProductMaster pm ON qc.productId = pm.idProduct\nWHERE pm.categoryId = @category_id\nORDER BY qc.checklistName, qp.parameterName\n',
        'tables': ['tbl_QualityChecklist', 'tbl_QualityParameter', 'tbl_ProductMaster'],
        'domain': 'Quality',
        'explanation': 'Shows quality checklists and their parameters filtered by product category.'
    },
    {
        'nl': 'Show all trips with total expenses',
        'sql': 'SELECT ts.tripNo, ts.tripDate, vm.vehicleNo, dm.driverName,\n       ts.loadingAmount, ts.unloadingAmount, ts.expenseAmount,\n       (ts.loadingAmount + ts.unloadingAmount + ts.expenseAmount) AS totalExpenses\nFROM tbl_TripSheet ts\nJOIN tbl_VehicleMaster vm ON ts.vehicleId = vm.idVehicle\nJOIN tbl_DriverMaster dm ON ts.driverId = dm.idDriver\nORDER BY ts.tripDate DESC\n',
        'tables': ['tbl_TripSheet', 'tbl_VehicleMaster', 'tbl_DriverMaster'],
        'domain': 'Logistics',
        'explanation': 'Displays trip details with vehicle, driver, and calculated total expenses.'
    },
    {
        'nl': 'Show product-wise pricing with current rates',
        'sql': 'SELECT pm.productName, pg.gradeName, pp.unitPrice, gsr.saleRate, gpr.purchaseRate\nFROM tbl_ProductPricing pp\nJOIN tbl_ProductMaster pm ON pp.productId = pm.idProduct\nJOIN tbl_ProductGrade pg ON pp.gradeId = pg.idGrade\nLEFT JOIN tbl_GlobalSaleRate gsr ON pp.productId = gsr.productId AND pp.gradeId = gsr.gradeId\nLEFT JOIN tbl_GlobalPurchaseRate gpr ON pp.productId = gpr.productId AND pp.gradeId = gpr.gradeId\nWHERE pp.isActive = 1\nORDER BY pm.productName, pg.gradeName\n',
        'tables': ['tbl_ProductPricing', 'tbl_ProductMaster', 'tbl_ProductGrade', 'tbl_GlobalSaleRate', 'tbl_GlobalPurchaseRate'],
        'domain': 'Pricing',
        'explanation': 'Shows product pricing with global sale and purchase rates for comparison.'
    },
    {
        'nl': 'List recent audit log entries by user',
        'sql': "SELECT al.activityDate, al.activity, al.tableName, al.recordId,\n       u.userName\nFROM tbl_AuditLog al JOIN tbl_UserMaster u ON al.userId = u.idUser\nWHERE al.userId = @user_id\nORDER BY al.activityDate DESC\n",
        'tables': ['tbl_AuditLog', 'tbl_UserMaster'],
        'domain': 'System',
        'explanation': 'Shows audit trail filtered by user with activity details and user name.'
    },
    {
        'nl': 'Show monthly sales trend for the current year',
        'sql': "SELECT MONTH(invoiceDate) AS monthNum,\n       DATENAME(MONTH, invoiceDate) AS monthName,\n       COUNT(idInvoice) AS invoiceCount,\n       SUM(grandTotal) AS totalSales\nFROM tbl_SaleInvoiceHeader\nWHERE YEAR(invoiceDate) = YEAR(GETDATE())\nGROUP BY MONTH(invoiceDate), DATENAME(MONTH, invoiceDate)\nORDER BY MONTH(invoiceDate)\n",
        'tables': ['tbl_SaleInvoiceHeader'],
        'domain': 'Sales',
        'explanation': 'Aggregates sales by month showing invoice count and total revenue trend.'
    },
    {
        'nl': 'Show vendor evaluation scores with average rating',
        'sql': 'SELECT o.firmName AS vendor,\n       COUNT(ve.idEvaluation) AS totalEvaluations,\n       AVG(ve.overallScore) AS averageScore,\n       MAX(ve.evaluationDate) AS lastEvaluated\nFROM tbl_VendorEvaluation ve\nJOIN tbl_Organization o ON ve.vendorId = o.idOrganization\nGROUP BY o.firmName\nORDER BY averageScore DESC\n',
        'tables': ['tbl_VendorEvaluation', 'tbl_Organization'],
        'domain': 'Purchase',
        'explanation': 'Aggregates vendor evaluation scores to show average rating, count, and last evaluation date.'
    },
    {
        'nl': 'Show stock transfer history between warehouses',
        'sql': 'SELECT st.transferNo, st.transferDate,\n       fw.warehouseName AS fromWarehouse,\n       tw.warehouseName AS toWarehouse,\n       pm.productName, st.quantity, st.statusId\nFROM tbl_StockTransfer st\nJOIN tbl_Warehouse fw ON st.fromWarehouseId = fw.idWarehouse\nJOIN tbl_Warehouse tw ON st.toWarehouseId = tw.idWarehouse\nJOIN tbl_ProductMaster pm ON st.productId = pm.idProduct\nORDER BY st.transferDate DESC\n',
        'tables': ['tbl_StockTransfer', 'tbl_Warehouse', 'tbl_ProductMaster'],
        'domain': 'Inventory',
        'explanation': 'Displays stock transfers with source and destination warehouse names and product details.'
    },
    {
        'nl': 'Show total outstanding amount by customer aging',
        'sql': "SELECT o.firmName,\n       SUM(CASE WHEN DATEDIFF(DAY, sih.invoiceDate, GETDATE()) <= 30 THEN sih.grandTotal ELSE 0 END) AS '0-30 Days',\n       SUM(CASE WHEN DATEDIFF(DAY, sih.invoiceDate, GETDATE()) BETWEEN 31 AND 60 THEN sih.grandTotal ELSE 0 END) AS '31-60 Days',\n       SUM(CASE WHEN DATEDIFF(DAY, sih.invoiceDate, GETDATE()) > 60 THEN sih.grandTotal ELSE 0 END) AS '60+ Days'\nFROM tbl_SaleInvoiceHeader sih\nJOIN tbl_Organization o ON sih.dealerOrgId = o.idOrganization\nJOIN dim_Status s ON sih.statusId = s.idStatus\nWHERE s.statusName NOT IN ('Paid', 'Cancelled')\nGROUP BY o.firmName\nORDER BY SUM(sih.grandTotal) DESC\n",
        'tables': ['tbl_SaleInvoiceHeader', 'tbl_Organization', 'dim_Status'],
        'domain': 'Finance',
        'explanation': 'Aging analysis of outstanding receivables grouped into 30/60/60+ day buckets.'
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
    },
    {
        'name': 'leave_overlap_check',
        'description': 'Employee cannot have overlapping leave applications for the same period',
        'category': 'hr',
        'severity': 'error',
        'applies_to': ['tbl_LeaveApplication'],
        'condition': 'EXISTS (SELECT 1 FROM tbl_LeaveApplication AS dup WHERE dup.employeeId = tbl_LeaveApplication.employeeId AND dup.idLeaveApplication != tbl_LeaveApplication.idLeaveApplication AND dup.fromDate <= tbl_LeaveApplication.toDate AND dup.toDate >= tbl_LeaveApplication.fromDate AND dup.statusId IN (SELECT idStatus FROM dim_Status WHERE statusCode IN (\'APPROVED\', \'PENDING\')))',
        'error_message': 'Employee already has an approved or pending leave application for an overlapping period.',
        'related_tables': ['tbl_LeaveApplication', 'tbl_Employee', 'dim_Status']
    },
    {
        'name': 'attendance_duplicate_check',
        'description': 'Employee cannot have duplicate attendance entries for the same date',
        'category': 'hr',
        'severity': 'error',
        'applies_to': ['tbl_Attendance'],
        'condition': 'EXISTS (SELECT 1 FROM tbl_Attendance AS dup WHERE dup.employeeId = tbl_Attendance.employeeId AND dup.attendanceDate = tbl_Attendance.attendanceDate AND dup.idAttendance != tbl_Attendance.idAttendance)',
        'error_message': 'Duplicate attendance entry for this employee on the same date.',
        'related_tables': ['tbl_Attendance', 'tbl_Employee']
    },
    {
        'name': 'sales_return_approval',
        'description': 'Sales return exceeding a threshold requires managerial approval before processing',
        'category': 'sales',
        'severity': 'warning',
        'applies_to': ['tbl_SaleReturn'],
        'condition': 'totalAmount > 10000 AND statusId NOT IN (SELECT idStatus FROM dim_Status WHERE statusCode = \'APPROVED\')',
        'error_message': 'Sales return above INR 10,000 requires approval before processing.',
        'related_tables': ['tbl_SaleReturn', 'tbl_SaleInvoiceHeader', 'dim_Status']
    },
    {
        'name': 'purchase_schedule_matching',
        'description': 'Purchase schedule quantity should not exceed the purchase order remaining quantity',
        'category': 'purchase',
        'severity': 'error',
        'applies_to': ['tbl_PurchaseSchedule'],
        'condition': 'quantity > (SELECT COALESCE(po.totalQty - SUM(ps2.quantity), 0) FROM tbl_PurchaseOrder po LEFT JOIN tbl_PurchaseSchedule ps2 ON po.idPurchaseOrder = ps2.purchaseOrderId AND ps2.idSchedule != tbl_PurchaseSchedule.idSchedule WHERE po.idPurchaseOrder = tbl_PurchaseSchedule.purchaseOrderId)',
        'error_message': 'Schedule quantity exceeds the remaining purchase order quantity.',
        'related_tables': ['tbl_PurchaseSchedule', 'tbl_PurchaseOrder']
    },
    {
        'name': 'payment_made_exceeds_invoice',
        'description': 'Payment made to a vendor should not exceed the linked purchase invoice amount',
        'category': 'finance',
        'severity': 'warning',
        'applies_to': ['tbl_PaymentMade'],
        'condition': 'amount > (SELECT COALESCE(SUM(pi.totalAmount), 0) FROM tbl_PurchaseInvoice pi JOIN tbl_PaymentMade pm2 ON pi.vendorId = pm2.vendorId WHERE pi.vendorId = tbl_PaymentMade.vendorId AND pi.statusId IN (SELECT idStatus FROM dim_Status WHERE statusCode != \'CANCELLED\'))',
        'error_message': 'Payment amount may exceed the total outstanding purchase invoices for this vendor.',
        'related_tables': ['tbl_PaymentMade', 'tbl_PurchaseInvoice', 'tbl_Organization']
    },
    {
        'name': 'booking_cancellation_check',
        'description': 'Booking with pending deliveries cannot be cancelled',
        'category': 'sales',
        'severity': 'error',
        'applies_to': ['tbl_Booking', 'tbl_BookingDelivery'],
        'condition': 'EXISTS (SELECT 1 FROM tbl_BookingDelivery bd WHERE bd.bookingId = tbl_Booking.idBooking AND bd.statusId IN (SELECT idStatus FROM dim_Status WHERE statusCode IN (\'PENDING\', \'IN_PROGRESS\')))',
        'error_message': 'Cannot cancel booking with pending or in-progress deliveries.',
        'related_tables': ['tbl_Booking', 'tbl_BookingDelivery', 'dim_Status']
    },
    {
        'name': 'negative_stock_adjustment',
        'description': 'Inventory adjustments reducing stock must be within available quantity',
        'category': 'inventory',
        'severity': 'error',
        'applies_to': ['tbl_InventoryAdjustment'],
        'condition': 'adjustmentType = \'REDUCE\' AND quantity > (SELECT COALESCE(SUM(closingQty), 0) FROM tbl_StockLedger WHERE productId = tbl_InventoryAdjustment.productId AND warehouseId = tbl_InventoryAdjustment.warehouseId)',
        'error_message': 'Adjustment quantity exceeds available stock for this product and warehouse.',
        'related_tables': ['tbl_InventoryAdjustment', 'tbl_StockLedger', 'tbl_Warehouse']
    },
    {
        'name': 'ewaybill_validity_check',
        'description': 'E-Way Bill must be valid (not expired) for goods in transit',
        'category': 'compliance',
        'severity': 'error',
        'applies_to': ['tbl_EwayBill', 'tbl_TripSheet'],
        'condition': "validTo < GETDATE() AND tbl_EwayBill.ewayBillNo IS NOT NULL AND EXISTS (SELECT 1 FROM tbl_TripSheet WHERE ewayBillId = tbl_EwayBill.idEwayBill AND tripStatusId IN (SELECT idStatus FROM dim_Status WHERE statusCode = 'IN_TRANSIT'))",
        'error_message': 'E-Way Bill has expired while goods are still in transit.',
        'related_tables': ['tbl_EwayBill', 'tbl_TripSheet', 'dim_Status']
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
    },
    {
        'category': 'leave_balance',
        'description': 'Calculate remaining leave balance per employee and leave type',
        'sql_template': "SELECT e.firstName + ' ' + e.lastName AS employeeName,\n       lt.leaveCode, lt.maxDays,\n       (lt.maxDays - COALESCE(SUM(la.totalDays), 0)) AS balanceDays\nFROM tbl_Employee e CROSS JOIN tbl_LeaveType lt\nLEFT JOIN tbl_LeaveApplication la ON e.idEmployee = la.employeeId AND la.leaveTypeId = lt.idLeaveType\n    AND YEAR(la.fromDate) = YEAR(GETDATE())\nGROUP BY e.firstName, e.lastName, lt.leaveCode, lt.maxDays\n",
        'tables': ['tbl_Employee', 'tbl_LeaveType', 'tbl_LeaveApplication'],
        'intent': 'How many leave days does employee X have remaining?'
    },
    {
        'category': 'payroll_summary',
        'description': 'Monthly payroll summary with gross, deductions, and net pay totals',
        'sql_template': "SELECT ph.payMonth, COUNT(DISTINCT pd.employeeId) AS totalEmployees,\n       SUM(pd.grossPay) AS totalGross, SUM(pd.totalDeductions) AS totalDeductions,\n       SUM(pd.netPay) AS totalNetPay\nFROM tbl_PayrollHeader ph JOIN tbl_PayrollDetail pd ON ph.idPayrollHeader = pd.payrollHeaderId\nWHERE MONTH(ph.payPeriodStart) = @month AND YEAR(ph.payPeriodStart) = @year\nGROUP BY ph.payMonth\n",
        'tables': ['tbl_PayrollHeader', 'tbl_PayrollDetail'],
        'intent': 'Show me the payroll summary for January 2024'
    },
    {
        'category': 'stock_movement',
        'description': 'Stock movement history for a product with transaction type',
        'sql_template': "SELECT transactionDate, transactionType, inwardQty, outwardQty, closingQty\nFROM tbl_StockLedger\nWHERE productId = @product_id\n  AND transactionDate BETWEEN @start_date AND @end_date\nORDER BY transactionDate\n",
        'tables': ['tbl_StockLedger'],
        'intent': 'Show the stock movement for product X over the last month'
    },
    {
        'category': 'trend_monthly',
        'description': 'Monthly trend aggregation for any metric with year comparison',
        'sql_template': "SELECT DATENAME(MONTH, @date_column) AS monthName,\n       MONTH(@date_column) AS monthNum, COUNT(*) AS recordCount,\n       SUM(@metric_column) AS totalMetric\nFROM @table_name\nWHERE YEAR(@date_column) = @year\nGROUP BY MONTH(@date_column), DATENAME(MONTH, @date_column)\nORDER BY MONTH(@date_column)\n",
        'tables': [],
        'intent': 'Show me the monthly sales trend for 2024'
    },
    {
        'category': 'aging_analysis',
        'description': 'Receivables/payables aging broken into 30/60/90+ day buckets',
        'sql_template': "SELECT o.firmName,\n       SUM(CASE WHEN DATEDIFF(DAY, @date_column, GETDATE()) <= 30 THEN @amount_column ELSE 0 END) AS '0-30 Days',\n       SUM(CASE WHEN DATEDIFF(DAY, @date_column, GETDATE()) BETWEEN 31 AND 60 THEN @amount_column ELSE 0 END) AS '31-60 Days',\n       SUM(CASE WHEN DATEDIFF(DAY, @date_column, GETDATE()) BETWEEN 61 AND 90 THEN @amount_column ELSE 0 END) AS '61-90 Days',\n       SUM(CASE WHEN DATEDIFF(DAY, @date_column, GETDATE()) > 90 THEN @amount_column ELSE 0 END) AS '90+ Days'\nFROM @table_name t JOIN tbl_Organization o ON t.@org_fk = o.idOrganization\nJOIN dim_Status s ON t.statusId = s.idStatus\nWHERE s.statusName NOT IN ('Paid', 'Cancelled')\nGROUP BY o.firmName\nORDER BY SUM(@amount_column) DESC\n",
        'tables': ['tbl_Organization', 'dim_Status'],
        'intent': 'Show me the aging report of outstanding invoices'
    },
    {
        'category': 'hr_headcount',
        'description': 'Employee headcount grouped by department or designation',
        'sql_template': "SELECT d.departmentName, COUNT(e.idEmployee) AS headcount\nFROM tbl_Employee e JOIN tbl_Department d ON e.departmentId = d.idDepartment\nWHERE e.isActive = 1\nGROUP BY d.departmentName\nORDER BY headcount DESC\n",
        'tables': ['tbl_Employee', 'tbl_Department'],
        'intent': 'How many employees are in each department?'
    },
    {
        'category': 'tds_summary',
        'description': 'TDS deduction summary grouped by section',
        'sql_template': 'SELECT tdsSection, SUM(tdsAmount) AS totalTds, COUNT(*) AS transactionCount\nFROM tbl_TDSDeduction\nWHERE YEAR(tdsDate) = @year\nGROUP BY tdsSection\nORDER BY tdsSection\n',
        'tables': ['tbl_TDSDeduction'],
        'intent': 'How much TDS was deducted under each section this year?'
    },
    {
        'category': 'running_balance',
        'description': 'Running balance calculation for ledger entries',
        'sql_template': "SELECT transactionDate, particulars, debit, credit,\n       SUM(debit - credit) OVER (ORDER BY transactionDate, idLedger) AS runningBalance\nFROM tbl_AccountLedger\nWHERE accountGroupId = @account_group_id\nORDER BY transactionDate\n",
        'tables': ['tbl_AccountLedger'],
        'intent': 'Show the ledger with running balance for account X'
    },
    {
        'category': 'product_pricing_check',
        'description': 'Compare product pricing against global rates to find discrepancies',
        'sql_template': "SELECT pm.productName, pg.gradeName, pp.unitPrice,\n       gsr.saleRate, gpr.purchaseRate\nFROM tbl_ProductPricing pp\nJOIN tbl_ProductMaster pm ON pp.productId = pm.idProduct\nJOIN tbl_ProductGrade pg ON pp.gradeId = pg.idGrade\nLEFT JOIN tbl_GlobalSaleRate gsr ON pp.productId = gsr.productId AND pp.gradeId = gsr.gradeId\nLEFT JOIN tbl_GlobalPurchaseRate gpr ON pp.productId = gpr.productId AND pp.gradeId = gpr.gradeId\nWHERE pp.isActive = 1 AND (pp.unitPrice > gsr.saleRate OR pp.unitPrice < gpr.purchaseRate)\n",
        'tables': ['tbl_ProductPricing', 'tbl_ProductMaster', 'tbl_ProductGrade', 'tbl_GlobalSaleRate', 'tbl_GlobalPurchaseRate'],
        'intent': 'Find products where pricing is outside global rate ranges'
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
    'total_rules': 20,
    'total_glossary_terms': 42,
    'total_sql_patterns': 19,
    'total_examples': 25
}
