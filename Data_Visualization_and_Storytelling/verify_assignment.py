"""Focused financial and dashboard checks; run from the project root."""
import unittest
import numpy as np
import pandas as pd
from retail_metrics import derive_measures, summarize


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


if __name__=='__main__':
    unittest.main()
