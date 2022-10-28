# RFM ile Müşteri Segmentasyonu (Customer Segmentation with RFM)

# 1. İş Problemi (Business Problem)
# 2. Veriyi Anlama (Data Understanding)
# 3. Veri Hazırlama (Data Preparation)
# 4. RFM Metriklerinin Hesaplanması (Calculating RFM Metrics)
# 5. RFM Skorlarının Hesaplanması (Calculating RFM Scores)
# 6. RFM Segmentlerinin Oluşturulması ve Analiz Edilmesi (Creating and Analysing RFM Segments)
# 7. Tüm sürecin Fonksiyonlaştırılması

# 1. İş Problemi (Business Problem)
#    müşterileri segmentlere ayırıp ilgilenmek istiyoruz:

# InvoiceNo: Fatura numarası. Her bir işleme yani faturaya ait eşsiz numara. C ile başlıyorsa iptal edilen işlem.
# StockCode: Ürün kodu. Her bir ürün için eşsiz numara.
# Description: Ürün ismi.
# Quantity: Ürün adedi. Faturalardaki ürünlerden kaçar tane satıldığını ifade etmektedir.
# InvoiceDate: Fatura tarihi ve zamanı.
# UnitPrice: Ürün fiyatı (Sterlin cinsinden)
# CustomerID: Eşsiz müşteri numarası
# Country: Ülke ismi. Müşterinin yaşadığı ülke.

# 2. Veriyi Anlama (Data Understanding)

import datetime as dt
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 500)
pd.set_option('display.float_format', lambda x:'%.5f' % x)   #sayısal değerlerin virgülden sonra kaç basamak gösterileceğini seçmek için %.5f %.3f gibi yazılabilir.

df_ = pd.read_excel(r'C:\Users\güneş market\Desktop\exceldosy\online_retail_II.xlsx', sheet_name='Year 2010-2011')

# excel dosyasını açmazsa aşağıdaki komutu yap:
import pip
pip.main(["install", "openpyxl"])

df = df_.copy()
df.head()
df['Invoice'].nunique()
df['TotalPrice'] = df['Quantity'] * df['Price']
df.groupby('Invoice').agg({'TotalPrice': 'sum'}).head()

# 3. Veri Hazırlama (Data Preparation)
df.shape
df.isnull().sum()
df.dropna(inplace=True)

# iade ürünler eksi değerler gelmesine neden oluyor, silmeliyiz:

df.describe().T
df = df[~df['Invoice'].str.contains('C', na=False)]
df.head()
df.describe().T


# 4. RFM Metriklerinin Hesaplanması (Calculating RFM Metrics)
df['InvoiceDate'].max()
today_date = dt.datetime(2011, 12, 11)
type(today_date)

rfm = df.groupby('Customer ID').agg({'InvoiceDate': lambda InvoiceDate: (today_date - InvoiceDate.max()).days,
                                      'Invoice': lambda Invoice: Invoice.nunique(),
                                      'TotalPrice': lambda TotalPrice: TotalPrice.sum()})
rfm.head()
rfm.columns = ['recency', 'frequency', 'monetary']  # değişkenlerin isimlerini rfm olarak atadık.
rfm.describe().T

# monetary değerinin 0 olmamalı, 0 olanları kaldıralım:

rfm = rfm[rfm['monetary'] > 0]
rfm.describe().T
rfm.shape # 4338 müşteri ve bu müşterileri temsil eden var rfm metrikleri var elimizde!
# bu metrikleri skorlara çevirmeliyiz, daha rahat kıyaslama yapabilmek için:

# 5. RFM Skorlarının Hesaplanması (Calculating RFM Scores)
# bu metrikleri skorlara çevirmek için qcut fonksiyonunu kulanabiliriz,
#  qcut fonksiyonu ile quartile'lara göre label atayarak bölebiliriz :

rfm['recency_score'] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])

# qcut ile yapılan şey 0-100 arasında değerler olsun: bu değerleri; 0-20, 20-40, 40-60, 60-80, 80-100 şeklinde böler.

rfm['monetary_score'] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

# aşağıda ismi yanlış yazarak atadım, bunu silmek için drop metodunu kullandım:
# rfm['frequncy_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
rfm.drop('frequncy_score', axis=1, inplace=True)

# frequency değeri için oluşturulan aralıklarda unique değerler yer almamakta, her bir aralıkta yinelenen çok fazla frekans bulunmaktadır,
#  ilk gördüğü değeri ilk sınıfa ataması için rank metodunu kullanırız:

rfm['frequency_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])

# skor değerlerini oluşturmalıyız, iki boyutlu görselde rfm skorları için recency ve frequency skorları yeterlidir:
#  bu nedenle rf değerlerini bir araya getirerek yazmamız gerekir:

rfm['RFM_SCORE'] = (rfm['recency_score'].astype(str) +
                    rfm['frequency_score'].astype(str))
rfm.describe().T

# örneğin 55 skorlu müşterileri çağıralım:

rfm[rfm['RFM_SCORE'] == '55']

# 6. RFM Segmentlerinin Oluşturulması ve Analiz Edilmesi (Creating and Analysing RFM Segments)

# regex
# okunabilirliği artırmak için regex (regular expressions) ekleyebiliriz.

seg_map = {
    r'[1-2][1-2]': 'hipernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

# bu isimleri replace ile atayabiliriz:
rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)

# segment analizi yapalım: örneğin bu sınıflardaki kişilerin recency ortalamaları nedir:
rfm[['segment', 'recency', 'frequency', 'monetary']].groupby('segment').agg(['mean', 'count'])

rfm[rfm['segment'] == 'cant_loose'].index

# yeni bir dataframe oluşturarak ayırmak istediğimiz grubu buna atayalım:
new_df = pd.DataFrame()
new_df['new_customer_id'] = rfm[rfm['segment'] == 'new_customers'].index

# integer hale getirelim, ondalıklardan kurtulalım:
new_df['new_customer_id'] = new_df['new_customer_id'].astype(int)

# bu dosyayı csv dosyası olarak çıkarmak için aşağıdaki komut yazılır sol sekmeden de reload from disk seçilir:

new_df.to_csv('new_customers.csv')