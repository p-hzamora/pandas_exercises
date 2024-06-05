
# path = Path(__file__).parent.parent / 'data.csv'
# string_pa = pd.ArrowDtype(pa.string())
# df = pd.read_csv(path, sep=';', dtype=string_pa, na_values=["-"])
# print(df.info())

string_pa = pd.ArrowDtype(pa.string())
str = pd.ArrowDtype(pa.string())
cat = pd.CategoricalDtype()
u8 = pd.UInt8Dtype()
u16 = pd.UInt16Dtype()
u32 = pd.UInt32Dtype()
u64 = pd.UInt64Dtype()
i8 = pd.Int8Dtype()
i16 = pd.Int16Dtype()
i32 = pd.Int32Dtype()
i64 = pd.Int64Dtype()
f32 = pd.Float32Dtype()
f64 = pd.Float64Dtype()
bl = pd.BooleanDtype()
dt = pd.DatetimeTZDtype()
td = pd.Timedelta()
pr = pd.PeriodDtype()

# try:
#     df = pd.read_csv(
#         "Data/sales_data_with_stores.csv",
#         dtype={
#             "store": cat,
#             "product_group": cat,
#             "product_code": u16,
#             "stock_qty": i32,
#             "cost": f64,
#             "price": f64,
#             "last_week_sales": u16,
#             "last_month_sales": u16,
#         },
#         engine="pyarrow",
#     )

# except Exception as e:
#     print(e)


# [
#     (np.iinfo(np.uint8).min, np.iinfo(np.uint8).max),
#     (np.iinfo(np.uint16).min, np.iinfo(np.uint16).max),
#     (np.iinfo(np.uint32).min, np.iinfo(np.uint32).max),
#     (np.iinfo(np.int8).min, np.iinfo(np.int8).max),
#     (np.iinfo(np.int16).min, np.iinfo(np.int16).max),
#     (np.iinfo(np.int32).min, np.iinfo(np.int32).max),
#     (np.iinfo(np.int64).min, np.iinfo(np.int64).max),
#     (np.finfo(np.float32).min, np.finfo(np.float32).max),
#     (np.finfo(np.float64).min, np.finfo(np.float64).max),
# ]

# @ld.logger_decorator
# def load_data():
#     path = Path(__file__).parent.parent / 'data.csv'
#     df = pd.read_csv(path, sep=';', dtype=str)
#     print(df.memory_usage(deep=True).sum())
#     return df

# load_data()

# num_rows = len(df)
# df_min = pd.DataFrame(df.min(), columns=["min"])
# df_max = pd.DataFrame(df.max(), columns=["max"])
# df_nunique = pd.DataFrame(df.nunique(), columns=["nunique"])
# df_null = pd.DataFrame(df.isna().sum(), columns=["nnull"])
# df_memory = pd.DataFrame(df.memory_usage(deep=True), columns=["memory"])
# df_type = pd.DataFrame(df.dtypes, columns=["dtype"])

# df = df_min.join(df_max)
# df = df.join(df_nunique)
# df = df.join(df_null)
# df = df.join(df_memory)
# df = df.join(df_type)
# df["nrows"] = num_rows
# df
