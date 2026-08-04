// ==============================================================================
// ENTERPRISE E-COMMERCE CONTROL TOWER — POWER QUERY (M) TRANSFORMATION SUITE
// Master ETL Code for Power BI Desktop
// ==============================================================================

// ------------------------------------------------------------------------------
// 0. PARAMETERS
// ------------------------------------------------------------------------------
let
    // Configurable root directory path pointing to data/processed/ or data/raw/
    FolderPath = "C:\PROJECTS\Data Analytics\E-Commerce\data\processed\" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]
in
    FolderPath

// ------------------------------------------------------------------------------
// 1. STAGING QUERIES (Load Disabled / Enable Load = False)
// ------------------------------------------------------------------------------

// stg_FactOrders
let
    Source = Csv.Document(File.Contents(FolderPath & "fact_orders.csv"), [Delimiter=",", Columns=49, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"order_id", type text},
        {"customer_id", type text},
        {"customer_unique_id", type text},
        {"order_status", type text},
        {"order_purchase_timestamp", type datetime},
        {"order_approved_at", type datetime},
        {"order_delivered_carrier_date", type datetime},
        {"order_delivered_customer_date", type datetime},
        {"order_estimated_delivery_date", type datetime},
        {"date_key", Int64.Type},
        {"delivery_days", type number},
        {"delay_days", type number},
        {"handling_days", type number},
        {"transit_days", type number},
        {"shipping_sla_days", type number},
        {"late_delivery_flag", Int64.Type},
        {"severe_delay_flag", Int64.Type},
        {"order_item_count", Int64.Type},
        {"gmv", type number},
        {"freight_value", type number},
        {"total_order_value", type number},
        {"review_score_avg", type number},
        {"low_review_flag", Int64.Type},
        {"high_review_flag", Int64.Type},
        {"customer_city", type text},
        {"customer_state", type text},
        {"customer_region", type text}
    })
in
    #"Changed Type"

// stg_FactOrderItems
let
    Source = Csv.Document(File.Contents(FolderPath & "fact_order_items.csv"), [Delimiter=",", Columns=33, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"order_id", type text},
        {"order_item_id", Int64.Type},
        {"product_id", type text},
        {"seller_id", type text},
        {"shipping_limit_date", type datetime},
        {"price", type number},
        {"freight_value", type number},
        {"total_item_value", type number},
        {"freight_ratio_pct", type number},
        {"product_category_name_english", type text},
        {"customer_unique_id", type text},
        {"date_key", Int64.Type},
        {"distance_km", type number},
        {"distance_band", type text},
        {"interstate_flag", Int64.Type},
        {"late_delivery_flag", Int64.Type}
    })
in
    #"Changed Type"

// stg_FactPayments
let
    Source = Csv.Document(File.Contents(FolderPath & "fact_payments.csv"), [Delimiter=",", Columns=5, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"order_id", type text},
        {"payment_sequential", Int64.Type},
        {"payment_type", type text},
        {"payment_installments", Int64.Type},
        {"payment_value", type number}
    })
in
    #"Changed Type"

// stg_FactReviews
let
    Source = Csv.Document(File.Contents(FolderPath & "fact_reviews.csv"), [Delimiter=",", Columns=8, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"review_id", type text},
        {"order_id", type text},
        {"review_score", Int64.Type},
        {"review_comment_title", type text},
        {"review_comment_message", type text},
        {"review_creation_date", type datetime},
        {"review_answer_timestamp", type datetime},
        {"response_time_days", type number}
    })
in
    #"Changed Type"

// stg_DimCustomers
let
    Source = Csv.Document(File.Contents(FolderPath & "dim_customers.csv"), [Delimiter=",", Columns=14, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"customer_unique_id", type text},
        {"customer_zip_code_prefix", type text},
        {"customer_city", type text},
        {"customer_state", type text},
        {"customer_region", type text},
        {"first_order_timestamp", type datetime},
        {"last_order_timestamp", type datetime},
        {"total_orders", Int64.Type},
        {"total_gmv", type number},
        {"average_order_value", type number},
        {"repeat_customer_flag", Int64.Type}
    })
in
    #"Changed Type"

// stg_DimSellers
let
    Source = Csv.Document(File.Contents(FolderPath & "dim_sellers.csv"), [Delimiter=",", Columns=17, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"seller_id", type text},
        {"seller_zip_code_prefix", type text},
        {"seller_city", type text},
        {"seller_state", type text},
        {"seller_region", type text},
        {"total_items_sold", Int64.Type},
        {"total_orders", Int64.Type},
        {"total_gmv", type number},
        {"avg_review_score", type number},
        {"on_time_rate", type number},
        {"late_delivery_rate", type number},
        {"avg_handling_days", type number}
    })
in
    #"Changed Type"

// stg_DimProducts
let
    Source = Csv.Document(File.Contents(FolderPath & "dim_products.csv"), [Delimiter=",", Columns=13, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"product_id", type text},
        {"product_category_name_english", type text},
        {"product_name_lenght", Int64.Type},
        {"product_description_lenght", Int64.Type},
        {"product_photos_qty", Int64.Type},
        {"product_weight_g", type number},
        {"product_volume_cm3", type number},
        {"product_size_category", type text}
    })
in
    #"Changed Type"

// stg_DimGeography
let
    Source = Csv.Document(File.Contents(FolderPath & "dim_geography.csv"), [Delimiter=",", Columns=5, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"zip_code_prefix", type text},
        {"city", type text},
        {"state", type text},
        {"latitude", type number},
        {"longitude", type number}
    })
in
    #"Changed Type"

// stg_DimDate
let
    Source = Csv.Document(File.Contents(FolderPath & "dim_date.csv"), [Delimiter=",", Columns=13, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"date_key", Int64.Type},
        {"full_date", type date},
        {"year", Int64.Type},
        {"quarter", type text},
        {"month_number", Int64.Type},
        {"month_name", type text},
        {"year_month", type text},
        {"day_of_week_number", Int64.Type},
        {"day_of_week_name", type text},
        {"is_weekend", Int64.Type}
    })
in
    #"Changed Type"

// ------------------------------------------------------------------------------
// 2. FINAL PRODUCTION MODEL QUERIES (Enable Load = True)
// ------------------------------------------------------------------------------

// FactOrders
let
    Source = stg_FactOrders,
    #"Selected Columns" = Table.SelectColumns(Source, {
        "order_id", "customer_id", "customer_unique_id", "order_status", 
        "order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date", 
        "order_delivered_customer_date", "order_estimated_delivery_date", "date_key", 
        "delivery_days", "delay_days", "handling_days", "transit_days", "shipping_sla_days", 
        "late_delivery_flag", "severe_delay_flag", "delay_band", "order_item_count", 
        "gmv", "freight_value", "total_order_value", "freight_ratio_pct", 
        "review_score_avg", "low_review_flag", "high_review_flag", "customer_state", "customer_region"
    })
in
    #"Selected Columns"

// FactOrderItems
let
    Source = stg_FactOrderItems,
    #"Selected Columns" = Table.SelectColumns(Source, {
        "order_id", "order_item_id", "product_id", "seller_id", "shipping_limit_date", 
        "price", "freight_value", "total_item_value", "freight_ratio_pct", 
        "product_category_name_english", "customer_unique_id", "date_key", 
        "distance_km", "distance_band", "interstate_flag", "late_delivery_flag", "delivery_days"
    })
in
    #"Selected Columns"

// FactPayments
let
    Source = stg_FactPayments
in
    Source

// FactReviews
let
    Source = stg_FactReviews
in
    Source

// DimCustomer
let
    Source = stg_DimCustomers
in
    Source

// DimSeller
let
    Source = stg_DimSellers
in
    Source

// DimProduct
let
    Source = stg_DimProducts
in
    Source

// DimCustomerGeography (Role-Playing Geography Dimension)
let
    Source = stg_DimGeography,
    #"Renamed Columns" = Table.RenameColumns(Source,{
        {"zip_code_prefix", "CustomerZipCode"},
        {"city", "CustomerCity"},
        {"state", "CustomerState"},
        {"latitude", "CustomerLatitude"},
        {"longitude", "CustomerLongitude"}
    })
in
    #"Renamed Columns"

// DimSellerGeography (Role-Playing Geography Dimension)
let
    Source = stg_DimGeography,
    #"Renamed Columns" = Table.RenameColumns(Source,{
        {"zip_code_prefix", "SellerZipCode"},
        {"city", "SellerCity"},
        {"state", "SellerState"},
        {"latitude", "SellerLatitude"},
        {"longitude", "SellerLongitude"}
    })
in
    #"Renamed Columns"

// DimDate
let
    Source = stg_DimDate
in
    Source

// DimOrderStatus
let
    Source = Table.FromRows(Json.Document(Binary.Decompress(Binary.FromText("i45WclTSUQrJSFXSUXLLT1eK1YlWcgSy/YoU3BJzUpV8UpNBLL98oERmUXFqXmpRJkK1E1jcCUl1TGpRJl7VrnkliXmpCs75eSkK4fklCs75+UX5eZk5Ck75hYm5icWpCj6peUDVsfkg42IB", BinaryEncoding.Base64), Compression.Deflate)), let _t = ((type nullable text) meta [Serialized.Text = true]) in type table [OrderStatus = _t, StatusCategory = _t, StatusOrder = _t]),
    #"Changed Type" = Table.TransformColumnTypes(Source,{{"OrderStatus", type text}, {"StatusCategory", type text}, {"StatusOrder", Int64.Type}})
in
    #"Changed Type"
