'''
    Author: Ribbon Huang
    根据爬取下来的资料，对股票进行预测
'''
from utils.mongou import MongoUse
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_pacf, plot_acf
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.stattools import adfuller
from utils.logger import LOGGER
from conf.settings import LOGGER_ANALYSIS_NAME
import prettytable
import numpy as np
from statsmodels.tsa.arima_model import ARMA
from conf.settings import PREDICT_START_POINT, PREDICT_END_POINT, MAX_COUNT, MAX_SQRT_COUNT

logger = LOGGER.createLogger(LOGGER_ANALYSIS_NAME)
db = MongoUse()
def pre_table(table_names, table_rows):
    table = prettytable.PrettyTable()
    table.field_names = table_names
    for row in table_rows:
        table.add_row(row)
    print(table)

'''
    数据分析：
        1. 平稳性分析
        2. 随机性检测
        3. 模型训练
        4. 结果预测
'''
class Analysis:
    def __init__(self, ts):
        self.ts = ts

    def adf_val(self, acf_title, pacf_title):
        # 平稳性分析
        plot_acf(self.ts, lags=20, title=acf_title).show()
        plot_pacf(self.ts, lags=20, title=pacf_title).show()
        adf, pvalue, usedlag, nobs, critical_values, icbest = adfuller(self.ts)
        table_rows = [[adf, pvalue, usedlag, nobs, critical_values, icbest]]
        table_names = ['adf', 'pvalue', 'usedlag', 'nobs', 'critical_values', 'icbest']
        pre_table(table_names, table_rows)
        return adf, pvalue, critical_values
        # print(adf, pvalue, usedlag, nobs, critical_values, icbest)

    def acorr_val(self):
        # 白噪声检测
        lbvalue, pvalue = acorr_ljungbox(self.ts, lags=1)
        table_rows = [[lbvalue, pvalue ]]
        table_names = ['lbvalue', 'pvalue']
        pre_table(table_names, table_rows)
        return pvalue

    def get_best_log(self, max_log=MAX_SQRT_COUNT, rule1=True, rule2=True):
        if rule1 and rule2:
            self.log_num = 0
            return 0, self.ts
        else:
            for i in range(1, max_log):
                # print(self.ts)
                self.ts = np.sqrt(self.ts)
                lbvalue, pvalue2 = acorr_ljungbox(self.ts, lags=1)
                adf, pvalue, usedlag, nobs, critical_values, icbest = adfuller(self.ts)
                rule1 = (adf < critical_values['1%'] and adf < critical_values['5%'] and adf < critical_values[
                    '10%'] and pvalue < 0.01)
                # print(rule1)
                rule2 = (pvalue2[0,] < 0.05)
                rule3 = i < max_log
                if rule1 and rule2 and rule3:
                    self.log_num = i
                    return i, self.ts
            self.log_num = max_log
            return max_log, self.ts

    def recover_log(self, predict_data):
        for i in range(1, self.log_num + 1):
            self.ts = np.power(self.ts, 2)
            predict_data = np.power(predict_data, 2)
        return predict_data

    def arma_fit(self):
        # 模型训练
        max_count = MAX_COUNT
        bic = float('inf')
        temp_score = []
        p = q = aic = hqic = 0
        for temp_p in range(max_count + 1):
            for temp_q in range(max_count + 1):
                model_arma = ARMA(self.ts, order=(temp_p, temp_q))
                try:
                    result_ARMA = model_arma.fit(disp=-1, method='css')
                except:
                    continue
                finally:
                    self.model = result_ARMA
                    temp_aic = result_ARMA.aic
                    temp_bic = result_ARMA.bic
                    temp_hqic = result_ARMA.hqic
                    temp = [temp_p, temp_q, temp_aic, temp_bic, temp_hqic]
                    temp_score.append(temp)
                    if temp_bic < bic:
                        p = temp_p
                        q = temp_q
                        aic = temp_aic
                        bic = temp_bic
                        hqic = temp_hqic
        names = ['p', 'q', 'aic', 'bic', 'hqic']
        table_rows = [[p, q, aic, bic, hqic]]
        pre_table(table_names=names, table_rows=table_rows)
        return self.model

    def predict_data(self, start, end, rule1=True, rule2=True):
        # 预测股票的走势
        # print(self.ts)
        predict_data = self.model.predict(start=start, end=end)
        if not(rule1 and rule2):
            predict_data = self.recover_log(predict_data=predict_data)
        # print(predict_data)
        plt.figure()
        predict_data.plot(label='predict data', style='--')
        self.ts.plot(label='raw data')
        plt.legend()
        plt.show()

'''
    分析流程整合
'''
def analysis_start():
    data = db.find()
    while True:
        try:
            df = next(data)
        except:
            break
        df['price'] = df['price']
        analysis = Analysis(df['price'])
        # 初始值的自相关，偏相关图形显示
        adf, pvalue, critical_values = analysis.adf_val(acf_title='raw data acf', pacf_title='raw data pacf')
        # 白噪声检测
        pvalue2 = analysis.acorr_val()

        rule1 = (adf < critical_values['1%'] and adf < critical_values['5%'] and adf < critical_values['10%'] and
                 pvalue < 0.01)
        rule2 = (pvalue2[0, ] < 0.05)

        # 稳定性处理， 进行log处理
        analysis.get_best_log(rule1=rule1, rule2=rule2)
        rule1 = (adf < critical_values['1%'] and adf < critical_values['5%'] and adf < critical_values['10%'] and
                 pvalue < 0.01)
        rule2 = (pvalue2[0,] < 0.05)

        # 训练模型，预测结果
        analysis.arma_fit()
        analysis.predict_data(start=PREDICT_START_POINT, end=PREDICT_END_POINT, rule1=rule1, rule2=rule2)

if __name__ == '__main__':
    analysis_start()

LOGGER.removeLogger()
