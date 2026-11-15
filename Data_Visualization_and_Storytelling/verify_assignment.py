"""Focused financial and dashboard checks; run from the project root."""
import unittest
import numpy as np
import pandas as pd
from retail_metrics import derive_measures, summarize
from pathlib import Path
from retail_metrics import annual_summary


class FinancialConventions(unittest.TestCase):
    def test_guide_shipping_is_charged_once_per_transaction(self):
        # Artificial arithmetic examples, not records added to the supplied dataset.
        rows=pd.DataFrame({'Order_ID':['A','B'],'Order_Date':['2024-01-01','2024-01-02'],
                           'Category':['Technology','Technology'],'Quantity':[2,1],
                           'Unit_Price':[100.,100.],'Discount_Pct':[.10,0.],
                           'Unit_Cost':[60.,50.],'Shipping_Cost':[5.,5.]})
        result=derive_measures(rows)
        self.assertEqual(result.loc[0,'GrossSales'],200)
        self.assertEqual(result.loc[0,'DiscountAmount'],20)
        self.assertEqual(result.loc[0,'NetSales'],180)
        self.assertEqual(result.loc[0,'ProductCost'],120)
        self.assertEqual(result.loc[0,'Profit'],55)
        self.assertAlmostEqual(result.loc[0,'ProfitMarginPct'],55/180*100)
        total=summarize(result,'Category').iloc[0]
        self.assertAlmostEqual(total.ProfitMarginPct,100/280*100)
        self.assertAlmostEqual(total.GrossWeightedDiscountPct,20/300*100)
        self.assertEqual(total.Orders,2)

    def test_actual_exports_against_original_workbooks(self):
        root=Path(__file__).resolve().parent
        raw=pd.concat([pd.read_excel(root/f'Data/BITS_Retail_{y}.xlsx') for y in [2024,2025,2026]],ignore_index=True)
        self.assertEqual(len(raw),1316)
        self.assertEqual(raw.duplicated().sum(),6)
        original=raw.drop_duplicates()
        master=pd.read_excel(root/'Data/BITS_Retail_Master.xlsx',sheet_name='Product_Master')
        original=original.merge(master[['Product_ID','Unit_Cost']],on='Product_ID',validate='many_to_one')
        exported=pd.read_csv(root/'output/BITS_Retail_Cleaned_Integrated.csv')
        self.assertEqual(len(exported),1310)
        self.assertTrue(exported.Order_ID.is_unique)
        self.assertFalse(exported.isna().any().any())
        expected=original.set_index('Order_ID').loc[exported.Order_ID]
        net=expected.Quantity.to_numpy()*expected.Unit_Price.to_numpy()*(1-expected.Discount_Pct.to_numpy())
        profit=net-expected.Quantity.to_numpy()*expected.Unit_Cost.to_numpy()-expected.Shipping_Cost.to_numpy()
        np.testing.assert_allclose(exported.NetSales,net)
        np.testing.assert_allclose(exported.Profit,profit)
        self.assertEqual(set(exported.Category),{'Technology','Furniture','Office Supplies'})
        for field in ['Year','Region','Category']:
            self.assertAlmostEqual(exported.groupby(field).NetSales.sum().sum(),exported.NetSales.sum())
            self.assertAlmostEqual(exported.groupby(field).Profit.sum().sum(),exported.Profit.sum())
        self.assertTrue(annual_summary(exported[exported.Year.isin([2024,2026])]).YoYSalesPct.isna().all())
        log=pd.read_csv(root/'output/Data_Cleaning_Log.csv')
        self.assertEqual(log.columns.tolist(),['Issue','Field','Records affected','Action taken','Justification','Validation outcome'])
        self.assertFalse(log.isna().any().any())


if __name__=='__main__':
    unittest.main()
