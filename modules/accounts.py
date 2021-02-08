import re

import dateparser


def get_reality_account(importer, account_description):
    if importer == 'wechat':
        return accounts_map[importer][account_description]
    return 'Unknown'


def get_account(trade_partner, trade_description, trade_date):
    for food in FOOD_SET:
        if food in trade_partner or food in trade_description:
            return 'Expenses:Food'

    if '滴滴' in trade_partner or '滴滴' in trade_description:
        if trade_date.hour >= 21 and trade_date.minute >= 30:
            return 'Assets:Receivables:公司报销'
        else:
            return 'Expenses:Transport:打车'

    return 'Unknown'


FOOD_SET = {'美食', '外卖', '餐厅', 'MTDP', '餐饮'}

TRANSPORT_SET = {'滴滴'}


def get_eating_account(from_user, description, time=None):
    if time == None or not hasattr(time, 'hour'):
        return 'Expenses:Eating:Others'
    elif time.hour <= 3 or time.hour >= 21:
        return 'Expenses:Eating:Nightingale'
    elif time.hour <= 10:
        return 'Expenses:Eating:Breakfast'
    elif time.hour <= 16:
        return 'Expenses:Eating:Lunch'
    else:
        return 'Expenses:Eating:Supper'


def get_credit_return(from_user, description, time=None):
    for key, value in credit_cards.items():
        if key == from_user:
            return value
    return "Unknown"


public_accounts = [
    'Assets:Company:Alipay:StupidAlipay'
]

credit_cards = {
    '中信银行': 'Liabilities:CreditCard:CITIC',
    '交通银行(4830)': 'Liabilities:CreditCard:交通银行'
}
accounts_map = {
    'wechat': {
        '零钱': 'Assets:Cash:WeChat',
        '中国银行(1886)': 'Assets:Bank:中国银行1886',
        '交通银行(4830)': 'Liabilities:CreditCard:交通银行4830',
    }
}


def get_expenses_account(expenses_categroy):
    result = expenses_categorys.get(expenses_categroy)
    if result is None:
        result = 'Expenses:Unknown'
    return result


def get_income_account(income_categroy):
    result = income_accounts.get(income_categroy)
    if result is None:
        result = 'Expenses:Unknown'
    return result


def get_base_account(account):
    result = assets_accounts.get(account)
    if result is not None:
        return result

    result = liabilities_accounts.get(account)
    if result is not None:
        return result

    return 'Unknown'


descriptions = {
    # '滴滴打车|滴滴快车': get_didi,
    '余额宝.*收益发放': 'Assets:Company:Alipay:MonetaryFund',
    '转入到余利宝': 'Assets:Bank:MyBank',
    '花呗收钱服务费': 'Expenses:Fee',
    '自动还款-花呗.*账单': 'Liabilities:Company:Huabei',
    '信用卡自动还款|信用卡还款': get_credit_return,
    '外卖订单': get_eating_account,
    '美团订单': get_eating_account,
    '上海交通卡发行及充值': 'Expenses:Transport:Card',
    '地铁出行': 'Expenses:Transport:City',
    '火车票': 'Expenses:Travel:Transport',
}

anothers = {
    '上海拉扎斯': get_eating_account
}

incomes = {
    '余额宝.*收益发放': 'Income:Trade:PnL',
}

description_res = dict([(key, re.compile(key)) for key in descriptions])
another_res = dict([(key, re.compile(key)) for key in anothers])
income_res = dict([(key, re.compile(key)) for key in incomes])

assets_accounts = {
    '中国银行1886': 'Assets:Bank:中国银行1886',
    '招商银行(0612)': 'Assets:Bank:招商银行0612',
    '中国银行(1886)': 'Assets:Bank:中国银行1886',
    '零钱': 'Assets:Bank:微信钱包',
    '公司报销': 'Assets:Receivables:公司报销',
    '记账过渡户': 'Assets:Receivables:记账过渡户',
    '押金户': 'Assets:Receivables:押金户',
    '老婆微信钱包': 'Assets:Bank:老婆微信钱包',
}

liabilities_accounts = {
    '交通银行(4830)': 'Liabilities:CreditCard:交通银行4830',
    '浦发银行(5278)': 'Liabilities:CreditCard:浦发银行5278',
    '招商银行(3396)': 'Liabilities:CreditCard:招商银行9619',
    '谢云辉': 'Liabilities:Payable:谢云辉',
    '六文': 'Liabilities:Payable:六文',

}
expenses_categorys = {
    '日常吃喝': 'Expenses:Food:日常吃喝',
    '工作聚餐': 'Expenses:Food:工作聚餐',
    '家庭聚餐': 'Expenses:Food:家庭聚餐',

    '房租': 'Expenses:Housing:房租',
    '水电煤': 'Expenses:Housing:水电煤',

    '打车': 'Expenses:Transport:打车',
    '火车': 'Expenses:Transport:火车',
    '飞机': 'Expenses:Transport:飞机',
    '单车': 'Expenses:Transport:单车',
    '租车': 'Expenses:Transport:租车',
    '加油费': 'Expenses:Transport:加油费',
    '维修费': 'Expenses:Transport:维修费',
    '地铁': 'Expenses:Transport:地铁',
    '高速费': 'Expenses:Transport:高速费',
    '停车费': 'Expenses:Transport:停车费',

    '电话费': 'Expenses:Communication:电话费',
    '宽带费': 'Expenses:Communication:宽带费',

    '充电宝': 'Expenses:Consumption:充电宝',
    '软件订阅购买': 'Expenses:Consumption:软件订阅购买',
    '电子产品': 'Expenses:Consumption:电子产品',

    '教育-妞妞': 'Expenses:Education:妞妞',
    '教育-朗朗': 'Expenses:Education:朗朗',

    '同事人情': 'Expenses:Favor:同事人情',
    '亲人人情': 'Expenses:Favor:亲人人情',
    '朋友人情': 'Expenses:Favor:朋友人情',

    '保险': 'Expenses:Finance:保险',
}

income_accounts = {
    '微信红包': 'Income:Other:收红包',
    '活动奖励': 'Income:Other:活动奖励'
}
