from typing import Dict, Optional
from typing import List
from typing import Union


class CapitalAdequacyCalculator:
    """
    Calculator cho các chỉ số Capital Adequacy trong mô hình CAMELS
    """

    def __init__(self):
        self.thresholds = {
            "growth_rate": {"good": 10, "acceptable": 5},
            "leverage_ratio": {"good": (12, 20), "warning": 25, "low": 12},
            "iccr": {"benchmark": "rwa_growth"},  # So sánh với tốc độ tăng RWA
        }

    def calculate_equity_growth_rate(
        self, current_equity: float, previous_equity: float
    ) -> Dict[str, Union[float, str]]:
        """
        a) Tốc độ tăng quy mô VCSH

        Args:
            current_equity: Vốn chủ sở hữu năm hiện tại
            previous_equity: Vốn chủ sở hữu năm trước

        Returns:
            Dict với growth_rate (%) và assessment
        """
        if previous_equity <= 0:
            return {"error": "Vốn chủ sở hữu năm trước phải > 0"}
        growth_rate = ((current_equity - previous_equity) / previous_equity) * 100
        return {"growth_rate": round(growth_rate, 2)}

    def calculate_cagr(self, equity_data: List[Dict]) -> Dict[str, Union[float, str]]:
        """
        b) CAGR - Compound Annual Growth Rate (3 năm)

        Args:
            equity_data: List các dict {'year': year, 'equity': value}
            Ví dụ: [{'year': 2022, 'equity': 45000},
                   {'year': 2023, 'equity': 50000},
                   {'year': 2024, 'equity': 58000}]

        Returns:
            Dict với CAGR (%) và assessment
        """
        if len(equity_data) < 2:
            return {"error": "Cần ít nhất 2 năm dữ liệu"}

        # Sort by year
        sorted_data = sorted(equity_data, key=lambda x: x["year"])

        beginning_value = sorted_data[0]["equity"]
        ending_value = sorted_data[-1]["equity"]
        num_periods = int(sorted_data[-1]["year"]) - int(sorted_data[0]["year"])

        if beginning_value <= 0 or ending_value <= 0 or num_periods <= 0:
            return {"error": "Dữ liệu không hợp lệ cho tính CAGR"}

        # CAGR Formula: (Ending Value / Beginning Value)^(1/n) - 1
        cagr = (pow(ending_value / beginning_value, 1 / num_periods) - 1) * 100

        return {"cagr": round(cagr, 2)}

    def calculate_leverage_ratio(
        self, total_assets: float, total_equity: float
    ) -> Dict[str, Union[float, str]]:
        """
        c) Hệ số đòn bẩy tài chính (L = Total Assets / Equity)

        Args:
            total_assets: Tổng tài sản
            total_equity: Vốn chủ sở hữu

        Returns:
            Dict với leverage ratio và assessment
        """
        if total_equity <= 0:
            return {"error": "Vốn chủ sở hữu phải > 0"}

        leverage_ratio = total_assets / total_equity
        return {
            "leverage_ratio": round(leverage_ratio, 2),
        }

    def calculate_iccr(
        self,
        retained_earnings: float,
        beginning_equity: float,
        dividends_paid: Optional[float] = None,
    ) -> Dict[str, Union[float, str]]:
        """
        d) Internal Capital Creation Rate - Tỷ lệ tăng trưởng vốn tự có bền vững

        Args:
            retained_earnings: Lợi nhuận giữ lại trong năm
            beginning_equity: Vốn chủ sở hữu đầu kỳ
            dividends_paid: Cổ tức đã trả (optional)

        Returns:
            Dict với ICCR (%) và assessment
        """
        if beginning_equity <= 0:
            return {"error": "Vốn chủ sở hữu đầu kỳ phải > 0"}

        # ICCR = Retained Earnings / Beginning Equity × 100
        iccr = (retained_earnings / beginning_equity) * 100

        # Tính retention ratio nếu có thông tin cổ tức
        retention_info = {}
        if dividends_paid is not None:
            total_earnings = retained_earnings + dividends_paid
            if total_earnings > 0:
                retention_ratio = retained_earnings / total_earnings
                payout_ratio = dividends_paid / total_earnings
                retention_info = {
                    "retention_ratio": round(retention_ratio, 4),
                    "payout_ratio": round(payout_ratio, 4),
                    "total_earnings": total_earnings,
                }
        result = {"iccr": round(iccr, 2)}

        if retention_info:
            result.update(retention_info)

        return result

    def comprehensive_capital_analysis(self, financial_data: Dict) -> Dict:
        """
        Phân tích tổng hợp Capital Adequacy

        Args:
            financial_data: Dict chứa dữ liệu tài chính nhiều năm
            Format: {
                2022: {CAPITAL_ADEQUACY: {...}},
                2023: {CAPITAL_ADEQUACY: {...}},
                2024: {CAPITAL_ADEQUACY: {...}}
            }
        """
        years = sorted(financial_data.keys())
        if len(years) < 2:
            return {"error": "Cần ít nhất 2 năm dữ liệu"}

        results = {}

        # 1. Tốc độ tăng trưởng từng năm
        growth_rates = []
        for i in range(1, len(years)):
            current_year = years[i]
            previous_year = years[i - 1]

            current_equity = financial_data[current_year]["CAPITAL_ADEQUACY"][
                "total_equity"
            ]
            previous_equity = financial_data[previous_year]["CAPITAL_ADEQUACY"][
                "total_equity"
            ]

            if current_equity and previous_equity:
                growth = self.calculate_equity_growth_rate(
                    current_equity, previous_equity
                )
                growth_rates.append(
                    {"period": f"{previous_year}-{current_year}", **growth}
                )

        results["yearly_growth_rates"] = growth_rates

        # 2. CAGR
        equity_data = []
        for year in years:
            equity = financial_data[year]["CAPITAL_ADEQUACY"]["total_equity"]
            if equity:
                equity_data.append({"year": year, "equity": equity})

        if len(equity_data) >= 2:
            results["cagr"] = self.calculate_cagr(equity_data)

        # 3. Leverage ratio từng năm
        leverage_ratios = []
        for year in years:
            total_assets = financial_data[year]["CAPITAL_ADEQUACY"]["total_assets"]
            total_equity = financial_data[year]["CAPITAL_ADEQUACY"]["total_equity"]

            if total_assets and total_equity:
                leverage = self.calculate_leverage_ratio(total_assets, total_equity)
                leverage["year"] = year
                leverage_ratios.append(leverage)

        results["leverage_ratios"] = leverage_ratios

        # 4. ICCR từng năm
        iccr_rates = []
        for i, year in enumerate(years):
            if i == 0:  # Skip first year (no previous year data)
                continue

            retained_earnings = financial_data[year]["CAPITAL_ADEQUACY"][
                "retained_earnings"
            ]
            beginning_equity = financial_data[years[i - 1]]["CAPITAL_ADEQUACY"][
                "total_equity"
            ]

            if retained_earnings is not None and beginning_equity:
                # Tính retained earnings cho năm hiện tại
                current_retained = financial_data[year]["CAPITAL_ADEQUACY"][
                    "retained_earnings"
                ]
                previous_retained = financial_data[years[i - 1]]["CAPITAL_ADEQUACY"][
                    "retained_earnings"
                ]

                if current_retained is not None and previous_retained is not None:
                    annual_retained = current_retained - previous_retained
                    iccr = self.calculate_iccr(annual_retained, beginning_equity)
                    iccr["year"] = year
                    iccr_rates.append(iccr)

        results["iccr_rates"] = iccr_rates

        return results


from typing import Dict


class AssetQualityCalculator:
    """
    Calculator cho các chỉ số Asset Quality trong mô hình CAMELS
    (chỉ trả về số liệu, không đánh giá)
    """

    def calculate_growth(self, current: float, previous: float) -> float:
        """Tính tốc độ tăng trưởng (%)"""
        if previous <= 0:
            return None
        return round(((current - previous) / previous) * 100, 2)

    def calculate_loan_to_asset_ratio(self, loans: float, assets: float) -> float:
        """Tỷ trọng dư nợ tín dụng / tổng tài sản (%)"""
        if assets <= 0:
            return None
        return round((loans / assets) * 100, 2)

    def calculate_npl_ratio(self, provision: float, loans: float) -> float:
        """Tỷ lệ nợ xấu (ước tính từ dự phòng / dư nợ)"""
        if loans <= 0:
            return None
        return round(abs(provision) / loans * 100, 2)

    def comprehensive_asset_quality_analysis(self, bank_data: Dict) -> Dict:
        """
        bank_data: dict chứa dữ liệu nhiều năm cho 1 ngân hàng
        Format: bank_data["2022"]["ASSET_QUALITY"]...
        """
        years = sorted(bank_data.keys())
        results = {"growth_rates": [], "loan_to_asset_ratios": [], "npl_ratios": []}

        # Growth rates (tổng tài sản, dư nợ tín dụng)
        for i in range(1, len(years)):
            prev, curr = years[i - 1], years[i]

            prev_assets = bank_data[prev]["CAPITAL_ADEQUACY"]["total_assets"]
            curr_assets = bank_data[curr]["CAPITAL_ADEQUACY"]["total_assets"]
            if prev_assets and curr_assets:
                results["growth_rates"].append(
                    {
                        "indicator": "total_assets",
                        "period": f"{prev}-{curr}",
                        "growth_rate": self.calculate_growth(curr_assets, prev_assets),
                    }
                )

            prev_loans = bank_data[prev]["ASSET_QUALITY"]["gross_loans_to_customers"]
            curr_loans = bank_data[curr]["ASSET_QUALITY"]["gross_loans_to_customers"]
            if prev_loans and curr_loans:
                results["growth_rates"].append(
                    {
                        "indicator": "gross_loans_to_customers",
                        "period": f"{prev}-{curr}",
                        "growth_rate": self.calculate_growth(curr_loans, prev_loans),
                    }
                )

        # Loan/Asset ratio
        for year in years:
            loans = bank_data[year]["ASSET_QUALITY"]["gross_loans_to_customers"]
            assets = bank_data[year]["CAPITAL_ADEQUACY"]["total_assets"]
            results["loan_to_asset_ratios"].append(
                {
                    "year": year,
                    "loan_to_asset_ratio": self.calculate_loan_to_asset_ratio(
                        loans, assets
                    ),
                }
            )

        # NPL ratio
        for year in years:
            loans = bank_data[year]["ASSET_QUALITY"]["gross_loans_to_customers"]
            provision = bank_data[year]["ASSET_QUALITY"]["loan_loss_provision"]
            results["npl_ratios"].append(
                {"year": year, "npl_ratio": self.calculate_npl_ratio(provision, loans)}
            )

        return results


from typing import Dict, Optional


class ManagementCompetenceCalculator:
    """
    Calculator cho các chỉ số Management Competence (M) trong CAMELS
    (chỉ tính CIR và OPEX/Tổng tài sản)
    """

    def calculate_cir(self, opex: float, toi: float) -> Optional[float]:
        """
        a) Cost-to-Income Ratio (CIR) = Chi phí hoạt động / Tổng thu nhập hoạt động (%)
        """
        if toi is None or toi == 0:
            return None
        return round(abs(opex) / toi * 100, 2)

    def calculate_opex_to_assets(self, opex: float, assets: float) -> Optional[float]:
        """
        b) OPEX / Tổng tài sản (%)
        """
        if assets is None or assets == 0:
            return None
        return round(abs(opex) / assets * 100, 2)

    def comprehensive_management_analysis(self, bank_data: Dict) -> Dict:
        """
        Phân tích tổng hợp Management Competence cho nhiều năm

        Args:
            bank_data: dict chứa dữ liệu nhiều năm cho 1 ngân hàng
            Format: bank_data["2022"]["MANAGEMENT_EFFICIENCY"]...

        Returns:
            Dict với CIR và OPEX/Assets theo từng năm
        """
        years = sorted(bank_data.keys())
        results = {"cir": [], "opex_to_assets": []}

        for year in years:
            mgmt = bank_data[year].get("MANAGEMENT_EFFICIENCY", {})
            cap = bank_data[year].get("CAPITAL_ADEQUACY", {})
            earn = bank_data[year].get("EARNINGS_PROFITABILITY", {})

            opex = mgmt.get("total_operating_expenses")
            toi = mgmt.get("total_operating_income") or earn.get(
                "total_operating_income"
            )
            assets = cap.get("total_assets")

            # CIR
            cir_val = self.calculate_cir(opex, toi) if opex and toi else None
            results["cir"].append({"year": year, "cir": cir_val})

            # OPEX/Assets
            opex_assets_val = (
                self.calculate_opex_to_assets(opex, assets) if opex and assets else None
            )
            results["opex_to_assets"].append(
                {"year": year, "opex_to_assets": opex_assets_val}
            )

        return results


from typing import Dict, Optional


class EarningStrengthCalculator:
    """
    Calculator cho các chỉ số Earning Strength (E) trong CAMELS
    """

    def calculate_profit_margin(
        self, net_profit: float, total_income: float
    ) -> Optional[float]:
        """
        PM – Profit Margin = LNST / Tổng thu nhập hoạt động (%)
        """
        if total_income is None or total_income == 0:
            return None
        return round(net_profit / total_income * 100, 2)

    def calculate_asset_utilization(
        self, total_income: float, total_assets: float
    ) -> Optional[float]:
        """
        AU – Asset Utilization = Tổng thu nhập hoạt động / Tổng tài sản (%)
        """
        if total_assets is None or total_assets == 0:
            return None
        return round(total_income / total_assets * 100, 2)

    def calculate_equity_multiplier(
        self, total_assets: float, total_equity: float
    ) -> Optional[float]:
        """
        EM – Equity Multiplier = Tổng tài sản / Vốn chủ sở hữu (lần)
        """
        if total_equity is None or total_equity == 0:
            return None
        return round(total_assets / total_equity, 2)

    def calculate_roe(self, pm: float, au: float, em: float) -> Optional[float]:
        """
        ROE = PM × AU × EM (%)
        """
        if pm is None or au is None or em is None:
            return None
        return round((pm / 100) * (au / 100) * em * 100, 2)

    def calculate_nim(
        self, net_interest_income: float, earning_assets: float
    ) -> Optional[float]:
        """
        NIM = Thu nhập lãi thuần / Tài sản sinh lãi (%)
        earning_assets có thể lấy từ: cho vay khách hàng + chứng khoán đầu tư + tiền gửi liên NH
        """
        if earning_assets is None or earning_assets == 0:
            return None
        return round(net_interest_income / earning_assets * 100, 2)

    def calculate_days_interest_receivable(
        self, interest_income: float, interest_receivable: float, period_days: int = 365
    ) -> Optional[float]:
        """
        Số ngày lãi phải thu = Lãi phải thu / (Thu nhập lãi bình quân 1 ngày)
        """
        if interest_income is None or interest_income == 0:
            return None
        daily_interest = interest_income / period_days
        if daily_interest == 0:
            return None
        return round(interest_receivable / daily_interest, 2)

    def comprehensive_earning_analysis(self, bank_data: Dict) -> Dict:
        """
        Phân tích tổng hợp Earning Strength cho nhiều năm

        Args:
            bank_data: dict chứa dữ liệu nhiều năm cho 1 ngân hàng
            Format: bank_data["2022"]["EARNINGS_PROFITABILITY"]...

        Returns:
            Dict với PM, AU, EM, ROE, NIM, Days Interest Receivable
        """
        years = sorted(bank_data.keys())
        results = {
            "profit_margin": [],
            "asset_utilization": [],
            "equity_multiplier": [],
            "roe": [],
            "nim": [],
            "days_interest_receivable": [],
        }

        for year in years:
            cap = bank_data[year].get("CAPITAL_ADEQUACY", {})
            earn = bank_data[year].get("EARNINGS_PROFITABILITY", {})
            assetq = bank_data[year].get("ASSET_QUALITY", {})

            net_profit = cap.get("net_profit_after_tax")
            total_income = earn.get("total_operating_income")
            total_assets = cap.get("total_assets")
            total_equity = cap.get("total_equity")

            # Dupont components
            pm = (
                self.calculate_profit_margin(net_profit, total_income)
                if net_profit and total_income
                else None
            )
            au = (
                self.calculate_asset_utilization(total_income, total_assets)
                if total_income and total_assets
                else None
            )
            em = (
                self.calculate_equity_multiplier(total_assets, total_equity)
                if total_assets and total_equity
                else None
            )
            roe = self.calculate_roe(pm, au, em) if pm and au and em else None

            results["profit_margin"].append({"year": year, "pm": pm})
            results["asset_utilization"].append({"year": year, "au": au})
            results["equity_multiplier"].append({"year": year, "em": em})
            results["roe"].append({"year": year, "roe": roe})

            # NIM
            net_interest_income = earn.get("net_interest_income")
            earning_assets = (
                assetq.get("gross_loans_to_customers", 0)
                + assetq.get("investment_securities_htm", 0)
                + assetq.get("investment_securities_afs", 0)
                + assetq.get("interbank_deposits_loans", 0)
            )
            nim = (
                self.calculate_nim(net_interest_income, earning_assets)
                if net_interest_income and earning_assets
                else None
            )
            results["nim"].append({"year": year, "nim": nim})

            # Days Interest Receivable
            interest_income = earn.get("gross_interest_income")
            interest_receivable = assetq.get("interest_and_fees_receivable")
            days_ir = (
                self.calculate_days_interest_receivable(
                    interest_income, interest_receivable
                )
                if interest_income and interest_receivable
                else None
            )
            results["days_interest_receivable"].append(
                {"year": year, "days_ir": days_ir}
            )

        return results


#
# with open('banking_index.json', 'r', encoding='utf-8') as file:
#     banking_index = json.load(file)
# ec = EarningStrengthCalculator().comprehensive_earning_analysis(banking_index['SHB'])
# print(ec)
