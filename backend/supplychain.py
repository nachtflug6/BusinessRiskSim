import pandas as pd

class SupplyChain:
    def __init__(self, df_companies: pd.DataFrame, df_risks: pd.DataFrame):
        self.df_companies = df_companies
        self.df_risks = df_risks

        company_hierarchy = []
        used_companies = []

        for k in range(len(df_companies.index)):
            level_companies = []
            level_used_companies = []
            for i, company in enumerate(df_companies['Company'], 0):
                suppliers = df_companies.iloc[i]['Supplier'].replace(" ", "").split(',')

                if company not in used_companies and company not in level_used_companies:
                    for j, affected_companies in enumerate(df_risks['Companies'], 0):
                        if company in affected_companies:
                            risk_code = df_risks['Risk']
                            # impacts = {'delivery assurance': row['delivery assurance'],
                            #                'customer requirements': row['customer requirements'],
                            #                'product data': row['product data'],
                            #                'green conversion': row['green conversion']}
                            # new_risk = Risk(row['Risks'], row['Disruption'], row['Frequency'], impacts)

                    if all(x in used_companies and x not in level_companies for x in
                           suppliers) or 'origin' in suppliers:
                        risk_list = []
                        for j, affected_companies in enumerate(df_risks['Companies'], 0):

                            if company in affected_companies:
                                risk_list.append(df_risks['Risk'].iloc[j])
                        level_used_companies.append(company)
                        level_companies.append({'company': company, 'suppliers': suppliers, 'risks': risk_list})

            used_companies = used_companies + level_used_companies

            company_hierarchy.append(level_companies)

        self.company_hierarchy = [level for level in company_hierarchy if level != []]

    def simulate(self, interval, num_runs):
        pass
